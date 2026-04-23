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


def fetch_counties(same_codes: Iterable[str], state: str | None = None) -> list[dict]:
    """Return active alerts whose SAME codes include any of the given codes.

    SAME codes are 6-digit: leading 0 + state FIPS (2) + county FIPS (3).
    e.g. Orange County FL = 012095 → SAME 012095
    If `state` given, scope the fetch to that state for efficiency.
    """
    wanted = set(same_codes)
    # Infer state from first SAME code if not given (digits 1-2 = state FIPS)
    if state is None:
        for s in wanted:
            if len(s) >= 3:
                _STATE_FIPS_TO_USPS.get(s[1:3])
                state = _STATE_FIPS_TO_USPS.get(s[1:3])
                break
    all_alerts = fetch_state(state or "US")
    out = []
    for a in all_alerts:
        same = set(a.get("same", []) or [])
        if same & wanted:
            out.append(a)
    return out


_STATE_FIPS_TO_USPS = {
    "01":"AL","02":"AK","04":"AZ","05":"AR","06":"CA","08":"CO","09":"CT","10":"DE",
    "11":"DC","12":"FL","13":"GA","15":"HI","16":"ID","17":"IL","18":"IN","19":"IA",
    "20":"KS","21":"KY","22":"LA","23":"ME","24":"MD","25":"MA","26":"MI","27":"MN",
    "28":"MS","29":"MO","30":"MT","31":"NE","32":"NV","33":"NH","34":"NJ","35":"NM",
    "36":"NY","37":"NC","38":"ND","39":"OH","40":"OK","41":"OR","42":"PA","44":"RI",
    "45":"SC","46":"SD","47":"TN","48":"TX","49":"UT","50":"VT","51":"VA","53":"WA",
    "54":"WV","55":"WI","56":"WY","72":"PR","78":"VI",
}


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
