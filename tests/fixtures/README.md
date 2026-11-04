# Test fixtures

`sample_transactions.csv` is **synthetic**. It follows the shape of the DLD transactions export but every row is invented (IDs start with `SYN-`). It is small on purpose and contains one example of each problem the pipeline must handle:

| Row | Planted issue |
|---|---|
| SYN-0002 | Thousands separator in `actual_worth` (`"920,000"`) |
| SYN-0003 | Same transaction appears twice (exact duplicate) |
| SYN-0006 | Missing English area name, Arabic name present |
| SYN-0007 | Impossible date (`31-02-2024`) |
| SYN-0008 | Non-numeric value (`n/a`) and empty `meter_sale_price` |
| SYN-0010 | Zero size and zero price |
| SYN-0011 | Trailing space in area name (`"Business Bay "`) |

Real DLD data is never committed to the repo.
