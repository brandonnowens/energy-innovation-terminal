import re
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from urllib.parse import urlparse
from app.models.organization import Organization, OrganizationAlias
from app.models.contact import Contact

def normalize_org_name(name: str) -> str:
    """Normalize organization name for matching."""
    if not name:
        return ""
    
    # Strip common suffixes
    suffixes = [
        r'\binc\.?$', r'\bincorporated\b', 
        r'\bllc\.?$', r'\bcorp\.?$', r'\bcorporation\b', 
        r'\bco\.?$', r'\bcompany\b', 
        r'\bltd\.?$', r'\blimited\b',
        r'\bfoundation\b'
    ]
    
    normalized = name.lower()
    for suffix in suffixes:
        normalized = re.sub(suffix, '', normalized).strip()
        
    # Remove all punctuation except spaces
    normalized = re.sub(r'[^\w\s]', '', normalized)
    # Condense multiple spaces
    normalized = re.sub(r'\s+', ' ', normalized).strip()
    
    return normalized

def find_or_create_org(
    db: Session, 
    name: str, 
    org_type: str, 
    website: Optional[str] = None, 
    state: Optional[str] = None,
    domain: Optional[str] = None
) -> Organization:
    """Find an existing organization or create a new one deterministically."""
    normalized_name = normalize_org_name(name)
    
    if not domain and website:
        parsed = urlparse(website if website.startswith('http') else f'http://{website}')
        domain = parsed.netloc.replace('www.', '')
        
    # Search by domain first
    if domain:
        existing = db.query(Organization).filter(Organization.domain == domain).first()
        if existing:
            return existing
            
    # Search by exact name or alias
    # Assuming names might exactly match
    orgs = db.query(Organization).all()
    for org in orgs:
        if normalize_org_name(org.name) == normalized_name:
            return org
            
        for alias in org.aliases_json or []:
            if normalize_org_name(alias) == normalized_name:
                return org
                
    # Create new
    new_org = Organization(
        name=name,
        org_type=org_type,
        website=website,
        domain=domain,
        state=state,
        data_provenance="inferred"
    )
    db.add(new_org)
    db.commit()
    db.refresh(new_org)
    return new_org

def extract_contacts_from_text(text: str) -> List[Dict]:
    """Extract contacts deterministically from unstructured text using regex."""
    if not text:
        return []
        
    contacts = []
    
    # Simple regex for Name <email>
    email_pattern = r'([A-Za-z\s]+)\s*<([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)>'
    for match in re.finditer(email_pattern, text):
        name = match.group(1).strip()
        email = match.group(2).strip()
        if name and email and name.lower() != 'contact':
            contacts.append({
                "name_display": name,
                "email": email
            })
            
    # Contact: Name, Title format
    contact_pattern = r'(?i)Contact:\s*([A-Za-z\s]+)(?:,\s*([A-Za-z\s]+))?'
    for match in re.finditer(contact_pattern, text):
        name = match.group(1).strip()
        title = match.group(2).strip() if match.group(2) else None
        
        # Avoid overriding if we already got this name
        if not any(c.get("name_display") == name for c in contacts):
            contacts.append({
                "name_display": name,
                "title": title
            })
            
    return contacts

def resolve_org_from_domain(domain: str, db: Session) -> Optional[Organization]:
    """Match organization by website domain."""
    if not domain:
        return None
        
    # Clean domain
    domain = domain.lower().replace('www.', '').replace('http://', '').replace('https://', '').split('/')[0]
    
    return db.query(Organization).filter(Organization.domain == domain).first()
