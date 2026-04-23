# Vision — Donor Briefing Tool

## The one-sentence product

Given a donor, return a structured briefing of everything current and recent happening in their **county, chapter, and region** — so the gift officer walks into every conversation informed.

## Why this wins

- Gift officers currently do this badly, manually, for their top 10 donors at best.
- Red Cross has every piece of data needed — it's just never been assembled for fundraising use.
- Costs pennies per briefing. Any retention lift pays back 100x.
- Portable: once built for NCFL, the same tool works for every region with a config swap.

## Usage modes

### 1. Donor-centric (primary)
Pick a donor. Get their county/chapter/region briefing.
```
brief --donor-id 12345
brief --donor-email jane@example.com
```

### 2. Geography-centric
Pick a place. Get the briefing.
```
brief --county "Orange, FL"
brief --chapter "Central Florida"
brief --region "North & Central Florida"
```

### 3. Daily / batch
Every morning, generate briefings for the top N donors the officer is planning to touch today — landed as HTML/PDF/Markdown in their inbox.

### 4. On-demand API
`info.jbf.com/brief?county=Orange,FL` — returns JSON briefing, consumable by other tools (Outlook add-in, Salesforce widget, Teams bot).

## What goes in a briefing

### RIGHT NOW (happening at query time)
- Active NWS watches/warnings touching their county
- Active Red Cross DAT responses (last 24h) in county/chapter
- Open shelters in chapter/region
- Active wildfires (FIRMS hotspots + InciWeb) in chapter/region
- Active flood gauges at or above action stage
- Active FEMA declarations affecting county
- Hurricane cone (if any active Atlantic/Gulf system threatens region)
- Power outages > threshold
- AirNow AQI > "Unhealthy" during fires

### RECENT (last 7 / 30 / 90 days, configurable)
- Home fires in county with Red Cross response
- Families / people / kids assisted in county & chapter
- Assistance dollars distributed
- Smoke alarms installed (Home Fire Campaign)
- Blood drives held, units collected
- Volunteers deployed out-of-area from chapter
- Shelter-days of operation
- Named storms / significant events

### CONTEXT (static-ish)
- Population, median age, %65+, %households with kids (ACS)
- ALICE households %
- Tornado/flood/wildfire/hurricane historical risk
- Number of Red Cross volunteers in county
- Number of smoke alarm partners
- Local media market

### DONOR-SPECIFIC (when donor selected)
- Giving history, last gift, frequency, channel
- Segment: new / recurring / major / lapsed / board / volunteer
- Past touches in last 90 days (don't repeat)
- Response history (opens, clicks, replies, gifts-after-touch)
- Prior incidents they were proximate to
- Board / volunteer / event attendance flags
- ALICE context of their ZIP

### NARRATIVE LAYER (LLM, Phase 2)
The tool emits both structured JSON and a ready-to-read narrative paragraph:

> "Mrs. Henderson lives in Orange County, where last month Red Cross volunteers responded to 7 home fires, helped 23 families (48 people, 14 of them children), and installed 31 smoke alarms across 8 neighborhoods. There's an active severe-thunderstorm watch for her area tonight. Three of her chapter's volunteers deployed to the Los Angeles wildfires last Thursday. Her giving history: monthly donor for 4 years, last gift $50 on April 1, has not been personally contacted in 87 days."

## Architectural options

### Option A — Standalone tool (recommended for speed)
- Python package in `src/`
- CLI for Dragon's local use
- AGOL Notebook for scheduled batch generation into a hosted table
- Optional REST facade hosted on Vercel (no PII layer) for public counts/context

### Option B — Bake into the knowledge graph (kg.jbf.com)
- Ingest all these layers into the KG
- Briefing becomes a traversal query
- Pros: unified entity resolution, relationship queries, extensible
- Cons: heavier lift up front, slower first demo

### Option C — info.jbf.com variant (hybrid)
- Public/safe version at info.jbf.com shows county/chapter/region situational awareness — no donor data
- Authenticated "pro" version at a separate domain adds donor layer
- Pros: showcase-able publicly without PII concerns
- Cons: two surfaces to maintain

**Recommendation:** Start with Option A. Land the CLI + AGOL Notebook in a week. If it sings, absorb into KG as Option B, and carve off the public-safe layer to info.jbf.com as Option C.

## Phase plan (revised)

### Phase 1 — County briefing skeleton (this week)
- Geography hierarchy resolver (donor → county → chapter → region) using FL county + chapter boundaries
- Public sources live: FEMA, NWS, NHC, FIRMS, USGS flood, power outage, AirNow
- CLI: `brief --county "Orange, FL"` returns JSON briefing (no RC internal data yet)

### Phase 2 — Red Cross internal layers
- In an AGOL Notebook, read donor / calls / shelters / Home Fire Campaign layers
- Merge into briefing
- Write briefings for every donor to a hosted table
- Experience Builder read-only view

### Phase 3 — Narrative + donor-specific
- LLM-rendered narrative paragraph
- Donor giving context
- Past-touch / response history

### Phase 4 — Surfaces
- info.jbf.com public variant (no PII)
- Email draft channel (Outlook Graph)
- Dashboard home screen

### Phase 5 — Intelligence
- Propensity scoring
- Anniversary triggers
- Attribution tracking
- KG integration

### Phase 6 — Portability & national rollout
- Config-swap for any region
- Multi-region dashboard for national comms / philanthropy leadership
