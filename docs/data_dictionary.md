# Data dictionary

One section per dataset. Each column lists its meaning, the target type for silver, and quality issues found by profiling (`docs/profiles/`).

> **Status:** column lists below are the *expected* DLD open-data schema, written before the first real download. Mark each column ✅ once confirmed against a real file, and add or remove columns to match what you actually receive.

## How to read a row

- **Transactions:** one row is one registered real-estate procedure (a sale, mortgage or gift) on one property on one date.
- **Rents:** one row is one registered Ejari rental contract for one or more units.

Write these two sentences in your own words once you have looked at real rows — this is the Week 1 checkpoint.

---

## Transactions

Business key: `transaction_id`. Grain in silver: one row per transaction number.

| Column | Meaning | Silver type | Confirmed | Quality notes |
|---|---|---|:---:|---|
| `transaction_id` | DLD transaction number | string | | Check for duplicates across loads |
| `procedure_id` | Procedure code | int | | |
| `trans_group_id` / `trans_group_en` / `trans_group_ar` | Group: Sales, Mortgages, Gifts | int / string | | Only Sales feed `fact_sales` |
| `procedure_name_en` / `procedure_name_ar` | Procedure, e.g. Sell, Sell - Pre registration | string | | Pre-registration indicates off-plan |
| `instance_date` | Registration date | date | | Confirm format (dd-mm-yyyy expected) |
| `property_type_en` / `_ar` | Land, Building, Unit, Villa | string | | |
| `property_sub_type_en` / `_ar` | Flat, Office, Shop, Residential land… | string | | |
| `property_usage_en` / `_ar` | Residential, Commercial… | string | | |
| `reg_type_en` / `_ar` | Off-Plan or Existing Properties | string | | Source of `is_offplan` |
| `area_id` | DLD area code | int | | Prefer this over names for joins |
| `area_name_en` / `area_name_ar` | Area name | string | | Spelling and spacing vary |
| `building_name_en` / `_ar` | Building | string | | Often null for land |
| `project_number` / `project_name_en` / `_ar` | Project | string | | |
| `master_project_en` / `_ar` | Master community | string | | |
| `nearest_landmark_en`, `nearest_metro_en`, `nearest_mall_en` | Location context | string | | |
| `rooms_en` / `_ar` | Bedrooms, e.g. "2 B/R", Studio | string | | Needs parsing to a number |
| `has_parking` | Parking included | boolean | | |
| `procedure_area` | Size in m² | decimal | | Zero values seen in fixture |
| `actual_worth` | Transaction value, AED | decimal | | Thousands separators possible |
| `meter_sale_price` | Price per m², AED | decimal | | Recompute and compare |
| `rent_value`, `meter_rent_price` | Rent fields on sales file | decimal | | Probably mostly null — confirm |
| `no_of_parties_role_1/2/3` | Number of buyers / sellers | int | | |

## Rents (Ejari)

Business key: `contract_id`. Grain in silver: one row per contract.

| Column | Meaning | Silver type | Confirmed | Quality notes |
|---|---|---|:---:|---|
| `contract_id` | Ejari contract number | string | | |
| `contract_reg_type_en` | New or Renew | string | | |
| `contract_start_date`, `contract_end_date` | Contract period | date | | End before start = quarantine |
| `contract_amount` | Total contract value, AED | decimal | | |
| `annual_amount` | Annualised rent, AED | decimal | | Use for yield; recompute if missing |
| `ejari_property_type_en`, `ejari_property_sub_type_en` | Property type | string | | Map to the sales property types |
| `property_usage_en` | Residential, Commercial… | string | | |
| `area_id`, `area_name_en` / `_ar` | Area | int / string | | Same mapping as transactions |
| `project_name_en`, `master_project_en` | Project | string | | |
| `actual_area` | Size in m² | decimal | | |
| `tenant_type_en` | Person or authority | string | | |
| `no_of_prop` | Units in the contract | int | | Multi-unit contracts distort medians |
| `is_free_hold` | Freehold area flag | boolean | | |

## Cross-dataset issues

| Issue | Datasets | Decision | Where handled |
|---|---|---|---|
| Area names differ between datasets | Transactions, rents | Map to one `area_key` via `silver.areas` | Module 3 |
| Sizes in m², dashboard in ft² | All | Convert in silver, keep both | Module 3 |
| Sales vs rent property types differ | Transactions, rents | Mapping table to `dim_property_type` | Module 4 |
