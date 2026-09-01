import './Insights.css';

const ICONS = {
  cost: (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M10 2.5 2.5 15.5h15L10 2.5Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <path d="M10 8v3.4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <circle cx="10" cy="13.4" r="0.9" fill="currentColor" />
    </svg>
  ),
  delay: (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <circle cx="10" cy="10" r="7.2" stroke="currentColor" strokeWidth="1.4" />
      <path d="M10 6v4.2l3 1.8" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  ),
  expenditure: (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M3 15V9.5L10 4l7 5.5V15" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <path d="M7.5 15v-4h5v4" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
    </svg>
  ),
  duplicate: (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <rect x="6.2" y="6.2" width="9.3" height="9.3" rx="1.4" stroke="currentColor" strokeWidth="1.4" />
      <path d="M4.5 12.3V5.9a1.4 1.4 0 0 1 1.4-1.4h6.4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  ),
};

/**
 * Insights — analytical observation list ("AI Insights").
 * Not a chatbot / conversational interface — a static list of
 * rule-derived observations passed in as props.
 *
 * Props:
 *  - insights: [{ id, type, text }]
 */
export default function Insights({ insights = [] }) {
  return (
    <div className="insights">
      <h3 className="panel-title">AI Insights</h3>

      {insights.length === 0 ? (
        <p className="insights__text">No flagged risk components in the complete matching result set.</p>
      ) : (
        <ul className="insights__list">
          {insights.map((item) => (
            <li key={item.id} className={`insights__item insights__item--${item.type}`}>
              <span className="insights__icon">{ICONS[item.type] || ICONS.cost}</span>
              <p className="insights__text">{item.text}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
