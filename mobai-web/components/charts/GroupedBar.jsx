"use client";

import EChart from "@/components/EChart";
import { C, tooltip, grid, valueAxis, categoryAxis } from "@/lib/echartsTheme";

// Generic horizontal grouped bar.
// rows: array of objects; category from rows[i][catKey]; series defined by [{name,key,color}].
export default function GroupedBar({ rows, catKey, series, axisName = "Net sentiment (%)", height = 420, min, max }) {
  const cats = rows.map((r) => r[catKey]);
  const option = {
    backgroundColor: "transparent",
    textStyle: { fontFamily: "Inter, system-ui, sans-serif", color: C.cream },
    grid: grid({ left: 8, right: 24 }),
    legend: { data: series.map((s) => s.name), textStyle: { color: C.creamMuted }, top: 0, itemWidth: 12, itemHeight: 12 },
    tooltip: tooltip({ trigger: "axis", axisPointer: { type: "shadow" } }),
    xAxis: valueAxis(axisName, { min, max }),
    yAxis: categoryAxis({ data: cats, inverse: true, axisLabel: { color: C.creamMuted, fontSize: 11 } }),
    series: series.map((s) => ({
      name: s.name,
      type: "bar",
      data: rows.map((r) => (r[s.key] == null ? 0 : r[s.key])),
      itemStyle: { color: s.color, borderRadius: 3 },
      barMaxWidth: 16,
    })),
  };
  return <EChart option={option} height={height} />;
}
