# Work backlog

This file is the persistent handoff log for future sessions. Append entries;
do not rewrite history. Use local time with an explicit offset.

## 2026-10-18T12:00:00+07:00 - Tighten ML-09 validation disclosure and trim no-op sensitivity

- Added a limitation to `work/scripts/ml09_validation.py` documenting that the eligible
  population is filtered on `impressions_next30d >= MIN_IMPRESSIONS`, a future-window
  volume floor (not a label-derived rule), per the hunting-leakage-and-validating skill's
  requirement to disclose outcome-window population selection.
- Removed the no-op `tier_support` sensitivity block (floors 1/10/30/100 returned identical
  90,750 rows); `sensitivity()` now returns only the CTR-threshold sensitivity.
- Files changed: `work/scripts/ml09_validation.py`.
- Verification: `python -m py_compile` passed; `git diff --check` clean; the notebook pulls
  `limitations` live from the JSON so cell 14 will print the new line on re-run.
- Remaining: re-run `w06_validation_audit.ipynb` to refresh
  `work/outputs/ml09_validation_metrics.json` / `ml09_validation_report.md` and commit the
  receipts. (Not executed here — warehouse needs HF_TOKEN; user runs.)

## 2026-10-16T05:01:29+07:00 - Execute simplified ML-07 and ML-08 review outputs

- Reviewed the user-executed ML-07 and ML-08 notebooks after removing ML-08 log-derived
  features and adding executable weak-pick, leakage, split, comparison, error, and feature
  influence outputs.
- ML-07 reports 349,411 queue rows, 75,500 actionable rows, 6 weak picks in the top 20,
  and 13 weak picks in the top 50. All six leakage checks pass.
- ML-08 uses 8 raw feature columns, with 90,750 eligible rows across 42 clients; the
  grouped holdout has 87,846 training rows across 33 clients and 2,904 holdout rows
  across 9 clients, with zero client overlap.
- Logistic Regression is selected by row-weighted Precision@50 (`0.9400`) versus Random
  Forest (`0.9200`) and the ML-07 baseline (`0.7200`). Random Forest has slightly higher
  client-balanced macro Precision@50 (`0.6412` versus `0.6345`), so the model choice should
  not be treated as universally superior across aggregation methods.
- ML-08 now carries ML-07-compatible observed reason codes, supporting reasons, suggested
  actions, and confidence notes, plus separate model signal codes. These are ranking
  context, not causal explanations. Permutation influence is led by clicks, position, and
  impressions; negative or near-zero engagement-feature influence is retained as observed.
- Files changed: `work/scripts/ml_contract.py`, `work/scripts/ml08_model.py`,
  `work/notebooks/w05_model.ipynb`, `work/outputs/ml08_model_metrics.json`,
  `work/outputs/ml08_model_report.md`, and `work/BACKLOG.md`.
- Verification: user-run ML-07 and ML-08 notebooks completed top to bottom; every code cell
  has output, no traceback was found, and output inspection found no credentials, raw
  queries, private URLs, or client names. Static Python compilation and `git diff --check`
  passed before execution.
- Remaining limitation: the grouped holdout is one single-period split with very small
  client groups, including 1-row and 3-row groups. ML-09 should use repeated grouped and
  time-aware validation with minimum support rules and uncertainty intervals.

## 2026-10-10T02:17:04+07:00 - Add client-balanced ML-07 and ML-08 validation receipts

- Added shared-holdout client-balanced Precision@10/20/50/100 and per-client support/base-rate
  receipts to ML-07 and ML-08. Baseline full-population metrics remain unchanged:
  Precision@10/20/50/100 `0.3000`/`0.4000`/`0.3800`/`0.3400`.
- The refreshed notebooks were run top to bottom by the user after the code changes. The
  shared holdout contains 2,904 rows across 9 clients. Row-weighted holdout Precision@50
  is `0.7200` for the baseline, `0.8600` for Logistic Regression, and `0.9200` for
  Random Forest.
- Client-balanced macro Precision@50 is `0.5345` for the baseline, `0.6234` for Logistic
  Regression, and `0.6412` for Random Forest. The macro result is the safer comparison
  because the row-weighted result is influenced by unequal client sizes.
