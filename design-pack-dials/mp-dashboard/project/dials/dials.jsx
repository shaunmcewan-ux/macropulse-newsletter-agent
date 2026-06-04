/* global React */
/* MacroPulse — 5 dial directions
 * Each component takes { state, size, score? } and renders an SVG dial.
 * Palette mirrors macropulse.uk's restrained orange/green/red plus a purple "top".
 */

const PHASES = [
  { id: 'risk-off', label: 'Risk Off',         abbr: 'RO',  color: '#ef5a6b', soft: 'rgba(239,90,107,0.16)', glow: 'rgba(239,90,107,0.45)', sublabel: 'Cash. Defensive. Wait.' },
  { id: 'btc',      label: 'BTC Accumulation', abbr: 'BTC', color: '#ff9d2f', soft: 'rgba(255,157,47,0.16)',  glow: 'rgba(255,157,47,0.45)',  sublabel: 'Build core position.' },
  { id: 'alt',      label: 'ALT Rotation',     abbr: 'ALT', color: '#4ec38a', soft: 'rgba(78,195,138,0.16)',  glow: 'rgba(78,195,138,0.45)',  sublabel: 'Capital flowing out the curve.' },
  { id: 'profit',   label: 'Take Profit',      abbr: 'TP',  color: '#b794f6', soft: 'rgba(183,148,246,0.16)', glow: 'rgba(183,148,246,0.45)', sublabel: 'Distribute. Lock gains.' },
];
const PHASE_BY_ID = Object.fromEntries(PHASES.map(p => [p.id, p]));
const phaseIndex = (id) => PHASES.findIndex(p => p.id === id);

const INK   = '#edf3f7';
const INK_2 = '#b9c4cc';
const INK_3 = '#7c8a95';
const INK_4 = '#4a5763';
const LINE  = 'rgba(237,243,247,0.10)';
const LINE_STRONG = 'rgba(237,243,247,0.16)';

/* ============================================================ *
 * D1 — Phase Arc (half-dial speedometer)                       *
 *   180° arc, 4 zones, animated needle, score readout below     *
 * ============================================================ */
function DialPhaseArc({ state = 'btc', score = null, size = 280 }) {
  const w = size, h = size * 0.72;
  const cx = w / 2, cy = h - 28;
  const r = w / 2 - 24;
  const i = phaseIndex(state);
  // each zone is 45° of the 180° arc. needle sits at zone midpoint
  const angleAt = (idx) => -180 + 22.5 + (idx * 45);
  const needleAngle = (typeof score === 'number')
    ? -180 + (score / 100) * 180
    : angleAt(i);
  const rad = (deg) => (deg * Math.PI) / 180;
  const polar = (radius, deg) => [cx + radius * Math.cos(rad(deg)), cy + radius * Math.sin(rad(deg))];

  const arcPath = (rOuter, rInner, a0, a1) => {
    const [x0o, y0o] = polar(rOuter, a0);
    const [x1o, y1o] = polar(rOuter, a1);
    const [x1i, y1i] = polar(rInner, a1);
    const [x0i, y0i] = polar(rInner, a0);
    return `M ${x0o} ${y0o} A ${rOuter} ${rOuter} 0 0 1 ${x1o} ${y1o} L ${x1i} ${y1i} A ${rInner} ${rInner} 0 0 0 ${x0i} ${y0i} Z`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} role="img" aria-label={`Dial state: ${PHASE_BY_ID[state].label}`}>
        {/* zone arcs */}
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
        {/* tick labels */}
        {PHASES.map((p, idx) => {
          const [tx, ty] = polar(r + 14, -180 + idx * 45 + 22.5);
          return (
            <text key={p.id}
              x={tx} y={ty + 4}
              textAnchor="middle"
              fontFamily='"JetBrains Mono", ui-monospace, monospace'
              fontSize={9}
              letterSpacing="0.18em"
              fill={idx === i ? p.color : INK_3}
              style={{ textTransform: 'uppercase', fontWeight: idx === i ? 600 : 500 }}
            >{p.abbr}</text>
          );
        })}
        {/* needle */}
        <g transform={`translate(${cx} ${cy}) rotate(${needleAngle + 90})`}>
          <line x1="0" y1="0" x2="0" y2={-(r - 12)} stroke={PHASE_BY_ID[state].color} strokeWidth="2.5" strokeLinecap="round"/>
          <circle cx="0" cy={-(r - 12)} r="4" fill={PHASE_BY_ID[state].color}/>
        </g>
        {/* hub */}
        <circle cx={cx} cy={cy} r="8" fill="#0c141b" stroke={LINE_STRONG}/>
        <circle cx={cx} cy={cy} r="3" fill={PHASE_BY_ID[state].color}/>
      </svg>
      <div style={{ textAlign: 'center', marginTop: -8 }}>
        <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', color: INK_3 }}>Current Phase</div>
        <div style={{ fontFamily: 'Fraunces, Georgia, serif', fontSize: 22, color: PHASE_BY_ID[state].color, fontWeight: 500, letterSpacing: '-0.01em', marginTop: 6, lineHeight: 1 }}>
          {PHASE_BY_ID[state].label}
        </div>
      </div>
    </div>
  );
}

