import { useMemo, useState } from 'react';
import './HeatMap.css';

function scoreToColor(score) {
  // 0 -> green, 50 -> amber, 100 -> red, interpolated in two stops
  const clamped = Math.max(0, Math.min(100, score));
  if (clamped <= 50) {
    const t = clamped / 50;
    return mix([201, 224, 210], [240, 191, 122], t); // low-green -> amber
  }
  const t = (clamped - 50) / 50;
  return mix([240, 191, 122], [200, 64, 44], t); // amber -> high-red
}

function mix(a, b, t) {
  const r = Math.round(a[0] + (b[0] - a[0]) * t);
  const g = Math.round(a[1] + (b[1] - a[1]) * t);
  const bl = Math.round(a[2] + (b[2] - a[2]) * t);
  return `rgb(${r}, ${g}, ${bl})`;
}

function riskLabel(score) {
  if (score >= 80) return 'Critical';
  if (score >= 50) return 'High';
  if (score >= 20) return 'Moderate';
  return 'Low';
}

/**
 * HeatMap — India state-level risk visualization.
 * Renders a proportionally-sized tile grid rather than invented geographic
 * coordinates, since the frontend has no verified per-project GPS data.
 *
 * Props:
 *  - data: [{ state, score, projectCount }]
 */
export default function HeatMap({ data = [] }) {
  const [sortMode, setSortMode] = useState('score');

  const sorted = useMemo(() => {
    const copy = [...data];
    if (sortMode === 'score') copy.sort((a, b) => b.score - a.score);
    else copy.sort((a, b) => a.state.localeCompare(b.state));
    return copy;
  }, [data, sortMode]);

  return (
    <div className="heatmap">
      <div className="heatmap__header">
        <div>
          <h3 className="panel-title">Risk Heatmap (India)</h3>
          <p className="panel-subtitle">Average overall risk across the complete matching dataset</p>
        </div>
        <select
          className="heatmap__select"
          value={sortMode}
          onChange={(e) => setSortMode(e.target.value)}
          aria-label="Sort states"
        >
          <option value="score">By Risk Score</option>
          <option value="name">By State</option>
        </select>
      </div>

      <div className="heatmap__grid">
        {sorted.map((s) => (
          <div
            key={s.state}
            className="heatmap__tile"
            style={{ background: scoreToColor(s.score) }}
            title={`${s.state}: ${s.score} average risk across ${s.projectCount} project(s) (${riskLabel(s.score)})`}
          >
            <span className="heatmap__tile-name">{s.state}</span>
            <span className="heatmap__tile-score">{s.score}</span>
          </div>
        ))}
      </div>

      <div className="heatmap__legend">
        <span className="heatmap__legend-label">Risk Score</span>
        <div className="heatmap__legend-bar" />
        <div className="heatmap__legend-ends">
          <span>Low</span>
          <span>High</span>
        </div>
      </div>
    </div>
  );
}
