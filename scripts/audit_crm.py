#!/usr/bin/env python3
"""
SOP 1 — CRM Data Audit
Reads a Salesforce-style CSV export, profiles every column,
detects duplicates, missing fields, stale records, and bad values.
Outputs a structured JSON report + prints a human-readable summary.
"""

import csv
import json
import os
import sys
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta

REQUIRED_FIELDS = [
    "email", "phone", "job_title", "company", "industry",
    "lifecycle_stage", "lead_source", "state"
]

HIGH_VALUE_FIELDS = ["email", "phone", "direct_dial", "job_title", "company"]


def load_csv(path):
    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames


def is_empty(val):
    if val is None:
        return True
    v = str(val).strip().lower()
    return v in ("", "n/a", "unknown", "none", "-", "null")


def is_valid_email(val):
    if is_empty(val):
        return False
    return bool(re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", val.strip()))


def is_valid_phone(val):
    if is_empty(val):
        return False
    digits = re.sub(r"\D", "", val)
    if digits in ("0000000000", "0000000"):
        return False
    return 7 <= len(digits) <= 15


def detect_duplicates(records):
    email_groups = defaultdict(list)
    name_company_groups = defaultdict(list)

    for r in records:
        email = (r.get("email") or "").strip().lower()
        if email and "@" in email:
            email_groups[email].append(r["record_id"])

        name_key = f"{(r.get('first_name') or '').strip().lower()}|{(r.get('last_name') or '').strip().lower()}|{(r.get('company') or '').strip().lower()}"
        if not is_empty(r.get("last_name")):
            name_company_groups[name_key].append(r["record_id"])

    email_dupes = {k: v for k, v in email_groups.items() if len(v) > 1}
    name_dupes = {k: v for k, v in name_company_groups.items() if len(v) > 1}

    all_dupe_ids = set()
    for ids in email_dupes.values():
        all_dupe_ids.update(ids)
    for ids in name_dupes.values():
        all_dupe_ids.update(ids)

    return {
        "email_duplicate_groups": len(email_dupes),
        "name_company_duplicate_groups": len(name_dupes),
        "total_records_in_duplicate_groups": len(all_dupe_ids),
        "sample_email_dupes": dict(list(email_dupes.items())[:5]),
        "sample_name_dupes": dict(list(name_dupes.items())[:5]),
    }


def detect_stale(records, stale_days=365):
    cutoff = datetime.now() - timedelta(days=stale_days)
    stale = []
    no_activity = []

    for r in records:
        last_act = r.get("last_activity_date", "")
        if is_empty(last_act):
            no_activity.append(r["record_id"])
            continue
        try:
            dt = datetime.strptime(last_act.strip(), "%Y-%m-%d")
            if dt < cutoff:
                stale.append(r["record_id"])
        except ValueError:
            no_activity.append(r["record_id"])

    return {
        "stale_records": len(stale),
        "no_activity_date": len(no_activity),
        "stale_pct": round(len(stale) / max(len(records), 1) * 100, 1),
        "cutoff_date": cutoff.strftime("%Y-%m-%d"),
    }


def field_completeness(records, fieldnames):
    total = len(records)
    results = {}
    for field in fieldnames:
        filled = sum(1 for r in records if not is_empty(r.get(field)))
        results[field] = {
            "filled": filled,
            "missing": total - filled,
            "completeness_pct": round(filled / max(total, 1) * 100, 1),
        }
    return results


def value_distribution(records, field, top_n=10):
    counter = Counter()
    for r in records:
        val = (r.get(field) or "").strip()
        if is_empty(val):
            counter["(empty)"] += 1
        else:
            counter[val] += 1
    return dict(counter.most_common(top_n))


def email_quality(records):
    total = len(records)
    valid = sum(1 for r in records if is_valid_email(r.get("email", "")))
    personal = sum(1 for r in records
                   if is_valid_email(r.get("email", ""))
                   and any(d in r["email"].lower() for d in ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "aol.com"]))
    return {
        "valid_emails": valid,
        "valid_pct": round(valid / max(total, 1) * 100, 1),
        "personal_emails": personal,
        "personal_pct": round(personal / max(total, 1) * 100, 1),
        "missing_or_invalid": total - valid,
    }


def phone_quality(records):
    total = len(records)
    valid_phone = sum(1 for r in records if is_valid_phone(r.get("phone", "")))
    valid_dd = sum(1 for r in records if is_valid_phone(r.get("direct_dial", "")))
    return {
        "valid_phone": valid_phone,
        "valid_phone_pct": round(valid_phone / max(total, 1) * 100, 1),
        "valid_direct_dial": valid_dd,
        "valid_direct_dial_pct": round(valid_dd / max(total, 1) * 100, 1),
    }


def title_inconsistency(records):
    titles = [r.get("job_title", "").strip() for r in records if not is_empty(r.get("job_title"))]
    counter = Counter(titles)
    return {
        "unique_title_variants": len(counter),
        "total_with_title": len(titles),
        "top_20_titles": dict(counter.most_common(20)),
    }


def owner_distribution(records):
    counter = Counter()
    for r in records:
        owner = (r.get("owner") or "").strip()
        counter[owner if owner else "(unassigned)"] += 1
    return dict(counter.most_common(20))


