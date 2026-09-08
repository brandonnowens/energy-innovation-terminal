"""Check what agency names and sample data look like in the SBIR CSV."""
import csv
import tempfile
from pathlib import Path
from collections import Counter
import requests

BULK_URL = "https://data.www.sbir.gov/awarddatapublic/award_data.csv"

print("Downloading first 5MB to check format...")
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
resp = requests.get(BULK_URL, headers=headers, timeout=30, stream=True)

# Read just first 5MB
data = b""
for chunk in resp.iter_content(chunk_size=1024*1024):
    data += chunk
    if len(data) > 5 * 1024 * 1024:
        break
resp.close()

# Decode and parse
text = data.decode("utf-8", errors="replace")
# Make sure we have complete lines
lines = text.split("\n")
lines = lines[:-1]  # drop possibly incomplete last line

csv.field_size_limit(2**30)
reader = csv.DictReader(lines)

agencies = Counter()
sample_rows = []
for i, row in enumerate(reader):
    agencies[row.get("Agency", "?")] += 1
    if i < 3:
        sample_rows.append(row)

print(f"\nTotal rows in sample: {sum(agencies.values())}")
print(f"\nAgency values found:")
for ag, cnt in agencies.most_common():
    print(f"  '{ag}': {cnt}")

print(f"\nSample row 1:")
for k, v in sample_rows[0].items():
    print(f"  {k}: {repr(v[:80]) if v else 'empty'}")
