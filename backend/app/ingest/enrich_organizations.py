import sys
import os
import json
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_dir))

from app.database import SessionLocal, engine, Base
from app.models.opportunity import Opportunity, OpportunityContact
from app.models.organization import Organization
from app.models.contact import Contact, OpportunityContactLink
from app.models.opportunity_organization import OpportunityOrganization
from app.engine.entity_resolution import find_or_create_org

def get_known_agencies():
    return {
        "DOE": {"name": "U.S. Department of Energy", "org_type": "funder", "geographic_scope": "national", "domain": "energy.gov"},
        "NSF": {"name": "National Science Foundation", "org_type": "funder", "geographic_scope": "national", "domain": "nsf.gov"},
        "ARPA-E": {"name": "Advanced Research Projects Agency-Energy", "org_type": "program_office", "geographic_scope": "national", "domain": "arpa-e.energy.gov"},
        "EPA": {"name": "U.S. Environmental Protection Agency", "org_type": "funder", "geographic_scope": "national", "domain": "epa.gov"},
        "NYSERDA": {"name": "New York State Energy Research and Development Authority", "org_type": "funder", "geographic_scope": "state", "domain": "nyserda.ny.gov"},
        "CEC": {"name": "California Energy Commission", "org_type": "funder", "geographic_scope": "state", "domain": "energy.ca.gov"},
        "MassCEC": {"name": "Massachusetts Clean Energy Center", "org_type": "funder", "geographic_scope": "state", "domain": "masscec.com"},
        "Gates Foundation": {"name": "Bill & Melinda Gates Foundation", "org_type": "funder", "geographic_scope": "international", "domain": "gatesfoundation.org"},
        "Colorado CEO": {"name": "Colorado Energy Office", "org_type": "funder", "geographic_scope": "state", "domain": "energyoffice.colorado.gov"},
        "NJEDA": {"name": "New Jersey Economic Development Authority", "org_type": "funder", "geographic_scope": "state", "domain": "njeda.com"},
        "WA Commerce": {"name": "Washington State Department of Commerce", "org_type": "funder", "geographic_scope": "state", "domain": "commerce.wa.gov"},
        "IL DCEO": {"name": "Illinois Department of Commerce and Economic Opportunity", "org_type": "funder", "geographic_scope": "state", "domain": "dceo.illinois.gov"},
        "MN Commerce": {"name": "Minnesota Department of Commerce", "org_type": "funder", "geographic_scope": "state", "domain": "mn.gov"},
        "Efficiency Maine": {"name": "Efficiency Maine", "org_type": "funder", "geographic_scope": "state", "domain": "efficiencymaine.com"},
        "MD MEA": {"name": "Maryland Energy Administration", "org_type": "funder", "geographic_scope": "state", "domain": "energy.maryland.gov"},
        "PA DEP": {"name": "Pennsylvania Department of Environmental Protection", "org_type": "funder", "geographic_scope": "state", "domain": "dep.pa.gov"},
        "VA Energy": {"name": "Virginia Department of Energy", "org_type": "funder", "geographic_scope": "state", "domain": "energy.virginia.gov"},
        "NM EMNRD": {"name": "New Mexico Energy, Minerals and Natural Resources Department", "org_type": "funder", "geographic_scope": "state", "domain": "emnrd.nm.gov"},
        "TX SECO": {"name": "Texas State Energy Conservation Office", "org_type": "funder", "geographic_scope": "state", "domain": "comptroller.texas.gov"},
        "WI OEI": {"name": "Wisconsin Office of Energy Innovation", "org_type": "funder", "geographic_scope": "state", "domain": "psc.wi.gov"},
        "IA IEDA": {"name": "Iowa Economic Development Authority", "org_type": "funder", "geographic_scope": "state", "domain": "iowaeda.com"},
    }

def main():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    known_agencies = get_known_agencies()
    
    # Pre-create known agencies to have them in the DB
    agency_map = {}
    for short_name, details in known_agencies.items():
        org = find_or_create_org(
            db=db,
            name=details["name"],
            org_type=details["org_type"],
            domain=details["domain"]
        )
        org.geographic_scope = details["geographic_scope"]
        
        # Add alias if it doesn't exist
        aliases = org.aliases_json or []
        if short_name not in aliases:
            aliases.append(short_name)
            org.aliases_json = aliases
            
        db.commit()
        agency_map[short_name] = org
        
    # Also handle parent relationship
    if "DOE" in agency_map and "ARPA-E" in agency_map:
        agency_map["ARPA-E"].parent_org_id = agency_map["DOE"].id
        db.commit()

    opps = db.query(Opportunity).all()
    orgs_created = len(agency_map)
    contacts_extracted = 0
    links_created = 0
    
    for opp in opps:
        agency_str = getattr(opp, 'agency', None)
        if agency_str:
            # Check if we know it
            if agency_str in agency_map:
                org = agency_map[agency_str]
            else:
                org = find_or_create_org(db, agency_str, "funder")
                orgs_created += 1
                agency_map[agency_str] = org
                
            # Link opportunity to org
            link = db.query(OpportunityOrganization).filter_by(
                opportunity_id=opp.id,
                organization_id=org.id,
                role="funder"
            ).first()
            if not link:
                link = OpportunityOrganization(
                    opportunity_id=opp.id,
                    organization_id=org.id,
                    role="funder"
                )
                db.add(link)
                links_created += 1
                
        else:
            org = None
            
        # Extract contacts
        if org and opp.contacts:
            for opp_contact in opp.contacts:
                if not opp_contact.name:
                    continue
                    
                # Find or create contact
                contact = db.query(Contact).filter_by(
                    organization_id=org.id,
                    name_display=opp_contact.name
                ).first()
                
                if not contact:
                    contact = Contact(
                        organization_id=org.id,
                        name_display=opp_contact.name,
                        email=opp_contact.email,
                        phone=opp_contact.phone,
                        data_provenance="observed"
                    )
                    db.add(contact)
                    db.flush()
                    contacts_extracted += 1
                    
                # Link contact to opp
                c_link = db.query(OpportunityContactLink).filter_by(
                    opportunity_id=opp.id,
                    contact_id=contact.id
                ).first()
                if not c_link:
                    c_link = OpportunityContactLink(
                        opportunity_id=opp.id,
                        contact_id=contact.id,
                        role="program"
                    )
                    db.add(c_link)

    db.commit()
    print(f"Orgs created/found: {orgs_created}")
    print(f"Contacts extracted: {contacts_extracted}")
    print(f"Links established: {links_created}")
    
if __name__ == "__main__":
    main()
