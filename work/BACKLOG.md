# Work backlog

This file is the persistent handoff log for future sessions. Append entries;
do not rewrite history. Use local time with an explicit offset.

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
