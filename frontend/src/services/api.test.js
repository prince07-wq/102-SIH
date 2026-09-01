import assert from 'node:assert/strict';
import test from 'node:test';

import {
  buildAnomalyDistribution,
  buildInsights,
  buildStateRiskData,
  buildSummary,
  getProjectExportUrl,
} from './api.js';
import {
  buildAnomalyCsv,
  buildInvestigationBrief,
  buildProjectReport,
  buildRiskSummaryCsv,
  buildStateRiskCsv,
} from '../utils/reports.js';

const AGGREGATES = {
  totalProjects: 12,
  totalSanctionAmount: 1500000,
  totalExpenditure: 900000,
  riskLevelCounts: { low: 3, moderate: 2, high: 4, critical: 3 },
  requiresReviewCount: 7,
  stateAggregates: [
    { state: 'Karnataka', projectCount: 8, averageRisk: 58.25 },
    { state: 'Kerala', projectCount: 4, averageRisk: 31.5 },
  ],
  flaggedComponentCounts: { cost: 3, delay: 2, expenditure: 4, duplicate: 1 },
};

test('dashboard analytics depend only on full filtered aggregates', () => {
  const firstPage = [{ projectId: '1' }];
  const secondPage = [{ projectId: '2' }];

  const before = {
    states: buildStateRiskData(AGGREGATES),
    anomalies: buildAnomalyDistribution(AGGREGATES),
    insights: buildInsights(AGGREGATES),
    summary: buildSummary(AGGREGATES),
  };

  assert.notDeepEqual(firstPage, secondPage);
  const after = {
    states: buildStateRiskData(AGGREGATES),
    anomalies: buildAnomalyDistribution(AGGREGATES),
    insights: buildInsights(AGGREGATES),
    summary: buildSummary(AGGREGATES),
  };
  assert.deepEqual(after, before);
});

test('state and detector visualizations include every aggregate entry', () => {
  const states = buildStateRiskData(AGGREGATES);
  const anomalies = buildAnomalyDistribution(AGGREGATES);

  assert.equal(states.length, AGGREGATES.stateAggregates.length);
  assert.equal(states.reduce((sum, state) => sum + state.projectCount, 0), 12);
  assert.deepEqual(
    Object.fromEntries(anomalies.map((item) => [item.key, item.value])),
    AGGREGATES.flaggedComponentCounts,
  );
});

test('report builders use aggregate values and current scope', () => {
  const scope = { search: 'street light', risk: 'HIGH', state: 'Karnataka', category: 'All' };
  const brief = buildInvestigationBrief(AGGREGATES, scope);

  assert.match(brief, /Search: street light/);
  assert.match(brief, /Matching projects: 12/);
  assert.match(brief, /Requires review: 7/);
  assert.match(brief, /Karnataka: 58.25 average risk/);
  assert.match(buildRiskSummaryCsv(AGGREGATES), /CRITICAL,3/);
  assert.match(buildAnomalyCsv(AGGREGATES), /expenditure,4/);
  assert.equal(buildStateRiskCsv(AGGREGATES).split('\n').length, 3);
});

test('filtered export URL preserves the complete investigator scope', () => {
  const url = new URL(getProjectExportUrl({
    search: 'street light',
    risk: 'HIGH',
    state: 'Karnataka',
    category: 'Roads & bridges',
  }));
  assert.equal(url.pathname, '/api/projects/export');
  assert.equal(url.searchParams.get('search'), 'street light');
  assert.equal(url.searchParams.get('risk'), 'HIGH');
  assert.equal(url.searchParams.get('state'), 'Karnataka');
  assert.equal(url.searchParams.get('category'), 'Roads & bridges');
  assert.equal(url.searchParams.has('page'), false);
});

test('project report contains one complete project record and detector evidence', () => {
  const project = {
    projectId: '133166',
    workName: 'Community hall construction',
    description: 'Construction of a community hall',
    state: 'Karnataka',
    constituency: 'Dharwad',
    mpName: 'Pralhad Venkatesh Joshi',
    authority: 'District Authority',
    sanctionDate: '2024-08-01',
    sanctionAmount: 500000,
    workStage: 'ONGOING',
    totalDisbursed: 250000,
    expenditureRecordCount: 2,
    firstExpenditureDate: '2024-09-01',
    lastExpenditureDate: '2025-01-10',
    uniqueVendorCount: 1,
    vendors: [{ vendorId: 'V-1', vendorName: 'Example Vendor' }],
    workIds: ['WS/133166'],
    risk: {
      overallScore: 55.21,
      level: 'HIGH',
      flagCount: 1,
      strongestDetector: 'delay',
      baseScore: 55.21,
      multiSignalBonus: 0,
      scoreCapped: false,
      cost: { score: 10, flagged: false, reason: 'Within peer range' },
      delay: { score: 55.21, flagged: true, reason: 'Longer duration signal' },
      expenditure: { score: 0, flagged: false, reason: 'No expenditure signal' },
      duplicate: { score: 12, flagged: false, reason: 'No repeated-project signal' },
    },
    similarProjects: [{
      projectId: '135169',
      workName: 'Related community hall',
      sanctionAmount: 450000,
      sanctionDate: '2024-08-02',
      dateDifferenceDays: 1,
      similarity: null,
    }],
  };

  const report = buildProjectReport(project, '2026-09-01T10:00:00.000Z');
  assert.match(report, /Project ID: 133166/);
  assert.match(report, /Generated: 2026-09-01T10:00:00.000Z/);
  assert.match(report, /Example Vendor \(ID: V-1\)/);
  assert.match(report, /Strongest detector: delay/);
  assert.match(report, /Multi-signal bonus: 0/);
  assert.match(report, /Cost\n  Score: 10\n  Flagged: No/);
  assert.match(report, /Delay\n  Score: 55.21\n  Flagged: Yes/);
  assert.match(report, /Candidate 1\n  Project ID: 135169/);
});

test('project report refuses to fabricate a report without a selected project', () => {
  assert.throws(() => buildProjectReport(null), /complete project record is required/);
});
