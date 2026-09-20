# Postgres 12 → 16 Upgrade: The 14th

On the 14th, we're moving from Postgres 12 to Postgres 16.

## What's Happening

**Date: the 14th.**

**Write freeze: roughly 20 minutes.** If you're planning a hotfix or wrapping up a feature branch, plan around this window.

**Read replicas: staying up.** Writes pause, but reads continue. Dashboards, reports, and read-heavy services should keep running normally.

## Why This Approach

The priorities here are minimal disruption and clear communication: freeze writes only as long as needed, and keep reads unaffected.

More details will follow as the date approaches. Thanks for planning around this.
