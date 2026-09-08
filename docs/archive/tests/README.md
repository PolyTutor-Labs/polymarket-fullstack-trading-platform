# Archived tests

These files document removed or renamed production APIs. They are **not** collected by pytest (`python_files = test_*.py` under `tests/` only).

| File | Why archived |
|---|---|
| `copy_trading_legacy.py` | Tested `api.modules.copy_trading` (whale-mirror). Production is `copytrader` Option B: whale as selector, own post-only quotes. |
| `trading_engine_legacy.py` | Tested `TradingEngine` / multi-profile executor. Production class is `Engine` with a different cycle. |
