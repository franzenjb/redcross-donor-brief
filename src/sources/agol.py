"""Red Cross AGOL internal layers.

This module runs inside an AGOL Notebook. `GIS("home")` authenticates as the
Notebook owner — no OAuth needed when the notebook lives in the Red Cross org.

For local dev (outside AGOL), we stub these to return empty lists so the
briefing tool is still runnable on free public data only.
"""
from __future__ import annotations
from typing import Iterable

try:
    from arcgis.gis import GIS  # type: ignore
    from arcgis.features import FeatureLayer  # type: ignore
    _HAS_ARCGIS = True
except ImportError:
    _HAS_ARCGIS = False


def _gis():
    if not _HAS_ARCGIS:
        return None
    return GIS("home")


def fetch_dat_dispatches(item_id: str, county_fips: Iterable[str] | None = None, lookback_days: int = 7) -> list[dict]:
    """1-800 call / DAT dispatch layer. Filter to confirmed responses in lookback."""
    if not _HAS_ARCGIS:
        return []
    # TODO: build WHERE clause once we know the real field names.
    # Placeholder:
    #   f"status IN ('Dispatched','Completed') AND created_date >= CURRENT_TIMESTAMP - {lookback_days}"
    layer = FeatureLayer.fromitem(_gis().content.get(item_id))
    features = layer.query(where="1=1", out_fields="*", return_geometry=True).features
    return [f.as_dict for f in features]


def fetch_smoke_alarm_installs(item_id: str, county_fips: Iterable[str] | None = None, lookback_days: int = 30) -> list[dict]:
    """Home Fire Campaign smoke alarm installs."""
    if not _HAS_ARCGIS:
        return []
    layer = FeatureLayer.fromitem(_gis().content.get(item_id))
    features = layer.query(where="1=1", out_fields="*").features
    return [f.as_dict for f in features]


def fetch_shelters(item_id: str, active_only: bool = True) -> list[dict]:
    """RC View shelter layer — openings & occupancy."""
    if not _HAS_ARCGIS:
        return []
    layer = FeatureLayer.fromitem(_gis().content.get(item_id))
    where = "status = 'Open'" if active_only else "1=1"
    features = layer.query(where=where, out_fields="*").features
    return [f.as_dict for f in features]


def fetch_donors(item_id: str, county_fips: Iterable[str] | None = None) -> list[dict]:
    """Donor layer — returns dicts with name, address, email, segment, giving info."""
    if not _HAS_ARCGIS:
        return []
    layer = FeatureLayer.fromitem(_gis().content.get(item_id))
    features = layer.query(where="1=1", out_fields="*").features
    return [f.as_dict for f in features]
