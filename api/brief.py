"""Vercel Python serverless endpoint.

Routes:
  GET /api/brief?county=Putnam
  GET /api/brief?chapter=North%20Florida
  GET /api/brief?region=1
"""
from __future__ import annotations
import json
import os
import sys
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

# Make the top-level `src` package importable when deployed to Vercel.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.geography.hierarchy import from_county  # noqa: E402
from src.briefing import county as county_brief  # noqa: E402
from src.briefing import chapter as chapter_brief  # noqa: E402
from src.briefing import region as region_brief  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        county = (qs.get("county") or [None])[0]
        chapter = (qs.get("chapter") or [None])[0]
        region = (qs.get("region") or [None])[0]
        lookback = int((qs.get("lookback") or ["365"])[0])

        try:
            if county:
                h = from_county(county)
                if not h:
                    return self._json({"error": f"county '{county}' not found"}, 404)
                out = county_brief.build(h, lookback_days_fema=lookback)
            elif chapter:
                out = chapter_brief.build(chapter, lookback_days_fema=lookback)
                if not out:
                    return self._json({"error": f"chapter '{chapter}' not found"}, 404)
            elif region:
                out = region_brief.build(lookback_days_fema=lookback)
            else:
                return self._json({"error": "provide ?county=X or ?chapter=Y or ?region=1"}, 400)
        except Exception as e:
            return self._json({"error": str(e)}, 500)

        return self._json(out, 200)

    def _json(self, body: dict, status: int):
        data = json.dumps(body, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "public, max-age=60")
        self.end_headers()
        self.wfile.write(data)
