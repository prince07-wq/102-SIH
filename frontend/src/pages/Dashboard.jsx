import { useEffect, useMemo, useState } from 'react';
import StatCard from '../components/StatCard';
import HeatMap from '../components/HeatMap';
import AnomalyChart from '../components/AnomalyChart';
import RiskyProj from '../components/RiskyProj';
import Insights from '../components/Insights';
import { getProjects, getStateRiskData, getAnomalyDistribution, getInsights, getSummary, FILTER_OPTIONS } from '../services/api';
import { formatNumberIN, formatCompactINR } from '../utils/format';
import './Dashboard.css';

const EMPTY_FILTERS = { risk: 'All', state: 'All', category: 'All', search: '' };

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState([]);
  const [stateRiskData, setStateRiskData] = useState([]);
  const [anomalyData, setAnomalyData] = useState([]);
  const [insights, setInsights] = useState([]);
  const [summary, setSummary] = useState(null);
  const [filters, setFilters] = useState(EMPTY_FILTERS);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      const [projectsRes, stateRes, anomalyRes, insightsRes, summaryRes] = await Promise.all([
        getProjects(),
        getStateRiskData(),
        getAnomalyDistribution(),
        getInsights(),
        getSummary(),
      ]);
      if (cancelled) return;
      setProjects(projectsRes);
      setStateRiskData(stateRes);
      setAnomalyData(anomalyRes);
      setInsights(insightsRes);
      setSummary(summaryRes);
      setLoading(false);
    }

    load();
    return () => {
      cancelled = true;
    };
  }, []);

  const filteredProjects = useMemo(() => {
    const q = filters.search.trim().toLowerCase();
    return projects.filter((p) => {
      if (filters.risk !== 'All' && p.risk.level !== filters.risk) return false;
      if (filters.state !== 'All' && p.state !== filters.state) return false;
      if (filters.category !== 'All' && p.category !== filters.category) return false;
      if (q) {
        const haystack = [p.projectId, p.workName, p.state, p.constituency, p.mpName, p.vendorName]
          .join(' ')
          .toLowerCase();
        if (!haystack.includes(q)) return false;
      }
      return true;
    });
  }, [projects, filters]);

  const hasActiveFilters =
    filters.risk !== 'All' || filters.state !== 'All' || filters.category !== 'All' || filters.search !== '';

  function updateFilter(key, value) {
    setFilters((f) => ({ ...f, [key]: value }));
  }

  if (loading || !summary) {
    return <div className="dashboard__loading">Loading dashboard…</div>;
  }

  return (
    <div className="dashboard">
      {/* Page header */}
      <div className="dashboard__page-header">
        <div>
          <h1 className="dashboard__title">Overview</h1>
          <p className="dashboard__subtitle">
            AI-powered intelligence to detect anomalies and prioritize MPLADS works for investigation.
          </p>
        </div>
        <div className="dashboard__page-controls">
          <button type="button" className="dashboard__control-btn">
            <IconCalendar />
            01 Apr 2021 &ndash; 31 Mar 2024
          </button>
          <button type="button" className="dashboard__control-btn">
            <IconFilter />
            Filters
          </button>
        </div>
      </div>

      {/* KPI cards */}
      <div className="dashboard__stats">
        <StatCard
          title="Total Works Analysed"
          value={formatNumberIN(summary.totalWorksAnalysed)}
          trend={summary.totalWorksTrend}
          icon={<IconGrid />}
          sparkline={[4, 5, 4.5, 6, 5.5, 7, 6.5, 8]}
        />
        <StatCard
          title="Sanctioned Amount"
          value={formatCompactINR(summary.totalSanctioned)}
          trend={summary.totalSanctionedTrend}
          icon={<IconGrid />}
          sparkline={[3, 3.4, 3.2, 4, 4.4, 4.2, 5, 5.4]}
        />
        <StatCard
          title="Total Expenditure"
          value={formatCompactINR(summary.totalExpenditure)}
          trend={summary.totalExpenditureTrend}
          icon={<IconGrid />}
          sparkline={[2.6, 3, 3.3, 3.1, 3.8, 4, 4.3, 4.8]}
        />
        <StatCard
          title="High Risk Works"
          value={formatNumberIN(summary.highRiskWorksNational)}
          trend={summary.highRiskWorksTrend}
          icon={<IconAlert />}
          accent="high"
          sparkline={[5, 5.4, 6, 5.8, 6.6, 7, 7.6, 8.2]}
        />
        <StatCard
          title="Under Investigation"
          value={formatNumberIN(summary.underInvestigation)}
          trend={summary.underInvestigationTrend}
          icon={<IconEyeSolid />}
          accent="info"
          sparkline={[3.4, 3.6, 3.5, 3.9, 4, 4.3, 4.5, 4.8]}
        />
      </div>

      {/* Heatmap + anomaly chart */}
      <div className="dashboard__geo-row">
        <div className="dashboard__geo-map">
          <HeatMap data={stateRiskData} />
        </div>
        <div className="dashboard__geo-chart">
          <AnomalyChart data={anomalyData} centerLabel={formatNumberIN(projects.length)} centerSublabel="In Sample" />
        </div>
      </div>

      {/* Filters + table + insights */}
      <div className="dashboard__work-row">
        <div className="dashboard__work-main">
          <div className="dashboard__filters">
            <FilterSelect
              label="Risk"
              value={filters.risk}
              onChange={(v) => updateFilter('risk', v)}
              options={FILTER_OPTIONS.riskLevels}
            />
            <FilterSelect
              label="State"
              value={filters.state}
              onChange={(v) => updateFilter('state', v)}
              options={FILTER_OPTIONS.states}
            />
            <FilterSelect
              label="Category"
              value={filters.category}
              onChange={(v) => updateFilter('category', v)}
              options={FILTER_OPTIONS.categories}
            />
            <div className="dashboard__filter-search">
              <IconSearchSm />
              <input
                type="text"
                placeholder="Search projects…"
                value={filters.search}
                onChange={(e) => updateFilter('search', e.target.value)}
                aria-label="Search projects"
              />
            </div>
            {hasActiveFilters && (
              <button type="button" className="dashboard__reset" onClick={() => setFilters(EMPTY_FILTERS)}>
                Reset
              </button>
            )}
          </div>

          <RiskyProj projects={filteredProjects} />
        </div>

        <div className="dashboard__work-side">
          <Insights insights={insights} />
        </div>
      </div>

      {/* Bottom summary bar */}
      <div className="dashboard__summary-bar">
        <div className="dashboard__summary-item">
          <span className="dashboard__summary-label">Active Investigation Scope</span>
          <span className="dashboard__summary-caption">Stats for current session cycle</span>
        </div>
        <div className="dashboard__summary-item dashboard__summary-item--metric">
          <span className="dashboard__summary-value dashboard__summary-value--high">{summary.activeInvestigationScope}%</span>
          <span className="dashboard__summary-caption">Critical Priority</span>
        </div>
        <div className="dashboard__summary-item dashboard__summary-item--metric">
          <span className="dashboard__summary-value">{summary.auditCoveragePct}%</span>
          <span className="dashboard__summary-caption">Audit Coverage</span>
        </div>
        <div className="dashboard__summary-item dashboard__summary-item--metric">
          <span className="dashboard__summary-value dashboard__summary-value--low">{summary.recoveredFunds}</span>
          <span className="dashboard__summary-caption">Recovered Funds</span>
        </div>
        <button type="button" className="dashboard__summary-cta">
          Generate Brief
        </button>
      </div>
    </div>
  );
}

