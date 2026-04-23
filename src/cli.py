"""Command-line entry point.

  python -m src.cli --county "Orange"
  python -m src.cli --county "Duval" --json
"""
from __future__ import annotations
import argparse
import json
import sys

from .geography.hierarchy import from_county
from .briefing import county as county_brief
from .briefing import chapter as chapter_brief
from .briefing import region as region_brief
from .render import narrative


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Red Cross donor briefing tool")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--county", help="County name (FL), e.g. 'Orange' or 'St. Johns'")
    g.add_argument("--chapter", help="Chapter name, e.g. 'North Florida'")
    g.add_argument("--region", action="store_true", help="Region-wide briefing (NCFL)")
    p.add_argument("--json", action="store_true", help="Output raw JSON briefing")
    p.add_argument("--lookback-fema", type=int, default=365, help="FEMA lookback days (default 365)")
    args = p.parse_args(argv)

    if args.county:
        h = from_county(args.county)
        if not h:
            print(f"ERROR: county '{args.county}' not found in FL county list", file=sys.stderr)
            return 2
        brief = county_brief.build(h, lookback_days_fema=args.lookback_fema)
        if args.json:
            print(json.dumps(brief, indent=2, default=str))
        else:
            print(narrative.render(brief))
        return 0

    if args.chapter:
        brief = chapter_brief.build(args.chapter, lookback_days_fema=args.lookback_fema)
        if not brief:
            print(f"ERROR: chapter '{args.chapter}' not in NCFL config", file=sys.stderr)
            return 2
        print(json.dumps(brief, indent=2, default=str))
        return 0

    if args.region:
        brief = region_brief.build(lookback_days_fema=args.lookback_fema)
        print(json.dumps(brief, indent=2, default=str))
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
