import { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import RiskBadge from '../components/RiskBadge';
import { getProjectById } from '../services/api';
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
  const [project, setProject] = useState(undefined); // undefined = loading, null = not found

  useEffect(() => {
    let cancelled = false;
    setProject(undefined);
    getProjectById(id).then((res) => {
      if (!cancelled) setProject(res);
    });
    return () => {
      cancelled = true;
    };
  }, [id]);

  if (project === undefined) {
    return <div className="pd__loading">Loading project record…</div>;
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

  const flaggedReasons = RISK_DIMENSIONS.filter((d) => project.risk[d.key].flagged);

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
        <RiskBadge level={project.risk.level} score={project.risk.overallScore} />
      </div>

      {/* Project information */}
      <div className="pd__section">
        <h3 className="panel-title">Project Information</h3>
        <div className="pd__info-grid">
          <InfoField label="State" value={project.state} />
          <InfoField label="Sanction Amount" value={formatINR(project.sanctionAmount)} mono />
          <InfoField label="Constituency" value={project.constituency} />
          <InfoField label="Sanction Date" value={project.sanctionDate} />
          <InfoField label="MP" value={project.mpName} />
          <InfoField label="Work Stage" value={project.workStage} />
          <InfoField label="Authority" value={project.authority} />
          <InfoField label="Vendor" value={project.vendorName} />
          <InfoField label="Category" value={project.category} />
          <InfoField label="Disbursed Amount" value={formatINR(project.totalDisbursed)} mono />
        </div>
      </div>

      {/* Overall risk + breakdown */}
      <div className="pd__risk-row">
        <div className="pd__section pd__risk-gauge-card">
          <h3 className="panel-title">Overall Risk</h3>
          <RiskGauge score={project.risk.overallScore} level={project.risk.level} />
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
                  <span className="pd__breakdown-score mono">{dim.score} /100</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Why flagged */}
      <div className="pd__section pd__why-flagged">
        <h3 className="pd__why-title">Why Flagged?</h3>

        {flaggedReasons.length === 0 ? (
          <p className="pd__why-empty">No anomaly detectors were triggered for this work.</p>
        ) : (
          <ul className="pd__why-list">
            {flaggedReasons.map((d) => (
              <li key={d.key} className={`pd__why-item pd__why-item--${d.key}`}>
                <span className="pd__why-icon">{FLAG_META[d.key].icon}</span>
                <div>
                  <span className="pd__why-label">{FLAG_META[d.key].label}</span>
                  <p className="pd__why-text">{project.risk[d.key].reason}</p>
                </div>
              </li>
            ))}
          </ul>
        )}

        <p className="pd__why-disclaimer">
          These indicators denote a potential irregularity that requires review &mdash; they are not a finding of
          fraud or wrongdoing.
        </p>
      </div>
    </div>
  );
}

function InfoField({ label, value, mono }) {
  return (
    <div className="pd__info-field">
      <span className="pd__info-label">{label}</span>
      <span className={`pd__info-value ${mono ? 'mono' : ''}`}>{value}</span>
    </div>
  );
}

function scoreTier(score) {
  if (score >= 70) return 'high';
  if (score >= 40) return 'medium';
  return 'low';
}

function RiskGauge({ score, level }) {
  // Semicircle gauge, 180deg sweep, drawn with a stroked arc path.
  const size = 168;
  const stroke = 14;
  const r = (size - stroke) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const circumference = Math.PI * r;
  const pct = Math.max(0, Math.min(100, score)) / 100;
  const dashOffset = circumference * (1 - pct);
  const color = level === 'HIGH' ? 'var(--risk-high)' : level === 'MEDIUM' ? 'var(--risk-medium)' : 'var(--risk-low)';

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
        <span className="pd__gauge-score">{score}</span>
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
