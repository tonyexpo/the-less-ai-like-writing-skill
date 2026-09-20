# Postgres 12 → 16 Upgrade: the 14th

On the 14th, we're upgrading from Postgres 12 to Postgres 16.

## What's happening

Writes will freeze for roughly 20 minutes. If you're planning a hotfix or wrapping up a feature branch around that window, build in a few minutes of slack.

Read replicas stay up throughout. Dashboards, reports, and other read-heavy services should keep running normally while writes are paused.

## Why this approach

The goal is a short, contained freeze rather than a longer outage, with enough notice that nobody gets caught mid-deploy.

More details as the date gets closer.
