Select * counts matched both in duckDB and on the snowflake datawarehouse. The count of the numbers is 3,336,716
The zone look up file will be created like a seed in dbt


## Day 7 — Star schema

- **Grain:** `fct_trips` is one row per valid trip; every design choice follows from that.
- **Five dimensions** (zone, date, vendor, payment type, rate code); `dim_zone` is role-playing
  (pickup and dropoff).
- **Unknown-member handling:** lookup dimensions add an "Unknown (code X)" row for codes not in
  the seeds, so no trip drops out of joins if TLC adds a code.
- **`date_key` as YYYYMMDD integer:** compact, sortable and readable.
- **Aggregate fact tables** at day × zone and day × hour grain, sharing the same conformed
  dimensions, so the dashboard reads small tables.
- **Marts as tables** (fact incremental): read constantly, so fast reads matter more than storage.
- **[N] dbt tests** including referential integrity (relationships), grain uniqueness
  (unique_combination_of_columns), row-count reconciliation and re-checked quality rules.