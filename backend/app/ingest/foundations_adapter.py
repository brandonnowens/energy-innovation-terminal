"""
Philanthropic Foundations & Climate Non-Profits Ingestion Adapter.

Ingests major philanthropic foundations, catalytic non-profit climate funds,
and charitable grantmakers funding energy innovation, clean tech deployment,
and grid decarbonization.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.organization import Organization
from app.models.program import Program
from app.models.opportunity import Opportunity, OpportunityCategory, EligibilityRule
from app.models.award import Award
from app.models.recipient import Recipient

logger = logging.getLogger("FoundationsAdapter")

FOUNDATIONS_DATA: List[Dict[str, Any]] = [
    # ── 1. THE ROCKEFELLER FOUNDATION ──
    {
        "organization": {
            "name": "The Rockefeller Foundation",
            "aliases_json": ["Rockefeller Foundation", "The Rockefeller Foundation", "Global Energy Alliance for People and Planet", "GEAPP"],
            "org_type": "foundation",
            "website": "https://www.rockefellerfoundation.org",
            "domain": "rockefellerfoundation.org",
            "city": "New York",
            "state": "NY",
            "country": "US",
            "geographic_scope": "global",
            "description": "Pioneering philanthropic institution investing catalytic capital in clean energy transitions, community microgrids, and the Global Energy Alliance for People and Planet (GEAPP).",
            "founded_year": 1913
        },
        "programs": [
            {
                "name": "Global Energy Alliance for People and Planet (GEAPP) Innovation Fund",
                "description": "Multi-billion-dollar global clean energy acceleration initiative driving renewable microgrids, battery storage, and distributed energy access.",
                "program_type": "grant",
                "target_stage": "deployment",
                "url": "https://www.energyalliance.org"
            },
            {
                "name": "Rockefeller Zero-Carbon Community Microgrid Initiative",
                "description": "Philanthropic grant program supporting resilient solar-plus-storage microgrids and clean power access for underserved urban and rural communities.",
                "program_type": "grant",
                "target_stage": "demonstration",
                "url": "https://www.rockefellerfoundation.org/initiative/power-energy"
            },
            {
                "name": "Catalytic Climate Finance Facility",
                "description": "Innovative financial structuring and non-dilutive grant facility accelerating early commercial scale-up of energy transition technologies.",
                "program_type": "grant",
                "target_stage": "commercialization",
                "url": "https://www.rockefellerfoundation.org/climate"
            }
        ],
        "opportunities": [
            {
                "solicitation_number": "ROCKEFELLER-GEAPP-2025",
                "name": "Global Energy Alliance for People and Planet Innovation Grant",
                "short_description": "Catalytic grant funding for innovative distributed renewable energy generation, battery storage, and microgrid management platforms.",
                "total_funding": 50000000.0,
                "max_per_award": 5000000.0,
                "award_min": 500000.0,
                "status": "open",
                "solicitation_type": "Philanthropic Grant",
                "enrollment_type": "Open Call / Rolling",
                "due_date_display": "December 31, 2026",
                "technology_area": "Clean Microgrids & Grid-Edge Optimization",
                "url": "https://www.energyalliance.org/innovation-fund"
            },
            {
                "solicitation_number": "ROCKEFELLER-MICROGRID-2025",
                "name": "Distributed Clean Energy Microgrid & Storage Deployment Grant",
                "short_description": "Capital grants for municipal and community microgrids integrating local solar PV, flow batteries, and intelligent load-shedding control.",
                "total_funding": 25000000.0,
                "max_per_award": 2500000.0,
                "award_min": 250000.0,
                "status": "open",
                "solicitation_type": "Philanthropic Grant",
                "enrollment_type": "Rolling Submission",
                "due_date_display": "November 30, 2026",
                "technology_area": "Energy Storage & Advanced Batteries",
                "url": "https://www.rockefellerfoundation.org/grants"
            },
            {
                "solicitation_number": "ROCKEFELLER-CLIMATE-CATALYST-2025",
                "name": "Catalytic Climate Finance & Transition Innovation Facility",
                "short_description": "Subsidized first-loss grant capital and project preparation funds for breakthrough clean tech hardware and energy infrastructure.",
                "total_funding": 30000000.0,
                "max_per_award": 3000000.0,
                "award_min": 500000.0,
                "status": "open",
                "solicitation_type": "Catalytic Finance Facility",
                "enrollment_type": "Rolling Review",
                "due_date_display": "December 15, 2026",
                "technology_area": "Clean Energy Innovation & Advanced Tech",
                "url": "https://www.rockefellerfoundation.org/catalytic-capital"
            }
        ]
    },

    # ── 2. BLOOMBERG PHILANTHROPIES ──
    {
        "organization": {
            "name": "Bloomberg Philanthropies",
            "aliases_json": ["Bloomberg Philanthropies", "Beyond Carbon", "Michael R. Bloomberg Foundation"],
            "org_type": "foundation",
            "website": "https://www.bloomberg.org",
            "domain": "bloomberg.org",
            "city": "New York",
            "state": "NY",
            "country": "US",
            "geographic_scope": "national",
            "description": "Major philanthropic platform leading the $500M+ Beyond Carbon campaign, clean power acceleration, and municipal building decarbonization.",
            "founded_year": 2006
        },
        "programs": [
            {
                "name": "Beyond Carbon Clean Energy Transition Initiative",
                "description": "Largest-ever philanthropic campaign in the US to accelerate 100% clean electricity generation, stop new gas buildouts, and modernize transmission.",
                "program_type": "grant",
                "target_stage": "deployment",
                "url": "https://www.bloomberg.org/environment/beyond-carbon"
            },
            {
                "name": "American Cities Clean Energy Transformation Program",
                "description": "Grants and technical capacity funding for city-wide thermal electrification, heat pump rollouts, and municipal solar power installations.",
                "program_type": "grant",
                "target_stage": "deployment",
                "url": "https://www.bloomberg.org/environment"
            }
        ],
        "opportunities": [
            {
                "solicitation_number": "BLOOMBERG-BEYOND-CARBON-2025",
                "name": "Beyond Carbon Clean Energy Innovation & Grid Decarbonization Grant",
                "short_description": "Non-dilutive grant funding for grid modeling tools, dynamic line rating demonstrations, and advanced clean power deployment coalitions.",
                "total_funding": 100000000.0,
                "max_per_award": 10000000.0,
                "award_min": 1000000.0,
                "status": "open",
                "solicitation_type": "Philanthropic Grant",
                "enrollment_type": "Annual Cycle",
                "due_date_display": "December 31, 2026",
                "technology_area": "Grid Modernization & Smart Power",
                "url": "https://www.bloomberg.org/environment/beyond-carbon"
            },
            {
                "solicitation_number": "BLOOMBERG-CITIES-2025",
                "name": "American Cities Clean Energy & Heat Pump Transformation Initiative",
                "short_description": "Direct deployment grants helping municipalities electrify district heating networks, municipal buildings, and transit facilities.",
                "total_funding": 40000000.0,
                "max_per_award": 4000000.0,
                "award_min": 500000.0,
                "status": "open",
                "solicitation_type": "Municipal Deployment Grant",
                "enrollment_type": "Rolling Submission",
                "due_date_display": "October 31, 2026",
                "technology_area": "Building Decarbonization & Efficiency",
                "url": "https://www.bloomberg.org/environment"
            }
        ]
    },

    # ── 3. BEZOS EARTH FUND ──
    {
        "organization": {
            "name": "Bezos Earth Fund",
            "aliases_json": ["Bezos Earth Fund", "Earth Fund"],
            "org_type": "foundation",
            "website": "https://www.bezosearthfund.org",
            "domain": "bezosearthfund.org",
            "city": "Washington",
            "state": "DC",
            "country": "US",
            "geographic_scope": "global",
            "description": "$10B commitment funding climate solutions, industrial decarbonization, green hydrogen, and advanced greenhouse gas tracking.",
            "founded_year": 2020
        },
        "programs": [
            {
                "name": "Industrial Decarbonization & Clean Fuels Initiative",
                "description": "Catalytic funding targeting zero-emission cement, low-carbon steel, green hydrogen, and sustainable alternative fuels.",
                "program_type": "grant",
                "target_stage": "r_and_d",
                "url": "https://www.bezosearthfund.org/our-programs/climate"
            },
            {
                "name": "Methane Abatement & Remote Sensing Grant Program",
                "description": "Funding global satellite tracking (MethaneSAT) and agricultural/landfill methane reduction technologies.",
                "program_type": "grant",
                "target_stage": "demonstration",
                "url": "https://www.bezosearthfund.org"
            }
        ],
        "opportunities": [
            {
                "solicitation_number": "BEZOS-EARTH-IND-2025",
                "name": "Zero-Carbon Cement, Steel & Industrial Decarbonization Challenge",
                "short_description": "Targeted multi-million-dollar grants for electro-calcination cement pilots, molten oxide electrolysis steelmaking, and clean heat.",
                "total_funding": 75000000.0,
                "max_per_award": 15000000.0,
                "award_min": 2000000.0,
                "status": "open",
                "solicitation_type": "Catalytic Challenge Grant",
                "enrollment_type": "Competitive RFP",
                "due_date_display": "December 31, 2026",
                "technology_area": "Industrial Decarbonization & Clean Heat",
                "url": "https://www.bezosearthfund.org/grants"
            },
            {
                "solicitation_number": "BEZOS-METHANE-2025",
                "name": "Global Methane Detection & Industrial Gas Abatement Initiative",
                "short_description": "Grant funding for sensor systems, point-source flare elimination, and advanced bio-methane destruction bio-filters.",
                "total_funding": 45000000.0,
                "max_per_award": 5000000.0,
                "award_min": 1000000.0,
                "status": "open",
                "solicitation_type": "Research & Deployment Grant",
                "enrollment_type": "Rolling Review",
                "due_date_display": "November 30, 2026",
                "technology_area": "Industrial Decarbonization & Clean Heat",
                "url": "https://www.bezosearthfund.org"
            }
        ]
    },

    # ── 4. WILLIAM AND FLORA HEWLETT FOUNDATION ──
    {
        "organization": {
            "name": "The Hewlett Foundation",
            "aliases_json": ["The Hewlett Foundation", "William and Flora Hewlett Foundation", "Hewlett Foundation"],
            "org_type": "foundation",
            "website": "https://www.hewlett.org",
            "domain": "hewlett.org",
            "city": "Menlo Park",
            "state": "CA",
            "country": "US",
            "geographic_scope": "national",
            "description": "One of the nation's largest climate grantmakers providing over $600M in long-term grants for clean energy, power sector transformation, and industrial transition.",
            "founded_year": 1966
        },
        "programs": [
            {
                "name": "Climate and Clean Energy Program",
                "description": "Dedicated funding supporting national power sector decarbonization, clean grid integration, and zero-emission heavy transport.",
                "program_type": "grant",
                "target_stage": "deployment",
                "url": "https://www.hewlett.org/programs/environment"
            }
        ],
        "opportunities": [
            {
                "solicitation_number": "HEWLETT-CLEAN-GRID-2025",
                "name": "National Power Sector Decarbonization & Grid Integration Grant",
                "short_description": "Philanthropic grants supporting clean power market design, transmission expansion modeling, and distributed energy resource aggregation.",
                "total_funding": 60000000.0,
                "max_per_award": 6000000.0,
                "award_min": 500000.0,
                "status": "open",
                "solicitation_type": "Philanthropic Grant",
                "enrollment_type": "Open Inquiry",
                "due_date_display": "December 31, 2026",
                "technology_area": "Grid Modernization & Smart Power",
                "url": "https://www.hewlett.org/grants"
            }
        ]
    },

    # ── 5. PRIME COALITION & PRIME IMPACT FUND ──
    {
        "organization": {
            "name": "Prime Coalition",
            "aliases_json": ["Prime Coalition", "Prime Impact Fund", "Azolla Ventures", "Project Frame"],
            "org_type": "non_profit",
            "website": "https://www.primecoalition.org",
            "domain": "primecoalition.org",
            "city": "Cambridge",
            "state": "MA",
            "country": "US",
            "geographic_scope": "national",
            "description": "Non-profit public charity steering catalytic capital from foundations and philanthropists into early-stage tough tech clean energy ventures with gigaton-scale abatement potential.",
            "founded_year": 2014
        },
        "programs": [
            {
                "name": "Catalytic Climate Tough Tech Program",
                "description": "Patient, catalytic early-stage non-dilutive and hybrid equity financing for high-risk, high-impact climate hardware.",
                "program_type": "grant",
                "target_stage": "r_and_d",
                "url": "https://www.primecoalition.org/programs"
            }
        ],
        "opportunities": [
            {
                "solicitation_number": "PRIME-IMPACT-2025",
                "name": "Catalytic Tough Tech Non-Dilutive & Patient Capital Grant",
                "short_description": "Early-stage non-dilutive proof-of-concept grants for breakthrough innovations in fusion, long-duration storage, green hydrogen, and carbon mineralization.",
                "total_funding": 20000000.0,
                "max_per_award": 2000000.0,
                "award_min": 250000.0,
                "status": "open",
                "solicitation_type": "Catalytic Grant",
                "enrollment_type": "Rolling Submission",
                "due_date_display": "December 31, 2026",
                "technology_area": "Clean Energy Innovation & Advanced Tech",
                "url": "https://www.primecoalition.org"
            }
        ]
    },

    # ── 6. ELEMENTAL EXCELERATOR ──
    {
        "organization": {
            "name": "Elemental Excelerator",
            "aliases_json": ["Elemental Excelerator", "Elemental Climate Accelerator"],
            "org_type": "non_profit",
            "website": "https://elementalexcelerator.com",
            "domain": "elementalexcelerator.com",
            "city": "Honolulu",
            "state": "HI",
            "country": "US",
            "geographic_scope": "national",
            "description": "Non-profit climate tech accelerator deploying equity-free project deployment grants ($1M-$3M per company) to scale first-of-a-kind (FOAK) clean energy projects.",
            "founded_year": 2009
        },
        "programs": [
            {
                "name": "First-of-a-Kind (FOAK) Climate Tech Project Deployment",
                "description": "Equity-free project finance grants helping hardware clean tech startups validate commercial installations with customers.",
                "program_type": "grant",
                "target_stage": "deployment",
                "url": "https://elementalexcelerator.com/programs"
            }
        ],
        "opportunities": [
            {
                "solicitation_number": "ELEMENTAL-DEPLOY-2025",
                "name": "Climate Tech FOAK Project Commercial Deployment & Equity-Free Grant",
                "short_description": "Direct equity-free non-dilutive grants of up to $3M per company to construct first-of-a-kind commercial pilots in frontline communities.",
                "total_funding": 15000000.0,
                "max_per_award": 3000000.0,
                "award_min": 1000000.0,
                "status": "open",
                "solicitation_type": "Project Deployment Grant",
                "enrollment_type": "Cohort Application",
                "due_date_display": "October 15, 2026",
                "technology_area": "Clean Transportation & Heavy Mobility",
                "url": "https://elementalexcelerator.com/apply"
            }
        ]
    },

    # ── 7. BREAKTHROUGH ENERGY FOUNDATION / CATALYST ──
    {
        "organization": {
            "name": "Breakthrough Energy Foundation",
            "aliases_json": ["Breakthrough Energy Foundation", "Breakthrough Energy Catalyst", "Breakthrough Energy Fellows"],
            "org_type": "foundation",
            "website": "https://breakthroughenergy.org",
            "domain": "breakthroughenergy.org",
            "city": "Kirkland",
            "state": "WA",
            "country": "US",
            "geographic_scope": "global",
            "description": "Philanthropic and catalytic capital branch of Breakthrough Energy funding Fellows, Exploratory Science, and large-scale Catalyst demonstration grants.",
            "founded_year": 2015
        },
        "programs": [
            {
                "name": "Breakthrough Energy Catalyst Commercial Scale-Up Facility",
                "description": "Catalytic philanthropic grants and patient equity to bridge the green premium in SAF, Direct Air Capture, Green Hydrogen, and Long-Duration Storage.",
                "program_type": "grant",
                "target_stage": "commercialization",
                "url": "https://breakthroughenergy.org/catalyst"
            },
            {
                "name": "Breakthrough Energy Fellows",
                "description": "Non-dilutive research and stipend funding for early-stage scientists commercializing tough tech clean energy breakthroughs.",
                "program_type": "grant",
                "target_stage": "r_and_d",
                "url": "https://breakthroughenergy.org/fellows"
            }
        ],
        "opportunities": [
            {
                "solicitation_number": "BEV-CATALYST-FOAK-2025",
                "name": "Breakthrough Energy Catalyst Commercial Demonstration Grant",
                "short_description": "Large-scale philanthropic grants designed to absorb early commercial risk and finance first-of-a-kind clean energy manufacturing facilities.",
                "total_funding": 150000000.0,
                "max_per_award": 50000000.0,
                "award_min": 5000000.0,
                "status": "open",
                "solicitation_type": "Catalytic Demonstration Grant",
                "enrollment_type": "Direct Inquiry",
                "due_date_display": "December 31, 2026",
                "technology_area": "Hydrogen & Clean Fuel Cells",
                "url": "https://breakthroughenergy.org/catalyst"
            },
            {
                "solicitation_number": "BEV-FELLOWS-COHORT-5",
                "name": "Breakthrough Energy Fellows Innovator & Discovery Grant",
                "short_description": "Fully funded non-dilutive research grants, lab access, and mentorship for deep tech energy entrepreneurs.",
                "total_funding": 25000000.0,
                "max_per_award": 1500000.0,
                "award_min": 250000.0,
                "status": "open",
                "solicitation_type": "Fellowship Grant",
                "enrollment_type": "Annual Cohort",
                "due_date_display": "September 30, 2026",
                "technology_area": "Clean Energy Innovation & Advanced Tech",
                "url": "https://breakthroughenergy.org/fellows"
            }
        ]
    },

    # ── 8. JOHN D. AND CATHERINE T. MACARTHUR FOUNDATION ──
    {
        "organization": {
            "name": "MacArthur Foundation",
            "aliases_json": ["MacArthur Foundation", "John D. and Catherine T. MacArthur Foundation"],
            "org_type": "foundation",
            "website": "https://www.macfound.org",
            "domain": "macfound.org",
            "city": "Chicago",
            "state": "IL",
            "country": "US",
            "geographic_scope": "national",
            "description": "Major philanthropic foundation funding climate solutions, the Catalytic Capital Consortium (C3), and clean power sector transition.",
            "founded_year": 1970
        },
        "programs": [
            {
                "name": "Climate Solutions & Catalytic Capital Consortium (C3)",
                "description": "Philanthropic program deploying catalytic grants to unlock private investment in climate resilience and renewable power systems.",
                "program_type": "grant",
                "target_stage": "deployment",
                "url": "https://www.macfound.org/programs/climate"
            }
        ],
        "opportunities": [
            {
                "solicitation_number": "MACARTHUR-C3-2025",
                "name": "Catalytic Capital Consortium Clean Energy Deployment Challenge",
                "short_description": "Non-dilutive grant funding supporting innovative financial instruments and community clean energy projects.",
                "total_funding": 50000000.0,
                "max_per_award": 5000000.0,
                "award_min": 500000.0,
                "status": "open",
                "solicitation_type": "Philanthropic Grant",
                "enrollment_type": "Open Request for Proposals",
                "due_date_display": "December 31, 2026",
                "technology_area": "Clean Energy Innovation & Advanced Tech",
                "url": "https://www.macfound.org/grants"
            }
        ]
    },

    # ── 9. THE MCKNIGHT FOUNDATION ──
    {
        "organization": {
            "name": "The McKnight Foundation",
            "aliases_json": ["The McKnight Foundation", "McKnight Foundation"],
            "org_type": "foundation",
            "website": "https://www.mcknight.org",
            "domain": "mcknight.org",
            "city": "Minneapolis",
            "state": "MN",
            "country": "US",
            "geographic_scope": "regional",
            "description": "Midwest philanthropic foundation funding regional grid decarbonization, clean heat, and equitable clean energy transition.",
            "founded_year": 1953
        },
        "programs": [
            {
                "name": "Midwest Clean Energy & Climate Program",
                "description": "Regional grant initiative funding clean electricity generation, electric transmission expansion, and building decarb across the Upper Midwest.",
                "program_type": "grant",
                "target_stage": "deployment",
                "url": "https://www.mcknight.org/programs/midwest-climate-energy"
            }
        ],
        "opportunities": [
            {
                "solicitation_number": "MCKNIGHT-MIDWEST-2025",
                "name": "Midwest Clean Energy Innovation & Regional Grid Resilience Grant",
                "short_description": "Grants accelerating renewable energy integration, battery storage, and transmission line optimization across MISO states.",
                "total_funding": 20000000.0,
                "max_per_award": 2000000.0,
                "award_min": 250000.0,
                "status": "open",
                "solicitation_type": "Regional Grant",
                "enrollment_type": "Bi-Annual Cycle",
                "due_date_display": "November 15, 2026",
                "technology_area": "Grid Modernization & Smart Power",
                "url": "https://www.mcknight.org/grants"
            }
        ]
    },

    # ── 10. THE KRESGE FOUNDATION ──
    {
        "organization": {
            "name": "The Kresge Foundation",
            "aliases_json": ["The Kresge Foundation", "Kresge Foundation"],
            "org_type": "foundation",
            "website": "https://kresge.org",
            "domain": "kresge.org",
            "city": "Troy",
            "state": "MI",
            "country": "US",
            "geographic_scope": "national",
            "description": "National foundation funding resilient community microgrids, urban thermal electrification, and climate justice clean tech deployments.",
            "founded_year": 1924
        },
        "programs": [
            {
                "name": "Environment & Resilient Community Microgrids",
                "description": "Funding urban solar-plus-storage microgrids and clean thermal energy systems for affordable housing and community hubs.",
                "program_type": "grant",
                "target_stage": "deployment",
                "url": "https://kresge.org/our-work/environment"
            }
        ],
        "opportunities": [
            {
                "solicitation_number": "KRESGE-CLEAN-COMM-2025",
                "name": "Community Clean Energy Resilience & Solar-Storage Microgrid Grant",
                "short_description": "Capital grants for low-income community microgrids, backup battery systems, and electric heat pump retrofits.",
                "total_funding": 15000000.0,
                "max_per_award": 1500000.0,
                "award_min": 200000.0,
                "status": "open",
                "solicitation_type": "Community Capital Grant",
                "enrollment_type": "Rolling Submission",
                "due_date_display": "October 31, 2026",
                "technology_area": "Clean Microgrids & Grid-Edge Optimization",
                "url": "https://kresge.org/grants"
            }
        ]
    },

    # ── 11. BARR FOUNDATION ──
    {
        "organization": {
            "name": "Barr Foundation",
            "aliases_json": ["Barr Foundation"],
            "org_type": "foundation",
            "website": "https://www.barrfoundation.org",
            "domain": "barrfoundation.org",
            "city": "Boston",
            "state": "MA",
            "country": "US",
            "geographic_scope": "regional",
            "description": "Boston-based foundation focusing on climate solutions, building thermal decarbonization, clean transportation, and clean power in New England.",
            "founded_year": 1997
        },
        "programs": [
            {
                "name": "Clean Energy & Thermal Electrification Initiative",
                "description": "Philanthropic grants accelerating offshore wind integration, networked geothermal heat pumps, and electric transit buses.",
                "program_type": "grant",
                "target_stage": "deployment",
                "url": "https://www.barrfoundation.org/climate"
            }
        ],
        "opportunities": [
            {
                "solicitation_number": "BARR-CLEAN-ENERGY-2025",
                "name": "Northeast Building Electrification & Clean Energy Innovation Grant",
                "short_description": "Funding community ground-source heat pump loops, offshore wind supply chain development, and heavy vehicle charging.",
                "total_funding": 15000000.0,
                "max_per_award": 1500000.0,
                "award_min": 200000.0,
                "status": "open",
                "solicitation_type": "Regional Initiative Grant",
                "enrollment_type": "Rolling Submission",
                "due_date_display": "December 15, 2026",
                "technology_area": "Building Decarbonization & Efficiency",
                "url": "https://www.barrfoundation.org/grants"
            }
        ]
    }
]


class FoundationsAdapter:
    """Ingests philanthropic foundations and climate non-profits into the database."""

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    def ingest(self, db: Session) -> Dict[str, Any]:
        orgs_added = 0
        progs_added = 0
        opps_added = 0
        opps_updated = 0

        for f_data in FOUNDATIONS_DATA:
            o_info = f_data["organization"]
            org = db.query(Organization).filter_by(name=o_info["name"]).first()
            if not org:
                org = Organization(
                    name=o_info["name"],
                    aliases_json=o_info.get("aliases_json", [o_info["name"]]),
                    org_type=o_info.get("org_type", "foundation"),
                    website=o_info.get("website"),
                    domain=o_info.get("domain"),
                    city=o_info.get("city"),
                    state=o_info.get("state"),
                    country=o_info.get("country", "US"),
                    geographic_scope=o_info.get("geographic_scope", "national"),
                    description=o_info.get("description"),
                    founded_year=o_info.get("founded_year"),
                    is_verified=True,
                    data_provenance="foundations_registry"
                )
                db.add(org)
                db.flush()
                orgs_added += 1

            # Ingest Programs
            prog_map = {}
            for p_info in f_data.get("programs", []):
                prog = db.query(Program).filter_by(name=p_info["name"]).first()
                if not prog:
                    prog = Program(
                        name=p_info["name"],
                        description=p_info.get("description"),
                        program_type=p_info.get("program_type", "grant"),
                        target_stage=p_info.get("target_stage", "deployment"),
                        url=p_info.get("url")
                    )
                    db.add(prog)
                    db.flush()
                    progs_added += 1
                prog_map[prog.name] = prog.id

            # Ingest Opportunities
            prog_list = f_data.get("programs", [])
            for opp_idx, opp_data in enumerate(f_data.get("opportunities", [])):
                target_prog_id = None
                if opp_idx < len(prog_list):
                    target_prog_id = prog_map.get(prog_list[opp_idx]["name"])
                elif prog_list:
                    target_prog_id = prog_map.get(prog_list[0]["name"])

                opp = db.query(Opportunity).filter_by(solicitation_number=opp_data["solicitation_number"]).first()

                if not opp:
                    opp = Opportunity(
                        solicitation_number=opp_data["solicitation_number"],
                        name=opp_data["name"],
                        agency=org.name,
                        agency_code=org.name[:10].upper(),
                        jurisdiction="foundation",
                        org_type="foundation",
                        organization_id=org.id,
                        program_id=target_prog_id,
                        short_description=opp_data.get("short_description"),
                        total_funding=opp_data.get("total_funding"),
                        max_per_award=opp_data.get("max_per_award"),
                        award_min=opp_data.get("award_min"),
                        status=opp_data.get("status", "open"),
                        solicitation_type=opp_data.get("solicitation_type", "Grant"),
                        enrollment_type=opp_data.get("enrollment_type", "Open Enrollment"),
                        due_date_display=opp_data.get("due_date_display"),
                        detail_page_url=opp_data.get("url"),
                        cost_share_pct=0.0
                    )

                    db.add(opp)
                    db.flush()

                    # Add Category
                    if opp_data.get("technology_area"):
                        cat = OpportunityCategory(
                            opportunity_id=opp.id,
                            category_type="technology",
                            category_value=opp_data["technology_area"],
                            confidence=1.0
                        )
                        db.add(cat)

                    # Add Eligibility
                    rule = EligibilityRule(
                        opportunity_id=opp.id,
                        rule_type="applicant",
                        rule_key="entity_type",
                        rule_value="All Organizations / Universities / Non-Profits",
                        is_hard_requirement=True
                    )
                    db.add(rule)

                    opps_added += 1
                else:
                    opp.name = opp_data["name"]
                    opp.short_description = opp_data.get("short_description")
                    opp.total_funding = opp_data.get("total_funding")
                    opp.organization_id = org.id
                    if target_prog_id:
                        opp.program_id = target_prog_id
                    opp.status = opp_data.get("status", "open")
                    opp.due_date_display = opp_data.get("due_date_display")
                    opps_updated += 1

        db.commit()
        logger.info(f"Foundations Ingestion: Orgs Added={orgs_added}, Progs Added={progs_added}, Opps Added={opps_added}, Opps Updated={opps_updated}")
        return {
            "organizations_added": orgs_added,
            "programs_added": progs_added,
            "opportunities_added": opps_added,
            "opportunities_updated": opps_updated
        }
