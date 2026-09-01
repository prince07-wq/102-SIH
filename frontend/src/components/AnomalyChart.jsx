import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';
import './AnomalyChart.css';

const COLORS = {
  cost: '#c8402c',
  delay: '#b5721a',
  expenditure: '#2a5f8f',
  duplicate: '#1f6e4a',
};

/**
 * AnomalyChart — donut visualization of anomaly-type distribution.
 * This component owns all chart/graph rendering for anomaly types.
 * RiskBadge is not involved here; it renders overall risk levels.
 *
 * Props:
 *  - data: [{ key, label, value, pct }]
 *  - centerLabel: string (optional) e.g. "12.4L"
 *  - centerSublabel: string (optional) e.g. "Analysed"
 */
export default function AnomalyChart({ data = [], centerLabel, centerSublabel = 'Analysed' }) {
  const chartData = data.map((d) => ({ ...d, fill: COLORS[d.key] || '#8b9188' }));

  return (
    <div className="anomaly-chart">
      <h3 className="panel-title">Risk by Anomaly Type</h3>

      <div className="anomaly-chart__body">
        <div className="anomaly-chart__donut">
          <ResponsiveContainer width="100%" height={160}>
            <PieChart>
              <Pie
                data={chartData}
                dataKey="value"
                nameKey="label"
                cx="50%"
                cy="50%"
                innerRadius={48}
                outerRadius={72}
                paddingAngle={2}
                stroke="none"
              >
                {chartData.map((entry) => (
                  <Cell key={entry.key} fill={entry.fill} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
          {centerLabel && (
            <div className="anomaly-chart__center">
              <span className="anomaly-chart__center-value">{centerLabel}</span>
              <span className="anomaly-chart__center-label">{centerSublabel}</span>
            </div>
          )}
        </div>

        <ul className="anomaly-chart__legend">
          {chartData.map((d) => (
            <li key={d.key} className="anomaly-chart__legend-item">
              <span className="anomaly-chart__legend-dot" style={{ background: d.fill }} />
              <span className="anomaly-chart__legend-label">{d.label}</span>
              <span className="anomaly-chart__legend-pct">{d.pct.toFixed(1)}%</span>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
