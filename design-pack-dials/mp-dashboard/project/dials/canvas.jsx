/* global React, ReactDOM, DesignCanvas, DCSection, DCArtboard,
   PHASES, INK, INK_2, INK_3, INK_4, LINE, LINE_STRONG,
   DialPhaseArc, DialConcentricRings, DialCycleWheel, DialSteppedLadder, DialTapeReader */

const DESIGNS = [
  {
    id: 'd1-phase-arc',
    name: 'Phase Arc',
    tag: 'Half-dial speedometer',
    blurb: '180° gauge with four colored zones and an animated needle. Literally a "dial". Universally readable.',
    component: DialPhaseArc,
    width: 660, height: 760,
    note: 'Best for: editorial homepage + dashboard hero. Scales to 480px tall.',
  },
  {
    id: 'd2-concentric',
    name: 'Concentric Rings',
    tag: 'Ring stack, outside→in',
    blurb: 'Four nested rings, one per phase. Active ring glows; cardinal markers dot the perimeter. Most distinctive.',
    component: DialConcentricRings,
    width: 660, height: 760,
    note: 'Best for: brand mark / favicon-able. Reads at 64px.',
  },
  {
    id: 'd3-cycle-wheel',
    name: 'Cycle Wheel',
    tag: 'Full circle, four quadrants',
    blurb: 'Clockwise quadrants. Marker travels the perimeter. Conveys "we are here in the cycle" better than any other.',
    component: DialCycleWheel,
    width: 660, height: 760,
    note: 'Best for: explaining the cyclical thesis. Pairs with a "what comes next" callout.',
  },
  {
    id: 'd4-stepped',
    name: 'Stepped Ladder',
    tag: 'Vertical thermometer',
    blurb: 'Four bars stacked bottom-up. Fills progressively. Editorial / Swiss / data-dashboard feel — quiet and confident.',
    component: DialSteppedLadder,
    width: 660, height: 760,
    note: 'Best for: sidebars, dashboards, mobile portrait. Stacks naturally.',
  },
  {
    id: 'd5-tape',
    name: 'Tape Reader',
    tag: 'Segmented bar with pointer',
    blurb: 'Four pill segments, one glowing, pointer above. Email-perfect — works as a single inline SVG at 560×80.',
    component: DialTapeReader,
    width: 660, height: 760,
    note: 'Best for: the newsletter strip + compact dashboard chips.',
  },
];

function ArtboardHeader({ name, tag, blurb, n }) {
  return (
    <div style={{ padding: '24px 28px 0' }}>
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', gap: 12 }}>
        <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', color: '#ff9d2f' }}>
          Direction 0{n}
        </div>
        <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', color: INK_3 }}>
          {tag}
        </div>
      </div>
      <div style={{ fontFamily: 'Fraunces, serif', fontSize: 28, fontWeight: 500, letterSpacing: '-0.02em', color: INK, marginTop: 10, lineHeight: 1.1 }}>
        {name}
      </div>
      <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 14, lineHeight: 1.55, color: INK_2, marginTop: 8, maxWidth: 540, textWrap: 'pretty' }}>
        {blurb}
      </div>
    </div>
  );
}

function StateCell({ phase, children }) {
  return (
    <div style={{
      background: 'rgba(255,255,255,0.025)',
      border: `1px solid ${LINE}`,
      borderRadius: 14,
      padding: '22px 16px 18px',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'flex-start',
      minHeight: 280,
      position: 'relative',
    }}>
      <div style={{
        position: 'absolute', top: 10, left: 14,
        display: 'flex', alignItems: 'center', gap: 6,
        fontFamily: '"JetBrains Mono", monospace', fontSize: 9,
        letterSpacing: '0.2em', textTransform: 'uppercase', color: INK_3,
      }}>
        <span style={{ width: 6, height: 6, borderRadius: 999, background: phase.color, boxShadow: `0 0 8px ${phase.color}` }}/>
        State {phase.abbr}
      </div>
      {children}
    </div>
  );
}

