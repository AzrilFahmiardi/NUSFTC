"use client";

import { useEffect, useState } from "react";
import ReactECharts from "echarts-for-react";

// Client-only ECharts wrapper. Renders a fixed-height placeholder on the server and
// before mount (no layout shift, no canvas-on-server errors), then the live chart.
export default function EChart({ option, height = 360, className = "", style = {} }) {
  const [mounted, setMounted] = useState(false);
  useEffect(() => setMounted(true), []);

  if (!mounted) {
    return <div className={`chart-box ${className}`} style={{ height, ...style }} aria-hidden="true" />;
  }
  return (
    <div className={`chart-box ${className}`} style={{ height, ...style }}>
      <ReactECharts
        option={option}
        style={{ height: "100%", width: "100%" }}
        opts={{ renderer: "canvas" }}
        notMerge
        lazyUpdate
      />
    </div>
  );
}
