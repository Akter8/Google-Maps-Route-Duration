from datetime import datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo
from src.collector import collect, make_record
from src.config import Route, Settings
from src.google_routes import RouteEstimate
def settings(): return Settings((Route("R1","private-a","private-b"),),"k","url","key")
def test_delay_calculation():
 r=make_record("R1",datetime.now(ZoneInfo("America/Los_Angeles")),datetime.now(ZoneInfo("America/Los_Angeles")),RouteEstimate(600,480,1000)); assert r["traffic_delay_seconds"] == 120
def test_dry_run_never_creates_clients(monkeypatch):
 assert collect(settings(), now=datetime(2026,9,22,7,15,tzinfo=ZoneInfo("America/Los_Angeles")), dry_run=True) == 0
