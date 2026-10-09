# ML-07 baseline output

- Feature window: `2026-01-01` to `2026-03-31`
- Label window: `2026-04-01` to `2026-04-30`
- Queue rows: **349,411**
- Actionable rows: **75,500**
- Eligible base rate: **0.5856**

| Metric | Value |
|---|---:|
| Precision@10 | 0.3000 |
| Precision@20 | 0.4000 |
| Precision@50 | 0.3800 |
| Precision@100 | 0.3400 |

Shared grouped-client holdout comparison metrics:

- Holdout rows: **2,904** across **9** clients
- Holdout Precision@10/20/50/100: **0.7000** / **0.7500** / **0.7200** / **0.6200**
- Client-balanced holdout Precision@10/20/50/100: **0.5889** / **0.5256** / **0.5368** / **0.5262**

Future labels are used only for evaluation. The score uses feature-window fields only.