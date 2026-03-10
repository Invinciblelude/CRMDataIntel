#!/usr/bin/env python3
"""
SOP 2 + SOP 4 — CRM Data Cleansing, Deduplication & Normalization
Takes a messy CRM CSV, cleans formats, deduplicates, normalizes titles/industries,
and outputs a clean CSV ready to reimport into Salesforce.
"""

import csv
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime

TITLE_MAP = {
    "ceo": ("CEO", "C-Suite"),
    "chief executive officer": ("CEO", "C-Suite"),
    "c.e.o.": ("CEO", "C-Suite"),
    "founder & ceo": ("CEO / Founder", "C-Suite"),
    "cfo": ("CFO", "C-Suite"),
    "chief financial officer": ("CFO", "C-Suite"),
    "c.f.o.": ("CFO", "C-Suite"),
    "cto": ("CTO", "C-Suite"),
    "chief technology officer": ("CTO", "C-Suite"),
    "c.t.o.": ("CTO", "C-Suite"),
    "coo": ("COO", "C-Suite"),
    "chief operating officer": ("COO", "C-Suite"),
    "c.o.o.": ("COO", "C-Suite"),
    "vp sales": ("VP of Sales", "VP"),
    "vp of sales": ("VP of Sales", "VP"),
    "vice president sales": ("VP of Sales", "VP"),
    "vice president, sales": ("VP of Sales", "VP"),
    "v.p. sales": ("VP of Sales", "VP"),
    "director of operations": ("Director of Operations", "Director"),
    "dir operations": ("Director of Operations", "Director"),
    "director, operations": ("Director of Operations", "Director"),
    "ops director": ("Director of Operations", "Director"),
    "director operations": ("Director of Operations", "Director"),
    "sales manager": ("Sales Manager", "Manager"),
    "sales mgr": ("Sales Manager", "Manager"),
    "mgr, sales": ("Sales Manager", "Manager"),
    "manager - sales": ("Sales Manager", "Manager"),
    "plant manager": ("Plant Manager", "Manager"),
    "plant mgr": ("Plant Manager", "Manager"),
    "facility manager": ("Plant Manager", "Manager"),
    "plant manger": ("Plant Manager", "Manager"),
    "maintenance manager": ("Maintenance Manager", "Manager"),
    "maintenance mgr": ("Maintenance Manager", "Manager"),
    "maint manager": ("Maintenance Manager", "Manager"),
    "purchasing manager": ("Purchasing Manager", "Manager"),
    "procurement manager": ("Purchasing Manager", "Manager"),
    "buyer": ("Purchasing Manager", "Manager"),
    "head of procurement": ("Purchasing Manager", "Manager"),
    "it director": ("IT Director", "Director"),
    "director of it": ("IT Director", "Director"),
    "dir it": ("IT Director", "Director"),
    "information technology director": ("IT Director", "Director"),
    "it dir": ("IT Director", "Director"),
    "sales representative": ("Sales Representative", "Individual Contributor"),
    "sales rep": ("Sales Representative", "Individual Contributor"),
    "account executive": ("Account Executive", "Individual Contributor"),
    "ae": ("Account Executive", "Individual Contributor"),
    "inside sales rep": ("Inside Sales Representative", "Individual Contributor"),
    "engineer": ("Engineer", "Individual Contributor"),
    "project engineer": ("Project Engineer", "Individual Contributor"),
    "sr engineer": ("Senior Engineer", "Individual Contributor"),
    "staff engineer": ("Staff Engineer", "Individual Contributor"),
    "accountant": ("Accountant", "Individual Contributor"),
    "staff accountant": ("Accountant", "Individual Contributor"),
    "senior accountant": ("Senior Accountant", "Individual Contributor"),
    "hr manager": ("HR Manager", "Manager"),
    "human resources manager": ("HR Manager", "Manager"),
    "hr mgr": ("HR Manager", "Manager"),
    "people manager": ("HR Manager", "Manager"),
    "marketing manager": ("Marketing Manager", "Manager"),
    "mktg manager": ("Marketing Manager", "Manager"),
    "marketing mgr": ("Marketing Manager", "Manager"),
    "dir marketing": ("Director of Marketing", "Director"),
    "owner": ("Owner", "Owner/Founder"),
    "business owner": ("Owner", "Owner/Founder"),
    "founder": ("Founder", "Owner/Founder"),
    "president": ("President", "C-Suite"),
    "co-founder": ("Co-Founder", "Owner/Founder"),
}

