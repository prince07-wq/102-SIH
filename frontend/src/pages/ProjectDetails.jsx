import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import RiskBadge from '../components/RiskBadge';
import ProjectReportDialog from '../components/ProjectReportDialog';
import { getProjectById } from '../services/api';
import { useSavedProjects } from '../hooks/useSavedProjects';
import { formatINR } from '../utils/format';
import './ProjectDetails.css';

const RISK_DIMENSIONS = [
  { key: 'cost', label: 'Cost Risk' },
  { key: 'delay', label: 'Delay Risk' },
  { key: 'expenditure', label: 'Expenditure Risk' },
  { key: 'duplicate', label: 'Duplicate Risk' },
];

const FLAG_META = {
  cost: { icon: '\u26A0', label: 'Cost anomaly' },
  delay: { icon: '\u25F7', label: 'Delay anomaly' },
  expenditure: { icon: '\u20B9', label: 'Expenditure anomaly' },
  duplicate: { icon: '\u29C9', label: 'Duplicate/similarity anomaly' },
};

export default function ProjectDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toggleSaved, isSaved } = useSavedProjects();
  const [project, setProject] = useState(undefined); // undefined = loading, null = not found
  const [error, setError] = useState(null);
  const [reportOpen, setReportOpen] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    getProjectById(id, controller.signal)
      .then((response) => {
        setError(null);
        setProject(response);
      })
      .catch((loadError) => {
        if (loadError.name !== 'AbortError') {
          setError(loadError.message);
          setProject(null);
        }
      });
    return () => controller.abort();
  }, [id]);

  if (project === undefined || (project && project.projectId !== id)) {
    return <div className="pd__loading">Loading project record…</div>;
  }

  if (project === null && error) {
    return (
      <div className="pd__not-found">
        <h2>Unable to load project</h2>
        <p>{error}</p>
        <button type="button" onClick={() => navigate('/')}>
          Back to Dashboard
        </button>
      </div>
    );
  }

  if (project === null) {
    return (
      <div className="pd__not-found">
        <h2>Project not found</h2>
        <p>We couldn&rsquo;t locate a record for &ldquo;{id}&rdquo;.</p>
        <button type="button" onClick={() => navigate('/')}>
          Back to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div className="pd">
      <Link to="/" className="pd__back">
        <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
          <path d="M10 3.5 5.5 8l4.5 4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
        Back to Dashboard
      </Link>

      <h1 className="pd__page-title">Project Details</h1>

      {/* Header card */}
      <div className="pd__header-card">
        <div className="pd__header-main">
          <h2 className="pd__work-name">{project.workName}</h2>
          <div className="pd__header-meta">
            <span>
              <IconPin /> {project.state}
            </span>
            <span className="pd__meta-dot">&middot;</span>
            <span>{project.constituency}</span>
            <span className="pd__meta-dot">&middot;</span>
            <span className="mono pd__meta-id">{project.projectId}</span>
          </div>
        </div>
        <div className="pd__header-actions">
          <button type="button" className="pd__report" onClick={() => setReportOpen(true)}>
            Generate Project Report
          </button>
          <button type="button" className="pd__save" onClick={() => toggleSaved(project)}>
            {isSaved(project.projectId) ? 'Saved for Review' : 'Save for Review'}
          </button>
          <RiskBadge level={project.risk.level} score={project.risk.overallScore} />
        </div>
      </div>

      {/* Project information */}
      <div className="pd__section">
        <h3 className="panel-title">Project Information</h3>
        <div className="pd__info-grid">
          <InfoField label="State" value={project.state} />
          <InfoField label="Activity" value={project.activityName} />
          <InfoField label="Sanction Amount" value={formatINR(project.sanctionAmount)} mono />
          <InfoField label="Constituency" value={project.constituency} />
          <InfoField label="Recommendation Date" value={project.recommendationDate} />
          <InfoField label="Sanction Date" value={project.sanctionDate} />
          <InfoField label="MP" value={project.mpName} />
          <InfoField label="Work Stage" value={project.workStage} />
          <InfoField label="Authority" value={project.authority} />
          <InfoField label="Category" value={project.category} />
          <InfoField label="Tenure" value={project.tenure} />
          <InfoField label="House of Parliament" value={project.houseOfParliament} />
          <InfoField label="Description" value={project.description} />
        </div>
      </div>

      {/* Expenditure information */}
      <div className="pd__section">
        <h3 className="panel-title">Expenditure Information</h3>
        <div className="pd__info-grid">
          <InfoField label="Has Expenditure" value={project.hasExpenditure ? 'Yes' : 'No'} />
          <InfoField label="Disbursed Amount" value={formatINR(project.totalDisbursed)} mono />
          <InfoField label="Payment Records" value={project.expenditureRecordCount} mono />
          <InfoField label="Unique Vendors" value={project.uniqueVendorCount} mono />
          <InfoField label="First Expenditure Date" value={project.firstExpenditureDate} />
          <InfoField label="Last Expenditure Date" value={project.lastExpenditureDate} />
          <InfoField
            label="Vendors and IDs"
            value={project.vendors
              .map((vendor) =>
                [vendor.vendorName, vendor.vendorId ? `ID ${vendor.vendorId}` : null]
                  .filter(Boolean)
                  .join(' · '),
              )
              .filter(Boolean)
              .join(', ')}
          />
          <InfoField label="Work IDs" value={project.workIds.join(', ')} mono />
        </div>
      </div>

      {/* Overall risk + breakdown */}
      <div className="pd__risk-row">
        <div className="pd__section pd__risk-gauge-card">
          <h3 className="panel-title">Overall Risk</h3>
          <RiskGauge score={project.risk.overallScore} level={project.risk.level} />
          <div className="pd__risk-evidence">
            <span>
              Strongest detector: <strong>{detectorLabel(project.risk.strongestDetector)}</strong>{' '}
              ({formatScore(project.risk.baseScore)} /100)
            </span>
            <span>
              Flag count: <strong>{project.risk.flagCount} of 4</strong>
            </span>
            <span>
              Multi-signal bonus: <strong>+{project.risk.multiSignalBonus}</strong>
              {project.risk.multiSignalBonus === 0 ? ' (fewer than two components flagged)' : ''}
            </span>
            <span>
              Combined score: min(100, {formatScore(project.risk.baseScore)} +{' '}
              {project.risk.multiSignalBonus})
              {project.risk.scoreCapped ? ' · capped at 100' : ''}
            </span>
          </div>
        </div>

        <div className="pd__section pd__risk-breakdown-card">
          <h3 className="panel-title">Risk Breakdown</h3>
          <div className="pd__breakdown-list">
            {RISK_DIMENSIONS.map((d) => {
              const dim = project.risk[d.key];
              return (
                <div className="pd__breakdown-row" key={d.key}>
                  <span className="pd__breakdown-label">{d.label}</span>
                  <div className="pd__breakdown-bar-track">
                    <div
                      className={`pd__breakdown-bar-fill pd__breakdown-bar-fill--${scoreTier(dim.score)}`}
                      style={{ width: `${dim.score}%` }}
                    />
                  </div>
                  <span className="pd__breakdown-score mono">{formatScore(dim.score)} /100</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Explainable component output */}
      <div className="pd__section pd__why-flagged">
        <h3 className="pd__why-title">Risk Component Explanations</h3>

        <ul className="pd__why-list">
          {RISK_DIMENSIONS.map((dimension) => {
            const component = project.risk[dimension.key];
            return (
              <li key={dimension.key} className={`pd__why-item pd__why-item--${dimension.key}`}>
                <span className="pd__why-icon">{FLAG_META[dimension.key].icon}</span>
                <div>
                  <span className="pd__why-label">
                    {FLAG_META[dimension.key].label} · {formatScore(component.score)} /100 ·{' '}
                    {component.flagged ? 'Risk signal' : 'Not flagged'}
                  </span>
                  <p className="pd__why-text">{component.reason}</p>
                </div>
              </li>
            );
          })}
        </ul>

        <p className="pd__why-disclaimer">
          These indicators denote a potential irregularity that requires review &mdash; they are not a finding of
          fraud or wrongdoing.
        </p>
      </div>

      {/* Similar-project evidence */}
      <div className="pd__section">
        <h3 className="panel-title">Similar Projects</h3>
        {project.similarProjects.length === 0 ? (
          <p className="pd__why-empty">No similar-project candidates were retained for this work.</p>
        ) : (
          <div className="pd__similar-list">
            {project.similarProjects.map((similar) => (
              <Link key={similar.projectId} to={`/projects/${similar.projectId}`} className="pd__similar-item">
                <div>
                  <span className="pd__similar-name">{similar.workName}</span>
                  <span className="mono pd__similar-id">{similar.projectId}</span>
                </div>
                <div className="pd__similar-meta">
                  <span>{formatINR(similar.sanctionAmount)}</span>
                  <span>{similar.sanctionDate || '—'}</span>
                  <span>
                    {similar.dateDifferenceDays === null
                      ? 'Date difference unavailable'
                      : `${similar.dateDifferenceDays} day difference`}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
      {reportOpen && <ProjectReportDialog project={project} onClose={() => setReportOpen(false)} />}
    </div>
  );
}

function InfoField({ label, value, mono }) {
  return (
    <div className="pd__info-field">
      <span className="pd__info-label">{label}</span>
      <span className={`pd__info-value ${mono ? 'mono' : ''}`}>
        {value === null || value === undefined || value === '' ? '—' : value}
      </span>
    </div>
  );
}

function scoreTier(score) {
  if (score >= 50) return 'high';
  if (score >= 20) return 'medium';
  return 'low';
}

function formatScore(score) {
  return Number(score).toFixed(2).replace(/\.00$/, '').replace(/(\.\d)0$/, '$1');
}

function detectorLabel(detector) {
  const labels = {
    cost: 'Cost',
    delay: 'Delay',
    expenditure: 'Expenditure',
    duplicate: 'Duplicate/similarity',
  };
  return labels[detector] || detector;
}

function RiskGauge({ score, level }) {
  // Semicircle gauge, 180deg sweep, drawn with a stroked arc path.
  const size = 168;
  const stroke = 14;
  const r = (size - stroke) / 2;
  const cy = size / 2;
  const circumference = Math.PI * r;
  const pct = Math.max(0, Math.min(100, score)) / 100;
  const dashOffset = circumference * (1 - pct);
  const color =
    level === 'CRITICAL' || level === 'HIGH'
      ? 'var(--risk-high)'
      : level === 'MODERATE' || level === 'MEDIUM'
        ? 'var(--risk-medium)'
        : 'var(--risk-low)';

  return (
    <div className="pd__gauge">
      <svg width={size} height={size / 2 + 10} viewBox={`0 0 ${size} ${size / 2 + 10}`}>
        <path
          d={`M ${stroke / 2} ${cy} A ${r} ${r} 0 0 1 ${size - stroke / 2} ${cy}`}
          fill="none"
          stroke="var(--border-subtle)"
          strokeWidth={stroke}
          strokeLinecap="round"
        />
        <path
          d={`M ${stroke / 2} ${cy} A ${r} ${r} 0 0 1 ${size - stroke / 2} ${cy}`}
          fill="none"
          stroke={color}
          strokeWidth={stroke}
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={dashOffset}
        />
      </svg>
      <div className="pd__gauge-value">
        <span className="pd__gauge-score">{formatScore(score)}</span>
        <span className={`pd__gauge-label pd__gauge-label--${scoreTier(score)}`}>{level.charAt(0)}{level.slice(1).toLowerCase()} Risk</span>
      </div>
    </div>
  );
}

function IconPin() {
  return (
    <svg width="11" height="11" viewBox="0 0 14 14" fill="none" style={{ marginRight: 2, verticalAlign: -1 }} aria-hidden="true">
      <path d="M7 12.8s4.2-4 4.2-7.3a4.2 4.2 0 1 0-8.4 0c0 3.3 4.2 7.3 4.2 7.3Z" stroke="currentColor" strokeWidth="1.2" strokeLinejoin="round" />
      <circle cx="7" cy="5.5" r="1.5" stroke="currentColor" strokeWidth="1.2" />
    </svg>
  );
}
