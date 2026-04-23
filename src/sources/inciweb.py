"""InciWeb — federal wildfire incidents (free, RSS/KML).

RSS by state FIPS: https://inciweb.nwcg.gov/feeds/rss/incidents/state/{FIPS}/
"""
from __future__ import annotations
import urllib.request
import xml.etree.ElementTree as ET

UA = "redcross-donor-brief/0.1"


def fetch_state(state_fips: str = "12") -> list[dict]:
    """Return active InciWeb incidents for a state (FIPS). FL = 12."""
    url = f"https://inciweb.nwcg.gov/feeds/rss/incidents/state/{state_fips}/"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        text = r.read().decode("utf-8", errors="replace")
    root = ET.fromstring(text)
    out = []
    for item in root.iter("item"):
        out.append({
            "title": _text(item, "title"),
            "link": _text(item, "link"),
            "description": _text(item, "description"),
            "pub_date": _text(item, "pubDate"),
        })
    return out


def _text(el, tag: str) -> str | None:
    child = el.find(tag)
    return child.text if child is not None else None


if __name__ == "__main__":
    incidents = fetch_state("12")
    print(f"InciWeb FL incidents: {len(incidents)}")
    for i in incidents[:5]:
        print(f"  {i['title']} ({i['pub_date']})")