- The holdout still contains very small client groups, including one client with 1 row and
  another with 3 rows; per-client metrics for those groups are unstable. The 9-client,
  single-period grouped holdout is not sufficient evidence of future-period generalization.
- Files changed: `work/scripts/ml_contract.py`, `work/scripts/ml07_baseline.py`,
  `work/scripts/ml08_model.py`, `work/notebooks/w04_baseline_score.ipynb`,
  `work/notebooks/w05_model.ipynb`, `work/outputs/ml07_baseline_metrics.json`,
  `work/outputs/ml07_baseline_report.md`, `work/outputs/ml08_model_metrics.json`,
  `work/outputs/ml08_model_report.md`, and `work/BACKLOG.md`.
- Verification: user-run top-to-bottom execution of both notebooks; refreshed outputs contain
  the client-balanced receipts and baseline calibration fields serialize as `null`. Changed
  Python scripts compiled successfully and `git diff --check` passed. No notebook was run by
  the assistant.
- Remaining limitation: ML-09 should use repeated grouped and time-aware validation, minimum
  per-client support rules, and uncertainty intervals before presenting a headline model
  improvement.

## 2026-10-07T04:55:31+07:00 - Complete script-based ML-07 and ML-08 execution

- Reworked ML-07 and ML-08 into thin notebook wrappers around reusable scripts in
  `work/scripts/`.
- ML-07 writes a public-safe queue CSV, metrics JSON, and Markdown report. The executed
  run produced 349,411 queue rows, 75,500 actionable rows, eligible base rate `0.5856`,
  and Precision@10/20/50/100 of `0.3000`/`0.4000`/`0.3800`/`0.3400`.
- ML-08 compares Logistic Regression and Random Forest against the ML-07 baseline using
  numeric features only, a client-grouped 20% holdout, and seed `42`. The executed run
  selected Logistic Regression by Precision@50: `0.9400`, versus Random Forest `0.9200`
  and the baseline `0.6600`.
- Both tasks export queue CSVs, metrics JSONs, and Markdown reports to `work/outputs/`.
  Both notebooks were rerun successfully and contain inspectable outputs without
  client names, raw queries, or private URLs.
- Files changed: `work/scripts/ml_contract.py`, `work/scripts/ml07_baseline.py`,
  `work/scripts/ml08_model.py`, `work/notebooks/w04_baseline_score.ipynb`,
  `work/notebooks/w05_model.ipynb`, `work/TODO.md`, and
  `work/BACKLOG.md`.
- Remaining limitation: ML-08 still needs a fuller documented error/feature-influence
  review before the entire checklist can be marked complete. The reported results are
  observed ranking evidence, not causal evidence.

## 2026-09-25T01:00:11+07:00 - Raise ML-07 CTR threshold to 0.5%

- Updated the transparent ML-07 rule from feature CTR below `0.2%` to below
  `0.5%`; the 100-impression floor, valid-position requirement, impression-based
  ranking, reason codes, denominator guards, and future-label isolation remain
  unchanged.
- Audited the prior implementation and found no related logic defect: the score
  already reads the threshold from `LOW_CTR_THRESHOLD`, position fallbacks keep
  missing/zero position out of `deep`, and precision@K evaluates the same
  eligible future-label slice.
- Files changed: `work/notebooks/w04_baseline_score.ipynb`, `work/TODO.md`,
  `work/BACKLOG.md`.
- Verification: top-to-bottom notebook execution succeeded from the repository
  root; the queue has 349,411 rows and 104,992 actionable rows, with precision@10
  `0.300000`, precision@20 `0.400000`, precision@50 `0.380000`, precision@100
  `0.340000`, eligible base rate `0.585554`, and leakage/public-safety checks
  passing. Evaluation uses the April future-label window only.
- Remaining limitation: `0.5%` is a transparent policy choice, not an optimized
  or causal cutoff.

## 2026-09-24T19:45:00+07:00 - Correct pooled CTR and simplify ML-07 baseline

- Repaired the earlier benchmark inconsistency: ML-03 now computes position-tier
  benchmarks as pooled CTR (`SUM(clicks) / SUM(impressions) * 100`) while retaining
  median CTR only as a comparison statistic.
- Standardized warehouse tier CASE logic in ML-04, ML-05, ML-06, and ML-07 so impressions
  below the feature floor, null position, and zero position are assigned an explicit
  no-position/no-volume category rather than `deep`.
