from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, log_loss
from sklearn.inspection import permutation_importance
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from ml07_baseline import confidence_note, supporting_reasons, suggested_action
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
    "ga4_available_90d",
    "engagement_available",
]
REVIEW_BUDGET = 50
FIGURES_DIR = Path(__file__).resolve().parents[2] / "work" / "figures"


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


def confidence_state(row: pd.Series) -> str:
    note = row["confidence_note"]
    if (
        row["impressions_90d"] >= 1000
        and "verify manually" not in note
        and "engagement not measured" not in note
    ):
        return "high"
    if row["impressions_90d"] >= 300:
        return "medium"
    return "low"


def save_count_plot(
    counts: pd.Series,
    title: str,
    path: Path,
    color: str,
    value_format: str = "{:,.3g}",
) -> None:
    labels = [str(label) for label in counts.index]
    values = counts.to_numpy(dtype=float)
    maximum = max(float(values.max()) if len(values) else 0, 1)
    fig, axis = plt.subplots(figsize=(9.6, 5.2), dpi=100)
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    axis.text(0.5, 0.94, title, ha="center", va="center", fontsize=24, color="#16232a")
    top, bottom = 0.82, 0.10
    step = (top - bottom) / max(len(labels), 1)
    bar_height = min(0.11, step * 0.72)
    for index, (label, value) in enumerate(zip(labels, values)):
        y = top - index * step - bar_height / 2
        width = 0.76 * value / maximum
        axis.text(0.29, y + bar_height / 2, label[:32], ha="right", va="center",
                  fontsize=13, color="#27343b")
        axis.barh(y + bar_height / 2, width, left=0.31, height=bar_height,
                  color=color, edgecolor="none")
        axis.text(0.31 + width + 0.008, y + bar_height / 2,
                  value_format.format(value), ha="left", va="center",
                  fontsize=13, color="#27343b")
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def save_queue_figures(queue: pd.DataFrame, figures_dir: Path) -> None:
    confidence = queue.assign(
        confidence_state=queue.apply(confidence_state, axis=1)
    )
    save_count_plot(
        confidence["confidence_state"].value_counts().reindex(
            ["high", "medium", "low"], fill_value=0
        ),
        "Review queue confidence mix",
        figures_dir / "confidence_mix.png",
        "#6F4E7C",
        value_format="{:,.0f}",
    )

    reason_sets = queue.apply(
        lambda row: set(
            [row["primary_reason_code"]]
            + str(row["supporting_reason_codes"]).split("|")
        )
        - {"", "none"},
        axis=1,
    )
    reason_counts = pd.Series(
        reason for reasons in reason_sets for reason in reasons
    ).value_counts()
    save_count_plot(
        reason_counts.sort_values(ascending=False),
        "All refresh reason codes",
        figures_dir / "reason_code_mix.png",
        "#8C6BB1",
        value_format="{:,.0f}",
    )


