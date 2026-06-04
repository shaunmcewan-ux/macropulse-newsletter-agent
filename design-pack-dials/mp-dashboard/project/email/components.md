# MacroPulse Email — Components Reference

Email-client safe component library for the MacroPulse newsletter. Every component is **table-based**, **inline-styled**, **no JS**, and uses the **Arial / Helvetica system stack**. The colour and type tokens come from [`tokens.json`](./tokens.json).

| | Constraints |
|---|---|
| Container | `width="600"` with `max-width:600px` — never wider |
| Backgrounds | `bgcolor` attr + inline `background:` for Outlook fallback |
| Fonts | `Arial, Helvetica, 'Helvetica Neue', sans-serif` everywhere |
| Layout | `<table role="presentation">`, `cellpadding`/`cellspacing="0"`, `border="0"` |
| Images | Inline `<svg>` (Apple Mail / Gmail / iOS); for Outlook desktop swap to a hosted PNG at `https://www.macropulse.uk/assets/...` |
| Entities | `&mdash; &ndash; &middot; &copy; &rsquo; &ldquo; &minus; &percnt; &pound; &amp;` — never raw non-ASCII |

Replace the **`{{variable}}`** placeholders below at send-time with your data layer (Mailchimp merge tags, Customer.io Liquid, etc.).

---

## 1 · Header

Logo lockup left, issue meta right, separated by a thin gradient rule.

**Variables**

| Name | Example | Notes |
|---|---|---|
| `issue.kind`   | `"Week Ahead"` or `"Week in Review"` | uppercase tracked eyebrow |
| `issue.date`   | `"Mon 18 May 2026"` | format day · DD MMM YYYY |
| `issue.number` | `79` | rendered as `Issue 79` |

**Block**

```html
<tr><td style="padding:24px 32px 20px;">
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
    <tr>
      <td valign="middle" align="left">
        <!-- glyph + word-mark lockup -->
        <table role="presentation" cellpadding="0" cellspacing="0" border="0">
          <tr>
            <td valign="middle" style="padding-right:12px;line-height:0;">
              <svg width="32" height="32" viewBox="0 0 32 32" xmlns="http://www.w3.org/2000/svg">
                <defs>
                  <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%"   stop-color="#dc2626"/>
                    <stop offset="35%"  stop-color="#f97316"/>
                    <stop offset="65%"  stop-color="#eab308"/>
                    <stop offset="100%" stop-color="#22c55e"/>
                  </linearGradient>
                </defs>
                <circle cx="16" cy="16" r="13" fill="none" stroke="url(#ring)" stroke-width="2.5"/>
                <polyline points="7,20 12,15 16,18 20,11 25,13"
                          fill="none" stroke="#ffffff" stroke-width="1.8"
                          stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
            </td>
            <td valign="middle"
                style="font-family:Arial,Helvetica,sans-serif;font-size:22px;font-weight:700;
                       letter-spacing:-0.01em;line-height:1;color:#ffffff;">
              Macro<span style="color:#f97316;">Pulse</span>
            </td>
          </tr>
        </table>
      </td>
      <td valign="middle" align="right" style="font-family:Arial,Helvetica,sans-serif;">
        <div style="font-size:11px;font-weight:600;letter-spacing:0.28em;text-transform:uppercase;
                    color:rgba(255,255,255,0.45);">{{issue.kind}}</div>
        <div style="font-size:13px;color:rgba(255,255,255,0.68);margin-top:6px;letter-spacing:0.02em;">
          {{issue.date}} &middot; Issue {{issue.number}}
        </div>
      </td>
    </tr>
  </table>
  <!-- gradient rule -->
  <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top:22px;">
    <tr><td height="1" bgcolor="#f97316"
            style="height:1px;line-height:1px;font-size:0;background:#f97316;
                   background-image:linear-gradient(90deg,#dc2626 0%,#f97316 24%,#eab308 48%,#22c55e 76%,#a855f7 100%);">&nbsp;</td></tr>
  </table>
</td></tr>
```