INDUSTRY_MAP = {
    "manufacturing": "Manufacturing",
    "mfg": "Manufacturing",
    "construction": "Construction",
    "general contracting": "Construction",
    "logistics": "Logistics & Distribution",
    "warehousing & logistics": "Logistics & Distribution",
    "energy": "Energy",
    "oil & gas": "Energy - Oil & Gas",
    "oil and gas": "Energy - Oil & Gas",
    "technology": "Technology",
    "tech": "Technology",
    "it": "Technology",
    "healthcare": "Healthcare",
    "medical": "Healthcare",
    "finance": "Financial Services",
    "financial services": "Financial Services",
    "automotive": "Automotive",
    "auto": "Automotive",
    "industrial equipment": "Industrial Equipment",
    "industrial services": "Industrial Services",
    "wholesale": "Wholesale & Distribution",
    "security": "Security Services",
    "agriculture": "Agriculture",
    "electrical": "Electrical",
    "aerospace": "Aerospace & Defense",
    "mining": "Mining",
    "environmental": "Environmental Services",
    "marine": "Marine",
    "chemical": "Chemical",
    "utilities": "Utilities",
    "real estate": "Real Estate",
    "transportation": "Transportation",
    "education": "Education",
    "packaging": "Packaging",
    "waste management": "Waste Management",
    "water treatment": "Water Treatment",
    "telecom": "Telecommunications",
    "other": "",
    "n/a": "",
    "unknown": "",
    "-": "",
}

STATE_MAP = {
    "california": "CA", "texas": "TX", "new york": "NY", "florida": "FL",
    "illinois": "IL", "ohio": "OH", "pennsylvania": "PA", "georgia": "GA",
    "north carolina": "NC", "michigan": "MI", "arizona": "AZ",
    "washington": "WA", "colorado": "CO", "nevada": "NV", "oregon": "OR",
    "indiana": "IN", "tennessee": "TN", "missouri": "MO",
    "wisconsin": "WI", "minnesota": "MN",
}

LEAD_SOURCE_MAP = {
    "website": "Website",
    "webform": "Website",
    "referral": "Referral",
    "cold call": "Cold Call",
    "trade show": "Trade Show",
    "tradeshow": "Trade Show",
    "linkedin": "LinkedIn",
    "inbound": "Inbound",
    "outbound": "Outbound",
    "partner": "Partner",
    "event": "Event",
}


def is_empty(val):
    if val is None:
        return True
    v = str(val).strip().lower()
    return v in ("", "n/a", "unknown", "none", "-", "null")


def clean_phone(val):
    if is_empty(val):
        return ""
    digits = re.sub(r"\D", "", val)
    if digits in ("0000000000", "0000000"):
        return ""
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    if 7 <= len(digits) <= 15:
        return digits
    return ""


def clean_email(val):
    if is_empty(val):
        return ""
    val = val.strip().lower()
    if re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", val):
        return val
    return ""


def clean_name(val):
    if is_empty(val):
        return ""
    return val.strip().title()


def clean_company(val):
    if is_empty(val):
        return ""
    val = re.sub(r"\s+", " ", val.strip())
    val = val.title()
    for suffix in [" Inc.", " Inc", " Llc", " Corp", " Co", " Ltd"]:
        if val.endswith(suffix):
            val = val[:-len(suffix)]
    return val.strip()


def normalize_title(val):
    if is_empty(val):
        return "", ""
    key = val.strip().lower()
    if key in TITLE_MAP:
        return TITLE_MAP[key]
    return val.strip().title(), "Unknown"


def normalize_industry(val):
    if is_empty(val):
        return ""
    key = val.strip().lower()
    return INDUSTRY_MAP.get(key, val.strip().title())


def normalize_state(val):
    if is_empty(val):
        return ""
    val = val.strip()
    if len(val) == 2:
        return val.upper()
    key = val.lower()
    return STATE_MAP.get(key, val)


def normalize_lead_source(val):
    if is_empty(val):
        return ""
    key = val.strip().lower()
    return LEAD_SOURCE_MAP.get(key, val.strip().title())


