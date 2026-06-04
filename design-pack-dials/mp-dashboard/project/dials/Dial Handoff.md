# MacroPulse Dial — Implementation Handoff

> **Status:** Awaiting design pick. This brief assumes **Direction 01 — Phase Arc** (the half-dial speedometer). To switch to D2 / D3 / D4 / D5, replace only the SVG body in §4. The data model, states enum, animation spec, and acceptance criteria are identical for all five.

---

## 1 · What we're building

A single, animated dial component representing the current macro cycle phase. It appears in two surfaces:

| Surface | Path | Variant |
|---|---|---|
| Website dashboard | `app/dashboard/page.tsx` (hero block) | React, interactive, animated transitions |
| Newsletter (HTML email) | `email/{monday,friday}-template.html` (Pulse Strip section) | Static inline SVG, no JS, no animation |

The dial replaces the existing horizontal gradient strip. Same data source, new visual.

---

## 2 · States

Four discrete phases, in cycle order:

```ts
export type CyclePhase = 'risk-off' | 'btc' | 'alt' | 'profit';

export const PHASES = [
  { id: 'risk-off', label: 'Risk Off',         abbr: 'RO',  index: 0 },
  { id: 'btc',      label: 'BTC Accumulation', abbr: 'BTC', index: 1 },
  { id: 'alt',      label: 'ALT Rotation',     abbr: 'ALT', index: 2 },
  { id: 'profit',   label: 'Take Profit',      abbr: 'TP',  index: 3 },
] as const;
```

Mapping logic (your existing scoring → phase) stays in the data layer. The component receives the resolved phase as a prop.

---

## 3 · Tokens

Extend the existing token file (assumed `app/styles/tokens.css` or equivalent). Reuse the three brand colors; **add only `--phase-profit`**.

```css
:root {
  /* existing brand */
  --orange-2:      #ff9d2f;
  --green:         #4ec38a;
  --red:           #ef5a6b;
  --line:          rgba(237,243,247,0.10);
  --line-strong:   rgba(237,243,247,0.16);
  --ink:           #edf3f7;
  --ink-2:         #b9c4cc;
  --ink-3:         #7c8a95;

  /* dial state palette */
  --phase-risk-off: var(--red);
  --phase-btc:      var(--orange-2);
  --phase-alt:      var(--green);
  --phase-profit:   #b794f6;       /* NEW — purple "top of cycle" */

  /* glow / soft fills, used for non-active zones */
  --phase-risk-off-soft: rgba(239, 90, 107, 0.16);
  --phase-btc-soft:      rgba(255, 157, 47, 0.16);
  --phase-alt-soft:      rgba(78, 195, 138, 0.16);
  --phase-profit-soft:   rgba(183, 148, 246, 0.16);
}
```

`#b794f6` is the only new color in the system. It maps to the "Top" zone of the existing email pulse strip, so the brand surfaces line up.

---

## 4 · The component

### File: `app/components/dial/PhaseArc.tsx`

