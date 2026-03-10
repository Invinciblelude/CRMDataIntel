# CRM Data Intelligence — Operations Plan

*Your complete business structure: what to do, when, and how*

---

## BUSINESS OVERVIEW

| Item | Detail |
|---|---|
| **Business Name** | CRM Data Intelligence (CRMDataIntel) |
| **Service** | CRM data audit, cleansing, enrichment, scoring, and ongoing maintenance |
| **Target Market** | B2B and industrial companies using Salesforce or other CRMs |
| **Delivery Model** | You + AI tools (Cursor, enrichment APIs) |
| **Revenue Streams** | One-time pilots ($3,500-$15,000) + monthly retainers ($1,500-$3,000) |
| **Website** | `site/index.html` (deploy to Vercel, Netlify, or any host) |
| **Tools** | Cursor AI, Python scripts, Apollo/Hunter/Cleanlist APIs |

---

## YOUR ROLE: WHAT YOU ACTUALLY DO

You wear 3 hats. Here's what each one means in practice:

### Hat 1: SALES (40% of time — weeks 1-4, then 20% ongoing)
**Goal:** Fill your pipeline with prospects and close pilot deals.

| Duty | How Often | Time |
|---|---|---|
| Drive industrial areas, note companies | 2x/week | 2 hrs each |
| Look up companies (website, LinkedIn, size, CRM) | Daily | 1 hr |
| Send cold emails using pitch template | Daily | 30 min |
| LinkedIn outreach (connect + message) | Daily | 30 min |
| Discovery calls with interested prospects | As booked | 30 min each |
| Run free assessments (3 hrs each) | 2-3/week | 6-9 hrs |
| Present assessment results and pitch pilot | As earned | 1 hr each |
| Send intake form, close deal, collect payment | As needed | 1 hr each |

### Hat 2: DELIVERY (40% of time during active pilots)
**Goal:** Execute the pilot and deliver results the client can see and feel.

| Duty | How Often | Time |
|---|---|---|
| Receive client data export (CSV or API) | Once per pilot | 30 min |
| Run audit script, review results | Once per pilot | 2 hrs |
| Customize cleaning rules for this client | Once per pilot | 3-6 hrs |
| Run cleanse + dedupe scripts | Once per pilot | 1-2 hrs |
| Set up enrichment workflow, run enrichment | Once per pilot | 2-4 hrs |
| Build/customize scoring model for their ICP | Once per pilot | 2-4 hrs |
| Build health report (before/after) | Once per pilot | 2-3 hrs |
| Write SOP document for client team | Once per pilot | 2 hrs |
| Present results to client | Once per pilot | 1-2 hrs |
| Handle revisions and QA | Throughout pilot | 3-4 hrs |

### Hat 3: OPERATIONS (20% of time)
**Goal:** Keep the business running, improve tools, handle admin.

| Duty | How Often | Time |
|---|---|---|
| Improve Python scripts based on client feedback | After each pilot | 2-3 hrs |
| Update website with new case studies | After each pilot | 1 hr |
| Invoice clients, track payments | Monthly | 1 hr |
| Update pitch materials if needed | Monthly | 1 hr |
| Learn new tools/techniques | Weekly | 2 hrs |
| Track KPIs (see below) | Weekly | 30 min |

---

## WEEKLY SCHEDULE (First 4 Weeks — Getting Started)

### WEEK 1: PROSPECTING
| Day | Morning (4 hrs) | Afternoon (4 hrs) |
|---|---|---|
| **Mon** | Drive industrial area #1, collect 15 company names | Look them up: website, LinkedIn, size, CRM |
| **Tue** | Drive industrial area #2, collect 15 company names | Look them up, sort into Tier A/B/C |
| **Wed** | Send cold emails to all 30 companies | LinkedIn outreach to decision-makers |
| **Thu** | Follow up on any responses, book calls | Run 1-2 free assessments on any sample data |
| **Fri** | Discovery calls | Refine scripts, update prospect list |

### WEEK 2: FIRST ASSESSMENTS
| Day | Morning (4 hrs) | Afternoon (4 hrs) |
|---|---|---|
| **Mon** | Run free assessments (audit scripts) | Build 1-page health reports for prospects |
| **Tue** | Present assessment results to 2-3 prospects | Follow up on Week 1 emails |
| **Wed** | Send second batch of cold emails (20 new companies) | LinkedIn outreach |
| **Thu** | Discovery calls, pitch pilots | Send intake forms to interested companies |
| **Fri** | Close first pilot deal | Begin data collection from first client |