def deduplicate(records):
    email_groups = defaultdict(list)
    name_groups = defaultdict(list)

    for i, r in enumerate(records):
        email = (r.get("email") or "").strip().lower()
        if email and "@" in email:
            base_email = re.sub(r"[._]", "", email.split("@")[0]) + "@" + email.split("@")[1]
            email_groups[base_email].append(i)

        name_key = f"{(r.get('first_name') or '').strip().lower()}|{(r.get('last_name') or '').strip().lower()}|{r.get('_clean_company', '').lower()}"
        if not is_empty(r.get("last_name")):
            name_groups[name_key].append(i)

    duplicate_indices = set()
    merge_log = []

    all_groups = list(email_groups.values()) + list(name_groups.values())

    for group_indices in all_groups:
        if len(group_indices) <= 1:
            continue

        best_idx = group_indices[0]
        best_score = 0
        for idx in group_indices:
            score = sum(1 for v in records[idx].values() if not is_empty(v))
            if score > best_score:
                best_score = score
                best_idx = idx

        for idx in group_indices:
            if idx != best_idx:
                for key, val in records[idx].items():
                    if is_empty(records[best_idx].get(key)) and not is_empty(val):
                        records[best_idx][key] = val
                duplicate_indices.add(idx)
                merge_log.append({
                    "kept": records[best_idx].get("record_id", ""),
                    "removed": records[idx].get("record_id", ""),
                })

    deduped = [r for i, r in enumerate(records) if i not in duplicate_indices]
    return deduped, merge_log


def cleanse_records(records):
    for r in records:
        r["first_name"] = clean_name(r.get("first_name", ""))
        r["last_name"] = clean_name(r.get("last_name", ""))
        r["email"] = clean_email(r.get("email", ""))
        r["phone"] = clean_phone(r.get("phone", ""))
        r["direct_dial"] = clean_phone(r.get("direct_dial", ""))

        std_title, seniority = normalize_title(r.get("job_title", ""))
        r["job_title"] = std_title
        r["seniority_level"] = seniority

        r["_clean_company"] = clean_company(r.get("company", ""))
        r["company"] = r["_clean_company"]

        r["industry"] = normalize_industry(r.get("industry", ""))
        r["state"] = normalize_state(r.get("state", ""))
        r["lead_source"] = normalize_lead_source(r.get("lead_source", ""))

        r["lifecycle_stage"] = (r.get("lifecycle_stage") or "").strip().title()
        if r["lifecycle_stage"] in ("Mql",):
            r["lifecycle_stage"] = "MQL"
        if r["lifecycle_stage"] in ("Sql",):
            r["lifecycle_stage"] = "SQL"

    return records


def run_cleanse(csv_path):
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        records = list(reader)
        fieldnames = list(reader.fieldnames)

    original_count = len(records)
    records = cleanse_records(records)
    deduped, merge_log = deduplicate(records)

    for r in deduped:
        r.pop("_clean_company", None)

    if "seniority_level" not in fieldnames:
        idx = fieldnames.index("job_title") + 1 if "job_title" in fieldnames else len(fieldnames)
        fieldnames.insert(idx, "seniority_level")

    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    os.makedirs(output_dir, exist_ok=True)

    clean_path = os.path.join(output_dir, "crm_cleaned.csv")
    with open(clean_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(deduped)

    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    os.makedirs(report_dir, exist_ok=True)
    merge_path = os.path.join(report_dir, "merge_log.json")
    with open(merge_path, "w") as f:
        json.dump({
            "original_records": original_count,
            "after_dedup": len(deduped),
            "duplicates_removed": original_count - len(deduped),
            "merge_details": merge_log,
        }, f, indent=2)

    print("=" * 55)
    print("  CRM CLEANSE & DEDUPE COMPLETE")
    print("=" * 55)
    print(f"  Original records:     {original_count}")
    print(f"  After deduplication:  {len(deduped)}")
    print(f"  Duplicates removed:   {original_count - len(deduped)}")
    print(f"  Merge log:            {merge_path}")
    print(f"  Cleaned CSV:          {clean_path}")
    print("=" * 55)

    return clean_path, len(deduped), original_count


def main():
    if len(sys.argv) < 2:
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "data", "sample_crm_export.csv")
    else:
        csv_path = sys.argv[1]

    if not os.path.exists(csv_path):
        print(f"File not found: {csv_path}")
        sys.exit(1)

    run_cleanse(csv_path)


if __name__ == "__main__":
    main()