```tsx
import { useId } from 'react';

type Props = {
  /** Resolved cycle phase. */
  phase: 'risk-off' | 'btc' | 'alt' | 'profit';
  /** Optional 0–100 score. When provided, needle interpolates within the phase zone. */
  score?: number;
  /** Outer width in px. Height auto-derives to ~0.72×. Default 320. */
  size?: number;
  /** Disable the entry/transition animation (used in screenshots, RSS embeds, email). */
  static?: boolean;
  /** Extra class on the root <figure>. */
  className?: string;
};

const PHASES = [
  { id: 'risk-off', label: 'Risk Off',         abbr: 'RO',  color: 'var(--phase-risk-off)' },
  { id: 'btc',      label: 'BTC Accumulation', abbr: 'BTC', color: 'var(--phase-btc)'      },
  { id: 'alt',      label: 'ALT Rotation',     abbr: 'ALT', color: 'var(--phase-alt)'      },
  { id: 'profit',   label: 'Take Profit',      abbr: 'TP',  color: 'var(--phase-profit)'   },
] as const;

export function PhaseArc({ phase, score, size = 320, static: isStatic, className }: Props) {
  const i = PHASES.findIndex(p => p.id === phase);
  const w = size;
  const h = size * 0.72;
  const cx = w / 2;
  const cy = h - 28;
  const r = w / 2 - 24;

  // Each zone occupies 45° of the 180° arc. Needle defaults to zone midpoint.
  // When `score` is supplied, map 0–100 → -180°..0° linearly.
  const needleAngle = typeof score === 'number'
    ? -180 + (Math.max(0, Math.min(100, score)) / 100) * 180
    : -180 + i * 45 + 22.5;

  const rad = (deg: number) => (deg * Math.PI) / 180;
  const polar = (radius: number, deg: number) =>
    [cx + radius * Math.cos(rad(deg)), cy + radius * Math.sin(rad(deg))] as const;

  const arcPath = (rOuter: number, rInner: number, a0: number, a1: number) => {
    const [x0o, y0o] = polar(rOuter, a0);
    const [x1o, y1o] = polar(rOuter, a1);
    const [x1i, y1i] = polar(rInner, a1);
    const [x0i, y0i] = polar(rInner, a0);
    return `M ${x0o} ${y0o} A ${rOuter} ${rOuter} 0 0 1 ${x1o} ${y1o} L ${x1i} ${y1i} A ${rInner} ${rInner} 0 0 0 ${x0i} ${y0i} Z`;
  };

  const uid = useId();
  const labelId = `dial-${uid}-label`;
  const activeColor = PHASES[i].color;

  return (
    <figure className={className} style={{ margin: 0 }} aria-labelledby={labelId}>
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} role="img">
        <title id={labelId}>
          MacroPulse dial: {PHASES[i].label}
          {typeof score === 'number' ? ` (score ${score}/100)` : ''}
        </title>

        {/* Four colored zones */}
        {PHASES.map((p, idx) => {
          const active = idx === i;
          const a0 = -180 + idx * 45;
          const a1 = a0 + 45;
          return (
            <path
              key={p.id}
              d={arcPath(r, r - 22, a0 + 1.2, a1 - 1.2)}
              fill={p.color}
              fillOpacity={active ? 0.95 : 0.18}
            />
          );
        })}

        {/* Zone labels */}
        {PHASES.map((p, idx) => {
          const [tx, ty] = polar(r + 14, -180 + idx * 45 + 22.5);
          return (
            <text
              key={p.id}
              x={tx} y={ty + 4}
              textAnchor="middle"
              fontFamily='"JetBrains Mono", ui-monospace, monospace'
              fontSize={Math.max(9, size / 32)}
              letterSpacing="0.18em"
              fill={idx === i ? p.color : 'var(--ink-3)'}
              fontWeight={idx === i ? 600 : 500}
              style={{ textTransform: 'uppercase' }}
            >
              {p.abbr}
            </text>
          );
        })}

        {/* Needle — rotates via transform */}
        <g
          transform={`translate(${cx} ${cy}) rotate(${needleAngle + 90})`}
          style={{
            transition: isStatic ? undefined : 'transform 600ms cubic-bezier(0.32, 0.72, 0.24, 1)',
            transformOrigin: `${cx}px ${cy}px`,
          }}
        >
          <line
            x1="0" y1="0" x2="0" y2={-(r - 12)}
            stroke={activeColor} strokeWidth="2.5" strokeLinecap="round"
          />
          <circle cx="0" cy={-(r - 12)} r="4" fill={activeColor} />
        </g>

        {/* Hub */}
        <circle cx={cx} cy={cy} r="8" fill="#0c141b" stroke="var(--line-strong)" />
        <circle cx={cx} cy={cy} r="3" fill={activeColor} />
      </svg>
    </figure>
  );
}
```

### Companion text block

