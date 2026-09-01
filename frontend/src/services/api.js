// services/api.js
//
// Data access and dashboard aggregation for the MPLADS FastAPI backend.

const configuredBaseUrl = import.meta.env?.VITE_API_BASE_URL;
export const API_BASE_URL = (configuredBaseUrl || 'http://localhost:8000').replace(/\/$/, '');

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: 'application/json' },
    ...options,
  });

  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const error = new Error(body?.detail || `API request failed with status ${response.status}`);
    error.status = response.status;
    throw error;
  }

  return response.json();
}

function appendParam(params, key, value) {
  if (value !== undefined && value !== null && value !== '' && value !== 'All') {
    params.set(key, value);
  }
}

export function buildProjectQuery({ risk, state, category, search } = {}) {
  const params = new URLSearchParams();
  appendParam(params, 'risk', risk);
  appendParam(params, 'state', state);
  appendParam(params, 'category', category);
  appendParam(params, 'search', search?.trim());
  return params;
}

export function getProjectExportUrl(filters = {}) {
  const query = buildProjectQuery(filters).toString();
  return `${API_BASE_URL}/api/projects/export${query ? `?${query}` : ''}`;
}

export function getProjects(
  { page = 1, pageSize = 8, risk, state, category, search } = {},
  signal,
) {
  const params = buildProjectQuery({ risk, state, category, search });
  params.set('page', String(page));
  params.set('page_size', String(pageSize));
  return request(`/api/projects?${params}`, { signal });
}

export function getProjectAggregates({ risk, state, category, search } = {}, signal) {
  const params = buildProjectQuery({ risk, state, category, search });
  const query = params.toString();
  return request(`/api/projects/aggregates${query ? `?${query}` : ''}`, { signal });
}

export async function getProjectById(id, signal) {
  try {
    return await request(`/api/projects/${encodeURIComponent(id)}`, { signal });
  } catch (error) {
    if (error.status === 404) return null;
    throw error;
  }
}

export function getProjectFilterOptions(signal) {
  return request('/api/projects/options', { signal });
}

export function getStatistics(signal) {
  return request('/api/statistics', { signal });
}

export function getAlerts({ page = 1, pageSize = 8 } = {}, signal) {
  const params = new URLSearchParams({ page: String(page), page_size: String(pageSize) });
  return request(`/api/alerts?${params}`, { signal });
}

export function buildStateRiskData(aggregates) {
  return aggregates.stateAggregates
    .map((state) => ({
      state: state.state,
      score: state.averageRisk,
      projectCount: state.projectCount,
    }))
    .sort((a, b) => b.score - a.score);
}

export function buildAnomalyDistribution(aggregates) {
  const counts = aggregates.flaggedComponentCounts;
  const total = Object.values(counts).reduce((sum, value) => sum + value, 0);
  const labels = {
    cost: 'Cost Anomaly',
    delay: 'Delay/Stagnation',
    expenditure: 'Expenditure',
    duplicate: 'Duplicate/Similar',
  };

  return Object.entries(counts).map(([key, value]) => ({
    key,
    label: labels[key],
    value,
    pct: total ? (value / total) * 100 : 0,
  }));
}

export function buildInsights(aggregates) {
  const labels = {
    cost: 'cost',
    delay: 'delay',
    expenditure: 'expenditure',
    duplicate: 'repeated-project',
  };

  const componentInsights = Object.keys(labels)
    .map((key) => {
      const flaggedCount = aggregates.flaggedComponentCounts[key];
      if (!flaggedCount) return null;
      return {
        id: key,
        type: key,
        text: `${flaggedCount} matching project(s) have a ${labels[key]} risk signal and require review.`,
      };
    })
    .filter(Boolean);

  const highestRiskState = [...aggregates.stateAggregates].sort(
    (a, b) => b.averageRisk - a.averageRisk,
  )[0];
  if (highestRiskState) {
    componentInsights.unshift({
      id: 'state-risk',
      type: 'cost',
      text: `${highestRiskState.state} has the highest average risk (${highestRiskState.averageRisk}) across ${highestRiskState.projectCount} matching project(s).`,
    });
  }
  return componentInsights;
}

export function buildSummary(aggregates) {
  const priorityRisk = aggregates.riskLevelCounts.high + aggregates.riskLevelCounts.critical;
  const alertCoverage = aggregates.totalProjects
    ? (aggregates.requiresReviewCount / aggregates.totalProjects) * 100
    : 0;
  const criticalShare = aggregates.totalProjects
    ? (aggregates.riskLevelCounts.critical / aggregates.totalProjects) * 100
    : 0;

  return {
    totalWorksAnalysed: aggregates.totalProjects,
    totalSanctioned: aggregates.totalSanctionAmount,
    totalExpenditure: aggregates.totalExpenditure,
    priorityRiskWorks: priorityRisk,
    underReview: aggregates.requiresReviewCount,
    moderateRisk: aggregates.riskLevelCounts.moderate,
    criticalSharePct: criticalShare.toFixed(1),
    alertCoveragePct: alertCoverage.toFixed(1),
  };
}

export const FALLBACK_FILTER_OPTIONS = {
  categories: [],
  states: [],
  riskLevels: ['CRITICAL', 'HIGH', 'MODERATE', 'LOW'],
};