def save_feature_importance_plot(
    feature_influence: list[dict[str, object]], figures_dir: Path
) -> None:
    influence = pd.DataFrame(feature_influence).sort_values("mean_score_decrease")
    labels = influence["feature"].astype(str).tolist()
    values = influence["mean_score_decrease"].to_numpy(dtype=float)
    deviations = influence["std_score_decrease"].to_numpy(dtype=float)
    maximum = max(abs(values).max() if len(values) else 0, 0.001)
    fig, axis = plt.subplots(figsize=(9.6, 5.2), dpi=100)
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    axis.text(0.5, 0.94, "Top model feature influence", ha="center",
              va="center", fontsize=24, color="#16232a")
    axis.text(0.59, 0.06, "permutation mean score decrease", ha="center",
              va="center", fontsize=12, color="#27343b")
    top, bottom = 0.82, 0.12
    step = (top - bottom) / max(len(labels), 1)
    bar_height = min(0.07, step * 0.72)
    zero = 0.59
    scale = 0.34 / maximum
    for index, (label, value) in enumerate(zip(labels, values)):
        y = top - index * step - bar_height / 2
        width = abs(value) * scale
        left = zero if value >= 0 else zero - width
        axis.text(0.185, y + bar_height / 2, label[:32], ha="right", va="center",
                  fontsize=13, color="#27343b")
        axis.barh(y + bar_height / 2, width, left=left, height=bar_height,
                  color="#4E79A7" if value >= 0 else "#E15759", edgecolor="none")
        axis.errorbar(zero + value * scale, y + bar_height / 2,
                      xerr=deviations[index] * scale, fmt="none",
                      ecolor="#27343b", elinewidth=1, capsize=2)
        axis.text(left + width + 0.008 if value >= 0 else left - 0.008,
                  y + bar_height / 2, f"{value:.3f}",
                  ha="left" if value >= 0 else "right", va="center",
                  fontsize=13, color="#27343b")
    axis.plot([zero, zero], [bottom - 0.01, top + 0.01], color="#333333", linewidth=0.8)
    fig.tight_layout()
    fig.savefig(figures_dir / "feature_importance.png", dpi=160)
    plt.close(fig)


