# PolyTutor Learning Path

Learn → Build → Backtest → Simulate → Trade → Analyze → Improve

## Stage 1 — Understand the System

```text
README.md
    ↓
docs/architecture.md
```

Goals: name the components, separate `api/`+`web/` from `research/`, know that live needs a dual guard.

## Stage 2 — Run the System

```text
docs/getting-started.md
    ↓
pytest
    ↓
paper module status + ALLOW_LIVE_TRADING=false
```

Goals: healthz, dashboard login, 102 tests green. Do not flip live.

## Stage 3 — Study the Trading Pipeline

Read in order:

1. `api/main.py` — process lifetime  
2. `api/services/engine.py` — `cycle()`  
3. `api/modules/base.py` + one module, e.g. `api/modules/copytrader/module.py`  
4. `api/modules/shared/signals.py` — Kelly / rank helpers  
5. `api/services/risk_manager.py` — `check()`  
6. `api/services/executor.py` — paper vs live  
7. `api/services/fills.py` + `position_manager.py`  
8. `web/app/api/terminal/route.ts` + `web/app/page.tsx`  

Companion: [trading-system.md](trading-system.md), [paper-vs-live.md](paper-vs-live.md), [risk-management.md](risk-management.md).

## Stage 4 — Study Backtesting

```text
docs/backtesting.md
    ↓
backtest/engine.py          (orphaned — read, do not “run official”)
    ↓
research/backtests/pacing_backtest/
    ↓
scripts/canonical/          (how parquet is built)
```

Goal: list what a script assumes about fills and time. Remember: a profitable backtest does not prove live profit.

## Stage 5 — Build an Experiment

1. Form a hypothesis (example: “late-auction Kelly floor is too large”).  
2. Choose data (`canonical` vs live snapshots).  
3. Implement under `research/` first — not `api/modules/` until you want production.  
4. Add or extend `tests/` if you change shared math.  
5. Evaluate failure cases (empty book, elapsed=1, DB down).  
6. Only then consider a sealed module folder.

## Stage 6 — Advanced Study

Supported by this repo (no extra product claims):

- Execution: `clob.py`, post-only, dual guard  
- Risk: exposure + depth fail-closed  
- Data: `canonical_data.py`, `parquet_archive.py`  
- Dashboard: password middleware, 15s poll  
- Database: `supabase/migrations/`  
- Ops: `infra/`, `scripts/windows/`, Railway `railway.toml`  

## When the system fails

Stale books, down APIs, vanished liquidity, paper≠live fills, 5-minute cycle vs tweet latency, overfit research, or a mis-set live guard. Details: README “Known Limitations” and [risk-management.md](risk-management.md).
