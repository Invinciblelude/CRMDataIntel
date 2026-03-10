#!/usr/bin/env python3
"""
Prospect Tracker — Your Sales Pipeline Database

This is YOUR CRM for tracking businesses you want to sell to.
Run this to add prospects, log outreach, and track your pipeline.

Usage:
  python3 prospect_tracker.py                    # Show dashboard
  python3 prospect_tracker.py add                # Add a new prospect
  python3 prospect_tracker.py list               # List all prospects
  python3 prospect_tracker.py outreach <id>      # Log outreach to a prospect
  python3 prospect_tracker.py status <id> <new>  # Change status
  python3 prospect_tracker.py import <csv>       # Import prospects from CSV
  python3 prospect_tracker.py export             # Export all to CSV
"""

import csv
import json
import os
import sys
from datetime import datetime

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
DB_PATH = os.path.join(DB_DIR, "prospects.json")

STATUSES = ["new", "researched", "contacted", "call_booked", "assessment_sent",
            "pilot_proposed", "pilot_active", "retainer", "lost", "not_fit"]

INDUSTRIES = ["dental", "medical", "manufacturing", "distribution", "staffing",
              "construction", "logistics", "hvac_plumbing_electrical",
              "energy", "real_estate", "other"]


def load_db():
    os.makedirs(DB_DIR, exist_ok=True)
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r") as f:
            return json.load(f)
    return {"prospects": [], "next_id": 1}


def save_db(db):
    with open(DB_PATH, "w") as f:
        json.dump(db, f, indent=2)


def add_prospect(db):
    print("\n--- ADD NEW PROSPECT ---")
    p = {}
    p["id"] = db["next_id"]
    db["next_id"] += 1

    p["company"] = input("Company name: ").strip()
    p["industry"] = input(f"Industry ({', '.join(INDUSTRIES)}): ").strip().lower() or "other"
    p["website"] = input("Website: ").strip()
    p["address"] = input("Address: ").strip()
    p["contact_name"] = input("Contact person name: ").strip()
    p["contact_title"] = input("Contact title: ").strip()
    p["phone"] = input("Phone: ").strip()
    p["email"] = input("Email: ").strip()
    p["employees"] = input("Approx employees: ").strip()
    p["crm_used"] = input("CRM they use (salesforce/hubspot/dentrix/other/unknown): ").strip()
    p["notes"] = input("Notes: ").strip()
    p["source"] = input("How you found them (drive-by/google-maps/linkedin/referral/other): ").strip()
    p["status"] = "new"
    p["created"] = datetime.now().strftime("%Y-%m-%d")
    p["outreach_log"] = []

    db["prospects"].append(p)
    save_db(db)
    print(f"\n  Added: #{p['id']} — {p['company']} ({p['industry']})")
    return db


def log_outreach(db, prospect_id):
    prospect = None
    for p in db["prospects"]:
        if p["id"] == prospect_id:
            prospect = p
            break

    if not prospect:
        print(f"Prospect #{prospect_id} not found.")
        return db

    print(f"\n--- LOG OUTREACH: #{prospect['id']} — {prospect['company']} ---")
    entry = {}
    entry["date"] = datetime.now().strftime("%Y-%m-%d %H:%M")
    entry["type"] = input("Type (email/call/walkin/linkedin/text/meeting): ").strip()
    entry["notes"] = input("What happened: ").strip()
    entry["next_step"] = input("Next step: ").strip()

    prospect["outreach_log"].append(entry)

    new_status = input(f"Update status? Current: {prospect['status']} (enter to keep, or new status): ").strip()
    if new_status and new_status in STATUSES:
        prospect["status"] = new_status

    save_db(db)
    print(f"  Logged outreach for {prospect['company']}")
    return db


def change_status(db, prospect_id, new_status):
    for p in db["prospects"]:
        if p["id"] == prospect_id:
            old = p["status"]
            p["status"] = new_status
            save_db(db)
            print(f"  #{p['id']} {p['company']}: {old} → {new_status}")
            return db
    print(f"Prospect #{prospect_id} not found.")
    return db


def list_prospects(db, filter_status=None):
    prospects = db["prospects"]
    if filter_status:
        prospects = [p for p in prospects if p["status"] == filter_status]

    if not prospects:
        print("\n  No prospects found.")
        return

    print(f"\n{'ID':>4}  {'Status':<16} {'Company':<30} {'Industry':<15} {'Contact':<20} {'Phone':<16} {'Outreach':<5}")
    print("-" * 110)
    for p in sorted(prospects, key=lambda x: STATUSES.index(x["status"]) if x["status"] in STATUSES else 99):
        outreach_count = len(p.get("outreach_log", []))
        print(f"{p['id']:>4}  {p['status']:<16} {p['company'][:29]:<30} {p.get('industry','')[:14]:<15} "
              f"{p.get('contact_name','')[:19]:<20} {p.get('phone','')[:15]:<16} {outreach_count:<5}")

    print(f"\n  Total: {len(prospects)} prospects")