def run_audit(csv_path):
    records, fieldnames = load_csv(csv_path)
    total = len(records)

    report = {
        "audit_date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source_file": os.path.basename(csv_path),
        "total_records": total,
        "field_completeness": field_completeness(records, fieldnames),
        "email_quality": email_quality(records),
        "phone_quality": phone_quality(records),
        "duplicates": detect_duplicates(records),
        "stale_records": detect_stale(records),
        "title_inconsistency": title_inconsistency(records),
        "industry_distribution": value_distribution(records, "industry", 20),
        "lifecycle_distribution": value_distribution(records, "lifecycle_stage", 10),
        "lead_source_distribution": value_distribution(records, "lead_source", 15),
        "state_distribution": value_distribution(records, "state", 25),
        "owner_distribution": owner_distribution(records),
    }

    critical_missing = {}
    for f in HIGH_VALUE_FIELDS:
        comp = report["field_completeness"].get(f, {})
        if comp.get("completeness_pct", 100) < 80:
            critical_missing[f] = comp

    report["critical_gaps"] = critical_missing

    score = 100
    email_pct = report["email_quality"]["valid_pct"]
    score -= max(0, (80 - email_pct)) * 0.5

    phone_pct = report["phone_quality"]["valid_phone_pct"]
    score -= max(0, (70 - phone_pct)) * 0.3

    dupe_pct = report["duplicates"]["total_records_in_duplicate_groups"] / max(total, 1) * 100
    score -= min(dupe_pct * 0.5, 15)

    stale_pct = report["stale_records"]["stale_pct"]
    score -= min(stale_pct * 0.3, 10)

    title_variants = report["title_inconsistency"]["unique_title_variants"]
    if title_variants > 30:
        score -= 5

    for f in REQUIRED_FIELDS:
        comp_pct = report["field_completeness"].get(f, {}).get("completeness_pct", 100)
        if comp_pct < 70:
            score -= 3

    report["data_health_score"] = round(max(0, min(100, score)), 1)

    grade_map = [(90, "A"), (80, "B"), (70, "C"), (60, "D")]
    grade = "F"
    for threshold, g in grade_map:
        if report["data_health_score"] >= threshold:
            grade = g
            break
    report["data_health_grade"] = grade

    return report


def print_summary(report):
    print("=" * 65)
    print("  CRM DATA AUDIT REPORT")
    print(f"  Source: {report['source_file']}")
    print(f"  Date: {report['audit_date']}")
    print(f"  Records: {report['total_records']}")
    print("=" * 65)

    print(f"\n  DATA HEALTH SCORE: {report['data_health_score']} / 100  "
          f"(Grade: {report['data_health_grade']})\n")

    print("-" * 65)
    print("  FIELD COMPLETENESS")
    print("-" * 65)
    for field, stats in report["field_completeness"].items():
        bar_len = int(stats["completeness_pct"] / 5)
        bar = "#" * bar_len + "." * (20 - bar_len)
        flag = " !! " if stats["completeness_pct"] < 70 else "    "
        print(f"  {flag}{field:<22} [{bar}] {stats['completeness_pct']:>5.1f}%  "
              f"({stats['missing']} missing)")

    print(f"\n{'-' * 65}")
    print("  EMAIL QUALITY")
    print(f"    Valid work emails:  {report['email_quality']['valid_pct']}%")
    print(f"    Personal emails:    {report['email_quality']['personal_pct']}%")
    print(f"    Missing/invalid:    {report['email_quality']['missing_or_invalid']}")

    print(f"\n  PHONE QUALITY")
    print(f"    Valid phone:        {report['phone_quality']['valid_phone_pct']}%")
    print(f"    Valid direct dial:  {report['phone_quality']['valid_direct_dial_pct']}%")

    print(f"\n{'-' * 65}")
    print("  DUPLICATES")
    dupes = report["duplicates"]
    print(f"    Email-based groups: {dupes['email_duplicate_groups']}")
    print(f"    Name+Company groups:{dupes['name_company_duplicate_groups']}")
    print(f"    Records affected:   {dupes['total_records_in_duplicate_groups']}")

    print(f"\n  STALE RECORDS (no activity since {report['stale_records']['cutoff_date']})")
    print(f"    Stale:              {report['stale_records']['stale_records']} "
          f"({report['stale_records']['stale_pct']}%)")

    print(f"\n{'-' * 65}")
    print("  TITLE INCONSISTENCY")
    print(f"    Unique variants:    {report['title_inconsistency']['unique_title_variants']}")
    print(f"    (Many variants of same role = normalization needed)")

    if report["critical_gaps"]:
        print(f"\n{'=' * 65}")
        print("  CRITICAL GAPS (high-value fields below 80%)")
        for field, stats in report["critical_gaps"].items():
            print(f"    {field}: {stats['completeness_pct']}% complete "
                  f"({stats['missing']} records missing)")

    print(f"\n{'=' * 65}")
    print("  RECOMMENDATIONS")
    print("  1. Deduplicate records (email + name/company matching)")
    print("  2. Enrich missing emails, phones, and direct dials")
    print("  3. Standardize job titles into role/seniority buckets")
    print("  4. Normalize industry and state fields")
    print("  5. Archive or re-engage stale records")
    print("  6. Implement validation rules to prevent future decay")
    print("=" * 65)


def main():
    if len(sys.argv) < 2:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "data", "sample_crm_export.csv")
    else:
        csv_path = sys.argv[1]

    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        sys.exit(1)

    report = run_audit(csv_path)

    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "audit_report.json")
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print_summary(report)
    print(f"\n  Full report saved: {report_path}")


if __name__ == "__main__":
    main()
