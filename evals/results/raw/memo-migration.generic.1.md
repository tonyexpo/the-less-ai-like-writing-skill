# Migration Moment: Why the Postgres 12 → 16 Upgrade Matters Now

The database layer isn't just infrastructure—it's the foundation everything else stands on. As our systems scale, staying current with the platforms that power them isn't optional. That's why, on the 14th, we're moving from Postgres 12 to Postgres 16.

## What's Happening

**Upgrade date: the 14th.** Mark it now to avoid friction later.

**Write freeze: roughly 20 minutes.** Short and scoped. If you're pushing a hotfix or wrapping up a feature branch, plan around this window.

**Read replicas: staying up.** While writes pause, reads carry on. Dashboards, reports, and read-heavy services should keep running undisturbed.

## Why This Approach

Three things guide this migration: minimal disruption, clear communication, and forward compatibility.

This isn't just a version bump. The goal is to gain the benefits of Postgres 16 without sacrificing stability along the way.

## Looking Ahead

The 14th is one step in keeping our systems ready for what's next. More details will follow as the date approaches. Thanks for planning around the upgrade.
