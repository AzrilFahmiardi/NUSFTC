"use client";

import molecular from "@/app/data/molecular.json";
import FlavorGraphExplorer from "@/components/FlavorGraphExplorer";
import CompatibilityTool from "@/components/CompatibilityTool";
import { ArrowDown } from "lucide-react";
import TierBar from "@/components/charts/TierBar";
import Reveal from "@/components/visual/Reveal";

const LAYERS = [
  { cls: "l1", name: "Consumer Voice", meta: "VADER, TextBlob, TF-IDF, K-Means. Input: consumer posts. Output: net sentiment per flavour, segments, pain points." },
  { cls: "l2", name: "Molecular AI (FlavorGraph)", meta: "metapath2vec on 8,298 nodes and 147,179 edges (Park et al., 2021). Output: a 300-dim embedding per node." },
  { cls: "l3", name: "Pairing-Compatibility Recommender", meta: "Cosine similarity to a consumer-liked anchor. Output: compatibility ranking and a human-testable shortlist." },
  { cls: "l4", name: "Product Science", meta: "Five-mechanism off-note masking. Input: the shortlisted variants. Output: the MoBai formulation." },
];

const G = molecular.graph;
const STATS = [
  { label: "Graph nodes", value: G.nodes.toLocaleString(), sub: `${G.ingredients.toLocaleString()} ingredients + ${G.compounds.toLocaleString()} compounds` },
  { label: "Edges", value: G.edges.toLocaleString(), sub: "molecular co-occurrence relationships" },
  { label: "Embedding", value: `${G.dim}-dim`, sub: `${G.embedded.toLocaleString()} nodes with vectors` },
  { label: "Screened for Variant C", value: G.screened.toLocaleString(), sub: "candidate ingredient nodes" },
];

function pick(sub) {
  return molecular.variants.find((v) => v.label.includes(sub));
}
const COMPAT_ITEMS = [
  { label: "Variant B: Coconut x Milk Tea", src: "Coconut × Milk Tea" },
  { label: "Variant B: full product", src: "Variant B · Full" },
  { label: "Variant A: Mango x Jasmine", src: "food node" },
  { label: "Variant A: full product", src: "Variant A · Full" },
  { label: "Mango alone", src: "Mango alone" },
  { label: "Vanilla alone", src: "Vanilla alone" },
  { label: "Strawberry (low baseline)", src: "Strawberry alone" },
]
  .map((it) => {
    const v = pick(it.src);
    return v ? { label: it.label, score: v.score, tier: v.tier } : null;
  })
  .filter(Boolean);

const VARIANT_C = molecular.variantC.map((c) => ({ label: c.name, score: c.score, tier: c.tier }));

export default function MolecularPage() {
  return (
    <>
      <section className="jsection">
        <p className="section-eyebrow">FlavorGraph screening</p>
        <h1 className="jtitle">Screening for molecularly compatible flavours</h1>
        <p className="jlead">
          The molecular layer maps consumer-preferred flavours into an embedding space and ranks candidate pairings by how
          compatible they are with the flavours consumers already like. It does not re-discover consumer preferences; it
          amplifies them, narrowing thousands of molecular candidates to a small, human-testable shortlist.
        </p>
      </section>

      <Reveal>
        <section className="jsection" data-tour="arch">
          <h2 className="jsubhead">Pipeline architecture</h2>
          <div className="arch">
            {LAYERS.map((l, i) => (
              <div key={l.cls}>
                <div className={`arch-layer ${l.cls}`}>
                  <span className="lname">{l.name}</span>
                  <span className="lmeta">{l.meta}</span>
                </div>
                {i < LAYERS.length - 1 && (
                  <div className="arch-arrow"><span className="arch-arrow-badge"><ArrowDown size={16} strokeWidth={2.6} aria-hidden="true" /></span></div>
                )}
              </div>
            ))}
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="jsection">
          <h2 className="jsubhead">FlavorGraph knowledge graph</h2>
          <div className="jgrid cols-4" data-tour="graph">
            {STATS.map((s) => (
              <div className="stat card glow" key={s.label}>
                <span className="label">{s.label}</span>
                <span className="value">{s.value}</span>
                <span className="sub">{s.sub}</span>
              </div>
            ))}
          </div>
          <p className="chart-caption">
            For MoBai, thirteen target flavour nodes were mapped to the graph. Oolong and osmanthus are absent from the
            vocabulary, so the milk-tea profile in Variant B uses black tea and milk as a proxy, noted as a known limitation.
          </p>
        </section>
      </Reveal>

      <Reveal>
        <section className="jsection">
          <h2 className="jsubhead">Explore the molecular graph</h2>
          <p className="jbody">Click any node. Ingredients link to their representative aroma compounds; compounds that share chemical families link to each other.</p>
          <div style={{ marginTop: 14 }} data-tour="explorer">
            <FlavorGraphExplorer />
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="jsection" data-tour="compat">
          <h2 className="jsubhead">Variant compatibility</h2>
          <p className="jbody">
            Both primary variants sit in the HIGH affinity tier and are well separated from the strawberry baseline,
            confirming the screen discriminates as intended. These two variants are the first outputs of the screen, not
            its limit. The dashed line marks the mean compatibility of the thirteen consumer flavours.
          </p>
          <div style={{ marginTop: 14 }}>
            <TierBar items={COMPAT_ITEMS} refLine={molecular.meanOf13} refLabel={`mean of 13 flavours (${molecular.meanOf13})`} max={0.9} height={360} />
          </div>
          <div className="jgrid cols-4" style={{ marginTop: 16 }}>
            {molecular.tiers.map((t) => (
              <div className="stat" key={t.tier}>
                <span className="label">{t.tier}</span>
                <span className="value" style={{ fontSize: "1.1rem" }}>{t.range}</span>
                <span className="sub">{t.interp}</span>
              </div>
            ))}
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="jsection" data-tour="tool">
          <h2 className="jsubhead">Live compatibility check</h2>
          <p className="jbody">
            Pick ingredients and the score is computed in your browser as cosine similarity to the consumer-liked anchor,
            the same logic used to score the variants. This is a molecular compatibility ranking, not a liking prediction.
          </p>
          <div style={{ marginTop: 14 }}>
            <CompatibilityTool />
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="jsection" data-tour="variantc">
          <h2 className="jsubhead">Variant C discovery</h2>
          <p className="jbody">
            Beyond confirming the two primary variants, the recommender screened the full ingredient vocabulary for a third
            candidate. Crushed pineapple ranked first at {molecular.variantC[0].score.toFixed(2)} in the MID-HIGH tier. It was
            not part of the anchor, so this is a genuine generalisation of the engine to a flavour it was never calibrated on.
          </p>
          <div style={{ marginTop: 14 }}>
            <TierBar items={VARIANT_C} max={0.75} height={380} />
          </div>
          <div className="note" style={{ marginTop: 18 }}>
            <strong>Transparency.</strong> The in-sample correlation between compatibility and the consumer sentiment used to
            build the anchor is Pearson {molecular.pearsonInSample}. Because the anchor is built from the same flavours it is
            correlated against, this is a descriptive consistency figure, not an out-of-sample predictive claim. Liking is
            validated separately by the consumer survey in the next stage.
          </div>
        </section>
      </Reveal>
    </>
  );
}
