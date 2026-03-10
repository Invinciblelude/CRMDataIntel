#!/usr/bin/env python3
"""
SOP 6 — Lead Scoring
Takes a cleaned CRM CSV and assigns each record a lead score (0-100)
based on completeness, recency, seniority, and ICP fit.
Outputs a scored CSV sorted by priority.
"""

import csv
import json
import os
import re
import sys
from datetime import datetime, timedelta

SENIORITY_SCORES = {
    "C-Suite": 30,
    "Owner/Founder": 28,
    "VP": 25,
    "Director": 20,
    "Manager": 15,
    "Individual Contributor": 8,
    "Unknown": 5,
}

ICP_INDUSTRIES = {
    "Manufacturing", "Construction", "Energy", "Energy - Oil & Gas",
    "Industrial Equipment", "Industrial Services", "Logistics & Distribution",
    "Automotive", "Aerospace & Defense", "Mining", "Chemical",
    "Utilities", "Water Treatment", "Waste Management",
}


def is_empty(val):
    if val is None:
        return True
    v = str(val).strip().lower()
    return v in ("", "n/a", "unknown", "none", "-", "null")


def completeness_score(record):
    key_fields = ["email", "phone", "direct_dial", "job_title", "company",
                  "industry", "state", "linkedin_url"]
    filled = sum(1 for f in key_fields if not is_empty(record.get(f)))
    return round((filled / len(key_fields)) * 20)


def recency_score(record):
    last_act = record.get("last_activity_date", "")
    if is_empty(last_act):
        return 0
    try:
        dt = datetime.strptime(last_act.strip(), "%Y-%m-%d")
    except ValueError:
        return 0

    days_ago = (datetime.now() - dt).days
    if days_ago <= 30:
        return 20
    if days_ago <= 90:
        return 15
    if days_ago <= 180:
        return 10
    if days_ago <= 365:
        return 5
    return 0


def seniority_score(record):
    level = record.get("seniority_level", "Unknown").strip()
    return SENIORITY_SCORES.get(level, 5)


def icp_score(record):
    industry = (record.get("industry") or "").strip()
    score = 0
    if industry in ICP_INDUSTRIES:
        score += 15
    employees = (record.get("employees") or "").strip()
    if employees in ("50-200", "200-500", "500-1000", "1000+"):
        score += 5
    elif not is_empty(employees):
        try:
            emp_num = int(re.sub(r"\D", "", employees))
            if emp_num >= 50:
                score += 5
        except ValueError:
            pass
    return min(score, 20)


def engagement_score(record):
    score = 0
    lifecycle = (record.get("lifecycle_stage") or "").strip()
    stage_scores = {
        "Customer": 10, "Evangelist": 10, "Opportunity": 8,
        "SQL": 6, "MQL": 4, "Lead": 2,
    }
    score += stage_scores.get(lifecycle, 0)
    return score


def score_records(records):
    for r in records:
        comp = completeness_score(r)
        rec = recency_score(r)
        sen = seniority_score(r)
        icp = icp_score(r)
        eng = engagement_score(r)

        total = min(comp + rec + sen + icp + eng, 100)

        r["score_completeness"] = comp
        r["score_recency"] = rec
        r["score_seniority"] = sen
        r["score_icp_fit"] = icp
        r["score_engagement"] = eng
        r["lead_score"] = total

        if total >= 75:
            r["priority"] = "Hot"
        elif total >= 55:
            r["priority"] = "Warm"
        elif total >= 35:
            r["priority"] = "Cool"
        else:
            r["priority"] = "Cold"

    records.sort(key=lambda x: x["lead_score"], reverse=True)
    return records


def run_scoring(csv_path):
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)
        fieldnames = list(reader.fieldnames)

    records = score_records(records)

    score_fields = ["score_completeness", "score_recency", "score_seniority",
                    "score_icp_fit", "score_engagement", "lead_score", "priority"]
    for sf in score_fields:
        if sf not in fieldnames:
            fieldnames.append(sf)

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    scored_path = os.path.join(output_dir, "crm_scored.csv")
    with open(scored_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    hot = sum(1 for r in records if r["priority"] == "Hot")
    warm = sum(1 for r in records if r["priority"] == "Warm")
    cool = sum(1 for r in records if r["priority"] == "Cool")
    cold = sum(1 for r in records if r["priority"] == "Cold")
    avg_score = round(sum(int(r["lead_score"]) for r in records) / max(len(records), 1), 1)

    summary = {
        "total_scored": len(records),
        "average_score": avg_score,
        "distribution": {"Hot": hot, "Warm": warm, "Cool": cool, "Cold": cold},
        "top_10": [
            {
                "record_id": r["record_id"],
                "name": f"{r.get('first_name', '')} {r.get('last_name', '')}".strip(),
                "company": r.get("company", ""),
                "title": r.get("job_title", ""),
                "score": r["lead_score"],
                "priority": r["priority"],
            }
            for r in records[:10]
        ],
    }

    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    os.makedirs(report_dir, exist_ok=True)
    summary_path = os.path.join(report_dir, "scoring_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    print("=" * 55)
    print("  LEAD SCORING COMPLETE")
    print("=" * 55)
    print(f"  Total scored:   {len(records)}")
    print(f"  Average score:  {avg_score}")
    print(f"  Hot (75+):      {hot}")
    print(f"  Warm (55-74):   {warm}")
    print(f"  Cool (35-54):   {cool}")
    print(f"  Cold (<35):     {cold}")
    print(f"\n  Top 5 leads:")
    for r in records[:5]:
        name = f"{r.get('first_name', '')} {r.get('last_name', '')}".strip()
        print(f"    {r['lead_score']:>3}  {name:<25} {r.get('company', ''):<25} {r.get('job_title', '')}")
    print(f"\n  Scored CSV:     {scored_path}")
    print(f"  Summary:        {summary_path}")
    print("=" * 55)


def main():
    if len(sys.argv) < 2:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "data", "crm_cleaned.csv")
    else:
        csv_path = sys.argv[1]

    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        sys.exit(1)

    run_scoring(csv_path)


if __name__ == "__main__":
    main()