def save_label_distribution_plot(
    data: pd.DataFrame, figures_dir: Path
) -> None:
    tier_order = ["top_3", "page_1", "striking", "page_3_5", "deep"]
    frame = data[data["position_tier"].isin(tier_order)].copy()
    frame["label_status"] = np.select(
        [
            ~frame["label_eligible"],
            frame["target"].eq(1),
        ],
        ["unqualified", "positive"],
        default="negative",
    )
    counts = (
        frame.groupby(["position_tier", "label_status"])
        .size()
        .unstack(fill_value=0)
        .reindex(index=tier_order, fill_value=0)
        .reindex(columns=["positive", "negative", "unqualified"], fill_value=0)
    )
    fig, axis = plt.subplots(figsize=(9.6, 5.2), dpi=100)
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    axis.text(0.5, 0.94, "Label distribution by position tier", ha="center",
              va="center", fontsize=24, color="#16232a")
    maximum = max(float(counts.sum(axis=1).max()), 1)
    colors = {"positive": "#59A14F", "negative": "#E15759", "unqualified": "#BAB0AC"}
    top, bottom = 0.82, 0.17
    step = (top - bottom) / max(len(counts), 1)
    bar_height = min(0.10, step * 0.70)
    for index, (tier, row) in enumerate(counts.iterrows()):
        y = top - index * step - bar_height / 2
        axis.text(0.29, y + bar_height / 2, str(tier), ha="right", va="center",
                  fontsize=13, color="#27343b")
        left = 0.31
        for status in ["positive", "negative", "unqualified"]:
            value = float(row[status])
            width = 0.76 * value / maximum
            axis.barh(y + bar_height / 2, width, left=left, height=bar_height,
                      color=colors[status], edgecolor="none")
            if value and width >= 0.08:
                axis.text(left + width / 2, y + bar_height / 2, f"{value:,.0f}",
                          ha="center", va="center", fontsize=10, color="white")
            left += width
    handles = [
        plt.Rectangle((0, 0), 1, 1, color=colors[status])
        for status in ["positive", "negative", "unqualified"]
    ]
    axis.legend(handles, ["positive", "negative", "unqualified"],
                loc="lower center", bbox_to_anchor=(0.59, 0.03), ncol=3,
                frameon=False, fontsize=11)
    fig.tight_layout()
    fig.savefig(figures_dir / "label_distribution.png", dpi=160)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ML-08 model comparison.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    connection = connect()
    all_data, model_data = load_contract(connection)
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
            "feature_eligible",
            "known_tier",
            "position_tier",
            "ga4_available_90d",
            "sessions_90d",
            "engagement_rate_feature",
            "engagement_available",
            "tier_support_rows",
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
    review["low_ctr_rule"] = review["ctr_feature"] < 0.5
    review["primary_reason_code"] = np.select(
        [
            ~review["feature_eligible"],
            ~review["known_tier"],
            review["feature_eligible"]
            & review["known_tier"]
            & review["low_ctr_rule"],
        ],
        ["insufficient_feature_volume", "no_position_data", "low_ctr"],
        default="no_action",
    )
    review["supporting_reason_codes"] = review.apply(supporting_reasons, axis=1)
    review["suggested_action"] = review.apply(suggested_action, axis=1)
    review["confidence_note"] = review.apply(confidence_note, axis=1)
    queue = review.sort_values(
        ["model_score", "content_hash_id"], ascending=[False, True], kind="stable"
    ).reset_index(drop=True)
    queue.insert(0, "rank", np.arange(1, len(queue) + 1))
    queue["model_signal_codes"] = np.select(
        [
            queue["error_type"].eq("false_positive"),
            queue["error_type"].eq("false_negative"),
            queue["model_rank"].le(REVIEW_BUDGET)
            & queue["baseline_rank"].gt(REVIEW_BUDGET),
            queue["model_score"].between(0.4, 0.6),
        ],
        [
            "model_false_positive_review",
            "model_false_negative_review",
            "model_baseline_disagreement",
            "model_low_confidence",
        ],
        default="model_ranked_lower_priority",
    )
    queue["model_signal_note"] = np.where(
        queue["model_rank"] <= REVIEW_BUDGET,
        "model-ranked high priority; review observed feature reasons",
        "model-ranked lower priority; retain manual review context",
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
            "primary_reason_code",
            "supporting_reason_codes",
            "suggested_action",
            "confidence_note",
            "model_signal_codes",
            "model_signal_note",
            "impressions_90d",
            "ctr_feature",
            "expected_ctr_feature",
            "error_type",
        ]
    ].to_csv(output_dir / "ml08_model_queue.csv", index=False)

    error_examples = {}
    for error_type in ["false_positive", "false_negative"]:
        error_examples[error_type] = (
            queue[queue["error_type"] == error_type]
            .head(10)[
                [
                    "rank",
                    "content_hash_id",
                    "client_hash_id",
                    "model_score",
                    "baseline_score",
                    "target",
                    "error_type",
                ]
            ]
            .to_dict(orient="records")
        )

    importance = permutation_importance(
        best_pipeline,
        X_test,
        y_test,
        scoring="average_precision",
        n_repeats=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )
    feature_influence = [
        {
            "feature": feature,
            "mean_score_decrease": float(mean),
            "std_score_decrease": float(std),
        }
        for feature, mean, std in sorted(
            zip(features, importance.importances_mean, importance.importances_std),
            key=lambda item: item[1],
            reverse=True,
        )
    ]
    split_details = {
        "eligible_rows": int(len(model_data)),
        "eligible_clients": int(model_data["client_hash_id"].nunique()),
        "train_rows": int(len(train)),
        "test_rows": int(len(test)),
        "train_clients": int(train["client_hash_id"].nunique()),
        "test_clients": int(test["client_hash_id"].nunique()),
        "client_overlap": int(
            len(set(train["client_hash_id"]) & set(test["client_hash_id"]))
        ),
        "train_positive_rate": float(train["target"].mean()),
        "test_positive_rate": float(test["target"].mean()),
    }
    leakage_checks = {
        "feature_window_before_label_window": FEATURE_END < LABEL_START,
        "future_fields_excluded_from_features": not any(
            "next30" in feature or "target" in feature for feature in features
        ),
        "identifiers_excluded_from_features": not any(
            "client" in feature or "content" in feature for feature in features
        ),
        "train_test_clients_disjoint": split_details["client_overlap"] == 0,
        "duplicate_test_grain": not test[
            ["client_hash_id", "content_hash_id"]
        ].duplicated().any(),
    }
    assert all(leakage_checks.values())

    metrics_payload = {
        "task": "ML-08",
        "random_state": RANDOM_STATE,
        "feature_window": [FEATURE_START, FEATURE_END],
        "label_window": [LABEL_START, LABEL_END],
        "target": "future CTR below half of feature position-tier pooled CTR",
        "split_strategy": f"GroupShuffleSplit by client_hash_id, test_size={HOLDOUT_TEST_SIZE}",
        "split_details": split_details,
        "held_out_clients": split_details["test_clients"],
        "feature_columns": features,
        "comparison": comparison.astype(object)
        .where(pd.notna(comparison), None)
        .to_dict(orient="records"),
        "client_balanced_comparison": client_balanced,
        "best_learned_model": best_model_name,
        "review_budget": REVIEW_BUDGET,
        "error_examples": error_examples,
        "feature_influence": feature_influence,
        "leakage_checks": leakage_checks,
        "queue_output": "work/outputs/ml08_model_queue.csv",
    }
    write_json(output_dir / "ml08_model_metrics.json", metrics_payload)
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    save_queue_figures(queue, FIGURES_DIR)
    save_feature_importance_plot(feature_influence, FIGURES_DIR)
    save_label_distribution_plot(all_data, FIGURES_DIR)
    report_lines = [
        "# ML-08 model comparison",
        "",
        f"- Feature window: `{FEATURE_START}` to `{FEATURE_END}`",
        f"- Label window: `{LABEL_START}` to `{LABEL_END}`",
        f"- Split: grouped by client, seed `{RANDOM_STATE}`, test size `20%`",
        f"- Eligible rows/clients: **{split_details['eligible_rows']:,}** / **{split_details['eligible_clients']}**",
        f"- Train rows/clients: **{split_details['train_rows']:,}** / **{split_details['train_clients']}**",
        f"- Held-out rows/clients: **{split_details['test_rows']:,}** / **{split_details['test_clients']}**",
        f"- Client overlap: **{split_details['client_overlap']}**",
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
            "Top false positives and false negatives at the fixed review budget:",
            "",
            "| Error type | Rank | Content ID | Model score | Baseline score | Target |",
            "|---|---:|---|---:|---:|---:|",
        ]
        + [
            f"| {row['error_type']} | {row['rank']} | `{row['content_hash_id']}` | "
            f"{row['model_score']:.4f} | {row['baseline_score']:.1f} | {row['target']} |"
            for error_type in ["false_positive", "false_negative"]
            for row in error_examples[error_type]
        ]
        + [
            "",
            "ML-07-compatible observed reason codes and actions are retained in the ML-08 queue. Model signal codes are separate ranking context, not causal explanations.",
            "",
            "| Rank | Primary reason | Supporting reasons | Suggested action | Model signal |",
            "|---:|---|---|---|---|",
        ]
        + [
            f"| {row['rank']} | {row['primary_reason_code']} | "
            f"{row['supporting_reason_codes']} | {row['suggested_action']} | "
            f"{row['model_signal_codes']} |"
            for row in queue.head(10).to_dict(orient="records")
        ]
        + [
            "",
            "Permutation feature influence on held-out average precision:",
            "",
            "| Feature | Mean score decrease | Standard deviation |",
            "|---|---:|---:|",
        ]
        + [
            f"| `{row['feature']}` | {row['mean_score_decrease']:.6f} | "
            f"{row['std_score_decrease']:.6f} |"
            for row in feature_influence
        ]
        + [
            "",
            "Leakage checks:",
            "",
        ]
        + [
            f"- `{name}`: **{'PASS' if passed else 'FAIL'}**"
            for name, passed in leakage_checks.items()
        ]
        + [
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
    print(f"Wrote {'ml08_model_queue.csv'}")
    print(f"Wrote {'ml08_model_metrics.json'}")
    print(f"Wrote {'ml08_model_report.md'}")


if __name__ == "__main__":
    main()