**Outlook fallback:** the gradient rule collapses to a 1 px solid `#f97316` line. This is intentional.

---

## 2 · Pulse Strip *(required on every issue)*

The visual signature. Sits directly under the header. Mirrors the MacroPulse Dial section on the website.

**Variables**

| Name | Example | Notes |
|---|---|---|
| `pulse.phase`         | `"Early Expansion"` | display heading |
| `pulse.summary`       | `"Risk on. Liquidity opening..."` | one-line caption |
| `pulse.score`         | `+3.0` | tinted green when positive, red when negative |
| `pulse.confidence`    | `68` | rendered `Conf 68/100` |
| `pulse.dialPosition`  | `55` | 0–100 — drives pointer X position |

**Pointer position math:** `x = round((dialPosition / 100) * 560) - 4` for the outer halo rect, `+2` more for the inner white rect.

**Block** *(svg + caption row only — wrap in the same card chrome as the others)*

```html
<!-- score + phase row -->
<table role="presentation" width="100%">
  <tr>
    <td valign="top" align="left" style="font-family:Arial,Helvetica,sans-serif;">
      <div style="font-size:26px;font-weight:600;letter-spacing:-0.015em;color:#ffffff;line-height:1.15;">
        {{pulse.phase}}
      </div>
      <div style="font-size:14px;color:rgba(255,255,255,0.68);margin-top:6px;line-height:1.4;">
        {{pulse.summary}}
      </div>
    </td>
    <td valign="top" align="right" style="font-family:Arial,Helvetica,sans-serif;white-space:nowrap;padding-left:16px;">
      <div style="font-size:28px;font-weight:700;letter-spacing:-0.02em;color:#22c55e;line-height:1;">
        {{pulse.score}}
      </div>
      <div style="font-size:11px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:rgba(255,255,255,0.45);margin-top:8px;">
        Conf {{pulse.confidence}}/100
      </div>
    </td>
  </tr>
</table>

<!-- gradient pill with pointer -->
<div style="margin-top:24px;line-height:0;text-align:center;">
  <svg width="100%" height="56" viewBox="0 0 560 56" preserveAspectRatio="none"
       xmlns="http://www.w3.org/2000/svg" role="img"
       aria-label="Pulse position {{pulse.dialPosition}} of 100">
    <defs>
      <linearGradient id="pulse" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0%"   stop-color="#dc2626"/>
        <stop offset="24%"  stop-color="#f97316"/>
        <stop offset="48%"  stop-color="#eab308"/>
        <stop offset="76%"  stop-color="#22c55e"/>
        <stop offset="100%" stop-color="#a855f7"/>
      </linearGradient>
    </defs>
    <rect x="0" y="0" width="560" height="56" rx="28" ry="28" fill="url(#pulse)"/>
    <!-- pointer at x = round(dialPosition/100 * 560) - 4 -->
    <rect x="{{pointer.x - 4}}" y="4" width="8"  height="48" rx="4" fill="#0a0a0a"/>
    <rect x="{{pointer.x - 2}}" y="6" width="4"  height="44" rx="2" fill="#ffffff"/>
  </svg>
</div>

<!-- caption row: highlight the active zone -->
<table role="presentation" width="100%" style="margin-top:12px;">
  <tr>
    <td align="left"   width="20%" style="font-size:10px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:rgba(255,255,255,0.45);">Sell</td>
    <td align="center" width="20%" style="font-size:10px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:rgba(255,255,255,0.45);">Hold</td>
    <td align="center" width="20%" style="font-size:10px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:#ffffff;">Buy BTC</td>
    <td align="center" width="20%" style="font-size:10px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:rgba(255,255,255,0.45);">Alt Season</td>
    <td align="right"  width="20%" style="font-size:10px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;color:rgba(255,255,255,0.45);">Top</td>
  </tr>
</table>
```

