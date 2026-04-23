"""Serve the ARC Geography lookup for the UI cascade.

Routes:
  GET /api/geography                     → index (states, divisions, region/chapter counts)
  GET /api/geography?state=FL            → counties in state
  GET /api/geography?chapter=ARC...      → counties in chapter
  GET /api/geography?region=...          → counties + chapters in region
  GET /api/geography?division=...        → counties in division
"""
from __future__ import annotations
import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.geography import arc_geography as ag  # noqa: E402


def _slim(rows):
    return [
        {
            "fips": r["FIPS"],
            "county": r["County"],
            "state": r["State"],
            "chapter": r.get("Chapter"),
            "region": r.get("Region"),
            "division": r.get("Division"),
        }
        for r in rows
    ]


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        state = (qs.get("state") or [None])[0]
        chapter = (qs.get("chapter") or [None])[0]
        region = (qs.get("region") or [None])[0]
        division = (qs.get("division") or [None])[0]

        try:
            if state:
                out = {"state": state.upper(), "counties": _slim(ag.counties_in_state(state))}
            elif chapter:
                rows = ag.counties_in_chapter(chapter)
                out = {"chapter": chapter, "counties": _slim(rows)}
            elif region:
                rows = ag.counties_in_region(region)
                chapters = sorted({r["Chapter"] for r in rows if r.get("Chapter")})
                out = {"region": region, "chapters": chapters, "counties": _slim(rows)}
            elif division:
                rows = ag.counties_in_division(division)
                out = {"division": division, "counties": _slim(rows)}
            else:
                rows = ag.all_counties()
                states = sorted({r["State"] for r in rows if r.get("State")})
                out = {
                    "states": states,
                    "divisions": ag.divisions(),
                    "regions": ag.regions(),
                    "chapters": ag.chapters(),
                    "county_count": len(rows),
                }
        except Exception as e:
            body = json.dumps({"error": str(e)}).encode("utf-8")
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(body)
            return

        body = json.dumps(out).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        self.wfile.write(body)
