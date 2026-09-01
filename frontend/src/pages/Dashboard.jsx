import { useEffect, useMemo, useState } from 'react';
import StatCard from '../components/StatCard';
import HeatMap from '../components/HeatMap';
import AnomalyChart from '../components/AnomalyChart';
import RiskyProj from '../components/RiskyProj';
import Insights from '../components/Insights';
import InvestigationBrief from '../components/InvestigationBrief';
import { useInvestigation } from '../context/InvestigationContext';
import {
  buildAnomalyDistribution,
  buildInsights,
  buildStateRiskData,
  buildSummary,
  FALLBACK_FILTER_OPTIONS,
  getProjectAggregates,
  getProjectExportUrl,
  getProjectFilterOptions,
  getProjects,
} from '../services/api';
import { formatNumberIN, formatCompactINR } from '../utils/format';
import './Dashboard.css';

const PAGE_SIZE = 8;

export default function Dashboard() {
  const { filters, search, searchInput, setFilter, setSearchMeta, reset } = useInvestigation();
  const [loading, setLoading] = useState(true);
  const [aggregatesLoading, setAggregatesLoading] = useState(true);
  const [projectsLoading, setProjectsLoading] = useState(true);
  const [metadataError, setMetadataError] = useState(null);
  const [aggregatesError, setAggregatesError] = useState(null);
  const [projectsError, setProjectsError] = useState(null);
  const [projectPage, setProjectPage] = useState({ total: 0, page: 1, pageSize: PAGE_SIZE, totalPages: 0, projects: [] });
  const [aggregates, setAggregates] = useState(null);
  const [filterOptions, setFilterOptions] = useState(FALLBACK_FILTER_OPTIONS);
  const [pageState, setPageState] = useState({ page: 1, signature: '' });
  const [briefOpen, setBriefOpen] = useState(false);
  const querySignature = `${filters.risk}|${filters.state}|${filters.category}|${search}`;
  const page = pageState.signature === querySignature ? pageState.page : 1;
  const scope = useMemo(() => ({ ...filters, search }), [filters, search]);

  useEffect(() => {
    const controller = new AbortController();
    getProjectFilterOptions(controller.signal)
      .then(setFilterOptions)
      .catch((loadError) => {
        if (loadError.name !== 'AbortError') setMetadataError(loadError.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setLoading(false);
      });
    return () => controller.abort();
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    // oxlint-disable-next-line react/set-state-in-effect -- marks the request lifecycle.
    setAggregatesLoading(true);
    getProjectAggregates(scope, controller.signal)
      .then((response) => {
        setAggregates(response);
        setAggregatesError(null);
      })
      .catch((loadError) => {
        if (loadError.name !== 'AbortError') setAggregatesError(loadError.message);
      })
      .finally(() => {
        if (!controller.signal.aborted) setAggregatesLoading(false);
      });
    return () => controller.abort();
  }, [scope]);

  useEffect(() => {
    const controller = new AbortController();
    // oxlint-disable-next-line react/set-state-in-effect -- marks the request lifecycle.
    setProjectsLoading(true);
    if (search) setSearchMeta({ loading: true, count: null, results: [] });
    getProjects({ ...scope, page, pageSize: PAGE_SIZE }, controller.signal)
      .then((response) => {
        setProjectPage(response);
        setProjectsError(null);
        setSearchMeta({ loading: false, count: search ? response.total : null, results: search ? response.projects.slice(0, 5) : [] });
      })
      .catch((loadError) => {
        if (loadError.name !== 'AbortError') {
          setProjectsError(loadError.message);
          setSearchMeta({ loading: false, count: 0, results: [] });
        }
      })
      .finally(() => {
        if (!controller.signal.aborted) setProjectsLoading(false);
      });
    return () => controller.abort();
  }, [page, scope, search, setSearchMeta]);

  const stateRiskData = useMemo(() => (aggregates ? buildStateRiskData(aggregates) : []), [aggregates]);
  const anomalyData = useMemo(() => (aggregates ? buildAnomalyDistribution(aggregates) : []), [aggregates]);
  const insights = useMemo(() => (aggregates ? buildInsights(aggregates) : []), [aggregates]);
  const summary = useMemo(() => (aggregates ? buildSummary(aggregates) : null), [aggregates]);
  const hasActiveFilters = filters.risk !== 'All' || filters.state !== 'All' || filters.category !== 'All' || searchInput !== '';

  function updateFilter(key, value) {
    setFilter(key, value);
    setPageState({ page: 1, signature: '' });
  }

  function resetFilters() {
    reset();
    setPageState({ page: 1, signature: '' });
  }

  if (loading || aggregatesLoading || (projectsLoading && projectPage.projects.length === 0)) return <div className="dashboard__loading">Loading dashboard…</div>;
  if (metadataError || aggregatesError || projectsError) return <div className="dashboard__loading">Unable to load dashboard: {metadataError || aggregatesError || projectsError}</div>;
  if (!summary) return <div className="dashboard__loading">Dashboard data is unavailable.</div>;

  return (
    <div className="dashboard">
      <div className="dashboard__page-header">
        <div><h1 className="dashboard__title">Overview</h1><p className="dashboard__subtitle">Intelligence from processed MPLADS projects and explainable anomaly risk signals.</p></div>
        <div className="dashboard__page-controls">
          <button type="button" className="dashboard__control-btn"><IconCalendar />All available records</button>
          <button type="button" className="dashboard__control-btn"><IconFilter />Filters</button>
        </div>
      </div>

      <div className="dashboard__stats">
        <StatCard title="Total Works Analysed" value={formatNumberIN(summary.totalWorksAnalysed)} icon={<IconGrid />} />
        <StatCard title="Sanctioned Amount" value={formatCompactINR(summary.totalSanctioned)} icon={<IconGrid />} />
        <StatCard title="Total Expenditure" value={formatCompactINR(summary.totalExpenditure)} icon={<IconGrid />} />
        <StatCard title="High/Critical Risk Works" value={formatNumberIN(summary.priorityRiskWorks)} icon={<IconAlert />} accent="high" />
        <StatCard title="Requires Review" value={formatNumberIN(summary.underReview)} icon={<IconEyeSolid />} accent="info" />
      </div>

      <div className="dashboard__geo-row">
        <div className="dashboard__geo-map"><HeatMap data={stateRiskData} /></div>
        <div className="dashboard__geo-chart"><AnomalyChart data={anomalyData} centerLabel={formatNumberIN(aggregates.totalProjects)} centerSublabel="Matching" /></div>
      </div>

      <div className="dashboard__work-row">
        <div className="dashboard__work-main">
          <div className="dashboard__filters">
            <FilterSelect label="Risk" value={filters.risk} onChange={(value) => updateFilter('risk', value)} options={filterOptions.riskLevels} />
            <FilterSelect label="State" value={filters.state} onChange={(value) => updateFilter('state', value)} options={filterOptions.states} />
            <FilterSelect label="Category" value={filters.category} onChange={(value) => updateFilter('category', value)} options={filterOptions.categories} />
            {search && <span className="dashboard__search-scope">Search: “{search}” · {formatNumberIN(projectPage.total)} results</span>}
            {hasActiveFilters && <button type="button" className="dashboard__reset" onClick={resetFilters}>Reset</button>}
          </div>
          <RiskyProj
            projects={projectPage.projects}
            total={projectPage.total}
            page={projectPage.page}
            pageSize={projectPage.pageSize}
            totalPages={projectPage.totalPages}
            loading={projectsLoading}
            onPageChange={(nextPage) => setPageState({ page: nextPage, signature: querySignature })}
            onExport={() => { window.location.href = getProjectExportUrl(scope); }}
          />
        </div>
        <div className="dashboard__work-side"><Insights insights={insights} /></div>
      </div>

      <div className="dashboard__summary-bar">
        <div className="dashboard__summary-item"><span className="dashboard__summary-label">Risk Review Scope</span><span className="dashboard__summary-caption">Derived from processed detector output</span></div>
        <SummaryMetric value={`${summary.criticalSharePct}%`} label="Critical Risk" className="dashboard__summary-value--high" />
        <SummaryMetric value={`${summary.alertCoveragePct}%`} label="Projects Requiring Review" />
        <SummaryMetric value={formatNumberIN(summary.moderateRisk)} label="Moderate Risk" className="dashboard__summary-value--low" />
        <button type="button" className="dashboard__summary-cta" onClick={() => setBriefOpen(true)}>Generate Brief</button>
      </div>
      {briefOpen && <InvestigationBrief aggregates={aggregates} scope={scope} onClose={() => setBriefOpen(false)} />}
    </div>
  );
}

function FilterSelect({ label, value, onChange, options }) {
  return (
    <label className="dashboard__filter-select">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="All">All</option>
        {options.map((option) => <option key={option} value={option}>{option.length > 22 ? `${option.slice(0, 22)}…` : option}</option>)}
      </select>
    </label>
  );
}

function SummaryMetric({ value, label, className = '' }) {
  return <div className="dashboard__summary-item dashboard__summary-item--metric"><span className={`dashboard__summary-value ${className}`}>{value}</span><span className="dashboard__summary-caption">{label}</span></div>;
}

function IconCalendar() {
  return <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true"><rect x="2.3" y="3.2" width="11.4" height="10.6" rx="1.3" stroke="currentColor" strokeWidth="1.2" /><path d="M2.3 6.4h11.4M5.3 2v2.4M10.7 2v2.4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" /></svg>;
}
function IconFilter() {
  return <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 3.2h12L9.3 8.4v4.1L6.7 14V8.4L2 3.2Z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" /></svg>;
}
function IconGrid() {
  return <svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M2 12.5 5.5 8 8.5 10.5 14 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" /></svg>;
}
function IconAlert() {
  return <svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M8 2 1.5 13.5h13L8 2Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" /><path d="M8 6.4v3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" /><circle cx="8" cy="11.2" r="0.8" fill="currentColor" /></svg>;
}
function IconEyeSolid() {
  return <svg viewBox="0 0 16 16" fill="none" aria-hidden="true"><path d="M1.5 8S4 3.5 8 3.5 14.5 8 14.5 8 12 12.5 8 12.5 1.5 8 1.5 8Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" /><circle cx="8" cy="8" r="1.9" stroke="currentColor" strokeWidth="1.4" /></svg>;
}
