# ML-06 — Signal audit

## Planning

- [x] Read `skills/README.md`, the ML-06 signal-audit skill, and the FlyRank data skill.
- [x] Recheck the completed ML-04/ML-05 contract, windows, leakage rules, and warehouse outputs.
- [x] Confirm the warehouse release as the data source.
- [x] Define three tests: position tier vs CTR, impression volume vs CTR reliability, and
      the `measurable_opportunity` flag's assumptions.

## Notebook implementation

- [ ] Preserve the supplied notebook prompts and add answer markdown cells below them.
- [ ] Connect to the warehouse with the established DuckDB retry and timeout settings.
- [ ] Verify source dates, the daily fact grain, and the April-1 feature/label windows.
- [ ] Describe distributions before comparing signals; handle traffic-heavy tails with
      log transforms or grouped summaries.
- [ ] Run one mini-test per signal with visible sample sizes and denominator guards.
- [ ] Apply the signal-audit sample-size floor: do not issue a verdict for buckets with
      fewer than 50 rows, or cross-cuts with fewer than 30 rows.
- [ ] Assign each test a `CONFIRMED`, `OPPOSITE`, `MIXED`, or `FALSE` verdict and explain
      the practical meaning without causal claims.
- [ ] Re-run the tests on a second valid slice and report whether the direction is stable.
- [ ] Check that no target-window, product-decision, identifier, or query-window fields
      leak into the audit.
- [ ] Keep outputs public-safe: no raw queries, URLs, client names, credentials, or data
      files committed.
- [ ] Complete the ML-06 self-check only after the notebook has been run successfully.

## Verification and handoff

- [ ] Validate notebook JSON and compile every code cell.
- [ ] Run the ML-06 notebook top to bottom and inspect all outputs.
- [ ] Re-read the changed files and inspect the final diff for unrelated changes.
- [ ] Confirm no datasets or secrets were added.
- [ ] Append the final ML-06 results, limitations, and verification details to
      `work/BACKLOG.md`.
- [ ] Commit the completed ML-06 implementation separately from the instruction and TODO
      commits.
