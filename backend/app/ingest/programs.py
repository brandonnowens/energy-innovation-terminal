"""Programs and commercialization data adapter.

Seeds the database with known NYSERDA Innovation and commercialization programs.
These are curated from verified public sources rather than dynamically scraped,
since program information changes infrequently.
"""

import logging
from sqlalchemy.orm import Session

from app.ingest.base import BaseAdapter
from app.models.program import Program, ProgramFocusArea
from app.models.source import IngestionRun, Source

logger = logging.getLogger(__name__)

# Curated program data from verified public sources
INNOVATION_PROGRAMS = [
    {
        "name": "Grid Modernization",
        "program_type": "innovation",
        "description": "Advancing technologies for a modernized, clean energy grid including Grid Enhancing Technologies (GETs), advanced power flow control, AI/ML grid optimization, DER integration, and cybersecurity.",
        "url": "https://www.nyserda.ny.gov/All-Programs/Innovation-at-NYSERDA",
        "contact_email": "smartgrid@nyserda.ny.gov",
        "parent_program": "Technology & Business Innovation",
        "focus_areas": [
            {"focus_area": "Grid Enhancing Technologies (GETs)", "keywords": "advanced conductors,power flow,dynamic line rating,grid sensors,synchrophasor,topology optimization"},
            {"focus_area": "AI/ML Grid Analytics", "keywords": "artificial intelligence,machine learning,grid optimization,predictive analytics,load forecasting"},
            {"focus_area": "DER Integration", "keywords": "distributed energy resources,inverter,microgrid,interconnection,hosting capacity"},
            {"focus_area": "Cybersecurity", "keywords": "cybersecurity,grid security,threat detection,critical infrastructure"},
        ],
    },
    {
        "name": "End-Use Energy Innovation (Buildings)",
        "program_type": "innovation",
        "description": "Next-gen heat pump systems, thermal energy storage, building envelope technologies, cold-climate performance, and intelligent building energy management.",
        "url": "https://www.nyserda.ny.gov/All-Programs/Innovation-at-NYSERDA",
        "contact_email": "innovation@nyserda.ny.gov",
        "parent_program": "Technology & Business Innovation",
        "focus_areas": [
            {"focus_area": "Heat Pump Innovation", "keywords": "heat pump,cold climate,variable speed,geothermal,air source"},
            {"focus_area": "Thermal Energy Storage", "keywords": "thermal storage,phase change,ice storage,thermal battery"},
            {"focus_area": "Building Envelope", "keywords": "insulation,air sealing,windows,building shell,envelope"},
            {"focus_area": "Building Energy Management", "keywords": "building management,smart building,controls,automation,HVAC optimization"},
        ],
    },
    {
        "name": "Advanced Fuels & Thermal Energy Networks",
        "program_type": "innovation",
        "description": "Clean hydrogen, electrolyzers, fuel cells, thermal energy networks (TENs), district geothermal, and renewable natural gas research and demonstration.",
        "url": "https://www.nyserda.ny.gov/All-Programs/Innovation-at-NYSERDA",
        "contact_email": "innovation@nyserda.ny.gov",
        "parent_program": "Technology & Business Innovation",
        "focus_areas": [
            {"focus_area": "Clean Hydrogen", "keywords": "hydrogen,electrolyzer,fuel cell,green hydrogen,hydrogen storage,hydrogen infrastructure"},
            {"focus_area": "Thermal Energy Networks", "keywords": "thermal energy network,district geothermal,ground source,district heating,TEN"},
            {"focus_area": "Alternative Fuels", "keywords": "ammonia,biofuel,renewable natural gas,synthetic fuel,sustainable aviation fuel"},
        ],
    },
    {
        "name": "Power Generation & Storage",
        "program_type": "innovation",
        "description": "Long-duration energy storage (LDES), flow batteries, advanced chemistries, solar/wind integration, and offshore wind components.",
        "url": "https://www.nyserda.ny.gov/All-Programs/Innovation-at-NYSERDA",
        "contact_email": "innovation@nyserda.ny.gov",
        "parent_program": "Technology & Business Innovation",
        "focus_areas": [
            {"focus_area": "Long-Duration Energy Storage", "keywords": "LDES,long duration,flow battery,iron-air,compressed air,gravity storage,thermal storage"},
            {"focus_area": "Advanced Battery Technologies", "keywords": "battery,lithium,solid state,sodium,zinc,next generation"},
            {"focus_area": "Offshore Wind", "keywords": "offshore wind,floating wind,wind turbine,wind components,supply chain"},
        ],
    },
    {
        "name": "Clean Transportation",
        "program_type": "innovation",
        "description": "Commercial fleet electrification, medium/heavy-duty zero-emission vehicles, smart charging, and vehicle-to-grid (V2G) systems.",
        "url": "https://www.nyserda.ny.gov/All-Programs/Innovation-at-NYSERDA",
        "contact_email": "cleantrans@nyserda.ny.gov",
        "parent_program": "Technology & Business Innovation",
        "focus_areas": [
            {"focus_area": "Fleet Electrification", "keywords": "fleet,medium duty,heavy duty,commercial vehicle,truck,bus,electrification"},
            {"focus_area": "Smart Charging & V2G", "keywords": "smart charging,vehicle to grid,V2G,managed charging,bidirectional"},
        ],
    },
    {
        "name": "Carbon Management & Industrial Decarbonization",
        "program_type": "innovation",
        "description": "Embodied carbon in concrete/steel, industrial heat electrification, and carbon capture/utilization research.",
        "url": "https://www.nyserda.ny.gov/All-Programs/Innovation-at-NYSERDA",
        "contact_email": "innovation@nyserda.ny.gov",
        "parent_program": "Technology & Business Innovation",
        "focus_areas": [
            {"focus_area": "Embodied Carbon", "keywords": "embodied carbon,concrete,steel,cement,low carbon materials,construction"},
            {"focus_area": "Industrial Heat", "keywords": "industrial heat,process heat,electrification,industrial decarbonization"},
            {"focus_area": "Carbon Capture & Utilization", "keywords": "carbon capture,CCUS,direct air capture,carbon utilization,mineralization"},
        ],
    },
]

