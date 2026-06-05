export default function ScoreGauge({ value = 0, label = '', size = 'default', color }) {
  const r = 45;
  const c = 2 * Math.PI * r;
  const p = Math.max(0, Math.min(100, value));
  const offset = c - (p / 100) * c;

  const autoColor = color || (
    value >= 80 ? '#1B7A4E' : value >= 60 ? '#B45309' : '#C53030'
  );

  const dim = size === 'large' ? 110 : 90;

  return (
    <div className={`gauge-wrap ${size === 'large' ? 'lg' : ''}`} style={{ width: dim, height: dim }}>
      <svg width="100%" height="100%" viewBox="0 0 100 100">
        <circle className="gauge-bg" cx="50" cy="50" r={r} />
        <circle
          className="gauge-fill"
          cx="50" cy="50" r={r}
          stroke={autoColor}
          strokeDasharray={c}
          strokeDashoffset={offset}
        />
      </svg>
      <div className="gauge-center">
        <div className="gv" style={{ color: autoColor }}>{Math.round(value)}</div>
        {label && <div className="gl">{label}</div>}
      </div>
    </div>
  );
}
