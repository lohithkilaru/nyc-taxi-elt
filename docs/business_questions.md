## 1. Which pickup zones and hours generate the most revenue?

**Query:** `dbt/analyses/q1_revenue_by_zone_hour.sql`

[Finding: which zones and hours top the list, with numbers.]
[Explanation: e.g., driven by trip volume or by high fares.]

## 2. How much does the congestion relief zone fee add per trip, and where is it paid most?

**Query:** `dbt/analyses/q2_cbd_fee.sql`

[Finding: average fee when paid, share of trips paying it in the top zones.]
[Which zones and boroughs pay the most in total.]

## 3. What share of trips are airport trips, and what do they earn?

**Query:** `dbt/analyses/q3_airport_trips.sql`

[Finding: share of trips vs. share of revenue; average revenue airport vs. non-airport.]
[Difference between trips from and to the airport.]

## 4. How do tip rates vary by payment type, borough and time of day?

**Query:** `dbt/analyses/q4_tip_rates.sql`

[Finding: card tip rate overall; how it changes by borough and time of day.]

**Caveat:** TLC records credit card tips only. Cash tips are not captured, so the near-zero
cash tip rate reflects a recording limitation, not passenger behavior.

## 5. Where do yellow and green taxis compete in the same zones?

**Query:** `dbt/analyses/q5_yellow_green_overlap.sql`

[Finding: which zones have substantial trips from both services, and where.]
[Whether this matches green taxi street-hail rules (outer boroughs, upper Manhattan).]

---

## Most surprising finding

[One sentence. This is the hook for the README, demo video and LinkedIn post.]