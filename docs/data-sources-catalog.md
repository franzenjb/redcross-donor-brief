# Data Sources Catalog

Every feed the briefing tool can tap. Grouped by access tier.

---

## Active hazards & events (current, real-time)

| Source | What it gives | Endpoint / access | Geography unit |
|---|---|---|---|
| **NWS alerts** | All active watches/warnings (tornado, severe storm, flood, heat, winter, etc.) | `api.weather.gov/alerts/active?area=FL` (free, no key) | Polygon / county / zone |
| **NHC products** | Atlantic hurricane cone, wind probs, storm surge | `nhc.noaa.gov/gis/` (KMZ/shapefile, free) | Basin / coastal |
| **NASA FIRMS** | Satellite wildfire hotspots (VIIRS every 3h, MODIS) | `firms.modaps.eosdis.nasa.gov/api/` (free, needs MAP_KEY) | Point |
| **InciWeb** | Federal wildfire incidents (named) | `inciweb.nwcg.gov` (KML/RSS, free) | Incident polygon |
| **NIFC** | National wildfire situation report | `nifc.gov` + ArcGIS services | Incident / state |
| **FL Forest Service** | State wildfire activity, burn bans | ArcGIS services | County / incident |
| **USGS water services** | Streamflow / stage, flood status | `waterservices.usgs.gov` (free, no key) | Gauge point |
| **AHPS / NWS river forecasts** | River forecast above flood stages | `water.weather.gov` | Gauge / reach |
| **FEMA disaster declarations** | Federal declarations (DR, EM, FM) | `fema.gov/api/open/v2/DisasterDeclarationsSummaries` (free) | County |
| **FEMA IHP** | Individual assistance counts | `fema.gov/api/open/v1/IndividualAssistance...` (free) | County |
| **PowerOutage.us** | Outages by county | `poweroutage.us/api/` (paid tier, or scrape free page) | County/utility |
| **AirNow** | AQI by station & zone | `airnowapi.org` (free, needs key) | Station / polygon |
| **NOAA HAB / Red Tide (FWC)** | FL coastal bloom reports | `fwc.myfwc.com` / open data | Sampling site |
| **Vaisala / NOAA GLM lightning** | Lightning strike density | Commercial or GLM satellite feed | Grid |
| **NOAA/NWS forecast** | 7-day forecast per point | `api.weather.gov/points/{lat,lon}` (free) | Point/zone |
| **FL DEM** | State emergency declarations | `floridadisaster.org` | State/county |
| **EarthquakeHazards USGS** | Earthquakes (unlikely FL but included) | `earthquake.usgs.gov/fdsnws/event/1/` | Point |

## Recent activity (rolling windows: 7/30/90 days)

| Source | What it gives |
|---|---|
| **Red Cross 1-800 calls layer** | DAT dispatches, fire counts, assistance stats |
| **Home Fire Campaign** | Smoke alarm installations by date/location |
| **RC View shelter history** | Prior shelter openings & durations |
| **Blood drives** | Drives held, units collected, hospitals supplied |
| **RC View volunteer deployments** | Out-of-region deployments originating from chapter |
| **FEMA DR history** | Declarations in last N days |
| **Significant weather events log** | NCEI storm events database (cumulative) |

## Context layers (static / slowly-changing)

| Source | What it gives |
|---|---|
| **ACS 2023** (Dragon has `ACS-2023-DATA-TASK`) | Population, age, households, income |
| **ALICE** (Dragon has `alice_master_database`) | Financial hardship index by county/tract |
| **HIFLD** | Hospitals, schools, fire/EMS stations, shelters |
| **Wildfire Risk to Communities** (USFS) | Structural wildfire risk score |
| **FEMA flood hazard layers** | Flood zones |
| **Hurricane evacuation zones (FL)** | Evac zones A-F |
| **CDC SVI** | Social Vulnerability Index by census tract |
| **NRI (FEMA National Risk Index)** | Combined risk score per hazard per county |
| **County & chapter boundaries** | Red Cross chapter polygons + FL county shapefile |
| **Media markets (DMA)** | Nielsen DMA polygons for coverage context |

## Red Cross organizational / programmatic

| Source | What it gives |
|---|---|
| **Chapter leadership** | ED, board members, territory |
| **FOCUS (Salesforce)** | Full donor CRM |
| **Volunteer roster** | Active volunteers by chapter/county |
| **Campaign calendar** | Active appeals, events |
| **Partnership Pulse** (Dragon's tool) | Corporate partnerships in area |
| **DCSOps** | Case management for disaster response |
| **Biomedical** | Blood supply status by region |

## Enrichment / narrative

| Source | What it gives |
|---|---|
| **News APIs (GDELT / NewsAPI / Bing)** | Local coverage of named incidents |
| **Census geocoder** | Address → county/tract (free) |
| **Mapbox isochrones** | Drive-time proximity |
| **Wikipedia** | Historical context for named events |

## Dragon's existing projects as data sources

| Project | Feeds in |
|---|---|
| `alice_master_database` | ALICE overlay |
| `alice-red-cross-data` | Red Cross × ALICE joined |
| `county-consolidation-tool` | County-level rollups |
| `redcross-fire-alarms-dashboard` | Home Fire Campaign installs |
| `red-cross-call-center` | 1-800 call analytics |
| `redcross-disaster-maps` | Disaster map patterns |
| `redcross-donor-map` / `redcross-donor-dashboard` | Existing donor viz |
| `partnership-pulse` | Corporate partnerships |
| `cap-data` | CAP / aerial data |
| `secar-weather-update` | Weather layer |
| `datagov-radar` | Federal data monitoring |
| `kg-explainer` / kg.jbf.com | Knowledge graph integration |

---

## Free-first build order

For Phase 1 the following are free, no-auth-required, and cover 80% of the situational awareness value:

1. **NWS alerts** — no key
2. **FEMA declarations** — no key
3. **USGS water services** — no key
4. **NOAA forecast** — no key
5. **NHC** — static KMZ, no key
6. **InciWeb** — RSS, no key
7. **Census geocoder** — no key

Needs key (still free):
- **NASA FIRMS** — MAP_KEY (register)
- **AirNow** — API key (register)

Paid / client-side only:
- **Red Cross internal layers** — inside AGOL Notebook as Dragon
- **PowerOutage.us** — paid for API, free scrape of site
- **Mapbox** — already on Dragon's stack
