# Historical backtest helper

This directory contains a standalone/historical backtesting implementation.

It is **not** wired into the current production FastAPI engine.

Current strategy research primarily lives under `research/`.

Use this implementation for study only unless independently validated.

## What is here

`engine.py` is a projection / regime / Kelly-style replay over:

```text
_DataMetricPulls/historical/{handle}/
```

Typical inputs (when those files exist):

- `dow_hourly_stats.json`
- auction tracking snapshots used by `run_backtest`

Typical outputs: a printed summary plus a `dict` with `summary`, `results`, and `totals` (invested, returned, P&L, ROI, win rate).

## What it is not

- Not imported by `api/`, `tests/`, or `scripts/`
- Not a supported CLI (`python -m backtest` is not a project command)
- Not the paper or live executor path
- Its original `all_trackings.json` source was removed in the canonical-data consolidation, so it will fail if invoked without reconstructed historical files

See [docs/backtesting.md](../docs/backtesting.md).
