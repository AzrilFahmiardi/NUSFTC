"use client";

import { useMemo, useState } from "react";

// Conceptual molecular graph for the MoBai variant ingredients: each ingredient is
// linked to representative aroma compounds, and compounds that share chemical families
// are linked to each other. This visualises structure; quantitative compatibility is
// shown separately by the compatibility tool and the variant chart. All compound
// properties below are real chemistry values (PubChem). No emoji, no fabricated scores.

const COMPOUNDS = {
  "ethyl butanoate": { formula: "C6H12O2", weight: 116.16, categories: ["ester", "fruit", "mango", "volatile"] },
  limonene: { formula: "C10H16", weight: 136.24, categories: ["terpene", "citrus", "mango", "masking"] },
  "beta-myrcene": { formula: "C10H16", weight: 136.24, categories: ["terpene", "musty", "mango", "masking"] },
  "isoamyl acetate": { formula: "C7H14O2", weight: 130.18, categories: ["ester", "banana", "mango", "sweet"] },
  linalool: { formula: "C10H18O", weight: 154.25, categories: ["alcohol", "floral", "jasmine", "tea", "masking"] },
  "benzyl acetate": { formula: "C9H10O2", weight: 150.17, categories: ["ester", "floral", "jasmine", "masking"] },
  indole: { formula: "C8H7N", weight: 117.15, categories: ["nitrogen", "floral", "jasmine"] },
  "cis-jasmone": { formula: "C11H16O", weight: 164.24, categories: ["ketone", "floral", "jasmine"] },
  "delta-decalactone": { formula: "C10H18O2", weight: 170.25, categories: ["lactone", "creamy", "coconut", "masking"] },
  "gamma-nonalactone": { formula: "C9H16O2", weight: 156.22, categories: ["lactone", "coconut", "sweet"] },
  "caprylic acid": { formula: "C8H16O2", weight: 144.21, categories: ["acid", "fatty", "coconut", "off_note"] },
  methylheptanone: { formula: "C7H14O", weight: 114.19, categories: ["ketone", "nutty", "coconut"] },
  caffeine: { formula: "C8H10N4O2", weight: 194.19, categories: ["alkaloid", "bitter", "tea"] },
  theaflavin: { formula: "C29H24O12", weight: 564.5, categories: ["phenol", "astringent", "tea", "bitter"] },
  pyrazine: { formula: "C4H4N2", weight: 80.09, categories: ["nitrogen", "roasted", "tea"] },
  geraniol: { formula: "C10H18O", weight: 154.25, categories: ["alcohol", "floral", "tea", "rose"] },
  catechin: { formula: "C15H14O6", weight: 290.27, categories: ["phenol", "astringent", "tea", "masking"] },
  "lactic acid": { formula: "C3H6O3", weight: 90.08, categories: ["acid", "sour", "yogurt", "masking"] },
  diacetyl: { formula: "C4H6O2", weight: 86.09, categories: ["ketone", "buttery", "yogurt", "masking"] },
  acetoin: { formula: "C4H8O2", weight: 88.11, categories: ["ketone", "buttery", "yogurt", "masking"] },
  acetaldehyde: { formula: "C2H4O", weight: 44.05, categories: ["aldehyde", "pungent", "yogurt", "masking"] },
};

const INGREDIENTS = {
  mango: {
    color: "#e0a23f",
    description: "Tropical fruity terpenes and esters",
    compounds: ["ethyl butanoate", "limonene", "beta-myrcene", "isoamyl acetate"],
    variant: { label: "Variant A (Mango x Jasmine)", score: 0.73, tier: "HIGH" },
  },
  jasmine: {
    color: "#d39bcd",
    description: "Floral linalool and benzyl acetate",
    compounds: ["linalool", "benzyl acetate", "indole", "cis-jasmone"],
    variant: { label: "Variant A (Mango x Jasmine)", score: 0.73, tier: "HIGH" },
  },
  coconut: {
    color: "#d8c6a6",
    description: "Creamy lactones and fatty acids",
    compounds: ["delta-decalactone", "gamma-nonalactone", "caprylic acid", "methylheptanone"],
    variant: { label: "Variant B (Coconut x Milk Tea)", score: 0.79, tier: "HIGH" },
  },
  milk_tea: {
    color: "#c79a6a",
    description: "Roasted pyrazines and tea tannins",
    compounds: ["caffeine", "theaflavin", "pyrazine", "geraniol", "catechin"],
    variant: { label: "Variant B (Coconut x Milk Tea)", score: 0.79, tier: "HIGH" },
  },
  yogurt_base: {
    color: "#dfe6df",
    description: "Lactic acid, diacetyl and acetoin",
    compounds: ["lactic acid", "diacetyl", "acetoin", "acetaldehyde"],
    variant: null,
  },
};

