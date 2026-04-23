"""Assemble a briefing for a Red Cross chapter (aggregation across its counties)."""
from __future__ import annotations
from datetime import datetime, timezone

from ..geography import fl_counties, ncfl
from ..sources import nws, fema, nifc, nhc


def build(chapter_name: str, lookback_days_fema: int = 365) -> dict | None:
    counties = ncfl.NCFL_CHAPTERS.get(chapter_name)
    if not counties:
        return None

    # Build FIPS / SAME sets for the chapter's counties
    fips5 = []
    same = []
    for cname in counties:
        hit = fl_counties.find(cname)
        if hit:
            f3, _ = hit
            fips5.append(fl_counties.full_fips(f3))
            same.append(fl_counties.same_code(f3))

    # Active alerts touching any county in chapter
    alerts = nws.fetch_counties(same)
    # Group alerts by event type
    alerts_by_event: dict[str, int] = {}
    for a in alerts:
        ev = a.get("event") or "Unknown"
        alerts_by_event[ev] = alerts_by_event.get(ev, 0) + 1

    # Active wildfires anywhere in chapter
    fires = nifc.fetch_counties(fips5)

    # FEMA declarations affecting any county in chapter
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
                "incident_begin": d.get("incidentBeginDate"),
                "incident_end": d.get("incidentEndDate"),
            }

    # NHC storms threatening FL (region-scope but surfaced here too)
    try:
        storms = [s for s in nhc.fetch_active() if nhc.threatens_florida(s)]
    except Exception as e:
        storms = [{"error": str(e)}]

    return {
        "geography": {
            "chapter": chapter_name,
            "counties": counties,
            "region": ncfl.REGION_NAME,
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "active": {
            "nws_alert_count": len(alerts),
            "nws_alerts_by_event": alerts_by_event,
            "nws_alerts": alerts,
            "wildfires": fires,
            "nhc_storms_threatening": storms,
        },
        "recent": {
            "fema_declarations": list(fema_unique.values()),
        },
    }
