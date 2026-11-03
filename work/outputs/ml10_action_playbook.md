# ML-10 action playbook

## Audience and intended use

This is a portfolio review aid for an SEO/content specialist. It ranks pages for human review; it does not automate edits or prove that an edit will improve traffic or CTR.

## Ranked actions and reason codes

Review the first 50 rows per cycle. Keep the observed reason code, supporting signals, suggested action, confidence note, and model signal note together. Treat the score as prioritization evidence, not a causal explanation.

## Review capacity and confidence boundaries

- Default capacity: 50 pages per review cycle.
- Require adequate impressions, a measurable CTR denominator, and agreement between reason code and model ranking.
- Keep low-confidence or contradictory rows for human review; do not auto-act.
- Validation reference: grouped P@50 0.88-0.96; time-aware P@50 0.72-0.90.

## Human-review checklist

1. Confirm page and query context in the source system.
2. Check impression volume and CTR denominator.
3. Compare CTR with the position-tier reference.
4. Inspect title, snippet, intent match, and technical status.
5. Record the chosen action, evidence, and reviewer confidence.
6. Re-measure after a defined observation window.

## No-go list

- Do not auto-publish edits from the queue.
- Do not use the queue for hiring or individual performance evaluation.
- Do not infer causality, intent, quality, or business impact from the score alone.
- Do not act on rows below the minimum denominator or missing critical context.

## Monitoring and retraining triggers

- Recheck Precision@50 and base rate each evaluation period.
- Review thresholds when base rate or top-50 precision shifts outside the validated range.
- Monitor impressions, CTR, position, missingness, and action mix for drift.
- Retrain only after a new time-aware evaluation preserves feature/label separation.

## Paper-safe exports

- Public queue rows exported: **2,904**.
- Pseudonymous client and content identifiers are omitted from the paper-facing queue.
