# MacroPulse Design System

_Started 2026-05-07 07:56 UTC_

---

## User



## Assistant

I'll write up 3-4 alternate design directions as a single research note — written descriptions and ASCII wireframes, as requested. Since this is a writeup rather than a visual mockup, I'll deliver it as a clean editorial HTML document that matches the MacroPulse voice (calm, research-led).

_[tool: update_todos]_

Acknowledging the reminder — I'll create an original design document, not recreate any branded UI. I'm writing fresh directions tuned to MacroPulse's own brand (orange-on-dark, editorial). Now building the document.

_[tool: write_file]_

_[tool: done]_

_[tool: fork_verifier_agent]_

Delivered **Dashboard Directions.html** — four written directions (The Front Page, The Compass, The Briefing Card, The Tape & Margin) with ASCII wireframes, section-by-section change lists, trade-offs, CSS hints, and a recommendation to ship Direction 04 with Direction 01's headline treatment.

## User

I want to extract a coherent design system from my MacroPulse website,
then identify which pages don't yet conform.

Site: https://www.macropulse.uk

The dashboard page (/dashboard/) was recently redesigned in your "Tape &
Margin" / "Front Page" combined direction and I'm happy with how it landed.
Now I want the rest of the site (homepage, methodology, about, newsletter,
contact, faq) to feel like it belongs to the same product without each one
turning into a dashboard clone.

Output I want, as a single document:

1. **Typography scale** — font families (Fraunces / Inter / JetBrains Mono),
   sizes, line heights, and the rule for when each one applies.
2. **Colour tokens** — full palette with semantic names (ink, ink-2, line,
   orange-1, orange-2, orange-3, green, red, etc.) and example usages.
3. **Spacing scale** — the rhythm in pixels/rem.
4. **Component patterns** — eyebrow label, hairline rule, section header,
   card, button, form-panel, CTA strip. For each, give CSS-ready specs.
5. **Page-by-page audit** — visit each page on the live site
   (https://www.macropulse.uk/, /methodology/, /about/, /newsletter/,
   /contact/, /faq/, /legal/) and call out where it diverges from the system
   you just defined. One concrete fix per divergence.
6. **A "do not propagate" list** — which dashboard moves should stay scoped
   to /dashboard/ (the sticky tape, the pulse strip, etc.) so the rest of
   the site doesn't become tool-shaped.

Voice: calm, research-led, editorial. Mobile-first.

## Assistant

_[tool: snip]_

_[tool: web_fetch]_

_[tool: web_fetch]_

_[tool: web_fetch]_

_[tool: web_fetch]_

_[tool: web_fetch]_

_[tool: web_fetch]_

_[tool: web_fetch]_

_[tool: web_fetch]_

_[tool: update_todos]_

_[tool: write_file]_

I got the homepage but the rest of the site is blocking my fetcher. I'll write the design system from the dashboard foundation (which is now the canonical reference), audit the homepage in detail, and for the other pages give a structured checklist framed honestly — patterns to look for, with the conformant version of each. I'll flag the limitation up front so you know what's observed vs. inferred.

_[tool: done]_

_[tool: fork_verifier_agent]_

_[tool: snip]_

Delivered **Design System.html** — single document with the full system (type / colour / spacing / 7 components with paste-ready specs), a per-page audit for all seven pages, and a "do not propagate" list scoping dashboard-only moves.

One honest caveat baked into the doc: my fetcher could only pull the homepage cleanly, so the homepage audit is grounded in the live content while the others are framed as "checks against the system" — likely divergences with concrete fixes, marked **Inferred** in the doc so you know what to verify against the live build.

## User

Verifier agent check completed

## Assistant

_[tool: str_replace_edit]_

_[tool: snip]_

_[tool: done]_

Fixed: scoped the block-code styling to `.comp-spec > code` and added an inline-code style for `.comp-spec p code` so inline mentions stay in flow.

## User

Redesign the MacroPulse homepage at https://www.macropulse.uk/ .

Brief: this is the front door for new visitors. They should understand
within fifteen seconds: (a) what MacroPulse is, (b) what they get if they
subscribe, (c) what the cycle indicator means, (d) why this is different
from generic crypto commentary.

Constraints: stay inside the design system from my previous chat (you wrote
it). Static HTML + vanilla CSS. Fraunces / Inter / JetBrains Mono. Mobile
first. The cycle indicator state ("BTC Accumulation", etc.) should appear
prominently — it's our thesis word.

Give me 3 directions, each with:
- ASCII wireframe of the above-the-fold view
- Section-by-section structure
- Copy suggestions for the headline, sub-deck, and primary CTA
- How the live cycle state pulls in (link to /dashboard/, embed it, or just
  reference it)
- Trade-offs vs current
- Effort: low/medium/high

End with a recommendation. Don't propose a homepage that looks like the
dashboard — they're different jobs.

## Assistant

_[tool: snip]_

