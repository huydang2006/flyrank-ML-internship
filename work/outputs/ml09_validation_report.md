# ML-09 validation audit

- Final feature window: `2026-01-01` to `2026-03-31`
- Final label window: `2026-04-01` to `2026-04-30`
- Eligible base rate: **0.5856**

Grouped client validation uses five fixed seeds and keeps clients disjoint.
- Logistic Regression P@50 range: **0.8800–0.9600**

Time-aware validation trains on an earlier rolling window and tests on the next window.
- Logistic Regression P@50 range: **0.7200–0.9000**

The model is a ranking aid. Results are observed and directional; they do not show that an edit causes recovery.

Leakage checks:

- `feature_window_before_label_window`: **PASS**
- `future_fields_excluded_from_features`: **PASS**
- `identifiers_excluded_from_features`: **PASS**
- `duplicate_grain`: **PASS**
