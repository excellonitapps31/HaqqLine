# HaqqLine signed-off sandbox pack

Pack id: `sandbox_decree_43_2013_table_v1`

This document is a demonstration extract, not an official DLD/RERA publication. Figures are synthetic for the Ignyte sandbox.

## Disclaimer

Information from a signed-off published rule pack in a sandbox. Not legal advice. Not a determination.

## Permitted increase (Decree 43/2013 style bands used in this sandbox)

Compare current annual rent C to the area index I.

gap = (I − C) / C

- If gap < 10%: permitted increase is 0%
- If gap < 20%: 5%
- If gap < 30%: 10%
- If gap < 40%: 15%
- Otherwise: 20%

permitted_new_rent = C × (1 + permitted_increase)

If proposed rent is greater than permitted_new_rent, the proposal is outside the band. Still information, not a ruling.

## Area index table (AED per year)

| Area key | Label | Index AED |
| --- | --- | --- |
| downtown_dubai | Downtown Dubai | 120000 |
| jlt | Jumeirah Lakes Towers | 85000 |
| international_city | International City | 42000 |
| dubai_marina | Dubai Marina | 110000 |
| al_barsha | Al Barsha | 90000 |

Unknown area: do not invent an index. Escalate to a human.

## Worked JLT example

Index 85000. Current 80000. gap = (85000−80000)/80000 = 6.25% → permitted increase 0%. Permitted new rent 80000.
Proposed 80000 is within band. Proposed 95000 is outside band.

## Synthetic Ejari (never invent a contract)

| Ejari id | Area | Annual rent AED | Term | Status |
| --- | --- | --- | --- | --- |
| EJ-1001 | downtown_dubai | 100000 | 2025-01-01 to 2026-12-31 | registered |
| EJ-1002 | jlt | 78000 | 2024-09-01 to 2026-08-31 | registered |
| EJ-1003 | dubai_marina | 95000 | 2025-03-15 to 2027-03-14 | registered |

Any other Ejari id: found false, invented false.

## Tools

Live HTTPS tools on https://haqqline.excellonit.net/api/v1 :

- lookup_rera_band
- lookup_ejari
- submit_to_human_queue (requires caller_confirmed true)
- escalate_human
