"""Master State & Utility Innovation Registry.

Comprehensive, authoritative registry of all 50 U.S. states + DC ranked by latest GSP/GDP,
containing detailed metadata, utility holding company hierarchies, innovation programs,
solicitations/opportunities, awards, awardees, geocodes, and taxonomies.
"""

from typing import List, Dict, Any

from app.ingest.states.tier1_ca_tx_ny_fl import TIER1_DATA
from app.ingest.states.tier2_il_pa_oh_ga import TIER2_DATA
from app.ingest.states.tier3_wa_nc_ma_mi import TIER3_DATA
from app.ingest.states.tier4_va_nj_co_tn import TIER4_DATA
from app.ingest.states.tier5_in_az_mn_wi import TIER5_DATA
from app.ingest.states.tier6_mo_md_ct_sc import TIER6_DATA
from app.ingest.states.tier7_or_la_al_ky import TIER7_DATA
from app.ingest.states.tier8_ut_ok_ia_nv import TIER8_DATA
from app.ingest.states.tier9_ks_ar_ne_dc import TIER9_DATA
from app.ingest.states.tier10_ms_nm_id_nh import TIER10_DATA
from app.ingest.states.tier11_hi_wv_de_me import TIER11_DATA
from app.ingest.states.tier12_ri_nd_sd_mt import TIER12_DATA
from app.ingest.states.tier13_ak_wy_vt import TIER13_DATA

# Combine all state tiers
STATE_UTILITY_DATA: Dict[str, Dict[str, Any]] = {}
for tier in [
    TIER1_DATA, TIER2_DATA, TIER3_DATA, TIER4_DATA,
    TIER5_DATA, TIER6_DATA, TIER7_DATA, TIER8_DATA,
    TIER9_DATA, TIER10_DATA, TIER11_DATA, TIER12_DATA,
    TIER13_DATA
]:
    STATE_UTILITY_DATA.update(tier)

