# Security Policy

PolyTutor trading systems can interact with:

* wallets
* signing keys
* Polymarket credentials
* APIs
* databases
* external market-data services

## Never commit

* wallet private keys
* seed phrases / mnemonics
* exchange credentials
* Polymarket signing secrets
* API bearer tokens
* Supabase service-role secrets
* production `.env` files

Use `.env` for local credentials. Commit only `.env.example` with placeholders.

Any credential accidentally committed should be considered compromised and rotated immediately, even if later removed from the current branch.

Deleting a secret from the latest commit does not remove it from Git history. History must be rewritten, and the credential must still be rotated.

## Basic repository scan

```bash
python scripts/security/check_secrets.py
```

This scanner is a basic safeguard and does not guarantee that the repository is free of secrets. Use GitHub secret scanning, gitleaks, or trufflehog before a public release.

## Reporting

If you find a committed credential, rotate it first, then tell the maintainers so history can be sanitized before publish.
