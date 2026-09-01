import { useEffect, useMemo, useState } from 'react';
import SavedProjectList from '../components/SavedProjectList';
import { getProjectAggregates, getProjectExportUrl } from '../services/api';
import { useInvestigation } from '../context/InvestigationContext';
import {
  buildAnomalyCsv,
  buildInvestigationBrief,
  buildRiskSummaryCsv,
  buildStateRiskCsv,
  downloadText,
  printBrief,
} from '../utils/reports';
import './UtilityPages.css';

export default function Reports() {
  const { filters, search } = useInvestigation();
  const [aggregates, setAggregates] = useState(null);
  const [error, setError] = useState(null);
  const scope = useMemo(() => ({ ...filters, search }), [filters, search]);

  useEffect(() => {
    const controller = new AbortController();
    getProjectAggregates(scope, controller.signal)
      .then((response) => {
        setAggregates(response);
        setError(null);
      })
      .catch((loadError) => {
        if (loadError.name !== 'AbortError') setError(loadError.message);
      });
    return () => controller.abort();
  }, [scope]);

  return (
    <div className="utility-page">
      <h1>Reports</h1>
      <p className="utility-page__lede">Project reports use one saved project. Scope reports use the current dashboard search and filters.</p>

      <section className="utility-page__section">
        <h2>Project Reports</h2>
        <p>Open or download a report for one saved/review project. Downloads use that project&rsquo;s complete API record.</p>
        <SavedProjectList />
      </section>

      <section className="utility-page__section">
        <h2>Scope Reports</h2>
        {error ? (
          <div className="utility-page__error">Unable to load scope reports: {error}</div>
        ) : !aggregates ? (
          <div className="utility-page__empty">Loading current scope reports…</div>
        ) : (
          <ScopeReports aggregates={aggregates} scope={scope} />
        )}
      </section>

      <p className="utility-page__note">No separate pre-generated report files are currently exposed by the backend.</p>
    </div>
  );
}

function ScopeReports({ aggregates, scope }) {
  const brief = buildInvestigationBrief(aggregates, scope);
  return (
    <>
      <p className="utility-page__scope-note">
        Current filtered/search scope: {aggregates.totalProjects} matching projects. These are aggregate reports, not individual project reports.
      </p>
      <div className="report-grid">
        <Report title="Scope Risk Summary" description="Risk-level and review counts for the current scope" onDownload={() => downloadText('scope-risk-summary.csv', buildRiskSummaryCsv(aggregates), 'text/csv;charset=utf-8')} />
        <Report title="Scope Anomaly Distribution" description="Detector-provided flagged counts for the current scope" onDownload={() => downloadText('scope-anomaly-distribution.csv', buildAnomalyCsv(aggregates), 'text/csv;charset=utf-8')} />
        <Report title="Scope State Risk Summary" description="Every matching state's count and average risk" onDownload={() => downloadText('scope-state-risk-summary.csv', buildStateRiskCsv(aggregates), 'text/csv;charset=utf-8')} />
        <Report title="Filtered Scope Project Export" description="All projects in the current scope as a server-streamed CSV" href={getProjectExportUrl(scope)} />
        <Report title="Scope Investigation Brief" description="Factual aggregate brief for the current scope—not an individual project report" onDownload={() => downloadText('mplads-scope-investigation-brief.txt', brief)} onPrint={() => printBrief(brief)} />
      </div>
    </>
  );
}

function Report({ title, description, onDownload, onPrint, href }) {
  return (
    <section className="report-card">
      <h2>{title}</h2>
      <p>{description}</p>
      <div>
        {href ? <a href={href}>Download CSV</a> : <button type="button" onClick={onDownload}>Download</button>}
        {onPrint && <button type="button" onClick={onPrint}>Print</button>}
      </div>
    </section>
  );
}
