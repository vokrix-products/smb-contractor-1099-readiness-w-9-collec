# SMB Contractor 1099 Readiness & W-9 Collection Status Tracker

**Archetype:** Extraction (polling file watcher, no HTTP server)

## Purpose

This backend polls a CSV directory, determines each contractor's W-9 collection status, computes 1099 threshold compliance, and outputs a dashboard JSON file for a frontend to serve.

## Input / Output

- **Input CSV directory:** `/data/input/` (files with `.csv` extension)
- **Output JSON dashboard:** `/data/output/dashboard.json`

## Status Strings

Each contractor record receives one of these exact status strings:

- `missing_w9:critical` – W-9 not collected, payment >= $2000
- `w9_collected:good` – W-9 collected, payment < $2000
- `above_threshold:critical` – W-9 collected, payment >= $2000
- `within_threshold:good` – W-9 not collected, payment < $2000

## How to Run Demo

```bash
pip install -r requirements.txt --quiet
python run_demo.py
```

Output: `Dashboard ready on http://localhost:8000` and a JSON file at `data/output/dashboard.json`.

## Poller (Production)

```bash
python poller.py
```

Watches `/data/input/` for new CSV files every 60 seconds and updates the dashboard JSON.

## Files

- `constants.py` – project-wide constants
- `w9_extractor.py` – PDF W-9 extraction via DeepSeek API
- `contractor_processor.py` – CSV processing and status logic
- `poller.py` – continuous file watcher
- `run_demo.py` – demonstration script (mock mode, no API calls)
- `run_tests.py` – unit tests
- `requirements.txt` – dependencies (requests, pytest)
