# ML-08 model comparison

- Feature window: `2026-01-01` to `2026-03-31`
- Label window: `2026-04-01` to `2026-04-30`
- Split: grouped by client, seed `42`, test size `20%`
- Eligible rows/clients: **90,750** / **42**
- Train rows/clients: **87,846** / **33**
- Held-out rows/clients: **2,904** / **9**
- Client overlap: **0**
- Best learned model by Precision@50: **logistic_regression**

| Model | P@10 | P@20 | P@50 | Macro P@50 | Correct@50 | Brier | Log loss |
|---|---:|---:|---:|---:|---:|---:|---:|
| logistic_regression | 0.9000 | 0.9500 | 0.9400 | 0.6345 | 47.0 | 0.2013 | 0.5929 |
| random_forest | 1.0000 | 1.0000 | 0.9200 | 0.6412 | 46.0 | 0.1877 | 0.5542 |
| ml07_rule_baseline | 0.7000 | 0.7500 | 0.7200 | 0.5345 | 36.0 | n/a | n/a |

Top false positives and false negatives at the fixed review budget:

| Error type | Rank | Content ID | Model score | Baseline score | Target |
|---|---:|---|---:|---:|---:|
| false_positive | 3 | `content_474c280cef704f95` | 0.9066 | 21084.0 | 0 |
| false_positive | 34 | `content_7f556c147bc569e1` | 0.7959 | 531.0 | 0 |
| false_positive | 41 | `content_23ee067b01faada5` | 0.7842 | 167.0 | 0 |
| false_negative | 51 | `content_468c6397d84e8e79` | 0.7701 | 16763.0 | 1 |
| false_negative | 52 | `content_3e0ec371cd4d481a` | 0.7677 | 647.0 | 1 |
| false_negative | 53 | `content_8d553f6c51080719` | 0.7666 | 181.0 | 1 |
| false_negative | 54 | `content_98648444f3cc6e80` | 0.7656 | 7748.0 | 1 |
| false_negative | 55 | `content_1d4ac05af1c261b7` | 0.7641 | 169.0 | 1 |
| false_negative | 56 | `content_29d4b767fecb3bbd` | 0.7635 | 107.0 | 1 |
| false_negative | 57 | `content_aa4d569acfa4b800` | 0.7624 | 270.0 | 1 |
| false_negative | 58 | `content_c39937641c46fa37` | 0.7576 | 497.0 | 1 |
| false_negative | 60 | `content_2001ba565f6aa72e` | 0.7572 | 238.0 | 1 |
| false_negative | 61 | `content_95c4755bd4e758c9` | 0.7551 | 464.0 | 1 |

ML-07-compatible observed reason codes and actions are retained in the ML-08 queue. Model signal codes are separate ranking context, not causal explanations.

| Rank | Primary reason | Supporting reasons | Suggested action | Model signal |
|---:|---|---|---|---|
| 1 | low_ctr | high_impressions|enough_volume|low_ctr|strong_position|engagement_not_measured | rewrite title/meta and improve snippet structure | model_ranked_lower_priority |
| 2 | low_ctr | high_impressions|enough_volume|low_ctr|strong_position|engagement_not_measured | rewrite title/meta and improve snippet structure | model_ranked_lower_priority |
| 3 | low_ctr | high_impressions|enough_volume|low_ctr|strong_position|engagement_not_measured | rewrite title/meta and improve snippet structure | model_false_positive_review |
| 4 | low_ctr | high_impressions|enough_volume|low_ctr|strong_position|engagement_not_measured | rewrite title/meta and improve snippet structure | model_ranked_lower_priority |
| 5 | low_ctr | high_impressions|enough_volume|low_ctr|engagement_not_measured|deep_position_caution | improve snippet structure | model_baseline_disagreement |
| 6 | low_ctr | enough_volume|low_ctr|engagement_not_measured|deep_position_caution | improve intent match | model_baseline_disagreement |
| 7 | low_ctr | enough_volume|low_ctr|engagement_not_measured|deep_position_caution | improve intent match | model_baseline_disagreement |
| 8 | low_ctr | enough_volume|low_ctr|engagement_not_measured|deep_position_caution | improve intent match | model_baseline_disagreement |
| 9 | low_ctr | enough_volume|low_ctr|engagement_not_measured|deep_position_caution | improve intent match | model_baseline_disagreement |
| 10 | low_ctr | high_impressions|enough_volume|low_ctr|strong_position|engagement_not_measured | rewrite title/meta and improve snippet structure | model_ranked_lower_priority |

Permutation feature influence on held-out average precision:

| Feature | Mean score decrease | Standard deviation |
|---|---:|---:|
| `clicks_90d` | 0.150885 | 0.006115 |
| `avg_position_feature` | 0.069666 | 0.004848 |
| `impressions_90d` | 0.065053 | 0.008371 |
| `engagement_available` | 0.012463 | 0.003087 |
| `ga4_available_90d` | 0.000552 | 0.000751 |
| `sessions_90d` | 0.000179 | 0.000580 |
| `engaged_sessions_90d` | -0.000317 | 0.000655 |
| `engagement_rate_feature` | -0.003187 | 0.001165 |

Leakage checks:

- `feature_window_before_label_window`: **PASS**
- `future_fields_excluded_from_features`: **PASS**
- `identifiers_excluded_from_features`: **PASS**
- `train_test_clients_disjoint`: **PASS**
- `duplicate_test_grain`: **PASS**

Model actions use a fixed review budget of the top 50 held-out rows; a 0.5 probability threshold is not used for queue selection.
Calibration metrics are reported only for probabilistic learned models; the rule baseline is evaluated as a ranking score.
Macro Precision@K gives each held-out client equal weight. Per-client rows and base rates are stored in the metrics JSON.
The queue is a review aid. Future-window fields are used for evaluation only.