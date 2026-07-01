// Shared ECharts styling helpers, aligned to the MoBai dark-green and gold palette.
// Charts compose these helpers rather than relying on a registered theme, which keeps
// full control and avoids theme-registration races with echarts-for-react.

export const C = {
  cream: "#f7f1e6",
  creamMuted: "#f7f1e6b8",
  creamFaint: "#f7f1e68a",
  gold: "#c5a35a",
  gold2: "#d9bd79",
  tea: "#8bb391",
  mint: "#b7d7be",
  terracotta: "#c97055",
  line: "#f7f1e624",
  grid: "#f7f1e614",
  panel: "#071a15",
};

// Affinity tiers and sentiment colours.
export const TIER_COLOR = {
  HIGH: "#8bb391",
  "MID-HIGH": "#d9bd79",
  MID: "#c5a35a",
  LOW: "#c97055",
};
export const POSITIVE = "#8bb391";
export const NEGATIVE = "#c97055";
export const NEUTRAL = "#7d8a82";

// Categorical palette for multi-series charts.
export const PALETTE = ["#d9bd79", "#8bb391", "#c97055", "#b7d7be", "#c5a35a", "#9bc0cf"];

export const textStyle = { fontFamily: "Inter, system-ui, sans-serif", color: C.cream };

export function tooltip(extra = {}) {
  return {
    backgroundColor: "#071a15f2",
    borderColor: C.line,
    borderWidth: 1,
    textStyle: { color: C.cream, fontFamily: "Inter, system-ui, sans-serif", fontSize: 12 },
    padding: [8, 12],
    ...extra,
  };
}

export function grid(extra = {}) {
  return { left: 8, right: 18, top: 24, bottom: 8, containLabel: true, ...extra };
}

export function axisLabel(extra = {}) {
  return { color: C.creamMuted, fontFamily: "Inter, system-ui, sans-serif", fontSize: 11, ...extra };
}

export function valueAxis(name, extra = {}) {
  return {
    type: "value",
    name,
    nameTextStyle: { color: C.creamFaint, fontSize: 11 },
    axisLine: { lineStyle: { color: C.line } },
    splitLine: { lineStyle: { color: C.grid } },
    axisLabel: axisLabel(),
    ...extra,
  };
}

export function categoryAxis(extra = {}) {
  return {
    type: "category",
    axisLine: { lineStyle: { color: C.line } },
    axisTick: { show: false },
    axisLabel: axisLabel(),
    ...extra,
  };
}
