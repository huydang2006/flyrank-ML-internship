from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml_contract import (
    FEATURE_END,
    FEATURE_START,
    HOLDOUT_TEST_SIZE,
    LABEL_END,
    LABEL_START,
    OUTPUT_DIR,
    RANDOM_STATE,
    connect,
    client_balanced_ranking,
    grouped_holdout,
    load_contract,
    ranking_metrics,
    write_json,
)


NUMERIC_FEATURES = [
    "impressions_90d",
    "clicks_90d",
    "sessions_90d",
    "engaged_sessions_90d",
    "avg_position_feature",
    "engagement_rate_feature",
    "log_impressions_90d",
    "log_clicks_90d",
    "log_sessions_90d",
    "ga4_available_90d",
    "engagement_available",
]
REVIEW_BUDGET = 50


def build_models() -> dict[str, object]:
    return {
        "logistic_regression": LogisticRegression(
            class_weight="balanced", max_iter=1000, random_state=RANDOM_STATE
        ),
        "random_forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_leaf=20,
            class_weight="balanced_subsample",
            n_jobs=-1,
            random_state=RANDOM_STATE,
        ),
    }


def build_preprocessor() -> ColumnTransformer:
    return ColumnTransformer(
        [
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                NUMERIC_FEATURES,
            ),
        ]
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ML-08 model comparison.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    connection = connect()
    _, model_data = load_contract(connection)
    train, test = grouped_holdout(model_data)

    features = NUMERIC_FEATURES
    X_train, X_test = train[features], test[features]
    y_train, y_test = train["target"].astype(int), test["target"].astype(int)
    results: list[dict[str, float | str | None]] = []
    fitted: dict[str, Pipeline] = {}
    client_balanced: dict[str, dict[str, object]] = {}
    for name, estimator in build_models().items():
        pipeline = Pipeline(
            [("preprocess", build_preprocessor()), ("model", estimator)]
        )
        pipeline.fit(X_train, y_train)
        scores = pipeline.predict_proba(X_test)[:, 1]
        metrics = ranking_metrics(y_test.to_numpy(), scores)
        metrics.update(
            {
                "model": name,
                "brier": float(brier_score_loss(y_test, scores)),
                "log_loss": float(log_loss(y_test, np.column_stack([1 - scores, scores]), labels=[0, 1])),
            }
        )
        results.append(metrics)
        fitted[name] = pipeline
        client_balanced[name] = client_balanced_ranking(test, scores)

    baseline_scores = test["baseline_score"].to_numpy(dtype=float)
    baseline_metrics = ranking_metrics(y_test.to_numpy(), baseline_scores)
    baseline_metrics.update(
        {
            "model": "ml07_rule_baseline",
            "brier": None,
            "log_loss": None,
        }
    )
    results.append(baseline_metrics)
    client_balanced["ml07_rule_baseline"] = client_balanced_ranking(
        test, baseline_scores
    )
    comparison = pd.DataFrame(results).sort_values(
        ["precision_at_50", "precision_at_20", "average_precision"]
        if "average_precision" in results[0]
        else ["precision_at_50", "precision_at_20"],
        ascending=False,
    )
    learned = comparison[comparison["model"] != "ml07_rule_baseline"]
    best_model_name = str(learned.iloc[0]["model"])
    best_pipeline = fitted[best_model_name]
    best_scores = best_pipeline.predict_proba(X_test)[:, 1]

    review = test[
        [
            "client_hash_id",
            "content_hash_id",
            "target",
            "ctr_feature",
            "expected_ctr_feature",
            "impressions_90d",
        ]
    ].copy()
    review["model_score"] = best_scores
    review["baseline_score"] = test["baseline_score"].to_numpy()
    review["baseline_rank"] = (
        test["baseline_score"].rank(method="first", ascending=False).astype(int).to_numpy()
    )
    review["model_rank"] = (
        review["model_score"].rank(method="first", ascending=False).astype(int)
    )
    review["error_type"] = np.select(
        [
            (review["model_rank"] <= REVIEW_BUDGET) & review["target"].eq(0),
            (review["model_rank"] > REVIEW_BUDGET) & review["target"].eq(1),
        ],
        ["false_positive", "false_negative"],
        default="correct",
    )
    queue = review.sort_values(
        ["model_score", "content_hash_id"], ascending=[False, True], kind="stable"
    ).reset_index(drop=True)
    queue.insert(0, "rank", np.arange(1, len(queue) + 1))
    queue["suggested_action"] = np.where(
        queue["model_rank"] <= REVIEW_BUDGET, "review_for_refresh", "monitor_or_defer"
    )
    queue[
        [
            "rank",
            "content_hash_id",
            "client_hash_id",
            "model_score",
            "model_rank",
            "baseline_score",
            "baseline_rank",
            "suggested_action",
            "impressions_90d",
            "ctr_feature",
            "expected_ctr_feature",
        ]
    ].to_csv(output_dir / "ml08_model_queue.csv", index=False)

    metrics_payload = {
        "task": "ML-08",
        "random_state": RANDOM_STATE,
        "feature_window": [FEATURE_START, FEATURE_END],
        "label_window": [LABEL_START, LABEL_END],
        "target": "future CTR below half of feature position-tier pooled CTR",
        "split_strategy": f"GroupShuffleSplit by client_hash_id, test_size={HOLDOUT_TEST_SIZE}",
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "held_out_clients": int(test["client_hash_id"].nunique()),
        "feature_columns": features,
        "comparison": comparison.astype(object)
        .where(pd.notna(comparison), None)
        .to_dict(orient="records"),
        "client_balanced_comparison": client_balanced,
        "best_learned_model": best_model_name,
        "review_budget": REVIEW_BUDGET,
        "queue_output": "work/outputs/ml08_model_queue.csv",
    }
    write_json(output_dir / "ml08_model_metrics.json", metrics_payload)
    report_lines = [
        "# ML-08 model comparison",
        "",
        f"- Feature window: `{FEATURE_START}` to `{FEATURE_END}`",
        f"- Label window: `{LABEL_START}` to `{LABEL_END}`",
        f"- Split: grouped by client, seed `{RANDOM_STATE}`, test size `20%`",
        f"- Best learned model by Precision@50: **{best_model_name}**",
        "",
        "| Model | P@10 | P@20 | P@50 | Macro P@50 | Correct@50 | Brier | Log loss |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for row in comparison.itertuples(index=False):
        brier = "n/a" if pd.isna(row.brier) else f"{row.brier:.4f}"
        log_loss_value = "n/a" if pd.isna(row.log_loss) else f"{row.log_loss:.4f}"
        report_lines.append(
            f"| {row.model} | {row.precision_at_10:.4f} | "
            f"{row.precision_at_20:.4f} | {row.precision_at_50:.4f} | "
            f"{client_balanced[row.model]['macro_precision_at_50']:.4f} | "
            f"{row.correct_at_50:.1f} | {brier} | {log_loss_value} |"
        )
    report_lines.extend(
        [
            "",
            f"Model actions use a fixed review budget of the top {REVIEW_BUDGET} held-out rows; a 0.5 probability threshold is not used for queue selection.",
            "Calibration metrics are reported only for probabilistic learned models; the rule baseline is evaluated as a ranking score.",
            "Macro Precision@K gives each held-out client equal weight. Per-client rows and base rates are stored in the metrics JSON.",
            "The queue is a review aid. Future-window fields are used for evaluation only.",
        ]
    )
    (output_dir / "ml08_model_report.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )
    print(f"Wrote {output_dir / 'ml08_model_queue.csv'}")
    print(f"Wrote {output_dir / 'ml08_model_metrics.json'}")
    print(f"Wrote {output_dir / 'ml08_model_report.md'}")


if __name__ == "__main__":
    main()
