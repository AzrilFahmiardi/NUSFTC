"use client";

import EChart from "@/components/EChart";
import { C, POSITIVE, NEGATIVE, tooltip, grid, valueAxis, categoryAxis } from "@/lib/echartsTheme";

// Horizontal diverging sentiment bars: positive share to the right, negative to the left.
// data: [{ flavor, pos, neg, net }] already sorted by net (descending).
export default function DivergingBar({ data, height = 420 }) {
  const cats = data.map((d) => d.flavor);
  const option = {
    backgroundColor: "transparent",
    textStyle: { fontFamily: "Inter, system-ui, sans-serif", color: C.cream },
    grid: grid({ left: 8, right: 36 }),
    legend: {
      data: ["Positive", "Negative"],
      textStyle: { color: C.creamMuted },
      top: 0,
      itemWidth: 12,
      itemHeight: 12,
    },
    tooltip: tooltip({
      trigger: "axis",
      axisPointer: { type: "shadow" },
      formatter: (p) => {
        const row = data[p[0].dataIndex];
        return `<b>${row.flavor}</b><br/>Positive ${row.pos}%<br/>Negative ${row.neg}%<br/>Net ${row.net}%<br/>${row.mentions ?? ""}${row.mentions ? " mentions" : ""}`;
      },
    }),
    xAxis: valueAxis("Sentiment share (%)", { axisLabel: { color: C.creamMuted, formatter: (v) => Math.abs(v) } }),
    yAxis: categoryAxis({ data: cats, inverse: true }),
    series: [
      {
        name: "Positive",
        type: "bar",
        stack: "s",
        data: data.map((d) => d.pos),
        itemStyle: { color: POSITIVE, borderRadius: [0, 3, 3, 0] },
        barWidth: "62%",
      },
      {
        name: "Negative",
        type: "bar",
        stack: "s",
        data: data.map((d) => -d.neg),
        itemStyle: { color: NEGATIVE, borderRadius: [3, 0, 0, 3] },
      },
    ],
  };
  return <EChart option={option} height={height} />;
}
