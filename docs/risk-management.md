# Risk Management

## Why Risk Matters

Prediction markets can go to 0 or 1. This stack can lose money on bad models, thin books, stuck orders, or a live-guard mistake. Risk code reduces some of those paths; it cannot make trading safe.

## Risk Categories

Strategy, market, liquidity/slippage, latency, partial fills, stale data, API/WS failure, sizing, model/overfit, credentials, and rule changes.

## Implemented Controls

Confirmed in `api/services/risk_manager.py`, `executor.py`, `engine.py`, `halt.py`, `config.py`:

- Fail-closed `check()` on DB/book errors
- Reject price ≤0 or ≥1, size ≤0, missing `token_id`
- Exits (`SELL` / `is_exit`) skip entry gates so inventory can leave during a breaker
- Per-module circuit breaker pauses **entries**
- Global halt (`/api/engine/halt` + `ADMIN_TOKEN`) blocks new entries, not liquidation
- Spread required; reject if `spread >` tolerance (default 5¢, overridable via metadata)
- Directional edge floor (default 2%; income modules may set `metadata.min_edge`)
- $1 notional dust floor
- Duplicate resting BUY per (module, market, bracket, **token**)
- Single-market, correlated-bucket, per-module budget, and portfolio caps
- Daily / weekly realized-loss limits and peak-equity drawdown
- Depth: reject if size > 30% of visible book or book unreadable
- Auction aggregate price ceiling helper (`aggregate_price_ceiling_ok`)
- Dual live guard: `active` + production + `PAPER_MODE=false` + `ALLOW_LIVE_TRADING=true`
- Post-only live orders only
- Paper stale-order expiry
- Dashboard locked without `DASHBOARD_PASSWORD`

## Recommended Additional Controls

**Not implemented as a complete production program:**

- Independent kill-switch outside this process
- Exchange-side max-loss / venue circuit breakers
- Formal model-risk / walk-forward certification for every module
- Full taker-fee and rebate accounting in paper
- Multi-region failover
- Professional secret scanning in CI (repo has only `scripts/security/check_secrets.py`)
- Legal/compliance review

Do not treat the list above as features.

## Position Sizing

Modules size their own `Signal.size`. Shared Kelly math is in `api/modules/shared/signals.py` (fractional Kelly, vol/regime, 15% cap, late-auction 30% floor). The risk gate does **not** re-run Kelly; it checks notional vs caps.

## Execution Risk

Live acks are `submitted`, not fills. Paper BUY fills 50% per cross. Queue position is not modeled.

## Liquidity & Slippage

Spread and depth checks use a snapshot. Books can empty between check and fill.

## API / Network Risk

httpx/CLOB/WS can fail. User WS has a stall timeout (`fills.py`). Proxy: `POLYMARKET_PROXY_URL`.

## Data Quality Risk

Canonical parquet QA exists in `canonical_data.py` for research loads. Live trading trusts vendor APIs. Stale quotes produce wrong paper fills and bad edges.

## Strategy / Model Risk

Nine independent modules; one bug should not rewrite another (`BaseModule` seal). Correlation caps are coarse.

## Backtest Risk

See [backtesting.md](backtesting.md). A green research script is not a live proof.

## Credential Security

[SECURITY.md](../SECURITY.md). Rotate anything that was ever committed.

## Operational Checklist

1. `PAPER_MODE=true`, `ALLOW_LIVE_TRADING=false` while learning  
2. Migrations applied; dashboard password set  
3. `pytest` + secret scan  
4. Confirm module `status` before any live flip  
5. Know how to POST halt  

## What Risk Controls Cannot Guarantee

No loss bound, no fill quality, no model validity, no uptime, and no protection from your own live-guard configuration.
