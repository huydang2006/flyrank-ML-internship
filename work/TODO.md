# Today’s plan — ML-05 leakage and feature-vector audit

## 1. Planning phase

- [x] Read `skills/README.md` and load the ML-05 leakage/validation skill.
- [x] Load the FlyRank data skill because this task uses the warehouse and its data rules.
- [x] Read the existing notebooks in order: ML-02, ML-03, ML-04, then the ML-05 skeleton.
- [x] Check the relevant docs for the warehouse grain, windows, missingness, and leakage warnings.
- [x] Record the current worktree state and avoid changing the unrelated deleted notebook.
- [x] Identify the small ML-04 follow-up checks before starting ML-05 implementation.

## 2. Previous-notebook follow-up

- [x] Reconcile ML-04’s feature-window prose (`2026-01-01` to `2026-03-31`) with the code’s `FEATURE_START = '2025-12-31'`; keep the intended 90-day window consistent everywhere.
- [x] Correct the ML-04 prevalence-query denominator guard from `NULLIF(impressions_next30d, 1)` to a zero guard, then rerun the notebook top to bottom.
- [x] Recheck any resulting counts and wording for consistency with the corrected window and label definition.

## 3. ML-05 implementation

- [x] Define the leakage-safe feature vector for the April 1 origin using only pre-origin daily facts and allowed dimension fields.
- [x] Document each feature’s meaning, missing-value treatment, categorical handling, availability time, and whether it is context-only.
- [x] Add explicit checks for label-derived fields, future-window overlap, query-table window overlap, product/decision flags, IDs, duplicate grains, and target-window columns.
- [x] Demonstrate the leakage checks with inspectable outputs, including a deliberate leaky-feature sanity test where appropriate.
- [x] List excluded fields and the reason for excluding each one.
- [x] Keep all outputs public-safe: no raw queries, URLs, client names, or datasets committed.
- [x] Complete the ML-05 self-check and preserve reproducible seeds/assumptions where applicable.

## Verification and handoff

- [x] Run the notebooks top to bottom after edits and inspect all validation outputs.
- [x] Confirm no dataset files are added and metrics/receipts remain reproducible.
- [x] Review the final diff for unrelated changes and summarize remaining limitations.
