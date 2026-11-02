# Render cutover

The terminal frontend stays on Cloudflare Pages (`energy-innovation-terminal`, `terminal.aixenergy.io`).

Two Render services were serving this repo:

| Render service | What it actually ran | State seen 2026-11-02 |
| --- | --- | --- |
| `energy-innovation-api` | Free Python web service, `uvicorn app.main:app`, root directory `backend`. This is the API the frontend calls. | Suspended |
| `energy-innovation-daily-sync` | Docker cron `python -m app.jobs.cron_sync --source all` at 06:00 UTC | Suspended |

`aixenergy-scout` and `aixenergy-scout-worker` belong to a different repository. Leave them alone.

The in-process schedulers inside the API (hourly ingestion, daily news, and `app.cron.daily_routine` at 06:00 UTC) only ran while that free web service was awake. The cron was the reliable daily job. It ran the feed sync and a digest. The GitHub Actions workflow runs the fuller routine: news, feed sync, digest, usage summary, and the data-quality audit.

## Where things run now

- **Daily update:** `.github/workflows/daily-update.yml`, 06:00 UTC, `python -m app.cron.daily_routine`.
- **API:** Worker `energy-innovation-api` at `https://energy-innovation-api.bowens-b7b.workers.dev`. The Worker proxies to one FastAPI container (`Dockerfile.api`, instance type `basic`, 1 GiB). The container sleeps after 15 minutes with no requests. `ENABLE_BACKGROUND_SCHEDULERS=false` and `SKIP_STARTUP_WARM=true` are set on that process.
- **Frontend:** `frontend/.env.production` sets `VITE_API_URL` to that Worker. Pages deploy bakes the value in at build time.

The FastAPI app stays a container because request handlers use psycopg2, numpy, matplotlib, PyMuPDF, and reportlab. A Worker isolate is 128 MB and, on the free plan, 10 ms of CPU. A static JSON dump cannot answer parameterized search, streaming chat, or PDF routes. Supabase remains the Postgres database the API already uses.

Containers require the Workers Paid plan ($5/month minimum). A `basic` instance bills memory only while it is awake (25 GiB-hours included, then $0.0000025 per GiB-second). One shared instance serves every visitor. CPU is billed only while the process is actually working. The Pages keep-alive ping is every 4 minutes while a tab is visible, which holds the container open during a session and lets it sleep afterward.

The first request after sleep waits until `/health` responds. Budget about two minutes for image start plus Python import. Later requests in that session are normal.

## Secrets

Set values in the dashboards. Do not commit them. Copy `DATABASE_URL` and `OPENAI_API_KEY` from the suspended Render service `energy-innovation-api` (Environment) when those values are already correct.

Use the Supabase **session pooler** URI (IPv4 host, port 5432, `sslmode=require`) if a direct `db.<project>.supabase.co` host times out from Cloudflare. The app accepts `postgresql://` and rewrites it to the psycopg2 driver.

### GitHub Actions repository secrets

Repository: `brandonnowens/energy-innovation-terminal`, Settings → Secrets and variables → Actions.

| Name | Required | Used by |
| --- | --- | --- |
| `DATABASE_URL` | yes | `daily-update.yml` |
| `OPENAI_API_KEY` | no | digest and news phases that call an LLM |
| `ANTHROPIC_API_KEY` | no | LLM fallback |
| `GEMINI_API_KEY` | no | LLM fallback |
| `SOCRATA_APP_TOKEN` | no | Socrata feeds |
| `GRANTS_GOV_API_KEY` | no | Grants.gov |
| `SAM_GOV_API_KEY` | no | SAM.gov |
| `CLOUDFLARE_API_TOKEN` | already used by Pages | `deploy-api.yml` |
| `CLOUDFLARE_ACCOUNT_ID` | already used by Pages | `deploy-api.yml` |

