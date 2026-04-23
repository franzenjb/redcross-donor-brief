"""Resolve donor → county → chapter → region and expose helpers."""
from __future__ import annotations
from dataclasses import dataclass

from . import fl_counties, ncfl


@dataclass
class Hierarchy:
    county_name: str
    county_fips_3: str
    county_fips_5: str
    county_same: str
    chapter_name: str | None
    region_name: str


def from_county(county_name: str) -> Hierarchy | None:
    hit = fl_counties.find(county_name)
    if not hit:
        return None
    f3, name = hit
    return Hierarchy(
        county_name=name,
        county_fips_3=f3,
        county_fips_5=fl_counties.full_fips(f3),
        county_same=fl_counties.same_code(f3),
        chapter_name=ncfl.chapter_for_county(name),
        region_name=ncfl.REGION_NAME,
    )


def region_county_same_codes() -> list[str]:
    """All SAME codes for counties in NCFL region — used to filter NWS alerts."""
    out = []
    for c in ncfl.all_counties_in_region():
        hit = fl_counties.find(c)
        if hit:
            out.append(fl_counties.same_code(hit[0]))
    return out


def region_county_fips_5() -> list[str]:
    out = []
    for c in ncfl.all_counties_in_region():
        hit = fl_counties.find(c)
        if hit:
            out.append(fl_counties.full_fips(hit[0]))
    return out
