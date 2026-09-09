"""
Comprehensive Automated Test Suite for Canonical FastAPI Intelligence & Control Layer.

Tests:
1. Database Repositories (Opportunity, Award, Organization, Recipient, Program)
2. Canonical Intelligence Modules (Fit, Capital Stack, Bankability, Win Rate, Teaming, Forecasting, Propensity, Rubric)
3. Grounded Agent Tools Manifest & Execution
4. In-Memory Asynchronous Job Runner
5. Observability Middleware Header Injection
6. V1 Versioned REST API Endpoints
"""

import sys
import asyncio
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).parent.resolve()
sys.path.insert(0, str(BACKEND_DIR))

from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.repositories import (
    OpportunityRepository,
    AwardRepository,
    OrganizationRepository,
    RecipientRepository,
    ProgramRepository,
)
from app.engine.profile import ProjectProfile
from app.intelligence import (
    score_opportunity_fit,
    solve_capital_stack,
    evaluate_technology_bankability,
    evaluate_win_rate,
    assemble_consortium_stack,
    forecast_upcoming_solicitations,
    rank_funder_propensity,
    get_agent_tools_manifest,
    execute_agent_tool,
)
from app.jobs.runner import default_job_runner, JobStatus

client = TestClient(app)


class TestIntelligenceArchitectureSuite(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = SessionLocal()

    @classmethod
    def tearDownClass(cls):
        cls.db.close()

    # ── 1. Database Repositories Tests ──

    def test_01_opportunity_repository(self):
        repo = OpportunityRepository(self.db)
        opps, total = repo.search_opportunities(limit=5)
        self.assertIsInstance(opps, list)
        self.assertGreaterEqual(total, 0)
        if opps:
            first_id = opps[0].id
            eager_opp = repo.get_by_id_eager(first_id)
            self.assertIsNotNone(eager_opp)
            self.assertEqual(eager_opp.id, first_id)
        print("[PASS] OpportunityRepository search and eager loading verified.")

    def test_02_award_repository(self):
        repo = AwardRepository(self.db)
        awards, total = repo.search_awards(limit=5)
        self.assertIsInstance(awards, list)
        self.assertGreaterEqual(total, 0)
        print("[PASS] AwardRepository search verified.")

    def test_03_organization_repository(self):
        repo = OrganizationRepository(self.db)
        orgs = repo.search_organizations(limit=5)
        self.assertIsInstance(orgs, list)
        print("[PASS] OrganizationRepository verified.")

    def test_04_recipient_repository(self):
        repo = RecipientRepository(self.db)
        recipients = repo.search_recipients(limit=5)
        self.assertIsInstance(recipients, list)
        print("[PASS] RecipientRepository verified.")

    def test_05_program_repository(self):
        repo = ProgramRepository(self.db)
        programs = repo.search_programs(limit=5)
        self.assertIsInstance(programs, list)
        print("[PASS] ProgramRepository verified.")

    # ── 2. Canonical Intelligence Modules Tests ──

    def test_06_capital_stack_solver(self):
        stack = solve_capital_stack(
            total_project_cost=5000000.0,
            grant_request=1500000.0,
            technology_type="energy_storage",
            location_state="NY",
            is_prevailing_wage_compliant=True,
            is_energy_community=True,
            is_domestic_content_compliant=False,
        )
        self.assertIn("capital_stack_breakdown", stack)
        self.assertIn("ira_tax_credits", stack)
        self.assertIn("blended_wacc_pct", stack)
        self.assertGreater(stack["ira_tax_credits"]["total_credit_pct"], 0)
        self.assertEqual(stack["total_project_cost"], 5000000.0)
        print(f"[PASS] Capital Stack Solver: Total ITC/Direct Pay = {stack['ira_tax_credits']['total_credit_pct']}% | Blended WACC = {stack['blended_wacc_pct']}%")

    def test_07_technology_bankability_rating(self):
        eval_res = evaluate_technology_bankability(
            technology_name="Flow Battery Long Duration Storage",
            trl=7,
            pilot_operating_hours=4000,
            field_deployments_count=5,
            degradation_rate_pct_annual=1.0,
            has_tier1_warranty_backing=True,
            has_ul_iec_safety_certification=True,
            has_independent_engineer_report=True,
            offtake_contract_status="pilot_agreement"
        )
        self.assertIn("composite_bankability_score", eval_res)
        self.assertIn("bankability_tier", eval_res)
        self.assertIn("pillars", eval_res)
        self.assertGreaterEqual(eval_res["composite_bankability_score"], 70.0)
        print(f"[PASS] Technology Bankability: Score = {eval_res['composite_bankability_score']} ({eval_res['bankability_tier']})")

    def test_08_predictive_forecasting(self):
        forecasts = forecast_upcoming_solicitations(self.db)
        self.assertIsInstance(forecasts, list)
        self.assertGreater(len(forecasts), 0)
        first_fc = forecasts[0]
        self.assertIn("predicted_title", first_fc)
        self.assertIn("agency", first_fc)
        self.assertIn("confidence_score", first_fc)
        print(f"[PASS] Predictive Forecasting: Found {len(forecasts)} forecasted solicitations.")

    def test_09_say_yes_propensity(self):
        profile = ProjectProfile(
            project_title="Brooklyn Microgrid Energy Storage",
            summary="Long duration energy storage for Brooklyn commercial grid reliability.",
            technology_areas=["energy storage", "microgrid"],
            target_location="Brooklyn NY"
        )
        scored_orgs = rank_funder_propensity(self.db, profile, limit=10)
        self.assertIsInstance(scored_orgs, list)
        self.assertGreater(len(scored_orgs), 0)
        self.assertIn("say_yes_score", scored_orgs[0])
        print(f"[PASS] Say-Yes Propensity: Top Funder = {scored_orgs[0]['organization_name']} (Score: {scored_orgs[0]['say_yes_score']})")

    def test_10_consortia_teaming(self):
        stack = assemble_consortium_stack(
            db=self.db,
            technology_area="energy storage",
            state_scope="NY"
        )
        self.assertIn("consortia_roles", stack)
        print(f"[PASS] Consortia Teaming: Assembled {len(stack['consortia_roles'])} stakeholder roles.")

    # ── 3. Agent Tools Manifest & Execution Tests ──

    def test_11_agent_tools_manifest(self):
        manifest = get_agent_tools_manifest()
        self.assertIsInstance(manifest, list)
        self.assertGreaterEqual(len(manifest), 8)
        tool_names = [t["name"] for t in manifest]
        self.assertIn("search_opportunities", tool_names)
        self.assertIn("solve_capital_stack", tool_names)
        self.assertIn("evaluate_technology_bankability", tool_names)
        print(f"[PASS] Agent Tools Manifest: {len(manifest)} grounded agent tools registered.")

    def test_12_execute_agent_tool(self):
        result = execute_agent_tool(
            tool_name="solve_capital_stack",
            arguments={
                "total_project_cost": 2000000.0,
                "grant_request": 500000.0,
                "technology_type": "solar"
            },
            db=self.db
        )
        self.assertNotIn("error", result)
        self.assertIn("capital_stack_breakdown", result)
        print("[PASS] execute_agent_tool('solve_capital_stack') executed cleanly.")

    # ── 4. Async Background Job Runner Tests ──

    def test_13_async_job_runner(self):
        import time

        async def dummy_task(x: int, y: int):
            await asyncio.sleep(0.01)
            return {"sum": x + y}

        job = default_job_runner.submit_job(
            job_type="test_calculation",
            coroutine_func=dummy_task,
            x=10,
            y=25,
            metadata={"caller": "unittest"}
        )
        self.assertIsNotNone(job.id)
        self.assertIn(job.status, [JobStatus.PENDING, JobStatus.RUNNING, JobStatus.COMPLETED])

        # Wait for thread execution to finish
        time.sleep(0.15)

        fetched_job = default_job_runner.get_job(job.id)
        self.assertEqual(fetched_job.status, JobStatus.COMPLETED)
        self.assertEqual(fetched_job.result, {"sum": 35})
        print(f"[PASS] Background Job Runner: Job [{job.id}] completed with result {fetched_job.result}.")

    # ── 5. Observability Middleware Header Test ──

    def test_14_observability_middleware_header(self):
        resp = client.get("/health")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("x-response-time-ms", resp.headers)
        duration = float(resp.headers["x-response-time-ms"])
        self.assertGreater(duration, 0.0)
        print(f"[PASS] Observability Middleware: X-Response-Time-Ms = {duration:.2f}ms")

    # ── 6. V1 Versioned REST API Endpoints Tests ──

    def test_15_v1_rank_opportunities_endpoint(self):
        payload = {
            "summary": "Next-generation solid-state lithium iron phosphate battery with advanced thermal safety.",
            "technology_areas": ["battery", "energy storage"],
            "sectors": ["grid", "commercial"],
            "trl_start": 6,
            "target_location": "NY",
            "limit": 5
        }
        resp = client.post("/api/v1/intelligence/rank-opportunities", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("results", data)
        print(f"[PASS] POST /api/v1/intelligence/rank-opportunities: Returned {len(data['results'])} ranked matches.")

    def test_16_v1_capital_stack_endpoint(self):
        payload = {
            "total_project_cost": 3000000.0,
            "grant_request": 750000.0,
            "technology_type": "hydrogen",
            "location_state": "NY",
            "is_prevailing_wage_compliant": True,
            "is_energy_community": False,
            "is_domestic_content_compliant": True
        }
        resp = client.post("/api/v1/intelligence/capital-stack", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("capital_stack", data)
        print("[PASS] POST /api/v1/intelligence/capital-stack: Solved capital stack successfully.")

    def test_17_v1_bankability_endpoint(self):
        payload = {
            "technology_name": "Thermal Energy Storage",
            "trl": 6,
            "pilot_operating_hours": 2000,
            "field_deployments_count": 4,
            "degradation_rate_pct_annual": 1.2,
            "has_tier1_warranty_backing": False,
            "has_ul_iec_safety_certification": True,
            "has_independent_engineer_report": False,
            "offtake_contract_status": "signed_loi"
        }
        resp = client.post("/api/v1/intelligence/bankability", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("bankability_evaluation", data)
        print("[PASS] POST /api/v1/intelligence/bankability: Evaluated bankability rating.")

    def test_18_v1_forecasts_endpoint(self):
        resp = client.get("/api/v1/intelligence/forecasts?horizon=all")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("forecasts", data)
        print(f"[PASS] GET /api/v1/intelligence/forecasts: Returned {data['count']} forecasts.")

    def test_19_v1_agent_tools_endpoints(self):
        resp_manifest = client.get("/api/v1/agents/tools")
        self.assertEqual(resp_manifest.status_code, 200)
        manifest_data = resp_manifest.json()
        self.assertEqual(manifest_data["status"], "success")
        self.assertGreaterEqual(manifest_data["tools_count"], 8)

        # Test execute-tool endpoint
        exec_payload = {
            "tool_name": "search_opportunities",
            "arguments": {"status": "open", "limit": 3}
        }
        resp_exec = client.post("/api/v1/agents/execute-tool", json=exec_payload)
        self.assertEqual(resp_exec.status_code, 200)
        exec_data = resp_exec.json()
        self.assertEqual(exec_data["status"], "success")
        self.assertIn("output", exec_data)
        print("[PASS] GET /api/v1/agents/tools and POST /api/v1/agents/execute-tool verified.")

    def test_20_v1_jobs_endpoints(self):
        resp = client.get("/api/v1/jobs")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "success")
        self.assertIn("jobs", data)

        resp_workers = client.get("/api/v1/jobs/ingestion-workers")
        self.assertEqual(resp_workers.status_code, 200)
        workers_data = resp_workers.json()
        self.assertEqual(workers_data["status"], "success")
        self.assertIn("workers", workers_data)
        print("[PASS] GET /api/v1/jobs and GET /api/v1/jobs/ingestion-workers verified.")


if __name__ == "__main__":
    unittest.main()