/* ============================================================ *
 * D2 — Concentric Phase Rings                                   *
 *   4 nested rings; active ring filled, others ghosted          *
 *   Distinctive, editorial — feels like the dial.               *
 * ============================================================ */
function DialConcentricRings({ state = 'btc', size = 280 }) {
  const i = phaseIndex(state);
  const cx = size / 2, cy = size / 2;
  // ring radii from outer to inner correspond to phases 0..3
  const ringRadii = [size * 0.46, size * 0.38, size * 0.30, size * 0.22];
  const stroke = 6;
  const phase = PHASE_BY_ID[state];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {/* background rings (all ghosted) */}
        {PHASES.map((p, idx) => (
          <circle key={`bg-${p.id}`}
            cx={cx} cy={cy} r={ringRadii[idx]}
            fill="none"
            stroke={p.color}
            strokeOpacity={0.16}
            strokeWidth={stroke}
          />
        ))}
        {/* active ring — drawn solid with glow */}
        <defs>
          <filter id={`glow-${state}`} x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="b"/>
            <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
          </filter>
        </defs>
        <circle cx={cx} cy={cy} r={ringRadii[i]}
          fill="none" stroke={phase.color} strokeWidth={stroke + 1}
          strokeLinecap="round"
          filter={`url(#glow-${state})`}
        />
        {/* phase markers around active ring at 4 cardinal points showing the cycle position */}
        {PHASES.map((p, idx) => {
          const angle = (idx / 4) * Math.PI * 2 - Math.PI / 2;
          const x = cx + ringRadii[i] * Math.cos(angle);
          const y = cy + ringRadii[i] * Math.sin(angle);
          const active = idx === i;
          return (
            <g key={`m-${p.id}`}>
              <circle cx={x} cy={y} r={active ? 7 : 3.5} fill={active ? p.color : '#0c141b'} stroke={p.color} strokeWidth={active ? 0 : 1.5}/>
            </g>
          );
        })}
        {/* center label */}
        <text x={cx} y={cy - 4} textAnchor="middle"
          fontFamily='"JetBrains Mono", monospace' fontSize={9}
          letterSpacing="0.22em" fill={INK_3}
          style={{ textTransform: 'uppercase' }}
        >Phase</text>
        <text x={cx} y={cy + 16} textAnchor="middle"
          fontFamily='Fraunces, serif' fontSize={20}
          fill={phase.color} fontWeight={500} letterSpacing="-0.01em"
        >{phase.abbr}</text>
      </svg>
      <div style={{ textAlign: 'center', marginTop: -8 }}>
        <div style={{ fontFamily: 'Fraunces, serif', fontSize: 22, color: phase.color, fontWeight: 500, letterSpacing: '-0.01em', lineHeight: 1 }}>
          {phase.label}
        </div>
        <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: INK_3, marginTop: 6 }}>Ring {i + 1} of 4 &middot; cycle outside&rarr;in</div>
      </div>
    </div>
  );
}

/* ============================================================ *
 * D3 — Cycle Wheel (full circle, 4 quadrants)                   *
 *   Quadrants colored by phase; marker dot on perimeter         *
 *   Conveys cyclical nature                                     *
 * ============================================================ */
