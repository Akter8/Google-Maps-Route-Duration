"""Timezone-aware weekday sampling schedule."""
from __future__ import annotations
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

WINDOWS = ((time(5), time(7), 30), (time(7), time(10), 15), (time(10), time(15), 30),
           (time(15), time(19), 15), (time(19), time(22), 30))

def scheduled_slots(day: datetime) -> list[datetime]:
    """Return local slots, including 22:00 only when it is a window boundary (not sampled)."""
    if day.weekday() >= 5:
        return []
    result: list[datetime] = []
    for start, end, minutes in WINDOWS:
        cursor = datetime.combine(day.date(), start, tzinfo=day.tzinfo)
        stop = datetime.combine(day.date(), end, tzinfo=day.tzinfo)
        while cursor < stop:
            result.append(cursor)
            cursor += timedelta(minutes=minutes)
    return result

def intended_slot(now: datetime, tolerance_minutes: int = 7) -> datetime | None:
    """Most recent permitted local slot within tolerance; `now` must be timezone aware."""
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    candidates = [slot for slot in scheduled_slots(now) if slot <= now]
    if not candidates:
        return None
    nearest = min(candidates, key=lambda slot: abs((now - slot).total_seconds()))
    return nearest if abs((now - nearest).total_seconds()) <= tolerance_minutes * 60 else None

def local_now(timezone: str) -> datetime:
    return datetime.now(ZoneInfo(timezone))