STATE_GDP_RANKING = [
    {"rank": 1, "state_code": "CA", "state_name": "California", "gdp_billions": 3890},
    {"rank": 2, "state_code": "TX", "state_name": "Texas", "gdp_billions": 2560},
    {"rank": 3, "state_code": "NY", "state_name": "New York", "gdp_billions": 2150},
    {"rank": 4, "state_code": "FL", "state_name": "Florida", "gdp_billions": 1580},
    {"rank": 5, "state_code": "IL", "state_name": "Illinois", "gdp_billions": 1080},
    {"rank": 6, "state_code": "PA", "state_name": "Pennsylvania", "gdp_billions": 965},
    {"rank": 7, "state_code": "OH", "state_name": "Ohio", "gdp_billions": 873},
    {"rank": 8, "state_code": "GA", "state_name": "Georgia", "gdp_billions": 827},
    {"rank": 9, "state_code": "WA", "state_name": "Washington", "gdp_billions": 801},
    {"rank": 10, "state_code": "NC", "state_name": "North Carolina", "gdp_billions": 794},
    {"rank": 11, "state_code": "MA", "state_name": "Massachusetts", "gdp_billions": 734},
    {"rank": 12, "state_code": "MI", "state_name": "Michigan", "gdp_billions": 673},
    {"rank": 13, "state_code": "VA", "state_name": "Virginia", "gdp_billions": 707},
    {"rank": 14, "state_code": "NJ", "state_name": "New Jersey", "gdp_billions": 782},
    {"rank": 15, "state_code": "CO", "state_name": "Colorado", "gdp_billions": 529},
    {"rank": 16, "state_code": "TN", "state_name": "Tennessee", "gdp_billions": 523},
    {"rank": 17, "state_code": "IN", "state_name": "Indiana", "gdp_billions": 497},
    {"rank": 18, "state_code": "AZ", "state_name": "Arizona", "gdp_billions": 508},
    {"rank": 19, "state_code": "MN", "state_name": "Minnesota", "gdp_billions": 472},
    {"rank": 20, "state_code": "WI", "state_name": "Wisconsin", "gdp_billions": 414},
    {"rank": 21, "state_code": "MO", "state_name": "Missouri", "gdp_billions": 422},
    {"rank": 22, "state_code": "MD", "state_name": "Maryland", "gdp_billions": 492},
    {"rank": 23, "state_code": "CT", "state_name": "Connecticut", "gdp_billions": 340},
    {"rank": 24, "state_code": "SC", "state_name": "South Carolina", "gdp_billions": 322},
    {"rank": 25, "state_code": "OR", "state_name": "Oregon", "gdp_billions": 316},
    {"rank": 26, "state_code": "LA", "state_name": "Louisiana", "gdp_billions": 309},
    {"rank": 27, "state_code": "AL", "state_name": "Alabama", "gdp_billions": 300},
    {"rank": 28, "state_code": "KY", "state_name": "Kentucky", "gdp_billions": 277},
    {"rank": 29, "state_code": "UT", "state_name": "Utah", "gdp_billions": 272},
    {"rank": 30, "state_code": "OK", "state_name": "Oklahoma", "gdp_billions": 242},
    {"rank": 31, "state_code": "IA", "state_name": "Iowa", "gdp_billions": 248},
    {"rank": 32, "state_code": "NV", "state_name": "Nevada", "gdp_billions": 239},
    {"rank": 33, "state_code": "KS", "state_name": "Kansas", "gdp_billions": 226},
    {"rank": 34, "state_code": "AR", "state_name": "Arkansas", "gdp_billions": 176},
    {"rank": 35, "state_code": "NE", "state_name": "Nebraska", "gdp_billions": 179},
    {"rank": 36, "state_code": "DC", "state_name": "District of Columbia", "gdp_billions": 174},
    {"rank": 37, "state_code": "MS", "state_name": "Mississippi", "gdp_billions": 146},
    {"rank": 38, "state_code": "NM", "state_name": "New Mexico", "gdp_billions": 130},
    {"rank": 39, "state_code": "ID", "state_name": "Idaho", "gdp_billions": 119},
    {"rank": 40, "state_code": "NH", "state_name": "New Hampshire", "gdp_billions": 111},
    {"rank": 41, "state_code": "HI", "state_name": "Hawaii", "gdp_billions": 108},
    {"rank": 42, "state_code": "WV", "state_name": "West Virginia", "gdp_billions": 99},
    {"rank": 43, "state_code": "DE", "state_name": "Delaware", "gdp_billions": 94},
    {"rank": 44, "state_code": "ME", "state_name": "Maine", "gdp_billions": 91},
    {"rank": 45, "state_code": "RI", "state_name": "Rhode Island", "gdp_billions": 77},
    {"rank": 46, "state_code": "ND", "state_name": "North Dakota", "gdp_billions": 74},
    {"rank": 47, "state_code": "SD", "state_name": "South Dakota", "gdp_billions": 72},
    {"rank": 48, "state_code": "MT", "state_name": "Montana", "gdp_billions": 71},
    {"rank": 49, "state_code": "AK", "state_name": "Alaska", "gdp_billions": 67},
    {"rank": 50, "state_code": "WY", "state_name": "Wyoming", "gdp_billions": 50},
    {"rank": 51, "state_code": "VT", "state_name": "Vermont", "gdp_billions": 43},
]

