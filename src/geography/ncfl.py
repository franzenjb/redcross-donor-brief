"""North & Central Florida region: chapter → county mapping.

NOTE: this is an approximation — confirm against the Red Cross org chart
and adjust. Chapter names and county assignments change over time. The list
below is our best starting point; anything wrong here gets fixed by editing
this one file.
"""
from __future__ import annotations

# Chapter → list of county names (match fl_counties.FL_COUNTIES_RAW names exactly)
NCFL_CHAPTERS: dict[str, list[str]] = {
    "Central Florida and the U.S. Virgin Islands": [
        "Orange",
        "Osceola",
        "Seminole",
        "Brevard",
        "Volusia",
        "Flagler",
        "Lake",
        "Sumter",
    ],
    "North Florida": [
        "Alachua",
        "Baker",
        "Bradford",
        "Citrus",
        "Columbia",
        "Dixie",
        "Gilchrist",
        "Hamilton",
        "Hernando",
        "Lafayette",
        "Levy",
        "Marion",
        "Putnam",
        "Suwannee",
        "Taylor",
        "Union",
    ],
    "Northeast Florida": [
        "Clay",
        "Duval",
        "Nassau",
        "St. Johns",
    ],
}

REGION_NAME = "North & Central Florida Region"


def all_counties_in_region() -> list[str]:
    counties = []
    for chapter_counties in NCFL_CHAPTERS.values():
        counties.extend(chapter_counties)
    return sorted(set(counties))


def chapter_for_county(county_name: str) -> str | None:
    for chapter, counties in NCFL_CHAPTERS.items():
        if county_name in counties:
            return chapter
    return None
