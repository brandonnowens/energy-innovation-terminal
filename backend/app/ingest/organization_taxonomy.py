"""Organization Taxonomy and Canonical Metadata Registry.

Provides structured categorization, jurisdiction, and utility sub-types
for all energy innovation funders, utilities, state agencies, and foundations.
"""

from typing import Dict, Any, Optional
from functools import lru_cache

ORGANIZATION_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # ── ⚡ ELECTRIC & GAS UTILITIES ──
    # New York Investor-Owned Utilities (IOUs)
    "Con Edison": {
        "full_name": "Consolidated Edison Company of New York",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "Investor-Owned Utility (IOU)",
        "logo_domain": "coned.com",
        "website": "https://www.coned.com",
        "description": "Electric, gas, and steam utility serving New York City and Westchester County.",
    },
    "National Grid": {
        "full_name": "National Grid USA (New York)",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "Investor-Owned Utility (IOU)",
        "logo_domain": "nationalgridus.com",
        "website": "https://www.nationalgridus.com",
        "description": "Electric and natural gas utility serving Upstate New York, NYC (Brooklyn/Queens/Staten Island), and Long Island.",
    },
    "NYSEG": {
        "full_name": "New York State Electric & Gas",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "Investor-Owned Utility (IOU)",
        "logo_domain": "nyseg.com",
        "website": "https://www.nyseg.com",
        "description": "Electric and natural gas utility serving upstate and central New York (Avangrid subsidiary).",
    },
    "RG&E": {
        "full_name": "Rochester Gas and Electric",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "Investor-Owned Utility (IOU)",
        "logo_domain": "rge.com",
        "website": "https://www.rge.com",
        "description": "Electric and gas utility serving the greater Rochester, NY metropolitan area (Avangrid subsidiary).",
    },
    "Central Hudson": {
        "full_name": "Central Hudson Gas & Electric",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "Investor-Owned Utility (IOU)",
        "logo_domain": "cenhud.com",
        "website": "https://www.cenhud.com",
        "description": "Regulated transmission and distribution utility serving the Mid-Hudson Valley (Fortis subsidiary).",
    },
    "Orange & Rockland": {
        "full_name": "Orange and Rockland Utilities",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "Investor-Owned Utility (IOU)",
        "logo_domain": "oru.com",
        "website": "https://www.oru.com",
        "description": "Electric and gas utility serving Rockland, Orange, and Sullivan counties in NY (Con Edison subsidiary).",
    },

    # New York Public Power Authorities & Management
    "NYPA": {
        "full_name": "New York Power Authority",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "Public Power Authority",
        "logo_domain": "nypa.gov",
        "website": "https://www.nypa.gov",
        "description": "The nation's largest state public power organization, operating clean generation and transmission across NY.",
    },
    "LIPA": {
        "full_name": "Long Island Power Authority",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "Public Power Authority",
        "logo_domain": "lipower.org",
        "website": "https://www.lipower.org",
        "description": "Municipal electric utility owning the electric transmission and distribution system in Nassau and Suffolk counties.",
    },
    "PSEG Long Island": {
        "full_name": "PSEG Long Island",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "Utility Operating Service",
        "logo_domain": "psegliny.com",
        "website": "https://www.psegliny.com",
        "description": "Operating agent managing the electric grid on behalf of Long Island Power Authority (LIPA).",
    },

    # Utility Collaboratives & State Regulators
    "Joint Utilities of NY": {
        "full_name": "Joint Utilities of New York",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "Utility Collaborative",
        "logo_domain": "jointutilitiesofny.org",
        "website": "https://jointutilitiesofny.org",
        "description": "Consortium of New York's 6 investor-owned utilities collaborating on grid modernization, EV integration, and hosting capacity.",
    },
    "NY PSC": {
        "full_name": "New York Public Service Commission",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "Regulatory Commission",
        "logo_domain": "dps.ny.gov",
        "website": "https://dps.ny.gov",
        "description": "New York State utility regulatory body overseeing REV demonstrations, clean energy proceedings, and tariff innovation.",
    },

    # Regional / National Utilities
    "PG&E": {
        "full_name": "Pacific Gas and Electric Company",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "California",
        "state": "CA",
        "sub_type": "Investor-Owned Utility (IOU)",
        "logo_domain": "pge.com",
        "website": "https://www.pge.com",
    },
    "SCE": {
        "full_name": "Southern California Edison",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "California",
        "state": "CA",
        "sub_type": "Investor-Owned Utility (IOU)",
        "logo_domain": "sce.com",
        "website": "https://www.sce.com",
    },
    "ComEd": {
        "full_name": "Commonwealth Edison",
        "category": "utility",
        "category_label": "Electric & Gas Utilities",
        "jurisdiction": "Illinois",
        "state": "IL",
        "sub_type": "Investor-Owned Utility (IOU)",
        "logo_domain": "comed.com",
        "website": "https://www.comed.com",
    },

    # ── 🏛️ FEDERAL AGENCIES ──
    "DOE": {
        "full_name": "U.S. Department of Energy",
        "category": "federal",
        "category_label": "Federal Agencies",
        "jurisdiction": "Federal",
        "state": "US",
        "sub_type": "Cabinet Department",
        "logo_domain": "energy.gov",
        "website": "https://www.energy.gov",
        "description": "Primary federal energy research, development, demonstration, and deployment agency.",
    },
    "ARPA-E": {
        "full_name": "Advanced Research Projects Agency-Energy",
        "category": "federal",
        "category_label": "Federal Agencies",
        "jurisdiction": "Federal",
        "state": "US",
        "sub_type": "Independent Agency / Office",
        "logo_domain": "arpa-e.energy.gov",
        "website": "https://arpa-e.energy.gov",
        "description": "High-risk, high-reward transformational energy technology research agency.",
    },
    "DOD": {
        "full_name": "U.S. Department of Defense",
        "category": "federal",
        "category_label": "Federal Agencies",
        "jurisdiction": "Federal",
        "state": "US",
        "sub_type": "Cabinet Department",
        "logo_domain": "defense.gov",
        "website": "https://www.defense.gov",
        "description": "Operational energy resilience, tactical power, advanced materials, and defense innovation.",
    },
    "NSF": {
        "full_name": "National Science Foundation",
        "category": "federal",
        "category_label": "Federal Agencies",
        "jurisdiction": "Federal",
        "state": "US",
        "sub_type": "Independent Agency",
        "logo_domain": "nsf.gov",
        "website": "https://www.nsf.gov",
        "description": "Fundamental scientific research, engineering, and translational technology innovation (TIP Directorate).",
    },
    "NASA": {
        "full_name": "National Aeronautics and Space Administration",
        "category": "federal",
        "category_label": "Federal Agencies",
        "jurisdiction": "Federal",
        "state": "US",
        "sub_type": "Independent Agency",
        "logo_domain": "nasa.gov",
        "website": "https://www.nasa.gov",
        "description": "Extreme environment power systems, high-density energy storage, and aerospace power conversion.",
    },
    "EPA": {
        "full_name": "U.S. Environmental Protection Agency",
        "category": "federal",
        "category_label": "Federal Agencies",
        "jurisdiction": "Federal",
        "state": "US",
        "sub_type": "Independent Agency",
        "logo_domain": "epa.gov",
        "website": "https://www.epa.gov",
        "description": "Emissions reduction, clean air, environmental monitoring, and Greenhouse Gas Reduction Fund programs.",
    },
    "USDA": {
        "full_name": "U.S. Department of Agriculture",
        "category": "federal",
        "category_label": "Federal Agencies",
        "jurisdiction": "Federal",
        "state": "US",
        "sub_type": "Cabinet Department",
        "logo_domain": "usda.gov",
        "website": "https://www.usda.gov",
        "description": "Rural Energy for America Program (REAP), bioeconomy research, and agricultural clean energy deployment.",
    },
    "DOT": {
        "full_name": "U.S. Department of Transportation",
        "category": "federal",
        "category_label": "Federal Agencies",
        "jurisdiction": "Federal",
        "state": "US",
        "sub_type": "Cabinet Department",
        "logo_domain": "transportation.gov",
        "website": "https://www.transportation.gov",
        "description": "Clean transit, EV charging corridors (NEVI), smart mobility, and freight decarbonization.",
    },
    "DOC": {
        "full_name": "U.S. Department of Commerce",
        "category": "federal",
        "category_label": "Federal Agencies",
        "jurisdiction": "Federal",
        "state": "US",
        "sub_type": "Cabinet Department",
        "logo_domain": "commerce.gov",
        "website": "https://www.commerce.gov",
        "description": "NIST manufacturing extension, regional clean tech hubs, and commercialization programs.",
    },

    # ── 🗽 STATE ENERGY AGENCIES ──
    "NYSERDA": {
        "full_name": "New York State Energy Research and Development Authority",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "State Energy Authority",
        "logo_domain": "nyserda.ny.gov",
        "website": "https://www.nyserda.ny.gov",
        "description": "Public benefit corporation advancing clean energy innovation, market development, and decarbonization in NY.",
    },
    "MassCEC": {
        "full_name": "Massachusetts Clean Energy Center",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "Massachusetts",
        "state": "MA",
        "sub_type": "State Clean Energy Center",
        "logo_domain": "masscec.com",
        "website": "https://www.masscec.com",
        "description": "State economic development agency accelerating clean tech commercialization and offshore wind.",
    },
    "CEC": {
        "full_name": "California Energy Commission",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "California",
        "state": "CA",
        "sub_type": "State Energy Commission",
        "logo_domain": "energy.ca.gov",
        "website": "https://www.energy.ca.gov",
        "description": "California's primary energy policy and planning agency (EPIC research and clean transportation programs).",
    },
    "Efficiency Maine": {
        "full_name": "Efficiency Maine Trust",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "Maine",
        "state": "ME",
        "sub_type": "State Energy Trust",
        "logo_domain": "efficiencymaine.com",
        "website": "https://www.efficiencymaine.com",
        "description": "Independent administrator for energy efficiency, heat pumps, and clean transportation in Maine.",
    },
    "NJEDA": {
        "full_name": "New Jersey Economic Development Authority",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "New Jersey",
        "state": "NJ",
        "sub_type": "State Development Authority",
        "logo_domain": "njeda.gov",
        "website": "https://www.njeda.gov",
        "description": "Clean energy venture funds, offshore wind port development, and green workforce programs in NJ.",
    },
    "Colorado CEO": {
        "full_name": "Colorado Energy Office",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "Colorado",
        "state": "CO",
        "sub_type": "State Energy Office",
        "logo_domain": "energyoffice.colorado.gov",
        "website": "https://energyoffice.colorado.gov",
        "description": "State energy agency reducing greenhouse gas emissions and expanding geothermal and EV infrastructure.",
    },
    "MD MEA": {
        "full_name": "Maryland Energy Administration",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "Maryland",
        "state": "MD",
        "sub_type": "State Energy Administration",
        "logo_domain": "energy.maryland.gov",
        "website": "https://energy.maryland.gov",
        "description": "State agency administering clean energy grants, solar incentives, and resiliency programs in Maryland.",
    },
    "WI OEI": {
        "full_name": "Wisconsin Office of Energy Innovation",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "Wisconsin",
        "state": "WI",
        "sub_type": "State Energy Office",
        "logo_domain": "psc.wi.gov",
        "website": "https://psc.wi.gov",
        "description": "State agency funding municipal energy resilience, microgrids, and clean energy innovation in Wisconsin.",
    },
    "IL DCEO": {
        "full_name": "Illinois Department of Commerce & Economic Opportunity",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "Illinois",
        "state": "IL",
        "sub_type": "State Department",
        "logo_domain": "dceo.illinois.gov",
        "website": "https://dceo.illinois.gov",
        "description": "Climate and Equitable Jobs Act (CEJA) grant administrator for clean energy transition in Illinois.",
    },
    "NM EMNRD": {
        "full_name": "New Mexico Energy, Minerals and Natural Resources Department",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "New Mexico",
        "state": "NM",
        "sub_type": "State Department",
        "logo_domain": "emnrd.nm.gov",
        "website": "https://www.emnrd.nm.gov",
        "description": "State agency advancing grid modernization, clean hydrogen, and renewable energy in New Mexico.",
    },
    "TX SECO": {
        "full_name": "Texas State Energy Conservation Office",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "Texas",
        "state": "TX",
        "sub_type": "State Energy Office",
        "logo_domain": "comptroller.texas.gov/programs/seco",
        "website": "https://comptroller.texas.gov/programs/seco/",
        "description": "Texas agency supporting energy efficiency, local government energy planning, and clean power.",
    },
    "WA Commerce": {
        "full_name": "Washington State Department of Commerce (Energy Division)",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "Washington",
        "state": "WA",
        "sub_type": "State Department",
        "logo_domain": "commerce.wa.gov",
        "website": "https://www.commerce.wa.gov",
        "description": "Clean Energy Fund administrator advancing grid modernization, maritime electrification, and clean tech.",
    },
    "MN Commerce": {
        "full_name": "Minnesota Department of Commerce (Energy Resources)",
        "category": "state",
        "category_label": "State Energy Agencies",
        "jurisdiction": "Minnesota",
        "state": "MN",
        "sub_type": "State Department",
        "logo_domain": "mn.gov/commerce",
        "website": "https://mn.gov/commerce",
        "description": "Administering State Energy Programs, community solar, and renewable development in Minnesota.",
    },

    # ── 🌱 PHILANTHROPIC FOUNDATIONS & CLIMATE FUNDS ──
    "Gates Foundation": {
        "full_name": "Bill & Melinda Gates Foundation",
        "category": "foundation",
        "category_label": "Philanthropic Foundations",
        "jurisdiction": "Global",
        "state": "Global",
        "sub_type": "Philanthropic Foundation",
        "logo_domain": "gatesfoundation.org",
        "website": "https://www.gatesfoundation.org",
        "description": "Global development and climate adaptation grants for clean agriculture, energy access, and health.",
    },
    "Breakthrough Energy": {
        "full_name": "Breakthrough Energy",
        "category": "foundation",
        "category_label": "Philanthropic Foundations",
        "jurisdiction": "Global",
        "state": "Global",
        "sub_type": "Climate Venture & Grant Fund",
        "logo_domain": "breakthroughenergy.org",
        "website": "https://breakthroughenergy.org",
        "description": "Venture and grant fund accelerating net-zero innovation across electricity, manufacturing, and transport.",
    },
    "Hewlett Foundation": {
        "full_name": "William and Flora Hewlett Foundation",
        "category": "foundation",
        "category_label": "Philanthropic Foundations",
        "jurisdiction": "National",
        "state": "National",
        "sub_type": "Philanthropic Foundation",
        "logo_domain": "hewlett.org",
        "website": "https://hewlett.org",
        "description": "Major climate initiative funding power sector decarbonization and clean energy transitions.",
    },
    "Bezos Earth Fund": {
        "full_name": "Bezos Earth Fund",
        "category": "foundation",
        "category_label": "Philanthropic Foundations",
        "jurisdiction": "Global",
        "state": "Global",
        "sub_type": "Philanthropic Foundation",
        "logo_domain": "bezosearthfund.org",
        "website": "https://www.bezosearthfund.org",
        "description": "$10B commitment funding climate solutions, clean energy transitions, and environmental justice.",
    },
    "MacArthur Foundation": {
        "full_name": "John D. and Catherine T. MacArthur Foundation",
        "category": "foundation",
        "category_label": "Philanthropic Foundations",
        "jurisdiction": "National",
        "state": "National",
        "sub_type": "Philanthropic Foundation",
        "logo_domain": "macfound.org",
        "website": "https://www.macfound.org",
    },
    "Kresge Foundation": {
        "full_name": "The Kresge Foundation",
        "category": "foundation",
        "category_label": "Philanthropic Foundations",
        "jurisdiction": "National",
        "state": "National",
        "sub_type": "Philanthropic Foundation",
        "logo_domain": "kresge.org",
        "website": "https://kresge.org",
    },
    "Barr Foundation": {
        "full_name": "Barr Foundation",
        "category": "foundation",
        "category_label": "Philanthropic Foundations",
        "jurisdiction": "Regional",
        "state": "MA",
        "sub_type": "Philanthropic Foundation",
        "logo_domain": "barrfoundation.org",
        "website": "https://www.barrfoundation.org",
    },

    # ── 🔬 NATIONAL LABORATORIES & RESEARCH INSTITUTES ──
    "EPRI": {
        "full_name": "Electric Power Research Institute",
        "category": "national_lab",
        "category_label": "Research Institutions",
        "jurisdiction": "National",
        "state": "US",
        "sub_type": "Research Institute",
        "logo_domain": "epri.com",
        "website": "https://www.epri.com",
        "description": "Independent, nonprofit energy research institute focusing on electricity generation, delivery, and use.",
    },

    # ── 🏛️ STATE ECONOMIC DEVELOPMENT AGENCIES ──
    "Empire State Development": {
        "full_name": "Empire State Development (ESD & NY Ventures)",
        "category": "state",
        "category_label": "State Economic Development Agencies",
        "jurisdiction": "New York",
        "state": "NY",
        "sub_type": "State Economic Development Agency",
        "logo_domain": "esd.ny.gov",
        "website": "https://esd.ny.gov",
        "description": "New York's chief economic development agency overseeing NY Ventures, NYSTAR Centers for Advanced Technology, and REDC."
    },
    "MassVentures": {
        "full_name": "Massachusetts Technology Development Corporation (MassVentures)",
        "category": "state",
        "category_label": "State Economic Development Agencies",
        "jurisdiction": "Massachusetts",
        "state": "MA",
        "sub_type": "State Venture Capital Arm",
        "logo_domain": "mass-ventures.com",
        "website": "https://www.mass-ventures.com",
        "description": "Quasi-public venture capital firm providing seed and growth financing to high-growth Massachusetts clean tech and deep tech companies."
    },
    "California GO-Biz": {
        "full_name": "California Governor's Office of Business and Economic Development",
        "category": "state",
        "category_label": "State Economic Development Agencies",
        "jurisdiction": "California",
        "state": "CA",
        "sub_type": "State Economic Development Agency",
        "logo_domain": "business.ca.gov",
        "website": "https://business.ca.gov",
        "description": "California state agency promoting economic development, climate business attraction, CalSEED, and ARCHES clean hydrogen hub initiatives."
    },
    "JobsOhio": {
        "full_name": "JobsOhio Clean Energy & Advanced Manufacturing",
        "category": "state",
        "category_label": "State Economic Development Agencies",
        "jurisdiction": "Ohio",
        "state": "OH",
        "sub_type": "Private Economic Development Corporation",
        "logo_domain": "jobsohio.com",
        "website": "https://www.jobsohio.com",
        "description": "Private non-profit economic development corporation driving clean energy manufacturing and supply chain investments across Ohio."
    },
    "MEDC": {
        "full_name": "Michigan Economic Development Corporation",
        "category": "state",
        "category_label": "State Economic Development Agencies",
        "jurisdiction": "Michigan",
        "state": "MI",
        "sub_type": "State Economic Development Corporation",
        "logo_domain": "michiganbusiness.org",
        "website": "https://www.michiganbusiness.org",
        "description": "State agency leading the Michigan Strategic Fund and EV/clean mobility innovation grants."
    },
    "Ben Franklin Tech Partners": {
        "full_name": "Ben Franklin Technology Partners (Pennsylvania)",
        "category": "state",
        "category_label": "State Economic Development Agencies",
        "jurisdiction": "Pennsylvania",
        "state": "PA",
        "sub_type": "State Technology Development Partnership",
        "logo_domain": "benfranklin.org",
        "website": "https://www.benfranklin.org",
        "description": "Pennsylvania state technology development initiative funding early-stage clean energy, battery, and advanced materials ventures."
    },
    "Connecticut Innovations": {
        "full_name": "Connecticut Innovations (CI) & ClimateTech Fund",
        "category": "state",
        "category_label": "State Economic Development Agencies",
        "jurisdiction": "Connecticut",
        "state": "CT",
        "sub_type": "State Strategic Venture Capital Arm",
        "logo_domain": "ctinnovations.com",
        "website": "https://ctinnovations.com",
        "description": "Connecticut's strategic venture capital arm investing in early-stage clean energy, fuel cell, and climate technologies."
    },
    "TEDCO": {
        "full_name": "Maryland Technology Development Corporation (TEDCO)",
        "category": "state",
        "category_label": "State Economic Development Agencies",
        "jurisdiction": "Maryland",
        "state": "MD",
        "sub_type": "State Technology Commercialization Agency",
        "logo_domain": "tedcomd.com",
        "website": "https://www.tedcomd.com",
        "description": "Maryland state corporation fostering early-stage technology transfer, seed funds, and clean energy commercialization."
    },
    "VIPC": {
        "full_name": "Virginia Innovation Partnership Corporation (VIPC)",
        "category": "state",
        "category_label": "State Economic Development Agencies",
        "jurisdiction": "Virginia",
        "state": "VA",
        "sub_type": "State Innovation & Commercialization Agency",
        "logo_domain": "virginiaipc.org",
        "website": "https://www.virginiaipc.org",
        "description": "Virginia state innovation authority providing catalytic matching grants and seed equity to energy and hardware startups."
    },
    "Colorado OEDIT": {
        "full_name": "Colorado Office of Economic Development and International Trade",
        "category": "state",
        "category_label": "State Economic Development Agencies",
        "jurisdiction": "Colorado",
        "state": "CO",
        "sub_type": "State Economic Development Office",
        "logo_domain": "oedit.colorado.gov",
        "website": "https://oedit.colorado.gov",
        "description": "Colorado state agency managing Advanced Industries clean tech grants, geothermal grants, and clean manufacturing tax credits."
    },
    "MN DEED": {
        "full_name": "Minnesota Department of Employment and Economic Development",
        "category": "state",
        "category_label": "State Economic Development Agencies",
        "jurisdiction": "Minnesota",
        "state": "MN",
        "sub_type": "State Economic Development Department",
        "logo_domain": "mn.gov/deed",
        "website": "https://mn.gov/deed",
        "description": "Minnesota principal economic development agency funding the Energy Transition Grant program and Launch Minnesota clean tech vouchers."
    },

    # ── 💼 CLIMATE VENTURE CAPITAL & PRIVATE EQUITY FUNDS ──
    "Breakthrough Energy Ventures": {
        "full_name": "Breakthrough Energy Ventures (BEV)",
        "category": "funder",
        "category_label": "Climate Venture Capital",
        "jurisdiction": "National",
        "state": "WA",
        "sub_type": "Climate Venture Capital",
        "logo_domain": "breakthroughenergy.org",
        "website": "https://breakthroughenergy.org",
        "description": "Bill Gates-founded climate technology investment firm backing technologies with potential to reduce at least 500 million metric tons of annual GHG emissions."
    },
    "Energy Impact Partners": {
        "full_name": "Energy Impact Partners (EIP)",
        "category": "funder",
        "category_label": "Climate Venture Capital",
        "jurisdiction": "National",
        "state": "NY",
        "sub_type": "Utility-Backed Climate Venture Firm",
        "logo_domain": "energyimpactpartners.com",
        "website": "https://www.energyimpactpartners.com",
        "description": "Global venture firm with $4B+ AUM backed by a collaborative coalition of 60+ global utility and industrial energy partners."
    },
    "Lowercarbon Capital": {
        "full_name": "Lowercarbon Capital",
        "category": "funder",
        "category_label": "Climate Venture Capital",
        "jurisdiction": "National",
        "state": "CA",
        "sub_type": "Frontier Climate Venture Fund",
        "logo_domain": "lowercarboncapital.com",
        "website": "https://lowercarboncapital.com",
        "description": "Chris Sacca-led climate tech venture fund investing aggressively in carbon removal, fusion power, industrial decarbonization, and low-carbon materials."
    },
    "Prelude Ventures": {
        "full_name": "Prelude Ventures",
        "category": "funder",
        "category_label": "Climate Venture Capital",
        "jurisdiction": "National",
        "state": "CA",
        "sub_type": "Pioneer Clean Tech Venture Fund",
        "logo_domain": "preludeventures.com",
        "website": "https://www.preludeventures.com",
        "description": "Venture capital firm partnering with entrepreneurs solving climate change across energy, manufacturing, food/agriculture, and transportation."
    },
    "Congruent Ventures": {
        "full_name": "Congruent Ventures",
        "category": "funder",
        "category_label": "Climate Venture Capital",
        "jurisdiction": "National",
        "state": "CA",
        "sub_type": "Early Stage Climate Venture Fund",
        "logo_domain": "congruentvc.com",
        "website": "https://congruentvc.com",
        "description": "Early-stage venture capital firm investing in climate and sustainability technologies across mobility, energy transition, and supply chain infrastructure."
    },
    "Clean Energy Ventures": {
        "full_name": "Clean Energy Ventures (CEV)",
        "category": "funder",
        "category_label": "Climate Venture Capital",
        "jurisdiction": "National",
        "state": "MA",
        "sub_type": "Early Stage Clean Energy Fund",
        "logo_domain": "cleanenergyventures.com",
        "website": "https://cleanenergyventures.com",
        "description": "Venture capital fund investing in early-stage clean energy companies with the potential to mitigate at least 2.5 gigatons of CO2e."
    },
    "Fifth Wall": {
        "full_name": "Fifth Wall Climate Tech",
        "category": "funder",
        "category_label": "Climate Venture Capital",
        "jurisdiction": "National",
        "state": "CA",
        "sub_type": "Real Estate & Built Environment Climate Fund",
        "logo_domain": "fifthwall.com",
        "website": "https://fifthwall.com",
        "description": "Venture capital firm specializing in Built World tech and dedicated Climate Tech real estate decarbonization."
    },
    "TPG Rise Climate": {
        "full_name": "TPG Rise Climate",
        "category": "funder",
        "category_label": "Climate Growth Equity",
        "jurisdiction": "National",
        "state": "CA",
        "sub_type": "Global Climate Growth Equity Fund",
        "logo_domain": "tpg.com",
        "website": "https://www.tpg.com/rise-climate",
        "description": "$7.3B+ dedicated climate investing arm of TPG global alternative asset firm targeting growth-stage clean tech leaders."
    },
    "Decarbonization Partners": {
        "full_name": "Decarbonization Partners (BlackRock & Temasek)",
        "category": "funder",
        "category_label": "Climate Growth Equity",
        "jurisdiction": "National",
        "state": "NY",
        "sub_type": "Strategic Decarbonization Growth Fund",
        "logo_domain": "decarbonizationpartners.com",
        "website": "https://www.decarbonizationpartners.com",
        "description": "Joint venture between BlackRock and Temasek investing in next-generation decarbonization and clean energy scale-ups."
    },
    "The Engine (MIT)": {
        "full_name": "The Engine Ventures (Spun out of MIT)",
        "category": "funder",
        "category_label": "Tough Tech Venture Capital",
        "jurisdiction": "National",
        "state": "MA",
        "sub_type": "Tough Tech & Deep Tech Venture Firm",
        "logo_domain": "engine.xyz",
        "website": "https://www.engine.xyz",
        "description": "Venture firm spun out of MIT providing long-horizon Tough Tech capital, labs, and specialized infrastructure."
    },
}

