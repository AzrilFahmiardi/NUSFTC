"use client";

import EChart from "@/components/EChart";
import { C, TIER_COLOR, tooltip, grid, valueAxis } from "@/lib/echartsTheme";

// Compatibility score (x) vs mean consumer liking (y), one point per tested concept.
// concepts: [{ concept, score, tier, liking }]. Annotated with the Spearman value.
export default function SurveyScatter({ concepts, spearman, height = 440 }) {
  const data = concepts.map((c) => ({
    value: [c.score, c.liking],
    name: c.concept,
    itemStyle: { color: TIER_COLOR[c.tier] || C.gold },
  }));
  const option = {
    backgroundColor: "transparent",
    textStyle: { fontFamily: "Inter, system-ui, sans-serif", color: C.cream },
    title: {
      text: `Spearman r = ${spearman}`,
      right: 12,
      top: 6,
      textStyle: { color: C.gold2, fontSize: 13, fontWeight: 800 },
    },
    grid: grid({ left: 8, right: 24, top: 30 }),
    tooltip: tooltip({
      trigger: "item",
      formatter: (p) => `<b>${p.data.name}</b><br/>Compatibility ${p.value[0].toFixed(2)}<br/>Mean liking ${p.value[1].toFixed(2)} / 9`,
    }),
    xAxis: valueAxis("FlavorGraph compatibility score", { min: 0, max: 1 }),
    yAxis: valueAxis("Mean consumer liking (9-point)", { min: 1, max: 9 }),
    series: [
      {
        type: "scatter",
        symbolSize: 18,
        data,
        label: {
          show: true,
          formatter: (p) => p.data.name,
          position: "top",
          color: C.cream,
          fontSize: 11,
          fontWeight: 650,
        },
        markLine: {
          symbol: "none",
          data: [{ yAxis: 5 }],
          lineStyle: { color: C.creamFaint, type: "dashed" },
          label: { color: C.creamMuted, fontSize: 10, formatter: "neutral midpoint" },
        },
      },
    ],
  };
  return <EChart option={option} height={height} />;
}