- Replaced ML-07's tier-relative shortfall score with the approved hand-calculable
  rule: eligible pages have feature CTR below `0.2%`; eligible pages rank by
  feature-window impressions. Pooled tier CTR remains descriptive context only.
- Files changed: `work/notebooks/w02_ml_task_framing.ipynb`,
  `work/notebooks/w03_data_contract.ipynb`,
  `work/notebooks/w03_feature_leakage_check.ipynb`,
  `work/notebooks/w04_signal_audit.ipynb`, `work/notebooks/w04_baseline_score.ipynb`,
  `work/TODO.md`.
- Verification: executed all five affected notebooks top to bottom from the repository
  root; warehouse source and date guards passed; ML-06 pooled tier audit remained
  `CONFIRMED`; ML-07 queue has 349,411 rows, 0 duplicate ID pairs, 0 threshold
  violations, contiguous ranks, and leakage/public-safety checks passed. Final
  ML-07 precision: @10 `0.800000`, @20 `0.750000`, @50 `0.820000`, @100 `0.820000`.
- Remaining limitations: the `0.2%` threshold is a transparent policy choice, not a
  causal or optimized cutoff; pooled tier CTR is retained for context and future
  analysis, not used by the simple ML-07 flag.

## 2026-09-24T17:29:10+07:00 - Revise ML-07 score and queue taxonomy

- Replaced the baseline score with `relative CTR shortfall × feature-window
  impressions`; removed `log1p` and the hand-set tier multiplier.
- Added notebook markdown tables defining primary reason codes, supporting reason
  codes, action mapping, and confidence notes.
- Changed the actionable thresholds to `underperformance` at 50% below the tier
  benchmark and `severe_underperformance` at 70% below. Added supporting signals
  for high impressions, enough volume, low CTR, strong position, sessions,
  guarded weak engagement, and unavailable engagement measurement.
- Added guarded engagement context using only warehouse fields available in the
  release: GA4 availability, sessions, and engaged sessions; unavailable
  pageview/scroll fields were not assumed.
- Added Precision@50 and Precision@100 while retaining Precision@10/@20 and the
  eligible base rate. The public-safe queue now exports primary/supporting
  reasons, suggested action, confidence note, and engagement rate.
- Files changed: `work/notebooks/w04_baseline_score.ipynb`, `work/BACKLOG.md`.
- Verification: successful top-to-bottom warehouse execution saved in the
  notebook; 349,411 queue rows; zero duplicate ID pairs; no forbidden exported
  fields; Precision@10 0.900000, Precision@20 0.800000, Precision@50 0.880000,
  Precision@100 0.900000; leakage checks passed; notebook code/JSON validation
  and `git diff --check` passed.
- Remaining limitations: precision is measured against the existing April
  future label and is not causal evidence; scroll-rate evidence is unavailable
  in this warehouse schema. Unrelated formatting-only changes in future
  notebooks were detected and left unstaged.

## 2026-09-24T15:29:09+07:00 - Complete ML-07 warehouse baseline queue

- Completed the warehouse-backed ML-07 baseline notebook using the established
  2026-01-01 through 2026-03-31 feature window and 2026-04-01 through 2026-04-30
  evaluation window.
- Defined a tier-aware CTR underperformance score with a 100-impression feature
  floor, denominator-safe pooled tier benchmarks, explicit reason codes, confidence
  notes, top-20 failure-mode review, and leakage/public-safety assertions.
- Exported the public-safe ranked artifact to `work/outputs/baseline_action_score.csv`.
- Files changed: `work/notebooks/w04_baseline_score.ipynb`, `work/TODO.md`,
  `work/BACKLOG.md`.
- Verification: notebook JSON/code validation, successful top-to-bottom warehouse
  execution saved in the committed notebook, 349,411-row queue validation, zero
  duplicate ID pairs, contiguous ranks, forbidden-field check, `git diff --check`,
  and no nested runner output remaining.
- Results: 78,436 actionable rows; eligible base rate 0.585554; precision@10
  1.000000; precision@20 1.000000; one weak pick was identified in the top 20.
