"use client";

import EChart from "@/components/EChart";
import { C, TIER_COLOR, tooltip, grid, valueAxis, categoryAxis } from "@/lib/echartsTheme";

// Mean hedonic liking per concept with standard-error whiskers.
// concepts: [{ concept, liking, se, tier }].
export default function LikingBar({ concepts, height = 400 }) {
  const cats = concepts.map((c) => c.concept);
  const option = {
    backgroundColor: "transparent",
    textStyle: { fontFamily: "Inter, system-ui, sans-serif", color: C.cream },
    grid: grid({ left: 8, right: 16, top: 24, bottom: 8 }),
    tooltip: tooltip({
      trigger: "item",
      formatter: (p) => {
        const c = concepts[p.dataIndex % concepts.length];
        return `<b>${c.concept}</b><br/>Mean liking ${c.liking.toFixed(2)} / 9<br/>SE ${c.se.toFixed(2)} | ${c.tier} tier`;
      },
    }),
    xAxis: categoryAxis({ data: cats, axisLabel: { color: C.creamMuted, fontSize: 10, interval: 0, width: 90, overflow: "break" } }),
    yAxis: valueAxis("Mean liking (9-point)", { min: 0, max: 9 }),
    series: [
      {
        type: "bar",
        data: concepts.map((c) => ({ value: c.liking, itemStyle: { color: TIER_COLOR[c.tier] || C.gold, borderRadius: [4, 4, 0, 0] } })),
        barWidth: "52%",
        markLine: {
          symbol: "none",
          data: [{ yAxis: 5 }],
          lineStyle: { color: C.creamFaint, type: "dashed" },
          label: { color: C.creamMuted, fontSize: 10, formatter: "neutral" },
        },
      },
      {
        type: "custom",
        renderItem: (params, api) => {
          const idx = api.value(0);
          const low = api.coord([idx, api.value(1)]);
          const high = api.coord([idx, api.value(2)]);
          const halfWidth = 6;
          const style = { stroke: C.cream, lineWidth: 1.5 };
          return {
            type: "group",
            children: [
              { type: "line", shape: { x1: low[0], y1: low[1], x2: high[0], y2: high[1] }, style },
              { type: "line", shape: { x1: low[0] - halfWidth, y1: low[1], x2: low[0] + halfWidth, y2: low[1] }, style },
              { type: "line", shape: { x1: high[0] - halfWidth, y1: high[1], x2: high[0] + halfWidth, y2: high[1] }, style },
            ],
          };
        },
        data: concepts.map((c, i) => [i, c.liking - c.se, c.liking + c.se]),
        z: 5,
      },
    ],
  };
  return <EChart option={option} height={height} />;
}
