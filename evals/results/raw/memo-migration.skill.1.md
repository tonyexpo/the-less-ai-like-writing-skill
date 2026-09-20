# Postgres 12 → 16 Upgrade: the 14th

On the 14th, we're moving from Postgres 12 to Postgres 16.

## What's happening

**Write freeze: about 20 minutes.** Writes pause; reads keep working. Dashboards, reports, and other read-heavy services should be largely unaffected.

If you're planning a hotfix or wrapping up a feature branch, plan around this window.

## Why this approach

The priorities here are minimal disruption and clear communication. We'd rather upgrade in a way people can plan around than rush it.

More details will follow as the date gets closer.