# Master Holding Companies
HOLDING_COMPANIES = {
    "NextEra Energy": {"name": "NextEra Energy, Inc.", "domain": "nexteraenergy.com", "state": "FL", "city": "Juno Beach"},
    "Duke Energy": {"name": "Duke Energy Corporation", "domain": "duke-energy.com", "state": "NC", "city": "Charlotte"},
    "Southern Company": {"name": "The Southern Company", "domain": "southerncompany.com", "state": "GA", "city": "Atlanta"},
    "Exelon": {"name": "Exelon Corporation", "domain": "exeloncorp.com", "state": "IL", "city": "Chicago"},
    "American Electric Power": {"name": "American Electric Power (AEP)", "domain": "aep.com", "state": "OH", "city": "Columbus"},
    "Xcel Energy": {"name": "Xcel Energy Inc.", "domain": "xcelenergy.com", "state": "MN", "city": "Minneapolis"},
    "Dominion Energy": {"name": "Dominion Energy, Inc.", "domain": "dominionenergy.com", "state": "VA", "city": "Richmond"},
    "Avangrid": {"name": "Avangrid, Inc.", "domain": "avangrid.com", "state": "CT", "city": "Orange"},
    "Eversource Energy": {"name": "Eversource Energy", "domain": "eversource.com", "state": "MA", "city": "Springfield / Boston"},
    "Entergy": {"name": "Entergy Corporation", "domain": "entergy.com", "state": "LA", "city": "New Orleans"},
    "WEC Energy Group": {"name": "WEC Energy Group, Inc.", "domain": "wecenergygroup.com", "state": "WI", "city": "Milwaukee"},
    "DTE Energy": {"name": "DTE Energy Company", "domain": "dteenergy.com", "state": "MI", "city": "Detroit"},
    "PPL Corporation": {"name": "PPL Corporation", "domain": "pplweb.com", "state": "PA", "city": "Allentown"},
    "FirstEnergy": {"name": "FirstEnergy Corp.", "domain": "firstenergycorp.com", "state": "OH", "city": "Akron"},
    "CenterPoint Energy": {"name": "CenterPoint Energy, Inc.", "domain": "centerpointenergy.com", "state": "TX", "city": "Houston"},
    "NiSource": {"name": "NiSource Inc.", "domain": "nisource.com", "state": "IN", "city": "Merrillville"},
    "Berkshire Hathaway Energy": {"name": "Berkshire Hathaway Energy (BHE)", "domain": "brkenergy.com", "state": "IA", "city": "Des Moines"},
    "Alliant Energy": {"name": "Alliant Energy Corporation", "domain": "alliantenergy.com", "state": "WI", "city": "Madison"},
    "Sempra": {"name": "Sempra", "domain": "sempra.com", "state": "CA", "city": "San Diego"},
    "Ameren": {"name": "Ameren Corporation", "domain": "ameren.com", "state": "MO", "city": "St. Louis"},
    "Pinnacle West": {"name": "Pinnacle West Capital Corporation", "domain": "pinnaclewest.com", "state": "AZ", "city": "Phoenix"},
    "Fortis": {"name": "Fortis Inc.", "domain": "fortisinc.com", "state": "NY", "city": "St. John's / Poughkeepsie"},
    "Evergy": {"name": "Evergy, Inc.", "domain": "evergy.com", "state": "MO", "city": "Kansas City"},
    "IDACORP": {"name": "IDACORP, Inc.", "domain": "idacorpinc.com", "state": "ID", "city": "Boise"},
    "Hawaiian Electric Industries": {"name": "Hawaiian Electric Industries, Inc.", "domain": "hei.com", "state": "HI", "city": "Honolulu"},
    "Black Hills Energy": {"name": "Black Hills Corporation", "domain": "blackhillsenergy.com", "state": "SD", "city": "Rapid City"},
    "NorthWestern Energy": {"name": "NorthWestern Energy Group, Inc.", "domain": "northwesternenergy.com", "state": "SD", "city": "Sioux Falls / Butte"},
    "ALLETE": {"name": "ALLETE, Inc.", "domain": "allete.com", "state": "MN", "city": "Duluth"},
    "OGE Energy": {"name": "OGE Energy Corp.", "domain": "oge.com", "state": "OK", "city": "Oklahoma City"},
    "PNM Resources": {"name": "PNM Resources, Inc.", "domain": "pnmresources.com", "state": "NM", "city": "Albuquerque"},
    "CMS Energy": {"name": "CMS Energy Corporation", "domain": "cmsenergy.com", "state": "MI", "city": "Jackson"},
    "Emera": {"name": "Emera Inc.", "domain": "emera.com", "state": "FL", "city": "Tampa / Halifax"},
    "AES Corporation": {"name": "The AES Corporation", "domain": "aes.com", "state": "VA", "city": "Arlington"},
}

def get_ordered_states() -> List[Dict[str, Any]]:
    """Return all states ordered by GDP ranking with their utility datasets."""
    ordered = []
    for item in STATE_GDP_RANKING:
        code = item["state_code"]
        state_data = STATE_UTILITY_DATA.get(code, {
            "state_code": code,
            "state_name": item["state_name"],
            "gdp_billions": item["gdp_billions"],
            "rank": item["rank"],
            "utilities": [],
        })
        ordered.append({**item, **state_data})
    return ordered
