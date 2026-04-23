"""Assemble a briefing for a Red Cross chapter (aggregation across its counties)."""
from __future__ import annotations
from datetime import datetime, timezone, date

from ..geography import arc_geography as ag
from ..sources import nws, fema, nifc, nhc


def _num(s):
    if s is None:
        return None
    try:
        return int(str(s).replace(",", "").replace("$", "").strip())
    except (ValueError, TypeError):
        return None


def _days_since(dt_str: str | None) -> int | None:
    if not dt_str:
        return None
    try:
        d = datetime.fromisoformat(dt_str.replace("Z", "+00:00")).date()
        return (date.today() - d).days
    except (ValueError, TypeError):
        return None


def build(chapter_name: str, lookback_days_fema: int = 365) -> dict | None:
    counties = ag.counties_in_chapter(chapter_name)
    if not counties:
        return None

    fips5 = [c["FIPS"] for c in counties]
    same = [c["same"] for c in counties]
    states = sorted({c["State"] for c in counties if c.get("State")})
    region_name = counties[0].get("Region")
    division_name = counties[0].get("Division")
    # Chapter HQ fields are identical across all counties in a chapter
    hq = counties[0]
    total_pop = sum((_num(c.get("Pop_2023")) or 0) for c in counties)
    total_sqmi = sum((float(c.get("SQ_MI") or 0)) for c in counties)

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
    for st in states:
        try:
            fires.extend(f for f in nifc.fetch_state(f"US-{st}") if f.get("county_fips") in fips_set)
        except Exception:
            pass
    fire_acres = sum(float(f.get("acres") or 0) for f in fires)

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
    fema_affected_fips: dict[int, set] = {}
    for d in decs:
        n = d.get("disasterNumber")
        full = f"{d.get('fipsStateCode') or ''}{d.get('fipsCountyCode') or ''}".zfill(5)
        if n not in fema_unique:
            fema_unique[n] = {
                "disaster_number": n,
                "incident_type": d.get("incidentType"),
                "title": d.get("declarationTitle"),
                "declaration_date": d.get("declarationDate"),
                "incident_begin": d.get("incidentBeginDate"),
                "incident_end": d.get("incidentEndDate"),
            }
        fema_affected_fips.setdefault(n, set()).add(full)
    for n, s in fema_affected_fips.items():
        fema_unique[n]["affected_fips"] = sorted(s)

    latest_fema = max(
        (d.get("declaration_date") for d in fema_unique.values() if d.get("declaration_date")),
        default=None,
    )

    try:
        storms = [s for s in nhc.fetch_active() if nhc.threatens_any(s, states)]
    except Exception as e:
        storms = [{"error": str(e)}]

    # Union of all fips across any active disaster/fire/alert — for map shading
    alert_fips = {f[1:] for a in alerts for f in (a.get("same", []) or []) if isinstance(f, str) and len(f) == 6}
    fema_fips = {f for s in fema_affected_fips.values() for f in s}
    fire_fips = {f.get("county_fips") for f in fires if f.get("county_fips")}

    return {
        "geography": {
            "chapter": chapter_name,
            "counties": [
                {"fips": c["FIPS"], "name": c["County"], "state": c["State"]}
                for c in counties
            ],
            "county_fips": fips5,
            "states": states,
            "region": region_name,
            "division": division_name,
        },
        "chapter_hq": {
            "address": hq.get("Address"),
            "address_2": hq.get("Address_2"),
            "city": hq.get("City"),
            "zip": hq.get("Zip"),
            "phone": hq.get("Phone"),
            "time_zone": hq.get("Time_Zone"),
        },
        "summary": {
            "county_count": len(counties),
            "total_population": total_pop,
            "total_sq_mi": round(total_sqmi, 0),
            "active_fire_count": len(fires),
            "active_fire_acres": round(fire_acres, 1),
            "active_alert_count": len(alerts),
            "recent_fema_count": len(fema_unique),
            "latest_fema_declaration_date": latest_fema,
            "days_since_latest_fema": _days_since(latest_fema),
        },
        "map_layers": {
            "fema_fips": sorted(fema_fips),
            "fire_fips": sorted(fire_fips),
            "alert_fips": sorted(alert_fips),
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