COMMERCIALIZATION_PROGRAMS = [
    {
        "name": "Scale for ClimateTech",
        "program_type": "commercialization",
        "description": "Manufacturing readiness accelerator providing Design for Manufacturing and Assembly (DFMA), supply chain supplier matching, and production scaling support in NYS. Helps climate tech companies move from prototype to manufacturing scale.",
        "url": "https://forclimatetech.org/scale-for-climatetech/",
        "contact_email": "innovation@nyserda.ny.gov",
        "target_stage": "scale-up",
        "target_applicant": "Hardware climate tech companies ready for manufacturing scale-up",
    },
    {
        "name": "Venture for ClimateTech",
        "program_type": "commercialization",
        "description": "Non-profit accelerator helping seed-stage cleantech companies achieve product-market fit, gain first customers, and raise venture capital.",
        "url": "https://forclimatetech.org/venture-for-climatetech/",
        "contact_email": "innovation@nyserda.ny.gov",
        "target_stage": "early-stage",
        "target_applicant": "Seed-stage cleantech startups",
    },
    {
        "name": "ClimateTech Expertise Network",
        "program_type": "commercialization",
        "description": "Provides early-stage climate tech startups with dedicated executive mentors, budgeting/resource planning, and talent acquisition support. Formerly Entrepreneur-in-Residence (EIR) program.",
        "url": "https://www.climatestartupsupport.com/",
        "contact_email": "innovation@nyserda.ny.gov",
        "target_stage": "early-stage",
        "target_applicant": "Early-stage climate tech startups in NY",
    },
    {
        "name": "The Clean Fight",
        "program_type": "commercialization",
        "description": "Growth-stage accelerator helping high-impact climate tech companies scale operations and secure enterprise/utility commercial contracts in NYS.",
        "url": "https://thecleanfight.com/",
        "contact_email": "innovation@nyserda.ny.gov",
        "target_stage": "growth",
        "target_applicant": "Growth-stage climate tech companies seeking utility/enterprise contracts",
    },
    {
        "name": "Activate Fellowship",
        "program_type": "commercialization",
        "description": "Two-year fellowship empowering scientists and postdoctoral researchers to commercialize hard-tech research into scalable businesses.",
        "url": "https://www.activate.org/the-fellowship",
        "contact_email": "innovation@nyserda.ny.gov",
        "target_stage": "early-stage",
        "target_applicant": "Scientists and postdoctoral researchers with hard-tech innovations",
    },
    {
        "name": "Carbontech Development Initiative (CDI)",
        "program_type": "commercialization",
        "description": "Columbia University partnership funding carbon capture, utilization, and conversion technologies from benchtop to pilot scale.",
        "url": "https://labtomarket.columbia.edu/cdi",
        "contact_email": "innovation@nyserda.ny.gov",
        "target_stage": "early-stage",
        "target_applicant": "Researchers and startups in carbon capture/utilization",
    },
    {
        "name": "FlexTech Program",
        "program_type": "technical_assistance",
        "description": "Cost-share for credible, objective technical assistance services such as energy audits for commercial, industrial, institutional, and multifamily customers paying into the System Benefits Charge.",
        "url": "https://www.nyserda.ny.gov/All-Programs/FlexTech-Program",
        "contact_email": "flextech@nyserda.ny.gov",
        "target_stage": "any",
        "target_applicant": "NY commercial/industrial/institutional/multifamily SBC ratepayers",
    },
    {
        "name": "Empire Building Challenge",
        "program_type": "deployment",
        "description": "Partnership with building owners to develop and demonstrate scalable low-carbon retrofit solutions for large existing buildings, including hospitals.",
        "url": "https://www.nyserda.ny.gov/All-Programs/Empire-Building-Challenge",
        "contact_email": "ebchospitals@nyserda.ny.gov",
        "target_stage": "deployment",
        "target_applicant": "Large building owners pursuing low-carbon retrofits in NY",
    },
]