_[tool: write_file]_

_[tool: done]_

_[tool: fork_verifier_agent]_

Delivered **Homepage Directions.html** — three directions (Editorial Front Door, Cycle Window, The Letter) with ASCII wireframes, section breakdowns, copy suggestions, cycle-state integration approach, trade-offs, and a recommendation to ship Direction 02 with Direction 03's voice paragraph borrowed in.

## User

Review my MacroPulse site for mobile UX. URL: https://www.macropulse.uk

I want a structured punch-list, not a redesign. For each of these pages:
homepage, /methodology/, /dashboard/, /about/, /newsletter/, /contact/,
/faq/

Open each on a phone-width viewport (375px and 414px) and call out:
- Anything that breaks the layout or causes horizontal scroll
- Tap targets smaller than 44px
- Text too small or too cramped
- Sticky elements that misbehave
- Navigation issues (the hamburger and the nav itself)
- Forms that are awkward on phones (subscribe form, contact form)
- Loading-state UX (the dashboard loads async)

Give me the issues ranked by severity (critical → polish), with one-line
fixes for each. No mockups needed — just the punch list and the fixes.

## Assistant

_[tool: snip]_

_[tool: write_file]_

_[tool: done]_

_[tool: fork_verifier_agent]_

_[tool: update_todos]_

## User

Verifier agent check completed

## Assistant

## Assistant

_[tool: snip]_

Mobile UX Punch-list delivered and verified — ready for the next ask.

## User

Audit my MacroPulse site (https://www.macropulse.uk) for content and
structural gaps.

Current pages: homepage, methodology, dashboard, newsletter, about, faq,
contact, legal.

What's missing that a research newsletter / crypto-macro product at this
stage typically needs? Specifically consider:

- A glossary explaining indicators (M2, PMI, real yields, BTC.D, TOTAL)
- A "previous issues" or sample-issues archive
- Pricing — currently planned at Free / £19/mo Weekly / £79/mo Pro but no
  pricing page exists
- Testimonials or social proof (when relevant later)
- A clearer "How is this different from [Glassnode / Bankless / generic
  crypto Twitter]?" comparison
- A press/media kit
- Any required UK regulatory disclosure for paid investment content
  (this is for a UK Ltd. company; treat as research advisory caveat,
  not legal advice)
- An RSS feed or way to follow without subscribing

For each gap, tell me:
- Whether it's "ship now" / "wait until paid tier launches" / "skip"
- A sketch of what it would contain
- Where it sits in the nav

## Assistant

_[tool: write_file]_

_[tool: done]_

_[tool: fork_verifier_agent]_

_[tool: snip]_

Delivered **Content Gaps.html** — eight gaps with verdicts (5 ship now, 2 wait, 1 skip), each with a what-it-contains sketch and nav placement, plus a consolidated nav map at the end. The UK regulatory section is framed as advisory caveat with one specific thing to flag to your solicitor (the FCA Oct 2023 financial-promotions regime for paid crypto-related content).

## User



## Assistant

_[tool: snip]_

_[tool: write_file]_

_[tool: done]_

_[tool: fork_verifier_agent]_

_[tool: snip]_

Delivered **Homepage v5 Directions.html**.

**Part 1 — three structural directions:**
- **A · The Evidence Margin** — current hero + a second-column EVIDENCE panel with five indicator readings, one inline chart, and a "now in its 7th week" subhead. Two-column on desktop, stacked on mobile. Medium effort, low marketing-risk.
- **B · The Issue, Front Page** — the homepage becomes Tuesday's note: real headline, byline, three to four paragraphs of writing, with the cycle state demoted to a kicker and held in a margin call-out card. Low effort, medium marketing-risk.
- **C · The Ledger** *(the invention)* — the homepage IS a running ledger of every regime call ever made; current call rendered in editorial Fraunces above, 6–8 past calls in mono below with dates and hold-durations. Masthead strip includes "**25 CALLS · 0 REVISIONS**" as the strongest factual claim on the site. Medium effort, low marketing-risk.

Each direction has mobile (390px) + desktop (1180px) ASCII wires, a 7-row change list vs v4, named visual moves, trade-offs, and a risk + effort row.

**Part 2 — five copy sets** plotted across the voice space, all layout-independent:
1. Quietly confident (v4 voice refined)
2. Cycle-first, declarative ("The read is BTC Accumulation.")
3. Honest about uncertainty ("I will be wrong sometimes.")
4. Allocator-direct, operator (brisk, spec-only)
5. Editorial, literary ("The dollar gives a tell, sometimes.")

**Recommendation:** Ship **Direction C + Set 03**. The ledger replaces the "trust me" assertion with a public record, and Set 03's voice ("I will be wrong sometimes — you'll know when, how, against which indicator") names that posture directly. Caveat in the doc: C requires ~18+ past entries to land; if the ledger is too short, ship A first (same architecture, easy migration to C later).