```tsx
// app/components/dial/DialReadout.tsx
export function DialReadout({ phase, score, summary }: {
  phase: CyclePhase; score?: number; summary?: string;
}) {
  const p = PHASES.find(p => p.id === phase)!;
  return (
    <div className="dial-readout">
      <span className="eyebrow">Current Phase</span>
      <h2 className="phase-name" style={{ color: `var(--phase-${phase})` }}>
        {p.label}
      </h2>
      {typeof score === 'number' && (
        <div className="score">
          <strong>{score > 0 ? '+' : ''}{score}</strong>
          <span className="muted">/100</span>
        </div>
      )}
      {summary && <p className="summary">{summary}</p>}
    </div>
  );
}
```

Use existing Fraunces (h2) / Inter (summary) / JetBrains Mono (eyebrow) font tokens — no new typography.

---

## 5 · Animation & transition

| Property | Value |
|---|---|
| Trigger | `phase` or `score` prop change |
| Element | The `<g>` wrapping the needle |
| Property | `transform: rotate()` |
| Duration | `600ms` |
| Easing | `cubic-bezier(0.32, 0.72, 0.24, 1)` (out-quint feel) |
| Reduced motion | When `prefers-reduced-motion: reduce`, set `transition: none` on the needle group |

The zone fills do **not** animate — they're stable. Only the needle moves.

```tsx
// Inside the component, add:
const prefersReducedMotion =
  typeof window !== 'undefined' &&
  window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;

const transition = (isStatic || prefersReducedMotion)
  ? undefined
  : 'transform 600ms cubic-bezier(0.32, 0.72, 0.24, 1)';
```

---

## 6 · Responsive behavior

| Breakpoint | Size prop | Notes |
|---|---|---|
| ≥ 1024 px (desktop dashboard hero) | `320` | Needle + readout side-by-side |
| 640 – 1023 px (tablet) | `260` | Needle + readout stacked |
| < 640 px (mobile) | `200` | Stacked. Zone labels shrink with `size / 32` |
| Newsletter email | `400` rendered at full width | See §8 |

The component is sized by the `size` prop, not by CSS — pass it explicitly per breakpoint via a container query or media-query CSS variable.

---

## 7 · Hosting page integration

### Dashboard hero (`app/dashboard/page.tsx`)

```tsx
import { PhaseArc } from '@/components/dial/PhaseArc';
import { DialReadout } from '@/components/dial/DialReadout';
import { getCurrentPhase } from '@/lib/data/phase';

export default async function DashboardPage() {
  const { phase, score, summary } = await getCurrentPhase();
  return (
    <section className="dial-hero">
      <PhaseArc phase={phase} score={score} size={320} />
      <DialReadout phase={phase} score={score} summary={summary} />
    </section>
  );
}
```

Replace whatever block currently holds the existing pulse strip. Match the parent card's existing border / radius / padding — no chrome belongs to the dial itself.

### Existing pulse strip

Delete (or feature-flag) the strip in:
- `email/monday-template.html` — Pulse Strip section, lines around the inline gradient `<svg>`
- `email/friday-template.html` — same section
- The dashboard hero

Replace with the dial. The phase labels (Sell / Hold / Buy BTC / Alt Season / Top) collapse to four (Risk Off / BTC / ALT / TP).

---

## 8 · Email variant

The email build must inline a **static** SVG — no React, no transitions, no `useId`. Generate it server-side at send time (or pre-render via a build script) and paste the markup into the templates.

### Build script: `scripts/render-dial-svg.ts`

```ts
import { PHASES } from '../app/components/dial/phases';

export function renderDialSVG({ phase, size = 400 }: { phase: string; size?: number }) {
  // Same geometry as PhaseArc.tsx, but emit a static string.
  // No needle transition. No JS.
  // CSS variables are inlined as literal hex values so email clients render them.
  // Output is plain SVG, no <defs id="...">.
  // ...
}
```

