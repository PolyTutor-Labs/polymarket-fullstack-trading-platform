# Backtesting

> A profitable backtest does not prove that a strategy will be profitable live.

## What backtesting is

A historical replay under stated fill, fee, and information assumptions. Those assumptions are usually kinder than a live book.

## What exists here

### Production engine — not a backtester

`api/services/engine.py` trades **current** markets on a timer. It is not an historical event loop.

### `backtest/engine.py` — standalone / historical helper

Projection/regime/Kelly-style functions over `_DataMetricPulls/historical/{handle}/`. **Nothing in `api/`, `tests/`, or `scripts/` imports it**, and the original `all_trackings.json` input was removed in the canonical-data consolidation. There is no supported CLI (`python -m backtest` is not a project command).

See `backtest/README.md`. Treat this file as historical code to read, not a certified runner.

### Research scripts — the real study surface

`research/backtests/pacing_backtest/`, `research/analysis/`, `research/experiments/`. These are one-off experiments. They may assume local parquet, Google Sheets, or X API tokens.

Canonical tables (when present) live under `_DataMetricPulls/canonical/` — posts, auctions, prices. Loaders: `api/modules/shared/canonical_data.py`.

Research code may contain experiment-specific assumptions and should be reviewed independently before reuse.

## How to run current backtests

There is **no single official command**. Typical study path:

1. Obtain or build canonical parquet (see `scripts/canonical/`).
2. Open the specific research script you intend to learn from.
3. Read its paths, date filters, and fill model.
4. Run that file only after you understand its side effects (Sheets upload, network).

Do not run research scripts against live trading credentials “to see what happens.”

## What the current engines do **not** uniformly model

Do not assume every script implements:

- taker/maker fees
- realistic queue priority
- latency
- partial fills
- look-ahead / leakage controls
- survivorship of delisted markets
- walk-forward locking

`PaperExecutor` (live paper) uses a 50% BUY chunk and top-of-book cross — that is **not** the research backtest engine.

Search a script for `fee`, `slippage`, and timestamp alignment before trusting P&L.

## Educational failure modes

| Concept | Why it matters here |
|---|---|
| Fees / slippage | Often omitted; live P&L shrinks |
| Latency | Tweet-speed edges die in a 5-minute cycle |
| Partial fills | Paper approximates; many scripts ignore |
| Look-ahead | Using resolution or future prints in features |
| Overfitting | Grid sweeps in `research/` without a locked holdout |
| Regime change | Elon/Trump pace is not stationary |
| Data leakage | Mixing train labels into test features |

## Output

Scripts write their own CSV/parquet/Sheets. `POLYTUTOR_OUTPUT_DIR` (default `./output`) is the portable scratch root. Nothing automatically publishes a “official backtest report.”

## Next

Read [paper-vs-live.md](paper-vs-live.md) and [risk-management.md](risk-management.md) before promoting any research result.
