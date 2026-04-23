"""Florida county list with FIPS codes.

State FIPS 12. County FIPS are the 3-digit codes; full FIPS = state+county (5-digit).
SAME codes for NWS are 6-digit with leading 0: "0" + full FIPS.
"""
from __future__ import annotations

# (county_fips_3digit, name)
FL_COUNTIES_RAW: list[tuple[str, str]] = [
    ("001", "Alachua"),
    ("003", "Baker"),
    ("005", "Bay"),
    ("007", "Bradford"),
    ("009", "Brevard"),
    ("011", "Broward"),
    ("013", "Calhoun"),
    ("015", "Charlotte"),
    ("017", "Citrus"),
    ("019", "Clay"),
    ("021", "Collier"),
    ("023", "Columbia"),
    ("027", "DeSoto"),
    ("029", "Dixie"),
    ("031", "Duval"),
    ("033", "Escambia"),
    ("035", "Flagler"),
    ("037", "Franklin"),
    ("039", "Gadsden"),
    ("041", "Gilchrist"),
    ("043", "Glades"),
    ("045", "Gulf"),
    ("047", "Hamilton"),
    ("049", "Hardee"),
    ("051", "Hendry"),
    ("053", "Hernando"),
    ("055", "Highlands"),
    ("057", "Hillsborough"),
    ("059", "Holmes"),
    ("061", "Indian River"),
    ("063", "Jackson"),
    ("065", "Jefferson"),
    ("067", "Lafayette"),
    ("069", "Lake"),
    ("071", "Lee"),
    ("073", "Leon"),
    ("075", "Levy"),
    ("077", "Liberty"),
    ("079", "Madison"),
    ("081", "Manatee"),
    ("083", "Marion"),
    ("085", "Martin"),
    ("086", "Miami-Dade"),
    ("087", "Monroe"),
    ("089", "Nassau"),
    ("091", "Okaloosa"),
    ("093", "Okeechobee"),
    ("095", "Orange"),
    ("097", "Osceola"),
    ("099", "Palm Beach"),
    ("101", "Pasco"),
    ("103", "Pinellas"),
    ("105", "Polk"),
    ("107", "Putnam"),
    ("109", "St. Johns"),
    ("111", "St. Lucie"),
    ("113", "Santa Rosa"),
    ("115", "Sarasota"),
    ("117", "Seminole"),
    ("119", "Sumter"),
    ("121", "Suwannee"),
    ("123", "Taylor"),
    ("125", "Union"),
    ("127", "Volusia"),
    ("129", "Wakulla"),
    ("131", "Walton"),
    ("133", "Washington"),
]

STATE_FIPS = "12"


def full_fips(county_fips_3: str) -> str:
    """'095' → '12095'"""
    return f"{STATE_FIPS}{county_fips_3.zfill(3)}"


def same_code(county_fips_3: str) -> str:
    """'095' → '012095' (NWS SAME code)"""
    return f"0{STATE_FIPS}{county_fips_3.zfill(3)}"


def find(name: str) -> tuple[str, str] | None:
    """Case-insensitive county name lookup. Returns (fips_3, name) or None."""
    n = name.strip().lower().replace(" county", "").replace(",", "").replace("fl", "").strip()
    for f, cname in FL_COUNTIES_RAW:
        if cname.lower() == n:
            return f, cname
    return None


def all_counties() -> list[dict]:
    return [
        {
            "name": name,
            "fips_3": f,
            "fips_5": full_fips(f),
            "same": same_code(f),
        }
        for f, name in FL_COUNTIES_RAW
    ]
