# MPLADS Risk Intelligence — Frontend

A React + Vite frontend for an MPLADS risk-intelligence / investigation dashboard.

## Run it

```bash
npm install
npm run dev
```

Then open the printed local URL (typically http://localhost:5173).

## What's inside

- **Dashboard / Overview** (`/`) — KPI cards, a state-level risk heatmap, an anomaly-type
  donut chart, a filterable/sortable/paginated "All Projects" table, AI-style insights,
  and a bottom summary bar.
- **Project Details** (`/project/:id`) — project identity, sanction/vendor information,
  an overall risk gauge, a risk-dimension breakdown, and a "Why Flagged?" panel.

## Data

- `src/mocks/projects.js` holds 145 synthetic projects. State names, MP names,
  constituencies, and allocation-scale figures are seeded from the real MPLADS
  MP-wise allocation dataset you provided (`MP_data.json`); everything under each
  project's `risk` object (scores, flags, reasons) and work-stage/vendor detail is
  synthetic, generated for demonstration only.
- `src/services/api.js` is the only place that touches the mock data. Every function
  is `async` and shaped like a real network call (`getProjects`, `getProjectById`,
  `getStateRiskData`, `getAnomalyDistribution`, `getInsights`, `getSummary`), so
  swapping in a real FastAPI backend later should not require touching any component.

## Notes on a couple of judgment calls

- **Heatmap**: rather than plotting invented project GPS coordinates onto a map,
  `HeatMap.jsx` renders a state-level risk tile grid (color-coded, sortable by score
  or name). This follows the brief's fallback guidance when precise geography isn't
  available.
- **KPI cards vs. table**: the five top-level KPI cards show nationwide illustrative
  figures (matching the scale in your reference image), while the "All Projects"
  table and donut chart are grounded in the actual 145-project synthetic sample —
  this mirrors how a real dashboard would separate national aggregates from a
  working investigation queue.
