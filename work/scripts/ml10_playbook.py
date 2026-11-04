from __future__ import annotations

import csv
import json
import textwrap
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "work" / "outputs"
FIGURES_DIR = ROOT / "work" / "figures"
METRICS_PATH = OUTPUT_DIR / "ml09_validation_metrics.json"
QUEUE_PATH = OUTPUT_DIR / "ml08_model_queue.csv"
PUBLIC_QUEUE_PATH = OUTPUT_DIR / "ml10_action_queue_public.csv"
REPORT_PATH = OUTPUT_DIR / "ml10_action_playbook.md"
ACTION_MIX_PATH = FIGURES_DIR / "ml10_top50_action_mix.png"


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
    labels = [
        "\n".join(textwrap.wrap(label, width=28, max_lines=2))
        for label in raw_labels
    ]
    values = [counts[label] for label in raw_labels]

    fig, axis = plt.subplots(figsize=(8, 4.5))
    axis.barh(labels, values, color="#1f77b4")
    axis.set_xlabel("Rows in top-50 review queue")
    axis.set_title("ML-10 suggested action mix at review budget 50")
    axis.set_xlim(0, max(values) + 5)
    for index, value in enumerate(values):
        axis.text(value + 0.3, index, str(value), va="center")
    fig.tight_layout()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(ACTION_MIX_PATH, dpi=160)
    plt.close(fig)


def write_report(metrics: dict, queue_rows: int) -> None:
    grouped = metrics["grouped_validation"]
    time_aware = metrics["time_aware_validation"]
    grouped_scores = [row["model"]["precision_at_50"] for row in grouped]
    time_scores = [row["model"]["precision_at_50"] for row in time_aware]
    lines = [
        "# ML-10 action playbook",
        "",
        "## Audience and intended use",
        "",
        "This is a portfolio review aid for an SEO/content specialist. It ranks pages for human review; it does not automate edits or prove that an edit will improve traffic or CTR.",
        "",
        "## Ranked actions and reason codes",
        "",
        "Review the first 50 rows per cycle. Keep the observed reason code, supporting signals, suggested action, confidence note, and model signal note together. Treat the score as prioritization evidence, not a causal explanation.",
        "",
        "## Review capacity and confidence boundaries",
        "",
        "- Default capacity: 50 pages per review cycle.",
        "- Require adequate impressions, a measurable CTR denominator, and agreement between reason code and model ranking.",
        "- Keep low-confidence or contradictory rows for human review; do not auto-act.",
        f"- Validation reference: grouped P@50 {min(grouped_scores):.2f}-{max(grouped_scores):.2f}; time-aware P@50 {min(time_scores):.2f}-{max(time_scores):.2f}.",
        "",
        "## Human-review checklist",
        "",
        "1. Confirm page and query context in the source system.",
        "2. Check impression volume and CTR denominator.",
        "3. Compare CTR with the position-tier reference.",
        "4. Inspect title, snippet, intent match, and technical status.",
        "5. Record the chosen action, evidence, and reviewer confidence.",
        "6. Re-measure after a defined observation window.",
        "",
        "## No-go list",
        "",
        "- Do not auto-publish edits from the queue.",
        "- Do not use the queue for hiring or individual performance evaluation.",
        "- Do not infer causality, intent, quality, or business impact from the score alone.",
        "- Do not act on rows below the minimum denominator or missing critical context.",
        "",
        "## Monitoring and retraining triggers",
        "",
        "- Recheck Precision@50 and base rate each evaluation period.",
        "- Review thresholds when base rate or top-50 precision shifts outside the validated range.",
        "- Monitor impressions, CTR, position, missingness, and action mix for drift.",
        "- Retrain only after a new time-aware evaluation preserves feature/label separation.",
        "",
        "## Paper-safe exports",
        "",
        f"- Public queue rows exported: **{queue_rows:,}**.",
        "- The top-50 suggested-action mix is exported as a paper-safe figure.",
        "- Pseudonymous client and content identifiers are omitted from the paper-facing queue.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    queue_rows = export_public_queue()
    save_action_mix_plot()
    write_report(metrics, queue_rows)
    print(f"Wrote {PUBLIC_QUEUE_PATH}")
    print(f"Wrote {REPORT_PATH}")
    print(f"Wrote {ACTION_MIX_PATH}")


if __name__ == "__main__":
    main()