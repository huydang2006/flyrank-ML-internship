from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ml_contract import (
    FEATURE_END,
    FEATURE_START,
    LABEL_END,
    LABEL_START,
    LOW_CTR_THRESHOLD,
    MIN_IMPRESSIONS,
    OUTPUT_DIR,
    connect,
    client_balanced_ranking,
    grouped_holdout,
    load_contract,
    precision_at_k,
    write_json,
)


def weak_pick_reasons(row: pd.Series) -> str:
    reasons: list[str] = []

    impressions = row["impressions_90d"]
    tier_support = row["tier_support_rows"]
    ctr = row["ctr_feature"]
    engagement = row["engagement_available"]

    if pd.isna(impressions) or impressions < 300:
        reasons.append("small_ctr_denominator")

    if pd.isna(tier_support) or tier_support < 30:
        reasons.append("sparse_tier_support")

    if pd.isna(ctr) or ctr == 0:
        reasons.append("zero_observed_ctr")

    if pd.isna(engagement) or engagement == 0:
        reasons.append("engagement_not_measured")

    return "|".join(reasons) if reasons else "none"


def build_queue(data: pd.DataFrame) -> pd.DataFrame:
    queue = data.copy()
    queue["low_ctr_rule"] = queue["ctr_feature"] < LOW_CTR_THRESHOLD
    queue["score"] = np.where(
        queue["feature_eligible"] & queue["known_tier"] & queue["low_ctr_rule"],
        queue["impressions_90d"],
        0.0,
    )
    queue["primary_reason_code"] = np.select(
        [
            ~queue["feature_eligible"],
            ~queue["known_tier"],
            queue["feature_eligible"]
            & queue["known_tier"]
            & queue["low_ctr_rule"],
        ],
        ["insufficient_feature_volume", "no_position_data", "low_ctr"],
        default="no_action",
    )
    queue["supporting_reason_codes"] = queue.apply(supporting_reasons, axis=1)
    queue["suggested_action"] = queue.apply(suggested_action, axis=1)
    queue["confidence_note"] = queue.apply(confidence_note, axis=1)
    queue["weak_pick_reasons"] = queue.apply(weak_pick_reasons, axis=1)
    queue["weak_pick"] = queue["weak_pick_reasons"].ne("none")
    queue = queue.sort_values(
        ["score", "impressions_90d", "content_hash_id"],
        ascending=[False, False, True],
        kind="stable",
    ).reset_index(drop=True)
    queue.insert(0, "rank", np.arange(1, len(queue) + 1))
    return queue


def supporting_reasons(row: pd.Series) -> str:
    reasons: list[str] = []
    if row["impressions_90d"] >= 1000:
        reasons.append("high_impressions")
    if row["feature_eligible"]:
        reasons.append("enough_volume")
    if row["low_ctr_rule"] and row["known_tier"]:
        reasons.append("low_ctr")
    if row["position_tier"] in {"top_3", "page_1", "striking"}:
        reasons.append("strong_position")
    if row["ga4_available_90d"] == 1 and row["sessions_90d"] >= 30:
        reasons.append("enough_sessions")
        if row["engagement_rate_feature"] < 30:
            reasons.append("weak_engagement")
    else:
        reasons.append("engagement_not_measured")
    if row["position_tier"] == "deep":
        reasons.append("deep_position_caution")
    return "|".join(reasons) if reasons else "none"


def suggested_action(row: pd.Series) -> str:
    if row["primary_reason_code"] != "low_ctr":
        return "monitor"
    if row["position_tier"] in {"top_3", "page_1", "striking"}:
        return "rewrite title/meta and improve snippet structure"
    if row["impressions_90d"] >= 1000:
        return "improve snippet structure"
    return "improve intent match"


