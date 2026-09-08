# Postgres 12 → 16 Upgrade: What to Know Before the 14th

On the 14th we're upgrading from Postgres 12 to Postgres 16.

## What's Happening

Writes will freeze for roughly 20 minutes during the upgrade. If you have a hotfix or a feature branch to land, plan around that window.

Read replicas stay up throughout. Dashboards, reports, and other read-heavy services should keep working without interruption.

## Why This Approach

We're keeping the freeze short and scoped, and leaving read traffic untouched, so the upgrade causes as little disruption as possible.

More details will follow as the date gets closer.