function DialCycleWheel({ state = 'btc', size = 280 }) {
  const i = phaseIndex(state);
  const phase = PHASE_BY_ID[state];
  const cx = size / 2, cy = size / 2;
  const r = size * 0.42;
  const rInner = size * 0.30;
  const rad = (deg) => (deg * Math.PI) / 180;
  const polar = (radius, deg) => [cx + radius * Math.cos(rad(deg)), cy + radius * Math.sin(rad(deg))];

  // start at top, go clockwise: phase 0 occupies -90..0, etc
  const arcPath = (a0, a1) => {
    const [x0o, y0o] = polar(r, a0);
    const [x1o, y1o] = polar(r, a1);
    const [x1i, y1i] = polar(rInner, a1);
    const [x0i, y0i] = polar(rInner, a0);
    const large = a1 - a0 > 180 ? 1 : 0;
    return `M ${x0o} ${y0o} A ${r} ${r} 0 ${large} 1 ${x1o} ${y1o} L ${x1i} ${y1i} A ${rInner} ${rInner} 0 ${large} 0 ${x0i} ${y0i} Z`;
  };
  // marker sits at midpoint of active quadrant on outer perimeter
  const markerAngle = -90 + i * 90 + 45;
  const [mx, my] = polar(r + 12, markerAngle);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        {PHASES.map((p, idx) => {
          const a0 = -90 + idx * 90 + 1.5;
          const a1 = -90 + (idx + 1) * 90 - 1.5;
          const active = idx === i;
          return (
            <path key={p.id}
              d={arcPath(a0, a1)}
              fill={p.color}
              fillOpacity={active ? 0.92 : 0.18}
            />
          );
        })}
        {/* phase abbrev labels at quadrant midpoints */}
        {PHASES.map((p, idx) => {
          const mid = -90 + idx * 90 + 45;
          const [lx, ly] = polar((r + rInner) / 2, mid);
          const active = idx === i;
          return (
            <text key={`l-${p.id}`}
              x={lx} y={ly + 3.5}
              textAnchor="middle"
              fontFamily='"JetBrains Mono", monospace' fontSize={10}
              letterSpacing="0.18em"
              fill={active ? '#0c141b' : INK_2}
              fontWeight={active ? 700 : 500}
              style={{ textTransform: 'uppercase' }}
            >{p.abbr}</text>
          );
        })}
        {/* outer perimeter marker dot — the current "now" */}
        <line x1={cx} y1={cy} x2={polar(r + 2, markerAngle)[0]} y2={polar(r + 2, markerAngle)[1]}
              stroke={phase.color} strokeOpacity="0" />
        <circle cx={mx} cy={my} r={6} fill={phase.color}/>
        <circle cx={mx} cy={my} r={11} fill={phase.color} fillOpacity={0.25}/>
        {/* center hub with cycle index */}
        <circle cx={cx} cy={cy} r={rInner - 8} fill="#0c141b" stroke={LINE}/>
        <text x={cx} y={cy - 4} textAnchor="middle"
          fontFamily='"JetBrains Mono", monospace' fontSize={9}
          letterSpacing="0.22em" fill={INK_3}
          style={{ textTransform: 'uppercase' }}
        >Cycle</text>
        <text x={cx} y={cy + 18} textAnchor="middle"
          fontFamily='Fraunces, serif' fontSize={22}
          fill={phase.color} fontWeight={500}
        >{i + 1}/4</text>
      </svg>
      <div style={{ textAlign: 'center', marginTop: -8 }}>
        <div style={{ fontFamily: 'Fraunces, serif', fontSize: 22, color: phase.color, fontWeight: 500, letterSpacing: '-0.01em', lineHeight: 1 }}>
          {phase.label}
        </div>
        <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: INK_3, marginTop: 6 }}>Clockwise &middot; one full revolution per cycle</div>
      </div>
    </div>
  );
}

/* ============================================================ *
 * D4 — Stepped Ladder (vertical thermometer)                    *
 *   4 horizontal bars stacked; fills bottom→top up to current   *
 *   Editorial / Swiss / data-dashboard feel                     *
 * ============================================================ */
function DialSteppedLadder({ state = 'btc', size = 280 }) {
  const i = phaseIndex(state);
  const phase = PHASE_BY_ID[state];
  const w = size;
  const h = size * 1.05;
  const rowH = 36;
  const gap = 8;
  const startY = h - 14 - rowH;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
        {/* axis line */}
        <line x1="38" y1="14" x2="38" y2={h - 14} stroke={LINE} strokeWidth="1"/>
        {PHASES.map((p, idx) => {
          // phase 0 = Risk Off at bottom (defensive baseline), phase 3 = Take Profit at top
          // visual stack: bottom to top, so idx 0 sits lowest
          const y = startY - idx * (rowH + gap);
          const active = idx === i;
          const filled = idx <= i;
          return (
            <g key={p.id}>
              {/* index marker on axis */}
              <circle cx="38" cy={y + rowH / 2} r={active ? 6 : 3} fill={filled ? p.color : '#0c141b'} stroke={p.color} strokeWidth={active ? 0 : 1.5}/>
              {/* bar */}
              <rect x="58" y={y} width={w - 78} height={rowH}
                fill={filled ? p.color : 'transparent'}
                fillOpacity={active ? 1 : (filled ? 0.16 : 0)}
                stroke={p.color} strokeOpacity={filled ? 0 : 0.18}
                strokeWidth="1"
                rx="6"
              />
              {/* label inside bar */}
              <text x="74" y={y + rowH / 2 + 4}
                fontFamily='"JetBrains Mono", monospace' fontSize={10}
                letterSpacing="0.18em"
                fill={active ? '#0c141b' : (filled ? p.color : INK_3)}
                fontWeight={active ? 700 : 500}
                style={{ textTransform: 'uppercase' }}
              >{size < 260 ? p.abbr : p.label}</text>
              {/* phase number trailing */}
              <text x={w - 28} y={y + rowH / 2 + 4}
                textAnchor="end"
                fontFamily='"JetBrains Mono", monospace' fontSize={10}
                fill={active ? '#0c141b' : INK_4}
                fontWeight={active ? 700 : 500}
              >0{idx + 1}</text>
            </g>
          );
        })}
      </svg>
      <div style={{ textAlign: 'center', marginTop: -8 }}>
        <div style={{ fontFamily: 'Fraunces, serif', fontSize: 22, color: phase.color, fontWeight: 500, letterSpacing: '-0.01em', lineHeight: 1 }}>
          {phase.label}
        </div>
        <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: INK_3, marginTop: 6 }}>Step {i + 1} of 4 &middot; fills as cycle advances</div>
      </div>
    </div>
  );
}

