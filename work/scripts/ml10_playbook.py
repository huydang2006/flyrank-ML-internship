from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "work" / "outputs"
METRICS_PATH = OUTPUT_DIR / "ml09_validation_metrics.json"
QUEUE_PATH = OUTPUT_DIR / "ml08_model_queue.csv"
PUBLIC_QUEUE_PATH = OUTPUT_DIR / "ml10_action_queue_public.csv"
REPORT_PATH = OUTPUT_DIR / "ml10_action_playbook.md"


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
        "- Pseudonymous client and content identifiers are omitted from the paper-facing queue.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8"))
    queue_rows = export_public_queue()
    write_report(metrics, queue_rows)
    print(f"Wrote {PUBLIC_QUEUE_PATH}")
    print(f"Wrote {REPORT_PATH}")


if __name__ == "__main__":
    main()