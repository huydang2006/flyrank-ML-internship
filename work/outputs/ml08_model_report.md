# ML-08 model comparison

- Feature window: `2026-01-01` to `2026-03-31`
- Label window: `2026-04-01` to `2026-04-30`
- Split: grouped by client, seed `42`, test size `20%`
- Best learned model by Precision@50: **logistic_regression**

| Model | Precision@10 | Precision@50 | Correct@50 | Brier | Log loss |
|---|---:|---:|---:|---:|---:|
| logistic_regression | 0.9000 | 0.9400 | 47.0 | 0.2059 | 0.6031 |
| random_forest | 1.0000 | 0.9200 | 46.0 | 0.1876 | 0.5530 |
| ml07_rule_baseline | 0.6000 | 0.6600 | 33.0 | 0.3072 | 11.0713 |

The queue is a review aid. Future-window fields are used for evaluation only.