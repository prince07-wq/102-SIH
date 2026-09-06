import './RiskBadge.css';

const LEVEL_CONFIG = {
  CRITICAL: { label: 'Critical Risk', short: 'Critical', className: 'risk-badge--critical' },
  HIGH: { label: 'High Risk', short: 'High', className: 'risk-badge--high' },
  MODERATE: { label: 'Moderate Risk', short: 'Moderate', className: 'risk-badge--moderate' },
  MEDIUM: { label: 'Moderate Risk', short: 'Moderate', className: 'risk-badge--moderate' },
  LOW: { label: 'Low Risk', short: 'Low', className: 'risk-badge--low' },
};

/**
 * RiskBadge — reusable Combined Risk V1 level indicator.
 * Displays overall risk level only. No chart logic lives here.
 *
 * Props:
 *  - level: 'CRITICAL' | 'HIGH' | 'MODERATE' | 'LOW'
 *  - score: number (optional)
 *  - size: 'sm' | 'md' (optional, default 'md')
 *  - showScore: boolean (optional, default true when score is provided)
 */
export default function RiskBadge({ level = 'LOW', score, size = 'md', showScore = true }) {
  const config = LEVEL_CONFIG[level] || LEVEL_CONFIG.LOW;

  return (
    <span className={`risk-badge risk-badge--${size} ${config.className}`}>
      <span className="risk-badge__dot" aria-hidden="true" />
      <span className="risk-badge__label">{size === 'sm' ? config.short : config.label}</span>
      {showScore && score !== undefined && score !== null && (
        <span className="risk-badge__score">{score}</span>
      )}
    </span>
  );
}
