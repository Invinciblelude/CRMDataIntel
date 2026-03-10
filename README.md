# CRM Data Intelligence

End-to-end CRM data audit, cleansing, enrichment, and lead scoring toolkit for industrial and B2B companies.

## What This Does

Turns messy customer databases into clean, scored, revenue-ready data.

| Stage | Script | Output |
|-------|--------|--------|
| **Generate sample data** | `scripts/generate_sample_data.py` | `data/sample_crm_export.csv` |
| **Audit** | `scripts/audit_crm.py` | `reports/audit_report.json` |
| **Clean & Deduplicate** | `scripts/cleanse_crm.py` | `data/crm_cleaned.csv` + `reports/merge_log.json` |
| **Score & Prioritize** | `scripts/score_leads.py` | `data/crm_scored.csv` + `reports/scoring_summary.json` |
| **Profitability Model** | `scripts/profitability_calc.py` | `reports/profitability_model.json` |
| **Prospect Tracker** | `scripts/prospect_tracker.py` | `data/prospects.json` |

## Quick Start

```bash
# 1. Generate sample messy CRM data
python3 scripts/generate_sample_data.py

# 2. Audit it
python3 scripts/audit_crm.py --csv data/sample_crm_export.csv

# 3. Clean it
python3 scripts/cleanse_crm.py --csv data/sample_crm_export.csv

# 4. Score it
python3 scripts/score_leads.py --csv data/crm_cleaned.csv

# 5. View profitability model
python3 scripts/profitability_calc.py
```

## Website

The `site/` folder contains a complete client-facing website:

- **Landing page** — `site/index.html`
- **Get Started (sales page)** — `site/pages/start.html`
- **Live Demo** — `site/pages/demo.html`
- **Free Audit Tool** — `site/pages/audit-tool.html` (browser-based, no backend)

```bash
cd site && python3 -m http.server 9090
# Open http://localhost:9090
```

## Sales Materials

| File | Purpose |
|------|---------|
| `pitch/services-sheet.html` | One-page printable services sheet |
| `pitch/pitch-script.md` | Call scripts, objection handling, email templates |
| `pitch/market-research.md` | Market intelligence and competitive analysis |
| `pitch/target-companies.md` | Target company profiles by industry |
| `pitch/intake-form.html` | Client intake form |
| `OPERATIONS-PLAN.md` | Full operational plan with SOPs and weekly schedule |

## Prospect Management

```bash
# Import starter prospects
python3 scripts/prospect_tracker.py import data/starter_prospects.csv

# View pipeline dashboard
python3 scripts/prospect_tracker.py

# Add a new prospect
python3 scripts/prospect_tracker.py add "Company Name" "dental" "Contact Name" "email@example.com" "555-0100"

# Log outreach
python3 scripts/prospect_tracker.py outreach 1 "Sent intro email"

# Update status
python3 scripts/prospect_tracker.py status 1 contacted
```

## License

Proprietary. All rights reserved.
