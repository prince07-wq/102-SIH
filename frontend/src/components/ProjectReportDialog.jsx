import { buildProjectReport, downloadText, printBrief, projectReportFilename } from '../utils/reports';

export default function ProjectReportDialog({ project, onClose }) {
  const report = buildProjectReport(project);

  return (
    <div className="brief" role="dialog" aria-modal="true" aria-labelledby="project-report-title">
      <div className="brief__panel">
        <div className="brief__header">
          <h2 id="project-report-title">Project Investigation Report</h2>
          <button type="button" onClick={onClose} aria-label="Close project report">&times;</button>
        </div>
        <pre className="brief__content">{report}</pre>
        <div className="brief__actions">
          <button type="button" onClick={() => downloadText(projectReportFilename(project.projectId), report)}>Download Project Report</button>
          <button type="button" onClick={() => printBrief(report)}>Print</button>
        </div>
      </div>
    </div>
  );
}
