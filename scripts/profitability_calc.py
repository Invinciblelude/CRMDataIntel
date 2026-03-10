#!/usr/bin/env python3
"""
Profitability & Workload Calculator

Run this to model different engagement sizes and see:
- How many hours each phase takes you
- What your enrichment API costs are
- Your gross profit and effective hourly rate
- How many engagements you can handle per month

Adjust the variables at the top to match your situation.
"""

import json
import os

# ====================================================================
# ADJUST THESE TO YOUR SITUATION
# ====================================================================

# Your monthly fixed costs
CURSOR_MONTHLY = 200          # Cursor AI subscription
ENRICHMENT_TOOL_MONTHLY = 50  # Apollo free/starter, Hunter starter, etc.
HOSTING_TOOLS_MONTHLY = 50    # Domain, email, misc tools
TRAVEL_MONTHLY = 200          # Gas/travel to industrial areas
MISC_MONTHLY = 100            # Phone, supplies, etc.

# Your available work hours
WORK_HOURS_PER_WEEK = 40
WEEKS_PER_MONTH = 4.3
BILLABLE_RATIO = 0.60  # 60% of time is billable (rest is admin, prospecting, learning)

# Enrichment API costs per record (pass-through)
COST_PER_EMAIL_ENRICHMENT = 0.05    # Cleanlist / Hunter range
COST_PER_FULL_ENRICHMENT = 0.25     # Full contact (email + phone + company)
ENRICHMENT_HIT_RATE = 0.70          # 70% of records actually get enriched

# ====================================================================
# ENGAGEMENT MODELS
# ====================================================================

ENGAGEMENTS = {
    "Free Assessment (Door Opener)": {
        "records": 500,
        "price": 0,
        "hours": {
            "discovery_call": 0.5,
            "data_export_setup": 0.5,
            "run_audit_script": 0.5,
            "prepare_1page_report": 1.0,
            "present_findings": 0.5,
        },
        "enrichment_records": 0,
        "enrichment_type": "none",
        "description": "Run audit on a sample, present 1-page health score. Goal: earn the pilot.",
    },

    "Basic Pilot (Tier 1)": {
        "records": 10000,
        "price": 3500,
        "hours": {
            "kickoff_and_intake": 1.5,
            "data_export_and_mapping": 2.0,
            "audit_and_profiling": 2.0,
            "build_cleaning_rules": 4.0,
            "run_cleanse_and_dedupe": 2.0,
            "normalize_titles_industries": 2.0,
            "basic_enrichment_setup": 2.0,
            "run_enrichment": 1.0,
            "lead_scoring_setup": 2.0,
            "build_health_report": 2.0,
            "write_sop_document": 2.0,
            "present_results": 1.5,
            "revisions_and_qa": 3.0,
        },
        "enrichment_records": 3000,  # typically 30% need enrichment
        "enrichment_type": "email_only",
        "description": "Audit + Cleanse + Dedupe + Normalize + Basic Enrichment + Score. 4 weeks.",
    },

    "Standard Pilot (Tier 2)": {
        "records": 30000,
        "price": 7500,
        "hours": {
            "kickoff_and_intake": 2.0,
            "data_export_and_mapping": 3.0,
            "audit_and_profiling": 3.0,
            "build_cleaning_rules": 6.0,
            "run_cleanse_and_dedupe": 3.0,
            "normalize_titles_industries": 3.0,
            "enrichment_workflow_setup": 4.0,
            "run_enrichment_waterfall": 2.0,
            "lead_scoring_model": 4.0,
            "segmentation_and_icp_mapping": 3.0,
            "build_dashboard": 4.0,
            "build_health_report": 3.0,
            "write_sop_and_playbook": 3.0,
            "present_results": 2.0,
            "revisions_and_qa": 4.0,
        },
        "enrichment_records": 10000,
        "enrichment_type": "full",
        "description": "Everything in Basic + Dashboard + ICP Segmentation + Full Enrichment. 4-6 weeks.",
    },

    "Enterprise Pilot (Tier 3)": {
        "records": 100000,
        "price": 15000,
        "hours": {
            "kickoff_and_stakeholder_meetings": 4.0,
            "data_export_multi_object": 5.0,
            "audit_and_profiling": 5.0,
            "build_cleaning_rules_complex": 10.0,
            "run_cleanse_and_dedupe": 4.0,
            "normalize_all_fields": 5.0,
            "enrichment_workflow_waterfall": 6.0,
            "run_enrichment": 3.0,
            "lead_scoring_model_custom": 6.0,
            "segmentation_icp_persona": 5.0,
            "build_dashboard_advanced": 6.0,
            "salesforce_sandbox_import": 4.0,
            "build_health_report": 4.0,
            "write_sop_playbook_training": 5.0,
            "present_to_leadership": 3.0,
            "revisions_qa_iteration": 6.0,
        },
        "enrichment_records": 30000,
        "enrichment_type": "full",
        "description": "Full org cleanup. Multi-object. Sandbox import. Leadership presentation. 6-8 weeks.",
    },

    "Monthly Retainer (Basic)": {
        "records": 10000,
        "price": 1500,
        "hours": {
            "weekly_quality_check": 2.0,  # 0.5hr x 4 weeks
            "monthly_dedupe_run": 1.0,
            "monthly_enrichment_new_leads": 1.0,
            "dashboard_update": 1.0,
            "monthly_report": 1.5,
            "client_call": 1.0,
        },
        "enrichment_records": 500,  # new leads per month
        "enrichment_type": "full",
        "description": "Weekly checks, monthly dedupe, enrich new leads, dashboard, report. Per month.",
    },

    "Monthly Retainer (Standard)": {
        "records": 30000,
        "price": 3000,
        "hours": {
            "weekly_quality_check": 4.0,
            "biweekly_dedupe_run": 2.0,
            "monthly_enrichment": 2.0,
            "scoring_model_refresh": 2.0,
            "dashboard_update": 2.0,
            "monthly_report": 2.0,
            "client_call_and_coaching": 2.0,
        },
        "enrichment_records": 1500,
        "enrichment_type": "full",
        "description": "Everything in Basic + scoring refresh + coaching. Per month.",
    },
}


