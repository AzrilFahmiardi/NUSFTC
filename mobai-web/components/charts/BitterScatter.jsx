"use client";

import EChart from "@/components/EChart";
import { C, POSITIVE, NEGATIVE, tooltip, grid, valueAxis } from "@/lib/echartsTheme";

// Bitter-risk screen: molecular weight (x) vs predicted bitter probability (y).
// points: [{ compound, mw, prob, status }]. top: [{compound, prob}] are labelled.
export default function BitterScatter({ points, threshold = 0.5, top = [], height = 440 }) {
  const labelSet = new Set(top.map((t) => t.compound));
  const mk = (status) =>
    points
      .filter((p) => p.status === status)
      .map((p) => ({
        value: [p.mw, p.prob],
        name: p.compound,
        label: labelSet.has(p.compound)
          ? { show: true, formatter: p.compound, position: "right", color: C.cream, fontSize: 10, fontWeight: 600 }
          : { show: false },
      }));

  const option = {
    backgroundColor: "transparent",
    textStyle: { fontFamily: "Inter, system-ui, sans-serif", color: C.cream },
    grid: grid({ left: 8, right: 30, top: 30 }),
    legend: { data: ["Bitter risk", "Safe"], textStyle: { color: C.creamMuted }, top: 0, itemWidth: 12, itemHeight: 12 },
    tooltip: tooltip({
      trigger: "item",
      formatter: (p) => `<b>${p.data.name}</b><br/>MW ${p.value[0]} g/mol<br/>Bitter probability ${p.value[1].toFixed(3)}`,
    }),
    xAxis: valueAxis("Molecular weight (g/mol)", { min: 0 }),
    yAxis: valueAxis("Predicted bitter probability", { min: 0, max: 1 }),
    series: [
      {
        name: "Bitter risk",
        type: "scatter",
        symbolSize: 11,
        data: mk("risk"),
        itemStyle: { color: NEGATIVE, opacity: 0.85, borderColor: "#0000001a" },
        markLine: {
          symbol: "none",
          data: [{ yAxis: threshold }],
          lineStyle: { color: C.creamFaint, type: "dashed" },
          label: { color: C.creamMuted, fontSize: 10, formatter: `risk threshold ${threshold}` },
        },
      },
      {
        name: "Safe",
        type: "scatter",
        symbolSize: 10,
        data: mk("safe"),
        itemStyle: { color: POSITIVE, opacity: 0.7, borderColor: "#0000001a" },
      },
    ],
  };
  return <EChart option={option} height={height} />;
}
