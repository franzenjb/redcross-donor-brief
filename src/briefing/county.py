"""Assemble a briefing for a single county."""
from __future__ import annotations
from datetime import datetime, timezone

from ..geography.hierarchy import Hierarchy
from ..sources import nws, fema, usgs_flood, nifc


def build(h: Hierarchy, lookback_days_fema: int = 180) -> dict:
    """Return a dict briefing for one county. Free-sources only in Phase 1."""
    # Active NWS alerts touching this county
    alerts = nws.fetch_counties([h.county_same])

    # FEMA declarations affecting this county
    decs = fema.fetch_counties([h.county_fips_5], lookback_days=lookback_days_fema)

    # Unique disaster numbers (a single disaster generates many per-county records)
    fema_unique = {}
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

    # NIFC WFIGS current wildfires — filter to this county
    try:
        wildfires_county = nifc.fetch_counties([h.county_fips_5])
        wildfires_state = nifc.fetch_state("US-FL")
    except Exception as e:
        wildfires_county = [{"error": str(e)}]
        wildfires_state = []

    return {
        "geography": {
            "county": h.county_name,
            "fips_5": h.county_fips_5,
            "chapter": h.chapter_name,
            "region": h.region_name,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "active": {
            "nws_alerts": alerts,
            "nhc_storms_threatening": _nhc_if_threatens(),
            "wildfires_county": wildfires_county,
            "wildfires_state_total": len(wildfires_state),
        },
        "recent": {
            "fema_declarations": list(fema_unique.values()),
        },
        "context": {
            # Populated in later phases (ACS, ALICE, NRI, etc.)
        },
        "red_cross_internal": {
            # Populated when run inside AGOL Notebook
        },
    }


def _nhc_if_threatens() -> list[dict]:
    from ..sources import nhc
    try:
        return [s for s in nhc.fetch_active() if nhc.threatens_florida(s)]
    except Exception as e:
        return [{"error": str(e)}]
