import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Link, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import ProjectDetails from './pages/ProjectDetails';
import './App.css';

const NAV_ITEMS = [
  { key: 'overview', label: 'Overview', path: '/', icon: IconGrid, active: true },
  { key: 'high-risk', label: 'High Risk Works', path: null, icon: IconAlert },
  { key: 'projects', label: 'Projects', path: null, icon: IconFolder },
  { key: 'anomalies', label: 'Anomalies', path: null, icon: IconPulse },
  { key: 'expenditure', label: 'Expenditure', path: null, icon: IconWallet },
  { key: 'duplicate', label: 'Duplicate Detector', path: null, icon: IconCopy },
  { key: 'analytics', label: 'Analytics', path: null, icon: IconBars },
  { key: 'reports', label: 'Reports', path: null, icon: IconDoc },
  { key: 'watchlist', label: 'Watchlist', path: null, icon: IconEye },
];

export default function App() {
  return (
    <BrowserRouter>
      <AppShell />
    </BrowserRouter>
  );
}

function AppShell() {
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Close the mobile sidebar drawer whenever the route changes.
  useEffect(() => {
    setSidebarOpen(false);
  }, [location.pathname]);

  return (
    <div className="app-shell">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} pathname={location.pathname} />

      {sidebarOpen && <div className="app-shell__scrim" onClick={() => setSidebarOpen(false)} aria-hidden="true" />}

      <div className="app-shell__main">
        <Header onToggleSidebar={() => setSidebarOpen((v) => !v)} />

        <div className="app-shell__content">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/project/:id" element={<ProjectDetails />} />
          </Routes>
        </div>
      </div>
    </div>
  );
}

function Sidebar({ open, onClose, pathname }) {
  return (
    <aside className={`sidebar ${open ? 'sidebar--open' : ''}`}>
      <div className="sidebar__brand">
        <div className="sidebar__brand-mark">
          <IconShield />
        </div>
        <div className="sidebar__brand-text">
          <span className="sidebar__brand-name">MPLADS</span>
          <span className="sidebar__brand-sub">RISK INTELLIGENCE</span>
        </div>
        <button className="sidebar__close" onClick={onClose} aria-label="Close navigation">
          &times;
        </button>
      </div>

      <nav className="sidebar__nav" aria-label="Primary">
        {NAV_ITEMS.map((item) => {
          const isActive = item.path && pathname === item.path;
          const Icon = item.icon;
          const content = (
            <>
              <Icon />
              <span>{item.label}</span>
            </>
          );
          return item.path ? (
            <Link key={item.key} to={item.path} className={`sidebar__link ${isActive ? 'is-active' : ''}`}>
              {content}
            </Link>
          ) : (
            <span key={item.key} className="sidebar__link sidebar__link--inactive" aria-disabled="true">
              {content}
            </span>
          );
        })}
      </nav>

      <div className="sidebar__system">
        <span className="sidebar__system-label">System</span>
        <span className="sidebar__link sidebar__link--inactive">
          <IconLayers />
          <span>Data Coverage</span>
        </span>
        <span className="sidebar__link sidebar__link--inactive">
          <IconSettings />
          <span>Settings</span>
        </span>
      </div>

      <div className="sidebar__mission">
        <p>
          <strong>Our mission:</strong> Detect anomalies. Prioritize investigation. Drive transparency.
        </p>
        <span className="sidebar__mission-link">Learn more</span>
      </div>
    </aside>
  );
}

function Header({ onToggleSidebar }) {
  return (
    <header className="app-header">
      <button className="app-header__menu" onClick={onToggleSidebar} aria-label="Toggle navigation">
        <IconMenu />
      </button>

      <div className="app-header__search">
        <IconSearch />
        <input type="text" placeholder="Search work, MP, vendor, location..." aria-label="Global search" />
      </div>

      <div className="app-header__right">
        <button className="app-header__icon-btn" aria-label="Notifications">
          <IconBell />
          <span className="app-header__badge" />
        </button>

        <div className="app-header__user">
          <div className="app-header__user-text">
            <span className="app-header__user-name">Investigation Cell</span>
            <span className="app-header__user-role">Investigator</span>
          </div>
          <div className="app-header__avatar">IC</div>
        </div>
      </div>
    </header>
  );
}

