#!/usr/bin/env python3
"""
Generate a realistic messy CRM dataset (600 records) that demonstrates
common Salesforce data quality problems: duplicates, missing fields,
inconsistent formatting, stale records, and bad values.
"""

import csv
import random
import string
import os
from datetime import datetime, timedelta

random.seed(42)

FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Charles", "Karen", "Chris",
    "Daniel", "Lisa", "Matthew", "Nancy", "Anthony", "Betty", "Mark",
    "Margaret", "Donald", "Sandra", "Steven", "Ashley", "Paul", "Kimberly",
    "Andrew", "Emily", "Joshua", "Donna", "Kenneth", "Michelle", "Kevin",
    "Carol", "Brian", "Amanda", "George", "Dorothy", "Timothy", "Melissa",
    "Ronald", "Deborah", "Edward", "Stephanie", "Jason", "Rebecca", "Jeff",
    "Sharon", "Ryan", "Laura", "Jacob", "Cynthia", "Gary", "Kathleen",
    "Nicholas", "Amy", "Eric", "Angela", "Jonathan", "Shirley", "Stephen",
    "Anna", "Larry", "Brenda", "Justin", "Pamela", "Scott", "Emma",
    "Brandon", "Nicole", "Benjamin", "Helen", "Samuel", "Samantha",
    "Raymond", "Katherine", "Gregory", "Christine", "Frank", "Debra",
    "Alexander", "Rachel", "Patrick", "Carolyn", "Jack", "Janet",
    "Dennis", "Catherine", "Jerry", "Maria", "Tyler", "Heather"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
    "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris",
    "Morales", "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan",
    "Cooper", "Peterson", "Bailey", "Reed", "Kelly", "Howard", "Ramos",
    "Kim", "Cox", "Ward", "Richardson", "Watson", "Brooks", "Chavez",
    "Wood", "James", "Bennett", "Gray", "Mendoza", "Ruiz", "Hughes",
    "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers", "Long",
    "Ross", "Foster", "Jimenez"
]

COMPANIES = [
    ("Acme Manufacturing", "acmemanufacturing.com", "Manufacturing"),
    ("CryoBuild Systems", "cryobuild.com", "Industrial Equipment"),
    ("Precision Metals Inc", "precisionmetals.com", "Manufacturing"),
    ("Atlas Logistics Group", "atlaslogistics.com", "Logistics"),
    ("Summit Energy Solutions", "summitenergy.com", "Energy"),
    ("Vanguard Construction", "vanguardconstruction.com", "Construction"),
    ("ProFlow Plumbing Supply", "proflowsupply.com", "Wholesale"),
    ("Pacific Steel Works", "pacificsteelworks.com", "Manufacturing"),
    ("Apex Industrial Services", "apexindustrial.com", "Industrial Services"),
    ("Delta Fabrication Co", "deltafab.com", "Manufacturing"),
    ("Ironclad Security Systems", "ironcladsecurity.com", "Security"),
    ("NovaTech Solutions", "novatechsolutions.com", "Technology"),
    ("Greenfield Farms LLC", "greenfieldfarms.com", "Agriculture"),
    ("Titan Concrete Supply", "titanconcrete.com", "Construction"),
    ("BlueLine Electrical", "bluelineelectrical.com", "Electrical"),
    ("Westside Auto Parts", "westsideautoparts.com", "Automotive"),
    ("CorePoint Engineering", "corepointeng.com", "Engineering"),
    ("SunPeak Solar", "sunpeaksolar.com", "Energy"),
    ("Falcon Aerospace", "falconaerospace.com", "Aerospace"),
    ("RedRock Mining Corp", "redrockmining.com", "Mining"),
    ("SafeGuard Environmental", "safeguardenv.com", "Environmental"),
    ("Metro Distribution Inc", "metrodistribution.com", "Logistics"),
    ("HighTide Marine", "hightidemarine.com", "Marine"),
    ("PrimeCare Medical Supply", "primecaremed.com", "Healthcare"),
    ("Sterling Chemical Co", "sterlingchemical.com", "Chemical"),
    ("PowerGrid Utilities", "powergridutil.com", "Utilities"),
    ("HarborView Properties", "harborviewprop.com", "Real Estate"),
    ("TrailBlazer Transport", "trailblazertrans.com", "Transportation"),
    ("Quantum Data Systems", "quantumdatasys.com", "Technology"),
    ("RiverBend Paper Mill", "riverbendpaper.com", "Manufacturing"),
    ("OakBridge Financial", "oakbridgefin.com", "Finance"),
    ("PeakView Analytics", "peakviewanalytics.com", "Technology"),
    ("Clearwater Treatment", "clearwatertreat.com", "Water Treatment"),
    ("MountainTop Telecom", "mountaintoptelecom.com", "Telecom"),
    ("GoldStar Packaging", "goldstarpackaging.com", "Packaging"),
    ("NorthStar Drilling", "northstardrilling.com", "Oil & Gas"),
    ("BrightPath Education", "brightpathedu.com", "Education"),
    ("StoneWall Masonry", "stonewallmasonry.com", "Construction"),
    ("EverGreen Recycling", "evergreenrecycling.com", "Waste Management"),
    ("SwiftCargo Freight", "swiftcargofreight.com", "Logistics"),
]

