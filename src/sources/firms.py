"""NASA FIRMS — wildfire satellite hotspots (free, requires MAP_KEY).

Register: https://firms.modaps.eosdis.nasa.gov/api/area/
Set FIRMS_MAP_KEY env var.
"""
from __future__ import annotations
import os
import urllib.request
import csv
import io
from typing import Literal

UA = "redcross-donor-brief/0.1"
BASE = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"

Sensor = Literal["VIIRS_SNPP_NRT", "VIIRS_NOAA20_NRT", "MODIS_NRT"]


def fetch_bbox(
    bbox: tuple[float, float, float, float] = (-88.0, 24.0, -80.0, 31.5),
    days: int = 1,
    sensor: Sensor = "VIIRS_SNPP_NRT",
) -> list[dict]:
    """Return wildfire hotspots within bbox (west, south, east, north) for last N days."""
    key = os.environ.get("FIRMS_MAP_KEY")
    if not key:
        raise RuntimeError("FIRMS_MAP_KEY env var not set — register at firms.modaps.eosdis.nasa.gov/api/area/")
    w, s, e, n = bbox
    url = f"{BASE}/{key}/{sensor}/{w},{s},{e},{n}/{days}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        text = r.read().decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(text)))
    return rows


# Florida bounding box: approximately -87.5 W to -79.9 E, 24.4 S to 31.0 N
FL_BBOX = (-87.6, 24.4, -79.9, 31.1)


if __name__ == "__main__":
    rows = fetch_bbox(FL_BBOX, days=3)
    print(f"FIRMS hotspots in FL bbox (3 days): {len(rows)}")
    for r in rows[:5]:
        print(f"  {r.get('acq_date')} {r.get('acq_time')} at ({r.get('latitude')},{r.get('longitude')}) conf={r.get('confidence')}")
