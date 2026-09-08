# Archived session notes (sanitized)

This is a public-safe remnant of an internal operator handoff. Hostnames, IPs,
accounts, wallets, project IDs, and deployment credentials were removed.

It is **not** current project configuration. Student path: [docs/](../).

## Educational takeaways

1. **Merged is not deployed.** Check the running SHA on the live host before
   diagnosing strategy logic. Repo-correct code can still be absent in production.
2. **Circuit breakers should be per module.** A single global loss counter can
   pause unrelated strategies.
3. **Alerts must be observable.** Do not wrap notifications in `except: pass`.
   Record whether the alert was delivered.
4. **Rotating a secret does not stop a running process.** A container keeps the
   environment it started with until it is restarted or removed.
5. **Enumerate every service.** A stale writer can live under an unrelated name.
6. **Paper P&L is not a validated live edge.** A quiet or losing paper module
   should not be described as a proven survivor.

## Where live notes belong now

- Engineering mistakes: `config/lessons.md` (no private infrastructure details)
- Public architecture: [docs/architecture.md](../architecture.md)
- Risk vs implementation: [docs/risk-management.md](../risk-management.md)
