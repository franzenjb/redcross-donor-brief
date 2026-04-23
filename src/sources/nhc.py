"""NHC Atlantic / Gulf hurricane products (free).

Current Storms JSON: https://www.nhc.noaa.gov/CurrentStorms.json
Detailed per-storm products at advisory endpoints.
"""
from __future__ import annotations
import urllib.request
import json
from typing import Iterable

UA = "redcross-donor-brief/0.1"
CURRENT = "https://www.nhc.noaa.gov/CurrentStorms.json"


def fetch_active() -> list[dict]:
    """Return currently active Atlantic & E. Pacific storms."""
    req = urllib.request.Request(CURRENT, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    out = []
    for s in data.get("activeStorms", []) or []:
        out.append({
            "id": s.get("id"),
            "name": s.get("name"),
            "classification": s.get("classification"),  # e.g. TS, HU, TD
            "basin": s.get("binNumber") or s.get("basin"),
            "intensity_mph": s.get("intensity"),
            "pressure_mb": s.get("pressure"),
            "lat": s.get("latitudeNumeric"),
            "lon": s.get("longitudeNumeric"),
            "movement_dir": s.get("movementDir"),
            "movement_speed_mph": s.get("movementSpeed"),
            "last_update": s.get("lastUpdate"),
            "advisory_url": s.get("publicAdvisory", {}).get("url") if isinstance(s.get("publicAdvisory"), dict) else None,
        })
    return out


# Rough bounding boxes for US states/territories that NHC storms can plausibly
# threaten. lat_min, lat_max, lon_min, lon_max (negative lon = W).
_STATE_BBOX = {
    "FL": (24.4, 31.1, -87.6, -79.9),
    "GA": (30.3, 35.0, -85.6, -80.8),
    "SC": (32.0, 35.2, -83.4, -78.5),
    "NC": (33.8, 36.6, -84.4, -75.4),
    "VA": (36.5, 39.5, -83.7, -75.2),
    "MD": (37.9, 39.7, -79.5, -75.0),
    "DE": (38.4, 39.8, -75.8, -75.0),
    "NJ": (38.9, 41.4, -75.6, -73.9),
    "NY": (40.5, 45.0, -79.8, -71.8),
    "CT": (40.9, 42.1, -73.7, -71.8),
    "RI": (41.1, 42.0, -71.9, -71.1),
    "MA": (41.2, 42.9, -73.5, -69.9),
    "NH": (42.7, 45.3, -72.6, -70.6),
    "ME": (43.0, 47.5, -71.1, -66.9),
    "AL": (30.1, 35.0, -88.5, -84.9),
    "MS": (30.1, 35.0, -91.7, -88.1),
    "LA": (28.9, 33.0, -94.1, -88.8),
    "TX": (25.8, 36.5, -106.7, -93.5),
    "PR": (17.8, 18.6, -67.3, -65.2),
    "VI": (17.6, 18.5, -65.1, -64.5),
    "HI": (18.9, 22.3, -160.3, -154.8),
}


def threatens_state(storm: dict, state: str, buffer_deg: float = 10.0) -> bool:
    """Is a storm within `buffer_deg` of this state's bounding box?"""
    box = _STATE_BBOX.get((state or "").upper())
    if not box:
        return False
    lat_min, lat_max, lon_min, lon_max = box
    try:
        lat = float(storm["lat"])
        lon = float(storm["lon"])
    except (KeyError, TypeError, ValueError):
        return False
    return (lat_min - buffer_deg) <= lat <= (lat_max + buffer_deg) \
        and (lon_min - buffer_deg) <= lon <= (lon_max + buffer_deg)


def threatens_any(storm: dict, states: Iterable[str], buffer_deg: float = 10.0) -> bool:
    return any(threatens_state(storm, s, buffer_deg) for s in states)


# Back-compat shim
def threatens_florida(storm: dict, buffer_deg: float = 10.0) -> bool:
    return threatens_state(storm, "FL", buffer_deg)


if __name__ == "__main__":
    storms = fetch_active()
    print(f"Active NHC storms: {len(storms)}")
    for s in storms:
        fl = " [THREATENS FL]" if threatens_state(s, "FL") else ""
        print(f"  {s['classification']} {s['name']} — {s['intensity_mph']} mph at ({s['lat']},{s['lon']}){fl}")
