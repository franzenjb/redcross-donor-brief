"""Assemble a briefing for a Red Cross region (any of the ~48 US regions)."""
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
    total_pop = sum((_num(c.get("Pop_2023")) or 0) for c in counties)
    total_sqmi = sum((float(c.get("SQ_MI") or 0)) for c in counties)

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

    alert_fips = {f[1:] for a in alerts for f in (a.get("same", []) or []) if isinstance(f, str) and len(f) == 6}
    fema_fips = {f for s in fema_affected_fips.values() for f in s}
    fire_fips = {f.get("county_fips") for f in fires if f.get("county_fips")}

    return {
        "geography": {
            "region": region_name,
            "chapters": chapters,
            "states": states,
            "county_count": len(counties),
            "counties": [
                {"fips": c["FIPS"], "name": c["County"], "state": c["State"], "chapter": c.get("Chapter")}
                for c in counties
            ],
            "county_fips": fips5,
            "division": division_name,
        },
        "summary": {
            "county_count": len(counties),
            "chapter_count": len(chapters),
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
            "wildfires_in_region": fires,
            "wildfires_state_total": fires_state_total,
            "nhc_storms_threatening": storms,
        },
        "recent": {
            "fema_declarations": list(fema_unique.values()),
        },
    }
