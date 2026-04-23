"""NIFC WFIGS — current federal wildfire incidents (free, no key).

This replaces the deprecated InciWeb RSS. The ArcGIS FeatureService exposes
IncidentName, POOCounty, POOFips, DailyAcres, PercentContained, and more.
"""
from __future__ import annotations
import urllib.request
import urllib.parse
import json
from datetime import datetime, timezone
from typing import Iterable

UA = "redcross-donor-brief/0.1"
BASE = (
    "https://services3.arcgis.com/T4QMspbfLg3qTGWY/arcgis/rest/services/"
    "WFIGS_Incident_Locations_Current/FeatureServer/0/query"
)

OUT_FIELDS = [
    "IncidentName",
    "IncidentShortDescription",
    "IncidentTypeCategory",
    "FireDiscoveryDateTime",
    "IncidentSize",
    "PercentContained",
    "FireCause",
    "POOCounty",
    "POOFips",
    "POOState",
    "POOCity",
    "GACC",
    "TotalIncidentPersonnel",
    "IncidentManagementOrganization",
    "InitialLatitude",
    "InitialLongitude",
    "UniqueFireIdentifier",
]


def fetch_state(state: str = "US-FL") -> list[dict]:
    """Active wildfire incidents for a state (POOState like 'US-FL')."""
    qs = urllib.parse.urlencode({
        "where": f"POOState='{state}'",
        "outFields": ",".join(OUT_FIELDS),
        "returnGeometry": "false",
        "f": "json",
        "resultRecordCount": "1000",
    })
    req = urllib.request.Request(f"{BASE}?{qs}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    return [_normalize(f["attributes"]) for f in data.get("features", [])]


def fetch_counties(fips_5digit: Iterable[str], state: str | None = None) -> list[dict]:
    """Active wildfires whose POOFips matches any given 5-digit FIPS.

    `state` = 2-letter USPS (e.g. 'FL'). If omitted, derived from first FIPS.
    """
    wanted = set(str(f).zfill(5) for f in fips_5digit)
    if state is None and wanted:
        from ..geography import arc_geography as ag
        first = next(iter(wanted))
        row = ag.by_fips(first)
        if row:
            state = row.get("State")
    all_fires = fetch_state(f"US-{(state or 'FL').upper()}")
    return [f for f in all_fires if f.get("county_fips") in wanted]


def _normalize(a: dict) -> dict:
    return {
        "name": a.get("IncidentName"),
        "short_desc": a.get("IncidentShortDescription"),
        "type": a.get("IncidentTypeCategory"),  # WF = wildfire, RX = prescribed
        "discovery": _ms_to_iso(a.get("FireDiscoveryDateTime")),
        "acres": a.get("IncidentSize"),
        "contained_pct": a.get("PercentContained"),
        "cause": a.get("FireCause"),
        "county": a.get("POOCounty"),
        "county_fips": a.get("POOFips"),
        "state": a.get("POOState"),
        "city": a.get("POOCity"),
        "gacc": a.get("GACC"),
        "personnel": a.get("TotalIncidentPersonnel"),
        "org": a.get("IncidentManagementOrganization"),
        "lat": a.get("InitialLatitude"),
        "lon": a.get("InitialLongitude"),
        "fire_id": a.get("UniqueFireIdentifier"),
    }


def _ms_to_iso(ms: int | None) -> str | None:
    if not ms:
        return None
    try:
        return datetime.fromtimestamp(int(ms) / 1000, tz=timezone.utc).isoformat()
    except (ValueError, TypeError):
        return None


if __name__ == "__main__":
    fires = fetch_state("US-FL")
    print(f"Active WF incidents in FL: {len(fires)}")
    for f in fires[:10]:
        c = f.get("contained_pct")
        pct = f"{c}%" if c is not None else "?"
        print(f"  {f['name']} — {f['county']} County, {f['acres']} acres, {pct} contained")
