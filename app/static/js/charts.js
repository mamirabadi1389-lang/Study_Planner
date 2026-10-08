const Charts = (() => {
  const num = (n, max = 1) =>
    Number(n).toLocaleString('fa-IR', { maximumFractionDigits: max });
  const esc = (s) =>
    String(s).replace(/[&<>"']/g, (c) => (
      { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
    ));

  /* items: [{ label, value, active?, tip? }] */
  const bar = (items, height = 220) => {
    const W = 420, T = 26, B = 30, X = 10;
    const max = Math.max(1, ...items.map((i) => i.value));
    const slot = (W - X * 2) / items.length;
    const bw = Math.min(34, slot * 0.58);
    const ch = height - T - B;
    const bars = items.map((it, i) => {
      const h = (it.value / max) * ch;
      const x = X + i * slot + (slot - bw) / 2;
      const y = T + ch - h;
      const cx = (x + bw / 2).toFixed(1);
      return `<g><title>${esc(it.tip || it.label)}: ${num(it.value)}</title>
        <rect x="${x.toFixed(1)}" y="${T}" width="${bw.toFixed(1)}" height="${ch}" rx="9" class="c-track"/>
        <rect x="${x.toFixed(1)}" y="${y.toFixed(1)}" width="${bw.toFixed(1)}" height="${h.toFixed(1)}" rx="9" fill="url(#gBar)"/>
        ${it.value ? `<text x="${cx}" y="${(y - 7).toFixed(1)}" text-anchor="middle" class="c-val">${num(it.value)}</text>` : ''}
        <text x="${cx}" y="${height - 9}" text-anchor="middle" class="c-lbl${it.active ? ' on' : ''}">${esc(it.label)}</text>
      </g>`;
    }).join('');
    return `<svg viewBox="0 0 ${W} ${height}" class="chart">${bars}</svg>`;
  };

  /* points: [{ label, value, tip? }] */
  const line = (points, max = 20, height = 240) => {
    const W = 560, L = 34, R = 14, T = 16, B = 34;
    const cw = W - L - R;
    const ch = height - T - B;
    const x = (i) => L + (points.length === 1 ? cw / 2 : (i * cw) / (points.length - 1));
    const y = (v) => T + ch - (Math.min(v, max) / max) * ch;

    const grid = [0, 0.25, 0.5, 0.75, 1].map((f) => {
      const gy = y(max * f);
      return `<line class="c-grid" x1="${L}" x2="${W - R}" y1="${gy.toFixed(1)}" y2="${gy.toFixed(1)}"/>
        <text class="c-axis" x="${L - 8}" y="${(gy + 3).toFixed(1)}" text-anchor="end">${num(max * f, 0)}</text>`;
    }).join('');

    const pts = points.map((p, i) => [x(i), y(p.value)]);
    const path = pts.map(([px, py], i) => `${i ? 'L' : 'M'}${px.toFixed(1)},${py.toFixed(1)}`).join(' ');
    const base = (T + ch).toFixed(1);
    const area = `${path} L${pts[pts.length - 1][0].toFixed(1)},${base} L${pts[0][0].toFixed(1)},${base} Z`;
    const step = Math.ceil(points.length / 7);

    const dots = points.map((p, i) => {
      const [px, py] = pts[i];
      const label = i % step === 0 || i === points.length - 1
        ? `<text class="c-lbl" x="${px.toFixed(1)}" y="${height - 10}" text-anchor="middle">${esc(p.label)}</text>`
        : '';
      return `<g><title>${esc(p.tip || p.label)}: ${num(p.value, 2)}</title>
        <circle class="c-dot" cx="${px.toFixed(1)}" cy="${py.toFixed(1)}" r="5"/>${label}</g>`;
    }).join('');

    return `<svg viewBox="0 0 ${W} ${height}" class="chart">${grid}
      <path d="${area}" fill="url(#gArea)"/>
      <path class="c-line" d="${path}"/>${dots}</svg>`;
  };

  /* items: [{ label, value, color }] */
  const donut = (items, top, bottom) => {
    const total = items.reduce((s, i) => s + i.value, 0);
    if (!total) return '';
    let acc = 0;
    const segs = items.map((it) => {
      const pct = (it.value / total) * 100;
      const len = Math.max(pct - 0.8, 0.1);
      const out = `<circle r="15.915" cx="21" cy="21" fill="none" stroke-width="4.2"
        style="stroke:${esc(it.color)}"
        stroke-dasharray="${len.toFixed(2)} ${(100 - len).toFixed(2)}"
        stroke-dashoffset="${(25 - acc).toFixed(2)}">
        <title>${esc(it.label)}: ${num(it.value, 1)}</title></circle>`;
      acc += pct;
      return out;
    }).join('');
    return `<svg viewBox="0 0 42 42" class="chart donut">
      <circle r="15.915" cx="21" cy="21" fill="none" stroke-width="4.2" class="d-bg"/>${segs}
      <text x="21" y="21.5" text-anchor="middle" class="d-top">${esc(top)}</text>
      <text x="21" y="26.5" text-anchor="middle" class="d-bot">${esc(bottom)}</text></svg>`;
  };

  /* days: [{ day, done }] oldest -> newest */
  const heat = (days, fmt) => {
    const pad = (new Date(`${days[0].day}T00:00:00`).getDay() + 1) % 7;
    const max = Math.max(1, ...days.map((d) => d.done));
    const cells = Array(pad).fill('<i class="hc pad"></i>').concat(days.map((d) => {
      const lv = d.done ? Math.ceil((d.done / max) * 4) : 0;
      return `<i class="hc lv${lv}" title="${esc(fmt(d.day))} — ${num(d.done, 0)}"></i>`;
    }));
    return `<div class="heat">${cells.join('')}</div>`;
  };

  return { bar, line, donut, heat };
})();