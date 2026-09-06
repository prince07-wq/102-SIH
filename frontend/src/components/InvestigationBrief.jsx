import { buildInvestigationBrief, downloadText, printBrief } from '../utils/reports';

export default function InvestigationBrief({ aggregates, scope, onClose }) {
  const brief = buildInvestigationBrief(aggregates, scope);

  return (
    <div className="brief" role="dialog" aria-modal="true" aria-labelledby="brief-title">
      <div className="brief__panel">
        <div className="brief__header">
          <h2 id="brief-title">Investigation Brief</h2>
          <button type="button" onClick={onClose} aria-label="Close investigation brief">&times;</button>
        </div>
        <pre className="brief__content">{brief}</pre>
        <div className="brief__actions">
          <button type="button" onClick={() => downloadText('mplads-investigation-brief.txt', brief)}>Download</button>
          <button type="button" onClick={() => printBrief(brief)}>Print</button>
        </div>
      </div>
    </div>
  );
}
