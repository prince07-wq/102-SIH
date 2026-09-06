import { useMemo, useState } from 'react';
import IndiaMap from '@react-map/india';
import { formatNumberIN } from '../utils/format';
import { buildIndiaMapModel, scoreToColor, selectMapState, sortMapRecords } from './heatMapModel';
import { INDIA_MAP_LABELS } from './heatMapLabels';
import './HeatMap.css';

const IndiaMapComponent = IndiaMap.default ?? IndiaMap;

/** India choropleth using the dashboard's already-loaded aggregate data. */
export default function HeatMap({ data = [], onApplyState }) {
  const [sortMode, setSortMode] = useState('score');
  const [selectedId, setSelectedId] = useState(null);
  const [tooltip, setTooltip] = useState(null);
  const model = useMemo(() => buildIndiaMapModel(
    data,
    import.meta.env.DEV ? (message) => console.warn(message) : null,
  ), [data]);
  const sorted = useMemo(() => sortMapRecords(model.records, sortMode), [model.records, sortMode]);
  const selected = model.byId[selectedId] ?? sorted[0] ?? null;
  const cityColors = useMemo(() => Object.fromEntries(model.features.flatMap((feature) =>
    feature.mapNames.map((mapName) => [mapName, scoreToColor(model.byId[feature.id]?.score)]),
  )), [model]);
  const selectedStyle = useMemo(() => selected
    ? model.features.find((feature) => feature.id === selected.id)?.mapNames
      .map((mapName) => `.heatmap__map path[id^="${mapName}-"] { stroke: #172f24 !important; stroke-width: 3 !important; }`).join('\n')
    : '', [model.features, selected]);

  function getRecordFromEvent(event) {
    const path = event.target.closest?.('path[id]');
    if (!path) return null;
    const mapName = Object.keys(model.byMapName).find((name) => path.id.startsWith(`${name}-`));
    return mapName ? model.byMapName[mapName] : null;
  }

  function handlePointerMove(event) {
    const record = getRecordFromEvent(event);
    if (!record) return setTooltip(null);
    const bounds = event.currentTarget.getBoundingClientRect();
    setTooltip({ record, x: event.clientX - bounds.left + 12, y: event.clientY - bounds.top + 12 });
  }

  function handleMapClick(event) {
    const record = getRecordFromEvent(event);
    if (record) selectMapState(record.id, model.byId, (next) => setSelectedId(next.id));
  }

  function handleLibrarySelect(mapName) {
    const record = model.byMapName[mapName];
    if (record) setSelectedId(record.id);
  }

  return (
    <div className="heatmap">
      <div className="heatmap__header">
        <div>
          <h3 className="panel-title">Risk Heatmap (India)</h3>
          <p className="panel-subtitle">Average overall risk across the complete matching dataset</p>
        </div>
        <select className="heatmap__select" value={sortMode} onChange={(event) => setSortMode(event.target.value)} aria-label="Sort states">
          <option value="score">By Risk Score</option><option value="name">By State</option>
        </select>
      </div>

      <div className="heatmap__content">
        <div className="heatmap__map-column">
          <div className="heatmap__map" aria-label="India state and union territory risk map"
            onPointerMove={handlePointerMove} onPointerLeave={() => setTooltip(null)} onClick={handleMapClick}>
            <style>{selectedStyle}</style>
            <div className="heatmap__svg">
              <IndiaMapComponent type="select-single" size={500} mapColor="rgb(226, 231, 227)" cityColors={cityColors}
                strokeColor="rgba(255, 255, 255, 0.95)" strokeWidth={1.15} hoverColor={undefined}
                selectColor={scoreToColor(selected?.score)} hints={false} onSelect={handleLibrarySelect} />
            </div>
            <svg className="heatmap__labels" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
              <g className="heatmap__label-lines">
                {INDIA_MAP_LABELS.filter((label) => label.callout).flatMap((label) => label.targets.map(([targetX, targetY], index) => (
                  <line key={`${label.id}-${index}`} x1={targetX} y1={targetY} x2={label.x} y2={label.y} />
                )))}
              </g>
              <g className="heatmap__label-text">
                {INDIA_MAP_LABELS.map((label) => (
                  <text key={label.id} x={label.x} y={label.y} textAnchor={label.anchor ?? 'middle'}
                    className={label.callout ? 'is-callout' : 'is-internal'}>
                    {label.lines.map((line, index) => (
                      <tspan key={line} x={label.x} dy={index === 0 ? -((label.lines.length - 1) * 1.05) : 2.1}>{line}</tspan>
                    ))}
                  </text>
                ))}
              </g>
            </svg>
            {tooltip && <div className="heatmap__tooltip" role="status" style={{ left: tooltip.x, top: tooltip.y }}>
              <strong>{tooltip.record.state}</strong>
              {tooltip.record.score !== null && <span>Avg. Risk Score: {tooltip.record.score}</span>}
              {tooltip.record.projectCount !== null && <span>Projects: {formatNumberIN(tooltip.record.projectCount)}</span>}
            </div>}
          </div>
          <div className="heatmap__legend" aria-label="Risk score scale from 0 low risk to 100 high risk">
            <span className="heatmap__legend-label">Risk Score</span><div className="heatmap__legend-bar" />
            <div className="heatmap__legend-ends"><span>0 · Low Risk</span><span>100 · High Risk</span></div>
          </div>
        </div>

        <aside className="heatmap__details" aria-live="polite">
          <span className="heatmap__details-eyebrow">Selected State / UT</span>
          {selected ? <>
            <h4>{selected.state}</h4>
            <dl>
              <div><dt>Average Risk Score</dt><dd>{selected.score ?? 'Not available'}</dd></div>
              <div><dt>Total Projects</dt><dd>{selected.projectCount === null ? 'Not available' : formatNumberIN(selected.projectCount)}</dd></div>
            </dl>
            {onApplyState && <button type="button" className="heatmap__cta" onClick={() => onApplyState(selected.backendState)}>
              View projects in {selected.state} <span aria-hidden="true">→</span>
            </button>}
          </> : <p className="heatmap__empty">No state-level risk data is available for this selection.</p>}
          {sorted.length > 0 && <div className="heatmap__ranking" aria-label="State risk ranking">
            {sorted.map((record) => <button type="button" key={record.id} className={record.id === selected?.id ? 'is-selected' : ''}
              onClick={() => setSelectedId(record.id)}><span>{record.state}</span><strong>{record.score ?? '—'}</strong></button>)}
          </div>}
        </aside>
      </div>
    </div>
  );
}
