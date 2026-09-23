# ML-06 — Signal audit

## Planning

- [x] Read `skills/README.md`, the ML-06 signal-audit skill, and the FlyRank data skill.
- [x] Recheck the completed ML-04/ML-05 contract, windows, leakage rules, and warehouse outputs.
- [x] Confirm the warehouse release as the data source.
- [x] Define three tests: position tier vs CTR, impression volume vs CTR reliability, and
      the `measurable_opportunity` flag's assumptions.

## Notebook implementation

- [x] Preserve the supplied notebook prompts and add answer markdown cells below them.
- [x] Connect to the warehouse with the established DuckDB retry and timeout settings.
- [x] Verify source dates, the daily fact grain, and the April-1 feature/label windows.
- [x] Describe distributions before comparing signals; handle traffic-heavy tails with
      log transforms or grouped summaries.
- [x] Run one mini-test per signal with visible sample sizes and denominator guards.
- [x] Apply the signal-audit sample-size floor: do not issue a verdict for buckets with
      fewer than 50 rows, or cross-cuts with fewer than 30 rows.
- [x] Assign each test a `CONFIRMED`, `OPPOSITE`, `MIXED`, or `FALSE` verdict and explain
      the practical meaning without causal claims.
- [x] Re-run the tests on a second valid slice and report whether the direction is stable.
- [x] Check that no target-window, product-decision, identifier, or query-window fields
      leak into the audit.
- [x] Keep outputs public-safe: no raw queries, URLs, client names, credentials, or data
      files committed.
- [x] Complete the ML-06 self-check only after the notebook has been run successfully.

## Verification and handoff

- [x] Validate notebook JSON and compile every code cell.
- [x] Run the ML-06 notebook top to bottom and inspect all outputs.
- [x] Re-read the changed files and inspect the final diff for unrelated changes.
- [x] Confirm no datasets or secrets were added.
- [x] Append the final ML-06 results, limitations, and verification details to
      `work/BACKLOG.md`.
- [x] Commit the completed ML-06 implementation separately from the instruction and TODO
      commits.
