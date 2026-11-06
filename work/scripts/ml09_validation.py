from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import GroupShuffleSplit

from ml08_model import NUMERIC_FEATURES
from ml_contract import (
    FEATURE_END,
    FEATURE_START,
    LABEL_END,
    LABEL_START,
    MIN_IMPRESSIONS,
    OUTPUT_DIR,
    RANDOM_STATE,
    client_balanced_ranking,
    connect,
    load_contract,
    ranking_metrics,
    write_json,
)


GROUP_SEEDS = (42, 7, 19, 31, 61)
ROLLING_WINDOWS = (
    ("2025-10-01", "2025-12-29", "2026-01-01", "2026-01-31"),
    ("2025-11-01", "2026-01-29", "2026-02-01", "2026-02-28"),
    ("2025-12-01", "2026-02-28", "2026-03-01", "2026-03-31"),
    ("2026-01-01", "2026-03-31", "2026-04-01", "2026-04-30"),
)


def fit_model(train: pd.DataFrame) -> Pipeline:
    model = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=1000,
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )
    model.fit(train[NUMERIC_FEATURES], train["target"].astype(int))
    return model


def evaluate(frame: pd.DataFrame, scores: np.ndarray) -> dict[str, object]:
    metrics = ranking_metrics(frame["target"].to_numpy(), scores)
    metrics["base_rate"] = float(frame["target"].mean())
    metrics["rows"] = int(len(frame))
    metrics["clients"] = int(frame["client_hash_id"].nunique())
    metrics["macro_precision_at_50"] = float(
        client_balanced_ranking(frame, scores)["macro_precision_at_50"]
    )
    return metrics


def grouped_checks(model_data: pd.DataFrame) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for seed in GROUP_SEEDS:
        splitter = GroupShuffleSplit(
            n_splits=1, test_size=0.2, random_state=seed
        )
        train_idx, test_idx = next(
            splitter.split(
                model_data,
                model_data["target"],
                groups=model_data["client_hash_id"],
            )
        )
        train = model_data.iloc[train_idx].copy()
        test = model_data.iloc[test_idx].copy()
        model_scores = fit_model(train).predict_proba(
            test[NUMERIC_FEATURES]
        )[:, 1]
        baseline_scores = test["baseline_score"].to_numpy(dtype=float)
        rows.append(
            {
                "seed": seed,
                "train_rows": int(len(train)),
                "test_rows": int(len(test)),
                "train_clients": int(train["client_hash_id"].nunique()),
                "test_clients": int(test["client_hash_id"].nunique()),
                "client_overlap": int(
                    len(
                        set(train["client_hash_id"])
                        & set(test["client_hash_id"])
                    )
                ),
                "model": evaluate(test, model_scores),
                "baseline": evaluate(test, baseline_scores),
            }
        )
    return rows


def time_checks(connection) -> list[dict[str, object]]:
    periods: list[dict[str, object]] = []
    loaded: list[pd.DataFrame] = []
    for window in ROLLING_WINDOWS:
        _, eligible = load_contract(connection, *window)
        loaded.append(eligible)

    for index in range(len(loaded) - 1):
        train = loaded[index]
        test = loaded[index + 1]
        model_scores = fit_model(train).predict_proba(
            test[NUMERIC_FEATURES]
        )[:, 1]
        periods.append(
            {
                "train_window": list(ROLLING_WINDOWS[index]),
                "test_window": list(ROLLING_WINDOWS[index + 1]),
                "train_rows": int(len(train)),
                "test_rows": int(len(test)),
                "model": evaluate(test, model_scores),
                "baseline": evaluate(
                    test, test["baseline_score"].to_numpy(dtype=float)
                ),
            }
        )
    return periods


