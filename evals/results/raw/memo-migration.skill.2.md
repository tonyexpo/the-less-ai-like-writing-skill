# Postgres 12 → 16 Upgrade: the 14th

On the 14th, we're moving from Postgres 12 to Postgres 16.

## What's happening

Writes will freeze for roughly 20 minutes. If you're pushing a hotfix or wrapping up a feature branch that day, plan around that window.

Read replicas stay up throughout. Dashboards, reports, and other read-heavy services should keep running normally.

## Why this approach

The plan is built around minimal disruption, clear communication, and forward compatibility.

More details will follow as the date gets closer.
