# redcross-donor-brief

**Donor situational-awareness briefing tool for Red Cross gift officers.**

Pick a donor (or a county, or a chapter). Get an instant briefing of what's happening — current and recent — in their **county → chapter → region**, drawn from Red Cross internal systems and public disaster/hazard feeds.

The gift officer uses this before a call, before writing a note, before a meeting. They walk in knowing what matters in the donor's world right now.

## The three-ring frame

```
               ┌──────────────────────────────────┐
               │          REGION                   │
               │  (e.g. North & Central Florida)  │
               │  - Active hurricane cone          │
               │  - Regional blood supply status   │
               │  - Volunteer deployments out      │
               │    ┌─────────────────────┐        │
               │    │     CHAPTER          │       │
               │    │  - Active DAT ops   │        │
               │    │  - Shelters open    │        │
               │    │  - Smoke alarm wk   │        │
               │    │   ┌───────────┐     │        │
               │    │   │  COUNTY   │     │        │
               │    │   │ DONOR ●   │     │        │
               │    │   │ - Fires   │     │        │
               │    │   │ - NWS wx  │     │        │
               │    │   │ - FEMA    │     │        │
               │    │   └───────────┘     │        │
               │    └─────────────────────┘        │
               └──────────────────────────────────┘
```

## Data layers (current + recent)

### Red Cross internal (pulled from client's AGOL org via Notebook)
- 1-800 Red Cross calls / DAT dispatches
- Home Fire Campaign smoke-alarm installations
- Shelter openings & occupancy (RC View)
- Volunteer deployments
- Blood drives / collection events / hospital deliveries
- Chapter / region boundaries
- Donor layer (NCFL)

### External hazards — active + recent
- **FEMA** disaster declarations (county-level)
- **NWS** active watches/warnings (tornado, severe thunderstorm, flood, heat, winter)
- **NHC** hurricane cone + surge zones (critical in FL)
- **NASA FIRMS** wildfire satellite hotspots (VIIRS + MODIS)
- **InciWeb** federal wildfire incidents
- **FL Forest Service** state wildfire activity, burn bans
- **USGS / AHPS** river gauges above action/flood stage
- **PowerOutage.us** power outage by county
- **AirNow** air quality (relevant during fires / HAB)
- **Lightning strikes** (Vaisala / NOAA GLM)
- **NOAA HAB / Red Tide** Florida coastal
- **FL DEM** state-level emergency declarations

### Context layers (what the place is like)
- **ACS 2023** demographics by county
- **ALICE** financial-hardship index (Dragon's `alice_master_database`)
- **HIFLD** hospitals, schools, critical infrastructure
- **Wildfire Risk to Communities** structural risk scores
- **FEMA flood zones**
- **Hurricane evacuation zones**

### Historical / anniversary
- Named local disasters on this day (1, 5, 10 years ago)
- Donor first-gift anniversary
- Giving milestones
- Sound the Alarm event anniversaries

### Knowledge graph (kg.jbf.com integration — Phase 2)
- Entity resolution across donors, counties, chapters, programs, incidents, volunteers
- Relationship queries ("what programs in this donor's county has Red Cross run in the last 3 years?")

## Delivery surfaces

- **CLI** — `python -m briefing --donor-id 12345` or `--county "Orange, FL"` (day-1 tool for Dragon)
- **AGOL Notebook** — scheduled, writes briefings to a hosted table viewable in Experience Builder
- **info.jbf.com variant** — potential public-safe surface (no donor PII) showing county/chapter/region situational awareness
- **Email/Outlook drafts** — Phase N, not now

## Repo layout

```
redcross-donor-brief/
├── README.md
├── src/
│   ├── sources/              # one file per external feed
│   │   ├── fema.py
│   │   ├── nws.py
│   │   ├── nhc.py
│   │   ├── firms.py
│   │   ├── inciweb.py
│   │   ├── usgs_flood.py
│   │   ├── power_outage.py
│   │   ├── airnow.py
│   │   ├── nifc.py
│   │   └── agol.py           # Red Cross internal layers
│   ├── geography/
│   │   ├── hierarchy.py      # donor → county → chapter → region
│   │   └── ncfl.py           # NCFL-specific chapter/county mapping
│   ├── briefing/
│   │   ├── county.py
│   │   ├── chapter.py
│   │   ├── region.py
│   │   └── donor.py          # compose all three
│   ├── render/
│   │   ├── narrative.py      # talking points
│   │   └── json_out.py
│   └── cli.py
├── notebook/
│   └── donor_brief.ipynb     # AGOL-side notebook
├── prompts/                  # LLM templates (Phase 2)
├── docs/
│   ├── vision.md
│   └── data-sources-catalog.md
└── config.example.json
```

## Status

Scaffolded 2026-04-23. Building source modules first.
