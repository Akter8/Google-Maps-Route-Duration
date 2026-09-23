# Traffic travel-time tracker

A private-route, traffic-aware commute observation system. GitHub Actions invokes a Python collector every five minutes on weekdays; the application converts the actual execution time to a Los Angeles sampling slot, avoids duplicates, queries Google Compute Routes, and writes only non-identifying measurements to Supabase.

## Setup

1. Create a Supabase project and run [`supabase_schema.sql`](supabase_schema.sql) in its SQL Editor.
2. In Google Cloud, enable **Routes API**, attach billing, create a server API key restricted to Routes API, and configure a budget alert and quota.
3. Add these GitHub Actions repository secrets: `GOOGLE_MAPS_API_KEY`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, and `ROUTES_JSON`.
4. Make `ROUTES_JSON` a compact private value such as `{"routes":[{"id":"R1","origin":"private origin","destination":"private destination"}]}`. Never commit it, a `.env`, addresses, or keys.
5. Enable Actions. The workflow runs every five minutes on weekdays and exits harmlessly outside a sampling slot. Use its `force` input only for a deliberate test.

Only route IDs (`R1`–`R6`) and measurements reach `traffic_observations`; addresses are never logged or stored. Before each route call, the collector checks for an existing slot and atomically reserves a request in Supabase. Its unique `(route_id, scheduled_slot)` constraint makes retries idempotent.

## Schedule and commands

Scheduling uses `America/Los_Angeles`, including DST. Weekday windows are: 05:00–07:00 every 30 minutes; 07:00–10:00 every 15; 10:00–15:00 every 30; 15:00–19:00 every 15; and 19:00–22:00 every 30. The default seven-minute tolerance maps 07:14–07:17 to 07:15, while storing both actual and intended timestamps. Set `SLOT_TOLERANCE_MINUTES` (0–30) to change it.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export ROUTES_JSON='{"routes":[{"id":"R1","origin":"...","destination":"..."}]}'
python -m src.collector --dry-run
export GOOGLE_MAPS_API_KEY='...'; export SUPABASE_URL='https://<project>.supabase.co'; export SUPABASE_SERVICE_ROLE_KEY='...'
python -m src.collector --force
pytest -q
python analysis/analyze.py --route-id R1
python analysis/export_csv.py --route-id R1 --start-date 2026-09-01 --end-date 2026-09-30 --output traffic.csv
```

Dry run needs only `ROUTES_JSON` and writes/calls nothing. `--force` bypasses only scheduling. Export supports date, route, weekday, and time filters.

## Cost and references

The default `MAX_MONTHLY_GOOGLE_REQUESTS=4500` applies a conservative request cap. Compute Routes is billed per request; `TRAFFIC_AWARE_OPTIMAL` is a higher-cost, higher-latency tier. Keep a Google Cloud budget alert and quota as independent safeguards. `duration` is traffic-aware and `staticDuration` is preserved so the collector calculates traffic delay.

Implementation follows Google’s [Compute Routes](https://developers.google.com/maps/documentation/routes/compute_route_directions), [traffic routing](https://developers.google.com/maps/documentation/routes/config_trade_offs), and [billing](https://developers.google.com/maps/documentation/routes/usage-and-billing) documentation, Supabase [Python guidance](https://supabase.com/docs/reference/python/installing), and GitHub [scheduled workflows](https://docs.github.com/actions/reference/events-that-trigger-workflows#schedule).
