# Capstone Report — <CTR / Engagement Opportunity Scoring>

- **Author:** Mai Huy Đăng
- **Lane:** 4 (CTR / Engagement Opportunity Scoring)
- **Repo:** https://github.com/huydang2006/flyrank-ML-internship
- **Date:**

> Copy this file to `work/capstone_report.md` and fill it in as you build. Sections 1–8
> mirror the Pass / Needs-Work rubric axes, so nothing here is optional. Sections 0 and 9
> are **paper sections**: your deployed research paper must carry both, and they're here so
> you never rebuild them from memory at ship time.

## 0. Abstract

Five sentences, written last, placed first: question → data → method → headline result →
what the output is for. This is the top of your deployed paper.

## 1. Problem framing

What decision does this support? Name the unit of analysis (page, client, day…), the output
(score, rank, cluster, report), the action a human takes from it, and the cost of a wrong
call. Why does data/ML help here at all?

======

**Decision supported:** Which visible pages are under-capturing clicks relative to others in the same search position tier, and are worth review for content or metadata improvement?

**Unit of analysis:** Individual content pages (one row per pseudonymized content item in the starter dataset).

**Output:** A ranked list of CTR underperformers with reason codes (high_impressions, very_low_ctr, weak_engagement) and recommend actions.

**Action:** Content reviewers, SEO strategists, or editors with a fixed weekly audit budget use the ranked list to allocate review effort — top candidates get metadata/content improvement actions (rewrite title/meta, improve intent match, improve engagement).

**Cost of a wrong call:**
- **False positive:** Reviewer wastes time auditing a low-volume page (e.g., 100 trailing impressions). Even if CTR is low, the volume is noise. Wasted effort.
- **False negative:** Missing a high-potential page (e.g., ~5,000 impressions at `page_1` with 0.01% CTR vs 0.23% expected). The gap suggests a fixable title/meta problem. If missed, 5,000 impressions stay uncaptured — real opportunity cost.

**Why data/ML helps:** A plain rule like "flag pages with CTR < 0.1%" catches noise and misses context. Ranking by position alone misses tier-specific underperformers. Ranking by impressions alone ignores position context. A tier-adjusted analysis calculates expected CTR *by position tier*, then flags pages that sit far below their tier's median — this is the signal that a simple if-statement cannot capture.

## 2. Data safety

Which data you used and which columns you deliberately excluded (and why). Leakage risks you
considered — especially label-derived fields (`trend_direction`, `trend_pct`) and pseudonymous
IDs (grouping only, never features). Confirm nothing client-identifying appears anywhere in
`work/`.

## 3. Baseline

The transparent rule or score you built first. Why it's a fair comparison, and its numbers on
the same data and metric as your model.

## 4. Model / analysis

Your method and why it fits the lane. The exact feature list (and what you left out on
purpose). The target or proxy definition, in one sentence.

## 5. Evaluation

Your split (grouped by client? time-aware?) and why. Metrics, model vs baseline **on the same
split**. What the errors look like — a short error analysis beats a big metric table.

## 6. Interpretation

What the model/clusters actually found. Feature importances or cluster profiles in plain
words. Surprises and negative results — a well-understood "no effect" is a valid result.

## 7. Recommendation

The ranked actions or decisions your output supports, and how a FlyRank editor would use them
tomorrow. State your confidence and the limits explicitly.

## 8. Reproducibility

The exact commands to re-run everything from a fresh clone, your random seeds, and your
environment (`pip freeze` highlights or `requirements.txt` deltas). If you claim a sealed or
holdout evaluation, two things must be committed: the cell/script that builds the sealed
frame, and the metrics file it produced — "evaluated once, blind" should be checkable from
your repo, not taken on faith.

## 9. Acknowledgments & data credit

One short section at the bottom of the deployed paper: "Built on the FlyRank ML Internship
dataset" **linking to https://flyrank.ai**. Crediting your data source is standard research
practice — and it's on the capstone's required-section list, so a paper without it isn't done.

======

Built on the FlyRank ML Internship dataset — https://flyrank.ai

---

> **Claims checklist before submitting:** observed / measured / directional / decision-support
> **Metrics vs. base rate:** report your task's base rate (majority-class %) next to any
> precision@K or accuracy — a high score can just be a high base rate. AUC / lift over
> baseline are the honest discrimination numbers.
> language everywhere · no causal claims without an experiment or causal design · no
> "predicted Google's algorithm" · no client-identifying details · numbers in this report
> match a fresh re-run.
