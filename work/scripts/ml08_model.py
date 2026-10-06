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
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml_contract import (
    FEATURE_END,
    FEATURE_START,
    LABEL_END,
    LABEL_START,
    OUTPUT_DIR,
    RANDOM_STATE,
    connect,
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
]


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
    splitter = GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=RANDOM_STATE)
    train_idx, test_idx = next(
        splitter.split(
            model_data,
            model_data["target"],
            groups=model_data["client_hash_id"],
        )
    )
    train = model_data.iloc[train_idx].copy()
    test = model_data.iloc[test_idx].copy()
    assert set(train["client_hash_id"]).isdisjoint(set(test["client_hash_id"]))
    assert train["target"].nunique() == 2 and test["target"].nunique() == 2

    features = NUMERIC_FEATURES
    X_train, X_test = train[features], test[features]
    y_train, y_test = train["target"].astype(int), test["target"].astype(int)
    results: list[dict[str, float | str]] = []
    fitted: dict[str, Pipeline] = {}
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

    baseline_scores = (test["baseline_score"] > 0).astype(float).to_numpy()
    baseline_metrics = ranking_metrics(y_test.to_numpy(), baseline_scores)
    baseline_metrics.update(
        {
            "model": "ml07_rule_baseline",
            "brier": float(brier_score_loss(y_test, baseline_scores)),
            "log_loss": float(log_loss(y_test, np.column_stack([1 - baseline_scores, baseline_scores]), labels=[0, 1])),
        }
    )
    results.append(baseline_metrics)
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
    review["baseline_flag"] = test["baseline_score"].gt(0).to_numpy()
    review["error_type"] = np.select(
        [
            (review["model_score"] >= 0.5) & review["target"].eq(0),
            (review["model_score"] < 0.5) & review["target"].eq(1),
        ],
        ["false_positive", "false_negative"],
        default="correct",
    )
    queue = review.sort_values(
        ["model_score", "content_hash_id"], ascending=[False, True], kind="stable"
    ).reset_index(drop=True)
    queue.insert(0, "rank", np.arange(1, len(queue) + 1))
    queue["suggested_action"] = np.where(
        queue["model_score"] >= 0.5, "review_for_refresh", "monitor_or_defer"
    )
    queue[
        [
            "rank",
            "content_hash_id",
            "client_hash_id",
            "model_score",
            "target",
            "baseline_flag",
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
        "split_strategy": "GroupShuffleSplit by client_hash_id, test_size=0.2",
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "held_out_clients": int(test["client_hash_id"].nunique()),
        "feature_columns": features,
        "comparison": comparison.to_dict(orient="records"),
        "best_learned_model": best_model_name,
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
        "| Model | Precision@10 | Precision@50 | Correct@50 | Brier | Log loss |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in comparison.itertuples(index=False):
        report_lines.append(
            f"| {row.model} | {row.precision_at_10:.4f} | "
            f"{row.precision_at_50:.4f} | {row.correct_at_50:.1f} | "
            f"{row.brier:.4f} | {row.log_loss:.4f} |"
        )
    report_lines.extend(
        [
            "",
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
