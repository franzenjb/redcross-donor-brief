"""Command-line entry point.

  python -m src.cli --state FL --county Putnam
  python -m src.cli --state CA --county "Los Angeles" --json
  python -m src.cli --chapter "ARC of Northeast Florida"
  python -m src.cli --region "North and Central Florida Region"
  python -m src.cli --fips 12107
"""
from __future__ import annotations
import argparse
import json
import sys

from .geography.hierarchy import from_state_county, from_fips
from .briefing import county as county_brief
from .briefing import chapter as chapter_brief
from .briefing import region as region_brief
from .render import narrative


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Red Cross donor briefing tool")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--county", help="County name (pair with --state)")
    g.add_argument("--fips", help="5-digit county FIPS (alternative to --state/--county)")
    g.add_argument("--chapter", help="Red Cross chapter name")
    g.add_argument("--region", help="Red Cross region name")
    p.add_argument("--state", help="2-letter state (required with --county)")
    p.add_argument("--json", action="store_true", help="Output raw JSON briefing")
    p.add_argument("--lookback-fema", type=int, default=365, help="FEMA lookback days (default 365)")
    args = p.parse_args(argv)

    if args.county or args.fips:
        if args.fips:
            h = from_fips(args.fips)
            if not h:
                print(f"ERROR: FIPS '{args.fips}' not found in ARC Geography", file=sys.stderr)
                return 2
        else:
            if not args.state:
                print("ERROR: --state is required with --county", file=sys.stderr)
                return 2
            h = from_state_county(args.state, args.county)
            if not h:
                print(f"ERROR: county '{args.county}' not found in state '{args.state}'", file=sys.stderr)
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
            print(f"ERROR: chapter '{args.chapter}' not found in ARC Geography", file=sys.stderr)
            return 2
        print(json.dumps(brief, indent=2, default=str))
        return 0

    if args.region:
        brief = region_brief.build(args.region, lookback_days_fema=args.lookback_fema)
        if not brief:
            print(f"ERROR: region '{args.region}' not found in ARC Geography", file=sys.stderr)
            return 2
        print(json.dumps(brief, indent=2, default=str))
        return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
