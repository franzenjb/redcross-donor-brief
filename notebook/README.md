# AGOL Notebook

## How to run `donor_brief_agol.ipynb`

1. Log into https://arc-nhq-gis.maps.arcgis.com
2. Click **Content → New item → Notebook**, or **Notebook** from the top nav
3. Create a new Python 3 notebook
4. **File → Import** and upload `donor_brief_agol.ipynb` from this repo — OR copy each cell's contents manually
5. Click **Run all cells**

## What you'll see

Cell 1: confirms you're authenticated (`GIS('home')` picks up your SSO session).

Cell 2: resolves the 3 items and prints title/type/owner/access.

Cell 3: for each item that's a Feature Service, introspects layer count, field list, row count, and prints first 3 sample rows.

## Next step

**Paste the schema output from Cell 3 back to me in chat.** Once I see the real field names (e.g. "donor_name" vs "full_name" vs "display_name", "giving_total_2yr" vs "cumulative_giving", etc.), I'll write the follow-on cells that:

- Geocode donors (if needed)
- Resolve each donor to their FL county
- Spatially join to smoke-alarm installs and DAT/call incidents
- Apply 30-day fatigue filter
- Generate briefings by hitting `https://redcross-donor-brief.vercel.app/api/brief?county=...` (or replicate inline so no public endpoint is needed)
- Write a "Pending Donor Briefings" hosted table you can review in Experience Builder

## Why a Notebook, not a script?

- **SAML SSO** — Red Cross AGOL can't be accessed from outside the org via username/password.
- **PII stays inside Red Cross** — donor data never crosses an API boundary we can see.
- **Auto-auth** — `GIS('home')` just works when the notebook runs inside the org.
- **Scheduled runs** — once built, AGOL Notebook Server can run this nightly.
