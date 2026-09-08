# Paper vs Live

Modes that actually exist in this repository.

There is no shadow-trading mode. `SHADOW_MODE` is not a supported setting and is not read by `api/`.

## Summary

| Mode | Market data | Execution | Real capital | Purpose |
|---|---|---|---|---|
| Paper | Live books | Simulated maker (DB only) | No | Operate the loop safely |
| Live | Live books + CLOB | Real post-only limits | Yes | Real execution |
| Research backtest | Historical files | Script-specific simulation | No | Study, not the production engine |

## Paper — SUPPORTED

**How to get it:** leave `modules.status` as anything other than `active` (typically `paper`). Keep `ALLOW_LIVE_TRADING=false`.

- `executor_for` returns `PaperExecutor` (`api/services/executor.py`).
- Orders are inserted locally (`status=open`, `executor=paper`).
- Fills happen when `Engine.cycle` calls `check_fills` against live best bid/ask.
- BUY fills are **partial** (50% of size per crossing cycle); SELL/exits fill remaining size when crossed.
- No CLOB post. No wallet spend.

**Limitations:** Uses live quotes but not exchange queue, maker rebates, or taker fees. Crossing `best_ask <= limit` is optimistic vs a real book. Stale paper orders expire after `stale_order_hours`.

## Live — SUPPORTED (dual-guarded)

Live requires **all** of:

1. Supabase `modules.status = 'active'`
2. `ENVIRONMENT=production`
3. `PAPER_MODE=false`
4. `ALLOW_LIVE_TRADING=true`
5. `POLYMARKET_PRIVATE_KEY` (and wallet fields used by `clob.get_clob_client`)

`LiveExecutor` raises if the env guard fails. A dashboard status flip alone must not spend money.

- Orders: `clob.place_post_only` only — maker, never market/FAK (`api/services/clob.py`).
- Ack status is `submitted`. Fills arrive via `fills.py`.
- Real capital, gas, and platform rules apply.

**Limitations:** Geoblock, key/wallet type, tick size, min shares/notional, WS stalls, unmatched live GTD expiry (engine stale-sweep is paper-only).

## Research backtest — PARTIALLY SUPPORTED

- Many scripts under `research/backtests/` and `research/analysis/`.
- `backtest/engine.py` is a standalone/historical helper. It is **not imported** by `api/` / `tests/` / `scripts/` and its original `all_trackings.json` source was removed. See `backtest/README.md`. Do not treat it as the official runner.

See [backtesting.md](backtesting.md).

## Recommended study order

Paper with `ALLOW_LIVE_TRADING=false` → read risk/execution code → only then consider live, after you understand the dual guard and [DISCLAIMER.md](../DISCLAIMER.md).
