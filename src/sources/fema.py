"""FEMA disaster declarations — fema.gov OpenFEMA API (free, no key).

Declarations are at the county level with FIPS codes.
"""
from __future__ import annotations
import urllib.request
import urllib.parse
import json
from datetime import datetime, timedelta, timezone
from typing import Iterable

BASE = "https://www.fema.gov/api/open/v2/DisasterDeclarationsSummaries"
UA = "redcross-donor-brief/0.1"


def fetch_state(state: str = "FL", lookback_days: int = 365) -> list[dict]:
    """Return FEMA declarations for a state within a lookback window."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    filt = f"state eq '{state}' and declarationDate ge '{cutoff}'"
    qs = urllib.parse.urlencode({
        "$filter": filt,
        "$orderby": "declarationDate desc",
        "$top": "1000",
    })
    req = urllib.request.Request(
        f"{BASE}?{qs}",
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    return data.get("DisasterDeclarationsSummaries", [])


def fetch_counties(county_fips_5digit: Iterable[str], lookback_days: int = 365) -> list[dict]:
    """Return declarations matching county FIPS (5-digit, state+county)."""
    wanted = set(county_fips_5digit)
    all_decs = fetch_state("FL", lookback_days)
    out = []
    for d in all_decs:
        # FEMA uses fipsStateCode + fipsCountyCode (separate fields)
        state_fips = d.get("fipsStateCode") or ""
        county_fips = d.get("fipsCountyCode") or ""
        full = f"{state_fips}{county_fips}"
        if full in wanted:
            out.append(d)
    return out


if __name__ == "__main__":
    decs = fetch_state("FL", 365)
    print(f"FL FEMA declarations (last 365 days): {len(decs)}")
    # Unique disaster numbers
    seen = {}
    for d in decs:
        n = d.get("disasterNumber")
        if n not in seen:
            seen[n] = d
    for d in list(seen.values())[:10]:
        print(f"  DR-{d.get('disasterNumber')} {d.get('incidentType')} — {d.get('declarationTitle')}")
