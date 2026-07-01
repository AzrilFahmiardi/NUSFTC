"use client";

import survey from "@/app/data/survey.json";
import SurveyScatter from "@/components/charts/SurveyScatter";
import LikingBar from "@/components/charts/LikingBar";

const TIER_CLASS = { HIGH: "high", "MID-HIGH": "mid-high", MID: "mid", LOW: "low" };

export default function ValidationPage() {
  return (
    <>
      <section className="jsection">
        <p className="section-eyebrow">Survey and decision gate</p>
        <h1 className="jtitle">Does molecular compatibility track real liking?</h1>
        <p className="jlead">
          A primary consumer survey tested whether flavour pairings the screen scores as more molecularly compatible are
          in fact liked more by real consumers. It is a validation of the screening method itself. Each of {survey.n}{" "}
          respondents rated five concepts on a nine-point hedonic scale, spanning the full compatibility-score range.
        </p>
      </section>

      <section className="jsection" data-tour="gate">
        <div className="jgrid cols-4">
          <div className="stat"><span className="label">Respondents</span><span className="value">{survey.n}</span><span className="sub">APAC urban, aged 25 to 38</span></div>
          <div className="stat"><span className="label">Spearman r</span><span className="value">{survey.spearman}</span><span className="sub">p = {survey.pValue}</span></div>
          <div className="stat"><span className="label">HIGH vs LOW liking</span><span className="value">{survey.highMean} / {survey.lowMean}</span><span className="sub">9-point hedonic scale</span></div>
          <div className="stat" style={{ justifyItems: "start" }}>
            <span className="label">Decision gate</span>
            <span className="gate green" style={{ marginTop: 4 }}><span className="dot" />{survey.gate}</span>
          </div>
        </div>
        <p className="chart-caption">
          A pre-committed decision gate was defined before data collection to prevent results from being read selectively.
          It required a positive rank correlation in the correct direction and a clear separation between the high tier and
          the low baseline. The result met the gate at the GREEN level.
        </p>
      </section>

      <section className="jsection" data-tour="surveycharts">
        <div className="jgrid cols-2">
          <div>
            <SurveyScatter concepts={survey.concepts} spearman={survey.spearman} height={440} />
            <p className="chart-caption">Compatibility score versus mean consumer liking, one point per concept, coloured by affinity tier.</p>
          </div>
          <div>
            <LikingBar concepts={survey.concepts} height={440} />
            <p className="chart-caption">Mean hedonic liking per concept with standard-error whiskers. Dashed line at the neutral midpoint.</p>
          </div>
        </div>
      </section>

      <section className="jsection">
        <h2 className="jsubhead">Per-concept results</h2>
        <div className="card">
          <table className="data-table">
            <thead>
              <tr><th>Concept</th><th>Compatibility</th><th>Tier</th><th>Mean liking</th><th>Purchase intent</th><th>Role</th></tr>
            </thead>
            <tbody>
              {survey.concepts.map((c) => (
                <tr key={c.concept}>
                  <td><strong>{c.concept}</strong></td>
                  <td>{c.score.toFixed(2)}</td>
                  <td><span className={`tier-badge ${TIER_CLASS[c.tier]}`}>{c.tier}</span></td>
                  <td>{c.liking.toFixed(2)} / 9</td>
                  <td>{c.purchase.toFixed(2)} / 5</td>
                  <td>{c.role}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </>
  );
}
