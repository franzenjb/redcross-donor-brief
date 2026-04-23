"""Assemble a briefing for a Red Cross chapter (aggregation across its counties).

Chapter resolution comes from the authoritative ARC Geography layer — works for
any of the ~226 US Red Cross chapters.
"""
from __future__ import annotations
from datetime import datetime, timezone

from ..geography import arc_geography as ag
from ..sources import nws, fema, nifc, nhc


def build(chapter_name: str, lookback_days_fema: int = 365) -> dict | None:
    counties = ag.counties_in_chapter(chapter_name)
    if not counties:
        return None

    fips5 = [c["FIPS"] for c in counties]
    same = [c["same"] for c in counties]
    states = sorted({c["State"] for c in counties if c.get("State")})
    region_name = counties[0].get("Region")
    division_name = counties[0].get("Division")

    # Collect NWS alerts across every state the chapter touches
    alerts: list[dict] = []
    same_set = set(same)
    for st in states:
        try:
            all_st = nws.fetch_state(st)
            for a in all_st:
                if set(a.get("same", []) or []) & same_set:
                    alerts.append(a)
        except Exception:
            pass
    alerts_by_event: dict[str, int] = {}
    for a in alerts:
        ev = a.get("event") or "Unknown"
        alerts_by_event[ev] = alerts_by_event.get(ev, 0) + 1

    # Active wildfires in any county in the chapter
    fires: list[dict] = []
    for st in states:
        try:
            all_st = nifc.fetch_state(f"US-{st}")
            fips_set = set(fips5)
            fires.extend(f for f in all_st if f.get("county_fips") in fips_set)
        except Exception:
            pass

    # FEMA declarations across states the chapter covers
    decs: list[dict] = []
    fips_set = set(fips5)
    for st in states:
        try:
            all_st = fema.fetch_state(st, lookback_days_fema)
            for d in all_st:
                full = f"{d.get('fipsStateCode') or ''}{d.get('fipsCountyCode') or ''}".zfill(5)
                if full in fips_set:
                    decs.append(d)
        except Exception:
            pass
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

    # NHC storms threatening any state the chapter covers
    try:
        storms = [s for s in nhc.fetch_active() if nhc.threatens_any(s, states)]
    except Exception as e:
        storms = [{"error": str(e)}]

    return {
        "geography": {
            "chapter": chapter_name,
            "counties": [f"{c['County']}, {c['State']}" for c in counties],
            "states": states,
            "region": region_name,
            "division": division_name,
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