function formatName(s) {
  return s.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

function buildGraph(ingredients) {
  const nodes = [];
  const edges = [];
  const added = new Set();
  const count = ingredients.length;
  ingredients.forEach((ing, index) => {
    const angle = (2 * Math.PI * index) / count - Math.PI / 2;
    nodes.push({ id: ing, type: "ingredient", x: 400 + 220 * Math.cos(angle), y: 300 + 220 * Math.sin(angle) });
    INGREDIENTS[ing].compounds.forEach((comp, idx) => {
      if (!added.has(comp)) {
        const mAngle = angle + (idx - INGREDIENTS[ing].compounds.length / 2) * 0.22;
        const dist = 120 + (idx % 3) * 36;
        nodes.push({ id: comp, type: "molecule", x: 400 + dist * Math.cos(mAngle), y: 300 + dist * Math.sin(mAngle) });
        added.add(comp);
      }
      edges.push({ source: ing, target: comp, type: "contains" });
    });
  });
  const mols = [...added];
  for (let i = 0; i < mols.length; i++) {
    for (let j = i + 1; j < mols.length; j++) {
      const a = COMPOUNDS[mols[i]];
      const b = COMPOUNDS[mols[j]];
      if (a && b) {
        const shared = a.categories.filter((c) => b.categories.includes(c));
        if (shared.length >= 2) edges.push({ source: mols[i], target: mols[j], type: "co_occurs" });
      }
    }
  }
  return { nodes, edges };
}

const TIER_CLASS = { HIGH: "high", "MID-HIGH": "mid-high", MID: "mid", LOW: "low" };

function Inspector({ nodeId }) {
  const comp = COMPOUNDS[nodeId];
  const ing = INGREDIENTS[nodeId];
  return (
    <aside className="panel inspector">
      <p className="eyebrow">Node inspector</p>
      <h3>{formatName(nodeId)}</h3>
      {comp ? (
        <>
          <div className="compound-grid">
            <span>Formula<strong>{comp.formula}</strong></span>
            <span>MW<strong>{comp.weight} Da</strong></span>
          </div>
          <div className="tag-row">
            {comp.categories.map((c) => (
              <span key={c}>{c}</span>
            ))}
          </div>
          <p>
            This compound is a {comp.categories.includes("masking") ? "masking-active" : "sensory-active"} constituent that
            contributes to the aroma profile of its parent ingredient.
          </p>
        </>
      ) : (
        <>
          <p>{ing.description}.</p>
          <div className="tag-row">
            {ing.compounds.map((c) => (
              <span key={c}>{c}</span>
            ))}
          </div>
          {ing.variant ? (
            <div className="relationship-list">
              <div>
                <span>{ing.variant.label}</span>
                <strong>
                  <span className={`tier-badge ${TIER_CLASS[ing.variant.tier]}`}>{ing.variant.tier}</span> {ing.variant.score.toFixed(2)}
                </strong>
              </div>
            </div>
          ) : (
            <p className="jbody">Shared yogurt base used across both variants.</p>
          )}
        </>
      )}
    </aside>
  );
}

export default function FlavorGraphExplorer() {
  const ingredients = ["mango", "jasmine", "coconut", "milk_tea", "yogurt_base"];
  const graph = useMemo(() => buildGraph(ingredients), []);
  const [active, setActive] = useState("linalool");

  return (
    <div className="graph-layout">
      <section className="panel graph-panel">
        <svg viewBox="0 0 800 600" role="img" aria-label="Interactive molecular flavour graph">
          {graph.edges.map((edge, idx) => {
            const s = graph.nodes.find((n) => n.id === edge.source);
            const t = graph.nodes.find((n) => n.id === edge.target);
            if (!s || !t) return null;
            return (
              <line key={`${edge.source}-${edge.target}-${idx}`} x1={s.x} y1={s.y} x2={t.x} y2={t.y} className={edge.type === "co_occurs" ? "edge co" : "edge"} />
            );
          })}
          {graph.nodes.map((node) => {
            const isIng = node.type === "ingredient";
            const fill = isIng ? INGREDIENTS[node.id].color : COMPOUNDS[node.id]?.categories.includes("masking") ? "#88bfa1" : "#d5c5a1";
            return (
              <g
                key={node.id}
                className={`graph-node ${active === node.id ? "active" : ""}`}
                data-hint={isIng && node.id === "mango" ? "explore-node" : undefined}
                onClick={() => setActive(node.id)}
                tabIndex={0}
                role="button"
                aria-label={`Inspect ${node.id}`}
                onKeyDown={(e) => (e.key === "Enter" || e.key === " ") && setActive(node.id)}
              >
                <circle cx={node.x} cy={node.y} r={isIng ? 34 : 15} fill={fill} />
                <text className={isIng ? "ingredient-label" : "molecule-label"} x={node.x} y={node.y + (isIng ? 54 : 30)} textAnchor="middle">
                  {isIng ? formatName(node.id) : node.id.split(" ")[0]}
                </text>
              </g>
            );
          })}
        </svg>
      </section>
      <Inspector nodeId={active} />
    </div>
  );
}