TITLE_VARIANTS = {
    "VP Sales": ["VP Sales", "VP of Sales", "Vice President Sales",
                 "Vice President, Sales", "V.P. Sales", "vp sales"],
    "Director Operations": ["Director of Operations", "Dir Operations",
                            "Director, Operations", "Ops Director",
                            "Director Of Operations", "director operations"],
    "Sales Manager": ["Sales Manager", "Sales Mgr", "Mgr, Sales",
                      "Manager - Sales", "sales manager", "SALES MANAGER"],
    "CEO": ["CEO", "Chief Executive Officer", "C.E.O.", "ceo",
            "Chief Exec Officer", "Founder & CEO"],
    "CFO": ["CFO", "Chief Financial Officer", "C.F.O.", "cfo"],
    "CTO": ["CTO", "Chief Technology Officer", "C.T.O.", "cto"],
    "COO": ["COO", "Chief Operating Officer", "C.O.O.", "coo"],
    "Plant Manager": ["Plant Manager", "Plant Mgr", "Facility Manager",
                      "plant manager", "Plant Manger"],
    "Maintenance Manager": ["Maintenance Manager", "Maintenance Mgr",
                            "Maint Manager", "maintenance manager"],
    "Purchasing Manager": ["Purchasing Manager", "Procurement Manager",
                           "Buyer", "purchasing manager", "Head of Procurement"],
    "IT Director": ["IT Director", "Director of IT", "Dir IT",
                    "Information Technology Director", "IT Dir"],
    "Sales Rep": ["Sales Representative", "Sales Rep", "Account Executive",
                  "AE", "sales rep", "Inside Sales Rep"],
    "Engineer": ["Engineer", "Project Engineer", "Sr Engineer",
                 "Staff Engineer", "engineer"],
    "Accountant": ["Accountant", "Staff Accountant", "Senior Accountant",
                   "accountant"],
    "HR Manager": ["HR Manager", "Human Resources Manager", "HR Mgr",
                   "People Manager", "hr manager"],
    "Marketing Manager": ["Marketing Manager", "Mktg Manager",
                          "Marketing Mgr", "Dir Marketing"],
    "Owner": ["Owner", "Business Owner", "Founder", "President",
              "owner", "Co-Founder"],
}

STATES = {
    "CA": "California", "TX": "Texas", "NY": "New York", "FL": "Florida",
    "IL": "Illinois", "OH": "Ohio", "PA": "Pennsylvania", "GA": "Georgia",
    "NC": "North Carolina", "MI": "Michigan", "AZ": "Arizona", "WA": "Washington",
    "CO": "Colorado", "NV": "Nevada", "OR": "Oregon", "IN": "Indiana",
    "TN": "Tennessee", "MO": "Missouri", "WI": "Wisconsin", "MN": "Minnesota",
}

LIFECYCLE_STAGES = ["Lead", "MQL", "SQL", "Opportunity", "Customer", "Evangelist"]
LEAD_SOURCES = ["Website", "Referral", "Cold Call", "Trade Show", "LinkedIn",
                "Inbound", "Outbound", "Partner", "Event", "webform",
                "TRADESHOW", "cold call", "website", ""]

INDUSTRIES_MESSY = [
    "Manufacturing", "manufacturing", "MANUFACTURING", "Mfg",
    "Construction", "construction", "CONSTRUCTION", "General Contracting",
    "Logistics", "logistics", "LOGISTICS", "Warehousing & Logistics",
    "Energy", "energy", "ENERGY", "Oil & Gas", "oil and gas",
    "Technology", "technology", "TECHNOLOGY", "Tech", "IT",
    "Healthcare", "healthcare", "HEALTHCARE", "Medical",
    "Finance", "finance", "FINANCE", "Financial Services",
    "Automotive", "automotive", "AUTOMOTIVE", "Auto",
    "", "Other", "N/A", "Unknown", "-",
]


def random_phone(broken=False):
    if broken:
        styles = [
            f"{random.randint(100,999)}{random.randint(100,999)}{random.randint(1000,9999)}",
            f"+1{random.randint(100,999)}{random.randint(100,999)}{random.randint(1000,9999)}",
            f"({random.randint(100,999)}) {random.randint(100,999)} {random.randint(1000,9999)}",
            f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(1000,9999)}",
            "N/A",
            "",
            "000-000-0000",
            f"+1 ({random.randint(100,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}",
        ]
        return random.choice(styles)
    area = random.randint(200, 999)
    ex = random.randint(200, 999)
    num = random.randint(1000, 9999)
    return f"({area}) {ex}-{num}"


