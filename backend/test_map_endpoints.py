from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

# 1. Awards Map
t0 = time.time()
res = client.get('/api/awards/map?limit=60000')
t1 = time.time()
print(f"/api/awards/map status {res.status_code} in {t1 - t0:.2f}s")
if res.status_code == 200:
    data = res.json()
    print("  Total matches in DB:", data['total'])
    print("  Total markers returned:", len(data['markers']))
    print("  Total funding: $" + f"{data['summary']['total_funding']:,.2f}")
    print("  Unique recipients:", data['summary']['unique_recipients'])
    print("  States covered:", data['summary']['states_covered'])

# 2. Recipients Map
t0 = time.time()
res_rec = client.get('/api/awards/recipients/map?limit=20000')
t1 = time.time()
print(f"\n/api/awards/recipients/map status {res_rec.status_code} in {t1 - t0:.2f}s")
if res_rec.status_code == 200:
    data_rec = res_rec.json()
    print("  Total recipients returned:", len(data_rec['markers']))
    print("  Total matches:", data_rec['total'])
