# U.S. Energy Innovation Database by Clean Energy Research, LLC

**The Upstream Innovation Intelligence Terminal for Advanced Energy**  
**Live Platform:** [terminal.aixenergy.io](https://terminal.aixenergy.io)

A high-performance intelligence and decision-support terminal indexing 56,413 active and historical funding awards, $104.16B in non-dilutive capital, patent linkages, venture capital rounds, and organizational networks across 140+ federal agencies, state energy offices, and electric utilities, backed by the **U.S. Energy Innovation Database** published by **Clean Energy Research, LLC**.

> **LEGAL, ETHICS & PUBLIC RECORDS COMPLIANCE NOTICE**
> 
> - **Independent Research Platform**: The *Energy Innovation Terminal* and *U.S. Energy Innovation Database* are independent computational research and decision-support tools created by Clean Energy Research, LLC outside of any official government agency capacity. This platform is **NOT** an official tool, publication, or service of NYSERDA, the State of New York, the US Department of Energy (DOE), ARPA-E, CEC, MassCEC, NSF, or any other government entity. No endorsement, sponsorship, or official affiliation is stated or implied.
> - **Exclusively Public Open Records**: All solicitations, awards, dockets, and patent linkages are compiled **strictly from publicly accessible open government records** (e.g., NY Open Data, Grants.gov, USAspending, official agency portals, USPTO). No non-public, internal, confidential, or deliberative agency data is used or contained herein.
> - **Resource Separation**: No government equipment, official working hours, facilities, or public agency funds were used in the creation or hosting of this platform.
> - **No Official Standing or Funding Guarantee**: Use of this platform does not constitute an official grant application, nor does it guarantee funding, evaluation preference, or scoring advantage with NYSERDA, US DOE, or any funding organization. Official applications must be submitted via each agency's designated portal.
> - **Nominative Fair Use**: All agency names, acronyms, and logos are used solely for nominative identification and public-interest informational reference under 15 U.S.C. § 1125.

---

## Commercial Licensing Architecture

| Plan Tier | Target Customer | Included Seats & Quotas | Monthly Price | Annual Rate |
| :--- | :--- | :--- | :--- | :--- |
| **Practitioner Seat** | Solo Grant Writers & Boutique Advisors | 1 Named Seat • Unlimited FOA Shreds • 56k+ Database • Vector PDF Exports | **$1,500 / mo** | **$15,000 / yr** ($1,250/mo) |
| **Boutique Team** | Grant Writing Firms & Gov Affairs Practices | 3 Team Seats • Consortia Teaming Radar • White-Label PDFs • Predictive Radar | **$4,500 / mo** | **$45,000 / yr** ($3,750/mo) |
| **Practice Group** | Consulting Firms & Clean Tech Practice Groups | 5–10 Seats • Team Collaboration • Central Billing • Priority Tech Support | **$7,500 / mo** | **$75,000 / yr** ($6,250/mo) |
| **Enterprise Practice** | Global Energy Advisory (ICF, Guidehouse, Big 4) | 15+ Seats • Direct REST API • Custom Ingestion Feeds • Dedicated Support SLA | **Custom Invoice** | **Volume Enterprise SLA** |

---

## Key Capabilities & Intelligence Modules

1. **AI Matching & Workstream Decomposition Engine (`/`)**
   - Ingests raw project concepts and identifies primary technology sectors, activity types, and TRL stages.
   - Deterministic eligibility screening (**PASS / FAIL / UNKNOWN**) per solicitation rule.
   - Multi-dimensional scoring and multi-agency capital stacking across federal and state funding streams.

2. **AI FOA Shredder & Proposal Studio (`/proposals`)**
   - Decomposes 80+ page federal FOAs into 4-part PDF blueprints in 10 seconds.
   - Instant compliance matrices, reviewer scoring rubrics, and red-team win angles.

3. **Nationwide Opportunities Index (`/opportunities`)**
   - Active and recurring solicitations from **US DOE (EERE, ARPA-E, OCED, MESC), CEC (EPIC, Clean Transportation), MassCEC, NYSERDA, NSF, SBIR/STTR, and 140+ state energy agencies & utilities**.
   - Automated deadline extraction, cost-share requirements, and concept paper requirements.

4. **Historical Awards & GIS Map Studio (`/awards`)**
   - **56,413 geocoded historical award records ($104.16B capital tracked)**.
   - High-resolution publication exports (4K / 300 DPI vector PDFs) for presentations and executive briefings.

5. **Decision-Maker Say-Yes Matrix & Contacts (`/contacts`)**
   - Direct directory of program managers, grant evaluators, and agency points of contact across 140+ entities.

6. **Venture Capital & Patent Intelligence (`/venture-patents`)**
   - Private capital equity rounds cross-referenced with non-dilutive public grants.
   - USPTO patent citations, assignee linkages, and clean technology IP tracking.

7. **Entity Knowledge Graph & Network Analytics (`/network`)**
   - Prime contractors, subcontractors, university tech transfer offices, and national lab partners.
   - Thematic community clustering and institutional network density analysis.

8. **Multi-Stage Capital Flow Sankey Visualizer (`/sankey`)**
   - Interactive flow visualization tracing capital from source agencies through programs, technology verticals, and recipient categories.

9. **Macro Market Trends & Quantitative Analytics (`/trends`)**
   - Time-series funding distributions, technology domain trajectories, and state-by-state funding heatmaps.

10. **Executive Strategic Monograph PDF Generator (`/reports`)**
    - Multi-page, publication-grade executive diligence reports with vector charts, GIS maps, and strategic syntheses.

---

## Multi-Agency Data Coverage

| Jurisdiction / Tier | Covered Agencies & Entities |
| :--- | :--- |
| **Federal** | US Department of Energy (DOE), ARPA-E, NSF, SBIR/STTR, Grants.gov, USAspending |
| **State Energy Offices** | California Energy Commission (CEC), MassCEC (MA), NYSERDA (NY), Colorado CEO, Illinois DCEO, Iowa IEDA, Maine Efficiency, Maryland MEA, Minnesota Commerce, New Mexico EMNRD, NJEDA (NJ), Pennsylvania DEP, Texas SECO, Virginia Energy, Washington Commerce, Wisconsin OEI |
| **Utilities & Authorities** | ConEd, National Grid, NYPA, LIPA, NYSEG, Orange & Rockland, Central Hudson, PSEG LI, RG&E, and Nationwide Utility Registry |
| **Philanthropic & Venture** | Breakthrough Energy, Gates Foundation, Bezos Earth Fund, Hewlett, MacArthur, Kresge, Barr, VC rounds & USPTO patents |

---

## 3-Layer Matching Architecture

```
Layer 1: Deterministic Eligibility Screening
  → PASS / FAIL / UNKNOWN per statutory rule
  → Explicit FAIL cannot be overridden by semantic similarity

Layer 2: Multi-Dimensional Fit Scoring
  → Technology fit, activity fit, funding scale, FTS relevance, objective alignment
  → Weighted scoring with transparent dimension breakdown

Layer 3: Strategic Reasoning & Capital Stacking
  → LLM synthesis and proposal co-pilot (Gemini / OpenAI / Anthropic)
  → Operates fully without LLM — search, indexing, and deterministic filtering remain 100% active
```

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+

### Setup

```bash
# Clone and enter project
cd nyserda-innovation-match

# Create .env from example
copy .env.example .env

# Set up Python virtual environment
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt

# Bootstrap database with live data
.venv\Scripts\python.exe backend\bootstrap.py

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Run Application

```bash
# Terminal 1: Start API server
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend

# Terminal 2: Start frontend dev server
cd frontend
npm run dev
```

Open **http://localhost:5173** in your browser.

---

## Tech Stack

### Backend
- **FastAPI** — High-performance async REST API
- **PostgreSQL / SQLite FTS5** — Full-text search with BM25 / Porter stemming
- **ReportLab & FPDF2** — Publication-grade PDF monograph & report generation
- **httpx & BeautifulSoup4** — Automated multi-agency ingestion pipeline
- **Pydantic v2 & SQLAlchemy 2** — Robust data modeling and ORM

### Frontend
- **React 19** with **TypeScript**
- **Vite 8** — Next-gen frontend tooling
- **Tailwind CSS** — Utility-first styling
- **TanStack Query v5** — Server state synchronization and caching
- **MapTiler SDK & MapLibre GL** — High-DPI GIS cartographic mapping
- **Sigma.js & Graphology** — WebGL-accelerated entity network graph rendering
- **Lucide React** — Crisp iconography

---

---

## Commercial Production Deployment

### 1. Docker Compose (Full Stack with PostgreSQL)

The easiest way to launch the full platform in staging or production is using Docker Compose:

```bash
# 1. Configure environment variables
copy .env.example .env

# 2. Build and start services (PostgreSQL + FastAPI App + Static React SPA)
docker compose up -d --build

# 3. View container health & logs
docker compose ps
docker compose logs -f app
```

The terminal interface will be accessible immediately at **http://localhost:8000**.

### 2. Single-Container Cloud Deployment (Google Cloud Run, AWS App Runner, Fly.io, Render)

The multi-stage `Dockerfile` compiles the React frontend assets into `frontend/dist` and packages the FastAPI production server to serve both the high-performance async API and the SPA frontend from a single lightweight container.

```bash
# Build the production image
docker build -t energy-innovation-terminal:latest .

# Run container pointing to managed PostgreSQL cluster (e.g. AWS RDS, Google Cloud SQL, Neon, Supabase)
docker run -d -p 8000:8000 \
  -e DATABASE_URL="postgresql+psycopg2://user:password@pg-host:5432/nyserda_innovation" \
  -e ENVIRONMENT="production" \
  -e JWT_SECRET_KEY="your-production-secret-key" \
  -e OPENAI_API_KEY="your-openai-key" \
  --name energy_terminal \
  energy-innovation-terminal:latest
```

### 3. Health Probes & Monitoring

- **Health Probe**: `GET /health` and `GET /api/health`
  - Returns `200 OK` with detailed database connectivity, engine dialect, service version, and environment status.
  - Used by Kubernetes liveness/readiness probes and Docker container healthchecks.
- **SEO & Sitemaps**: `GET /sitemap.xml`, `GET /sitemap-opportunities.xml`, `GET /sitemap-recipients.xml`
- **Generative Engine Optimization (GEO)**: `GET /llms.txt`, `GET /ai.txt`
- **RSS Syndication Feed**: `GET /feed/rss/opportunities.xml`

---

## Environment Variables Reference

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `DATABASE_URL` | `postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/nyserda_innovation` | Primary PostgreSQL database connection string |
| `ENVIRONMENT` | `production` | Runtime mode (`development`, `staging`, `production`) |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated list or `*`) |
| `JWT_SECRET_KEY` | `energysignal-jwt-secret-key-2026-secure-token` | Cryptographic secret for signing JWT auth tokens |
| `LLM_PROVIDER` | `none` | Active LLM synthesis provider (`openai`, `gemini`, `anthropic`, `none`) |
| `OPENAI_API_KEY` | `""` | OpenAI API key for AI proposals, report synthesis, and match analysis |
| `GEMINI_API_KEY` | `""` | Google Gemini API key |
| `ANTHROPIC_API_KEY` | `""` | Anthropic Claude API key |
| `TAVUS_API_KEY` | `""` | Tavus.io API key for Conversational Video Advisor |
| `PUBLIC_BENEFIT_MODE` | `true` | When true, grants open access to all terminal features |
| `ADMIN_PRIMARY_EMAIL` | `bowens@aixenergy.io` | Default administrative account email |
| `ADMIN_GMAIL_USER` | `bowens@aixenergy.io` | Admin outbound/inbound sync Gmail user |
| `ADMIN_GMAIL_PASSWORD` | `""` | Gmail App Password for correspondence sync |

---

## Suggested Citation

When citing data, graphics, or reports generated by this platform, please use the following citation formats:

### APA (7th Edition)
```text
Owens, B. N. (2026). U.S. Energy Innovation Database (Version 3.5.0) [Data set and software]. Clean Energy Research, LLC. https://terminal.aixenergy.io
```

### BibTeX
```bibtex
@misc{owens2026energyinnovation,
  author = {Brandon N. Owens},
  title = {U.S. Energy Innovation Database},
  year = {2026},
  publisher = {Clean Energy Research, LLC},
  url = {https://terminal.aixenergy.io},
  note = {Multi-agency cross-jurisdictional intelligence covering 56,413 awards, $104.16B capital, and 140+ federal & state utilities}
}
```

### Chicago
```text
Owens, Brandon N. 2026. "U.S. Energy Innovation Database." Clean Energy Research, LLC. https://terminal.aixenergy.io.
```

---

## Guardrails & Integrity

- **Datastore is Source of Truth** — Zero hallucinations of funding amounts, deadlines, or statutory rules.
- **Strict Eligibility Integrity** — Hard eligibility disqualifications cannot be overridden by semantic relevance.
- **Attribution & Transparency** — Every record, stat, and graphic is cited with its authoritative public source (`U.S. Energy Innovation Database`, Clean Energy Research, LLC).

