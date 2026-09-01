function scopeLines({ search, risk, state, category }) {
  return [
    search ? `Search: ${search}` : 'Search: none',
    `Risk: ${risk && risk !== 'All' ? risk : 'All levels'}`,
    `State: ${state && state !== 'All' ? state : 'All states'}`,
    `Category: ${category && category !== 'All' ? category : 'All categories'}`,
  ];
}

export function buildInvestigationBrief(aggregates, scope) {
  const risk = aggregates.riskLevelCounts;
  const flags = aggregates.flaggedComponentCounts;
  const highestRiskStates = [...aggregates.stateAggregates]
    .sort((a, b) => b.averageRisk - a.averageRisk || b.projectCount - a.projectCount)
    .slice(0, 5);

  return [
    'MPLADS Investigation Brief',
    `Generated: ${new Date().toLocaleString()}`,
    '',
    'Scope',
    ...scopeLines(scope),
    '',
    `Matching projects: ${aggregates.totalProjects}`,
    `Total sanction amount: INR ${aggregates.totalSanctionAmount.toFixed(2)}`,
    `Total expenditure: INR ${aggregates.totalExpenditure.toFixed(2)}`,
    `Requires review: ${aggregates.requiresReviewCount}`,
    '',
    'Risk distribution',
    `LOW: ${risk.low}`,
    `MODERATE: ${risk.moderate}`,
    `HIGH: ${risk.high}`,
    `CRITICAL: ${risk.critical}`,
    '',
    'Detector flag counts',
    `Cost: ${flags.cost}`,
    `Delay: ${flags.delay}`,
    `Expenditure: ${flags.expenditure}`,
    `Duplicate/similarity: ${flags.duplicate}`,
    '',
    'Highest average-risk states in this scope',
    ...(highestRiskStates.length
      ? highestRiskStates.map(
          (item) => `${item.state}: ${item.averageRisk} average risk across ${item.projectCount} projects`,
        )
      : ['No matching state data.']),
    '',
    'Note: This brief summarizes processed risk signals for review. It does not assert fraud or wrongdoing.',
  ].join('\n');
}

function reportValue(value) {
  if (value === null || value === undefined || value === '') return 'Not available';
  if (typeof value === 'boolean') return value ? 'Yes' : 'No';
  return String(value);
}

function reportAmount(value) {
  return value === null || value === undefined ? 'Not available' : `INR ${Number(value).toFixed(2)}`;
}

