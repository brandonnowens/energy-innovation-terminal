import urllib.request
import json

url = "https://tavusapi.com/v2/conversations"
key = "b6c16583ce4c44ec970137dc7d142036"

# Test 1: with persona_id and replica_id
payload = {
    "persona_id": "p2fbd605",
    "replica_id": "rcb937aad536",
    "conversation_name": "U.S. Energy Innovation Database Test"
}

req = urllib.request.Request(
    url,
    data=json.dumps(payload).encode("utf-8"),
    headers={"x-api-key": key, "Content-Type": "application/json"}
)

try:
    with urllib.request.urlopen(req, timeout=30) as response:
        print("Success:", response.status, response.read().decode())
except urllib.error.HTTPError as e:
    print("HTTPError:", e.code, e.read().decode())
except Exception as e:
    print("Exception:", e)
