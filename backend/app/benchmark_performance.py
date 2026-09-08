"""Automated Performance & Latency Benchmark Test Suite."""

import time
import statistics
from fastapi.testclient import TestClient
from app.main import app

def run_benchmark():
    client = TestClient(app)
    
    endpoints = [
        ("Health Probe", "GET", "/health"),
        ("API Health", "GET", "/api/health"),
        ("Opportunities List", "GET", "/api/opportunities?page_size=20"),
        ("Awards List", "GET", "/api/awards?page_size=20"),
        ("Awards Stats (Agg)", "GET", "/api/awards/stats"),
        ("Sankey Capital Flow", "GET", "/api/sankey/flow?preset=ecosystem"),
        ("Sankey Macro Insights", "GET", "/api/sankey/insights"),
        ("Trends Overview", "GET", "/api/trends/overview?data_source=awards"),
        ("Contacts Summary Stats", "GET", "/api/contacts/stats"),
        ("Attributions Overview", "GET", "/api/attributions/overview"),
        ("Policies Reference List", "GET", "/api/policies?limit=20"),
        ("Knowledge Graph (Cached)", "GET", "/api/network/graph?node_limit=500"),
    ]

    print("\n================ SYSTEM PERFORMANCE & LATENCY BENCHMARK ================\n")
    print(f"{'Endpoint':<26} | {'Method':<6} | {'Status':<6} | {'Avg Latency (ms)':<16} | {'P95 (ms)':<10}")
    print("-" * 75)

    results = []
    for name, method, path in endpoints:
        latencies = []
        # Warm-up call
        if method == "GET":
            w_res = client.get(path)
            assert w_res.status_code == 200, f"Warmup failed for {path}: {w_res.status_code}"
            
            # 5 benchmark runs
            for _ in range(5):
                t0 = time.perf_counter()
                res = client.get(path)
                t1 = time.perf_counter()
                assert res.status_code == 200
                latencies.append((t1 - t0) * 1000.0)

        avg_lat = statistics.mean(latencies)
        p95_lat = sorted(latencies)[int(len(latencies) * 0.95)]
        results.append((name, method, avg_lat, p95_lat))
        print(f"{name:<26} | {method:<6} | {'200 OK':<6} | {avg_lat:>13.2f} ms | {p95_lat:>7.2f} ms")

    print("\n" + "=" * 75)
    total_avg = statistics.mean([r[2] for r in results])
    print(f"Overall Average Endpoint Response Time: {total_avg:.2f} ms across {len(endpoints)} tested endpoints")
    print("========================================================================\n")


if __name__ == "__main__":
    run_benchmark()
