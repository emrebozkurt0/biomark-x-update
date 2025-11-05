import React from 'react';

const Chip = ({ children, color = '#e8eefc', textColor = '#2f4fb5' }) => (
  <span
    style={{
      display: 'inline-block',
      padding: '2px 8px',
      borderRadius: '999px',
      background: color,
      color: textColor,
      fontWeight: 700,
      fontSize: 12,
      marginRight: 8,
      whiteSpace: 'nowrap'
    }}
  >
    {children}
  </span>
);

export default function AggregationHelpContent() {
  return (
    <div style={{ fontSize: 13.5, lineHeight: 1.6 }}>
      <div style={{ fontWeight: 700, marginBottom: 6 }}>Aggregation methods</div>
      <div style={{ color: '#444', marginBottom: 10 }}>
        Merge multiple ranked biomarker lists into one consensus list (Top‑N).
      </div>

      <ul style={{ paddingLeft: 16, margin: 0, listStyle: 'none' }}>
        <li style={{ marginBottom: 8 }}>
          <Chip color="#efe7ff" textColor="#5c2fb5">Reciprocal Rank Fusion (RRF)</Chip>
          Robust default. Rewards features that appear near the top across lists; parameter <b>k</b> controls how quickly lower ranks are discounted.
        </li>
        <li style={{ marginBottom: 8 }}>
          <Chip color="#e7fbf6" textColor="#0f8a6a">Rank Product</Chip>
          Uses the geometric mean of ranks; highlights consistently high‑ranking features; less affected by a single extreme list.
        </li>
        <li style={{ marginBottom: 8 }}>
          <Chip color="#fff3e1" textColor="#b55a00">Weighted Borda Count</Chip>
          Sums ranks with optional <b>weights</b>; give higher weight to methods you trust more (e.g., SHAP &gt; t‑test).
        </li>
        <li style={{ marginBottom: 4 }}>
          <Chip color="#eef2f7" textColor="#334155">Simple Sum</Chip>
          Adds ranks equally; easy to interpret but a bit more sensitive to outliers and number of lists.
        </li>
      </ul>

      <div style={{ marginTop: 10, background: '#f7fbff', border: '1px solid #e1efff', borderRadius: 8, padding: '8px 10px' }}>
        <div style={{ fontWeight: 700, color: '#2f4fb5', marginBottom: 4 }}>Tips</div>
        <ul style={{ paddingLeft: 18, margin: 0 }}>
          <li>Start with <b>RRF</b> for a balanced choice.</li>
          <li>Use <b>Weighted Borda</b> to prioritize specific methods via weights.</li>
          <li>Compare Top‑N lists across methods to check stability.</li>
        </ul>
      </div>
    </div>
  );
}
