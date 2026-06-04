# HANDOFF — Newsletter Archive (for the website chat)

Build the **newsletter archive page** at `/newsletter/` (or `/newsletter/archive/`)
on macropulse.uk and have it pick up new issues automatically after each
Monday and Friday newsletter run.

═══════════════════════════════════════════════════════════════════
ARCHITECTURE — single source of truth
═══════════════════════════════════════════════════════════════════

The newsletter agent at `github.com/shaunmcewan-ux/macropulse-newsletter-agent`
(local: `C:\Users\shaun\Documents\GitHub\macropulse-newsletter-agent`)
publishes each issue to **Mailchimp** AND writes two artefacts to the
repo's `archive/` directory:

  archive/
    <YYYY-MM-DD>-monday.html      // the rendered email body
    <YYYY-MM-DD>-friday.html
    index.json                    // manifest of all issues (newest last)

The website is the consumer. It reads `archive/index.json` and renders
the list of issues plus the individual issue pages.

═══════════════════════════════════════════════════════════════════
INGESTION OPTIONS — pick one, document the choice
═══════════════════════════════════════════════════════════════════

▸ Option A — Pull from the agent repo via GitHub Raw

  The website's build/CI step fetches:

    https://raw.githubusercontent.com/shaunmcewan-ux/macropulse-newsletter-agent/main/archive/index.json

  Then for each issue listed, fetches:

    https://raw.githubusercontent.com/shaunmcewan-ux/macropulse-newsletter-agent/main/archive/<html_path>

  Pros: no second deploy step; the agent repo is the source of truth.
  Cons: requires the agent to commit + push after each send (currently
        it does not — see "Agent-side work needed" below).

▸ Option B — Pull from Mailchimp's API

  The website's build/CI step queries the Mailchimp Reports API for
  campaigns sent in the last N days:

    GET https://us1.api.mailchimp.com/3.0/campaigns?status=sent

  For each campaign, fetch the rendered HTML body:

    GET https://us1.api.mailchimp.com/3.0/campaigns/{id}/content

  Pros: zero coordination with the agent — Mailchimp IS the source of truth
        for "sent" status; works for back-catalogue too.
  Cons: requires the website to hold a Mailchimp API key (read-only is fine);
        loses the agent's editorial metadata (headline, dial state, scorecard)
        unless parsed from the HTML.

▸ Option C — Hybrid (recommended)

  - Index/listing: pull `archive/index.json` from the agent repo (cheap,
    has the editorial metadata: dial state, scorecard tally, headline).
  - Issue body: render from the matching HTML in `archive/`, OR redirect
    to the Mailchimp campaign URL `https://mailchi.mp/<campaign_id>` for
    a guaranteed-faithful render with hosted images intact.

═══════════════════════════════════════════════════════════════════
DATA SHAPE — archive/index.json
═══════════════════════════════════════════════════════════════════

```json
{
  "_schema_version": 1,
  "issues": [
    {
      "issue_number": 48,
      "date": "2026-06-03",
      "type": "monday",                       // "monday" | "friday"
      "title": "Week Ahead",                  // "Week Ahead" | "Week in Review"
      "subject": "MacroPulse | Week Ahead | 3 June 2026",
      "headline": "BTC's intraday flush, and the dial that didn't move",
      "dial_state": "BTC Accumulation",
      "dial_weeks_held": 7,
      "scorecard": "3 supportive · 4 neutral · 1 headwind",
      "html_path": "archive/2026-06-03-monday.html",
      "mailchimp_campaign_id": "5ac41c9081",
      "sent_at": "2026-06-04T00:00:00Z",
      "slug": "2026-06-03-week-ahead"
    }
  ]
}
```

`slug` is what the website should use for permalinks, e.g.
`/newsletter/2026-06-03-week-ahead/`.

═══════════════════════════════════════════════════════════════════
ARCHIVE PAGE LAYOUT (suggested)
═══════════════════════════════════════════════════════════════════

`/newsletter/`

  - Header: "Newsletter archive"
  - Stat line: "<N> issues since November 2024"
  - List, newest first, each row:
      - Date · Issue # · Type (Week Ahead / Week in Review)
      - Headline (large, link to issue page)
      - Dial state pill + scorecard tally
      - "Read →" link to `/newsletter/<slug>/`

`/newsletter/<slug>/`

  - Render the saved HTML body inline (it's a complete email, dark theme,
    600 px — wrap it in the site's container or iframe it for isolation)
  - Optional: a "View in Mailchimp" link to `https://mailchi.mp/<campaign_id>`
  - Optional: prev / next issue navigation

═══════════════════════════════════════════════════════════════════
AGENT-SIDE WORK NEEDED (separate task, owned by newsletter agent)
═══════════════════════════════════════════════════════════════════

The agent today writes archive/<file>.html and archive/index.json locally
but does NOT commit and push them. For Option A or Option C to work
end-to-end, the newsletter agent needs one of:

  i.  Auto-commit + push after each successful publish — extend
      `mailer/send_mailchimp.py` to run `git add archive/ && git commit
      && git push` after `send_campaign()` returns 200.

  ii. Manual commit each week — Shaun pushes the archive/ changes after
      reviewing the published email.

  iii. CI step — a GitHub Action triggered by a tag/comment/manual
       dispatch that ingests the latest run and commits.

(i) is cleanest if the host running the scheduled agent has push access
to the repo. (ii) is fine while volume is low.

═══════════════════════════════════════════════════════════════════
ISSUE NUMBERING — keep these aligned
═══════════════════════════════════════════════════════════════════

`archive/index.json` issue numbers must agree with
`https://www.macropulse.uk/data/latest-issue.json`. The current state:

  - `latest-issue.json` says: number 47 (date 2026-05-11)
  - `ledger.json` says: totalIssues 27, since 2024-11-05
  - This handoff seeds the next number as 48 (date 2026-06-03)

These two counters disagreed before; surface the disagreement in the
website's archive footer if it persists. Long-term, both should point
at the same canonical sequence.

═══════════════════════════════════════════════════════════════════
DESIGN — keep it dashboard-consistent
═══════════════════════════════════════════════════════════════════

The archive list uses the same surface as the dashboard:
  - dark bg #0c141b, cards #111a23, borders #1c2935
  - text ink #edf3f7 / secondary #b9c4cc / muted #7c8a95
  - brand orange #ff9d2f for state pills and link hover
  - state pill colours (match the dial handoff):
      Risk Off          #ef5a6b
      BTC Accumulation  #ff9d2f
      Alt Rotation      #4ec38a
      Take Profit       #b794f6

═══════════════════════════════════════════════════════════════════
ASK BACK
═══════════════════════════════════════════════════════════════════

Once you've chosen an option (A / B / C), reply with:
  - Which option you picked and why.
  - Whether the website needs the agent to commit + push the archive/
    directory, or whether you'll pull from Mailchimp's API instead.
  - The chosen URL structure for individual issue pages.
  - Any additional metadata you want surfaced in `index.json` that
    isn't there today (e.g. word count, reading time, tags).

Then I'll wire the agent side to match.