The Cloudflare token needs Workers Scripts edit and Containers edit in addition to the Pages permission it already has. A 403 on the deploy workflow means the token is missing one of those.

### Wrangler secrets for the API Worker

These are Worker secrets, not GitHub secrets. From `workers/energy-innovation-api` after the Worker exists:

```bash
npx wrangler secret put DATABASE_URL
npx wrangler secret put OPENAI_API_KEY
npx wrangler secret put ANTHROPIC_API_KEY
npx wrangler secret put GEMINI_API_KEY
npx wrangler secret put JWT_SECRET_KEY
npx wrangler secret put GHOST_ADMIN_API_KEY
npx wrangler secret put GHOST_WEBHOOK_SECRET
npx wrangler secret put ADMIN_GMAIL_PASSWORD
npx wrangler secret put TAVUS_API_KEY
npx wrangler secret put SOCRATA_APP_TOKEN
npx wrangler secret put GRANTS_GOV_API_KEY
npx wrangler secret put SAM_GOV_API_KEY
```

`DATABASE_URL` is required. The Worker refuses to start the container without it. Set `JWT_SECRET_KEY` only when the Render service overrode it; otherwise omit it and existing tokens keep validating. Set the LLM, Ghost, Gmail, and Tavus secrets when those features should keep working. Omit a secret to leave that feature on the application default.

Changing a secret applies on the next cold start. After `wrangler secret put`, redeploy or wait for the container to sleep so the new value is picked up.

## Manual steps

Do these in order. Do not delete or unsuspend anything on Render until the new API answers.

1. Confirm the Cloudflare account can use Containers (Workers Paid).
2. Add the GitHub Actions secrets listed above. `DATABASE_URL` is the one the daily job checks for.
3. Deploy the API from this branch before merging, so the Worker and image exist first:
   - Actions → **Deploy API container** → Run workflow → branch `cursor/render-cutover-a834` (or `main` after merge), or locally from the repo root:

     ```bash
     cd workers/energy-innovation-api
     npm ci
     npx wrangler login
     npx wrangler deploy
     ```

     The first deploy builds `Dockerfile.api` and provisions the image. That takes several minutes. `wrangler deploy` can return before the image is ready.
4. Put the Wrangler secrets, at least `DATABASE_URL` and `OPENAI_API_KEY`.
5. Wait until the image shows ready in the Cloudflare Containers dashboard, then:

   ```bash
   curl -sS https://energy-innovation-api.bowens-b7b.workers.dev/health
   ```

   Expect `"status": "ok"` and `"database": {"status": "healthy"}`. A connection timeout means switch `DATABASE_URL` to the Supabase session pooler and cold-start again.
6. Merge the pull request (or re-run **Production Deployment to Cloudflare Pages**). The Pages build reads `frontend/.env.production` and publishes `terminal.aixenergy.io` against the Worker.
7. Open `https://terminal.aixenergy.io`, let the first load finish, and confirm opportunities or the digest return data. Chat needs `OPENAI_API_KEY` on the Worker.
8. Run **Daily data update** once with `workflow_dispatch` (skip ingestion the first time if you only want to prove the database connection). The schedule runs only from `main`, at 06:00 UTC, after this workflow file is on `main`.
9. After steps 5–8 succeed, delete these two Render services in the dashboard. They are already suspended. Deleting them is the step that stops the Render bill for this app.
   - `energy-innovation-api` — https://dashboard.render.com/web/srv-dag8bh2jnfac73dremf0
   - `energy-innovation-daily-sync` — https://dashboard.render.com/cron/crn-dage78142hec73bteu50

   `render.yaml` still lists the legacy services so a blueprint sync does not remove them on its own. After the dashboard delete, the blueprint entries can be removed in a follow-up.

Optional: attach `api.terminal.aixenergy.io` to the Worker and set `VITE_API_URL` to that hostname, then redeploy Pages. Until that DNS record exists, the `workers.dev` hostname is the API.
