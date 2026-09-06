import test from 'node:test';
import assert from 'node:assert/strict';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import IndiaMap from '@react-map/india';
import { buildIndiaMapModel, scoreToColor, selectMapState, sortMapRecords } from './heatMapModel.js';
import { INDIA_MAP_CALLOUT_IDS, INDIA_MAP_LABELS, getMapLabelByFeatureId } from './heatMapLabels.js';

const backendRows = [
  { state: 'Odisha', score: 44.35, projectCount: 9842 },
  { state: 'NCT of Delhi', score: 67.5, projectCount: 120 },
  { state: 'The Dadra And Nagar Haveli And Daman And Diu', score: 12, projectCount: 9 },
];

test('map model renders backend values on known India features', () => {
  const model = buildIndiaMapModel(backendRows);
  assert.equal(model.features.length, 36);
  assert.deepEqual(model.byId['IN-OR'], { id: 'IN-OR', state: 'Odisha', backendState: 'Odisha', score: 44.35, projectCount: 9842 });
  assert.equal(model.byId['IN-DL'].score, 67.5);
  assert.equal(scoreToColor(44.35), 'rgb(236, 195, 132)');
});

test('every current state and union territory maps to a boundary in the SVG', () => {
  const model = buildIndiaMapModel();
  assert.equal(model.features.length, 36);
  const svg = renderToStaticMarkup(React.createElement(IndiaMap.default ?? IndiaMap, { type: 'select-single' }));
  for (const feature of model.features) {
    for (const mapName of feature.mapNames) assert.equal(svg.includes(`id="${mapName}-`), true, mapName);
  }
  assert.match(svg, /id="Ladakh-/);
});

test('all state names currently emitted by the backend aggregate map cleanly', () => {
  const backendStateNames = [
    'Andaman And Nicobar Islands', 'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chandigarh',
    'Chhattisgarh', 'Delhi', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jammu And Kashmir',
    'Jharkhand', 'Karnataka', 'Kerala', 'Ladakh', 'Lakshadweep', 'Madhya Pradesh', 'Maharashtra',
    'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Puducherry', 'Punjab', 'Rajasthan',
    'Sikkim', 'Tamil Nadu', 'Telangana', 'The Dadra And Nagar Haveli And Daman And Diu', 'Tripura',
    'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
  ];
  const model = buildIndiaMapModel(backendStateNames.map((state) => ({ state, score: 1, projectCount: 1 })));
  assert.equal(model.records.length, 36);
  assert.deepEqual(model.unmatched, []);
});

test('label model contains exactly one readable label for all 36 states and union territories', () => {
  assert.equal(INDIA_MAP_LABELS.length, 36);
  assert.equal(new Set(INDIA_MAP_LABELS.map((label) => label.id)).size, 36);
  for (const label of INDIA_MAP_LABELS) {
    assert.ok(label.name);
    assert.ok(label.lines.join(' ').trim());
  }
});

test('every mapped geographic feature resolves to a display label', () => {
  const { features } = buildIndiaMapModel();
  for (const feature of features) assert.equal(getMapLabelByFeatureId(feature.id)?.name, feature.name, feature.id);
});

test('small and narrow regions resolve to configured callouts and leader targets', () => {
  const expectedCallouts = ['IN-DL', 'IN-CH', 'IN-PY', 'IN-GA', 'IN-SK', 'IN-TR', 'IN-MN', 'IN-MZ', 'IN-NL', 'IN-ML', 'IN-AN', 'IN-LD', 'IN-DN'];
  assert.deepEqual([...INDIA_MAP_CALLOUT_IDS].sort(), expectedCallouts.sort());
  for (const id of expectedCallouts) {
    const label = getMapLabelByFeatureId(id);
    assert.equal(label.callout, true);
    assert.ok(label.targets.length > 0);
  }
});

test('aliases and the merged union territory map to current feature IDs', () => {
  const model = buildIndiaMapModel(backendRows);
  assert.equal(model.byId['IN-DL'].state, 'Delhi');
  assert.equal(model.byId['IN-DN'].projectCount, 9);
});

test('unmatched and missing rows do not crash and are reported', () => {
  const warnings = [];
  const model = buildIndiaMapModel([{ state: 'Unknown Region', score: 5 }, null], (message) => warnings.push(message));
  assert.deepEqual(model.unmatched, ['Unknown Region', null]);
  assert.equal(model.records.length, 0);
  assert.equal(warnings.length, 2);
  assert.equal(scoreToColor(null), 'rgb(226, 231, 227)');
});

test('state click adapter selects the correct backend state and detail values', () => {
  const model = buildIndiaMapModel(backendRows);
  let selected = null;
  const detail = selectMapState('IN-OR', model.byId, (record) => { selected = record; });
  assert.equal(selected.backendState, 'Odisha');
  assert.equal(detail.score, 44.35);
  assert.equal(detail.projectCount, 9842);
  assert.equal(selectMapState('IN-XX', model.byId, () => assert.fail()), null);
});

test('risk-score and state sorting remain available', () => {
  const records = buildIndiaMapModel(backendRows).records;
  assert.equal(sortMapRecords(records, 'score')[0].state, 'Delhi');
  assert.equal(sortMapRecords(records, 'name')[0].state, 'Dadra and Nagar Haveli and Daman and Diu');
});
