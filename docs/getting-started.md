# Getting Started

## Requirements

The repo does **not** pin a Python or Node version in an engines file.

- Python 3.11+ is recommended (the current test suite was run on 3.11).
- Node.js with `npm` (Next.js 14 in `web/package.json`).
- A Supabase project if you want the engine and dashboard to persist/read state.
- Optional: Polymarket credentials only if you study live execution.

## Clone the Repository

```bash
git clone <your-fork-or-local-path>
cd polymarket-fullstack-trading-platform
```

## Python Environment

```bash
python -m venv .venv
```

Windows: `.venv\Scripts\activate`  
Unix: `source .venv/bin/activate`

## Install Backend Dependencies

```bash
pip install -r requirements.txt
```

`api/requirements.txt` is a slimmer Railway-oriented set. Local tests use the root file (includes pytest, pandas, numpy).

## Install Frontend Dependencies

```bash
cd web
npm install
cd ..
```

## Environment Configuration

Copy `.env.example` to `.env` at the **repository root**. `web/next.config.js` loads that root file for local Next.js.

Required to do useful work:

| Variable | Purpose |
|---|---|
| `SUPABASE_URL` / `SUPABASE_SERVICE_KEY` | Engine + server dashboard queries |
| `NEXT_PUBLIC_SUPABASE_URL` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Frontend client |
| `DASHBOARD_PASSWORD` | Dashboard unlock; empty → HTTP 503 |
| `NEXT_PUBLIC_API_URL` | Default `http://localhost:8010` |
| `PAPER_MODE` | Default `true` |
| `ALLOW_LIVE_TRADING` | Default `false` — keep it false while learning |

Do not put real secrets in git. See [SECURITY.md](../SECURITY.md).

## Local Data Requirements

Large parquet archives live under `_DataMetricPulls/` (gitignored). Override with `POLYTUTOR_DATA_DIR`. The engine can run without them; research/canonical scripts cannot.

Apply `supabase/migrations/` to an empty project if you are standing up a new database.

## Start the Backend

From the repo root, with venv active:

```bash
python -m uvicorn api.main:app --reload --port 8010
```

Health: `GET http://localhost:8010/api/healthz` → `{"status":"ok","running":true}`.

On start the process **discovers modules and starts the scheduler**. Without Supabase, cycles will log DB errors.

## Start the Dashboard

```bash
cd web
npm run dev
```

Open `http://localhost:3010` (not `/dashboard` — the app page is `/`). Enter `DASHBOARD_PASSWORD`.

Windows helper: `scripts/windows/start.bat` (API 8010, UI 3010).

## Verify the System

1. `/api/healthz` returns ok.
2. Dashboard login succeeds.
3. `/api/engine/health` returns cycle metadata (needs a running API).

## Run Tests

```bash
pytest
python -m compileall api tests backtest scripts research
```

Expect 102 passed.

## Run Security Scan

```bash
python scripts/security/check_secrets.py
```

## Common Setup Problems

- **Dashboard 503**: `DASHBOARD_PASSWORD` unset.
- **API up, empty terminal**: Supabase keys missing or migrations not applied.
- **Port in use**: 8010 / 3010 taken.
- **docker-compose ports**: file uses 8000/3000; local scripts use 8010/3010.

More: [troubleshooting.md](troubleshooting.md).

## Next Steps

[architecture.md](architecture.md) → [trading-system.md](trading-system.md) → [learning-path.md](learning-path.md).