**Active-zone rule:** brighten the caption (`color:#ffffff`) for whichever zone the pointer sits in. Zones are `0–20 Sell`, `20–40 Hold`, `40–60 Buy BTC`, `60–80 Alt Season`, `80–100 Top`.

---

## 3 · Market Snapshot

7-row table: BTC, ETH, SUI, DOGE, S&P 500, Gold, Oil. Columns: asset, price, 24 h pill, 7 d pill.

**Variables**

```ts
type Row = {
  asset:  string;   // "BTC"
  price:  string;   // "$73,420" (pre-formatted, currency-aware)
  d1:     number;   // +2.1
  d7:     number;   // +8.4
};
type Snapshot = { rows: Row[]; asOf: string }
```

**Pill rule:** positive = green tint (`bg:#0f2a1a`, `text:#4ade80`), negative = red tint (`bg:#2a1010`, `text:#f87171`). Always render `+` for positive, `&minus;` for negative.

**Row block**

```html
<tr>
  <td align="left"  style="padding:14px 0;font-size:15px;font-weight:600;color:#ffffff;
                            border-bottom:1px solid rgba(255,255,255,0.06);">{{row.asset}}</td>
  <td align="right" style="padding:14px 0;font-size:15px;font-weight:500;color:#ffffff;
                            border-bottom:1px solid rgba(255,255,255,0.06);">{{row.price}}</td>
  <td align="right" style="padding:14px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
    <span style="display:inline-block;padding:5px 10px;
                 background:{{ row.d1 > 0 ? '#0f2a1a' : '#2a1010' }};
                 color:{{ row.d1 > 0 ? '#4ade80' : '#f87171' }};
                 font-size:12px;font-weight:600;border-radius:999px;line-height:1;">
      {{row.d1.formatted}}%
    </span>
  </td>
  <td align="right" style="padding:14px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
    <span style="display:inline-block;padding:5px 10px;
                 background:{{ row.d7 > 0 ? '#0f2a1a' : '#2a1010' }};
                 color:{{ row.d7 > 0 ? '#4ade80' : '#f87171' }};
                 font-size:12px;font-weight:600;border-radius:999px;line-height:1;">
      {{row.d7.formatted}}%
    </span>
  </td>
</tr>
```

**Last-row tweak:** drop the bottom border by changing `padding:14px 0` to `padding:14px 0 0` and removing the `border-bottom`.

---

## 4 · Indicator Pulse *(Friday only)*

2×2 grid: BTC.D, ETH/BTC, TOTAL2, TOTAL3.

**Variables**

```ts
type Tile = {
  label:   "BTC.D" | "ETH/BTC" | "TOTAL2" | "TOTAL3";
  value:   string;  // "51.8%" / "0.0538" / "$1.42T" / "$720B"
  delta:   string;  // "+1.4%" / "-0.6pp"
  positive: boolean;
};
```

**Tile block** *(repeat 4×, two per row, stack on mobile via the `.stack` class on the outer wrappers)*

```html
<td class="stack" valign="top" width="50%" style="padding:0 6px 12px 0;">
  <table role="presentation" width="100%" bgcolor="#1a1a1a"
         style="background:#1a1a1a;border:1px solid rgba(255,255,255,0.1);border-radius:20px;">
    <tr><td style="padding:20px;">
      <div style="font-size:10px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;
                  color:rgba(255,255,255,0.45);">{{tile.label}}</div>
      <div style="font-size:28px;font-weight:600;color:#ffffff;line-height:1;margin-top:10px;
                  letter-spacing:-0.015em;">{{tile.value}}</div>
      <div style="margin-top:14px;">
        <span style="display:inline-block;padding:4px 9px;
                     background:{{ tile.positive ? '#0f2a1a' : '#2a1010' }};
                     color:{{ tile.positive ? '#4ade80' : '#f87171' }};
                     font-size:11px;font-weight:600;border-radius:999px;line-height:1;">
          {{tile.delta}} w/w
        </span>
      </div>
    </td></tr>
  </table>
</td>
```

