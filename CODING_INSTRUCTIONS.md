# Work-session instructions

Use this file when starting a new coding or notebook session in this repository.

## Start here

1. Read `skills/README.md` first. Find the task in its table and load exactly one
   task skill. Also load `skills/flyrank/flyrank-data/SKILL.md` whenever the task
   touches FlyRank data or warehouse queries.
2. Read `work/TODO.md`, then read the relevant notebooks and docs in order.
3. Read `work/BACKLOG.md` to understand previous changes, errors, and unfinished
   follow-ups.
4. Search the repository before assuming anything is missing, complete, or
   implemented. Inspect the current git status before editing.
5. Work on one task per conversation. If the scope is unclear or a design choice
   materially changes the result, ask one focused question before coding.
6. Keep notebook template markdown cells intact. Do not rewrite or delete the
   supplied prompts. When a notebook needs written answers, add a new markdown
   answer cell directly below the relevant template markdown cell and before its
   code cell. The only edits allowed inside supplied markdown cells are checking
   the final self-check boxes. The ML-05 markdown is intentionally a hand-written
   template.

## While working

- Never assume a notebook, cell, metric, or claim is correct because it already
  exists or is marked complete. Perform a quick code and output recheck first.
- Trace definitions back to the relevant docs, especially:
  - `docs/data-dictionary.md` for columns, units, missingness, and leakage traps;
  - `docs/ml-intern-dataset-and-lane-guide.md` for lane, validation, and
    public-safety rules;
  - `docs/ml-core-foundation-framework.md` for general ML reasoning and checks.
- Preserve the repository rules in `work/README.md`: do not commit datasets,
  keep reproducible outputs/receipts, and use observed or directional language.
- Make precise changes only in the requested scope. Do not restore, revert, or
  overwrite unrelated user changes.
- Do not print private data, client names, raw queries, credentials, or secrets.
- Use the existing project tools and tests. Do not add tooling unless a real
  dependency or validation gap requires it.

## Before declaring the task done

1. Re-read the changed files and inspect the diff.
2. Run the relevant checks, then run the affected notebook top to bottom
   (Runtime → Run all). Read the outputs, not only the exit status.
3. Check for leakage, time-window overlap, invalid denominators, duplicate
   grains, missingness mistakes, accidental identifiers, and misleading claims.
4. Confirm no datasets or secrets were added and that reproducibility is intact.
5. Update checkboxes in `work/TODO.md` only for work actually completed.
6. Append a dated entry to `work/BACKLOG.md` describing:
   - what changed and why;
   - files changed;
   - verification performed;
   - remaining limitations or follow-ups;
   - any problem as `[ERROR]`, with the timestamp and affected files.
7. Commit the finished change with a meaningful message explaining what and why.
   Include the repository co-author trailer required by the project instructions.
   Do not push, publish, or sync globally; leave the commit available for the
   user to inspect.
8. Never commit notebook work until every affected notebook has been run
   successfully from top to bottom with no exception. Read the outputs, not
   only the exit status.

## Required final response

Give a concise summary with links to changed files, verification results,
commit hash/message, and any `[ERROR]` or remaining follow-up. Do not claim
anything was verified if it was not actually run.
