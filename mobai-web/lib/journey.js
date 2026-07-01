// Single source of truth for the guided journey. The home route is the engine
// landing; the content routes use natural product-style names (no "Step N" labels).
export const STEPS = [
  { path: "/", key: "home", title: "MoBai AI Flavour Engine", short: "Home", tagline: "The engine" },
  { path: "/data", key: "data", title: "Consumer Data", short: "Data", tagline: "Social listening" },
  { path: "/insights", key: "insights", title: "Consumer Insights", short: "Insights", tagline: "What the data reveals" },
  { path: "/molecular", key: "molecular", title: "Molecular Pairing AI", short: "Molecular AI", tagline: "FlavorGraph screening" },
  { path: "/masking", key: "masking", title: "Off-Note Masking", short: "Masking", tagline: "Bitter-risk and masking" },
  { path: "/validation", key: "validation", title: "Consumer Validation", short: "Validation", tagline: "Survey and decision gate" },
  { path: "/pipeline", key: "pipeline", title: "The Pipeline", short: "Pipeline", tagline: "How it connects" },
];

export function stepIndex(pathname) {
  const i = STEPS.findIndex((s) => s.path === pathname);
  return i === -1 ? 0 : i;
}

export function progressPct(pathname) {
  const i = stepIndex(pathname);
  return Math.round((i / (STEPS.length - 1)) * 100);
}
