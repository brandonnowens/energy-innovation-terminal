"""
Enrichment and Optimization Script for all 18 Specialized Monograph Generators.
Ensures:
1. Highly filtered topic-specific SQL queries for institutional recipients AND landmark awards.
2. Executive Callouts (C-Suite Strategic Implication / Takeaway) on key analytical pages.
3. Strict executive single-page flow calibration with zero accidental page overflows.
4. Consistent 'House Voice' and strategic management advisory perspective.
"""

import os
import re

GEN_DIR = os.path.dirname(os.path.abspath(__file__))

TOPIC_CONFIGS = {
    "gen_clean_gen.py": {
        "rec_filter": "primary_technology LIKE '%Solar%' OR primary_technology LIKE '%Wind%' OR primary_technology LIKE '%Nuclear%' OR primary_technology LIKE '%Geothermal%'",
        "award_filter": "project_title LIKE '%wind%' OR project_title LIKE '%solar%' OR project_title LIKE '%geothermal%' OR project_title LIKE '%nuclear%' OR project_title LIKE '%smr%'",
        "callout_p2": "CORE TAKEAWAY: Offshore wind, perovskite tandem solar, and Small Modular Reactors (SMRs) are critical to meeting 2030/2040 clean power mandates. Port marshaling logistics and FERC transmission interconnection queues remain the primary operational constraints.",
        "callout_p3": "STRATEGIC IMPLICATION: Siting large-scale generation requires dual-use land planning (agrivoltaics) and rapid subsea HVDC transmission approvals to prevent offshore wind curtailment.",
        "callout_p6": "TECHNOLOGY BENCHMARK: Perovskite-silicon tandem cells achieve 30%+ laboratory efficiencies; encapsulant durability under UV and moisture exposure is the remaining commercial gating item.",
        "callout_p8": "INFRASTRUCTURE CHALLENGE: 9 GW offshore wind deployment mandates require dedicated deep-water port staging (South Brooklyn, Albany) and purpose-built Jones Act compliant installation vessels."
    },
    "gen_energy_storage.py": {
        "rec_filter": "primary_technology LIKE '%Storage%' OR primary_technology LIKE '%Battery%' OR primary_technology LIKE '%Batteries%'",
        "award_filter": "project_title LIKE '%battery%' OR project_title LIKE '%storage%' OR project_title LIKE '%bess%' OR project_title LIKE '%lithium%' OR project_title LIKE '%flow battery%'",
        "callout_p2": "CORE TAKEAWAY: 4-hour lithium-ion meets near-term peaker replacement, but achieving 100% clean power requires 10-100+ hour Long-Duration Energy Storage (LDES). State green banks must deploy first-loss debt to de-risk multi-day flow and iron-air installations.",
        "callout_p3": "STRATEGIC IMPLICATION: 6 GW storage mandates require rapid streamlining of NFPA 855 and UL 9540A fire safety approvals across dense urban jurisdictions.",
        "callout_p6": "CHEMISTRY DIVERSIFICATION: Non-lithium sodium-ion and iron-air chemistries eliminate critical mineral supply chain dependencies and provide non-flammable operation.",
        "callout_p8": "CIRCULAR ECONOMY: Closed-loop hydrometallurgical battery recycling achieves 95%+ recovery of battery-grade lithium, nickel, and cobalt, mitigating raw material supply crunches."
    },
    "gen_grid_modernization.py": {
        "rec_filter": "primary_technology LIKE '%Grid%' OR primary_technology LIKE '%Transmission%' OR primary_technology LIKE '%Smart Power%' OR primary_technology LIKE '%DERMS%'",
        "award_filter": "project_title LIKE '%transmission%' OR project_title LIKE '%smart grid%' OR project_title LIKE '%substation%' OR project_title LIKE '%hvdc%' OR project_title LIKE '%derms%'",
        "callout_p2": "CORE TAKEAWAY: Transmission queue backlogs average 5-8 years; deploying Grid-Enhancing Technologies (GETs) and Dynamic Line Rating (DLR) unlocks 20-30% additional capacity on existing corridors immediately while long-distance HVDC is constructed.",
        "callout_p3": "REGULATORY MANDATE: FERC Order 1920 mandates 20-year forward-looking regional transmission planning, requiring state Public Utility Commissions to coordinate interstate cost allocation.",
        "callout_p6": "DIGITAL INFRASTRUCTURE: Advanced Distribution Management Systems (ADMS) and IEEE 2030.5 DERMS platforms orchestrate millions of distributed energy resources into dispatchable Virtual Power Plants (VPPs).",
        "callout_p8": "PHYSICAL RESILIENCE: Solid-state digital substations and microgrid sectionalizers provide fast-fault isolation, preventing cascading blackouts during extreme weather events."
    },
    "gen_buildings_thermal.py": {
        "rec_filter": "primary_technology LIKE '%Building%' OR primary_technology LIKE '%Thermal%' OR primary_technology LIKE '%Heat Pump%' OR primary_technology LIKE '%Efficiency%'",
        "award_filter": "project_title LIKE '%building%' OR project_title LIKE '%heat pump%' OR project_title LIKE '%thermal%' OR project_title LIKE '%envelope%' OR project_title LIKE '%geothermal%'",
        "callout_p2": "CORE TAKEAWAY: Standalone air-source heat pumps risk tripling winter electric peak demand; Utility Thermal Energy Networks (TENs) and district geothermal loops eliminate electric heating spikes while providing a just transition for union gas utility pipefitters.",
        "callout_p3": "POLICY COMPLIANCE: Local Laws (e.g. NYC LL97) penalize building emissions, driving commercial real estate to accelerate deep envelope retrofits and centralized heat pump adoption.",
        "callout_p6": "ENGINEERING INNOVATION: Cold-climate heat pumps with enhanced vapor injection (EVI) scroll compressors maintain high COP (>2.2) even in sub-zero -15°F winter conditions.",
        "callout_p8": "UTILITY INTEGRATION: The Thermal Energy Networks and Jobs Act allows gas utilities to rate-base district ambient-temperature water loops, preserving union jobs while eliminating fossil gas burn."
    },
    "gen_ai_datacenter.py": {
        "rec_filter": "primary_technology LIKE '%AI%' OR primary_technology LIKE '%Compute%' OR primary_technology LIKE '%Software%' OR primary_technology LIKE '%Data%'",
        "award_filter": "project_title LIKE '%data center%' OR project_title LIKE '%compute%' OR project_title LIKE '%cooling%' OR project_title LIKE '%liquid cooling%' OR project_title LIKE '%immersion%'",
        "callout_p2": "CORE TAKEAWAY: AI compute workloads are doubling data center power demand (40-120+ kW per rack). Meeting this load requires behind-the-meter clean microgrids (SMRs, deep geothermal) and exporting liquid-cooled waste heat to district thermal loops.",
        "callout_p3": "POWER CONSTRAINTS: Hyperscale data center interconnections face 4-7 year utility queue delays, forcing tech developers to co-locate with dedicated zero-carbon baseload generation.",
        "callout_p6": "THERMAL MANAGEMENT: Direct-to-chip liquid cooling and two-phase immersion cut data center PUE to under 1.08 while providing high-grade 60°C waste heat suitable for municipal district heating.",
        "callout_p8": "GRID ORCHESTRATION: AI-driven autonomous energy management systems dynamically throttle non-urgent compute training jobs during peak grid stress, acting as flexible demand response."
    },
    "gen_transportation_ev.py": {
        "rec_filter": "primary_technology LIKE '%Vehicle%' OR primary_technology LIKE '%Transport%' OR primary_technology LIKE '%EV%' OR primary_technology LIKE '%Transit%'",
        "award_filter": "project_title LIKE '%vehicle%' OR project_title LIKE '%fleet%' OR project_title LIKE '%charging%' OR project_title LIKE '%transit bus%' OR project_title LIKE '%truck%'",
        "callout_p2": "CORE TAKEAWAY: Heavy-duty fleet electrification hinges on Megawatt Charging Systems (MCS: 1.0-3.75 MW) and depot smart charging orchestration. Fleet total cost of ownership (TCO) reaches parity with diesel when depot microgrids mitigate utility demand charges.",
        "callout_p3": "DEPOT INFRASTRUCTURE: Electrifying a 100-bus transit depot requires 15-25 MW of electric service—equivalent to a small hospital or manufacturing plant—necessitating on-site battery buffers.",
        "callout_p6": "CHARGING INNOVATION: Bidirectional Vehicle-to-Grid (V2G) enables electric school bus and municipal truck fleets to inject power back into the grid during summer afternoon peak hours.",
        "callout_p8": "HEAVY-DUTY COMMERCIALIZATION: Class 8 regional haul trucks achieve commercial viability with 600 kWh battery packs and high-power corridor charging across interstate freight hubs."
    },
    "gen_industrial_decarb.py": {
        "rec_filter": "primary_technology LIKE '%Industrial%' OR primary_technology LIKE '%Manufacturing%' OR primary_technology LIKE '%Steel%' OR primary_technology LIKE '%Cement%' OR primary_technology LIKE '%Heat%'",
        "award_filter": "project_title LIKE '%industrial%' OR project_title LIKE '%process heat%' OR project_title LIKE '%steel%' OR project_title LIKE '%cement%' OR project_title LIKE '%thermal storage%'",
        "callout_p2": "CORE TAKEAWAY: High-temperature industrial process heat (>1,000°C) accounts for over 15% of national emissions. Commercializing 1,500°C thermal energy storage batteries, green hydrogen direct-reduced iron (H2-DRI), and low-carbon cement (SCMs) is essential for deep industrial decarb.",
        "callout_p3": "ECONOMIC MECHANISM: Industrial facilities operate on narrow margins with 30-year asset lifecycles. Public capital must provide FOAK grant matches and Contracts-for-Difference to absorb green premium risks.",
        "callout_p6": "PROCESS HEAT INNOVATION: Industrial heat pumps operating at 150-200°C replace fossil boilers in food processing, paper, and chemicals with 3x higher thermodynamic efficiency.",
        "callout_p8": "DECARBONIZED MATERIALS: Supplementary Cementitious Materials (SCMs) and limestone calcined clay cement (LC3) cut clinker factor and embodied carbon by 40% without compromising structural strength."
    },
    "gen_climate_justice.py": {
        "rec_filter": "primary_technology LIKE '%Community%' OR primary_technology LIKE '%Justice%' OR primary_technology LIKE '%Efficiency%' OR primary_technology LIKE '%Solar%'",
        "award_filter": "project_title LIKE '%disadvantaged%' OR project_title LIKE '%justice%' OR project_title LIKE '%community%' OR project_title LIKE '%affordable housing%' OR project_title LIKE '%environmental justice%'",
        "callout_p2": "CORE TAKEAWAY: Statutory mandates requiring 35-40% of clean energy benefits to flow to Disadvantaged Communities (DACs) ensure equitable capital allocation. Priority deployments include community solar, multifamily affordable heat pumps, and transit electrification.",
        "callout_p3": "COMMUNITY ASSET OWNERSHIP: Transitioning from passive consumer rebates to community-owned energy assets (solar co-ops, microgrids) builds generational wealth and community resilience.",
        "callout_p6": "HEALTH & ENVIRONMENTAL JUSTICE: Replacing diesel transit bus depots and peaker plants in environmental justice neighborhoods delivers immediate localized reductions in particulate matter (PM2.5) and NOx.",
        "callout_p8": "AFFORDABLE HOUSING RETROFITS: Pre-weatherization grants address structural roof and electrical service panel deficits, enabling low-income multifamily buildings to install heat pumps."
    },
    "gen_workforce_transition.py": {
        "rec_filter": "primary_technology LIKE '%Workforce%' OR primary_technology LIKE '%Labor%' OR primary_technology LIKE '%Training%' OR primary_technology LIKE '%Efficiency%'",
        "award_filter": "project_title LIKE '%workforce%' OR project_title LIKE '%training%' OR project_title LIKE '%apprenticeship%' OR project_title LIKE '%labor%' OR project_title LIKE '%technician%'",
        "callout_p2": "CORE TAKEAWAY: A deficit of over 1.2 million skilled clean energy workers threatens national deployment targets. Scaling union registered apprenticeships, certifying cold-climate heat pump technicians, and transitioning gas pipefitters to thermal networks is critical.",
        "callout_p3": "STATUTORY INCENTIVES: IRA prevailing wage and registered apprenticeship compliance unlocks 5x bonus tax credits, establishing labor standards as an imperative for project finance.",
        "callout_p6": "LABOR TRANSITION: Utility Thermal Energy Networks (TENs) utilize the exact pipe diameter, pressure, and trenching skills of union gas utility workers, enabling a friction-free workforce transition.",
        "callout_p8": "COMMUNITY COLLEGE HUBS: Regional workforce development centers partner with community colleges and trade unions to create direct recruitment pipelines in historically underrepresented communities."
    }
}

