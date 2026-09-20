# Postgres Upgrade: 12 to 16 on the 14th

On the 14th, we're upgrading from Postgres 12 to Postgres 16.

## What's Happening

**Date: the 14th.**

**Write freeze: about 20 minutes.** Writes will pause during the upgrade. If you're planning a hotfix or wrapping up a feature branch, plan around that window.

**Read replicas: staying up.** Reads keep working while writes are paused, so dashboards, reports, and other read-heavy services should be largely unaffected.

## Why This Approach

The goal is minimal disruption: a short, scoped write freeze instead of a longer outage, with reads unaffected throughout.

## What's Next

More details will follow as the date gets closer. Thanks for planning around the freeze window.
