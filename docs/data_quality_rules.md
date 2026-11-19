| Reason code | Rule | Yellow Aug 2026 | Action | Why |
|---|---|---|---|---|
| missing_timestamp | Pickup or dropoff is null | 0 rows (0%) | Reject | Can't place the trip in time |
| dropoff_not_after_pickup | Dropoff must be after pickup | 1,204 rows (0.03%) | Reject | Impossible trip; likely a clock error |
| null passenger_count | Passenger count missing | 85,310 rows (2.4%) | Keep | Common for valid trips; not reliable enough to reject |