from datetime import datetime
from zoneinfo import ZoneInfo
from src.scheduler import intended_slot, scheduled_slots
TZ=ZoneInfo("America/Los_Angeles")
def test_peak_slot_and_tolerance():
 assert intended_slot(datetime(2026,9,22,7,17,tzinfo=TZ),7).strftime("%H:%M") == "07:15"
 assert intended_slot(datetime(2026,9,22,7,23,tzinfo=TZ),7) is None
def test_weekend_and_boundaries():
 assert not scheduled_slots(datetime(2026,9,20,tzinfo=TZ)); assert intended_slot(datetime(2026,9,22,7,0,tzinfo=TZ)).strftime("%H:%M") == "07:00"
def test_dst_timezone_aware():
 slots=scheduled_slots(datetime(2026,3,9,12,tzinfo=TZ)); assert slots[0].tzinfo == TZ and slots[0].strftime("%H:%M") == "05:00"
