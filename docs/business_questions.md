# Business questions

The dashboard exists to answer these questions for brokers, investors, banks and developers. Every gold table and DAX measure should trace back to at least one of them.

| # | Question | Who asks | Metric | Gold source | Dashboard page |
|---|---|---|---|---|---|
| 1 | Where are prices rising fastest? | Investors, developers | YoY change in median price per sqft, by area | `agg_area_monthly` | Market overview |
| 2 | What does a square foot cost by area and property type? | Brokers, buyers | Median price per sqft | `fact_sales`, `agg_area_monthly` | Area deep-dive |
| 3 | What gross rental yield can an investor expect in each area? | Investors | Median annual rent / median sale price | `agg_area_monthly` | Rental yield |
| 4 | How is market activity trending? | Banks, developers | Monthly sales count and total value (AED) | `fact_sales` | Market overview |
| 5 | Do off-plan units sell at a premium or discount to ready units? | Investors, developers | Median price per sqft, off-plan vs ready | `fact_sales` | Off-plan vs ready |
| 6 | What share of sales is off-plan, and is it rising? | Banks (risk), developers | Off-plan share of sales count | `fact_sales` | Off-plan vs ready |
| 7 | Which projects and developers lead sales volume? | Brokers, developers | Sales count and value by project | `fact_sales`, `dim_project` | Area deep-dive |
| 8 | Do our price trends agree with the official DLD index? | Analysts (validation) | Own monthly median vs DLD index, % gap | `agg_area_monthly`, index | Market overview (note) |

## Definitions

- **Price per sqft:** `actual_worth / (procedure_area × 10.7639)`, sales only, outliers flagged and excluded from medians.
- **Gross rental yield:** median annual rent / median sale price for the same area, property type and month. Reported only when both sides have at least a minimum number of records (threshold decided in Module 4).
- **Off-plan:** registration type is Off-Plan, or the procedure is a pre-registration.

## Out of scope (for now)

Net yield (service charges, vacancy), mortgage affordability, and forecasting. These are listed as "what I would do next" in the README.
