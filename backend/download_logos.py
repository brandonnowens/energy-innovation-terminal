"""Download organization logos from official domains via Clearbit Logo API."""
import urllib.request
import os
import ssl

LOGO_DIR = 'frontend/public/logos'
os.makedirs(LOGO_DIR, exist_ok=True)

# Map org name -> official website domain
ORG_DOMAINS = {
    'NYSERDA': 'nyserda.ny.gov',
    'DOE': 'energy.gov',
    'NSF': 'nsf.gov',
    'ARPA-E': 'arpa-e.energy.gov',
    'EPA': 'epa.gov',
    'DOD': 'defense.gov',
    'NASA': 'nasa.gov',
    'USDA': 'usda.gov',
    'DOT': 'transportation.gov',
    'DOC': 'commerce.gov',
    'Gates Foundation': 'gatesfoundation.org',
    'CEC': 'energy.ca.gov',
    'MassCEC': 'masscec.com',
    'NJEDA': 'njeda.gov',
    'Efficiency Maine': 'efficiencymaine.com',
    'Colorado CEO': 'energyoffice.colorado.gov',
    'MN Commerce': 'mn.gov',
    'WA Commerce': 'commerce.wa.gov',
    'IL DCEO': 'illinois.gov',
    'MD MEA': 'energy.maryland.gov',
    'NM EMNRD': 'emnrd.nm.gov',
    'TX SECO': 'comptroller.texas.gov',
    'WI OEI': 'oei.wi.gov',
}

# Create SSL context that doesn't verify (for corporate firewalls)
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

downloaded = 0
failed = []

for org, domain in ORG_DOMAINS.items():
    filename = org.lower().replace(' ', '_').replace('-', '_') + '.png'
    filepath = os.path.join(LOGO_DIR, filename)
    
    if os.path.exists(filepath) and os.path.getsize(filepath) > 500:
        print(f"  SKIP {org} (already exists)")
        downloaded += 1
        continue
    
    # Try Clearbit logo API (returns 128x128 PNG)
    url = f"https://logo.clearbit.com/{domain}?size=128"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        data = resp.read()
        if len(data) > 500:  # Valid image (not error page)
            with open(filepath, 'wb') as f:
                f.write(data)
            print(f"  OK   {org} -> {filename} ({len(data)} bytes)")
            downloaded += 1
        else:
            failed.append(org)
            print(f"  FAIL {org}: response too small ({len(data)} bytes)")
    except Exception as e:
        failed.append(org)
        print(f"  FAIL {org}: {e}")

print(f"\nDownloaded: {downloaded}/{len(ORG_DOMAINS)}")
if failed:
    print(f"Failed: {', '.join(failed)}")
