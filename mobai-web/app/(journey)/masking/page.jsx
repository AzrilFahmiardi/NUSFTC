"use client";

import { Package, Flame, Droplets, Sprout, Leaf } from "lucide-react";
import bitter from "@/app/data/bitter_risk.json";
import BitterScatter from "@/components/charts/BitterScatter";

const MECHANISMS = [
  { icon: Package, title: "Cyclic oligosaccharide encapsulation", body: "Beta-cyclodextrin physically captures volatile off-note compounds within a molecular cavity, reducing the off-aroma at the receptors and directly addressing the off-smell complaint prominent in China." },
  { icon: Flame, title: "Maillard reaction flavour masking", body: "A controlled heat-induced reaction generates roasted and caramel notes that shift the flavour foreground away from protein off-notes." },
  { icon: Droplets, title: "Acidity and pH modulation", body: "Mild acidification suppresses the bitter and astringent perceptions associated with protein hydrolysates." },
  { icon: Sprout, title: "Probiotic-driven fermentation", body: "Fermentation with a documented probiotic strain contributes dairy-fresh notes that mask chalky and metallic perceptions, addressing the texture complaint prominent in the English market." },
  { icon: Leaf, title: "Tea-polyphenol matrix interaction", body: "Polyphenols from the tea base bind protein molecules, reducing the free protein available to generate off-notes while contributing a controlled level of astringency." },
];

export default function MaskingPage() {
  return (
    <>
      <section className="jsection">
        <p className="section-eyebrow">Bitter-risk and masking</p>
        <h1 className="jtitle">Targeting the compounds behind protein off-notes</h1>
        <p className="jlead">
          High-protein beverages generate off-notes from their amino-acid content. A supervised classifier encodes each
          constituent as a molecular fingerprint and predicts a bitter-risk probability for every compound in the MoBai
          flavour universe. This points masking effort at the right targets; it does not predict consumer liking.
        </p>
      </section>

      <section className="jsection" data-tour="bitter">
        <h2 className="jsubhead">Bitter-risk screen</h2>
        <BitterScatter points={bitter.points} threshold={bitter.threshold} top={bitter.top} height={460} />
        <p className="chart-caption">
          Each point is a compound positioned by molecular weight and predicted bitter probability across {bitter.total}
          {" "}compounds. Points above the threshold are flagged as bitter-risk. The branched-chain and aromatic amino acids
          dominate, consistent with the food-science literature on protein bitterness.
        </p>
        <div className="jgrid cols-5" style={{ marginTop: 16, gridTemplateColumns: "repeat(5, 1fr)" }}>
          {bitter.top.map((t) => (
            <div className="stat" key={t.compound}>
              <span className="label">{t.compound}</span>
              <span className="value" style={{ color: "#c97055" }}>{t.prob.toFixed(2)}</span>
              <span className="sub">bitter risk</span>
            </div>
          ))}
        </div>
      </section>

      <section className="jsection" data-tour="mech">
        <h2 className="jsubhead">Five-mechanism masking strategy</h2>
        <p className="jbody">
          Guided by the screen, five mechanisms are applied in the formulation. Together they target both the texture
          off-notes prominent in the English market and the aroma off-notes prominent in China, plus excessive sweetness.
        </p>
        <div className="jgrid cols-2" style={{ marginTop: 16 }}>
          {MECHANISMS.map(({ icon: Icon, title, body }) => (
            <div className="mech" key={title}>
              <div className="mech-head">
                <Icon size={20} strokeWidth={2} className="ic" />
                <h4>{title}</h4>
              </div>
              <p>{body}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
