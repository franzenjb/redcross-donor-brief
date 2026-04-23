"""ARC Geography — the authoritative Red Cross geography layer.

Source: `Master_ARC_Geography_2022` FeatureServer, layer 5 (Counties) at
https://services.arcgis.com/pGfbNJoYypmNq86F/arcgis/rest/services/Master_ARC_Geography_2022/FeatureServer/5

Published from the "ARC Geography Base" web map owned by Jeff Franzen at the
Red Cross NHQ AGOL org. Publicly queryable, no token. 3,162 US counties with:
  - FIPS (5-digit), County, State
  - Chapter, Region, Division (RC org hierarchy)
  - 2023 demographics (pop, age, race, income, housing)

This module fetches the whole layer once (paged if needed), caches to
`src/geography/arc_geography_cache.json`, and serves lookups in-memory.
Refresh by deleting the cache file.
"""
from __future__ import annotations
import json
import os
import urllib.request
import urllib.parse
from functools import lru_cache
from typing import Iterable

SERVICE = (
    "https://services.arcgis.com/pGfbNJoYypmNq86F/arcgis/rest/services/"
    "Master_ARC_Geography_2022/FeatureServer/5"
)
UA = "redcross-donor-brief/0.1"

_DIR = os.path.dirname(os.path.abspath(__file__))
_CACHE = os.path.join(_DIR, "arc_geography_cache.json")

# Fields we actually use downstream. Keeping the list tight makes the cache
# small and the queries fast. Demographics can be added here later.
_FIELDS = [
    "FIPS", "County", "County_Long", "State",
    "Chapter", "ECODE",
    "Region", "RCODE",
    "Division", "DCODE",
    "FEMA_Region",
    # Chapter HQ contact (carried on every county row)
    "Address", "Address_2", "City", "Zip", "Phone", "Time_Zone",
    # Area
    "SQ_MI",
    # Demographics
    "Pop_2023", "Pop_Den_2023", "Total_HH_2023", "Avg_HH_Size_2023",
    "Median_Age_2023", "Med_HH_Inc_2023", "Med_Home_Val_2023",
    "Youth_0_14_Pop_2023", "Yng_Adult_15_24_Pop_2023",
    "Adult_25_64_Pop_2023", "Seniors_65_up_Pop_2023",
    "Owner_2023", "Renter_2023", "Vacant_2023",
    "Diversity_Index_2023",
]


def _fetch_page(offset: int, page_size: int = 2000) -> list[dict]:
    qs = urllib.parse.urlencode({
        "where": "1=1",
        "outFields": ",".join(_FIELDS),
        "returnGeometry": "false",
        "resultOffset": str(offset),
        "resultRecordCount": str(page_size),
        "orderByFields": "FIPS ASC",
        "f": "json",
    })
    req = urllib.request.Request(
        f"{SERVICE}/query?{qs}",
        headers={"User-Agent": UA, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    return [f["attributes"] for f in data.get("features", [])]


def _fetch_all() -> list[dict]:
    out: list[dict] = []
    offset = 0
    page_size = 2000
    while True:
        page = _fetch_page(offset, page_size)
        if not page:
            break
        out.extend(page)
        if len(page) < page_size:
            break
        offset += page_size
    return out


def _build_cache() -> list[dict]:
    rows = _fetch_all()
    # Normalize: ensure FIPS is 5-digit string, derive SAME code.
    for r in rows:
        fips = str(r.get("FIPS") or "").strip().zfill(5)
        r["FIPS"] = fips
        r["same"] = "0" + fips  # NWS SAME = 0 + state_fips(2) + county_fips(3)
    with open(_CACHE, "w", encoding="utf-8") as f:
        json.dump(rows, f)
    return rows


@lru_cache(maxsize=1)
def _load() -> list[dict]:
    if os.path.exists(_CACHE):
        try:
            with open(_CACHE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return _build_cache()


def refresh() -> int:
    """Force-refresh the cache from the live FeatureService. Returns row count."""
    rows = _build_cache()
    _load.cache_clear()
    return len(rows)


# ---- Lookups ---------------------------------------------------------------


def all_counties() -> list[dict]:
    return _load()


def by_fips(fips_5: str | int) -> dict | None:
    fips = str(fips_5).zfill(5)
    for c in _load():
        if c["FIPS"] == fips:
            return c
    return None


def _norm(name: str) -> str:
    n = (name or "").strip().lower()
    for suf in (" county", " parish", " borough", " municipality",
                " census area", " city and borough"):
        if n.endswith(suf):
            n = n[: -len(suf)]
    return n.strip()


def by_state_county(state: str, county: str) -> dict | None:
    s = (state or "").strip().upper()
    n = _norm(county)
    for c in _load():
        if (c.get("State") or "").upper() == s and _norm(c.get("County") or "") == n:
            return c
    return None


def counties_in_state(state: str) -> list[dict]:
    s = (state or "").strip().upper()
    return [c for c in _load() if (c.get("State") or "").upper() == s]


def counties_in_chapter(chapter: str) -> list[dict]:
    return [c for c in _load() if (c.get("Chapter") or "") == chapter]


def counties_in_region(region: str) -> list[dict]:
    return [c for c in _load() if (c.get("Region") or "") == region]


def counties_in_division(division: str) -> list[dict]:
    return [c for c in _load() if (c.get("Division") or "") == division]


def chapters() -> list[str]:
    return sorted({c["Chapter"] for c in _load() if c.get("Chapter")})


def regions() -> list[str]:
    return sorted({c["Region"] for c in _load() if c.get("Region")})


def divisions() -> list[str]:
    return sorted({c["Division"] for c in _load() if c.get("Division")})


def same_codes_for(counties: Iterable[dict]) -> list[str]:
    return [c["same"] for c in counties if c.get("same")]


if __name__ == "__main__":
    rows = _load()
    print(f"ARC Geography: {len(rows)} counties cached at {_CACHE}")
    print(f"  {len(chapters())} chapters, {len(regions())} regions, {len(divisions())} divisions")
