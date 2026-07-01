"use client";

import { useEffect } from "react";
import { usePathname, useRouter } from "next/navigation";
import { driver } from "driver.js";
import "driver.js/dist/driver.css";
import { Compass } from "lucide-react";
import { STEPS } from "@/lib/journey";
import { showClickHint, hideClickHint } from "@/lib/clickHint";

// Per-stage tour steps. Every important insight we want a judge to absorb lives here,
// so a lazy explorer still receives the full story just by moving through the stages.
const TOUR_STEPS = {
  "/": [
    { popover: { title: "Welcome to the MoBai engine", description: "MoBai is an AI flavour-personalisation engine. This walkthrough shows how it turns consumer conversation into a validated product. It runs automatically; use Next to move through it, or close it to stop." } },
    { element: '[data-tour="hero"]', popover: { title: "What it does", description: "It listens to bilingual social conversation, screens molecular flavour compatibility, and validates the result with real consumers." } },
    { element: '[data-tour="product"]', popover: { title: "The first outputs", description: "Two validated MoBai drinks: a mango-jasmine and a coconut-milk-tea high-protein yogurt. They are examples of what the engine produces, not its limit." } },
    { element: '[data-tour="flow"]', popover: { title: "Five connected stages", description: "Data, Insights, Molecular AI, Masking, and Validation. Follow them in order, or jump from the top navigation." } },
  ],
  "/data": [
    { element: '[data-tour="sources"]', popover: { title: "6,670 posts, 4 platforms, 2 languages", description: "Twitter for English, plus Xiaohongshu, Weibo, and Douyin for China. The engine is source-agnostic; this demo ships with these datasets and can ingest more." } },
  ],
  "/insights": [
    { element: '[data-tour="flavors"]', hint: '[data-tour="market"] button:last-child', popover: { title: "A shared flavour territory", description: "Mango, coconut, milk tea, and matcha are positive in both markets. Try the toggle to switch between the English and China signals." } },
    { element: '[data-tour="crossmarket"]', popover: { title: "Complementary pain, real leverage", description: "English foregrounds texture, China foregrounds aroma, so the masking must address both. Master Kong appears in China with positive sentiment." } },
    { element: '[data-tour="segments"]', popover: { title: "Cross-market segments", description: "Segments draw from both markets, confirming genuine consumer types rather than a language split." } },
  ],
  "/molecular": [
    { element: '[data-tour="arch"]', popover: { title: "Four connected layers", description: "Consumer voice, the FlavorGraph molecular AI, our pairing-compatibility recommender, and product science." } },
    { element: '[data-tour="graph"]', popover: { title: "FlavorGraph at scale", description: "8,298 nodes with 300-dimensional embeddings from Park et al. 2021, a scale no human formulator could survey by hand." } },
    { element: '[data-tour="explorer"]', hint: '[data-hint="explore-node"]', popover: { title: "Explore the molecules", description: "Click any node to see how an ingredient links to its aroma compounds and to shared chemical families." } },
    { element: '[data-tour="compat"]', popover: { title: "The compatibility screen", description: "Variant A scores 0.73 and Variant B 0.79, both HIGH, well clear of the strawberry baseline at 0.26 (LOW)." } },
    { element: '[data-tour="tool"]', hint: '[data-tour="tool"] .pick', popover: { title: "Try it live", description: "Pick ingredients and your browser computes the molecular compatibility in real time. This is a ranking screen, not a liking prediction." } },
    { element: '[data-tour="variantc"]', popover: { title: "A discovered flavour", description: "Screening 8,279 ingredients, the engine surfaced crushed pineapple (0.61) as a third candidate it was never calibrated on." } },
  ],
  "/masking": [
    { element: '[data-tour="bitter"]', popover: { title: "Targeting off-notes", description: "A classifier flags the compounds behind protein off-notes. Branched-chain and aromatic amino acids such as tryptophan (0.92) rank highest." } },
    { element: '[data-tour="mech"]', popover: { title: "Five masking mechanisms", description: "Together they address both the texture off-notes prominent in English and the aroma off-notes prominent in China." } },
  ],
  "/validation": [
    { element: '[data-tour="gate"]', popover: { title: "A pre-committed decision gate", description: "With n=34, Spearman r=0.90 and HIGH-tier liking 6.9 versus 4.3 for the low baseline, the result meets the gate at GREEN." } },
    { element: '[data-tour="surveycharts"]', popover: { title: "Compatibility tracks liking", description: "Concepts the screen rates more compatible are liked more by real consumers, validating the method itself." } },
  ],
  "/pipeline": [
    { element: '[data-tour="performance"]', popover: { title: "Measured, not asserted", description: "The performance metrics behind each stage of the engine. That is the MoBai engine end to end, from consumer language to a validated product. Replay this tour anytime from the Tour button." } },
  ],
};

