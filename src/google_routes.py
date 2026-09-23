"""Small, auditable client for Google Routes API Compute Routes."""
from __future__ import annotations
import re
from dataclasses import dataclass
import requests

ENDPOINT = "https://routes.googleapis.com/directions/v2:computeRoutes"

class GoogleRoutesError(RuntimeError): pass

@dataclass(frozen=True)
class RouteEstimate:
    duration_seconds: float
    static_duration_seconds: float
    distance_meters: int

def duration_seconds(value: str) -> float:
    match = re.fullmatch(r"([0-9]+(?:\.[0-9]+)?)s", value)
    if not match: raise GoogleRoutesError("Google returned an invalid duration")
    return float(match.group(1))

class GoogleRoutesClient:
    def __init__(self, api_key: str, timeout_seconds: int = 20) -> None:
        self.api_key, self.timeout_seconds = api_key, timeout_seconds

    def compute(self, origin: str, destination: str) -> RouteEstimate:
        body = {"origin": {"address": origin}, "destination": {"address": destination},
                "travelMode": "DRIVE", "routingPreference": "TRAFFIC_AWARE_OPTIMAL",
                "trafficModel": "BEST_GUESS"}
        try:
            response = requests.post(ENDPOINT, json=body, timeout=self.timeout_seconds,
                headers={"Content-Type": "application/json", "X-Goog-Api-Key": self.api_key,
                "X-Goog-FieldMask": "routes.duration,routes.staticDuration,routes.distanceMeters"})
        except requests.RequestException as exc:
            raise GoogleRoutesError(f"Google request failed: {type(exc).__name__}") from exc
        if not response.ok:
            raise GoogleRoutesError(f"Google API HTTP {response.status_code}")
        routes = response.json().get("routes", [])
        if not routes: raise GoogleRoutesError("Google returned no route")
        route = routes[0]
        try:
            return RouteEstimate(duration_seconds(route["duration"]), duration_seconds(route["staticDuration"]), int(route["distanceMeters"]))
        except (KeyError, ValueError) as exc:
            raise GoogleRoutesError("Google response missing required route fields") from exc
