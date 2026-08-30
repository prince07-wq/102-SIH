// services/api.js
//
// Data access layer for the MPLADS Risk Intelligence frontend.
//
// Every function below currently resolves from local synthetic data
// (src/mocks/projects.js), but each is written to look and behave like an
// async network call. When a real FastAPI backend is available, these
// implementations can be swapped for `fetch()` calls without changing any
// component code, since components only ever talk to this module.

import { projects as mockProjects } from '../mocks/projects';

const NETWORK_DELAY_MS = 120;

function delay(ms = NETWORK_DELAY_MS) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

// ---------------------------------------------------------------------
// State-level risk aggregation
// ---------------------------------------------------------------------
// India state/UT risk intensities. Where the synthetic project set has
// direct coverage of a state, the score reflects that sample; the
// remaining states are seeded with illustrative pseudo-scores so the
// heatmap reads as a complete country view. All figures are synthetic.
const STATE_RISK_SEED = {
  'Uttar Pradesh': 78, Bihar: 74, 'West Bengal': 69, Maharashtra: 66,
  'Madhya Pradesh': 71, Jharkhand: 63, Odisha: 58, 'Tamil Nadu': 52,
  Rajasthan: 61, Karnataka: 47, 'Andhra Pradesh': 44, Telangana: 42,
  Gujarat: 39, Punjab: 55, Haryana: 49, Kerala: 33, Assam: 57,
  Chhattisgarh: 60, Uttarakhand: 41, 'Himachal Pradesh': 28,
  'Jammu And Kashmir': 45, Delhi: 36, Goa: 22, Tripura: 38,
  Meghalaya: 34, Manipur: 40, Nagaland: 31, Mizoram: 24, Sikkim: 18,
  'Arunachal Pradesh': 30, Puducherry: 26, Chandigarh: 20, Ladakh: 16,
  Lakshadweep: 14,
  'The Dadra And Nagar Haveli And Daman And Diu': 25,
  'Andaman And Nicobar Islands': 19,
};

function buildStateRiskData() {
  return Object.entries(STATE_RISK_SEED)
    .map(([state, score]) => ({ state, score }))
    .sort((a, b) => b.score - a.score);
}

// ---------------------------------------------------------------------
// Anomaly distribution (donut chart)
// ---------------------------------------------------------------------
function buildAnomalyDistribution(list) {
  const counts = { cost: 0, delay: 0, expenditure: 0, duplicate: 0 };
  list.forEach((p) => {
    if (p.risk.cost.flagged) counts.cost += 1;
    if (p.risk.delay.flagged) counts.delay += 1;
    if (p.risk.expenditure.flagged) counts.expenditure += 1;
    if (p.risk.duplicate.flagged) counts.duplicate += 1;
  });
  const total = counts.cost + counts.delay + counts.expenditure + counts.duplicate || 1;
  return [
    { key: 'cost', label: 'Cost Anomaly', value: counts.cost, pct: (counts.cost / total) * 100 },
    { key: 'delay', label: 'Delay/Stagnation', value: counts.delay, pct: (counts.delay / total) * 100 },
    { key: 'expenditure', label: 'Expenditure', value: counts.expenditure, pct: (counts.expenditure / total) * 100 },
    { key: 'duplicate', label: 'Duplicate/Similar', value: counts.duplicate, pct: (counts.duplicate / total) * 100 },
  ];
}

