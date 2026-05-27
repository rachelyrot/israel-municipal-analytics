// Semi-circular gauge for percentage KPIs.
// The arc goes from left (0%) through the top to right (100%).
// A tick marks the national average position.
export function SemiGauge({ value, nationalAvg, higherIsBetter, unit }) {
  const W = 120, H = 72, cx = 60, cy = 70, r = 52, sw = 11

  function pt(pct) {
    const a = Math.PI * (1 - pct)
    return [cx + r * Math.cos(a), cy - r * Math.sin(a)]
  }

  function arcPath(p0, p1) {
    const [fx, fy] = pt(p0)
    const [tx, ty] = pt(p1)
    // sweep=0 → counterclockwise in SVG screen space → top arc
    return `M ${fx.toFixed(2)} ${fy.toFixed(2)} A ${r} ${r} 0 0 0 ${tx.toFixed(2)} ${ty.toFixed(2)}`
  }

  const v = Math.min(100, Math.max(0, value ?? 0))
  const av = Math.min(100, Math.max(0, nationalAvg ?? 50))
  const vp = v / 100

  const isAbove = value != null && nationalAvg != null && value > nationalAvg
  const color = nationalAvg == null
    ? '#3b82f6'
    : higherIsBetter === false
      ? (isAbove ? '#ef4444' : '#22c55e')
      : (isAbove ? '#22c55e' : '#ef4444')

  // Tick endpoints for national average
  const ang = Math.PI * (1 - av / 100)
  const [ix, iy] = [cx + (r - sw) * Math.cos(ang), cy - (r - sw) * Math.sin(ang)]
  const [ox, oy] = [cx + (r + 5) * Math.cos(ang), cy - (r + 5) * Math.sin(ang)]

  return (
    <svg width={W} height={H} viewBox={`0 0 ${W} ${H}`} className="block mx-auto overflow-visible">
      {/* background arc */}
      <path d={arcPath(0, 1)} fill="none" stroke="#e5e7eb" strokeWidth={sw} strokeLinecap="round" />
      {/* value arc */}
      {vp > 0.005 && (
        <path d={arcPath(0, vp)} fill="none" stroke={color} strokeWidth={sw} strokeLinecap="round" />
      )}
      {/* national average tick */}
      {nationalAvg != null && (
        <line x1={ix.toFixed(2)} y1={iy.toFixed(2)} x2={ox.toFixed(2)} y2={oy.toFixed(2)}
          stroke="#374151" strokeWidth={2.5} strokeLinecap="round" />
      )}
      {/* value label */}
      <text x={cx} y={cy - 18} textAnchor="middle" fontSize={19} fontWeight="700" fill="#111827">
        {v.toLocaleString('he-IL', { maximumFractionDigits: 1 })}
      </text>
      <text x={cx} y={cy - 4} textAnchor="middle" fontSize={9} fill="#9ca3af">{unit}</text>
    </svg>
  )
}
