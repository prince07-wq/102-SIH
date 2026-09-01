import './StatCard.css';

/**
 * StatCard — reusable KPI card. No dashboard-specific data lives here.
 *
 * Props:
 *  - title: string
 *  - value: string | number
 *  - subtitle: string (optional)
 *  - trend: string (optional) e.g. "+8.7%"
 *  - trendDirection: 'up' | 'down' (optional, default inferred from trend sign)
 *  - icon: ReactNode (optional)
 *  - accent: 'default' | 'high' | 'info' (optional) — tints the icon chip
 *  - sparkline: number[] (optional) — small trend line under the value
 */
export default function StatCard({
  title,
  value,
  subtitle,
  trend,
  trendDirection,
  icon,
  accent = 'default',
  sparkline,
}) {
  const direction = trendDirection || (trend && trend.trim().startsWith('-') ? 'down' : 'up');

  return (
    <div className="stat-card">
      <div className="stat-card__top">
        {icon && <div className={`stat-card__icon stat-card__icon--${accent}`}>{icon}</div>}
        {trend && (
          <span className={`stat-card__trend stat-card__trend--${direction}`}>
            <TrendArrow direction={direction} />
            {trend}
          </span>
        )}
      </div>

      <div className="stat-card__value">{value}</div>
      <div className="stat-card__title">{title}</div>
      {subtitle && <div className="stat-card__subtitle">{subtitle}</div>}

      {sparkline && sparkline.length > 1 && (
        <Sparkline data={sparkline} direction={direction} />
      )}
    </div>
  );
}

function TrendArrow({ direction }) {
  return direction === 'down' ? (
    <svg width="10" height="10" viewBox="0 0 10 10" fill="none" aria-hidden="true">
      <path d="M2 3L5 7L8 3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ) : (
    <svg width="10" height="10" viewBox="0 0 10 10" fill="none" aria-hidden="true">
      <path d="M2 7L5 3L8 7" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function Sparkline({ data, direction }) {
  const w = 100;
  const h = 26;
  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1;
  const step = w / (data.length - 1);

  const points = data
    .map((d, i) => {
      const x = i * step;
      const y = h - ((d - min) / range) * h;
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(' ');

  const color = direction === 'down' ? 'var(--risk-high)' : 'var(--brand-primary)';

  return (
    <svg className="stat-card__spark" viewBox={`0 0 ${w} ${h}`} preserveAspectRatio="none" aria-hidden="true">
      <polyline points={points} fill="none" stroke={color} strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
