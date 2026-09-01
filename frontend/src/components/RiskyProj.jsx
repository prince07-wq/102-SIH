import { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import RiskBadge from './RiskBadge';
import { useSavedProjects } from '../hooks/useSavedProjects';
import { formatINR } from '../utils/format';
import './RiskyProj.css';

const COLUMNS = [
  { key: 'workName', label: 'Project', sortable: false },
  { key: 'state', label: 'State', sortable: true },
  { key: 'category', label: 'Category', sortable: true },
  { key: 'sanctionAmount', label: 'Sanction Amount', sortable: true },
  { key: 'workStage', label: 'Work Stage', sortable: false },
  { key: 'riskScore', label: 'Risk Score', sortable: true },
  { key: 'riskLevel', label: 'Risk Level', sortable: false },
];

/**
 * RiskyProj — the "All Projects" table.
 * Receives one server-filtered page and owns only page-local sorting and
 * row navigation. Page changes are delegated to the dashboard.
 * Does not fetch data directly.
 *
 * Props:
 *  - projects: Project[]
 *  - onExport: () => void (optional)
 */
export default function RiskyProj({
  projects = [],
  total = 0,
  page = 1,
  pageSize = 8,
  totalPages = 0,
  loading = false,
  onPageChange,
  onExport,
}) {
  const navigate = useNavigate();
  const { toggleSaved, isSaved } = useSavedProjects();
  const [sortKey, setSortKey] = useState('riskScore');
  const [sortDir, setSortDir] = useState('desc');

  const sorted = useMemo(() => {
    const list = [...projects];
    list.sort((a, b) => {
      let av;
      let bv;
      switch (sortKey) {
        case 'riskScore':
          av = a.risk.overallScore;
          bv = b.risk.overallScore;
          break;
        case 'sanctionAmount':
          av = a.sanctionAmount;
          bv = b.sanctionAmount;
          break;
        case 'state':
          av = a.state;
          bv = b.state;
          break;
        case 'category':
          av = a.category;
          bv = b.category;
          break;
        default:
          av = a.risk.overallScore;
          bv = b.risk.overallScore;
      }
      if (typeof av === 'string') {
        return sortDir === 'asc' ? av.localeCompare(bv) : bv.localeCompare(av);
      }
      return sortDir === 'asc' ? av - bv : bv - av;
    });
    return list;
  }, [projects, sortKey, sortDir]);

  const currentPage = page;
  const pageStart = total ? (currentPage - 1) * pageSize : 0;

  function toggleSort(key) {
    if (!COLUMNS.find((c) => c.key === key)?.sortable) return;
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortKey(key);
      setSortDir('desc');
    }
  }

  function goToPage(p) {
    if (!onPageChange || totalPages === 0) return;
    onPageChange(Math.min(Math.max(1, p), totalPages));
  }

  const pageNumbers = getPageNumbers(currentPage, totalPages);

  return (
    <div className="risky-proj">
      <div className="risky-proj__header">
        <h3 className="panel-title">All Projects</h3>
        <button type="button" className="risky-proj__export" onClick={onExport}>
          <svg width="13" height="13" viewBox="0 0 16 16" fill="none" aria-hidden="true">
            <path d="M8 2v8.2M8 10.2 5 7.2M8 10.2l3-3" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
            <path d="M3 12v1.4A1.6 1.6 0 0 0 4.6 15h6.8A1.6 1.6 0 0 0 13 13.4V12" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          Export
        </button>
      </div>

      <div className="risky-proj__scroll">
        <table className="risky-proj__table">
          <thead>
            <tr>
              {COLUMNS.map((col) => (
                <th
                  key={col.key}
                  className={col.sortable ? 'is-sortable' : ''}
                  onClick={() => toggleSort(col.key)}
                >
                  <span>
                    {col.label}
                    {col.sortable && sortKey === col.key && (
                      <span className="risky-proj__sort-arrow">{sortDir === 'asc' ? '\u2191' : '\u2193'}</span>
                    )}
                  </span>
                </th>
              ))}
              <th aria-hidden="true" />
            </tr>
          </thead>
          <tbody>
            {sorted.map((p) => (
              <tr
                key={p.projectId}
                className="risky-proj__row"
                onClick={() => navigate(`/projects/${p.projectId}`)}
                tabIndex={0}
                role="link"
                onKeyDown={(e) => {
                  if (e.key === 'Enter') navigate(`/projects/${p.projectId}`);
                }}
              >
                <td className="risky-proj__work">
                  <span className="risky-proj__work-name">{p.workName}</span>
                  <span className="risky-proj__work-id mono">{p.projectId}</span>
                </td>
                <td>{p.state}</td>
                <td>{p.category}</td>
                <td className="mono">{formatINR(p.sanctionAmount)}</td>
                <td>
                  <span className="risky-proj__stage">{p.workStage}</span>
                </td>
                <td className="mono risky-proj__score">{p.risk.overallScore}</td>
                <td>
                  <RiskBadge level={p.risk.level} size="sm" showScore={false} />
                </td>
                <td className="risky-proj__actions">
                  <button
                    type="button"
                    className={isSaved(p.projectId) ? 'is-saved' : ''}
                    onClick={(event) => {
                      event.stopPropagation();
                      toggleSaved(p);
                    }}
                    aria-label={isSaved(p.projectId) ? 'Remove from review list' : 'Save for review'}
                    title={isSaved(p.projectId) ? 'Saved for review' : 'Save for Review'}
                  >
                    {isSaved(p.projectId) ? '★' : '☆'}
                  </button>
                  <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
                    <path d="M6 3.5 10.5 8 6 12.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </td>
              </tr>
            ))}

            {loading && (
              <tr>
                <td colSpan={8} className="risky-proj__empty">
                  Loading projects…
                </td>
              </tr>
            )}

            {!loading && sorted.length === 0 && (
              <tr>
                <td colSpan={8} className="risky-proj__empty">
                  No projects match the current filters.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="risky-proj__footer">
        <span className="risky-proj__count">
          Showing {total === 0 ? 0 : pageStart + 1} to {Math.min(pageStart + projects.length, total)} of{' '}
          {total} results
        </span>

        <div className="risky-proj__pagination">
          <button type="button" onClick={() => goToPage(currentPage - 1)} disabled={loading || currentPage === 1} aria-label="Previous page">
            &lsaquo;
          </button>
          {pageNumbers.map((p, i) =>
            p === '...' ? (
              <span key={`ellipsis-${i}`} className="risky-proj__ellipsis">
                &hellip;
              </span>
            ) : (
              <button
                key={p}
                type="button"
                className={p === currentPage ? 'is-active' : ''}
                onClick={() => goToPage(p)}
                disabled={loading}
              >
                {p}
              </button>
            )
          )}
          <button
            type="button"
            onClick={() => goToPage(currentPage + 1)}
            disabled={loading || totalPages === 0 || currentPage === totalPages}
            aria-label="Next page"
          >
            &rsaquo;
          </button>
        </div>
      </div>
    </div>
  );
}

function getPageNumbers(current, total) {
  if (total <= 7) return Array.from({ length: total }, (_, i) => i + 1);
  const pages = new Set([1, 2, total - 1, total, current - 1, current, current + 1]);
  const sorted = [...pages].filter((p) => p >= 1 && p <= total).sort((a, b) => a - b);
  const result = [];
  let prev = 0;
  for (const p of sorted) {
    if (prev && p - prev > 1) result.push('...');
    result.push(p);
    prev = p;
  }
  return result;
}