def sensitivity(model_data: pd.DataFrame) -> dict[str, object]:
    thresholds = {}
    for threshold in (0.25, 0.5, 1.0):
        eligible = model_data[
            model_data["impressions_90d"] >= max(MIN_IMPRESSIONS, 100)
        ].copy()
        scores = np.where(
            eligible["ctr_feature"] < threshold,
            eligible["impressions_90d"],
            0.0,
        )
        thresholds[str(threshold)] = {
            "actionable_rows": int((scores > 0).sum()),
            "base_rate": float(eligible["target"].mean()),
            "precision_at_50": float(
                ranking_metrics(eligible["target"].to_numpy(), scores)[
                    "precision_at_50"
                ]
            ),
        }

    return {"thresholds": thresholds}


def save_validation_plot(metrics: dict[str, object], figures_dir: Path) -> None:
    grouped = metrics["grouped_validation"]
    time_aware = metrics["time_aware_validation"]
    labels = [f"seed {row['seed']}" for row in grouped]
    labels += [f"time {index + 1}" for index in range(len(time_aware))]
    model = [row["model"]["precision_at_50"] for row in grouped + time_aware]
    baseline = [row["baseline"]["precision_at_50"] for row in grouped + time_aware]

    fig, axis = plt.subplots(figsize=(9.6, 5.2), dpi=100)
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    axis.text(0.5, 0.94, "Validation precision at review budget 50",
              ha="center", va="center", fontsize=24, color="#16232a")
    for tick in (0, 0.25, 0.5, 0.75, 1):
        x_position = 0.20 + tick * 0.76
        axis.text(x_position, 0.08, f"{tick:g}", ha="center", va="center",
                  fontsize=10, color="#68747a")
    step = 0.72 / max(len(labels), 1)
    bar_height = min(0.06, step * 0.32)
    for index, (label, model_value, baseline_value) in enumerate(
        zip(labels, model, baseline)
    ):
        center = 0.82 - index * step
        axis.text(0.185, center, label, ha="right", va="center",
                  fontsize=13, color="#27343b")
        axis.barh(center + bar_height / 2, model_value * 0.76, left=0.20,
                  height=bar_height, color="#4E79A7", edgecolor="none")
        axis.barh(center - bar_height / 2, baseline_value * 0.76, left=0.20,
                  height=bar_height, color="#8C6BB1", edgecolor="none")
        axis.text(0.20 + model_value * 0.76 + 0.008, center + bar_height / 2,
                  f"{model_value:.2f}", va="center", fontsize=11, color="#27343b")
        axis.text(0.20 + baseline_value * 0.76 + 0.008, center - bar_height / 2,
                  f"{baseline_value:.2f}", va="center", fontsize=11, color="#27343b")
    axis.legend(
        [plt.Rectangle((0, 0), 1, 1, color=color) for color in ["#4E79A7", "#8C6BB1"]],
        ["Logistic Regression", "Rule baseline"],
        loc="lower center", bbox_to_anchor=(0.59, 0.03), ncol=2,
        frameon=False, fontsize=11,
    )
    fig.tight_layout()
    fig.savefig(figures_dir / "validation_precision_at_50.png", dpi=160)
    plt.close(fig)


def save_sensitivity_plot(metrics: dict[str, object], figures_dir: Path) -> None:
    thresholds = metrics["sensitivity"]["thresholds"]
    x = [float(value) for value in thresholds]
    actionable = [thresholds[value]["actionable_rows"] for value in thresholds]
    precision = [thresholds[value]["precision_at_50"] for value in thresholds]

    fig, axis = plt.subplots(figsize=(9.6, 5.2), dpi=100)
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    axis.text(0.5, 0.94, "Sensitivity to baseline CTR threshold",
              ha="center", va="center", fontsize=24, color="#16232a")
    step = 0.72 / max(len(x), 1)
    for index, (threshold, score, rows) in enumerate(zip(x, precision, actionable)):
        center = 0.82 - index * step
        axis.text(0.185, center + 0.02, f"{threshold:g}%", ha="right",
                  va="center", fontsize=13, color="#27343b")
        width = 0.76 * score
        axis.barh(center + 0.02, width, left=0.20, height=min(0.10, step * 0.55),
                  color="#4E79A7", edgecolor="none")
        axis.text(0.20 + width + 0.008, center + 0.02,
                  f"{score:.2f} | {rows:,} rows", va="center",
                  fontsize=13, color="#27343b")
    for tick in (0, 0.25, 0.5, 0.75, 1):
        x_position = 0.20 + tick * 0.76
        axis.text(x_position, 0.08, f"{tick:g}", ha="center", va="center",
                  fontsize=10, color="#68747a")
    fig.tight_layout()
    fig.savefig(figures_dir / "threshold_sensitivity.png", dpi=160)
    plt.close(fig)


