export function StatTile({ label, value, unit, sub, accentVar }) {
  return (
    <div className="stat-tile" style={accentVar ? { '--tile-accent': `var(${accentVar})` } : undefined}>
      <div className="stat-tile__label">{label}</div>
      <div className="stat-tile__value tabular-nums">
        {value}
        {unit ? <span className="stat-tile__unit"> {unit}</span> : null}
      </div>
      {sub ? <div className="stat-tile__sub">{sub}</div> : null}
    </div>
  );
}