export function buildProjectReport(project, generatedAt = new Date()) {
  if (!project?.projectId) throw new Error('A complete project record is required');

  const risk = project.risk;
  const vendors = project.vendors?.length
    ? project.vendors.map(
        (vendor) => `${reportValue(vendor.vendorName)} (ID: ${reportValue(vendor.vendorId)})`,
      )
    : ['No vendor records available'];
  const workIds = project.workIds?.length ? project.workIds : ['No work IDs available'];
  const similarProjects = project.similarProjects?.length
    ? project.similarProjects.flatMap((similar, index) => [
        `Candidate ${index + 1}`,
        `  Project ID: ${reportValue(similar.projectId)}`,
        `  Work name: ${reportValue(similar.workName)}`,
        `  Sanction amount: ${reportAmount(similar.sanctionAmount)}`,
        `  Sanction date: ${reportValue(similar.sanctionDate)}`,
        `  Date difference days: ${reportValue(similar.dateDifferenceDays)}`,
        `  Similarity: ${reportValue(similar.similarity)}`,
      ])
    : ['No similar-project evidence available'];

  const detectorLines = ['cost', 'delay', 'expenditure', 'duplicate'].flatMap((name) => {
    const detector = risk?.[name];
    return [
      `${name.charAt(0).toUpperCase()}${name.slice(1)}`,
      `  Score: ${reportValue(detector?.score)}`,
      `  Flagged: ${reportValue(detector?.flagged)}`,
      `  Reason: ${reportValue(detector?.reason)}`,
    ];
  });

  return [
    'MPLADS Project Investigation Report',
    `Generated: ${new Date(generatedAt).toISOString()}`,
    '',
    'Project',
    `Project ID: ${reportValue(project.projectId)}`,
    `Project name: ${reportValue(project.workName)}`,
    `Description: ${reportValue(project.description)}`,
    `State: ${reportValue(project.state)}`,
    `Constituency: ${reportValue(project.constituency)}`,
    `MP: ${reportValue(project.mpName)}`,
    `Authority: ${reportValue(project.authority)}`,
    '',
    'Sanction',
    `Sanction date: ${reportValue(project.sanctionDate)}`,
    `Sanction amount: ${reportAmount(project.sanctionAmount)}`,
    `Work stage: ${reportValue(project.workStage)}`,
    '',
    'Expenditure',
    `Total expenditure: ${reportAmount(project.totalDisbursed)}`,
    `Expenditure record count: ${reportValue(project.expenditureRecordCount)}`,
    `First expenditure date: ${reportValue(project.firstExpenditureDate)}`,
    `Last expenditure date: ${reportValue(project.lastExpenditureDate)}`,
    `Unique vendor count: ${reportValue(project.uniqueVendorCount)}`,
    'Vendors:',
    ...vendors.map((vendor) => `  ${vendor}`),
    'Work IDs:',
    ...workIds.map((workId) => `  ${workId}`),
    '',
    'Overall risk',
    `Overall score: ${reportValue(risk?.overallScore)}`,
    `Risk level: ${reportValue(risk?.level)}`,
    `Flag count: ${reportValue(risk?.flagCount)}`,
    `Strongest detector: ${reportValue(risk?.strongestDetector)}`,
    `Base score: ${reportValue(risk?.baseScore)}`,
    `Multi-signal bonus: ${reportValue(risk?.multiSignalBonus)}`,
    `Score capped at 100: ${reportValue(risk?.scoreCapped)}`,
    '',
    'Detector evidence',
    ...detectorLines,
    '',
    'Similar-project evidence',
    ...similarProjects,
    '',
    'Note: This report presents processed risk signals for review. It does not assert fraud or wrongdoing.',
  ].join('\n');
}

export function projectReportFilename(projectId) {
  const safeId = String(projectId).replaceAll(/[^a-zA-Z0-9_-]/g, '-');
  return `mplads-project-${safeId}-report.txt`;
}

function csvCell(value) {
  const text = String(value ?? '');
  return /[",\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

export function buildRiskSummaryCsv(aggregates) {
  return [
    ['risk_level', 'project_count'],
    ['LOW', aggregates.riskLevelCounts.low],
    ['MODERATE', aggregates.riskLevelCounts.moderate],
    ['HIGH', aggregates.riskLevelCounts.high],
    ['CRITICAL', aggregates.riskLevelCounts.critical],
    ['REQUIRES_REVIEW', aggregates.requiresReviewCount],
  ].map((row) => row.map(csvCell).join(',')).join('\n');
}

export function buildAnomalyCsv(aggregates) {
  return [
    ['detector', 'flagged_project_count'],
    ...Object.entries(aggregates.flaggedComponentCounts),
  ].map((row) => row.map(csvCell).join(',')).join('\n');
}

export function buildStateRiskCsv(aggregates) {
  return [
    ['state', 'project_count', 'average_risk'],
    ...aggregates.stateAggregates.map((item) => [item.state, item.projectCount, item.averageRisk]),
  ].map((row) => row.map(csvCell).join(',')).join('\n');
}

export function downloadText(filename, text, type = 'text/plain;charset=utf-8') {
  const blob = new Blob([text], { type });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

export function printBrief(brief) {
  const printWindow = window.open('', '_blank');
  if (!printWindow) return false;
  const escaped = brief
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;');
  printWindow.document.write(`<title>MPLADS Investigation Brief</title><pre>${escaped}</pre>`);
  printWindow.document.close();
  printWindow.print();
  return true;
}
