# Alerts pipeline

The market-alert bot runs 3x/day (~07:05, ~15:05, ~20:05 UTC) in a
network-locked environment that can only reach GitHub.

## Data in: `dashboard-cache.json`

`www.macropulse.uk/api/dashboard` is NOT reachable from the bot's environment
(proxy policy 403). Instead, the `dashboard-cache.yml` Action fetches it 20
minutes before each bot run and commits the JSON here as
`alerts/dashboard-cache.json` (with a `cachedAtISO` stamp added).

**Bot: at the start of each run, `git pull` and read
`alerts/dashboard-cache.json` instead of calling the API.** Check
`cachedAtISO` — if it is more than ~2 hours old, the cache workflow likely
failed; fall back to WebSearch for prices and note the staleness in the run
summary.

## Alerts out: `outbox.json`

The bot cannot POST to push services either. It writes the digest to
`alerts/outbox.json` and commits it; the `alert-relay.yml` Action relays any
non-empty message to ntfy (`NTFY_TOPIC` repo secret), which pushes to the
phone. An empty `message` means "no alerts this run" and the relay skips it.

## State: `state.json`

Dedup state — last run time plus every price alert, data release, and news
item already sent, so the bot doesn't repeat itself. Pruned after 7 days.
