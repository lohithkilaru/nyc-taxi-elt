# Data Quality Rules

Applied in `dbt/models/intermediate/int_trips_checked.sql`.
Rules apply to both yellow and green trips. A row gets the **first** reason that matches;
rows that match none are valid. Rejected rows are quarantined in `int_trip_rejects`,
never deleted, and a test enforces raw rows = validated + rejected for every source file.

## Rejection rules

| # | Reason code | Rule | Yellow rows (%) | Green rows (%) | Action | Why |
|---|---|---|---|---|---|---|
| 1 | `missing_timestamp` | Pickup or dropoff time is null | | | Reject | The trip can't be placed in time |
| 2 | `pickup_outside_file_month` | Pickup month differs from the file's month | | | Reject | Trips belong to their pickup month; prevents double counting across files |
| 3 | `dropoff_not_after_pickup` | Dropoff is at or before pickup | | | Reject | Physically impossible; meter or clock error |
| 4 | `trip_over_24h` | Trip lasts more than 24 hours | | | Reject | Almost certainly a meter left running |
| 5 | `negative_amount` | Fare or total is below zero | | | Reject | Refunds, voids or corrections, not real trips |
| 6 | `non_positive_distance` | Distance is zero or negative | | | Reject | Cancelled trips or GPS errors (revisit if the share is large) |
| 7 | `duplicate_trip` | Same trip appears more than once in a file | | | Reject extra copies | Would double count revenue |

A duplicate is the same service, vendor, pickup and dropoff time, pickup and dropoff zone,
and total amount within one source file. The first copy is kept.

## Checked but kept

| Check | Yellow rows (%) | Green rows (%) | Decision | Why |
|---|---|---|---|---|
| Null `passenger_count` | | | Keep | Common in valid trips; driver-entered and unreliable |
| Codes not in the lookup seeds | | | Keep, noted | Recorded as a finding; relationship tests flag them on Day 7 |

## Known trade-offs

- **Border trips** (crossing midnight at month end) are judged by **pickup** time. If TLC files
  some of them in the following month's file, those are rejected under rule 2. To revisit after
  checking how often this happens.
- Thresholds (24 hours, zero distance) are deliberately simple and can be tightened after review.

## Results

*To fill in after `dbt build --select intermediate`: reject counts by reason and overall reject rate per service.*