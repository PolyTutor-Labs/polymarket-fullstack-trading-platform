# Trading System

Lifecycle of one engine cycle, as implemented today.

```text
Market discovery / books / tweets
        ↓
module.evaluate(module_id) → Signal[]
        ↓
risk_manager.check (exits first)
        ↓
executor_for(modules.status)
        ↓
orders row (paper open | live submitted)
        ↓
fills (paper book-cross | live WS/REST)
        ↓
positions + trades
        ↓
dashboard / health
```

## 1. Market data

**What happens:** Modules call shared helpers (Gamma discovery, CLOB books, tweet counts, whale trades).  
**Files:** `api/modules/shared/discovery.py`, `tweet_count.py`, `windows.py`, `fair_value.py`, `api/modules/*/data.py`, `api/services/clob.py`.  
**Inputs:** Live HTTP/WS, optional `_DataMetricPulls`.  
**Outputs:** Prices, token ids, auction windows.  
**Failures:** Timeouts, empty books, geoblock; risk then rejects `no_spread_data` / `no_depth_data`.

## 2. Decision / signal

**What happens:** `BaseModule.evaluate` runs `_evaluate_async` and returns `risk_manager.Signal` objects (`price`, `size`, `token_id`, `edge`, `is_exit`, …).  
**Files:** `api/modules/base.py`, each `api/modules/<name>/module.py`.  
Registered strategies include `arb_scanner`, `copytrader`, `elon_late_arb`, `elon_reversion`, `lp_rewards`, `market_maker`, `mirror_trader`, `s2_basket_hold`, `sports_sweep`.  
**Failures:** One module exception is caught; other modules continue (`engine.py`).

## 3. Candidate trade

A `Signal` is a proposed limit, not an order. Kelly/ranking helpers live in `api/modules/shared/signals.py` and are used by some modules/tests; the risk gate does not recompute Kelly.

## 4. Risk validation

**What happens:** `check(signal, breaker_tripped)` fail-closes. SELLs / `is_exit` skip entry gates (breaker still pauses **entries** only).  
**File:** `api/services/risk_manager.py`.  
**Rejects include:** bad price/size, missing token, no spread, edge floor, dust notional, duplicate resting BUY, exposure caps, daily/weekly loss, drawdown, no/excess depth, DB errors.  
**Output:** `RiskVerdict`; row written via `_record_signal`.

## 5. Execution

**File:** `api/services/executor.py`.

| Path | When | Behavior |
|---|---|---|
| `PaperExecutor` | `modules.status` ≠ `active` | Inserts `orders` status `open`, post-only GTC, no CLOB |
| `LiveExecutor` | status `active` **and** dual env guard | `clob.place_post_only`; ack is `submitted`, not filled |

Live constructor refuses unless `environment=production`, `paper_mode=false`, `allow_live_trading=true`, and a private key exists.

## 6. Order / fill handling

- Paper: `PaperExecutor.check_fills` crosses live top-of-book; BUY fills in 50% chunks (`QUEUE_FILL_FRAC`).
- Live: `api/services/fills.py` user WebSocket + `reconcile_open_orders` REST. `MATCHED` is provisional; `CONFIRMED` is on-chain settled.

**Failures:** Stall watchdog on half-open sockets; missing `orderID` → rejected.

## 7. Position state

`api/services/position_manager.py` applies buy/sell fills; engine also sweeps `closing` and expires stale **paper** orders (`stale_order_hours`, default 6).

## 8. Persistence / metrics

Supabase tables include `modules`, `orders`, `trades`, `positions`, `signals`, `logs`, snapshots. Migrations: `supabase/migrations/`.

## 9. API / dashboard

- `GET /api/healthz` — process up.
- `GET /api/engine/health` — cycling vs trading vs stuck.
- `POST /api/engine/halt` — `ADMIN_TOKEN`; stops **new entries**, does not flatten positions.
- UI: `web/app/page.tsx` every 15s via `web/app/api/terminal/route.ts`.
