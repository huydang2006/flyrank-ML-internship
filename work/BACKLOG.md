# Work backlog

This file is the persistent handoff log for future sessions. Append entries;
do not rewrite history. Use local time with an explicit offset.

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
