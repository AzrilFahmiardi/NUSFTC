// A floating animated hand that hovers over an element to invite a click during the
// guided tour. It disappears as soon as the user clicks the target (or the tour moves
// on). Rendered as a pointer-events-none overlay so it never blocks the real click.

let node = null;
let target = null;
let onTargetClick = null;
let reposition = null;

const HAND_SVG = `
<svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
  <path d="M22 14a8 8 0 0 1-8 8"/>
  <path d="M18 11v-1a2 2 0 0 0-2-2 2 2 0 0 0-2 2"/>
  <path d="M14 10V9a2 2 0 0 0-2-2 2 2 0 0 0-2 2v1"/>
  <path d="M10 9.5V4a2 2 0 0 0-2-2 2 2 0 0 0-2 2v10"/>
  <path d="M18 11a2 2 0 1 1 4 0v3a8 8 0 0 1-8 8h-2c-2.8 0-4.5-.86-5.99-2.34l-3.6-3.6a2 2 0 0 1 2.83-2.82L7 15"/>
</svg>`;

export function hideClickHint() {
  if (target && onTargetClick) target.removeEventListener("click", onTargetClick);
  if (reposition) {
    window.removeEventListener("scroll", reposition, true);
    window.removeEventListener("resize", reposition);
  }
  if (node && node.parentNode) node.parentNode.removeChild(node);
  node = null;
  target = null;
  onTargetClick = null;
  reposition = null;
}

export function showClickHint(selector) {
  if (typeof document === "undefined") return;
  hideClickHint();
  const el = document.querySelector(selector);
  if (!el) return;
  target = el;

  node = document.createElement("div");
  node.className = "click-hint";
  node.innerHTML = `<span class="ch-ripple"></span><span class="ch-hand">${HAND_SVG}</span>`;
  document.body.appendChild(node);

  reposition = () => {
    if (!target) return;
    const r = target.getBoundingClientRect();
    node.style.left = `${r.left + r.width * 0.5}px`;
    node.style.top = `${r.top + r.height * 0.5}px`;
  };
  reposition();
  window.addEventListener("scroll", reposition, true);
  window.addEventListener("resize", reposition);

  onTargetClick = () => hideClickHint();
  el.addEventListener("click", onTargetClick, { once: true });
}