def random_email(first, last, domain, broken=False):
    if broken:
        styles = [
            "",
            "N/A",
            f"{first.lower()}@{domain}",
            f"{first.lower()}{last.lower()}@gmail.com",
            f"{first[0].lower()}{last.lower()}@{domain}",
            f"{first.lower()}.{last.lower()}@{domain}",
        ]
        return random.choice(styles)
    return f"{first.lower()}.{last.lower()}@{domain}"


def random_date(start_year=2019, end_year=2026):
    start = datetime(start_year, 1, 1)
    end = datetime(end_year, 3, 1)
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


def generate_records(n=600):
    records = []
    used_emails = set()
    record_id = 1000

    for i in range(n):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        company_name, domain, base_industry = random.choice(COMPANIES)

        is_messy = random.random() < 0.4
        is_duplicate = random.random() < 0.12
        is_stale = random.random() < 0.15

        title_key = random.choice(list(TITLE_VARIANTS.keys()))
        title = random.choice(TITLE_VARIANTS[title_key])

        email = random_email(first, last, domain, broken=(random.random() < 0.25))
        phone = random_phone(broken=(random.random() < 0.30))
        direct_dial = random_phone(broken=(random.random() < 0.55))

        state_code = random.choice(list(STATES.keys()))
        if is_messy and random.random() < 0.4:
            state_val = STATES[state_code]
        elif is_messy and random.random() < 0.3:
            state_val = ""
        else:
            state_val = state_code

        industry = random.choice(INDUSTRIES_MESSY) if is_messy else base_industry

        if is_messy and random.random() < 0.3:
            company_display = random.choice([
                company_name.upper(),
                company_name.lower(),
                company_name + " " + random.choice(["Inc", "Inc.", "LLC", "Corp", ""]),
                company_name.replace(" ", "  "),
            ])
        else:
            company_display = company_name

        lifecycle = random.choice(LIFECYCLE_STAGES)
        lead_source = random.choice(LEAD_SOURCES)

        created = random_date(2019, 2025)
        if is_stale:
            last_activity = created + timedelta(days=random.randint(1, 90))
        else:
            last_activity = random_date(2024, 2026)

        annual_revenue = ""
        employees = ""
        if random.random() > 0.35:
            rev_options = [
                "$1M-$5M", "$5M-$10M", "$10M-$50M", "$50M-$100M",
                "$100M+", "1000000", "5000000", "50M", "$10M", "",
                "Unknown", "N/A",
            ]
            annual_revenue = random.choice(rev_options)
        if random.random() > 0.30:
            emp_options = [
                "10-50", "50-200", "200-500", "500-1000", "1000+",
                "25", "150", "450", "1200", "", "Unknown", "N/A",
            ]
            employees = random.choice(emp_options)

        linkedin = ""
        if random.random() > 0.50:
            linkedin = f"https://linkedin.com/in/{first.lower()}-{last.lower()}-{random.randint(100,999)}"

        notes = ""
        if random.random() > 0.60:
            note_options = [
                "Met at trade show 2024",
                "Interested in automation",
                "Follow up Q1",
                "Not interested right now",
                "Budget approved for Q2",
                "Sent proposal 11/2024",
                "Left voicemail",
                "Referred by existing customer",
                "Needs predictive maintenance solution",
                "Looking for CRM cleanup",
                "Decision maker",
                "Gatekeeper - need to get to director",
                "",
            ]
            notes = random.choice(note_options)

        record = {
            "record_id": f"SF-{record_id}",
            "first_name": first if random.random() > 0.05 else "",
            "last_name": last,
            "email": email,
            "phone": phone,
            "direct_dial": direct_dial,
            "job_title": title,
            "company": company_display,
            "domain": domain if random.random() > 0.20 else "",
            "industry": industry,
            "state": state_val,
            "lifecycle_stage": lifecycle,
            "lead_source": lead_source,
            "created_date": created.strftime("%Y-%m-%d"),
            "last_activity_date": last_activity.strftime("%Y-%m-%d"),
            "annual_revenue": annual_revenue,
            "employees": employees,
            "linkedin_url": linkedin,
            "notes": notes,
            "owner": random.choice(["Rep A", "Rep B", "Rep C", "Rep D", ""]),
        }

        records.append(record)
        record_id += 1

        if is_duplicate:
            dup = dict(record)
            dup["record_id"] = f"SF-{record_id}"
            record_id += 1
            if random.random() < 0.5:
                dup["email"] = email.replace(".", "_") if email and "@" in email else email
            if random.random() < 0.5:
                dup["phone"] = random_phone(broken=True)
            if random.random() < 0.3:
                dup["job_title"] = random.choice(TITLE_VARIANTS[title_key])
            if random.random() < 0.3:
                dup["company"] = company_name + " Inc."
            dup["created_date"] = (created + timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")
            records.append(dup)

    return records


def main():
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "sample_crm_export.csv")

    records = generate_records(600)
    random.shuffle(records)

    fieldnames = list(records[0].keys())
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Generated {len(records)} records -> {output_path}")


if __name__ == "__main__":
    main()
