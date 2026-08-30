import './RiskBadge.css';

const LEVEL_CONFIG = {
  HIGH: { label: 'High Risk', short: 'High', className: 'risk-badge--high' },
  MEDIUM: { label: 'Medium Risk', short: 'Medium', className: 'risk-badge--medium' },
  LOW: { label: 'Low Risk', short: 'Low', className: 'risk-badge--low' },
};

/**
 * RiskBadge — reusable HIGH / MEDIUM / LOW indicator.
 * Displays overall risk level only. No chart logic lives here.
 *
 * Props:
 *  - level: 'HIGH' | 'MEDIUM' | 'LOW'
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
