"""NHC Atlantic / Gulf hurricane products (free).

Current Storms JSON: https://www.nhc.noaa.gov/CurrentStorms.json
Detailed per-storm products at advisory endpoints.
"""
from __future__ import annotations
import urllib.request
import json

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


def threatens_florida(storm: dict, buffer_deg: float = 10.0) -> bool:
    """Rough heuristic — is a storm within buffer degrees of FL bounding box?"""
    try:
        lat = float(storm["lat"])
        lon = float(storm["lon"])
    except (KeyError, TypeError, ValueError):
        return False
    # FL box
    return (24.4 - buffer_deg) <= lat <= (31.1 + buffer_deg) and (-87.6 - buffer_deg) <= lon <= (-79.9 + buffer_deg)


if __name__ == "__main__":
    storms = fetch_active()
    print(f"Active NHC storms: {len(storms)}")
    for s in storms:
        fl = " [THREATENS FL]" if threatens_florida(s) else ""
        print(f"  {s['classification']} {s['name']} — {s['intensity_mph']} mph at ({s['lat']},{s['lon']}){fl}")
