from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
METRICS_PATH = ROOT / "work" / "outputs" / "ml09_validation_metrics.json"
FIGURES_DIR = ROOT / "work" / "figures"


def save_validation_plot(metrics: dict) -> None:
    grouped = metrics["grouped_validation"]
    time_aware = metrics["time_aware_validation"]
    labels = [f"seed {row['seed']}" for row in grouped]
    labels += [f"time {index + 1}" for index in range(len(time_aware))]
    model = [row["model"]["precision_at_50"] for row in grouped + time_aware]
    baseline = [row["baseline"]["precision_at_50"] for row in grouped + time_aware]

    fig, axis = plt.subplots(figsize=(8, 4.5))
    positions = range(len(labels))
    axis.bar([p - 0.18 for p in positions], model, width=0.36, label="Logistic Regression")
    axis.bar([p + 0.18 for p in positions], baseline, width=0.36, label="Rule baseline")
    axis.set_xticks(list(positions), labels, rotation=35, ha="right")
    axis.set_ylim(0, 1)
    axis.set_ylabel("Precision@50")
    axis.set_title("ML-09 validation precision at review budget 50")
    axis.legend()
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "ml09_validation_precision_at_50.png", dpi=160)
    plt.close(fig)


def save_sensitivity_plot(metrics: dict) -> None:
    thresholds = metrics["sensitivity"]["thresholds"]
    x = [float(value) for value in thresholds]
    actionable = [thresholds[value]["actionable_rows"] for value in thresholds]
    precision = [thresholds[value]["precision_at_50"] for value in thresholds]

    fig, axis = plt.subplots(figsize=(7, 4.5))
    axis.plot(x, precision, marker="o", color="#1f77b4")
    axis.set_xlabel("CTR threshold (%)")
    axis.set_ylabel("Precision@50")
    axis.set_ylim(0, 1)
    axis.set_title("Sensitivity to baseline CTR threshold")
    for threshold, score, rows in zip(x, precision, actionable):
        axis.annotate(f"{score:.2f}\n{rows:,} rows", (threshold, score), textcoords="offset points", xytext=(0, 8), ha="center")
    fig.tight_layout()
    fig.savefig(FIGURES_DIR / "ml09_threshold_sensitivity.png", dpi=160)
    plt.close(fig)


def main() -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    save_validation_plot(metrics)
    save_sensitivity_plot(metrics)
    print(f"Wrote figures to {FIGURES_DIR}")


if __name__ == "__main__":
    main()