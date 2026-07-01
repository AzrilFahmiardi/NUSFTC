"use client";

import { useMemo, useState } from "react";
import { FlaskConical, RotateCcw } from "lucide-react";
import engine from "@/app/data/compat_engine.json";

const TIER_CLASS = { HIGH: "high", "MID-HIGH": "mid-high", MID: "mid", LOW: "low" };

function tierOf(score) {
  if (score >= engine.tiers.HIGH) return "HIGH";
  if (score >= engine.tiers.MID_HIGH) return "MID-HIGH";
  if (score >= engine.tiers.MID) return "MID";
  return "LOW";
}

function dot(a, b) {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i] * b[i];
  return s;
}

// Average the selected unit vectors, renormalise, then cosine to the anchor.
// This mirrors the screening logic in notebooks/04_predict_variants.py exactly.
function combineScore(vectors) {
  const dim = engine.dim;
  const mean = new Array(dim).fill(0);
  vectors.forEach((v) => {
    for (let i = 0; i < dim; i++) mean[i] += v[i];
  });
  let norm = 0;
  for (let i = 0; i < dim; i++) {
    mean[i] /= vectors.length;
    norm += mean[i] * mean[i];
  }
  norm = Math.sqrt(norm);
  for (let i = 0; i < dim; i++) mean[i] /= norm;
  return dot(mean, engine.anchor);
}

export default function CompatibilityTool() {
  const byName = useMemo(() => Object.fromEntries(engine.nodes.map((n) => [n.name, n])), []);
  const groups = useMemo(() => {
    const order = ["Variant ingredient", "Reference flavour", "Variant C candidate", "Explore"];
    const g = {};
    engine.nodes.forEach((n) => {
      (g[n.group] = g[n.group] || []).push(n);
    });
    return order.filter((k) => g[k]).map((k) => [k, g[k]]);
  }, [byName]);

  const [selected, setSelected] = useState(["fresh_mango", "jasmine_tea"]);

  const toggle = (name) =>
    setSelected((prev) => (prev.includes(name) ? prev.filter((n) => n !== name) : prev.length >= 3 ? prev : [...prev, name]));

  const applyPreset = (names) => setSelected(names.filter((n) => byName[n]));

  const result = useMemo(() => {
    if (selected.length === 0) return null;
    // If the selection exactly matches a known preset, use its stored canonical score.
    const preset = engine.presets.find(
      (p) => p.names.length === selected.length && p.names.every((n) => selected.includes(n))
    );
    if (preset) return { score: preset.score, tier: preset.tier };
    const vectors = selected.map((n) => byName[n].vec);
    const score = combineScore(vectors);
    return { score, tier: tierOf(score) };
  }, [selected, byName]);

  const markerPct = result ? Math.max(0, Math.min(1, result.score)) * 100 : 0;

  return (
    <div className="tool-grid">
      <div>
        <div className="chips" style={{ marginBottom: 16 }}>
          {engine.presets.slice(0, 3).map((p) => (
            <button key={p.label} type="button" className="pick" onClick={() => applyPreset(p.names)}>
              {p.label}
            </button>
          ))}
          <button type="button" className="pick" onClick={() => setSelected([])}>
            <RotateCcw size={13} strokeWidth={2.2} style={{ marginRight: 5, verticalAlign: "-2px" }} />
            Clear
          </button>
        </div>

        <div className="picker">
          {groups.map(([group, items]) => (
            <div className="picker-group" key={group}>
              <div className="picker-group-label">{group}</div>
              <div className="picker-items">
                {items.map((n) => (
                  <button
                    key={n.name}
                    type="button"
                    className={`pick${selected.includes(n.name) ? " selected" : ""}`}
                    onClick={() => toggle(n.name)}
                    aria-pressed={selected.includes(n.name)}
                  >
                    {n.label}
                  </button>
                ))}
              </div>
            </div>
          ))}
        </div>
        <p className="chart-caption">Select up to three ingredients. Molecular pairing-compatibility is the cosine similarity of the combined vector to the consumer-liked anchor. This is a ranking screen, not a liking prediction.</p>
      </div>

      <div className="tool-readout">
        <div className="picker-group-label" style={{ display: "flex", alignItems: "center", gap: 7 }}>
          <FlaskConical size={15} strokeWidth={2.2} /> Compatibility
        </div>
        {result ? (
          <>
            <div className="tool-score">{result.score.toFixed(2)}</div>
            <span className={`tier-badge ${TIER_CLASS[result.tier]}`}>{result.tier} affinity</span>
            <div className="tool-scale">
              <div className="marker" style={{ left: `${markerPct}%` }} />
              <span className="tick" style={{ left: "35%" }}>0.35</span>
              <span className="tick" style={{ left: "50%" }}>0.50</span>
              <span className="tick" style={{ left: "70%" }}>0.70</span>
            </div>
            <p className="chart-caption" style={{ marginTop: 18 }}>
              {selected.map((n) => byName[n].label).join(" + ")}
            </p>
          </>
        ) : (
          <p className="jbody" style={{ marginTop: 10 }}>Select one or more ingredients to compute a molecular compatibility score.</p>
        )}
      </div>
    </div>
  );
}
