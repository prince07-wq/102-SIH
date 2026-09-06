export const ML_AGREEMENT_LABELS = Object.freeze({
  BOTH_HIGH: 'Corroborated Anomaly',
  ML_ONLY: 'AI-Detected Pattern',
  RULE_ONLY: 'Explainable Risk Signal',
  NEITHER: 'No Significant Anomaly Detected',
  ML_NOT_APPLICABLE: 'ML Analysis Not Applicable',
});

export const ML_ANOMALY_LEVELS = Object.freeze([
  'BASELINE',
  'ELEVATED',
  'HIGH',
  'VERY_HIGH',
]);

export const ML_RULE_AGREEMENTS = Object.freeze([
  'BOTH_HIGH',
  'ML_ONLY',
  'RULE_ONLY',
  'NEITHER',
  'ML_NOT_APPLICABLE',
]);

export const RISK_SCORE_EXPLANATION =
  'Represents anomaly severity and review priority from explainable checks, not probability of fraud.';

export const ML_SCORE_EXPLANATION =
  "Measures how unusual a project's multidimensional expenditure behavior is compared with other expenditure-bearing MPLADS projects. It is not a probability of fraud.";

export function getMlAgreementLabel(value) {
  return ML_AGREEMENT_LABELS[value] || 'Agreement unavailable';
}

export function formatMlLevel(value) {
  if (!value) return 'Level unavailable';
  return value
    .toLowerCase()
    .split('_')
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(' ');
}

export function formatMlScore(value) {
  if (value === null || value === undefined || !Number.isFinite(Number(value))) {
    return 'Unavailable';
  }
  return Number(value).toFixed(2).replace(/\.00$/, '').replace(/(\.\d)0$/, '$1');
}

export function buildMlPresentation(project) {
  if (project?.mlEligible !== true) {
    return {
      eligible: false,
      heading: 'ML analysis not applicable',
      explanation:
        'Insufficient expenditure behavior is available for behavioral anomaly analysis.',
      agreementLabel: getMlAgreementLabel('ML_NOT_APPLICABLE'),
      scoreText: null,
      anomalyStatus: null,
    };
  }

  return {
    eligible: true,
    heading: 'AI Analysis',
    explanation: ML_SCORE_EXPLANATION,
    agreementLabel: getMlAgreementLabel(project.mlRuleAgreement),
    scoreText: formatMlScore(project.mlAnomalyScore),
    anomalyStatus: project.mlIsAnomaly === true
      ? 'Anomaly detected'
      : 'No anomaly detected',
    anomalyDetected: project.mlIsAnomaly === true,
    levelText: formatMlLevel(project.mlAnomalyLevel),
  };
}
