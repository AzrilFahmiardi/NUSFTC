"use client";

import performance from "@/app/data/performance.json";
import Reveal from "@/components/visual/Reveal";

export default function PipelinePage() {
  return (
    <>
      <section className="jsection">
        <p className="section-eyebrow">How it connects</p>
        <h1 className="jtitle">One engine, one continuous loop</h1>
        <p className="jlead">
          The stages form a single loop, designed so that no component carries more inferential weight than it can
          support. Consumer voice identifies what people want and what fails them. The molecular layer ranks the pairings
          most compatible with those preferences. The survey closes the loop by testing whether the compatibility signal
          translates into real preference, and the GREEN gate confirms that it does for this panel and these concepts. The
          same loop can be re-run on new data and new flavour territories.
        </p>
      </section>

      <Reveal>
        <section className="jsection">
          <h2 className="jsubhead">Data pipeline summary</h2>
          <div className="card">
            <table className="data-table">
              <thead><tr><th>Component</th><th>Details</th></tr></thead>
              <tbody>
                {performance.dataVolume.map((d) => (
                  <tr key={d.component}><td><strong>{d.component}</strong></td><td>{d.detail}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </Reveal>

      <Reveal>
        <section className="jsection" data-tour="performance">
          <h2 className="jsubhead">AI performance metrics</h2>
          <div className="card">
            <table className="data-table">
              <thead><tr><th>Metric</th><th>Value</th><th>Notes</th></tr></thead>
              <tbody>
                {performance.metrics.map((m) => (
                  <tr key={m.metric}><td><strong>{m.metric}</strong></td><td>{m.value}</td><td>{m.notes}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>
      </Reveal>
    </>
  );
}