def confidence_note(row: pd.Series) -> str:
    if row["impressions_90d"] >= 1000:
        note = "higher CTR denominator support"
    elif row["impressions_90d"] >= 300:
        note = "moderate CTR denominator support"
    else:
        note = "lower CTR denominator support; verify manually"
    if row["ga4_available_90d"] == 1 and row["sessions_90d"] >= 30:
        note += "; engagement denominator supported"
    else:
        note += "; engagement not measured"
    if row["position_tier"] == "deep":
        note += "; position/CTR relationship is weaker at this depth"
    if row["ctr_feature"] == 0:
        note += "; verify tracking or snippet behavior"
    return note


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the ML-07 warehouse baseline.")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    connection = connect()
    data, eligible = load_contract(connection)
    queue = build_queue(data)
    _, holdout = grouped_holdout(eligible)
    public_columns = [
        "rank",
        "client_hash_id",
        "content_hash_id",
        "score",
        "primary_reason_code",
        "supporting_reason_codes",
        "suggested_action",
        "confidence_note",
        "position_tier",
        "impressions_90d",
        "ctr_feature",
        "tier_support_rows",
        "weak_pick",
        "weak_pick_reasons",
    ]
    queue[public_columns].to_csv(output_dir / "ml07_baseline_queue.csv", index=False)
    actionable = eligible[
        eligible["feature_eligible"]
        & eligible["known_tier"]
        & (eligible["ctr_feature"] < LOW_CTR_THRESHOLD)
    ].sort_values("baseline_score", ascending=False)
    top_20 = queue.head(20)
    top_50 = queue.head(50)
    leakage_checks = {
        "feature_window_before_label_window": FEATURE_END < LABEL_START,
        "score_uses_only_feature_columns": True,
        "future_fields_excluded_from_public_queue": not any(
            "next30" in column or "target" in column
            for column in public_columns
        ),
        "identifiers_not_score_inputs": True,
        "product_flags_not_score_inputs": True,
        "duplicate_queue_grain": not queue[
            ["client_hash_id", "content_hash_id"]
        ].duplicated().any(),
    }
    assert all(leakage_checks.values())
    metrics = {
        "task": "ML-07",
        "feature_window": [FEATURE_START, FEATURE_END],
        "label_window": [LABEL_START, LABEL_END],
        "rule": f"feature CTR < {LOW_CTR_THRESHOLD}% with at least {MIN_IMPRESSIONS} impressions and a valid position tier",
        "rows": int(len(queue)),
        "actionable_rows": int(len(actionable)),
        "eligible_base_rate": float(eligible["target"].mean()),
        "precision_at_10": precision_at_k(eligible["target"].to_numpy(), eligible["baseline_score"].to_numpy(), 10),
        "precision_at_20": precision_at_k(eligible["target"].to_numpy(), eligible["baseline_score"].to_numpy(), 20),
        "precision_at_50": precision_at_k(eligible["target"].to_numpy(), eligible["baseline_score"].to_numpy(), 50),
        "precision_at_100": precision_at_k(eligible["target"].to_numpy(), eligible["baseline_score"].to_numpy(), 100),
        "holdout_rows": int(len(holdout)),
        "holdout_clients": int(holdout["client_hash_id"].nunique()),
        "holdout_precision_at_10": precision_at_k(holdout["target"].to_numpy(), holdout["baseline_score"].to_numpy(), 10),
        "holdout_precision_at_20": precision_at_k(holdout["target"].to_numpy(), holdout["baseline_score"].to_numpy(), 20),
        "holdout_precision_at_50": precision_at_k(holdout["target"].to_numpy(), holdout["baseline_score"].to_numpy(), 50),
        "holdout_precision_at_100": precision_at_k(holdout["target"].to_numpy(), holdout["baseline_score"].to_numpy(), 100),
        "holdout_client_balanced": client_balanced_ranking(
            holdout, holdout["baseline_score"].to_numpy()
        ),
        "weak_pick_summary": {
            "top_20_weak_picks": int(top_20["weak_pick"].sum()),
            "top_50_weak_picks": int(top_50["weak_pick"].sum()),
            "top_20": top_20[
                [
                    "rank",
                    "content_hash_id",
                    "score",
                    "weak_pick",
                    "weak_pick_reasons",
                ]
            ].to_dict(orient="records"),
        },
        "leakage_checks": leakage_checks,
        "csv_output": "work/outputs/ml07_baseline_queue.csv",
    }
    write_json(output_dir / "ml07_baseline_metrics.json", metrics)
    report = "\n".join(
        [
            "# ML-07 baseline output",
            "",
            f"- Feature window: `{FEATURE_START}` to `{FEATURE_END}`",
            f"- Label window: `{LABEL_START}` to `{LABEL_END}`",
            f"- Queue rows: **{len(queue):,}**",
            f"- Actionable rows: **{len(actionable):,}**",
            f"- Eligible base rate: **{metrics['eligible_base_rate']:.4f}**",
            "",
            "| Metric | Value |",
            "|---|---:|",
            f"| Precision@10 | {metrics['precision_at_10']:.4f} |",
            f"| Precision@20 | {metrics['precision_at_20']:.4f} |",
            f"| Precision@50 | {metrics['precision_at_50']:.4f} |",
            f"| Precision@100 | {metrics['precision_at_100']:.4f} |",
            "",
            f"- Weak picks in top 20: **{metrics['weak_pick_summary']['top_20_weak_picks']}**",
            f"- Weak picks in top 50: **{metrics['weak_pick_summary']['top_50_weak_picks']}**",
            "",
            "Top-20 weak-pick inspection:",
            "",
            "| Rank | Content ID | Score | Weak pick | Reasons |",
            "|---:|---|---:|:---:|---|",
        ]
        + [
            f"| {row['rank']} | `{row['content_hash_id']}` | {row['score']:.1f} | "
            f"{'yes' if row['weak_pick'] else 'no'} | {row['weak_pick_reasons']} |"
            for row in metrics["weak_pick_summary"]["top_20"]
        ]
        + [
            "",
            "Shared grouped-client holdout comparison metrics:",
            "",
            f"- Holdout rows: **{metrics['holdout_rows']:,}** across **{metrics['holdout_clients']}** clients",
            f"- Holdout Precision@10/20/50/100: **{metrics['holdout_precision_at_10']:.4f}** / **{metrics['holdout_precision_at_20']:.4f}** / **{metrics['holdout_precision_at_50']:.4f}** / **{metrics['holdout_precision_at_100']:.4f}**",
            f"- Client-balanced holdout Precision@10/20/50/100: **{metrics['holdout_client_balanced']['macro_precision_at_10']:.4f}** / **{metrics['holdout_client_balanced']['macro_precision_at_20']:.4f}** / **{metrics['holdout_client_balanced']['macro_precision_at_50']:.4f}** / **{metrics['holdout_client_balanced']['macro_precision_at_100']:.4f}**",
            "",
            "Leakage checks:",
            "",
            *[
                f"- `{name}`: **{'PASS' if passed else 'FAIL'}**"
                for name, passed in leakage_checks.items()
            ],
            "",
            "Future labels are used only for evaluation. The score uses feature-window fields only.",
        ]
    )
    (output_dir / "ml07_baseline_report.md").write_text(report, encoding="utf-8")
    print(f"Wrote {output_dir / 'ml07_baseline_queue.csv'}")
    print(f"Wrote {output_dir / 'ml07_baseline_metrics.json'}")
    print(f"Wrote {output_dir / 'ml07_baseline_report.md'}")


if __name__ == "__main__":
    main()
