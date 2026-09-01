import { useState } from 'react';
import { Link } from 'react-router-dom';
import RiskBadge from './RiskBadge';
import { getProjectById } from '../services/api';
import { useSavedProjects } from '../hooks/useSavedProjects';
import { buildProjectReport, downloadText, projectReportFilename } from '../utils/reports';

export default function SavedProjectList() {
  const { savedProjects, toggleSaved } = useSavedProjects();
  const [downloadingId, setDownloadingId] = useState(null);
  const [error, setError] = useState(null);

  async function downloadProjectReport(savedProject) {
    setDownloadingId(savedProject.projectId);
    setError(null);
    try {
      const project = await getProjectById(savedProject.projectId);
      if (!project) throw new Error(`Project ${savedProject.projectId} is no longer available`);
      downloadText(projectReportFilename(project.projectId), buildProjectReport(project));
    } catch (downloadError) {
      setError(downloadError.message);
    } finally {
      setDownloadingId(null);
    }
  }

  if (savedProjects.length === 0) {
    return <div className="utility-page__empty">No projects have been saved for review. Select a project before generating a project report.</div>;
  }

  return (
    <>
      {error && <div className="utility-page__error" role="alert">Unable to download report: {error}</div>}
      <div className="saved-list">
        {savedProjects.map((project) => (
          <div className="saved-list__item" key={project.projectId}>
            <div className="saved-list__summary">
              <strong>{project.workName}</strong>
              <span>{project.state} · {project.constituency} · {project.projectId}</span>
            </div>
            <RiskBadge level={project.riskLevel} score={project.overallScore} />
            <div className="saved-list__actions">
              <Link to={`/projects/${project.projectId}`}>Open</Link>
              <button type="button" onClick={() => downloadProjectReport(project)} disabled={downloadingId === project.projectId}>
                {downloadingId === project.projectId ? 'Preparing…' : 'Download Report'}
              </button>
              <button type="button" onClick={() => toggleSaved(project)}>Remove</button>
            </div>
          </div>
        ))}
      </div>
    </>
  );
}
