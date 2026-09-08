# Troubleshooting

## Backend does not start

```bash
python -m uvicorn api.main:app --reload --port 8010
```

- Activate `.venv` and `pip install -r requirements.txt`.
- Import errors: run from **repo root**, not `api/`.
- Missing `.env`: copy `.env.example`. Cycles will still error without Supabase, but the process should bind.

## Frontend does not start

```bash
cd web && npm install && npm run dev
```

Listens on **3010** (`package.json`). Docker maps host `3010` to that same process port.

## Environment variables missing

`web/next.config.js` reads the **root** `.env`. A `web/.env` is unnecessary for local next if the root file exists.

Dashboard **503** “dashboard locked”: set `DASHBOARD_PASSWORD`.

## Supabase configuration missing

Engine and `web/app/api/terminal/route.ts` need URL + service or anon keys. Empty tables → empty terminal, not necessarily a crash.

Apply `supabase/migrations/` in order on a new project.

## Data directory missing

`_DataMetricPulls` is gitignored. Production engine can cycle without it. Canonical/research scripts fail with file-not-found. Set `POLYTUTOR_DATA_DIR` if you keep data elsewhere.

## Port already in use

- API: user-facing **8010** (uvicorn `--port 8010` locally; Docker `8010:8000`).
- UI: user-facing **3010**.
- VPS/watchdog helpers may still talk to process port **8000** on the host where uvicorn is bound internally.

Change the uvicorn `--port` and `NEXT_PUBLIC_API_URL` / `CORS_ORIGINS` together.

## Tests fail

```bash
pytest
```

Must collect **only** `tests/` (102 tests). If research files appear, you are not using repo-root `pytest.ini`.

## Dashboard cannot reach API

The terminal primarily reads **Supabase**, not the FastAPI trade path. Health still uses `NEXT_PUBLIC_API_URL` (default `http://localhost:8010`). CORS default is `http://localhost:3010`.

`scripts/windows/start.bat` opens `/dashboard`; the Next app route is `/`. Use `http://localhost:3010/`.

## External APIs unavailable

CLOB/Gamma/tweet APIs down → empty signals, `no_spread_data` / `no_depth_data` rejects. Live WS stall: see `fills.py` stall timeout.

Optional `POLYMARKET_PROXY_URL` routes Polymarket HTTP through the Cloudflare worker (`api/services/polymarket_proxy.py`).

## Windows startup scripts fail

`scripts/windows/start.bat` expects `python` and `npm` on PATH and a `web/node_modules` install. It starts two extra consoles; closing them stops the servers.

## Secret scan fails

```bash
python scripts/security/check_secrets.py
```

Fix real credentials; do not weaken the scanner. Placeholders in `.env.example` should pass.

## Quality commands (copy-paste)

```bash
pytest
python -m compileall api tests backtest scripts research
python scripts/security/check_secrets.py
cd web && npm run lint && npm run typecheck && npm run build
```
