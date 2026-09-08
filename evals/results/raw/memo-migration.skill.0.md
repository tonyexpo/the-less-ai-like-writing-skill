# Postgres 12 → 16 Upgrade: The 14th

On the 14th, we're upgrading from Postgres 12 to Postgres 16.

## What's Happening

**Upgrade date: the 14th.** Mark it now so there's less scrambling later.

**Write freeze: roughly 20 minutes.** If you're planning a hotfix or wrapping up a feature branch, plan around this window.

**Read replicas: staying up.** Writes pause, but reads continue. Dashboards, reports, and other read-heavy services should keep working normally during the freeze.

## Why This Approach

The goal is minimal disruption: a short, scoped write freeze instead of a longer outage, with reads unaffected throughout.

More details will follow as the date approaches.
