"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ArrowLeft, ArrowRight } from "lucide-react";
import { STEPS, stepIndex, progressPct } from "@/lib/journey";
import { TourButton, useGuidedAutostart } from "./Tour";

export default function JourneyShell({ children }) {
  const pathname = usePathname();
  const idx = stepIndex(pathname);
  const current = STEPS[idx];
  const prev = STEPS[idx - 1];
  const next = STEPS[idx + 1];
  const pct = progressPct(pathname);
  useGuidedAutostart();

  return (
    <>
      <header className="journey-nav">
        <Link href="/" className="brand" aria-label="MoBai home">
          <span className="brand-mark">M</span>
          <span>MoBai</span>
        </Link>
        <nav className="journey-steps" data-tour="steps" aria-label="Pipeline steps">
          {STEPS.slice(1).map((s) => (
            <Link key={s.path} href={s.path} className={`journey-step-link${s.path === pathname ? " active" : ""}`}>
              {s.short}
            </Link>
          ))}
        </nav>
        <div className="journey-actions">
          <TourButton />
        </div>
      </header>

      <div className="journey-progress" data-tour="progress" role="progressbar" aria-valuenow={pct} aria-valuemin={0} aria-valuemax={100}>
        <i style={{ width: `${pct}%` }} />
      </div>

      <main className="journey-main">{children}</main>

      <footer className="journey-footer">
        {prev ? (
          <Link href={prev.path} className="step-btn ghost" data-tour="prev">
            <ArrowLeft size={16} strokeWidth={2.2} aria-hidden="true" />
            <span>{prev.short}</span>
          </Link>
        ) : (
          <span className="step-btn-spacer" />
        )}

        <span className="step-eyebrow">{current.tagline}</span>

        {next ? (
          <Link href={next.path} className="step-btn primary" data-tour="next">
            <span>{next.short}</span>
            <ArrowRight size={16} strokeWidth={2.2} aria-hidden="true" />
          </Link>
        ) : (
          <span className="step-btn-spacer" />
        )}
      </footer>
    </>
  );
}
