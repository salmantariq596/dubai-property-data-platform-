# Profile: sample_transactions (synthetic)

Generated 2026-11-04 13:59 UTC by `dld-profile`.

## Summary

| Metric | Value |
|---|---|
| Source file | `sample_transactions.csv` |
| Rows | 12 |
| Columns | 12 |
| Exact duplicate rows | 1 |
| Rows sharing a `transaction_id` | 2 |

## Columns

| Column | Inferred type | Null % | Distinct | Range | Top values |
|---|---|---:|---:|---|---|
| `transaction_id` | text | 0.0 | 11 |  | SYN-0003 (2), SYN-0001 (1), SYN-0002 (1) |
| `instance_date` | date | 0.0 | 11 | 2024-01-05 – 2024-01-15 | 07-01-2024 (2), 05-01-2024 (1), 06-01-2024 (1) |
| `trans_group_en` | text | 0.0 | 3 |  | Sales (9), Mortgages (2), Gifts (1) |
| `procedure_name_en` | text | 0.0 | 4 |  | Sell (7), Sell - Pre registration (2), Mortgage Registration (2) |
| `property_type_en` | text | 0.0 | 3 |  | Unit (10), Villa (1), Land (1) |
| `property_sub_type_en` | text | 0.0 | 4 |  | Flat (9), Villa (1), Residential (1) |
| `reg_type_en` | text | 0.0 | 2 |  | Existing Properties (9), Off-Plan Properties (3) |
| `area_name_en` | text | 8.3 | 6 |  | Business Bay (3), Dubai Marina (3), Jumeirah Village Circle (2) |
| `area_name_ar` | text (Arabic) | 0.0 | 5 |  | الخليج التجارى (5), مرسى دبي (3), قرية جميرا الدائرية (2) |
| `procedure_area` | numeric | 0.0 | 11 | 0 – 950 | 110.0 (2), 85.5 (1), 62.1 (1) |
| `actual_worth` | numeric | 0.0 | 11 | 0 – 5,600,000 | 2300000 (2), 1450000 (1), 920,000 (1) |
| `meter_sale_price` | numeric | 8.3 | 10 | 0 – 20,909.09 | 20909.09 (2), 16959.06 (1), 14814.81 (1) |

## Flags for the data dictionary

- 2 rows share a `transaction_id` value — decide the dedup rule for silver (latest ingested wins?).
- 1 exact duplicate rows.
- `instance_date` is mostly dates (91.7%) but some values will fail a cast — quarantine candidates.
- `procedure_area` has zero or negative values (min 0).
- `actual_worth` is mostly numeric (91.7%) but some values will fail a cast — quarantine candidates.
- `actual_worth` has zero or negative values (min 0).
- `meter_sale_price` has zero or negative values (min 0).
