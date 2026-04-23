"""AirNow — current AQI (free, requires API key).

Register at https://docs.airnowapi.org/ and set AIRNOW_API_KEY env var.
"""
from __future__ import annotations
import os
import urllib.request
import urllib.parse
import json

UA = "redcross-donor-brief/0.1"
BASE = "https://www.airnowapi.org/aq/observation/zipCode/current/"


def fetch_zip(zip_code: str, distance_miles: int = 25) -> list[dict]:
    key = os.environ.get("AIRNOW_API_KEY")
    if not key:
        raise RuntimeError("AIRNOW_API_KEY env var not set — register at airnowapi.org")
    qs = urllib.parse.urlencode({
        "format": "application/json",
        "zipCode": zip_code,
        "distance": distance_miles,
        "API_KEY": key,
    })
    req = urllib.request.Request(f"{BASE}?{qs}", headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)
