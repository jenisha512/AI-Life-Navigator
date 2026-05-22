# MedRoute AI

MedRoute AI is a Flask-based emergency hospital allocation prototype. It recommends a hospital shortlist based on city, emergency type, severity, ICU availability, care level, and current ICU load, then explains the recommendation through an integrated assistant.

## What the project includes

- A guided triage homepage for city, emergency, and severity intake
- A ranking engine that scores hospitals by readiness and operational fit
- A results dashboard with score breakdowns, map view, charting, and shortlist comparison
- A context-aware assistant that explains recommendation strength and next steps
- Dataset generation and enrichment scripts for raw and synthetic hospital data

## Tech stack

- Python 3.10+
- Flask
- Pandas
- RapidFuzz
- Vanilla HTML, CSS, and JavaScript
- Leaflet and Chart.js on the frontend

## Project structure

```text
app.py                          Flask routes and page rendering
config.py                       Project-relative configuration and dataset paths
services/
  allocation_engine.py          Hospital scoring and ranking logic
  chatbot_service.py            Explainability assistant replies
  location_service.py           Location and map URL helpers
utils/
  data_loader.py                Dataset loading and validation
templates/
  index.html                    Homepage and triage form
  result.html                   Recommendation dashboard
static/
  css/style.css                 Shared design system and page styles
  js/home.js                    Homepage interactions
  js/result.js                  Results page interactions
  js/chat.js                    Assistant interactions
  brand-mark.svg                Product symbol
  favicon.svg                   Browser tab icon
scripts/
  osm_hospital_scraper.py       Fetch raw hospital data from Overpass
  enrich_hospital_data.py       Add operational fields to raw data
generate_hospital_dataset.py    Generate a synthetic demo dataset
tests/
  test_app.py                   Smoke tests for app routes and chat
```

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Optional: add an `.env` file in the project root if you want environment-based settings.
   You can copy `.env.example` and fill in your own values.
4. Start the app from any working directory:

```bash
python -m flask --app app run --host 127.0.0.1 --port 5001
```

Then open [http://127.0.0.1:5001](http://127.0.0.1:5001).

## Data files

The app reads the primary dataset from:

```text
data/india_hospital_dataset.csv
```

The raw scraped hospital file is stored at:

```text
data/real_india_hospitals_raw.csv
```

Both paths are resolved relative to the project directory, so the app and scripts no longer depend on the current shell location.

## Utility scripts

Generate a synthetic hospital dataset:

```bash
python generate_hospital_dataset.py
```

Scrape raw hospital locations:

```bash
python scripts/osm_hospital_scraper.py
```

Enrich the raw hospital dataset with operational fields:

```bash
python scripts/enrich_hospital_data.py
```

## Tests

Run the smoke tests with:

```bash
python -m unittest tests.test_app
```

These checks cover:

- Homepage loading
- State and city lookup endpoints
- Valid and invalid allocation flows
- Assistant replies

## Clean handoff notes

- Keep secrets in `.env`, not in committed files
- Ignore generated caches, logs, and packaging artifacts with `.gitignore`
- Use the `data/` folder as the single source of truth for datasets

## Notes

- The recommendation engine is decision support, not clinical advice.
- The frontend is optimized for demo and academic evaluation workflows.
- Recommendation scoring is intentionally explainable so reviewers can see why a hospital ranked first.
