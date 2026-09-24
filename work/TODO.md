# Future work roadmap

ML-02 through ML-06 are complete. Start each future session by reading
`skills/README.md`, the applicable task skill, `CODING_INSTRUCTIONS.md`, and
`work/BACKLOG.md`. Work on one notebook per session, preserve template prompts,
save executed outputs inside the committed notebook, and append a dated backlog
entry before committing.

## ML-07 — Rule baseline and ranked review queue

- [x] Re-read the lane decision, ML-04 contract, ML-05 leakage audit, and ML-06 verdicts.
- [x] Define a transparent fixed-threshold baseline rule in plain language:
      feature CTR below 0.5%, at least 100 impressions, and a valid position tier.
- [x] Use pooled CTR consistently for tier context and repair no-position fallbacks
      so missing/zero position is never classified as `deep`.
- [x] Include explicit reason codes, volume floors, denominator guards, and confidence notes.
- [x] Build the full ranked queue and export the required public-safe artifact to
      `work/outputs/`.
- [x] Review the top 20 manually: action, reason code, confidence, and failure mode.
- [x] Check that IDs are grouping fields only and that no product flags or future windows
      enter the score.
- [x] Run the notebook top to bottom, inspect outputs, save outputs in the notebook, and
      update `work/BACKLOG.md`.

## ML-08 — Model and baseline comparison

- [ ] Choose a model appropriate to the ranking/scoring question and explain why it is
      worth the added complexity over the rule baseline.
- [ ] Reuse the same feature contract, eligible population, target definition, split,
      and primary metric as ML-07.
- [ ] Use a grouped-by-client or otherwise defensible split; record the seed and all
      preprocessing decisions.
- [ ] Compare model and baseline in one honest table, including budget-aware metrics.
- [ ] Inspect errors, calibration/ranking behavior, feature influence, and weak picks.
- [ ] Check for target leakage, identifiers, duplicate grains, missingness artifacts, and
      unsupported causal language.
- [ ] Export reproducible model metrics and queue artifacts to `work/outputs/`.
- [ ] Run the notebook top to bottom, save outputs in the notebook, and update the backlog.

## ML-09 — Validation and research-claim audit

- [ ] Re-read the validation and honest-claims skills before changing the evaluation design.
- [ ] Re-run the final model and baseline under an honest grouped or time-aware split.
- [ ] Compare before/after results without changing the metric or population to improve the
      story.
- [ ] Repeat the leakage audit on the final feature set and verify time-window separation.
- [ ] Check sensitivity to thresholds, client groups, periods, and minimum denominators.
- [ ] Identify unstable, sparse, or contradictory findings and preserve them as limitations.
- [ ] Rewrite the strongest claim using observed, measured, directional, decision-support
      language.
- [ ] Save validation tables/receipts, execute top to bottom, persist notebook outputs,
      and update the backlog.

## ML-10 — Action playbook

- [ ] Convert the validated queue into human-readable actions and reason codes.
- [ ] Define intended users, review capacity, confidence boundaries, and out-of-scope use.
- [ ] Add a human-review checklist and a no-go list for unsafe automation.
- [ ] Specify monitoring, drift, threshold-review, and retraining triggers.
- [ ] Export the final queue, figures, and tables needed by the paper to `work/outputs/`.
- [ ] Verify that every recommendation traces to an observed signal or validated model
      result and that no client-identifying information is exposed.
- [ ] Run the notebook top to bottom, save outputs in the notebook, and update the backlog.

## Capstone writing — ML-11 and ML-12

- [ ] Re-read the paper-writing and honest-claims skills; collect only committed outputs
      from ML-04 through ML-10.
- [ ] Write the research question and decision context.
- [ ] Document the release, tables, grains, windows, eligibility floors, exclusions,
      missingness, and privacy boundaries.
- [ ] Describe the baseline, model, split design, metrics, leakage checks, and validation.
- [ ] Build a results table that compares model and baseline on the same evaluation design.
- [ ] Write limitations before recommendations; avoid causal claims and unsupported
      generalization.
- [ ] Add the ranked recommendations, reason codes, human-review requirements, and
      monitoring plan from ML-10.
- [ ] Generate and embed the paper figures/tables from reproducible `work/outputs/` files.
- [ ] Complete the closing section: 5-minute demo outline, social-post cut, and
      employer-facing summary for ML-12.
- [ ] Run `capstone.ipynb` top to bottom, inspect every output, save outputs in the
      committed notebook, and update `work/BACKLOG.md`.
- [ ] Perform a final public-safety, leakage, reproducibility, and diff review.
- [ ] Record the deployed paper URL in `submission/paper_url.txt` when deployment is done.
- [ ] Commit the capstone only after all affected notebooks execute successfully.

## Final handoff

- [ ] Confirm no datasets, credentials, raw queries, private URLs, or client names are
      committed.
- [ ] Confirm every completed notebook has inspectable outputs committed in its `.ipynb`.
- [ ] Confirm every reported number traces to an executed notebook or committed receipt.
- [ ] Review the final repository diff and backlog for remaining limitations.
