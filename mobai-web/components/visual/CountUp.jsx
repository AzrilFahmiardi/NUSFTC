"use client";

import { useEffect, useRef, useState } from "react";
import { useInView } from "framer-motion";

// Animated number that counts up when scrolled into view.
export default function CountUp({ to, decimals = 0, prefix = "", suffix = "", duration = 1.1 }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-40px" });
  const [val, setVal] = useState(0);

  useEffect(() => {
    if (!inView) return;
    let raf;
    let startT = null;
    const tick = (t) => {
      if (startT === null) startT = t;
      const p = Math.min(1, (t - startT) / (duration * 1000));
      const eased = 1 - Math.pow(1 - p, 3);
      setVal(to * eased);
      if (p < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [inView, to, duration]);

  const formatted = val.toLocaleString(undefined, { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
  return (
    <span ref={ref}>
      {prefix}
      {formatted}
      {suffix}
    </span>
  );
}