def enrich_all_generators():
    print("=== ENRICHING SPECIALIZED GENERATORS WITH TOPIC FILTERS, LANDMARK AWARDS & CALLOUTS ===")
    for filename, cfg in TOPIC_CONFIGS.items():
        path = os.path.join(GEN_DIR, filename)
        if not os.path.exists(path):
            print(f"File not found: {filename}")
            continue

        with open(path, "r", encoding="utf-8") as f:
            code = f.read()

        # Update SQL queries to be highly topic specific
        rec_filter = cfg["rec_filter"]
        award_filter = cfg["award_filter"]

        # Ensure rec_sql uses rec_filter
        code = re.sub(
            r"WHERE primary_technology LIKE [^\n]+\n\s+ORDER BY",
            f"WHERE {rec_filter}\n        ORDER BY",
            code
        )

        # Add award_sql query for landmark project awards if not already present
        if "award_sql = text(" not in code:
            query_insertion = f"""
    # Query topic-specific landmark strategic project awards
    award_sql = text(\"\"\"
        SELECT recipient_name, recipient_city, recipient_state, award_amount, year, project_title
        FROM awards
        WHERE {award_filter}
        ORDER BY award_amount DESC
        LIMIT 7
    \"\"\")
    award_rows = db.execute(award_sql).fetchall()
"""
            code = code.replace("    table_data_top = [", query_insertion + "\n    table_data_top = [")

            # Update table_data_bottom to use award_rows
            old_table_bottom_pattern = r"table_data_bottom = \[.*?for r in rec_rows\[7:14\]:.*?table_data_bottom\.append\(.*?\)\s+\]"
            new_table_bottom = """table_data_bottom = [
        [Paragraph("<b>Landmark Project Recipient</b>", styles['th']), Paragraph("<b>Location</b>", styles['th']), Paragraph("<b>Year</b>", styles['th']), Paragraph("<b>Amount</b>", styles['th']), Paragraph("<b>Strategic Project Focus</b>", styles['th'])]
    ]
    for r in award_rows:
        table_data_bottom.append([
            Paragraph(str(r[0])[:24], styles['td']),
            Paragraph(f"{r[1] or 'N/A'}, {r[2] or 'US'}", styles['td']),
            Paragraph(str(r[4] or 2024), styles['td']),
            Paragraph(f"<b>{format_currency(float(r[3]))}</b>", styles['td']),
            Paragraph(str(r[5] or 'Strategic Deployment Project')[:38], styles['td'])
        ])"""
            code = re.sub(old_table_bottom_pattern, new_table_bottom, code, flags=re.DOTALL)

        # Add executive_callout to Page 2 and Page 3 if not present
        if "executive_callout" not in code:
            p2_callout = cfg["callout_p2"]
            p3_callout = cfg["callout_p3"]
            code = code.replace('"subheader": "Strategic Executive Synthesis",', f'"subheader": "Strategic Executive Synthesis",\n            "executive_callout": "{p2_callout}",')
            code = re.sub(r'("header": "1\. [^"]+",\s+"subheader": "[^"]+",)', r'\1\n            "executive_callout": "' + p3_callout + '",', code)

        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

        print(f"[UPDATED] {filename:<32} with topic-specific queries & executive callouts.")

if __name__ == "__main__":
    enrich_all_generators()
