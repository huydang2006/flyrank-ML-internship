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

- Weak picks in top 20: **6**
- Weak picks in top 50: **13**

Top-20 weak-pick inspection:

| Rank | Content ID | Score | Weak pick | Reasons |
|---:|---|---:|:---:|---|
| 1 | `content_e241d6415ac9e534` | 509684.0 | no | none |
| 2 | `content_ec2e0346994fb5a5` | 509532.0 | no | none |
| 3 | `content_e8a52cf3d5988c07` | 508139.0 | no | none |
| 4 | `content_b99ea6861864dea5` | 463218.0 | yes | engagement_not_measured |
| 5 | `content_acbcc847f8996314` | 433095.0 | yes | engagement_not_measured |
| 6 | `content_00d4fdf6e48a2d38` | 407604.0 | no | none |
| 7 | `content_471d9cabce329a66` | 393421.0 | no | none |
| 8 | `content_1e921148b5fee86a` | 384139.0 | no | none |
| 9 | `content_7172a7fad43f0998` | 369204.0 | yes | engagement_not_measured |
| 10 | `content_8e1334d6356668e3` | 362658.0 | no | none |
| 11 | `content_cf651123f1085418` | 360822.0 | no | none |
| 12 | `content_fd2117c2c6790e4b` | 353760.0 | no | none |
| 13 | `content_b556f0bd87d6fcca` | 339568.0 | no | none |
| 14 | `content_36e53e9c707674fc` | 336457.0 | no | none |
| 15 | `content_95ff62babbfac9c7` | 333917.0 | no | none |
| 16 | `content_fec55986a1868d62` | 332651.0 | yes | engagement_not_measured |
| 17 | `content_b17c1d1cb0a346d6` | 320097.0 | no | none |
| 18 | `content_f352b7cfd0b2f434` | 317526.0 | yes | engagement_not_measured |
| 19 | `content_df47d1b976106de4` | 311782.0 | no | none |
| 20 | `content_7c6373141eae744a` | 311359.0 | yes | engagement_not_measured |

Shared grouped-client holdout comparison metrics:

- Holdout rows: **2,904** across **9** clients
- Holdout Precision@10/20/50/100: **0.7000** / **0.7500** / **0.7200** / **0.6200**
- Client-balanced holdout Precision@10/20/50/100: **0.5778** / **0.5312** / **0.5390** / **0.5250**

Leakage checks:

- `feature_window_before_label_window`: **PASS**
- `score_uses_only_feature_columns`: **PASS**
- `future_fields_excluded_from_public_queue`: **PASS**
- `identifiers_not_score_inputs`: **PASS**
- `product_flags_not_score_inputs`: **PASS**
- `duplicate_queue_grain`: **PASS**

Future labels are used only for evaluation. The score uses feature-window fields only.