// ---------------------------------------------------------------------
// AI insights (rule-based, generated from the synthetic dataset)
// ---------------------------------------------------------------------
function buildInsights(list) {
  const insights = [];

  const byStateCost = {};
  list.forEach((p) => {
    if (p.risk.cost.flagged) byStateCost[p.state] = (byStateCost[p.state] || 0) + 1;
  });
  const topCostState = Object.entries(byStateCost).sort((a, b) => b[1] - a[1])[0];
  if (topCostState) {
    insights.push({
      id: 'cost',
      type: 'cost',
      text: `${topCostState[0]} has ${topCostState[1]} works flagged with unusually high costs compared to similar works in their districts.`,
    });
  }

  const delayedCount = list.filter((p) => p.risk.delay.flagged).length;
  const byStateDelay = {};
  list.forEach((p) => {
    if (p.risk.delay.flagged) byStateDelay[p.state] = (byStateDelay[p.state] || 0) + 1;
  });
  const topDelayState = Object.entries(byStateDelay).sort((a, b) => b[1] - a[1])[0];
  if (topDelayState) {
    insights.push({
      id: 'delay',
      type: 'delay',
      text: `${topDelayState[1]} works in ${topDelayState[0]} have been delayed beyond 180 days without a progress update.`,
    });
  } else if (delayedCount) {
    insights.push({ id: 'delay', type: 'delay', text: `${delayedCount} works have been delayed beyond 180 days.` });
  }

  const expByState = {};
  list.forEach((p) => {
    if (p.risk.expenditure.flagged) {
      expByState[p.state] = (expByState[p.state] || 0) + p.totalDisbursed;
    }
  });
  const topExpState = Object.entries(expByState).sort((a, b) => b[1] - a[1])[0];
  if (topExpState) {
    const cr = (topExpState[1] / 1e7).toFixed(1);
    insights.push({
      id: 'expenditure',
      type: 'expenditure',
      text: `Expenditure spikes detected in ${topExpState[0]}, totalling approximately \u20B9${cr} Cr against physical progress reported.`,
    });
  }

  const dupCount = list.filter((p) => p.risk.duplicate.flagged).length;
  const dupStates = new Set(list.filter((p) => p.risk.duplicate.flagged).map((p) => p.state)).size;
  if (dupCount) {
    insights.push({
      id: 'duplicate',
      type: 'duplicate',
      text: `${dupCount} possible duplicate or highly similar works detected across ${dupStates} states.`,
    });
  }

  return insights;
}

// ---------------------------------------------------------------------
// Summary statistics (KPI cards + bottom summary bar)
// ---------------------------------------------------------------------
function buildSummary(list) {
  const highRisk = list.filter((p) => p.risk.level === 'HIGH').length;
  const totalSanctioned = list.reduce((sum, p) => sum + p.sanctionAmount, 0);
  const totalDisbursed = list.reduce((sum, p) => sum + p.totalDisbursed, 0);

  return {
    // Nationwide-scale figures presented for dashboard context; the
    // synthetic project sample below represents a working subset used
    // for the "All Projects" investigation table.
    totalWorksAnalysed: 1248532,
    totalWorksTrend: '+8.7%',
    totalSanctioned: 1453420000000, // ₹1,45,342 Cr equivalent, illustrative
    totalSanctionedTrend: '+6.3%',
    totalExpenditure: 987650000000, // ₹98,765 Cr equivalent, illustrative
    totalExpenditureTrend: '+9.1%',
    highRiskWorksNational: 8843,
    highRiskWorksTrend: '+14.2%',
    underInvestigation: 1243,
    underInvestigationTrend: '+5.6%',

    // Figures grounded directly in the synthetic sample dataset.
    sampleWorksAnalysed: list.length,
    sampleHighRisk: highRisk,
    sampleSanctioned: totalSanctioned,
    sampleDisbursed: totalDisbursed,

    activeInvestigationScope: 42,
    auditCoveragePct: 89,
    recoveredFunds: '\u20B914K Cr',
  };
}

// ---------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------

export async function getProjects() {
  await delay();
  return mockProjects;
}

export async function getProjectById(id) {
  await delay(80);
  return mockProjects.find((p) => p.projectId === id) || null;
}

export async function getStateRiskData() {
  await delay(80);
  return buildStateRiskData();
}

export async function getAnomalyDistribution() {
  await delay(80);
  return buildAnomalyDistribution(mockProjects);
}

export async function getInsights() {
  await delay(80);
  return buildInsights(mockProjects);
}

export async function getSummary() {
  await delay(60);
  return buildSummary(mockProjects);
}

export const FILTER_OPTIONS = {
  categories: [
    'Roads & Bridges',
    'Drainage',
    'Education',
    'Water Supply',
    'Health',
    'Sanitation',
    'Community Infrastructure',
    'Others',
  ],
  states: Array.from(new Set(mockProjects.map((p) => p.state))).sort(),
  riskLevels: ['HIGH', 'MEDIUM', 'LOW'],
};