The outer wrapper alternates `padding:0 6px 12px 0` (left tile) and `padding:0 0 12px 6px` (right tile) to maintain a 12 px gutter. Bottom row uses `padding:0 6px 0 0` and `padding:0 0 0 6px`.

---

## 5 · Week Ahead Calendar *(Monday only)*

5-row table for Mon–Fri.

**Variables**

```ts
type DayRow = {
  short:  "Mon" | "Tue" | "Wed" | "Thu" | "Fri";
  num:    number;          // 18
  events: { label: string; type: ChipType }[];
};
type ChipType = "cpi" | "fomc" | "nfp" | "earnings" | "geopolitics";
```

**Chip palette**

| `type`        | `background` | `color` |
|---|---|---|
| `cpi`         | `#1d2a4d` | `#93b8f7` |
| `fomc`        | `#3a2748` | `#c4a8f5` |
| `nfp`         | `#2a2218` | `#f9b27a` |
| `earnings`    | `#1c3326` | `#7bd4a0` |
| `geopolitics` | `#3a1a1a` | `#f08c8c` |

**Row block**

```html
<tr>
  <td valign="top" width="72" style="padding:14px 0;border-top:1px solid rgba(255,255,255,0.06);">
    <div style="font-size:10px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;
                color:rgba(255,255,255,0.45);">{{day.short}}</div>
    <div style="font-size:18px;font-weight:600;color:#ffffff;line-height:1;margin-top:6px;">
      {{day.num}}
    </div>
  </td>
  <td valign="middle" style="padding:14px 0;border-top:1px solid rgba(255,255,255,0.06);">
    {{#each day.events}}
    <span style="display:inline-block;padding:6px 12px;background:{{chip.bg}};color:{{chip.text}};
                 font-size:11px;font-weight:600;border-radius:999px;line-height:1;
                 margin:0 4px 4px 0;">{{event.label}}</span>
    {{/each}}
  </td>
</tr>
```

Bump the first row's top border to `rgba(255,255,255,0.1)` and add a matching bottom border on the last row.

---

## 6 · Chart Spotlight

Full-width card containing one SVG chart (560 × 210), title above, 2–3 line analysis below. **Two stacked per issue.**

**Variables**

```ts
type Spotlight = {
  number:   1 | 2;
  title:    string;       // "BTC reclaims the 200-day..."
  series:   { x: number; y: number }[]; // 0..560 / 0..210
  refLine?: { y: number; label: string }; // dashed reference (200d MA, range cap, etc.)
  accent:   "#f97316" | "#3b82f6" | "#22c55e" | "#a855f7";  // line + endpoint
  legend:   { left: string; mid?: string; right: string };  // "BTC/USD" "200d MA" "$73,420"
  analysis: string;       // 2–3 line markdown
};
```

**SVG path generation**

Given the series, produce two paths:

```js
const stroke = `M${pts.map(p => `${p.x},${p.y}`).join(' L')}`;
const fill   = `${stroke} L${last.x},210 L0,210 Z`;
```

**Block**