@lru_cache(maxsize=2048)
def get_organization_profile(name: str) -> Dict[str, Any]:
    """Retrieve metadata profile for an organization name or code."""
    if name in ORGANIZATION_TAXONOMY:
        return {**ORGANIZATION_TAXONOMY[name], "code": name}

    # Check nationwide state utility registry
    try:
        from app.ingest.state_utility_registry import STATE_UTILITY_DATA, HOLDING_COMPANIES
        for state_code, state_info in STATE_UTILITY_DATA.items():
            for u in state_info.get("utilities", []):
                if name.lower() in [u["name"].lower(), u.get("short_name", "").lower()]:
                    return {
                        "code": u.get("short_name", u["name"]),
                        "full_name": u["name"],
                        "category": "utility",
                        "category_label": "Electric & Gas Utilities",
                        "jurisdiction": state_info.get("state_name", state_code),
                        "state": state_code,
                        "sub_type": u.get("sub_type", "Investor-Owned Utility (IOU)"),
                        "logo_domain": u.get("logo_domain"),
                        "website": u.get("website"),
                        "description": u.get("description"),
                    }
        for h_key, h_info in HOLDING_COMPANIES.items():
            if name.lower() in [h_key.lower(), h_info["name"].lower()]:
                return {
                    "code": h_key,
                    "full_name": h_info["name"],
                    "category": "utility",
                    "category_label": "Electric & Gas Utilities",
                    "jurisdiction": "National",
                    "state": h_info.get("state", "US"),
                    "sub_type": "Holding Company",
                    "logo_domain": h_info.get("domain"),
                    "website": f"https://www.{h_info.get('domain')}" if h_info.get("domain") else None,
                    "description": f"Parent holding company headquartered in {h_info.get('city')}, {h_info.get('state')}.",
                }
    except Exception:
        pass
    
    # Fuzzy match / fallback heuristics
    name_lower = name.lower()
    if any(u in name_lower for u in ["electric", "power", "edison", "grid", "gas", "utility", "nyiso", "pud", "cooperative", "emc", "co-op"]):
        category = "utility"
        category_label = "Electric & Gas Utilities"
        sub_type = "Electric & Gas Utility"
    elif any(f in name_lower for f in ["department of", "u.s.", "national science", "nasa", "epa", "arpa", "doe", "usda"]):
        category = "federal"
        category_label = "Federal Agencies"
        sub_type = "Federal Agency"
    elif any(s in name_lower for s in ["authority", "office", "commission", "center", "state"]):
        category = "state"
        category_label = "State Energy Agencies"
        sub_type = "State Agency"
    elif any(fn in name_lower for fn in ["foundation", "fund", "trust", "climate"]):
        category = "foundation"
        category_label = "Philanthropic Foundations"
        sub_type = "Philanthropic Foundation"
    else:
        category = "state"
        category_label = "State Energy Agencies"
        sub_type = "Energy Organization"

    return {
        "code": name,
        "full_name": name,
        "category": category,
        "category_label": category_label,
        "jurisdiction": "New York" if "ny" in name_lower or "new york" in name_lower else "National",
        "state": "NY" if "ny" in name_lower or "new york" in name_lower else "US",
        "sub_type": sub_type,
        "logo_domain": None,
        "website": None,
        "description": None,
    }

