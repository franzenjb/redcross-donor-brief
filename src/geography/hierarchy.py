"""Resolve any US county into the Red Cross briefing geography.

Backed by `arc_geography` (the authoritative ARC Geography FeatureService).
Every Hierarchy carries county → chapter → region → division for the full US,
plus chapter HQ contact info and demographics.
"""
from __future__ import annotations
from dataclasses import dataclass, field

from . import arc_geography as ag


@dataclass
class Hierarchy:
    county_name: str
    state: str
    county_fips_5: str
    county_same: str
    chapter_name: str | None = None
    region_name: str | None = None
    division_name: str | None = None
    row: dict = field(default_factory=dict)  # full ARC Geography row


def _to_hierarchy(row: dict | None) -> Hierarchy | None:
    if not row:
        return None
    return Hierarchy(
        county_name=row.get("County") or "",
        state=row.get("State") or "",
        county_fips_5=row.get("FIPS") or "",
        county_same=row.get("same") or "",
        chapter_name=row.get("Chapter"),
        region_name=row.get("Region"),
        division_name=row.get("Division"),
        row=row,
    )


def from_state_county(state: str, county: str) -> Hierarchy | None:
    return _to_hierarchy(ag.by_state_county(state, county))


def from_fips(fips_5: str | int) -> Hierarchy | None:
    return _to_hierarchy(ag.by_fips(fips_5))


def counties_in_chapter(chapter: str) -> list[Hierarchy]:
    return [h for h in (_to_hierarchy(r) for r in ag.counties_in_chapter(chapter)) if h]


def counties_in_region(region: str) -> list[Hierarchy]:
    return [h for h in (_to_hierarchy(r) for r in ag.counties_in_region(region)) if h]


def counties_in_division(division: str) -> list[Hierarchy]:
    return [h for h in (_to_hierarchy(r) for r in ag.counties_in_division(division)) if h]