function DesignArtboard({ design, n }) {
  const D = design.component;
  return (
    <div style={{
      background: 'linear-gradient(180deg,#0c141b 0%, #080e13 100%)',
      width: '100%', height: '100%',
      display: 'flex', flexDirection: 'column',
    }}>
      <ArtboardHeader name={design.name} tag={design.tag} blurb={design.blurb} n={n}/>
      <div style={{
        padding: '20px 28px 0',
        flex: 1,
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: 12,
      }}>
        {PHASES.map(p => (
          <StateCell key={p.id} phase={p}>
            <D state={p.id} size={240}/>
          </StateCell>
        ))}
      </div>
      <div style={{
        padding: '14px 28px 22px',
        fontFamily: '"JetBrains Mono", monospace', fontSize: 10,
        letterSpacing: '0.14em', textTransform: 'uppercase', color: INK_4,
        display: 'flex', justifyContent: 'space-between',
      }}>
        <span>{design.note}</span>
        <span>SVG &middot; works in email &amp; web</span>
      </div>
    </div>
  );
}

/* Section 2 — head-to-head comparison at a single state */
function ComparisonArtboard({ state }) {
  return (
    <div style={{
      background: 'linear-gradient(180deg,#0c141b 0%, #080e13 100%)',
      width: '100%', height: '100%',
      padding: '24px 28px',
      display: 'flex', flexDirection: 'column',
    }}>
      <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between' }}>
        <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', color: '#ff9d2f' }}>
          Side-by-side
        </div>
        <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', color: INK_3 }}>
          State: {state.toUpperCase()}
        </div>
      </div>
      <div style={{ fontFamily: 'Fraunces, serif', fontSize: 24, fontWeight: 500, color: INK, marginTop: 8, letterSpacing: '-0.015em' }}>
        All five directions at the same state
      </div>
      <div style={{
        marginTop: 24,
        flex: 1,
        display: 'grid',
        gridTemplateColumns: 'repeat(5, 1fr)',
        gap: 12,
        alignItems: 'start',
      }}>
        {DESIGNS.map((d, idx) => {
          const D = d.component;
          return (
            <div key={d.id} style={{
              background: 'rgba(255,255,255,0.025)',
              border: `1px solid ${LINE}`,
              borderRadius: 12,
              padding: '18px 12px 14px',
              display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8,
              minHeight: 320,
            }}>
              <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 9, letterSpacing: '0.18em', textTransform: 'uppercase', color: INK_3 }}>
                D{idx + 1} &middot; {d.name}
              </div>
              <D state={state} size={170}/>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/* Recommendation artboard */
function RecommendationArtboard() {
  return (
    <div style={{
      background: 'linear-gradient(180deg,#16212c 0%, #0c141b 100%)',
      width: '100%', height: '100%',
      padding: '32px 36px',
      display: 'flex', flexDirection: 'column',
      gap: 18,
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <span style={{ width: 8, height: 8, borderRadius: 999, background: '#ff9d2f', boxShadow: '0 0 12px #ff9d2f' }}/>
        <span style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', color: '#ff9d2f' }}>
          Recommendation
        </span>
      </div>
      <div style={{ fontFamily: 'Fraunces, serif', fontSize: 38, fontWeight: 500, letterSpacing: '-0.02em', color: INK, lineHeight: 1.08 }}>
        Ship <em style={{ fontStyle: 'italic', background: 'linear-gradient(135deg,#ffbd69,#ff9d2f,#f07d0a)', WebkitBackgroundClip: 'text', backgroundClip: 'text', color: 'transparent' }}>Direction 01 — Phase Arc.</em>
      </div>
      <div style={{ fontFamily: 'Fraunces, serif', fontSize: 17, fontWeight: 400, color: INK_2, lineHeight: 1.55, maxWidth: 580, textWrap: 'pretty' }}>
        It is the only direction that satisfies all four constraints at once: <strong style={{ color: INK, fontWeight: 500 }}>literally a dial</strong> (matches the product name), <strong style={{ color: INK, fontWeight: 500 }}>scales</strong> from 64px favicon to a hero element, <strong style={{ color: INK, fontWeight: 500 }}>encodes both discrete state and a continuous score</strong> via needle angle, and <strong style={{ color: INK, fontWeight: 500 }}>renders identically in inline SVG</strong> across Gmail / Apple Mail / Outlook 365.
      </div>
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: 10,
        marginTop: 8,
      }}>
        {[
          { k: '01', v: 'Built for animation', d: 'Needle rotates between phases; 600ms easeInOutCubic. Falls back to instant in email.' },
          { k: '02', v: 'Score-aware', d: 'Needle can render at score=0–100 inside the phase zone, preserving the granularity of the current strip.' },
          { k: '03', v: 'Brand-safe', d: 'Uses the existing orange/green/red palette + a purple "top" — no new colors invented.' },
          { k: '04', v: 'Two-format', d: 'One React component, one stripped SVG snippet. Same data, same look.' },
        ].map(item => (
          <div key={item.k} style={{
            background: 'rgba(255,255,255,0.04)',
            border: `1px solid ${LINE}`,
            borderRadius: 12,
            padding: '14px 14px 12px',
          }}>
            <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 10, letterSpacing: '0.2em', color: INK_4 }}>{item.k}</div>
            <div style={{ fontFamily: 'Fraunces, serif', fontSize: 17, color: INK, marginTop: 6, letterSpacing: '-0.01em' }}>{item.v}</div>
            <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: INK_2, marginTop: 6, lineHeight: 1.5 }}>{item.d}</div>
          </div>
        ))}
      </div>
      <div style={{
        marginTop: 'auto',
        padding: '14px 16px',
        background: 'rgba(255,157,47,0.06)',
        border: '1px solid rgba(255,157,47,0.25)',
        borderLeft: '3px solid #ff9d2f',
        borderRadius: '0 12px 12px 0',
        fontFamily: 'Inter, sans-serif',
        fontSize: 13, lineHeight: 1.55, color: INK_2,
      }}>
        <strong style={{ color: INK, fontWeight: 600 }}>Pick another?</strong> The Claude Code handoff is parameterised — swap <code style={{ fontFamily: '"JetBrains Mono", monospace', color: '#ff9d2f', fontSize: 12 }}>D1</code> for any of <code style={{ fontFamily: '"JetBrains Mono", monospace', color: '#ff9d2f', fontSize: 12 }}>D2…D5</code> in the doc&rsquo;s first table and the rest of the handoff still applies.
      </div>
    </div>
  );
}