const RUN_KEY = "mobai_guided_run"; // sessionStorage: an active guided run is chaining across stages

function stopRun() {
  // Closing the tour only stops the current chain; it does not disable it forever.
  try { sessionStorage.removeItem(RUN_KEY); } catch {}
}

function startTour(pathname, router) {
  if (typeof window === "undefined") return;
  const steps = TOUR_STEPS[pathname];
  if (!steps || !steps.length) return;
  const idx = STEPS.findIndex((s) => s.path === pathname);
  const nextPath = STEPS[idx + 1]?.path;

  let advancing = false; // true when we tear down to move to the next stage (not a user dismiss)
  let d;
  d = driver({
    showProgress: true,
    overlayColor: "#04130f",
    overlayOpacity: 0.72,
    stagePadding: 6,
    stageRadius: 10,
    popoverClass: "mobai-tour",
    nextBtnText: "Next",
    prevBtnText: "Back",
    doneBtnText: nextPath ? "Next stage" : "Done",
    steps: steps.map((s) => ({
      ...s,
      onHighlighted: s.hint ? () => showClickHint(s.hint) : undefined,
      onDeselected: s.hint ? () => hideClickHint() : undefined,
    })),
    onNextClick: () => {
      if (d.isLastStep()) {
        advancing = true;
        d.destroy();
        if (nextPath) router.push(nextPath); // guided run stays on; next stage auto-shows
        else {
          try { sessionStorage.removeItem(RUN_KEY); } catch {} // finished all stages (not disabled)
        }
      } else {
        d.moveNext();
      }
    },
    onDestroyStarted: () => {
      // Fired by the close button, Escape, or an overlay click. If we are not
      // programmatically advancing to the next stage, the user dismissed it, so
      // treat that as an explicit disable.
      hideClickHint();
      if (!advancing) stopRun();
      d.destroy();
    },
  });
  d.drive();
}

export function useGuidedAutostart() {
  const pathname = usePathname();
  const router = useRouter();
  useEffect(() => {
    if (typeof window === "undefined") return;
    if (!TOUR_STEPS[pathname]) return;
    try {
      // Clear any legacy permanent-disable flag from an earlier build.
      localStorage.removeItem("mobai_tour_off");

      // The home route always (re)starts a guided run, so opening or reloading
      // the site always shows the guide. Closing it only stops the current run.
      if (pathname === "/") {
        Object.keys(sessionStorage)
          .filter((k) => k.startsWith("mobai_seen_"))
          .forEach((k) => sessionStorage.removeItem(k));
        sessionStorage.setItem(RUN_KEY, "1");
      }
      if (sessionStorage.getItem(RUN_KEY) !== "1") return;

      const seenKey = "mobai_seen_" + pathname;
      if (sessionStorage.getItem(seenKey) === "1") return;

      const t = setTimeout(() => {
        // Set the seen flag inside the timer so React strict-mode double-invoke
        // (mount, cleanup, mount) does not consume the flag before firing.
        if (sessionStorage.getItem(seenKey) === "1") return;
        sessionStorage.setItem(seenKey, "1");
        startTour(pathname, router);
      }, 600);
      return () => clearTimeout(t);
    } catch {}
  }, [pathname, router]);
}

export function TourButton() {
  const pathname = usePathname();
  const router = useRouter();
  const replay = () => {
    try {
      localStorage.removeItem("mobai_tour_off"); // clear any legacy disable flag
      Object.keys(sessionStorage)
        .filter((k) => k.startsWith("mobai_seen_"))
        .forEach((k) => sessionStorage.removeItem(k));
      sessionStorage.setItem(RUN_KEY, "1");
      sessionStorage.setItem("mobai_seen_" + pathname, "1");
    } catch {}
    startTour(pathname, router);
  };
  return (
    <button type="button" className="tour-button" data-tour="tour-button" onClick={replay}>
      <Compass size={16} strokeWidth={2.2} aria-hidden="true" />
      <span>Tour</span>
    </button>
  );
}