### WEEK 3: FIRST PILOT + CONTINUED PROSPECTING
| Day | Morning (4 hrs) | Afternoon (4 hrs) |
|---|---|---|
| **Mon** | Client pilot: audit + profiling | Prospecting: new emails + follow-ups |
| **Tue** | Client pilot: build cleaning rules | Prospecting: LinkedIn + calls |
| **Wed** | Client pilot: run cleanse + dedupe | Run 1-2 more free assessments |
| **Thu** | Client pilot: enrichment setup + run | Present assessments, pitch pilots |
| **Fri** | Client pilot: scoring + health report | Admin: invoicing, KPI tracking |

### WEEK 4: DELIVER + CLOSE MORE
| Day | Morning (4 hrs) | Afternoon (4 hrs) |
|---|---|---|
| **Mon** | Client pilot: write SOP + finalize report | Prospecting |
| **Tue** | Present pilot results to client | Pitch retainer to client |
| **Wed** | Close second pilot deal | Start second client audit |
| **Thu** | Second client pilot work | Follow-up outreach |
| **Fri** | Update website with case study | Review KPIs, plan next month |

---

## ONGOING WEEKLY SCHEDULE (Month 2+, with active retainers)

| Day | Morning (4 hrs) | Afternoon (4 hrs) |
|---|---|---|
| **Mon** | Retainer work: weekly quality checks, dashboards | New pilot work (if active) |
| **Tue** | New pilot work | Prospecting: emails, LinkedIn, calls |
| **Wed** | New pilot work | Free assessments for new prospects |
| **Thu** | Retainer work: monthly reports, enrichment | Present results, pitch meetings |
| **Fri** | Admin, invoicing, script improvements | Learning, tool optimization |

---

## STANDARD OPERATING PROCEDURES (SOPs)

### SOP 1: FREE ASSESSMENT (3 hours)
1. Receive prospect info (company name, CRM type, rough record count)
2. Get a CSV sample (500-1000 records) from them
3. Run `python3 scripts/audit_crm.py [their_file.csv]`
4. Review output, note top 3-5 issues
5. Create 1-page summary: health score, critical gaps, recommendation
6. Present in 15-min call or send as PDF
7. If they're interested → send intake form → pitch pilot

### SOP 2: PILOT — AUDIT PHASE (5-7 hours)
1. Receive signed intake form + full data export
2. Save raw data with timestamp (never modify originals)
3. Run full audit: `python3 scripts/audit_crm.py [their_file.csv]`
4. Document findings in `reports/audit_report.json`
5. Present initial audit to client for feedback
6. Agree on cleaning rules, enrichment scope, and scoring criteria

### SOP 3: PILOT — CLEANSE + ENRICH (10-20 hours)
1. Customize `cleanse_crm.py` for client's specific fields and rules
2. Run cleanse: `python3 scripts/cleanse_crm.py [their_file.csv]`
3. Review merge log, verify no good data was lost
4. Set up enrichment API calls (Apollo/Hunter/Cleanlist)
5. Run enrichment on records with missing key fields
6. Merge enrichment results into cleaned dataset
7. Run QA: spot-check 50 random records manually

### SOP 4: PILOT — SCORE + DELIVER (8-12 hours)
1. Customize `score_leads.py` for client's ICP (industries, titles, sizes)
2. Run scoring: `python3 scripts/score_leads.py [cleaned_file.csv]`
3. Generate health report (before/after)
4. Write SOP document for their team (data entry rules, maintenance schedule)
5. Package deliverables: cleaned CSV, scored CSV, health report, SOP, merge log
6. Present to client in 30-60 min meeting
7. Pitch the retainer: "This is what the data looks like today. In 90 days it'll start decaying again unless we maintain it."

### SOP 5: RETAINER — MONTHLY CYCLE
| Week | Task |
|---|---|
| Week 1 | Run quality check, flag new duplicates and missing fields |
| Week 2 | Dedupe new records, normalize new entries |
| Week 3 | Enrich new leads entered since last month |
| Week 4 | Update dashboard, refresh scores, send monthly report to client |

---

## KEY PERFORMANCE INDICATORS (KPIs)

Track these weekly in a simple spreadsheet:

### Sales KPIs
| Metric | Target (Month 1) | Target (Month 3) | Target (Month 6) |
|---|---|---|---|
| Companies contacted | 30/week | 20/week | 10/week |
| Free assessments delivered | 3/week | 2/week | 1/week |
| Pilot proposals sent | 2/month | 3/month | 2/month |
| Pilots closed | 1/month | 2/month | 1-2/month |
| Retainers active | 0 | 1-2 | 3-4 |

### Delivery KPIs
| Metric | Target |
|---|---|
| Pilot delivered on time (4 weeks) | 100% |
| Health score improvement | +10 points minimum |
| Duplicates removed | 50%+ reduction |
| Client satisfaction (would refer) | Yes on every pilot |
| Pilot → retainer conversion | 50%+ |

