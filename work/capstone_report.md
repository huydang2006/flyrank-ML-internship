# Capstone Report — CTR / Engagement Opportunity Scoring

- **Author:** Mai Huy Đăng
- **Lane:** 4 (CTR / Engagement Opportunity Scoring)
- **Repo:** <https://github.com/huydang2006/flyrank-ML-internship>
- **Date:** 2026-11-07

## 0. Abstract

This study asks whether a transparent rule and a grouped client-holdout model can rank visible
pages that under-capture clicks relative to their search-position tier. It uses the FlyRank
internship warehouse, aggregating search and analytics signals from 2026-01-01 through
2026-03-31 and evaluating a future window from 2026-04-01 through 2026-04-30. A
logistic-regression ranking model is compared with a fixed CTR-and-volume rule under the same
client-disjoint split and top-50 review budget. On the recorded holdout, logistic regression
achieved Precision@50 of 0.94 versus 0.72 for the rule baseline, while time-aware validation
ranged from 0.72 to 0.90. The result is a public-safe, human-review prioritization aid rather
than a causal estimate or automated publishing system.

## 1. Problem framing

**Decision supported:** Which visible pages under-capture clicks relative to others in the same
search-position tier and are worth review for content or metadata improvement?

**Unit of analysis:** One pseudonymized content item at the 2026-04-01 decision point,
aggregated by client and content hash.

**Output and action:** A ranked list of CTR underperformers with reason codes, supporting signals,
confidence notes, and suggested review actions. Content reviewers use a fixed review budget to
inspect the highest-ranked candidates.

A false positive spends scarce review capacity on a noisy or low-priority row. A false negative
leaves a potentially reviewable opportunity unseen. A raw CTR threshold ignores position context
and volume, so the tier-adjusted ranking provides useful decision support without automating edits.

## 2. Data safety

The analysis uses the FlyRank internship warehouse release and its daily content-performance fact
table. The feature window is 2026-01-01 through 2026-03-31 and the future label window is
2026-04-01 through 2026-04-30. The evaluated population requires at least 100 impressions in
both windows and a known position tier.

The eight score inputs are `clicks_90d`, `impressions_90d`, `avg_position_feature`,
`sessions_90d`, `engaged_sessions_90d`, `engagement_rate_feature`, `ga4_available_90d`, and
`engagement_available`. Trend fields, future-window fields, product/provider flags, client IDs,
and content IDs are excluded from score inputs. Pseudonymous IDs are used only for joins and
grouped splits. The public queue omits both client and content identifiers.

## 3. Baseline

The baseline flags feature CTR below 0.5% when feature impressions are at least 100 and a valid
position tier exists, then ranks by feature impressions. It uses the same feature/label contract
and grouped holdout as the learned models. On the 2,904-row holdout it achieved P@10 0.70,
P@20 0.75, P@50 0.72, and P@100 0.62. The eligible-population base rate was 0.5856.

## 4. Model / analysis

Logistic regression fits the lane because it produces a compact ranking score from measurable
feature-window signals and is easier to inspect than a more complex alternative. The target is 1
when future-window CTR is below half of the feature-window position-tier expected CTR, subject to
feature and label volume floors and a known position tier.

Random forest is reported as a secondary comparison, not as the selected model. Trend fields,
future-window fields, identifiers, and product/provider flags are deliberately excluded.

## 5. Evaluation

The primary split is grouped by client with seed 42 and a 20% test size: 87,846 training rows
across 33 clients and 2,904 held-out rows across 9 clients, with zero client overlap. At the
fixed top-50 review budget, logistic regression scored P@50 0.94, random forest 0.92, and the
rule baseline 0.72. Client-balanced Macro P@50 was 0.6345, 0.6368, and 0.5368 respectively.

Five grouped seeds produced logistic-regression P@50 of 0.88–0.96; time-aware validation
produced 0.72–0.90. Error review found both false positives and false negatives near the review
boundary, supporting human review of disagreements rather than automatic action.

## 6. Interpretation

The grouped holdout shows that the logistic-regression ranking model outperformed the rule
baseline at the row-weighted top-50 budget. Random forest had slightly higher client-balanced
Macro P@50, so the learned model is not uniformly superior under every aggregation.

Permutation influence was largest for `clicks_90d`, followed by `impressions_90d` and
`avg_position_feature`. This is ranking influence, not a causal explanation.

## 7. Recommendation

Review the first 50 rows per cycle. Confirm volume, CTR denominator, position-tier context, title
and snippet, intent match, and technical status in the source system. Use title/meta and snippet
review for high-volume, strong-position, low-CTR rows; use intent-match review when position is
deep or model and baseline disagree. Record evidence, action, and reviewer confidence, then
re-measure after a defined observation window.

Do not auto-publish edits, use the queue for personnel evaluation, or infer causality, intent,
quality, or business impact from the score alone. Recheck base rate and P@50 each period; review
thresholds when they move outside the validated range, and retrain only after a new time-aware
evaluation preserves feature/label separation.

## 8. Reproducibility

The pipeline uses the committed scripts and notebooks under `work/`, with warehouse access
configured through `HF_TOKEN`. The feature window is 2026-01-01 through 2026-03-31 and the label
window is 2026-04-01 through 2026-04-30. The grouped split uses seed 42 and a 20% test size.

The committed ML-07, ML-08, and ML-09 metrics JSON files are the receipts for the reported
results. The capstone notebook reads them rather than hard-coding a second source.

## 9. Acknowledgments & data credit

Built on the FlyRank ML Internship dataset — <https://flyrank.ai>

> Claims use observed, measured, directional, and decision-support language. No causal claims,
> client-identifying details, raw queries, credentials, or unsupported search-engine claims are
> included.
