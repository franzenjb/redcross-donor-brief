"""List FL counties + chapters for the UI dropdown."""
from __future__ import annotations
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.geography import fl_counties, ncfl  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        out = {
            "region": ncfl.REGION_NAME,
            "chapters": {
                name: sorted(counties)
                for name, counties in ncfl.NCFL_CHAPTERS.items()
            },
            "all_fl_counties": [c["name"] for c in fl_counties.all_counties()],
            "ncfl_counties": ncfl.all_counties_in_region(),
        }
        body = json.dumps(out).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "public, max-age=3600")
        self.end_headers()
        self.wfile.write(body)