```html
<div style="margin-top:18px;line-height:0;">
  <svg width="100%" height="210" viewBox="0 0 560 210" preserveAspectRatio="none"
       xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{{spotlight.title}}">
    <defs>
      <linearGradient id="s{{n}}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%"   stop-color="{{accent}}" stop-opacity="0.32"/>
        <stop offset="100%" stop-color="{{accent}}" stop-opacity="0"/>
      </linearGradient>
    </defs>
    <!-- 3 grid lines -->
    <line x1="0" y1="50"  x2="560" y2="50"  stroke="#ffffff" stroke-opacity="0.06"/>
    <line x1="0" y1="105" x2="560" y2="105" stroke="#ffffff" stroke-opacity="0.06"/>
    <line x1="0" y1="160" x2="560" y2="160" stroke="#ffffff" stroke-opacity="0.06"/>
    <!-- optional dashed reference -->
    <line x1="0" y1="{{refLine.y}}" x2="560" y2="{{refLine.y}}"
          stroke="#ffffff" stroke-opacity="0.35" stroke-width="1.2" stroke-dasharray="4 4"/>
    <!-- area + line -->
    <path d="{{fillPath}}" fill="url(#s{{n}})"/>
    <path d="{{strokePath}}" stroke="{{accent}}" stroke-width="2" fill="none"
          stroke-linejoin="round" stroke-linecap="round"/>
    <!-- endpoint dot + halo -->
    <circle cx="{{last.x}}" cy="{{last.y}}" r="4" fill="{{accent}}"/>
    <circle cx="{{last.x}}" cy="{{last.y}}" r="8" fill="{{accent}}" fill-opacity="0.25"/>
    <!-- legend texts -->
    <text x="12"  y="20" font-family="Arial,Helvetica,sans-serif" font-size="11" font-weight="600" fill="#ffffff" fill-opacity="0.85">{{legend.left}}</text>
    <text x="540" y="20" font-family="Arial,Helvetica,sans-serif" font-size="11" font-weight="600" fill="#ffffff" text-anchor="end">{{legend.right}}</text>
  </svg>
</div>
```

**Outlook desktop:** chart renders blank. Provide a hosted PNG fallback as a sibling `<img>` inside an `<!--[if mso]>` block if pixel-perfect parity matters more than file size.

---

## 7 · Portfolio Performance *(Friday only)*

3-row table for the held book + an inverted "Allocation guidance" total card.

**Variables**

```ts
type Holding = {
  asset:       string;   // "BTC"
  entry:       string;   // "£52,800"
  current:     string;   // "£58,940"
  d7:          number;   // +2.0
  sinceIncept: number;   // +11.6
};
type Portfolio = {
  rows:       Holding[];
  totalPct:   number;     // +8.4 — book PnL since inception
  guidance:   { heading: string; copy: string };  // shown on inverted card
};
```

