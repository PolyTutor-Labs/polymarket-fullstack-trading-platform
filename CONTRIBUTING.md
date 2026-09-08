# Contributing to PolyTutor Labs

Thank you for helping keep this an honest engineering lab.

## Contribution Types

Welcome:

- bug fixes
- documentation
- tests
- backtesting improvements (with stated assumptions)
- research experiments
- risk-control improvements
- performance and developer tooling

Not welcome:

- guaranteed-profit claims
- committed credentials or wallet keys
- undocumented live-trading parameter changes

## Development Setup

Follow [docs/getting-started.md](docs/getting-started.md).

## Before Opening a PR

```bash
pytest
python -m compileall api tests backtest scripts research
python scripts/security/check_secrets.py
cd web && npm run lint && npm run typecheck && npm run build
```

Frontend checks are required when `web/` changes.

## Testing Requirements

- Behavioral changes need tests under `tests/`
- Do not collect research scripts as production tests (`pytest.ini` uses `testpaths = tests`)
- Do not skip or weaken tests to force green

## Strategy / Research Contributions

- Document hypothesis, data, and failure cases
- Say what the experiment does **not** model (fees, latency, look-ahead)
- Keep new experiments in `research/` unless they are production modules
- Production modules belong in `api/modules/<name>/` with no cross-module imports (see `config/MODULE_ARCHITECTURE.md`)

## Security Rules

Never commit:

- wallet private keys or seed phrases
- Polymarket signing secrets
- API bearer tokens
- Supabase service-role keys
- production `.env` files

See [SECURITY.md](SECURITY.md). Run `python scripts/security/check_secrets.py`.

## Documentation Standards

- Document the actual repository; do not invent features
- Prefer `docs/` for long explanations; keep README short
- Do not add developer-machine paths

## Pull Request Expectations

- Small, reviewable diffs
- Honest description of risk if money-touching code changes
- No “this is profitable” language without a documented, audited study