def calc_enrichment_cost(records, enrich_type):
    actual = int(records * ENRICHMENT_HIT_RATE)
    if enrich_type == "none":
        return 0, 0
    elif enrich_type == "email_only":
        return actual, round(actual * COST_PER_EMAIL_ENRICHMENT, 2)
    else:  # full
        return actual, round(actual * COST_PER_FULL_ENRICHMENT, 2)


def calc_engagement(name, eng):
    total_hours = sum(eng["hours"].values())
    enriched, enrich_cost = calc_enrichment_cost(
        eng["enrichment_records"], eng["enrichment_type"]
    )

    gross_revenue = eng["price"]
    direct_costs = enrich_cost
    gross_profit = gross_revenue - direct_costs
    effective_rate = round(gross_profit / max(total_hours, 1), 2)

    return {
        "engagement": name,
        "description": eng["description"],
        "records": eng["records"],
        "price_charged": eng["price"],
        "total_hours": round(total_hours, 1),
        "hours_breakdown": {k: v for k, v in eng["hours"].items()},
        "enrichment_records_sent": eng["enrichment_records"],
        "enrichment_records_hit": enriched,
        "enrichment_cost": enrich_cost,
        "gross_profit": gross_profit,
        "effective_hourly_rate": effective_rate,
    }


def calc_monthly_capacity():
    total_hours = WORK_HOURS_PER_WEEK * WEEKS_PER_MONTH
    billable_hours = total_hours * BILLABLE_RATIO
    return round(total_hours, 1), round(billable_hours, 1)


