"""Assemble a briefing for a Red Cross region (any of the ~48 US regions)."""
from __future__ import annotations
from datetime import datetime, timezone

from ..geography import arc_geography as ag
from ..sources import nws, fema, nifc, nhc


def build(region_name: str, lookback_days_fema: int = 365) -> dict | None:
    counties = ag.counties_in_region(region_name)
    if not counties:
        return None

    fips5 = [c["FIPS"] for c in counties]
    same = [c["same"] for c in counties]
    states = sorted({c["State"] for c in counties if c.get("State")})
    chapters = sorted({c["Chapter"] for c in counties if c.get("Chapter")})
    division_name = counties[0].get("Division")

    same_set = set(same)
    fips_set = set(fips5)

    alerts: list[dict] = []
    for st in states:
        try:
            for a in nws.fetch_state(st):
                if set(a.get("same", []) or []) & same_set:
                    alerts.append(a)
        except Exception:
            pass
    alerts_by_event: dict[str, int] = {}
    for a in alerts:
        ev = a.get("event") or "Unknown"
        alerts_by_event[ev] = alerts_by_event.get(ev, 0) + 1

    fires: list[dict] = []
    fires_state_total = 0
    for st in states:
        try:
            all_st = nifc.fetch_state(f"US-{st}")
            fires_state_total += len(all_st)
            fires.extend(f for f in all_st if f.get("county_fips") in fips_set)
        except Exception:
            pass

    decs: list[dict] = []
    for st in states:
        try:
            for d in fema.fetch_state(st, lookback_days_fema):
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
            }

    try:
        storms = [s for s in nhc.fetch_active() if nhc.threatens_any(s, states)]
    except Exception as e:
        storms = [{"error": str(e)}]

    return {
        "geography": {
            "region": region_name,
            "chapters": chapters,
            "states": states,
            "county_count": len(counties),
            "division": division_name,
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
