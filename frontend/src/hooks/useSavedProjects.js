import { useCallback, useEffect, useState } from 'react';

const STORAGE_KEY = 'mplads_saved_projects_v1';
const CHANGE_EVENT = 'mplads:saved-projects-changed';

function readSavedProjects() {
  if (typeof window === 'undefined') return [];
  try {
    const saved = JSON.parse(window.localStorage.getItem(STORAGE_KEY) || '[]');
    return Array.isArray(saved) ? saved : [];
  } catch {
    return [];
  }
}

function projectSummary(project) {
  return {
    projectId: project.projectId,
    workName: project.workName,
    state: project.state,
    constituency: project.constituency,
    riskLevel: project.risk?.level,
    overallScore: project.risk?.overallScore,
    savedAt: new Date().toISOString(),
  };
}

export function useSavedProjects() {
  const [savedProjects, setSavedProjects] = useState(readSavedProjects);

  useEffect(() => {
    const refresh = () => setSavedProjects(readSavedProjects());
    window.addEventListener('storage', refresh);
    window.addEventListener(CHANGE_EVENT, refresh);
    return () => {
      window.removeEventListener('storage', refresh);
      window.removeEventListener(CHANGE_EVENT, refresh);
    };
  }, []);

  const toggleSaved = useCallback((project) => {
    const current = readSavedProjects();
    const exists = current.some((saved) => saved.projectId === project.projectId);
    const next = exists
      ? current.filter((saved) => saved.projectId !== project.projectId)
      : [projectSummary(project), ...current];
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
    window.dispatchEvent(new Event(CHANGE_EVENT));
  }, []);

  const isSaved = useCallback(
    (projectId) => savedProjects.some((project) => project.projectId === projectId),
    [savedProjects],
  );

  return { savedProjects, toggleSaved, isSaved };
}
