const INDIA_STATE_FEATURES = [
  ['IN-AN', 'Andaman and Nicobar Islands', ['Andaman and Nicobar']], ['IN-AP', 'Andhra Pradesh'],
  ['IN-AR', 'Arunachal Pradesh'], ['IN-AS', 'Assam'], ['IN-BR', 'Bihar'], ['IN-CH', 'Chandigarh'],
  ['IN-CT', 'Chhattisgarh', ['Chattisgarh']],
  ['IN-DL', 'Delhi', ['NCT of Delhi', 'National Capital Territory of Delhi', 'New Delhi']],
  ['IN-GA', 'Goa'], ['IN-GJ', 'Gujarat'], ['IN-HR', 'Haryana'], ['IN-HP', 'Himachal Pradesh'],
  ['IN-JK', 'Jammu and Kashmir', ['Jammu & Kashmir']], ['IN-JH', 'Jharkhand'], ['IN-KA', 'Karnataka'],
  ['IN-KL', 'Kerala'], ['IN-LA', 'Ladakh'], ['IN-LD', 'Lakshadweep'], ['IN-MP', 'Madhya Pradesh'],
  ['IN-MH', 'Maharashtra'], ['IN-MN', 'Manipur'], ['IN-ML', 'Meghalaya'], ['IN-MZ', 'Mizoram'],
  ['IN-NL', 'Nagaland'], ['IN-OR', 'Odisha', ['Orissa']], ['IN-PY', 'Puducherry', ['Pondicherry']],
  ['IN-PB', 'Punjab'], ['IN-RJ', 'Rajasthan'], ['IN-SK', 'Sikkim'], ['IN-TN', 'Tamil Nadu'],
  ['IN-TG', 'Telangana'],
  ['IN-DN', 'Dadra and Nagar Haveli and Daman and Diu', [
    'The Dadra And Nagar Haveli And Daman And Diu', 'Dadra and Nagar Haveli', 'Daman and Diu',
  ]],
  ['IN-TR', 'Tripura'], ['IN-UP', 'Uttar Pradesh'], ['IN-UT', 'Uttarakhand', ['Uttaranchal']],
  ['IN-WB', 'West Bengal'],
].map(([id, name, aliases = []]) => ({
  id,
  name,
  aliases,
  mapNames: id === 'IN-DN' ? ['Dadra and Nagar Haveli', 'Daman and Diu'] : [name],
}));

const NEUTRAL_MAP_COLOR = 'rgb(226, 231, 227)';

function normalizeStateName(value) {
  return String(value ?? '').normalize('NFKD').replace(/[\u0300-\u036f]/g, '').toLowerCase()
    .replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, ' ').trim().replace(/^the /, '');
}

const FEATURE_BY_NAME = new Map();
for (const feature of INDIA_STATE_FEATURES) {
  for (const name of [feature.name, ...feature.aliases]) FEATURE_BY_NAME.set(normalizeStateName(name), feature);
}

function finiteNumber(value) {
  if (value === null || value === undefined || value === '') return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

function mix(start, end, amount) {
  const channels = start.map((value, index) => Math.round(value + (end[index] - value) * amount));
  return `rgb(${channels[0]}, ${channels[1]}, ${channels[2]})`;
}

export function scoreToColor(score) {
  const numericScore = finiteNumber(score);
  if (numericScore === null) return NEUTRAL_MAP_COLOR;
  const clamped = Math.max(0, Math.min(100, numericScore));
  if (clamped <= 50) return mix([201, 224, 210], [240, 191, 122], clamped / 50);
  return mix([240, 191, 122], [200, 64, 44], (clamped - 50) / 50);
}

/** Maps aggregate rows to stable SVG feature IDs and reports every unmatched name. */
export function buildIndiaMapModel(data = [], warn = null) {
  const byId = {};
  const byMapName = {};
  const unmatched = [];
  for (const row of Array.isArray(data) ? data : []) {
    const feature = FEATURE_BY_NAME.get(normalizeStateName(row?.state));
    if (!feature) {
      unmatched.push(row?.state ?? null);
      if (warn) warn(`India risk map: unmatched backend state name: ${String(row?.state)}`);
      continue;
    }
    if (byId[feature.id]) {
      if (warn) warn(`India risk map: duplicate aggregate row mapped to ${feature.name}`);
      continue;
    }
    byId[feature.id] = {
      id: feature.id, state: feature.name, backendState: row.state,
      score: finiteNumber(row.score), projectCount: finiteNumber(row.projectCount),
    };
    for (const mapName of feature.mapNames) byMapName[mapName] = byId[feature.id];
  }
  return { features: INDIA_STATE_FEATURES, records: Object.values(byId), byId, byMapName, unmatched };
}

export function sortMapRecords(records, mode = 'score') {
  const sorted = [...records];
  if (mode === 'name') return sorted.sort((a, b) => a.state.localeCompare(b.state));
  return sorted.sort((a, b) => (b.score ?? -Infinity) - (a.score ?? -Infinity));
}

/** Selects a mapped state; useful for mouse, keyboard, and test adapters. */
export function selectMapState(stateId, byId, onSelect) {
  const record = byId?.[stateId] ?? null;
  if (record && onSelect) onSelect(record);
  return record;
}

export { INDIA_STATE_FEATURES, NEUTRAL_MAP_COLOR, normalizeStateName };