def dashboard(db):
    prospects = db["prospects"]
    total = len(prospects)

    if total == 0:
        print("\n" + "=" * 60)
        print("  YOUR PROSPECT PIPELINE — EMPTY")
        print("=" * 60)
        print("\n  No prospects yet. Start adding with:")
        print("    python3 prospect_tracker.py add")
        print("\n  Or import from CSV:")
        print("    python3 prospect_tracker.py import prospects.csv")
        print()
        return

    status_counts = {}
    for s in STATUSES:
        count = sum(1 for p in prospects if p["status"] == s)
        if count > 0:
            status_counts[s] = count

    industry_counts = {}
    for p in prospects:
        ind = p.get("industry", "other")
        industry_counts[ind] = industry_counts.get(ind, 0) + 1

    total_outreach = sum(len(p.get("outreach_log", [])) for p in prospects)
    contacted = sum(1 for p in prospects if p["status"] not in ["new", "researched", "not_fit"])
    active_deals = sum(1 for p in prospects if p["status"] in ["pilot_proposed", "pilot_active", "retainer"])

    pipeline_value = 0
    for p in prospects:
        if p["status"] == "pilot_proposed":
            pipeline_value += 5000
        elif p["status"] == "pilot_active":
            pipeline_value += 5000
        elif p["status"] == "retainer":
            pipeline_value += 2000

    print("\n" + "=" * 60)
    print("  YOUR PROSPECT PIPELINE")
    print(f"  {datetime.now().strftime('%B %d, %Y')}")
    print("=" * 60)

    print(f"\n  PIPELINE SUMMARY")
    print(f"  {'Total prospects:':<30} {total}")
    print(f"  {'Contacted:':<30} {contacted}")
    print(f"  {'Active deals:':<30} {active_deals}")
    print(f"  {'Total outreach logged:':<30} {total_outreach}")
    print(f"  {'Est. pipeline value:':<30} ${pipeline_value:,}")

    print(f"\n  STATUS BREAKDOWN")
    for s, c in status_counts.items():
        bar = "#" * (c * 2)
        label = s.replace("_", " ").title()
        print(f"    {label:<20} {bar} {c}")

    print(f"\n  BY INDUSTRY")
    for ind, c in sorted(industry_counts.items(), key=lambda x: -x[1]):
        label = ind.replace("_", " ").title()
        print(f"    {label:<25} {c}")

    needs_followup = [p for p in prospects if p["status"] in ["contacted", "assessment_sent", "pilot_proposed"]]
    if needs_followup:
        print(f"\n  NEEDS FOLLOW-UP ({len(needs_followup)})")
        for p in needs_followup:
            last = p["outreach_log"][-1] if p.get("outreach_log") else None
            last_date = last["date"][:10] if last else "never"
            print(f"    #{p['id']} {p['company'][:25]:<25} Status: {p['status']:<18} Last: {last_date}")

    print("\n" + "=" * 60)


def import_csv(db, csv_path):
    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        return db

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            p = {
                "id": db["next_id"],
                "company": row.get("company", row.get("name", "")).strip(),
                "industry": row.get("industry", row.get("category", "other")).strip().lower(),
                "website": row.get("website", row.get("url", "")).strip(),
                "address": row.get("address", "").strip(),
                "contact_name": row.get("contact_name", row.get("contact", "")).strip(),
                "contact_title": row.get("contact_title", row.get("title", "")).strip(),
                "phone": row.get("phone", row.get("telephone", "")).strip(),
                "email": row.get("email", "").strip(),
                "employees": row.get("employees", "").strip(),
                "crm_used": row.get("crm_used", row.get("crm", "unknown")).strip(),
                "notes": row.get("notes", "").strip(),
                "source": row.get("source", "csv_import").strip(),
                "status": "new",
                "created": datetime.now().strftime("%Y-%m-%d"),
                "outreach_log": [],
            }
            if p["company"]:
                db["prospects"].append(p)
                db["next_id"] += 1
                count += 1

    save_db(db)
    print(f"\n  Imported {count} prospects from {csv_path}")
    return db


def export_csv(db):
    output_path = os.path.join(DB_DIR, "prospects_export.csv")
    if not db["prospects"]:
        print("No prospects to export.")
        return

    fields = ["id", "company", "industry", "website", "address", "contact_name",
              "contact_title", "phone", "email", "employees", "crm_used",
              "notes", "source", "status", "created"]

    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(db["prospects"])

    print(f"\n  Exported {len(db['prospects'])} prospects to {output_path}")


def main():
    db = load_db()
    args = sys.argv[1:]

    if not args:
        dashboard(db)
    elif args[0] == "add":
        add_prospect(db)
    elif args[0] == "list":
        filter_status = args[1] if len(args) > 1 else None
        list_prospects(db, filter_status)
    elif args[0] == "outreach" and len(args) > 1:
        log_outreach(db, int(args[1]))
    elif args[0] == "status" and len(args) > 2:
        change_status(db, int(args[1]), args[2])
    elif args[0] == "import" and len(args) > 1:
        import_csv(db, args[1])
    elif args[0] == "export":
        export_csv(db)
    elif args[0] == "dashboard":
        dashboard(db)
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