/* ---------------------------------------------------------------------- */
/* Inline icon set (kept minimal — no external icon dependency)            */
/* ---------------------------------------------------------------------- */

function IconShield() {
  return (
    <svg viewBox="0 0 20 20" fill="none" aria-hidden="true">
      <path d="M10 2 3.5 4.4v4.9c0 4.2 2.8 7.6 6.5 8.7 3.7-1.1 6.5-4.5 6.5-8.7V4.4L10 2Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
      <path d="M7.2 10.1l2 2 3.6-4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function IconGrid() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <rect x="2.5" y="2.5" width="5.5" height="5.5" rx="1" stroke="currentColor" strokeWidth="1.3" />
      <rect x="10" y="2.5" width="5.5" height="5.5" rx="1" stroke="currentColor" strokeWidth="1.3" />
      <rect x="2.5" y="10" width="5.5" height="5.5" rx="1" stroke="currentColor" strokeWidth="1.3" />
      <rect x="10" y="10" width="5.5" height="5.5" rx="1" stroke="currentColor" strokeWidth="1.3" />
    </svg>
  );
}
function IconAlert() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <path d="M9 2.5 1.8 15h14.4L9 2.5Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
      <path d="M9 7.2v3.4" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
      <circle cx="9" cy="12.6" r="0.8" fill="currentColor" />
    </svg>
  );
}
function IconFolder() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <path d="M2.5 5.2c0-.7.6-1.3 1.3-1.3h3.1l1.4 1.6h6a1.3 1.3 0 0 1 1.3 1.3v6a1.3 1.3 0 0 1-1.3 1.3H3.8a1.3 1.3 0 0 1-1.3-1.3V5.2Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
    </svg>
  );
}
function IconPulse() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <path d="M2 9.5h3l1.6-4.2 2.6 8 1.8-5.4 1.2 1.6H16" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}
function IconWallet() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <rect x="2.3" y="4.5" width="13.4" height="9.5" rx="1.6" stroke="currentColor" strokeWidth="1.3" />
      <path d="M11.5 9.3h2.6" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  );
}
function IconCopy() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <rect x="6.3" y="6.3" width="9" height="9" rx="1.3" stroke="currentColor" strokeWidth="1.3" />
      <path d="M4.3 11.3V4.3a1.3 1.3 0 0 1 1.3-1.3h7" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  );
}
function IconBars() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <path d="M4 14V8M9 14V4M14 14v-5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  );
}
function IconDoc() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <path d="M4.5 2.5h6l3 3v10a1 1 0 0 1-1 1h-8a1 1 0 0 1-1-1v-12a1 1 0 0 1 1-1Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
      <path d="M6.5 8.5h5M6.5 11.3h5" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}
function IconEye() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <path d="M1.8 9S4.5 4 9 4s7.2 5 7.2 5-2.7 5-7.2 5-7.2-5-7.2-5Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
      <circle cx="9" cy="9" r="2" stroke="currentColor" strokeWidth="1.3" />
    </svg>
  );
}
function IconLayers() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <path d="M9 2.5 2 6.3 9 10l7-3.7L9 2.5Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
      <path d="M2 10 9 13.7 16 10M2 13.4 9 17l7-3.6" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
    </svg>
  );
}
function IconSettings() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <circle cx="9" cy="9" r="2.3" stroke="currentColor" strokeWidth="1.3" />
      <path d="M9 2.8v1.5M9 13.7v1.5M15.2 9h-1.5M4.3 9H2.8M13.2 4.8l-1 1M5.8 12.2l-1 1M13.2 13.2l-1-1M5.8 5.8l-1-1" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round" />
    </svg>
  );
}
function IconMenu() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <path d="M2.5 5h13M2.5 9h13M2.5 13h13" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}
function IconSearch() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <circle cx="8.1" cy="8.1" r="4.6" stroke="currentColor" strokeWidth="1.4" />
      <path d="M15 15 12 12" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}
function IconBell() {
  return (
    <svg viewBox="0 0 18 18" fill="none" aria-hidden="true">
      <path d="M5 7.5a4 4 0 0 1 8 0v3.2l1.3 1.9H3.7L5 10.7V7.5Z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round" />
      <path d="M7.5 14.8a1.5 1.5 0 0 0 3 0" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round" />
    </svg>
  );
}
