"use client";

import EChart from "@/components/EChart";
import { C, TIER_COLOR, tooltip, grid, valueAxis, categoryAxis } from "@/lib/echartsTheme";

// Horizontal bars coloured by affinity tier, with an optional reference line.
// items: [{ label, score, tier }]. Sorted descending by score for display.
export default function TierBar({ items, refLine, refLabel, max = 1, height = 420 }) {
  const sorted = [...items].sort((a, b) => a.score - b.score); // ascending -> top is highest with inverse axis off
  const cats = sorted.map((d) => d.label);
  const series = {
    type: "bar",
    data: sorted.map((d) => ({ value: d.score, itemStyle: { color: TIER_COLOR[d.tier] || C.gold, borderRadius: [0, 4, 4, 0] } })),
    barWidth: "60%",
    label: {
      show: true,
      position: "right",
      color: C.cream,
      fontWeight: 700,
      fontSize: 11,
      formatter: (p) => p.value.toFixed(2),
    },
  };
  if (refLine != null) {
    series.markLine = {
      symbol: "none",
      data: [{ xAxis: refLine }],
      lineStyle: { color: C.creamFaint, type: "dashed" },
      label: { color: C.creamMuted, fontSize: 10, formatter: refLabel || `${refLine}` },
    };
  }
  const option = {
    backgroundColor: "transparent",
    textStyle: { fontFamily: "Inter, system-ui, sans-serif", color: C.cream },
    grid: grid({ left: 8, right: 48 }),
    tooltip: tooltip({
      trigger: "item",
      formatter: (p) => `<b>${cats[p.dataIndex]}</b><br/>Compatibility ${p.value.toFixed(3)}<br/>${sorted[p.dataIndex].tier} tier`,
    }),
    xAxis: valueAxis("Molecular compatibility (cosine to anchor)", { min: 0, max }),
    yAxis: categoryAxis({ data: cats, axisLabel: { color: C.creamMuted, fontSize: 11, width: 220, overflow: "truncate" } }),
    series: [series],
  };
  return <EChart option={option} height={height} />;
}
