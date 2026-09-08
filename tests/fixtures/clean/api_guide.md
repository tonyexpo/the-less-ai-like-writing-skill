# Rate limits

Every token gets 600 requests per minute. The counter resets on a sliding
window, not on the minute boundary, so bursting 600 requests at 10:00:59 does
not buy you another 600 at 10:01:00.

When you go over, the API returns 429 with a `Retry-After` header in seconds.
Respect it. Clients that retry immediately get their token throttled harder for
the next five minutes.

## What counts as a request

- Any call to `/v1/messages`, including ones that fail validation.
- Streaming calls count once, at connection time.
- `/v1/models` and other metadata endpoints are free.

Batch jobs are metered separately and do not draw down your per-minute budget.

## Raising the limit

Write to support with your token prefix and the peak rate you need. We have
approved 5,000/min for a few customers, but not without a look at the traffic
shape first. Sustained load is easier to approve than spikes.
