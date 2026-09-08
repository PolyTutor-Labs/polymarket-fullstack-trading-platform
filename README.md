# Polymarket Full-Stack Trading Platform

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](requirements.txt)
[![Next.js](https://img.shields.io/badge/Next.js-14-black?logo=nextdotjs)](web/package.json)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?logo=typescript&logoColor=white)](web/tsconfig.json)
[![PolyTutor Labs](https://img.shields.io/badge/PolyTutor%20Labs-Educational-1a365d)](#polytutor-labs)
[![tests](https://img.shields.io/badge/tests-102%20passing-brightgreen)](tests/)

> Learn how a complete Polymarket trading system connects market data, strategy modules, risk checks, execution, persistence, backtesting research, APIs, and a web dashboard.

**PolyTutor Labs · Intermediate · Educational / research**

PolyTutor Educational Release: v0.1.0

Learn → Build → Backtest → Simulate → Trade → Analyze → Improve

## About This Project

This repository is an educational PolyTutor Labs project for studying the architecture of a full-stack Polymarket trading system. It is a working engineering lab, not a guaranteed-profit bot and not an official Polymarket product.

The live application path is FastAPI (`api/main.py`) plus a scheduler-driven `Engine`, pluggable strategy modules, a fail-closed risk gate, paper or live executors, Supabase persistence, and a Next.js terminal. Research and historical experiments live separately under `research/` and must be reviewed before reuse.

## What You'll Learn

- how a Polymarket trading backend is structured
- how strategy modules emit `Signal` objects into a shared engine cycle
- how risk checks interact with execution
- how paper resting orders differ from live post-only CLOB orders
- how orders, fills, and positions are persisted
- how a Next.js dashboard reads application state
- how research scripts differ from production application code
- why a profitable historical study does not prove live performance

## What This Repository Contains

| Area | Role |
|---|---|
| `api/` | FastAPI app, engine, risk, execution, strategy modules |
| `web/` | Next.js 14 maker terminal |
| `backtest/` | Standalone/historical helper (not wired into FastAPI; see `backtest/README.md`) |
| `research/` | Experiments and historical analyses |
| `supabase/` | Schema migrations |
| `tests/` | Current automated suite (102 tests) |

## System Architecture

```
Market data (Gamma / CLOB / tweets)
        → strategy modules (api/modules/*)
        → risk_manager.check
        → PaperExecutor or LiveExecutor
        → Supabase (orders, trades, positions, signals)
        → Next.js dashboard (reads Supabase)
```

See [docs/architecture.md](docs/architecture.md) for the component diagram.

## Quick Start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env          # then fill placeholders
cd web && npm install && cd ..
python -m uvicorn api.main:app --reload --port 8010
# other terminal:
cd web && npm run dev         # http://localhost:3010
```

Full setup: [docs/getting-started.md](docs/getting-started.md).

## Trading Modes

| Mode | Status | Notes |
|---|---|---|
| Paper | Supported | Module status ≠ `active` → simulated maker fills vs live book |
| Live | Supported, dual-guarded | Needs `active` + `ENVIRONMENT=production` + `PAPER_MODE=false` + `ALLOW_LIVE_TRADING=true` |
| Research backtests | Partial | Scripts under `research/`; `backtest/engine.py` is standalone/historical |

Details: [docs/paper-vs-live.md](docs/paper-vs-live.md).

## Repository Structure

```text
api/         FastAPI entry, engine, risk, executors, strategy modules
backtest/    Standalone/historical helper (see backtest/README.md)
config/      Internal specs and historical notes (not the student path)
docs/        PolyTutor educational guides
infra/       Railway/VPS/Cloudflare helpers
research/    Experiments — not production-ready by default
scripts/     Ops, canonical data, Windows launchers, secret scan
supabase/    SQL migrations
tests/       Application test suite
web/         Next.js dashboard (port 3010)
```

`_DataMetricPulls/` is the local/runtime data root (gitignored). Override with `POLYTUTOR_DATA_DIR`.

## Documentation

| Guide | Purpose |
|---|---|
| [Getting Started](docs/getting-started.md) | Install and run |
| [Architecture](docs/architecture.md) | System map |
| [Trading System](docs/trading-system.md) | One trade through the stack |
| [Paper vs Live](docs/paper-vs-live.md) | Execution modes |
| [Backtesting](docs/backtesting.md) | Historical study limits |
| [Risk Management](docs/risk-management.md) | Implemented vs recommended controls |
| [Learning Path](docs/learning-path.md) | Guided study order |
| [Troubleshooting](docs/troubleshooting.md) | Common setup failures |
| [Disclaimer](DISCLAIMER.md) | Risk and educational use |
| [Contributing](CONTRIBUTING.md) | How to propose changes |
| [Security](SECURITY.md) | Credential rules |

## Testing & Quality

```bash
pytest
python -m compileall api tests backtest scripts research
python scripts/security/check_secrets.py
cd web && npm run lint && npm run typecheck && npm run build
```

## Known Limitations

This project can fail or diverge from expectations when market data is stale, APIs or WebSockets drop, liquidity vanishes, spreads widen, paper fills differ from live queue position, latency rises, strategy assumptions break, platform rules change, or historical models overfit. See [docs/risk-management.md](docs/risk-management.md).

## Security

Never commit `.env`, wallet keys, seed phrases, or API tokens. Scan with `python scripts/security/check_secrets.py`. Full policy: [SECURITY.md](SECURITY.md).

## Project History & Attribution

This PolyTutor Labs project is based on an existing Polymarket trading codebase and has been reorganized for educational use.

Original project: https://github.com/udt1234/polymarket-trading-bot-3.21.26

PolyTutor Labs work includes repository organization, portable paths, credential/history hardening, test stabilization, and this educational documentation. We do not claim original authorship of the entire trading codebase.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Prefer tests and honest failure notes over profit claims.

## Disclaimer

Educational and research use only. Not financial advice. Trading can lose capital. Backtests do not guarantee live results. Full text: [DISCLAIMER.md](DISCLAIMER.md).

## PolyTutor Labs

Learn → Build → Backtest → Simulate → Trade → Analyze → Improve

This is an engineering lab and trading school, not a signal service.