function FilterSelect({ label, value, onChange, options }) {
  return (
    <label className="dashboard__filter-select">
      <span>{label}</span>
      <select value={value} onChange={(e) => onChange(e.target.value)}>
        <option value="All">All</option>
        {options.map((opt) => (
          <option key={opt} value={opt}>
            {opt.length > 22 ? `${opt.slice(0, 22)}\u2026` : opt}
          </option>
        ))}
      </select>
    </label>
  );
}

function IconCalendar() {
  return (
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <rect x="2.3" y="3.2" width="11.4" height="10.6" rx="1.3" stroke="currentColor" strokeWidth="1.2" />
      <path d="M2.3 6.4h11.4M5.3 2v2.4M10.7 2v2.4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}
function IconFilter() {
  return (
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M2 3.2h12L9.3 8.4v4.1L6.7 14V8.4L2 3.2Z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" />
    </svg>
  );
}
function IconGrid() {
  return (
    <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M2 12.5 5.5 8 8.5 10.5 14 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function IconAlert() {
  return (
    <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M8 2 1.5 13.5h13L8 2Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <path d="M8 6.4v3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <circle cx="8" cy="11.2" r="0.8" fill="currentColor" />
    </svg>
  );
}
function IconEyeSolid() {
  return (
    <svg viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <path d="M1.5 8S4 3.5 8 3.5 14.5 8 14.5 8 12 12.5 8 12.5 1.5 8 1.5 8Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <circle cx="8" cy="8" r="1.9" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  );
}
function IconSearchSm() {
  return (
    <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <circle cx="7.2" cy="7.2" r="4.1" stroke="currentColor" strokeWidth="1.3" />
      <path d="M13.3 13.3 10.6 10.6" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  );
}