- [ERROR] 2026-09-24T15:29:09+07:00 — the first post-edit execution used a
  non-f-string SQL template for `MIN_FEATURE_IMPRESSIONS` and failed in
  `work/notebooks/w04_baseline_score.ipynb`; fixed before the successful run.
  [ERROR] 2026-09-24T15:29:09+07:00 — the first successful runner used the notebook
  directory as its working directory and wrote a temporary nested artifact; the
  specific `work/notebooks/work/` path was removed and the notebook was rerun from
  the repository root.
- Remaining limitations: this is an observed, directional decision-support queue,
  not evidence that refreshing a page will cause recovery; future validation remains
  part of ML-08/ML-09.

## 2026-09-24T14:10:27+07:00 - Clarify warehouse dataset policy

- Updated the session instructions to make the dataset transition explicit:
  starter CSV for early starter-work assignments, then the FlyRank warehouse
  release from W03/ML-04 onward unless a task explicitly specifies otherwise.
- Files changed: `CODING_INSTRUCTIONS.md`, `work/BACKLOG.md`.
- Verification: reviewed the documentation diff and ran `git diff --check`.
- Remaining limitations: none; ML-07 implementation is still pending.

## 2026-09-24T04:45:00+07:00 - Create future work roadmap

- Replaced the completed ML-06 checklist with a forward-looking roadmap for ML-07,
  ML-08, ML-09, ML-10, and capstone writing through ML-11/ML-12.
- Added explicit gates for committed notebook outputs, reproducible receipts, leakage
  checks, public safety, validation, and final deployment handoff.
- Files changed: `work/TODO.md`, `work/BACKLOG.md`.
- Verification: reviewed the roadmap for alignment with the existing notebook skeletons
  and ran `git diff --check`.
- Remaining limitations: all roadmap items are future work and remain unchecked.

## 2026-09-24T04:40:00+07:00 - Persist ML-06 outputs and align eligibility floor

- Corrected ML-06 so tests 1 and 2 first apply the ML-04-style feature eligibility floor
  of `impressions >= 100`; the separate future-label floor is not applicable because
  ML-06 has no future label.
- Saved the successful top-to-bottom execution outputs directly into
  `work/notebooks/w04_signal_audit.ipynb`.
- Audited completed notebooks for missing outputs: ML-02, ML-03, ML-04, and ML-05
  already contained outputs; no other notebook was marked complete.
- Updated `CODING_INSTRUCTIONS.md` to require committed executed notebook outputs and
  public-safe output inspection.
- Files changed: `CODING_INSTRUCTIONS.md`, `work/notebooks/w04_signal_audit.ipynb`,
  `work/TODO.md`, `work/BACKLOG.md`.
- Verification: ML-06 executed top to bottom successfully; source count/date and
  duplicate-grain checks passed; JSON/code validation and `git diff --check` passed.
- Results after the floor: position tier vs pooled CTR `CONFIRMED`; impression volume
  vs CTR stability `CONFIRMED`; measurable opportunity flag `MIXED`.

## 2026-09-24T01:35:00+07:00 — Reset TODO for ML-06 signal audit

- Removed the completed ML-04/ML-05 planning checklist and replaced it with the scoped
  ML-06 signal-audit plan.
- Files changed: `work/TODO.md`, `work/BACKLOG.md`.
- Verification: reviewed the rewritten checklist and ran `git diff --check`.
- Remaining limitations: ML-06 notebook implementation and execution are still pending.

## 2026-09-24T01:55:00+07:00 ? Complete ML-06 signal audit

- Implemented the warehouse-backed ML-06 notebook with distribution checks, three signal tests, sample-size floors, denominator-safe pooled rates, a second-window stability check, and explicit pre-origin/source guards.
- Results: position tier vs pooled CTR was `CONFIRMED`; impression volume vs CTR spread was `MIXED`; the `measurable_opportunity` flag was `MIXED` because its session requirement depends on GA4 availability.
- Files changed: `work/notebooks/w04_signal_audit.ipynb`, `work/TODO.md`, `work/BACKLOG.md`.
- Verification: notebook JSON parsing, Python compilation of all code cells, `git diff --check`, and two successful top-to-bottom notebook executions against the warehouse. The final run confirmed 78,835,655 source rows from 2025-01-27 through 2026-06-30 and zero duplicate daily grains in the primary window.
- Remaining limitations: the notebook reports observed associations only; it does not establish causal effects.