Inline the returned string directly into the template at the Pulse Strip slot.

### Email-safe substitutions

| `app/styles/tokens.css` var | Literal value to inline |
|---|---|
| `var(--phase-risk-off)` | `#ef5a6b` |
| `var(--phase-btc)`      | `#ff9d2f` |
| `var(--phase-alt)`      | `#4ec38a` |
| `var(--phase-profit)`   | `#b794f6` |
| `var(--ink-3)`          | `#7c8a95` |
| `var(--line-strong)`    | `#34404b` (closest Outlook-safe solid) |

### Outlook desktop fallback

Outlook Windows desktop does not render inline SVG. Wrap the SVG in `<!--[if !mso]><!-- -->...<!--<![endif]-->` and emit a hosted PNG fallback for `mso` builds at `https://www.macropulse.uk/assets/email/dial/{{phase}}@2x.png`.

---

## 9 · Accessibility

| Requirement | How |
|---|---|
| Screen reader announces state | `<title>` inside SVG + `aria-labelledby` on `<figure>` |
| Color is not the sole signal | Each phase has a unique abbreviation label drawn on the arc |
| Motion respects user prefs | `prefers-reduced-motion` disables the needle transition |
| Color contrast | Active zone fill `0.95` opacity over `#080e13` exceeds 4.5:1 for all four colors. Inactive zone fill `0.18` is decorative only — never holds text. |

---

## 10 · Acceptance criteria

- [ ] `<PhaseArc phase="btc" />` renders without warnings in dev console
- [ ] `<PhaseArc phase="btc" score={45} />` places the needle inside the BTC zone (not at the zone midpoint)
- [ ] Changing the `phase` prop transitions the needle over 600 ms
- [ ] `prefers-reduced-motion: reduce` removes the transition
- [ ] All four phases render with the colors in §3 and no others
- [ ] Component renders correctly at `size={200}`, `300`, `400`
- [ ] Email build emits a single inline `<svg>` with no `var()` references
- [ ] Screen-reader output reads e.g. "MacroPulse dial: BTC Accumulation, score 45 of 100"
- [ ] Lighthouse a11y score on `/dashboard` does not regress
- [ ] Existing pulse-strip element is removed from `monday-template.html`, `friday-template.html`, and the dashboard

---

## 11 · Stretch goals (post-launch)

1. **Confidence indicator** — small dotted halo around the hub whose density reflects `confidence` (0–100). Optional prop, off by default.
2. **History trail** — ghosted needles at -1w / -1m positions to show drift. Toggle in dashboard only.
3. **Interactive scrub** — on the dashboard, dragging the needle scrubs through historical phases. Read-only outside dashboard.
4. **OG image** — generate a 1200×630 PNG of the dial per phase for social sharing of newsletter issues.

---

## 12 · Switching to a different direction

The contract `(phase, score?, size?, static?)` is identical across **D1 – D5**. To swap:

| Direction | Replace §4 SVG body with | Notes |
|---|---|---|
| D2 — Concentric Rings | `<circle>` stack from `dials/dials.jsx → DialConcentricRings` | Drop the needle transition; transition `r` and `opacity` of the active ring instead. |
| D3 — Cycle Wheel | Quadrant arcs from `DialCycleWheel` | Transition the perimeter marker position. |
| D4 — Stepped Ladder | Bar stack from `DialSteppedLadder` | Transition the active-bar fill via `fill-opacity`. At small sizes show `abbr`, full label only ≥ 260 px. |
| D5 — Tape Reader | Pill segments from `DialTapeReader` | This is the closest evolution of the current strip — minimal churn for users. |

All other sections (tokens, animation, email build, a11y, AC) remain unchanged.

---

## 13 · Reference

- Live design exploration: `dials/Dial Directions.html`
- Source for all 5 dial implementations: `dials/dials.jsx`
- Current pulse strip (for diff): `email/monday-template.html` § *Pulse Strip*
- Site palette: `Design System.html`
