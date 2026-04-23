"""PowerOutage.us — county-level outage counts.

Their API is paid but the homepage JSON is publicly readable.
Using the state-level aggregate endpoint that powers the site:
  https://poweroutage.us/api/web/states/Florida

If that changes / is rate-limited, fall back to scraping the state page.
"""
from __future__ import annotations
import urllib.request
import json

UA = "redcross-donor-brief/0.1"


def fetch_state(state: str = "Florida") -> dict:
    """Return state-level power outage summary.

    Shape not guaranteed stable — treat as best-effort.
    """
    url = f"https://poweroutage.us/api/web/states/{state}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.load(r)
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    d = fetch_state("Florida")
    print(json.dumps(d, indent=2)[:500])
