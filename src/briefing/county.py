"""Assemble a briefing for a single county (any US county)."""
from __future__ import annotations
from datetime import datetime, timezone, date

from ..geography.hierarchy import Hierarchy
from ..sources import nws, fema, nifc, nhc


def _num(s):
    """Convert comma/dollar formatted strings to int; return None if not parseable."""
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


def build(h: Hierarchy, lookback_days_fema: int = 180) -> dict:
    alerts = nws.fetch_counties([h.county_same], state=h.state)

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

    try:
        wildfires_county = nifc.fetch_counties([h.county_fips_5], state=h.state)
        wildfires_state = nifc.fetch_state(f"US-{h.state}")
    except Exception as e:
        wildfires_county = [{"error": str(e)}]
        wildfires_state = []

    try:
        storms = [s for s in nhc.fetch_active() if nhc.threatens_state(s, h.state)]
    except Exception as e:
        storms = [{"error": str(e)}]

    # Summary numbers gift officers care about
    active_fire_acres = sum(
        float(f.get("acres") or 0) for f in wildfires_county if not f.get("error")
    )
    latest_fema = None
    if fema_unique:
        latest_fema = max(
            (d.get("declaration_date") for d in fema_unique.values() if d.get("declaration_date")),
            default=None,
        )
    r = h.row or {}

    return {
        "geography": {
            "county": h.county_name,
            "county_long": r.get("County_Long"),
            "state": h.state,
            "fips_5": h.county_fips_5,
            "chapter": h.chapter_name,
            "region": h.region_name,
            "division": h.division_name,
            "fema_region": r.get("FEMA_Region"),
            "sq_mi": r.get("SQ_MI"),
        },
        "chapter_hq": {
            "address": r.get("Address"),
            "address_2": r.get("Address_2"),
            "city": r.get("City"),
            "zip": r.get("Zip"),
            "phone": r.get("Phone"),
            "time_zone": r.get("Time_Zone"),
        },
        "demographics": {
            "population": _num(r.get("Pop_2023")),
            "pop_density_per_sqmi": _num(r.get("Pop_Den_2023")),
            "households": _num(r.get("Total_HH_2023")),
            "avg_hh_size": r.get("Avg_HH_Size_2023"),
            "median_age": r.get("Median_Age_2023"),
            "median_hh_income": _num(r.get("Med_HH_Inc_2023")),
            "median_home_value": _num(r.get("Med_Home_Val_2023")),
            "seniors_65_plus": _num(r.get("Seniors_65_up_Pop_2023")),
            "youth_0_14": _num(r.get("Youth_0_14_Pop_2023")),
            "owner_occupied": _num(r.get("Owner_2023")),
            "renter_occupied": _num(r.get("Renter_2023")),
            "vacant": _num(r.get("Vacant_2023")),
            "diversity_index": _num(r.get("Diversity_Index_2023")),
        },
        "summary": {
            "active_fire_count": sum(1 for f in wildfires_county if not f.get("error")),
            "active_fire_acres": round(active_fire_acres, 1),
            "active_alert_count": len(alerts),
            "recent_fema_count": len(fema_unique),
            "latest_fema_declaration_date": latest_fema,
            "days_since_latest_fema": _days_since(latest_fema),
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
    }
