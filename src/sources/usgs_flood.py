"""USGS Water Services — stream gauges above action / flood stages (free, no key).

Returns current stage/discharge for active sites in a state, plus NWS flood
thresholds when joined with AHPS (separate service).
"""
from __future__ import annotations
import urllib.request
import urllib.parse
import json
from typing import Iterable

BASE = "https://waterservices.usgs.gov/nwis/iv/"
UA = "redcross-donor-brief/0.1"


def fetch_state(state: str = "fl", parameter: str = "00065") -> list[dict]:
    """Return current instantaneous values for all active gauges in a state.

    parameter 00065 = gage height (ft), 00060 = discharge (cfs).
    """
    qs = urllib.parse.urlencode({
        "format": "json",
        "stateCd": state,
        "parameterCd": parameter,
        "siteStatus": "active",
    })
    req = urllib.request.Request(
        f"{BASE}?{qs}",
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    out = []
    for ts in data.get("value", {}).get("timeSeries", []):
        src = ts.get("sourceInfo", {})
        vals = ts.get("values", [{}])[0].get("value", [])
        if not vals:
            continue
        latest = vals[-1]
        geo = src.get("geoLocation", {}).get("geogLocation", {})
        out.append({
            "site_code": src.get("siteCode", [{}])[0].get("value"),
            "site_name": src.get("siteName"),
            "lat": geo.get("latitude"),
            "lon": geo.get("longitude"),
            "value": float(latest.get("value")) if latest.get("value") not in (None, "") else None,
            "dateTime": latest.get("dateTime"),
            "parameter": parameter,
        })
    return out


# TODO: integrate AHPS flood-stage thresholds for at-or-above-action filtering.
# AHPS service: https://water.weather.gov/ahps2/index.php?wfo=xxx — no clean API,
# but USGS has NWS flood categories in some metadata. Alternative: NWS forecast
# points at api.weather.gov/gridpoints or manual threshold table per gauge.


if __name__ == "__main__":
    g = fetch_state("fl")
    print(f"FL active gage-height sites: {len(g)}")
    for s in g[:5]:
        print(f"  {s['site_name']}: {s['value']} ft at {s['dateTime']}")