## 2026-09-24T01:30:00+07:00 — Clarify notebook answer-cell workflow

- Updated `CODING_INSTRUCTIONS.md` so notebook template prompts remain intact while
  written answers are added in new markdown cells between each prompt and its code cell.
- Files changed: `CODING_INSTRUCTIONS.md`, `work/BACKLOG.md`.
- Verification: reviewed the diff and ran `git diff --check`.
- Remaining limitations: none; this change affects workflow guidance only.

## 2026-09-10T16:05:00+07:00 — ML-05 feature-vector and leakage audit

- Changed the ML-04 contract to use the intended 90-day feature window (`2026-01-01` through `2026-03-31`) and corrected the future-CTR denominator guard to `NULLIF(..., 0)`.
- Completed the ML-05 notebook with a pre-origin daily feature vector, documented missingness/categorical handling, executable leakage checks, a deliberate future-only feature sanity test, and explicit exclusions.
- Files changed: `work/notebooks/w03_data_contract.ipynb`, `work/notebooks/w03_feature_leakage_check.ipynb`, `work/TODO.md`.
- Verification: notebook JSON parsing, Python compilation of ML-05 code cells, `git diff --check`, and repository diff inspection passed. Full notebook execution was not possible locally because `HF_TOKEN` is unavailable and no Jupyter runner is installed; run both notebooks top to bottom in Colab before relying on warehouse outputs.
- Remaining limitation: warehouse-backed SQL and resulting counts still need Colab execution with a read token.

## 2026-09-10T18:10:00+07:00 — Warehouse notebook execution fixed and verified

- Added DuckDB HTTP resilience settings to both warehouse notebooks: `http_retries = 10`, `http_timeout = 120`, and disabled the HTTP metadata cache.
- Fixed the ML-05 dimension joins with explicit `ON` predicates to avoid DuckDB's ambiguous `client_hash_id` error.
- Files changed in commit `73bfa97`: `work/notebooks/w03_data_contract.ipynb` and `work/notebooks/w03_feature_leakage_check.ipynb`.
- Verification performed: both notebooks ran top to bottom locally with `HF_TOKEN`; ML-04 completed its window, grain, prevalence, missingness, referential-integrity, and query-window checks; ML-05 built 349,411 feature rows, found zero duplicate feature grains, and completed the deliberate leaky-feature sanity test.

## 2026-09-10T18:26:36+07:00 — Commit and notebook-template gates

- Updated `CODING_INSTRUCTIONS.md` to require successful top-to-bottom notebook execution with no exception before committing, and to preserve notebook markdown templates except for template-code comments and final self-check boxes.
- Updated `work/TODO.md` to record the completed top-to-bottom notebook verification.
- Files changed: `CODING_INSTRUCTIONS.md`, `work/TODO.md`, `work/BACKLOG.md`.
- Verification: the previous backlog entry records successful top-to-bottom execution of both affected notebooks with `HF_TOKEN`; current changes were reviewed before staging.
- Remaining limitation: existing notebook edits are intentionally kept for the separate notebook commit; future notebook work must follow the new markdown-preservation rule.

## 2026-09-24T14:18:52+07:00 - Complete ML-07 baseline score

- Implemented the warehouse-backed ML-04 feature contract in `w04_baseline_score.ipynb`, including a transparent tier-aware score, reason codes, feature and label denominator guards, confidence notes, future-label evaluation, and leakage checks.
- Exported the public-safe ranked queue to `work/outputs/baseline_action_score.csv` (ignored by git); the queue contains 349,411 rows and 85,706 actionable reviews.
- Added a top-20 review, explicit weak-pick inspection, precision@10/20, base rate, and run-safe assertions for dates, duplicate grain, identifiers, product flags, and future-window isolation.
- Files changed: `work/notebooks/w04_baseline_score.ipynb`, `work/TODO.md`, `work/BACKLOG.md`; generated CSV remains gitignored.
- Verification: notebook executed top to bottom with `HF_TOKEN`; source check reported 78,835,655 rows through 2026-06-30, zero duplicate feature grains, and leakage check `PASS`.
- Remaining limitations: this is an observed decision-support ranking rule; April labels are used for evaluation only and do not establish causal impact.