/* ──────────────────────────  CANVAS  ────────────────────────── */
function App() {
  return (
    <DesignCanvas
      title="MacroPulse — Dial Directions"
      subtitle="Five alternates for the cycle dial · 4 states · ready for web + email"
    >
      <DCSection
        id="all-states"
        title="Five directions · all four states each"
        subtitle="Each artboard shows one design rendered at every cycle state. Click any artboard to focus."
      >
        {DESIGNS.map((d, idx) => (
          <DCArtboard key={d.id} id={d.id} label={`D${idx + 1} · ${d.name}`} width={d.width} height={d.height}>
            <DesignArtboard design={d} n={idx + 1}/>
          </DCArtboard>
        ))}
      </DCSection>

      <DCSection
        id="comparison"
        title="Head-to-head"
        subtitle="The same state across all five directions. Easiest way to compare visual weight."
      >
        <DCArtboard id="cmp-risk-off" label="State · Risk Off" width={1100} height={460}>
          <ComparisonArtboard state="risk-off"/>
        </DCArtboard>
        <DCArtboard id="cmp-btc" label="State · BTC Accumulation" width={1100} height={460}>
          <ComparisonArtboard state="btc"/>
        </DCArtboard>
        <DCArtboard id="cmp-alt" label="State · ALT Rotation" width={1100} height={460}>
          <ComparisonArtboard state="alt"/>
        </DCArtboard>
        <DCArtboard id="cmp-profit" label="State · Take Profit" width={1100} height={460}>
          <ComparisonArtboard state="profit"/>
        </DCArtboard>
      </DCSection>

      <DCSection
        id="recommendation"
        title="Recommendation + handoff"
        subtitle="Where we'd ship. See dials/Dial Handoff.md for the implementation brief."
      >
        <DCArtboard id="recommendation" label="Recommendation" width={900} height={580}>
          <RecommendationArtboard/>
        </DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App/>);
