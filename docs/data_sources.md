# Data sources

All data comes from official Dubai Land Department (DLD) open data. No listing sites are scraped: listing prices are asking prices, while DLD records are registered transaction prices.

## Datasets

| Dataset | Business key | Role in the platform | Primary source | Fallback |
|---|---|---|---|---|
| Transactions (sales, mortgages, gifts) | `transaction_id` | `fact_sales` | DLD open data portal — data.dubailand.gov.ae | Dubai Pulse `dld_transactions-open` |
| Rents (Ejari contracts) | `contract_id` | `fact_rents`, rental yield | DLD open data portal | Dubai Pulse |
| Units, buildings, projects | per table | Dimensions | DLD open data portal | Dubai Pulse |
| Developers, brokers | per table | Dimensions | DLD open data portal | Dubai Pulse |
| Residential Sale Price Index | month | Validate own price trends | Dubai Pulse `dld_residential_sale_index-open` | — |

## Status of each source (fill in during Week 1)

The Dubai Pulse transactions listing showed a last update of **24 April 2024** when checked in November 2026, so it may not hold recent years. Confirm before relying on it.

| Dataset | Source checked | Date checked | Years available | Format | File size | Rows | Update frequency | Notes |
|---|---|---|---|---|---|---|---|---|
| Transactions | | | | | | | | |
| Rents | | | | | | | | |
| Projects | | | | | | | | |
| Price index | | | | | | | | |

## Download log

Record every file you land in `data/raw/`, so any load can be reproduced.

| Load date | Dataset | File name | Source URL | Rows | Notes |
|---|---|---|---|---|---|
| | | | | | |

## Known caveats

- **Download paths and formats change.** Note the exact URL and date of every download.
- **Bilingual columns.** Arabic and English names sit side by side. Read files as UTF-8 (`utf-8-sig` strips a byte-order mark) and keep both name columns.
- **Area names are inconsistent** across datasets (spelling, spacing, Arabic vs English). Silver will use a mapping table, `silver.areas`.
- **Units.** DLD records sizes in square metres (`procedure_area`, `meter_sale_price`). The dashboard reports price per square foot; 1 m² = 10.7639 ft².
- **Currency.** Values are in AED. A USD column uses the fixed peg of 3.6725 AED per USD.
- **Late registrations.** Off-plan sales can be registered weeks after month-end, so the latest month is preliminary and volumes revise upward.
- **Licence.** Check and record the terms of use shown on the portal before publishing any derived figures.
