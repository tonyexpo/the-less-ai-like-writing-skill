# Migration Moment: The Postgres 12 → 16 Upgrade

On the 14th, we're moving from Postgres 12 to Postgres 16.

## What's Happening

**Upgrade date: the 14th.** Mark it now so there's less scrambling later.

**Write freeze: roughly 20 minutes.** If you're pushing a hotfix or wrapping up a feature branch, plan around this window.

**Read replicas: staying up.** Writes pause, but reads continue. Dashboards, reports, and read-heavy services should keep running normally.

## Why This Approach

We're aiming for minimal disruption and clear communication, without cutting corners on the upgrade itself.

More details will follow as the date approaches. Thanks for bearing with the brief interruption.