def main():
    total_monthly_hours, billable_hours = calc_monthly_capacity()
    fixed_costs = (CURSOR_MONTHLY + ENRICHMENT_TOOL_MONTHLY +
                   HOSTING_TOOLS_MONTHLY + TRAVEL_MONTHLY + MISC_MONTHLY)

    print("=" * 70)
    print("  CRM DATA SERVICES — PROFITABILITY & WORKLOAD CALCULATOR")
    print("=" * 70)

    print(f"\n  MONTHLY OVERHEAD")
    print(f"  {'Cursor AI:':<30} ${CURSOR_MONTHLY:>8}")
    print(f"  {'Enrichment tool (base):':<30} ${ENRICHMENT_TOOL_MONTHLY:>8}")
    print(f"  {'Hosting / tools:':<30} ${HOSTING_TOOLS_MONTHLY:>8}")
    print(f"  {'Travel / gas:':<30} ${TRAVEL_MONTHLY:>8}")
    print(f"  {'Misc:':<30} ${MISC_MONTHLY:>8}")
    print(f"  {'-'*40}")
    print(f"  {'TOTAL MONTHLY FIXED COSTS:':<30} ${fixed_costs:>8}")

    print(f"\n  CAPACITY")
    print(f"  {'Total hours/month:':<30} {total_monthly_hours:>8}")
    print(f"  {'Billable hours (60%):':<30} {billable_hours:>8}")
    print(f"  {'Non-billable (sales/admin):':<30} {total_monthly_hours - billable_hours:>8}")

    results = []
    for name, eng in ENGAGEMENTS.items():
        r = calc_engagement(name, eng)
        results.append(r)

    print(f"\n{'=' * 70}")
    print("  ENGAGEMENT PROFITABILITY BREAKDOWN")
    print(f"{'=' * 70}")

    for r in results:
        print(f"\n  --- {r['engagement']} ---")
        print(f"  {r['description']}")
        print(f"  {'Records:':<30} {r['records']:>10,}")
        print(f"  {'Price charged:':<30} ${r['price_charged']:>9,}")
        print(f"  {'Your hours:':<30} {r['total_hours']:>10}")
        print(f"  {'Enrichment cost:':<30} ${r['enrichment_cost']:>9,.2f}")
        print(f"  {'Gross profit:':<30} ${r['gross_profit']:>9,.2f}")
        print(f"  {'Effective $/hour:':<30} ${r['effective_hourly_rate']:>9,.2f}")
        print()
        print(f"  Hours breakdown:")
        for task, hrs in r["hours_breakdown"].items():
            label = task.replace("_", " ").title()
            print(f"    {label:<40} {hrs:>5.1f}h")

    print(f"\n{'=' * 70}")
    print("  MONTHLY SCENARIO MODELING")
    print(f"{'=' * 70}")

    scenarios = [
        {
            "name": "Month 1 (Getting Started)",
            "mix": [
                ("Free Assessment (Door Opener)", 3),
                ("Basic Pilot (Tier 1)", 1),
            ]
        },
        {
            "name": "Month 3 (Building Pipeline)",
            "mix": [
                ("Free Assessment (Door Opener)", 2),
                ("Basic Pilot (Tier 1)", 1),
                ("Standard Pilot (Tier 2)", 1),
            ]
        },
        {
            "name": "Month 6 (Cruising)",
            "mix": [
                ("Standard Pilot (Tier 2)", 1),
                ("Monthly Retainer (Basic)", 2),
                ("Monthly Retainer (Standard)", 1),
            ]
        },
        {
            "name": "Month 12 (Scaled)",
            "mix": [
                ("Enterprise Pilot (Tier 3)", 1),
                ("Monthly Retainer (Basic)", 2),
                ("Monthly Retainer (Standard)", 2),
            ]
        },
    ]

    for scenario in scenarios:
        total_hours_used = 0
        total_revenue = 0
        total_enrich_cost = 0

        print(f"\n  --- {scenario['name']} ---")
        for eng_name, qty in scenario["mix"]:
            r = calc_engagement(eng_name, ENGAGEMENTS[eng_name])
            hours = r["total_hours"] * qty
            rev = r["price_charged"] * qty
            ecost = r["enrichment_cost"] * qty
            total_hours_used += hours
            total_revenue += rev
            total_enrich_cost += ecost
            print(f"    {qty}x {eng_name:<40} {hours:>5.1f}h  ${rev:>8,}")

        net_profit = total_revenue - total_enrich_cost - fixed_costs
        utilization = round(total_hours_used / billable_hours * 100, 1)
        eff_rate = round(net_profit / max(total_hours_used, 1), 2)

        print(f"    {'─' * 60}")
        print(f"    {'Total hours:':<40} {total_hours_used:>5.1f}h  ({utilization}% of capacity)")
        print(f"    {'Gross revenue:':<40}         ${total_revenue:>8,}")
        print(f"    {'Enrichment costs:':<40}         ${total_enrich_cost:>8,.0f}")
        print(f"    {'Fixed overhead:':<40}         ${fixed_costs:>8,}")
        print(f"    {'NET PROFIT:':<40}         ${net_profit:>8,.0f}")
        print(f"    {'Net $/hour:':<40}         ${eff_rate:>8,.2f}")

    # Save full results as JSON
    report_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "reports")
    os.makedirs(report_dir, exist_ok=True)
    output = {
        "fixed_monthly_costs": {
            "cursor": CURSOR_MONTHLY,
            "enrichment_tool": ENRICHMENT_TOOL_MONTHLY,
            "hosting": HOSTING_TOOLS_MONTHLY,
            "travel": TRAVEL_MONTHLY,
            "misc": MISC_MONTHLY,
            "total": fixed_costs,
        },
        "capacity": {
            "total_hours_month": total_monthly_hours,
            "billable_hours_month": billable_hours,
        },
        "engagements": results,
    }
    path = os.path.join(report_dir, "profitability_model.json")
    with open(path, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\n{'=' * 70}")
    print(f"  Full model saved: {path}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    main()
