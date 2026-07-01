"use client";

import { Fragment } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import { ArrowRight, Database, Lightbulb, Atom, ShieldCheck, ClipboardCheck } from "lucide-react";
import Reveal from "@/components/visual/Reveal";

const MoleculeField = dynamic(() => import("@/components/visual/MoleculeField"), { ssr: false });

const FLOW = [
  { icon: Database, k: "01", t: "Data", href: "/data" },
  { icon: Lightbulb, k: "02", t: "Insights", href: "/insights" },
  { icon: Atom, k: "03", t: "Molecular AI", href: "/molecular" },
  { icon: ShieldCheck, k: "04", t: "Masking", href: "/masking" },
  { icon: ClipboardCheck, k: "05", t: "Validation", href: "/validation" },
];

export default function Home() {
  return (
    <>
      <section className="engine-hero hero-spot" data-tour="hero">
        <div className="hero-canvas" aria-hidden="true">
          <MoleculeField />
        </div>
        <div>
          <p className="section-eyebrow">MoBai N54 - KSF Global Innovation Challenge 2026</p>
          <h1><span className="shimmer">An AI engine that turns consumer conversation into validated flavour.</span></h1>
          <p className="jlead">
            MoBai is an AI flavour-personalisation engine. It listens to bilingual social conversation, screens the
            molecular compatibility of flavour pairings, and closes the loop with a consumer panel. The two MoBai drinks
            shown here are its first validated outputs, not the limit of what it can produce.
          </p>
          <div className="hero-cta">
            <Link href="/data" className="step-btn primary">
              Begin the walkthrough <ArrowRight size={16} strokeWidth={2.2} />
            </Link>
            <Link href="/molecular" className="step-btn ghost" data-tour="explore-link">
              Explore the engine
            </Link>
          </div>
        </div>
        <div className="hero-product" data-tour="product">
          <img src="/assets/mobai-bottles.png" alt="MoBai high-protein RTD yogurt drink, two flavour variants" />
        </div>
      </section>

      <Reveal>
        <section className="jsection">
          <p className="section-eyebrow">How the engine works</p>
          <h2 className="jtitle">Five stages, one continuous loop</h2>
          <p className="jlead">
            Each stage hands a concrete result to the next. Consumer voice defines the target, molecular AI screens for
            compatible flavours, and a primary survey validates the outcome. Follow the walkthrough, or jump into any stage.
          </p>
          <div className="flowstrip" data-tour="flow" style={{ marginTop: 20 }}>
            {FLOW.map(({ icon: Icon, k, t, href }, i) => (
              <Fragment key={t}>
                <Link href={href} className="fs-node">
                  <Icon size={20} strokeWidth={2} color="#d9bd79" />
                  <span className="fs-k">{k}</span>
                  <span className="fs-t">{t}</span>
                </Link>
                {i < FLOW.length - 1 && <span className="fs-arrow" aria-hidden="true"><ArrowRight size={16} /></span>}
              </Fragment>
            ))}
          </div>
        </section>
      </Reveal>
    </>
  );
}
