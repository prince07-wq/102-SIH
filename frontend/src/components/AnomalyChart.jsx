import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import './AnomalyChart.css';

const COLORS = {
  cost: '#c8402c',
  delay: '#b5721a',
  expenditure: '#2a5f8f',
  duplicate: '#1f6e4a',
};

const FACTORS = [
  { key: 'cost', label: 'Cost' },
  { key: 'delay', label: 'Delay' },
  { key: 'expenditure', label: 'Expenditure' },
  { key: 'duplicate', label: 'Duplicate' },
];

/**
 * Factor analytics card: nationwide detector ranking, or state-scoped
 * anomaly-type and detector-score distributions. ML scores are intentionally
 * not rendered here.
 */
export default function AnomalyChart({
  data = [],
  centerLabel,
  centerSublabel = 'Analysed',
  analytics,
  factor,
  selectedState,
  loading = false,
  error,
  onFactorChange,
  onStateSelect,
  onRetry,
}) {
  const chartData = data.map((d) => ({ ...d, fill: COLORS[d.key] || '#8b9188' }));
  const factorLabel = FACTORS.find((item) => item.key === factor)?.label;
  const isStateView = selectedState && selectedState !== 'All';
  const hasDistribution = analytics?.scoreBands?.some((band) => band.projectCount > 0);
  const rankedStates = analytics?.stateMetrics || [];

  return (
    <div className="anomaly-chart">
      <div className="anomaly-chart__header">
        <div>
          <h3 className="panel-title">
            {!factor
              ? `Risk by Anomaly Type${isStateView ? ` — ${selectedState}` : ''}`
              : isStateView
                ? `${factorLabel} Risk in ${selectedState}`
                : `${factorLabel} Risk by State — All India`}
          </h3>
          <p className="anomaly-chart__subtitle">
            {factor
              ? 'Detector score indicates review priority, not fraud probability.'
              : 'Distribution of projects flagged by each explainable detector.'}
          </p>
        </div>
        <div className="anomaly-chart__factors" aria-label="Anomaly factor">
          {FACTORS.map((item) => (
            <button
              key={item.key}
              type="button"
              className={item.key === factor ? 'is-active' : ''}
              onClick={() => onFactorChange(item.key === factor ? null : item.key)}
              aria-pressed={item.key === factor}
            >
              {item.label}
            </button>
          ))}
        </div>
      </div>

      {!factor && (
        chartData.some((item) => item.value > 0) ? (
          <OverviewDonut
            data={chartData}
            centerLabel={centerLabel}
            centerSublabel={centerSublabel}
          />
        ) : <ChartStatus>No flagged detector signals in this scope.</ChartStatus>
      )}

      {factor && loading && <ChartStatus>Loading factor analytics…</ChartStatus>}
      {factor && !loading && error && (
        <ChartStatus tone="error">
          <span>Unable to load factor analytics: {error}</span>
          <button type="button" onClick={onRetry}>Retry</button>
        </ChartStatus>
      )}
      {factor && !loading && !error && !analytics && <ChartStatus>No analytics available.</ChartStatus>}

      {factor && !loading && !error && analytics && !isStateView && (
        rankedStates.length ? (
          <div className="anomaly-chart__ranking" role="img" aria-label={`${factorLabel} risk ranking by state`}>
            <div style={{ height: Math.max(320, rankedStates.length * 29) }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={rankedStates} layout="vertical" margin={{ top: 4, right: 28, bottom: 8, left: 8 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} label={{ value: 'Average detector score', position: 'insideBottom', offset: -4, fontSize: 11 }} />
                  <YAxis type="category" dataKey="state" width={126} tick={{ fontSize: 11 }} interval={0} />
                  <Tooltip content={<StateTooltip factorLabel={factorLabel} />} />
                  <Bar
                    dataKey="averageScore"
                    fill={COLORS[factor]}
                    radius={[0, 3, 3, 0]}
                    minPointSize={2}
                    cursor="pointer"
                    onClick={(entry) => onStateSelect(entry?.state || entry?.payload?.state)}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        ) : <ChartStatus>No states match the current filters.</ChartStatus>
      )}

      {factor && !loading && !error && analytics && isStateView && (
        <div className="anomaly-chart__state-view anomaly-chart__state-view--factor">
          <section className="anomaly-chart__state-section">
            <h4>{factorLabel} detector score distribution</h4>
            {hasDistribution ? (
              <>
                <div className="anomaly-chart__distribution">
                  <ResponsiveContainer width="100%" height={190}>
                    <BarChart data={analytics.scoreBands} margin={{ top: 8, right: 8, bottom: 6, left: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} />
                      <XAxis dataKey="label" tick={{ fontSize: 11 }} />
                      <YAxis allowDecimals={false} tick={{ fontSize: 11 }} width={48} />
                      <Tooltip formatter={(value) => [value, 'Projects']} />
                      <Bar dataKey="projectCount" fill={COLORS[factor]} radius={[3, 3, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
                {analytics.unscoredProjects > 0 && (
                  <p className="anomaly-chart__note">
                    {analytics.unscoredProjects.toLocaleString('en-IN')} not-applicable project(s) excluded from score bands.
                  </p>
                )}
              </>
            ) : <ChartStatus>No detector scores match the current filters.</ChartStatus>}
          </section>
        </div>
      )}
    </div>
  );
}

function OverviewDonut({ data, centerLabel, centerSublabel }) {
  return (
    <div className="anomaly-chart__body">
      <div className="anomaly-chart__donut">
        <ResponsiveContainer width="100%" height={160}>
          <PieChart>
            <Pie data={data} dataKey="value" nameKey="label" cx="50%" cy="50%" innerRadius={48} outerRadius={72} paddingAngle={2} stroke="none">
              {data.map((entry) => <Cell key={entry.key} fill={entry.fill} />)}
            </Pie>
            <Tooltip formatter={(value, name) => [value, name]} />
          </PieChart>
        </ResponsiveContainer>
        {centerLabel && (
          <div className="anomaly-chart__center">
            <span className="anomaly-chart__center-value">{centerLabel}</span>
            <span className="anomaly-chart__center-label">{centerSublabel}</span>
          </div>
        )}
      </div>
      <AnomalyLegend data={data} />
    </div>
  );
}

function AnomalyLegend({ data }) {
  return (
    <ul className="anomaly-chart__legend">
      {data.map((item) => (
        <li key={item.key} className="anomaly-chart__legend-item">
          <span className="anomaly-chart__legend-dot" style={{ background: item.fill }} />
          <span className="anomaly-chart__legend-label">{item.label}</span>
          <span className="anomaly-chart__legend-pct">{item.pct.toFixed(1)}%</span>
        </li>
      ))}
    </ul>
  );
}

function StateTooltip({ active, payload, factorLabel }) {
  if (!active || !payload?.length) return null;
  const state = payload[0].payload;
  return (
    <div className="anomaly-chart__tooltip">
      <strong>{state.state}</strong>
      <span>{factorLabel} average score: {state.averageScore?.toFixed(2) ?? 'Unavailable'}</span>
      <span>Flagged projects: {state.flaggedProjects.toLocaleString('en-IN')}</span>
      <span>Total projects: {state.totalProjects.toLocaleString('en-IN')}</span>
    </div>
  );
}

function ChartStatus({ children, tone = 'neutral' }) {
  return <div className={`anomaly-chart__status anomaly-chart__status--${tone}`}>{children}</div>;
}