class ProgramsAdapter(BaseAdapter):
    """Seeds the database with curated NYSERDA program information."""

    source_name = "nyserda_programs_curated"
    source_type = "curated"
    authority_rank = 4

    def ingest(self, db: Session) -> dict:
        stats = {"added": 0, "updated": 0, "unchanged": 0, "errors": 0}

        run = IngestionRun(source_name=self.source_name, status="running")
        db.add(run)
        db.commit()

        try:
            all_programs = INNOVATION_PROGRAMS + COMMERCIALIZATION_PROGRAMS

            for prog_data in all_programs:
                try:
                    existing = db.query(Program).filter_by(name=prog_data["name"]).first()

                    if existing:
                        # Update
                        existing.description = prog_data.get("description", existing.description)
                        existing.url = prog_data.get("url", existing.url)
                        existing.contact_email = prog_data.get("contact_email")
                        existing.target_stage = prog_data.get("target_stage")
                        existing.target_applicant = prog_data.get("target_applicant")
                        existing.last_verified_at = self.now_utc()
                        db.commit()
                        stats["updated"] += 1
                    else:
                        program = Program(
                            name=prog_data["name"],
                            program_type=prog_data["program_type"],
                            description=prog_data.get("description"),
                            url=prog_data.get("url"),
                            contact_email=prog_data.get("contact_email"),
                            parent_program=prog_data.get("parent_program"),
                            target_stage=prog_data.get("target_stage"),
                            target_applicant=prog_data.get("target_applicant"),
                            source_url=prog_data.get("url"),
                        )
                        db.add(program)
                        db.flush()

                        for fa_data in prog_data.get("focus_areas", []):
                            db.add(ProgramFocusArea(
                                program_id=program.id,
                                focus_area=fa_data["focus_area"],
                                description=fa_data.get("description"),
                                keywords=fa_data.get("keywords"),
                            ))

                        db.commit()
                        stats["added"] += 1

                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error processing program {prog_data.get('name')}: {e}")
                    db.rollback()

            # Update source
            source = db.query(Source).filter_by(name=self.source_name).first()
            if not source:
                source = Source(
                    name=self.source_name,
                    url="https://www.nyserda.ny.gov/All-Programs/Innovation-at-NYSERDA",
                    source_type=self.source_type,
                    authority_rank=self.authority_rank,
                    description="Curated NYSERDA program and commercialization data",
                    update_frequency="monthly",
                )
                db.add(source)

            source.last_fetched_at = self.now_utc()
            source.fetch_status = "success"
            source.record_count = len(all_programs)

            run.status = "success"
            run.records_added = stats["added"]
            run.records_updated = stats["updated"]
            run.completed_at = self.now_utc()
            db.commit()

        except Exception as e:
            run.status = "error"
            run.error_details = str(e)
            run.completed_at = self.now_utc()
            db.commit()
            raise

        return stats
