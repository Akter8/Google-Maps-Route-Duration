"""Configuration loading and validation. Sensitive route data stays in environment variables."""
from __future__ import annotations

import json
import os
from dataclasses import dataclass


class ConfigError(ValueError):
    """Raised for invalid or incomplete runtime configuration."""


@dataclass(frozen=True)
class Route:
    id: str
    origin: str
    destination: str


@dataclass(frozen=True)
class Settings:
    routes: tuple[Route, ...]
    google_api_key: str
    supabase_url: str
    supabase_service_role_key: str
    max_monthly_google_requests: int = 4500
    timezone: str = "America/Los_Angeles"
    slot_tolerance_minutes: int = 7


def load_routes(raw: str) -> tuple[Route, ...]:
    try:
        payload = json.loads(raw)
        items = payload["routes"]
    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ConfigError("ROUTES_JSON must be JSON with a routes array") from exc
    if not isinstance(items, list) or not 1 <= len(items) <= 6:
        raise ConfigError("ROUTES_JSON must contain between 1 and 6 routes")
    routes: list[Route] = []
    ids: set[str] = set()
    for item in items:
        if not isinstance(item, dict):
            raise ConfigError("Each route must be an object")
        route_id, origin, destination = item.get("id"), item.get("origin"), item.get("destination")
        if not isinstance(route_id, str) or route_id not in {f"R{i}" for i in range(1, 7)}:
            raise ConfigError("Route IDs must be R1 through R6")
        if route_id in ids or not all(isinstance(v, str) and v.strip() for v in (origin, destination)):
            raise ConfigError("Route IDs must be unique and origins/destinations must be non-empty")
        ids.add(route_id)
        routes.append(Route(route_id, origin.strip(), destination.strip()))
    return tuple(routes)


def load_settings(require_services: bool = True) -> Settings:
    routes_raw = os.getenv("ROUTES_JSON")
    if not routes_raw:
        raise ConfigError("ROUTES_JSON is required")
    try:
        limit = int(os.getenv("MAX_MONTHLY_GOOGLE_REQUESTS", "4500"))
        tolerance = int(os.getenv("SLOT_TOLERANCE_MINUTES", "7"))
    except ValueError as exc:
        raise ConfigError("Request limit and slot tolerance must be integers") from exc
    if limit < 1 or tolerance < 0 or tolerance > 30:
        raise ConfigError("Request limit must be positive and tolerance must be 0-30 minutes")
    settings = Settings(load_routes(routes_raw), os.getenv("GOOGLE_MAPS_API_KEY", ""),
                        os.getenv("SUPABASE_URL", ""), os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
                        limit, os.getenv("TRAFFIC_TIMEZONE", "America/Los_Angeles"), tolerance)
    if require_services and not all((settings.google_api_key, settings.supabase_url, settings.supabase_service_role_key)):
        raise ConfigError("GOOGLE_MAPS_API_KEY, SUPABASE_URL, and SUPABASE_SERVICE_ROLE_KEY are required")
    return settings
