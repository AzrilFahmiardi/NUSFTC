"use client";

import { useState } from "react";
import consumer from "@/app/data/consumer.json";
import DivergingBar from "@/components/charts/DivergingBar";
import GroupedBar from "@/components/charts/GroupedBar";
import Reveal from "@/components/visual/Reveal";

const toFlavor = (rows) => rows.map((r) => ({ flavor: r.label, pos: r.pos, neg: r.neg, net: r.net, mentions: r.mentions }));

export default function InsightsPage() {
  const [market, setMarket] = useState("EN");
  const isEN = market === "EN";
  const flavors = isEN ? consumer.flavorsEN : consumer.flavorsZH;
  const pains = isEN ? consumer.painsEN : consumer.painsZH;

  return (
    <>
      <section className="jsection">
        <p className="section-eyebrow">What the data reveals</p>
        <h1 className="jtitle">The insights the engine surfaced</h1>
        <p className="jlead">
          Processed across both markets, the corpus produces a clear brief. A small set of flavours dominates positive
          sentiment, the pain signal is complementary between markets, and the consumer segments hold across languages.
          These are the signals the molecular layer then acts on.
        </p>
      </section>

      <Reveal>
        <section className="jsection" data-tour="flavors">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
            <h2 className="jsubhead" style={{ margin: 0 }}>Flavour preferences and pain points</h2>
            <div className="market-toggle" role="tablist" aria-label="Market" data-tour="market">
              <button className={isEN ? "active" : ""} onClick={() => setMarket("EN")} role="tab" aria-selected={isEN}>Twitter (EN)</button>
              <button className={!isEN ? "active" : ""} onClick={() => setMarket("ZH")} role="tab" aria-selected={!isEN}>China (ZH)</button>
            </div>
          </div>
          <div className="jgrid cols-2" style={{ marginTop: 16 }}>
            <div>
              <DivergingBar data={toFlavor(flavors)} height={430} />
              <p className="chart-caption">
                {isEN
                  ? "English flavour preference by net sentiment. Mango leads, followed by vanilla, caramel, coconut, and milk tea."
                  : "Chinese flavour preference by net sentiment, strongly positive on Xiaohongshu. Milk tea, coconut, mango, and jasmine all carry real volume."}
              </p>
            </div>
            <div>
              <DivergingBar data={toFlavor(pains)} height={430} />
              <p className="chart-caption">
                {isEN
                  ? "English pain points are led by chalky and gritty texture. Texture is the dominant complaint."
                  : "Chinese pain points are led by an off or beany smell, then price and over-sweetness. Aroma leads here, not texture."}
              </p>
            </div>
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="jsection" data-tour="crossmarket">
          <h2 className="jsubhead">Cross-market reading</h2>
          <p className="jbody">
            Read together, the two markets give a clearer brief than either alone. Mango, coconut, milk tea, and matcha are
            positive in both, which is what gives confidence that the flavour direction is not a local artefact. The pain
            signal is complementary: English foregrounds texture, China foregrounds aroma, so the combined corpus describes
            the full surface of the protein off-note problem.
          </p>
          <div className="jgrid cols-2" style={{ marginTop: 16 }}>
            <div>
              <GroupedBar
                rows={consumer.crossMarket}
                catKey="flavor"
                axisName="Net sentiment (%)"
                min={-100}
                max={100}
                height={420}
                series={[
                  { name: "Twitter (EN)", key: "en", color: "#d9bd79" },
                  { name: "XHS China (ZH)", key: "zh", color: "#8bb391" },
                ]}
              />
              <p className="chart-caption">Flavours positive in both markets define the MoBai flavour territory.</p>
            </div>
            <div>
              <GroupedBar
                rows={consumer.competitorsZH}
                catKey="label"
                axisName="Net sentiment (%)"
                min={0}
                max={100}
                height={420}
                series={[{ name: "China brand sentiment", key: "net", color: "#9bc0cf" }]}
              />
              <p className="chart-caption">
                China competitor sentiment. Master Kong appears in the conversation with positive sentiment, relevant to
                the brief emphasis on Master Kong leverage.
              </p>
            </div>
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="jsection" data-tour="segments">
          <h2 className="jsubhead">Consumer segmentation</h2>
          <p className="jbody">
            Segmentation runs on the joint bilingual corpus, so consumer types are defined by behaviour rather than by
            language. Both segments draw from both markets, confirming genuine cross-market consumer types rather than a
            language split.
          </p>
          <div className="card" style={{ marginTop: 14 }}>
            <table className="data-table">
              <thead>
                <tr><th>Share</th><th>Leading flavour</th><th>Leading pain</th><th>Occasion</th><th>Source mix (China / Twitter)</th></tr>
              </thead>
              <tbody>
                {consumer.segmentsJoint.map((s, i) => (
                  <tr key={i}>
                    <td><strong>{s.pct}%</strong></td><td>{s.flavor}</td><td>{s.pain}</td><td>{s.occasion}</td><td>{s.china}% / {s.twitter}%</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </Reveal>
    </>
  );
}
