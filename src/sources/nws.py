"""NWS active alerts — api.weather.gov (free, no key).

Active watches/warnings/advisories. Filter by state, then by county FIPS if needed.
"""
from __future__ import annotations
import urllib.request
import json
from typing import Iterable

BASE = "https://api.weather.gov/alerts/active"
UA = "redcross-donor-brief/0.1 (+https://kg.jbf.com)"


def fetch_state(state: str = "FL") -> list[dict]:
    """Return all active NWS alerts for a state."""
    req = urllib.request.Request(
        f"{BASE}?area={state}",
        headers={"User-Agent": UA, "Accept": "application/geo+json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    return [_normalize(f) for f in data.get("features", [])]


def fetch_counties(county_fips: Iterable[str]) -> list[dict]:
    """Return active alerts whose SAME/UGC codes include any of the given county FIPS.

    SAME codes are 6-digit: leading 0 + state FIPS (2) + county FIPS (3).
    e.g. Orange County FL = 012095 → SAME 012095
    """
    wanted = set(county_fips)
    all_alerts = fetch_state("FL")
    out = []
    for a in all_alerts:
        same = set(a.get("same", []) or [])
        if same & wanted:
            out.append(a)
    return out


def _normalize(feature: dict) -> dict:
    p = feature.get("properties", {})
    return {
        "id": p.get("id"),
        "event": p.get("event"),
        "severity": p.get("severity"),
        "urgency": p.get("urgency"),
        "certainty": p.get("certainty"),
        "headline": p.get("headline"),
        "description": p.get("description"),
        "instruction": p.get("instruction"),
        "sent": p.get("sent"),
        "effective": p.get("effective"),
        "expires": p.get("expires"),
        "area_desc": p.get("areaDesc"),
        "same": (p.get("geocode") or {}).get("SAME", []),
        "ugc": (p.get("geocode") or {}).get("UGC", []),
        "geometry": feature.get("geometry"),
    }


if __name__ == "__main__":
    import sys
    alerts = fetch_state("FL")
    print(f"Active FL alerts: {len(alerts)}")
    for a in alerts[:5]:
        print(f"  [{a['severity']}] {a['event']} — {a['area_desc']}")
