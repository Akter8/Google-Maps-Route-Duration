from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo
from src.collector import collect, make_record, route_for_slot
from src.config import Route, Settings
from src.google_routes import RouteEstimate
def settings(): return Settings((Route("R1","private-a","private-b"),),"k","url","key")
def test_delay_calculation():
 r=make_record("R1", "outbound", datetime.now(ZoneInfo("America/Los_Angeles")),datetime.now(ZoneInfo("America/Los_Angeles")),RouteEstimate(600,480,1000)); assert r["traffic_delay_seconds"] == 120 and r["direction"] == "outbound"
def test_route_for_slot_reverses_from_1pm_through_before_7pm():
 route = Route("R1", "origin", "destination")
 assert route_for_slot(route, datetime(2026, 9, 22, 13, 0, tzinfo=ZoneInfo("America/Los_Angeles"))) == ("return", "destination", "origin")
 assert route_for_slot(route, datetime(2026, 9, 22, 18, 45, tzinfo=ZoneInfo("America/Los_Angeles"))) == ("return", "destination", "origin")
def test_route_for_slot_is_outbound_before_1pm_and_at_7pm():
 route = Route("R1", "origin", "destination")
 assert route_for_slot(route, datetime(2026, 9, 22, 12, 30, tzinfo=ZoneInfo("America/Los_Angeles"))) == ("outbound", "origin", "destination")
 assert route_for_slot(route, datetime(2026, 9, 22, 19, 0, tzinfo=ZoneInfo("America/Los_Angeles"))) == ("outbound", "origin", "destination")
def test_dry_run_never_creates_clients(monkeypatch):
 assert collect(settings(), now=datetime(2026,9,22,7,15,tzinfo=ZoneInfo("America/Los_Angeles")), dry_run=True) == 0
