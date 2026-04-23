"""Render a briefing dict as plain-text talking points.

Phase 2 swaps this for an LLM-drafted paragraph. Phase 1 is deterministic.
"""
from __future__ import annotations


def render(briefing: dict) -> str:
    g = briefing["geography"]
    state = g.get("state") or ""
    lines: list[str] = []
    lines.append(f"=== {g['county']} County, {state} ===")
    lines.append(f"Chapter: {g['chapter'] or '(unknown)'}")
    lines.append(f"Region: {g.get('region') or '(unknown)'}")
    lines.append(f"Division: {g.get('division') or '(unknown)'}")
    lines.append(f"Generated: {briefing['generated_at']}")
    lines.append("")

    # Active alerts
    alerts = briefing.get("active", {}).get("nws_alerts", [])
    lines.append(f"ACTIVE NWS ALERTS ({len(alerts)}):")
    if alerts:
        for a in alerts:
            lines.append(f"  [{a.get('severity','?')}] {a.get('event')} — {a.get('headline')}")
    else:
        lines.append("  (none)")
    lines.append("")

    # NHC
    storms = briefing.get("active", {}).get("nhc_storms_threatening", [])
    lines.append(f"ACTIVE STORMS THREATENING {state or 'AREA'} ({len(storms)}):")
    if storms:
        for s in storms:
            if "error" in s:
                lines.append(f"  (error: {s['error']})")
            else:
                lines.append(f"  {s.get('classification')} {s.get('name')} — {s.get('intensity_mph')} mph")
    else:
        lines.append("  (none)")
    lines.append("")

    # Wildfires — in this county
    wfc = briefing.get("active", {}).get("wildfires_county", [])
    state_total = briefing.get("active", {}).get("wildfires_state_total", 0)
    lines.append(f"ACTIVE WILDFIRES IN COUNTY ({len(wfc)}; {state_total} statewide):")
    for w in wfc[:10]:
        if "error" in w:
            lines.append(f"  (error: {w['error']})")
        else:
            pct = f"{w.get('contained_pct')}%" if w.get('contained_pct') is not None else "?"
            acres = w.get('acres') or '?'
            lines.append(f"  {w.get('name')} — {acres} acres, {pct} contained ({w.get('cause') or 'cause unknown'})")
    lines.append("")

    # FEMA
    fema = briefing.get("recent", {}).get("fema_declarations", [])
    lines.append(f"RECENT FEMA DECLARATIONS AFFECTING COUNTY ({len(fema)}):")
    for d in fema[:10]:
        lines.append(f"  DR-{d.get('disaster_number')} {d.get('incident_type')} — {d.get('title')} ({d.get('declaration_date','')[:10]})")
    if len(fema) > 10:
        lines.append(f"  ... and {len(fema) - 10} more")

    return "\n".join(lines)
