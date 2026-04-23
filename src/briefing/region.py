"""Assemble a briefing for the entire NCFL region."""
from __future__ import annotations
from datetime import datetime, timezone

from ..geography import hierarchy, ncfl
from ..sources import nws, fema, nifc, nhc


def build(lookback_days_fema: int = 365) -> dict:
    same = hierarchy.region_county_same_codes()
    fips5 = hierarchy.region_county_fips_5()

    alerts = nws.fetch_counties(same)
    alerts_by_event: dict[str, int] = {}
    for a in alerts:
        ev = a.get("event") or "Unknown"
        alerts_by_event[ev] = alerts_by_event.get(ev, 0) + 1

    fires = nifc.fetch_counties(fips5)
    fires_state_total = len(nifc.fetch_state("US-FL"))

    decs = fema.fetch_counties(fips5, lookback_days=lookback_days_fema)
    fema_unique: dict[int, dict] = {}
    for d in decs:
        n = d.get("disasterNumber")
        if n not in fema_unique:
            fema_unique[n] = {
                "disaster_number": n,
                "incident_type": d.get("incidentType"),
                "title": d.get("declarationTitle"),
                "declaration_date": d.get("declarationDate"),
            }

    try:
        storms = [s for s in nhc.fetch_active() if nhc.threatens_florida(s)]
    except Exception as e:
        storms = [{"error": str(e)}]

    return {
        "geography": {
            "region": ncfl.REGION_NAME,
            "chapters": list(ncfl.NCFL_CHAPTERS.keys()),
            "county_count": len(ncfl.all_counties_in_region()),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "active": {
            "nws_alert_count": len(alerts),
            "nws_alerts_by_event": alerts_by_event,
            "wildfires_in_region": fires,
            "wildfires_state_total": fires_state_total,
            "nhc_storms_threatening": storms,
        },
        "recent": {
            "fema_declarations": list(fema_unique.values()),
        },
    }
