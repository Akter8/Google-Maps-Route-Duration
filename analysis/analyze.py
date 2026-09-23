"""Print factual route-duration summaries from Supabase."""
from __future__ import annotations
import argparse, os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from src.supabase_db import TrafficDatabase

def summarize(frame: pd.DataFrame) -> dict[str, pd.DataFrame]:
    frame = frame[frame.api_success].copy()
    frame["scheduled_slot"] = pd.to_datetime(frame["scheduled_slot"])
    frame["departure_time"] = frame.scheduled_slot.dt.strftime("%H:%M")
    agg = ["count", "mean", "median", lambda x: x.quantile(.75), lambda x: x.quantile(.9), lambda x: x.quantile(.95), "max", "std"]
    per_route = frame.groupby("route_id").agg(duration_seconds=agg, traffic_delay_seconds=["median", lambda x: x.quantile(.9)])
    by_time = frame.groupby("departure_time").duration_seconds.agg(["median", lambda x: x.quantile(.75), lambda x: x.quantile(.9)])
    by_weekday = frame.groupby("day_of_week").duration_seconds.agg(["median", lambda x: x.quantile(.9)])
    return {"per route": per_route, "by departure time": by_time, "by weekday": by_weekday}

def main() -> None:
    p = argparse.ArgumentParser(); p.add_argument("--route-id"); args = p.parse_args()
    db = TrafficDatabase(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    data = db.fetch_observations({"route_id": args.route_id})
    if not data: print("No observations found."); return
    for label, table in summarize(pd.DataFrame(data)).items(): print(f"\n{label.upper()}\n{table.round(1).to_string()}")
if __name__ == "__main__": main()
