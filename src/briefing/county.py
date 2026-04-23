"""Assemble a briefing for a single county (any US county)."""
from __future__ import annotations
from datetime import datetime, timezone

from ..geography.hierarchy import Hierarchy
from ..sources import nws, fema, nifc, nhc


def build(h: Hierarchy, lookback_days_fema: int = 180) -> dict:
    """Return a dict briefing for one county. Free-sources only in Phase 1."""
    # Active NWS alerts touching this county
    alerts = nws.fetch_counties([h.county_same], state=h.state)

    # FEMA declarations affecting this county
    decs = fema.fetch_counties([h.county_fips_5], lookback_days=lookback_days_fema, state=h.state)
    fema_unique: dict[int, dict] = {}
    for d in decs:
        n = d.get("disasterNumber")
        if n not in fema_unique:
            fema_unique[n] = {
                "disaster_number": n,
                "incident_type": d.get("incidentType"),
                "title": d.get("declarationTitle"),
                "declaration_date": d.get("declarationDate"),
                "incident_begin": d.get("incidentBeginDate"),
                "incident_end": d.get("incidentEndDate"),
            }

    # NIFC WFIGS current wildfires — filter to this county + state total
    try:
        wildfires_county = nifc.fetch_counties([h.county_fips_5], state=h.state)
        wildfires_state = nifc.fetch_state(f"US-{h.state}")
    except Exception as e:
        wildfires_county = [{"error": str(e)}]
        wildfires_state = []

    # NHC storms threatening this county's state
    try:
        storms = [s for s in nhc.fetch_active() if nhc.threatens_state(s, h.state)]
    except Exception as e:
        storms = [{"error": str(e)}]

    return {
        "geography": {
            "county": h.county_name,
            "state": h.state,
            "fips_5": h.county_fips_5,
            "chapter": h.chapter_name,
            "region": h.region_name,
            "division": h.division_name,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "active": {
            "nws_alerts": alerts,
            "nhc_storms_threatening": storms,
            "wildfires_county": wildfires_county,
            "wildfires_state_total": len(wildfires_state),
        },
        "recent": {
            "fema_declarations": list(fema_unique.values()),
        },
        "context": {},
        "red_cross_internal": {},
    }
