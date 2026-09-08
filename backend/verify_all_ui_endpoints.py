import urllib.request, json

# 1. Map endpoint
res_map = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/awards/map?limit=60000').read())
print(f"Map API: {len(res_map['markers'])} markers delivered out of {res_map['total']} total awards (${res_map['summary']['total_funding']:,.2f})")

# 2. Recipients Map endpoint
res_rec = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/awards/recipients/map?limit=20000').read())
print(f"Recipients Map API: {len(res_rec['markers'])} recipients delivered out of {res_rec['total']} total")

# 3. Network Graph endpoint
res_net = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/network/graph?node_limit=2500').read())
print(f"Network Graph API: {len(res_net['nodes'])} nodes and {len(res_net['edges'])} relationships")

# 4. Sankey Flow endpoint
res_san = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/sankey/flow?preset=ecosystem').read())
print(f"Sankey Flow API: {len(res_san['nodes'])} flow nodes and {len(res_san['links'])} capital channels (${res_san['meta']['total_value']:,.2f})")

# 5. Trends Overview
res_trends = json.loads(urllib.request.urlopen('http://127.0.0.1:8000/api/trends/overview').read())
print(f"Trends Overview API: {len(res_trends)} historical yearly trend data points")

# 6. Chart Dynamic Aggregation
req = urllib.request.Request('http://127.0.0.1:8000/api/charts/data', data=json.dumps({'metric': 'award_amount', 'group_by': 'state'}).encode('utf-8'), headers={'Content-Type': 'application/json'})
res_charts = json.loads(urllib.request.urlopen(req).read())
print(f"Charts Dynamic API: {len(res_charts)} state funding distributions")
