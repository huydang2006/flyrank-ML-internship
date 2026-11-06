from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "work" / "outputs"
FIGURES_DIR = ROOT / "work" / "figures"
METRICS_PATH = OUTPUT_DIR / "ml09_validation_metrics.json"
QUEUE_PATH = OUTPUT_DIR / "ml08_model_queue.csv"
PUBLIC_QUEUE_PATH = OUTPUT_DIR / "ml10_action_queue_public.csv"
ACTION_MIX_PATH = FIGURES_DIR / "top50_action_mix.png"


def export_public_queue() -> int:
    hidden = {"content_hash_id", "client_hash_id"}
    with QUEUE_PATH.open(newline="", encoding="utf-8") as source, PUBLIC_QUEUE_PATH.open(
        "w", newline="", encoding="utf-8"
    ) as target:
        reader = csv.DictReader(source)
        fields = [field for field in reader.fieldnames or [] if field not in hidden]
        writer = csv.DictWriter(target, fieldnames=fields)
        writer.writeheader()
        count = 0
        for row in reader:
            writer.writerow({field: row[field] for field in fields})
            count += 1
    return count


def save_action_mix_plot() -> None:
    with PUBLIC_QUEUE_PATH.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))[:50]
    counts: dict[str, int] = {}
    for row in rows:
        action = row["suggested_action"]
        counts[action] = counts.get(action, 0) + 1
    raw_labels = list(reversed(counts))
    labels = raw_labels
    values = [counts[label] for label in raw_labels]

    fig, axis = plt.subplots(figsize=(11, 5.2), dpi=100)
    axis.set_xlim(0, 1)
    axis.set_ylim(0, 1)
    axis.axis("off")
    axis.text(0.5, 0.94, "Suggested action mix at review budget 50",
              ha="center", va="center", fontsize=24, color="#16232a")
    maximum = max(values) if values else 1
    step = 0.72 / max(len(labels), 1)
    for index, (label, value) in enumerate(zip(labels, values)):
        center = 0.82 - index * step
        axis.text(0.30, center, label[:32], ha="right", va="center",
                  fontsize=11, color="#27343b")
        width = 0.76 * value / maximum
        axis.barh(center, width, left=0.32, height=min(0.11, step * 0.70),
                  color="#426B69", edgecolor="none")
        axis.text(0.32 + width + 0.008, center, f"{value:,}",
                  va="center", fontsize=13, color="#27343b")
    fig.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(ACTION_MIX_PATH, dpi=160)
    plt.close(fig)

def main() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    queue_rows = export_public_queue()
    save_action_mix_plot()
    print(f"Wrote {'ml10_action_queue_public.csv'}")


if __name__ == "__main__":
    main()