### Financial KPIs
| Metric | Month 1 | Month 3 | Month 6 | Month 12 |
|---|---|---|---|---|
| Revenue | $3,500 | $11,000 | $13,500 | $24,000 |
| Costs | $600 | $2,500 | $2,800 | $6,550 |
| Net profit | $2,900 | $8,500 | $10,700 | $17,450 |
| Active retainers | 0 | 1-2 | 3 | 4+ |
| Recurring monthly revenue | $0 | $1,500-$3,000 | $4,500-$6,000 | $9,000-$12,000 |

---

## FILE STRUCTURE — YOUR ENTIRE BUSINESS

```
crm-data-services/
├── site/                          ← YOUR WEBSITE
│   ├── index.html                 ← Main landing page (deploy this)
│   └── css/style.css              ← Stylesheet
│
├── pitch/                         ← SALES MATERIALS
│   ├── services-sheet.html        ← 1-page PDF (print from browser)
│   ├── intake-form.html           ← Send to clients before starting
│   ├── pitch-script.md            ← Word-for-word scripts + objections
│   ├── target-companies.md        ← 8 company types + what to say to each
│   └── market-research.md         ← Market data, competitors, stats
│
├── scripts/                       ← YOUR DELIVERY TOOLS
│   ├── generate_sample_data.py    ← Create demo dataset
│   ├── audit_crm.py               ← SOP 1: Audit any CRM CSV
│   ├── cleanse_crm.py             ← SOP 2-3: Clean, dedupe, normalize
│   ├── score_leads.py             ← SOP 4: Lead scoring
│   └── profitability_calc.py      ← Model your costs and revenue
│
├── data/                          ← DATA FILES
│   ├── sample_crm_export.csv      ← Demo: messy data (689 records)
│   ├── crm_cleaned.csv            ← Demo: cleaned data (598 records)
│   └── crm_scored.csv             ← Demo: scored data with priorities
│
├── reports/                       ← DELIVERABLES
│   ├── data-health-report.html    ← Before/after report (show clients)
│   ├── audit_report.json          ← Full audit data
│   ├── merge_log.json             ← Duplicate merge documentation
│   ├── scoring_summary.json       ← Score distribution + top leads
│   └── profitability_model.json   ← Your financial model
│
└── OPERATIONS-PLAN.md             ← THIS FILE — your business playbook
```

---

## CHECKLIST: WHAT'S DONE vs WHAT'S LEFT

### DONE
- [x] Website (landing page with services, process, industries, results, pricing, contact form)
- [x] Services sheet (1-page PDF, printable)
- [x] Intake form (send to clients)
- [x] Pitch script (30-sec, 90-sec, objections, emails)
- [x] Target company guide (8 types, what to say to each)
- [x] Market research (stats, competitors, pricing)
- [x] Audit tool (Python, works on any CSV)
- [x] Cleanse/dedupe tool (Python)
- [x] Lead scoring tool (Python)
- [x] Profitability calculator (Python)
- [x] Sample demo data (689 messy records)
- [x] Sample cleaned data (598 records)
- [x] Sample scored data (with priorities)
- [x] Before/after health report (show prospects)
- [x] Operations plan with SOPs, schedule, KPIs

### TO DO (your next actions)
- [ ] Replace [Your Name], [your@email.com], [your phone] in services-sheet.html
- [ ] Replace placeholder text in site/index.html footer with your info
- [ ] Deploy website (Vercel, Netlify, or any static host)
- [ ] Buy a domain (e.g., crmdataintel.com)
- [ ] Set up a business email (you@crmdataintel.com)
- [ ] Sign up for Apollo.io free tier (enrichment API)
- [ ] Sign up for Hunter.io starter ($49/mo when needed)
- [ ] Create a LinkedIn profile for the business
- [ ] Drive industrial areas and build first prospect list of 30 companies
- [ ] Send first batch of cold emails
- [ ] Book first discovery call
- [ ] Run first free assessment
- [ ] Close first pilot

---

## 90-DAY MILESTONE TARGETS

| Day | Milestone |
|---|---|
| **Day 1-3** | Fill in your info on all materials. Deploy website. Set up email. |
| **Day 4-7** | Drive industrial areas. Build list of 30 target companies. |
| **Day 7-14** | Contact all 30. Book 3-5 discovery calls. Run 2-3 free assessments. |
| **Day 14-21** | Present assessments. Send 2-3 pilot proposals. |
| **Day 21-30** | Close first pilot ($3,500-$7,500). Begin delivery. |
| **Day 30-45** | Deliver first pilot. Pitch retainer. Contact 20 more companies. |
| **Day 45-60** | Close second pilot. Start first retainer. |
| **Day 60-90** | 2 pilots delivered, 1-2 retainers running, $8K-$15K earned. |
