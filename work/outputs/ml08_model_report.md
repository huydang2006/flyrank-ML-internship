# ML-08 model comparison

- Feature window: `2026-01-01` to `2026-03-31`
- Label window: `2026-04-01` to `2026-04-30`
- Split: grouped by client, seed `42`, test size `20%`
- Best learned model by Precision@50: **random_forest**

| Model | P@10 | P@20 | P@50 | Macro P@50 | Correct@50 | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|---:|
| random_forest | 1.0000 | 1.0000 | 0.9200 | 0.6412 | 46.0 | 0.1891 | 0.5566 |
| logistic_regression | 1.0000 | 1.0000 | 0.8600 | 0.6234 | 43.0 | 0.1900 | 0.5602 |
| ml07_rule_baseline | 0.7000 | 0.7500 | 0.7200 | 0.5345 | 36.0 | n/a | n/a |

Model actions use a fixed review budget of the top 50 held-out rows; a 0.5 probability threshold is not used for queue selection.
Calibration metrics are reported only for probabilistic learned models; the rule baseline is evaluated as a ranking score.
Macro Precision@K gives each held-out client equal weight. Per-client rows and base rates are stored in the metrics JSON.
The queue is a review aid. Future-window fields are used for evaluation only.