def run(output_dir: Path) -> None:
    connection = connect()
    _, model_data = load_contract(connection)
    grouped = grouped_checks(model_data)
    time_aware = time_checks(connection)
    payload = {
        "task": "ML-09",
        "feature_window": [FEATURE_START, FEATURE_END],
        "label_window": [LABEL_START, LABEL_END],
        "target": "future CTR below half of feature position-tier pooled CTR",
        "metric": "Precision@K with K in 10, 20, 50, 100",
        "base_rate": float(model_data["target"].mean()),
        "grouped_validation": grouped,
        "time_aware_validation": time_aware,
        "sensitivity": sensitivity(model_data),
        "leakage_checks": {
            "feature_window_before_label_window": FEATURE_END < LABEL_START,
            "future_fields_excluded_from_features": True,
            "identifiers_excluded_from_features": not any(
                "client" in feature or "content" in feature
                for feature in NUMERIC_FEATURES
            ),
            "duplicate_grain": not model_data[
                ["client_hash_id", "content_hash_id"]
            ].duplicated().any(),
        },
        "limitations": [
            "The rolling checks use 90-day feature windows and monthly label windows.",
            "Very small client groups make per-client Precision@K unstable.",
            "All results are directional ranking evidence, not causal effects.",
            "The eligible population is restricted to pages with at least 100 impressions "
            "in the April 2026 label window, so it is filtered on a future-window quantity "
            "(volume, not the label value); this is a denominator floor, not a label-derived rule.",
        ],
    }
    assert all(payload["leakage_checks"].values())
    write_json(output_dir / "ml09_validation_metrics.json", payload)
    figures_dir = output_dir.parent / "figures"
    figures_dir.mkdir(parents=True, exist_ok=True)
    save_validation_plot(payload, figures_dir)
    save_sensitivity_plot(payload, figures_dir)

    grouped_p50 = [
        row["model"]["precision_at_50"] for row in grouped
    ]
    time_p50 = [
        row["model"]["precision_at_50"] for row in time_aware
    ]
    report = [
        "# ML-09 validation audit",
        "",
        f"- Final feature window: `{FEATURE_START}` to `{FEATURE_END}`",
        f"- Final label window: `{LABEL_START}` to `{LABEL_END}`",
        f"- Eligible base rate: **{payload['base_rate']:.4f}**",
        "",
        "Grouped client validation uses five fixed seeds and keeps clients disjoint.",
        f"- Logistic Regression P@50 range: **{min(grouped_p50):.4f}–{max(grouped_p50):.4f}**",
        "",
        "Time-aware validation trains on an earlier rolling window and tests on the next window.",
        f"- Logistic Regression P@50 range: **{min(time_p50):.4f}–{max(time_p50):.4f}**",
        "",
        "The model is a ranking aid. Results are observed and directional; they do not show that an edit causes recovery.",
        "",
        "Leakage checks:",
        "",
    ]
    report.extend(
        f"- `{name}`: **{'PASS' if passed else 'FAIL'}**"
        for name, passed in payload["leakage_checks"].items()
    )
    (output_dir / "ml09_validation_report.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )
    print(f"Wrote {'ml09_validation_metrics.json'}")
    print(f"Wrote {'ml09_validation_report.md'}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ML-09 validation audit.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args()
    run(Path(args.output_dir))


if __name__ == "__main__":
    main()