**Inverted total card** *(white background, slate text — matches the website's "Allocation guidance" block)*

```html
<table role="presentation" width="100%" bgcolor="#ffffff"
       style="background:#ffffff;border-radius:24px;margin-top:24px;">
  <tr><td style="padding:24px 24px 22px;">
    <table role="presentation" width="100%">
      <tr>
        <td valign="top" align="left" style="font-family:Arial,Helvetica,sans-serif;">
          <div style="font-size:10px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;
                      color:rgba(10,10,10,0.55);">Allocation Guidance</div>
          <div style="font-size:22px;font-weight:700;color:#0a0a0a;line-height:1.2;
                      letter-spacing:-0.015em;margin-top:8px;">{{guidance.heading}}</div>
          <div style="font-size:13px;color:rgba(10,10,10,0.65);margin-top:6px;line-height:1.5;max-width:320px;">
            {{guidance.copy}}
          </div>
        </td>
        <td valign="top" align="right" style="font-family:Arial,Helvetica,sans-serif;
                                              white-space:nowrap;padding-left:16px;">
          <div style="font-size:10px;font-weight:600;letter-spacing:0.2em;text-transform:uppercase;
                      color:rgba(10,10,10,0.55);">Book PnL</div>
          <div style="font-size:28px;font-weight:700;color:#0a0a0a;line-height:1;
                      margin-top:8px;letter-spacing:-0.02em;">{{totalPct.formatted}}</div>
          <div style="font-size:11px;font-weight:600;color:#0a0a0a;margin-top:6px;">since inception</div>
        </td>
      </tr>
    </table>
  </td></tr>
</table>
```

---

## 8 · Feature Article

Eyebrow ("This Week" / "Last Week"), 3xl headline, 3–4 paragraphs, optional pull-quote with left-border accent, CTA button at the bottom.

**Variables**

```ts
type Feature = {
  eyebrow:   "This Week" | "Last Week";
  headline:  string;
  body:      string[];        // 3–4 paragraphs
  pullQuote?: string;         // optional — inserted between paragraphs 1 and 2
  cta:       { label: string; href: string };
};
```

**Pull quote block**

```html
<table role="presentation" width="100%" style="margin:24px 0;">
  <tr>
    <td style="border-left:3px solid #f97316;padding:4px 0 4px 18px;">
      <div style="font-family:Arial,Helvetica,sans-serif;font-style:italic;font-size:19px;
                  line-height:1.45;color:#ffffff;font-weight:400;">
        &ldquo;{{pullQuote}}&rdquo;
      </div>
    </td>
  </tr>
</table>
```

**CTA button**

```html
<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin-top:28px;">
  <tr>
    <td bgcolor="#f97316" style="border-radius:999px;">
      <a href="{{cta.href}}"
         style="display:inline-block;padding:13px 24px;font-family:Arial,Helvetica,sans-serif;
                font-size:14px;font-weight:600;color:#0a0a0a;text-decoration:none;letter-spacing:0.02em;">
        {{cta.label}} &rarr;
      </a>
    </td>
  </tr>
</table>
```

---

## 9 · Footer

Logo, tagline, link row, unsubscribe / view-in-browser / preferences, copyright.

**Variables**

| Name | Example |
|---|---|
| `tagline` | `"Reading the macro tape so you don't have to."` |
| `urls.framework / .dial / .newsletter / .glossary` | absolute URLs |
| `urls.unsub / .viewInBrowser / .prefs` | ESP merge tags (`*\|UNSUB\|*` etc.) |
| `year` | `2026` |

Keep the structure as-is from the templates — three stacked rows with `align="center"`, separated by mid-dots. The bottom row sits behind a 1 px top border for visual closure.

---

## Composition order

### Monday — Week Ahead

1. Header
2. **Pulse Strip**
3. Market Snapshot
4. **Week Ahead Calendar**
5. Chart Spotlight #1 (BTC)
6. Chart Spotlight #2 (S&P 500)
7. Feature Article (eyebrow: *This Week*)
8. Footer

### Friday — Week in Review

1. Header
2. **Pulse Strip**
3. Market Snapshot
4. **Indicator Pulse**
5. Chart Spotlight #1 (BTC.D)
6. Chart Spotlight #2 (TOTAL3)
7. **Portfolio Performance**
8. Feature Article (eyebrow: *Last Week*)
9. Footer

---

## Client behaviour

| Client | Cards | Rounded corners | SVG | Pills (rgba) | Verdict |
|---|---|---|---|---|---|
| Apple Mail (macOS, iOS) | ✓ | ✓ | ✓ | ✓ | Pixel-perfect |
| Gmail (web, light) | ✓ | ✓ | ✓ | ✓ | Pixel-perfect |
| Gmail (web, dark)  | ✓ | ✓ | ✓ | ✓ | Pixel-perfect — `meta[color-scheme]` keeps the dark canvas |
| Gmail iOS / Android | ✓ | ✓ | ✓ | ✓ | Pixel-perfect |
| Outlook 365 web    | ✓ | ✓ | ✓ | ✓ | Pixel-perfect |
| Outlook 365 macOS  | ✓ | ✓ | ✓ | partial | Cards render; pills lose tint, fall back to solid hex equivalent |
| Outlook Windows desktop | ✓ | partial | ✗ | partial | Use hosted PNG fallback for charts + Pulse Strip; cards render with 90° corners |
| Yahoo / AOL        | ✓ | ✓ | ✓ | ✓ | Pixel-perfect |

**Hosted-image fallback path:** when Outlook Windows is in scope, export each SVG at 2× and host at `https://www.macropulse.uk/assets/email/{{issue.id}}/{{component}}@2x.png`, wrap in `<!--[if mso]><img src="..." width="560" alt=""/><![endif]-->` immediately after the inline SVG, and wrap the SVG itself in `<!--[if !mso]><!-- ... -->...<!--<![endif]-->`.

---

## Screenshots

Open [`index.html`](./index.html) in the preview pane to see both templates rendered live at desktop (640 px) and mobile (390 px) widths. Sample data is hard-coded; swap with your ESP merge tags before send.
