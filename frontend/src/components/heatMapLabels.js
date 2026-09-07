/**
 * Presentation-only label layout for the India SVG.
 * Coordinates are percentages of the rendered map viewBox and are deliberately
 * separate from backend name normalization and risk data mapping.
 */
export const INDIA_MAP_LABELS = [
  { id: 'IN-AN', name: 'Andaman and Nicobar Islands', lines: ['Andaman &', 'Nicobar'], x: 96, y: 87, callout: true, targets: [[85, 86]] },
  { id: 'IN-AP', name: 'Andhra Pradesh', lines: ['Andhra', 'Pradesh'], x: 44, y: 72 },
  { id: 'IN-AR', name: 'Arunachal Pradesh', lines: ['Arunachal', 'Pradesh'], x: 89, y: 28 },
  { id: 'IN-AS', name: 'Assam', lines: ['Assam'], x: 83, y: 35 },
  { id: 'IN-BR', name: 'Bihar', lines: ['Bihar'], x: 59, y: 36 },
  { id: 'IN-CH', name: 'Chandigarh', lines: ['Chandigarh'], x: 10, y: 20, callout: true, targets: [[29.3, 20.9]] },
  { id: 'IN-CT', name: 'Chhattisgarh', lines: ['Chhattisgarh'], x: 48, y: 53 },
  { id: 'IN-DL', name: 'Delhi', lines: ['Delhi'], x: 16, y: 27, callout: true, targets: [[30.5, 27.7]] },
  { id: 'IN-GA', name: 'Goa', lines: ['Goa'], x: 10, y: 72, callout: true, targets: [[19.9, 71.6]] },
  { id: 'IN-GJ', name: 'Gujarat', lines: ['Gujarat'], x: 10.5, y: 47 },
  { id: 'IN-HR', name: 'Haryana', lines: ['Haryana'], x: 25.5, y: 25 },
  { id: 'IN-HP', name: 'Himachal Pradesh', lines: ['Himachal', 'Pradesh'], x: 32, y: 16.5 },
  { id: 'IN-JK', name: 'Jammu and Kashmir', lines: ['Jammu &', 'Kashmir'], x: 21.5, y: 12 },
  { id: 'IN-JH', name: 'Jharkhand', lines: ['Jharkhand'], x: 59, y: 44 },
  { id: 'IN-KA', name: 'Karnataka', lines: ['Karnataka'], x: 28, y: 73 },
  { id: 'IN-KL', name: 'Kerala', lines: ['Kerala'], x: 27, y: 88 },
  { id: 'IN-LA', name: 'Ladakh', lines: ['Ladakh'], x: 31, y: 6.5 },
  { id: 'IN-LD', name: 'Lakshadweep', lines: ['Lakshadweep'], x: 2, y: 89, anchor: 'start', callout: true, targets: [[16.1, 89.3]] },
  { id: 'IN-MP', name: 'Madhya Pradesh', lines: ['Madhya', 'Pradesh'], x: 35, y: 43 },
  { id: 'IN-MH', name: 'Maharashtra', lines: ['Maharashtra'], x: 29, y: 59 },
  { id: 'IN-MN', name: 'Manipur', lines: ['Manipur'], x: 98, y: 41, anchor: 'end', callout: true, targets: [[87.8, 40.5]] },
  { id: 'IN-ML', name: 'Meghalaya', lines: ['Meghalaya'], x: 70, y: 40.5, callout: true, targets: [[79.1, 37.9]] },
  { id: 'IN-MZ', name: 'Mizoram', lines: ['Mizoram'], x: 96, y: 49, anchor: 'end', callout: true, targets: [[84.4, 45.6]] },
  { id: 'IN-NL', name: 'Nagaland', lines: ['Nagaland'], x: 98, y: 34, anchor: 'end', callout: true, targets: [[89.3, 36.1]] },
  { id: 'IN-OR', name: 'Odisha', lines: ['Odisha'], x: 56, y: 56 },
  { id: 'IN-PY', name: 'Puducherry', lines: ['Puducherry'], x: 49, y: 90, callout: true, targets: [[40.5, 86]] },
  { id: 'IN-PB', name: 'Punjab', lines: ['Punjab'], x: 24, y: 20 },
  { id: 'IN-RJ', name: 'Rajasthan', lines: ['Rajasthan'], x: 18, y: 35 },
  { id: 'IN-SK', name: 'Sikkim', lines: ['Sikkim'], x: 64, y: 28, callout: true, targets: [[69.4, 31.2]] },
  { id: 'IN-TN', name: 'Tamil Nadu', lines: ['Tamil', 'Nadu'], x: 35, y: 87 },
  { id: 'IN-TG', name: 'Telangana', lines: ['Telangana'], x: 39, y: 63 },
  { id: 'IN-DN', name: 'Dadra and Nagar Haveli and Daman and Diu', lines: ['Dadra & Nagar Haveli', 'Daman & Diu'], x: 2, y: 58, anchor: 'start', callout: true, targets: [[16.7, 55.6], [8.9, 53.5]] },
  { id: 'IN-TR', name: 'Tripura', lines: ['Tripura'], x: 73, y: 51, callout: true, targets: [[80.6, 43.9]] },
  { id: 'IN-UP', name: 'Uttar Pradesh', lines: ['Uttar', 'Pradesh'], x: 44, y: 32 },
  { id: 'IN-UT', name: 'Uttarakhand', lines: ['Uttarakhand'], x: 39, y: 22 },
  { id: 'IN-WB', name: 'West Bengal', lines: ['West', 'Bengal'], x: 67, y: 45 },
];

const LABEL_BY_ID = Object.fromEntries(INDIA_MAP_LABELS.map((label) => [label.id, label]));

export function getMapLabelByFeatureId(featureId) {
  return LABEL_BY_ID[featureId] ?? null;
}

export const INDIA_MAP_CALLOUT_IDS = INDIA_MAP_LABELS.filter((label) => label.callout).map((label) => label.id);