/* ============================================================ *
 * D5 — Tape Reader (segmented horizontal bar)                   *
 *   4 named segments; active segment glows                      *
 *   Most email-friendly; refined evolution of current strip     *
 * ============================================================ */
function DialTapeReader({ state = 'btc', size = 280 }) {
  const i = phaseIndex(state);
  const phase = PHASE_BY_ID[state];
  const w = size;
  const h = 80;
  const segW = (w - 24) / 4;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14, width: w + 20 }}>
      <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'baseline' }}>
        <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', color: INK_3 }}>MacroPulse</div>
        <div style={{ fontFamily: '"JetBrains Mono", monospace', fontSize: 10, letterSpacing: '0.22em', textTransform: 'uppercase', color: INK_3 }}>0{i + 1}/04</div>
      </div>
      <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
        {PHASES.map((p, idx) => {
          const x = 12 + idx * segW;
          const active = idx === i;
          // pill shape: only outer segments have rounded outer corners
          const isFirst = idx === 0, isLast = idx === 3;
          const rTL = isFirst ? 16 : 0;
          const rBL = isFirst ? 16 : 0;
          const rTR = isLast ? 16 : 0;
          const rBR = isLast ? 16 : 0;
          // path with custom corners
          const path = `M ${x + rTL} 12
                        L ${x + segW - 2 - rTR} 12
                        ${rTR ? `Q ${x + segW - 2} 12 ${x + segW - 2} ${12 + rTR}` : `L ${x + segW - 2} 12`}
                        L ${x + segW - 2} ${44 - rBR}
                        ${rBR ? `Q ${x + segW - 2} 44 ${x + segW - 2 - rBR} 44` : `L ${x + segW - 2} 44`}
                        L ${x + rBL} 44
                        ${rBL ? `Q ${x} 44 ${x} ${44 - rBL}` : `L ${x} 44`}
                        L ${x} ${12 + rTL}
                        ${rTL ? `Q ${x} 12 ${x + rTL} 12` : `L ${x} 12`}
                        Z`;
          return (
            <g key={p.id}>
              <path d={path}
                fill={p.color}
                fillOpacity={active ? 0.92 : 0.14}
              />
              {active && (
                <path d={path}
                  fill="none" stroke={p.color} strokeWidth="1.5" strokeOpacity="0.5"
                />
              )}
              <text x={x + segW / 2} y={62}
                textAnchor="middle"
                fontFamily='"JetBrains Mono", monospace' fontSize={10}
                letterSpacing="0.18em"
                fill={active ? p.color : INK_3}
                fontWeight={active ? 600 : 500}
                style={{ textTransform: 'uppercase' }}
              >{p.abbr}</text>
            </g>
          );
        })}
        {/* pointer triangle above active segment */}
        <g transform={`translate(${12 + i * segW + segW / 2} 4)`}>
          <path d="M -5 0 L 5 0 L 0 8 Z" fill={phase.color}/>
        </g>
      </svg>
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontFamily: 'Fraunces, serif', fontSize: 22, color: phase.color, fontWeight: 500, letterSpacing: '-0.01em', lineHeight: 1 }}>
          {phase.label}
        </div>
        <div style={{ fontFamily: 'Inter, sans-serif', fontSize: 12, color: INK_3, marginTop: 6 }}>{phase.sublabel}</div>
      </div>
    </div>
  );
}

/* expose for canvas file */
Object.assign(window, {
  PHASES, PHASE_BY_ID, INK, INK_2, INK_3, INK_4, LINE, LINE_STRONG,
  DialPhaseArc, DialConcentricRings, DialCycleWheel, DialSteppedLadder, DialTapeReader,
});
