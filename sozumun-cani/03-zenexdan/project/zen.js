// «Sözümün Canı — Zənəxdan» : one fine line — ink, smile, frown, doors, knot, the word that smiles
const DUR = 58.7;
const cv = document.getElementById('c'); cv.width = W; cv.height = H;
const X = cv.getContext('2d');
const mk = () => { const c = document.createElement('canvas'); c.width = W; c.height = H; return c; };
const layer = mk(), LC = layer.getContext('2d');
const LOGO = new Image(); window.LOGO_READY = new Promise(r => { LOGO.onload = r; LOGO.onerror = r; }); LOGO.src = LOGO_SRC;
const FR = 'FR', IN = 'Inter';
let LOGO_DARK = null;

// ---------- atmosphere ----------
function dawn(c, k = {}) {
  const mix = (a, b, t) => a.map((v, i) => Math.round(v + (b[i] - v) * t));
  let top = [26, 16, 22], mid = [44, 26, 32], bot = [58, 33, 36];
  const g0 = k.grey || 0, w = k.warm || 0;
  top = mix(top, [14, 17, 22], g0); mid = mix(mid, [24, 28, 35], g0); bot = mix(bot, [30, 33, 40], g0);
  top = mix(top, [40, 24, 22], w); mid = mix(mid, [74, 42, 36], w); bot = mix(bot, [92, 52, 40], w);
  const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, `rgb(${top})`); g.addColorStop(0.55, `rgb(${mid})`); g.addColorStop(1, `rgb(${bot})`);
  c.fillStyle = g; c.fillRect(0, 0, W, H);
  const gx = k.gx ?? CX, gy = k.gy ?? 900, gr = k.gr ?? 900;
  const col = g0 > 0.5 ? 'rgba(160,175,190,0.07)' : `rgba(243,190,150,${0.12 + 0.12 * w})`;
  const r = c.createRadialGradient(gx, gy, 0, gx, gy, gr); r.addColorStop(0, col); r.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = r; c.fillRect(0, 0, W, H);
}
function paper(c, a = 1) {
  c.save(); c.globalAlpha = a;
  const g = c.createRadialGradient(CX, 860, 100, CX, 960, 1250); g.addColorStop(0, '#efe4d2'); g.addColorStop(0.7, '#dccdb6'); g.addColorStop(1, '#bba88e');
  c.fillStyle = g; c.fillRect(0, 0, W, H); c.globalAlpha = a * 0.5; c.drawImage(FIBRE, 0, 0); c.restore();
}
const FIBRE = (() => { const cc = mk(), c = cc.getContext('2d'), r = rng(8); for (let i = 0; i < 2200; i++) { c.strokeStyle = `rgba(90,60,40,${0.02 + r() * 0.04})`; c.lineWidth = 0.5 + r(); const x = r() * W, y = r() * H, a = r() * 6.3, l = 8 + r() * 40; c.beginPath(); c.moveTo(x, y); c.lineTo(x + Math.cos(a) * l, y + Math.sin(a) * l); c.stroke(); } return cc; })();
const SPECK = (() => { const r = rng(19), a = []; for (let i = 0; i < 80; i++) a.push({ x: r() * W, y: r() * H, z: 0.3 + r() * 0.7, ph: r() * 6.3 }); return a; })();
function specks(c, t, amt = 0.5, col = '250,215,180') {
  c.save(); c.globalCompositeOperation = 'lighter';
  for (const m of SPECK) { const x = m.x + Math.sin(t * 0.3 + m.ph) * 20 * m.z, y = ((m.y - t * 9 * m.z) % H + H) % H; c.fillStyle = `rgba(${col},${amt * (0.1 + 0.3 * (0.5 + 0.5 * Math.sin(t * 1.2 + m.ph))) * m.z})`; c.beginPath(); c.arc(x, y, 0.8 + 2 * m.z, 0, 7); c.fill(); }
  c.restore();
}
function glw(c, x, y, r, col, a) { if (a <= 0) return; const g = c.createRadialGradient(x, y, 0, x, y, r); g.addColorStop(0, `rgba(${col},${a})`); g.addColorStop(0.45, `rgba(${col},${a * 0.3})`); g.addColorStop(1, `rgba(${col},0)`); c.fillStyle = g; c.fillRect(x - r, y - r, 2 * r, 2 * r); }
function warmGrad(c, y0, y1) { const g = c.createLinearGradient(0, y0, 0, y1); g.addColorStop(0, '#fff3e2'); g.addColorStop(0.5, PEACH); g.addColorStop(1, '#d98a6c'); return g; }

// ---------- the fine line ----------
// a tapered stroke along a quadratic: bend>0 smiles (∪), bend<0 frowns (∩)
function fineLine(c, cx, cy, w, bend, o = {}) {
  const N = 70, draw = o.draw ?? 1, lw = o.lw ?? 5, col = o.col || PEACH;
  const P0 = [cx - w / 2, cy - (o.lift || 0)], P1 = [cx, cy + bend * 2], P2 = [cx + w / 2, cy - (o.lift || 0)];
  const s0 = 0.5 - draw / 2, s1 = 0.5 + draw / 2;
  c.save(); c.fillStyle = col; c.globalAlpha *= (o.a ?? 1);
  if (o.glow) { c.shadowColor = o.glowCol || 'rgba(243,190,150,0.7)'; c.shadowBlur = o.glow; }
  const L = [], R = [];
  for (let i = 0; i <= N; i++) {
    const u = lerp(s0, s1, i / N), q = qpt(P0, P1, P2, u), tg = qtan(P0, P1, P2, u), l = Math.hypot(tg[0], tg[1]) || 1;
    const nx = -tg[1] / l, ny = tg[0] / l, ww = lw * Math.pow(Math.sin(Math.PI * u), 0.7) + 0.4;
    L.push([q[0] + nx * ww / 2, q[1] + ny * ww / 2]); R.push([q[0] - nx * ww / 2, q[1] - ny * ww / 2]);
  }
  c.beginPath(); c.moveTo(...L[0]); for (const q of L) c.lineTo(...q); for (let i = R.length - 1; i >= 0; i--) c.lineTo(...R[i]); c.closePath(); c.fill();
  c.restore();
  return { P0, P1, P2 };
}
// the dimple: a small crescent
function dimple(c, x, y, s, a = 1, col = PEACH, glow = 10) {
  if (a <= 0) return;
  c.save(); c.globalAlpha *= a; c.fillStyle = col; c.shadowColor = 'rgba(243,190,150,0.6)'; c.shadowBlur = glow;
  c.beginPath(); c.arc(x, y, s, Math.PI * 0.62, Math.PI * 1.38); c.arc(x + s * 0.42, y, s * 0.82, Math.PI * 1.3, Math.PI * 0.7, true); c.closePath(); c.fill(); c.restore();
}
// a strand of hair: a long, thin, swaying curve
function strand(c, x, y, len, t, ph, o = {}) {
  c.save(); c.strokeStyle = o.col || INK; c.lineWidth = o.w || 1.4; c.globalAlpha *= (o.a ?? 1); c.lineCap = 'round';
  c.beginPath(); c.moveTo(x, y);
  const N = 24; let px = x, py = y;
  for (let i = 1; i <= N; i++) { const s = i / N; px = x + Math.sin(s * 3.2 + ph + t * 0.8) * 26 * s * (o.sway ?? 1) + (o.curl || 0) * s * s * 60; py = y + s * len; c.lineTo(px, py); }
  c.stroke(); c.restore();
  return [px, py];
}

// ---------- captions ----------
const CAP = { 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1, 9: 1, 10: 1 };
function captions(c, t) {
  for (const li in CAP) {
    const Ln = LINES[li], next = LINES[+li + 1];
    const endT = Math.min(Ln.e + 0.7, next ? next.s - 0.05 : 99);
    const s0 = +li === 3 ? 9.7 : Ln.s - 0.15; // first caption waits until the paper has given way to dawn
    if (t < s0 || t > endT) continue;
    const fade = sm(p(t, s0, s0 + 0.25)) * (1 - sm(p(t, endT - 0.35, endT)));
    const o = { ff: IN, wt: 400, sz: 37 };
    c.save(); font(c, o); const sp = c.measureText(' ').width;
    const lines = [[]]; let lw = 0; const maxW = 820;
    for (const [w, wt] of Ln.w) { const ww = c.measureText(w).width; if (lw + ww > maxW && lines[lines.length - 1].length) { lines.push([]); lw = 0; } lines[lines.length - 1].push([w, wt, ww]); lw += ww + sp; }
    const lh = 54, bottom = 1555, top = bottom - (lines.length - 1) * lh;
    const g = c.createLinearGradient(0, top - 130, 0, H); g.addColorStop(0, 'rgba(12,7,9,0)'); g.addColorStop(0.3, `rgba(12,7,9,${0.45 * fade})`); g.addColorStop(1, `rgba(12,7,9,${0.5 * fade})`);
    c.fillStyle = g; c.fillRect(0, top - 130, W, H - top + 130);
    lines.forEach((L, j) => {
      const total = L.reduce((a, q) => a + q[2], 0) + sp * (L.length - 1); let x = CX - total / 2;
      for (const [w, wt, ww] of L) {
        const k = sm(p(t, wt - 0.08, wt + 0.2)); const cur = t >= wt - 0.05 && t < wt + 0.45;
        c.globalAlpha = fade * (0.12 + 0.86 * k); c.fillStyle = cur ? SUN : CREAM; c.textAlign = 'left';
        c.shadowColor = 'rgba(0,0,0,0.6)'; c.shadowBlur = 10; c.fillText(w, x, top + j * lh + (1 - k) * 6); x += ww + sp;
      }
    });
    c.restore();
  }
}
// ---------- branding ----------
function branding(c, t, onPaper) {
  if (!LOGO.naturalWidth) return;
  const ar = LOGO.naturalHeight / LOGO.naturalWidth;
  const topA = sm(p(t, 0.4, 1.2)) * (1 - sm(p(t, 54.4, 55.0)));
  if (topA > 0) {
    const lw = 200, lh = lw * ar;
    // on the cream paper the logo is shown in dark ink (same shape, transparency preserved), turning white as dawn arrives
    const pa = onPaper;
    if (!LOGO_DARK) { LOGO_DARK = document.createElement('canvas'); LOGO_DARK.width = LOGO.naturalWidth; LOGO_DARK.height = LOGO.naturalHeight; const g = LOGO_DARK.getContext('2d'); g.drawImage(LOGO, 0, 0); g.globalCompositeOperation = 'source-in'; g.fillStyle = '#2a1d1a'; g.fillRect(0, 0, LOGO_DARK.width, LOGO_DARK.height); }
    if (pa < 1) { c.save(); c.globalAlpha = 0.9 * topA * (1 - pa); c.drawImage(LOGO, CX - lw / 2, 150, lw, lh); c.restore(); }
    if (pa > 0) { c.save(); c.globalAlpha = 0.92 * topA * pa; c.drawImage(LOGO_DARK, CX - lw / 2, 150, lw, lh); c.restore(); }
    T(c, 'SÖZÜMÜN CANI', CX, 150 + lh + 60, { ff: IN, wt: 500, sz: 22, ls: 8, col: pa > 0.5 ? '#5a4036' : GOLD_L, a: 0.8 * topA });
  }
  const endK = eio(p(t, 54.9, 56.0));
  if (endK > 0) {
    const lw = 380, lh = lw * ar, y0 = 360;
    c.save(); c.globalAlpha = endK; c.drawImage(LOGO, CX - lw / 2, y0 + (1 - endK) * 18, lw, lh); c.restore();
    letters(c, 'SÖZÜMÜN CANI', CX, y0 + lh + 92, { ff: FR, wt: 400, sz: 52, ls: 14, col: CREAM }, (i) => { const ti = 55.8 + i * 0.07; const r = sm(p(t, ti, ti + 0.6)); return { a: r, dy: (1 - r) * 12, blur: (1 - r) * 6 }; });
  }
}

// ================= SCENES =================
// Z1 — Vidadi's lines in ink on pale paper; black strands fall beside a pale chin and settle in a dimple
const STR = (() => { const r = rng(23), a = []; for (let i = 0; i < 14; i++) a.push({ x: 300 + r() * 480, ph: r() * 6, len: 260 + r() * 200, d: r(), small: i >= 8 }); return a; })();
const VO = { ff: 'FR', it: true, wt: 400, sz: 66, col: INK, blurIn: 8 };
function wordX(c, words, idx, o) { c.save(); font(c, o); const sp = c.measureText(' ').width; const ws = words.map(w => c.measureText(w).width); const total = ws.reduce((a, b) => a + b, 0) + sp * (words.length - 1); let x = CX - total / 2; for (let i = 0; i < idx; i++) x += ws[i] + sp; c.restore(); return x + ws[idx] / 2; }
const REV = LINES[3].w[7][1];
function z1(c, t, noWord) {
  paper(c, 1);
  const L0 = LINES[0].w, L1 = LINES[1].w, L2 = LINES[2].w; c.__t = t;
  const fadeAll = 1 - sm(p(t, 8.6, 9.6));
  c.save(); c.globalAlpha = fadeAll;
  // a big opening quotation mark, drawn from the first frame
  const q = eo(p(t, 0.0, 0.9));
  T(c, '“', CX, 520 + (1 - q) * 30, { ff: FR, it: true, wt: 400, sz: 260, col: TERRA, a: q * 0.85 });
  wordsLine(c, [{ s: 'Molla', t: L0[0][1] }, { s: 'Vəli', t: L0[1][1] }, { s: 'Vidadi', t: L0[2][1] }], CX, 610, { ff: IN, wt: 600, sz: 30, ls: 9, col: '#6b4a3c' });
  wordsLine(c, [{ s: 'yazırdı', t: L0[3][1] }], CX, 662, { ff: FR, it: true, wt: 300, sz: 40, col: '#6b4a3c' });
  // the chin: a pale, soft curve (buxaq) with the strands beside it
  const chin = eo(p(t, L1[2][1] - 0.2, L1[3][1] + 0.6)); // "ağ buxağın"
  const cy = 1190;
  if (chin > 0) {
    c.save(); c.globalAlpha = chin; const g = c.createRadialGradient(CX, cy - 60, 20, CX, cy - 40, 300); g.addColorStop(0, 'rgba(255,250,242,0.95)'); g.addColorStop(1, 'rgba(255,250,242,0)'); c.fillStyle = g; c.beginPath(); c.ellipse(CX, cy - 70, 300, 210, 0, 0, 7); c.fill(); c.restore();
    fineLine(c, CX, cy, 360 * chin, 70, { lw: 2.6, col: '#8a6250', a: 0.9 });
  }
  // strands: black ones beside the chin (siyah tellər), then small ones falling into the dimple (xırda tellər)
  const dX = CX + 128, dY = cy + 40;
  STR.forEach((s, i) => {
    if (!s.small) {
      const a = sm(p(t, L1[0][1] + s.d * 0.9, L1[0][1] + s.d * 0.9 + 0.9));
      if (a <= 0) return;
      const side = i % 2 ? 1 : -1, x = CX + side * (190 + s.d * 80);
      strand(c, x, 700 - s.d * 60, lerp(120, s.len + 120, a), t, s.ph, { w: 1.6, a: a * 0.9, curl: side * 0.6 });
    } else {
      const st = L2[0][1] + (i - 8) * 0.16, f = eio(p(t, st, st + 1.5));
      if (f <= 0) return;
      const x0 = lerp(CX - 60 + (i - 8) * 30, dX - 20 + (i - 8) * 6, f), y0 = lerp(780, dY - 120, f);
      strand(c, x0, y0, lerp(160, 110, f), t * (1 - f), s.ph, { w: 1.1, a: 0.85, sway: 1 - f * 0.8, curl: 0.25 * f });
    }
  });
  dimple(c, dX, dY, 16, sm(p(t, L2[2][1] - 0.1, L2[2][1] + 0.6)), TERRA, 6);
  // the verse
  const vo = VO;
  wordsLine(c, [{ s: 'Siyah', t: L1[0][1] }, { s: 'tellər', t: L1[1][1] }, { s: 'ağ', t: L1[2][1] }, { s: 'buxağın', t: L1[3][1] }, { s: 'yanına,', t: L1[4][1] }], CX, 800, vo);
  wordsLine(c, [{ s: 'Xırda', t: L2[0][1] }, { s: 'tellər', t: L2[1][1] }, { s: 'zənəxdana', t: L2[2][1], a: 0 }, { s: 'düşübdü.', t: L2[3][1] }], CX, 895, vo);
  c.restore();
  // the word itself stays at full strength until it lifts into the title
  if (!noWord && t < REV - 0.5) { const k = said(t, L2[2][1]); T(c, 'zənəxdana', wordX(c, ['Xırda', 'tellər', 'zənəxdana', 'düşübdü.'], 2, VO), 895 + (1 - k) * 18, Object.assign({}, VO, { col: TERRA, a: k, blur: (1 - k) * 8 })); }
}
// Z2 — "bu günün sözü": the word rises from the verse into the title, paper warms into dawn
function z2(c, t) {
  const pp = 1 - eio(p(t, 8.9, 10.4));
  z1(c, t, true);
  c.save(); c.globalAlpha = 1 - pp; dawn(c, { warm: 0.4, gy: 960 }); c.restore(); specks(c, t, 0.4 * (1 - pp));
  const L3 = LINES[3].w; c.__t = t;
  wordsLine(c, [{ s: 'Bəli,', t: L3[0][1] }], CX, 640, { ff: FR, it: true, wt: 300, sz: 48, col: pp > 0.5 ? '#6b4a3c' : GOLD_L, a: 1 - sm(p(t, 9.0, 9.5)) });
  wordsLine(c, [{ s: 'bu', t: L3[1][1] }, { s: 'günün', t: L3[2][1] }, { s: 'sözü', t: L3[3][1] }], CX, 700, { ff: FR, it: true, wt: 300, sz: 54, col: GOLD_L, a: 1 - pp * 0.6 });
  const rev = L3[7][1];
  const k = eio(p(t, rev - 0.5, rev + 0.4));
  const x0 = wordX(c, ['Xırda', 'tellər', 'zənəxdana', 'düşübdü.'], 2, VO);
  const y = lerp(895, 980, k), sz = lerp(66, 168, k), wx = lerp(x0, CX, k);
  const fn = { ff: FR, it: k < 0.5, wt: k < 0.5 ? 400 : 600, sz, ls: lerp(0, 10, k) };
  const word = k < 0.5 ? 'zənəxdana' : 'ZƏNƏXDAN';
  const sw = k < 0.5 ? 1 - k * 2 : (k - 0.5) * 2;
  if (t < rev - 0.5) T(c, 'zənəxdana', x0, 895, Object.assign({}, VO, { col: TERRA }));
  else T(c, word, wx, y, Object.assign({}, fn, { col: k < 0.5 ? TERRA : warmGrad(c, y - 140, y), a: sw, glow: 20 * k, glowCol: 'rgba(243,190,150,0.6)' }));
  // the smile line draws beneath the word, a dimple at its end
  const sl = eo(p(t, rev, rev + 0.9));
  if (sl > 0) { fineLine(c, CX, 1060, 700 * sl, 34, { lw: 5, col: PEACH, glow: 14 }); dimple(c, CX + 350 * sl + 20, 1050, 13, sl, PEACH); }
}
// Z3 — the meaning: a fine line that appears when we smile
function z3(c, t) {
  const L = LINES[4].w; c.__t = t;
  dawn(c, { warm: 0.45, gy: 960 }); specks(c, t, 0.4);
  const up = eio(p(t, 12.5, 13.3));
  const wy = lerp(980, 560, up), wsz = lerp(168, 112, up);
  T(c, 'ZƏNƏXDAN', CX, wy, { ff: FR, wt: 600, sz: wsz, ls: lerp(10, 8, up), col: warmGrad(c, wy - 100, wy), glow: 16, glowCol: 'rgba(243,190,150,0.5)' });
  T(c, 'qəmzə', CX, 760, { ff: FR, it: true, wt: 300, sz: 96, col: CREAM, a: said(t, L[3][1], 0.5), blur: (1 - said(t, L[3][1], 0.5)) * 10 });
  // the line: flat -> smiling when "güləndə"; dimple on "üzdə"; thins to a fine stroke on "incə cizgi"
  const smileK = eio(p(t, L[5][1] - 0.1, L[5][1] + 0.7));
  const fine = eio(p(t, L[9][1], L[10][1] + 0.4));
  const draw = eo(p(t, 12.6, 13.4));
  fineLine(c, CX, 1060 - smileK * 10, 700, lerp(34, 70, smileK), { lw: lerp(5, 2.2, fine), col: PEACH, glow: 14, draw, lift: smileK * 20 });
  const dk = said(t, L[6][1], 0.6);
  dimple(c, CX + 372, 1030 - smileK * 30, lerp(13, 18, dk), Math.max(draw, dk), PEACH, 8 + 14 * dk);
  dimple(c, CX - 372, 1030 - smileK * 30, 18, dk, PEACH, 8 + 14 * dk);
  wordsLine(c, [{ s: 'o', t: L[8][1] }, { s: 'incə', t: L[9][1] }, { s: 'cizgi', t: L[10][1] }], CX, 1240, { ff: FR, it: true, wt: 300, sz: 64, col: GOLD_L });
}
// Z4 — morning rush, traffic; the smile is dragged down into a frown
function z4(c, t) {
  const L = LINES[5].w; c.__t = t;
  const gk = eio(p(t, 18.3, 19.4));
  dawn(c, { warm: 0.45 * (1 - gk), grey: gk, gy: 820 });
  // traffic: rows of brake lights in perspective, crawling
  const tk = said(t, L[3][1], 0.8);
  if (tk > 0) {
    c.save(); c.globalCompositeOperation = 'lighter';
    for (let row = 0; row < 9; row++) {
      const z = (row + ((t * 0.12) % 1)) / 9, y = lerp(820, 1500, z * z), sc = lerp(0.25, 1.4, z * z);
      for (let lane = -2; lane <= 2; lane++) {
        const x = CX + lane * 210 * sc + Math.sin(row * 3 + lane) * 10;
        const br = (0.55 + 0.45 * Math.sin(t * 1.5 + row + lane * 2)) * tk * (0.4 + 0.6 * z);
        for (const dx of [-38, 38]) glw(c, x + dx * sc, y, 26 * sc + 6, '255,70,55', 0.55 * br);
      }
    }
    c.restore();
    c.save(); c.globalAlpha = tk * 0.5; c.strokeStyle = 'rgba(154,163,173,0.4)'; c.lineWidth = 2; for (const s of [-1, 1]) { c.beginPath(); c.moveTo(CX + s * 20, 800); c.lineTo(CX + s * 700, 1600); c.stroke(); } c.restore();
  }
  wordsLine(c, [{ s: 'Səhər-səhər', t: L[0][1] }], CX, 500, { ff: FR, it: true, wt: 300, sz: 74, col: CREAM });
  wordsLine(c, [{ s: 'işə', t: L[1][1] }, { s: 'tələsəndə', t: L[2][1] }], CX, 580, { ff: IN, wt: 500, sz: 30, ls: 8, col: GREY });
  // the line from Z3 arrives smiling, then turns into a frown and sinks ("yerlə gedir")
  const frown = eio(p(t, L[7][1] - 0.2, L[7][1] + 0.8)), sink = ei(p(t, L[8][1], L[9][1] + 0.6));
  const ly = lerp(1060, 1430, sink) + 0;
  const col = `rgb(${Math.round(lerp(242, 154, gk))},${Math.round(lerp(185, 163, gk))},${Math.round(lerp(160, 173, gk))})`;
  fineLine(c, CX, ly, lerp(700, 560, frown), lerp(60, -70, frown), { lw: lerp(2.2, 4, frown), col, glow: 8 * (1 - gk), lift: lerp(20, -20, frown), a: 1 - sm(p(t, 24.2, 24.9)) });
  // "qaşqabaq": a frowning baseline
  const qk = said(t, L[7][1], 0.5);
  letters(c, 'qaşqabaq', CX, 900 + sink * 80, { ff: FR, it: true, wt: 400, sz: 104, col: '#c9ced4' }, (i, n) => { const u = (i - (n - 1) / 2) / ((n - 1) / 2); return { a: qk * (1 - sm(p(t, 24.2, 24.9))), dy: (u * u) * 60 * frown - (1 - u * u) * 10 * frown, rot: u * 0.22 * frown, blur: (1 - qk) * 8 }; });
}
// Z5 — closed doors open onto warm light; hardness softens; a sincere smile
function z5(c, t) {
  const L = LINES[6].w; c.__t = t;
  const open = eio(p(t, L[3][1] - 0.15, L[3][1] + 1.2));
  dawn(c, { grey: 0.8 * (1 - open), warm: 0.7 * open, gy: 900 });
  // light behind the doors
  glw(c, CX, 900, 900 * open + 1, '255,214,165', 0.55 * open);
  const dw = 230, dh = 640, dy = 600;
  const dA = sm(p(t, L[1][1] - 0.2, L[1][1] + 0.4)) * (1 - sm(p(t, 28.2, 29.0)));
  if (dA > 0) {
    c.save(); c.globalAlpha = dA;
    for (const s of [-1, 1]) {
      const w = dw * Math.cos(open * 1.25); // swinging open
      const x0 = s < 0 ? CX - dw : CX + dw - w; // hinged at the outer edges: a gap of light opens in the middle
      c.fillStyle = '#2b2a31'; c.fillRect(x0, dy, w, dh);
      c.strokeStyle = 'rgba(243,205,140,0.6)'; c.lineWidth = 2; c.strokeRect(x0 + 18 * Math.cos(open), dy + 22, w - 36 * Math.cos(open), dh - 44);
      c.fillStyle = SUN; c.beginPath(); c.arc(s < 0 ? x0 + w - 20 : x0 + 20, dy + dh / 2, 6, 0, 7); c.fill();
    }
    c.restore();
  }
  T(c, 'qapalı qapılar', CX, 520, { ff: FR, it: true, wt: 300, sz: 62, col: CREAM, a: said(t, L[1][1]) * (1 - sm(p(t, 27.4, 28.0))) });
  // "çətin vəziyyət" — a jagged line that softens ("yumşaldan")
  const jg = said(t, L[5][1], 0.4) * (1 - sm(p(t, 30.2, 30.8))), soft = eio(p(t, L[8][1] - 0.1, L[8][1] + 0.9));
  if (jg > 0) {
    c.save(); c.globalAlpha = jg; c.strokeStyle = soft > 0.5 ? PEACH : '#c9ced4'; c.lineWidth = 3; c.lineJoin = 'round'; c.beginPath();
    for (let x = 160; x <= 920; x += 6) { const ph = (x - 160) / 60, tri = Math.abs((ph % 2) - 1) * 2 - 1, sn = Math.sin(ph * Math.PI); const y = 1335 + lerp(tri, sn, soft) * lerp(40, 24, soft); x === 160 ? c.moveTo(x, y) : c.lineTo(x, y); }
    c.stroke(); c.restore();
    T(c, 'ən çətin vəziyyət', CX, 1278, { ff: IN, wt: 500, sz: 28, ls: 8, col: GREY, a: jg * (1 - soft * 0.5) });
  }
  // the strongest "weapon": a sincere smile, glowing in the doorway
  const sk = said(t, L[13][1], 0.6), tb = said(t, L[15][1], 0.8);
  T(c, 'ən güclü silahımız', CX, 560, { ff: IN, wt: 500, sz: 28, ls: 8, col: SUN, a: said(t, L[10][1]) * (1 - tb) });
  if (sk > 0) { fineLine(c, CX, 960, 520, 64, { lw: 6, col: warmGrad(c, 900, 1100), glow: 30, draw: eo(sk), lift: 18 }); dimple(c, CX + 282, 930, 16, sk, '#fff0dc', 18); dimple(c, CX - 282, 930, 16, sk, '#fff0dc', 18); }
  T(c, 'təbəssüm', CX, 1250, { ff: FR, it: true, wt: 400, sz: 150, col: warmGrad(c, 1130, 1260), a: tb, blur: (1 - tb) * 14, glow: 24, glowCol: 'rgba(243,190,150,0.6)' });
  T(c, 'səmimi', CX, 1080, { ff: FR, it: true, wt: 300, sz: 58, col: CREAM, a: said(t, L[13][1]) * 0.9 });
}
// Z6 — tension: a tangled knot; no need for long words; a smile is enough — the knot unties
function z6(c, t) {
  const L7 = LINES[7].w, L8 = LINES[8].w; c.__t = t;
  const untie = eio(p(t, L8[1][1] - 0.2, L8[1][1] + 1.3));
  dawn(c, { warm: 0.2 + 0.5 * untie, grey: 0.4 * (1 - untie), gy: 960 }); specks(c, t, 0.3);
  const kn = sm(p(t, 33.2, 33.9));
  // knot: a looping line whose loops relax into the smile curve
  c.save(); c.globalAlpha = kn; c.strokeStyle = untie > 0.5 ? PEACH : '#d3c3bc'; c.lineWidth = 3.2; c.lineCap = 'round'; c.shadowColor = 'rgba(243,190,150,0.5)'; c.shadowBlur = 10 * untie;
  const vib = (1 - untie) * Math.sin(t * 40) * 1.6;
  c.beginPath();
  for (let i = 0; i <= 400; i++) {
    const u = i / 400, x = lerp(140, 940, u);
    const loopsA = (1 - untie) * 90 * Math.sin(u * Math.PI);
    const ang = u * Math.PI * 2 * 5;
    const yS = 980 + 70 * Math.pow((u - 0.5) * 2, 2) * -1 + 70; // smile curve (∪)
    const px = x + Math.cos(ang) * loopsA * 0.7, py = lerp(980, yS - 70, untie) + Math.sin(ang) * loopsA + vib;
    i ? c.lineTo(px, py) : c.moveTo(px, py);
  }
  c.stroke(); c.restore();
  if (untie > 0.6) { const a = p(untie, 0.6, 1); dimple(c, 958, 905, 15, a, PEACH, 14); dimple(c, 122, 905, 15, a, PEACH, 14); }
  T(c, 'gərginlik', CX, 640, { ff: FR, it: true, wt: 400, sz: 100, col: '#d3c3bc', a: said(t, L7[0][1], 0.5) * (1 - untie), blur: (1 - said(t, L7[0][1], 0.5)) * 10 });
  // "uzun sözlər" — a long stream of small words that thins out ("ehtiyac qalmır")
  const ls = said(t, L7[6][1], 0.4), gone = sm(p(t, L7[9][1] - 0.1, L7[9][1] + 0.5));
  if (ls > 0 && gone < 1) {
    const stream = 'söz söz söz söz söz söz söz söz söz söz söz söz söz söz söz söz söz söz';
    T(c, stream, CX - 200 + ((t * 120) % 200), 1220, { ff: FR, it: true, wt: 300, sz: 34, col: GREY, a: ls * (1 - gone) * 0.8 });
  }
  T(c, 'gülümsəmək', CX, 640, { ff: FR, it: true, wt: 400, sz: 112, col: warmGrad(c, 540, 650), a: said(t, L8[1][1], 0.6), glow: 20, glowCol: 'rgba(243,190,150,0.6)' });
  T(c, 'bəs edir', CX, 1230, { ff: IN, wt: 500, sz: 30, ls: 10, col: SUN, a: said(t, L8[2][1], 0.5) });
}
// Z7 — daily worries crowd; may they not take you from yourself; the smile is not erased
const WORRY = (() => { const r = rng(55), a = []; for (let i = 0; i < 18; i++) a.push({ a: r() * 6.28, r: 300 + r() * 260, ph: r() * 6, d: r() }); return a; })();
function z7(c, t) {
  const L9 = LINES[9].w, L10 = LINES[10].w; c.__t = t;
  dawn(c, { warm: 0.55, gy: 960 }); specks(c, t, 0.4);
  const cx = CX, cy = 960;
  // you: a warm light; worries circle in, then are pushed away on "uzaqlaşdırmasın"
  const you = sm(p(t, 39.6, 40.4)) * (1 - sm(p(t, 44.3, 44.9)));
  glw(c, cx, cy, 220, '255,210,165', 0.45 * you); glw(c, cx, cy, 18, '255,245,230', 0.95 * you);
  const qk = said(t, L9[5][1], 0.8), push = eio(p(t, L9[8][1], L9[8][1] + 1.0));
  WORRY.forEach((w, i) => {
    const a = clamp(qk * 2 - w.d) * (1 - push) * you; if (a <= 0) return;
    const rr = lerp(w.r, w.r * 0.45, qk) + push * 500, ang = w.a + t * 0.15;
    T(c, 'qayğı', cx + Math.cos(ang) * rr, cy + Math.sin(ang) * rr * 0.9, { ff: FR, it: true, wt: 300, sz: 34, col: GREY, a: a * 0.75 });
  });
  T(c, 'özünüzdən', CX, 560, { ff: FR, it: true, wt: 300, sz: 70, col: CREAM, a: said(t, L9[7][1], 0.5) * (1 - sm(p(t, 44.0, 44.5))) });
  // the smile, the dimple — and an eraser that passes without erasing it
  const sm2 = eio(p(t, L10[0][1] - 0.2, L10[3][1] + 0.4));
  if (sm2 > 0) {
    fineLine(c, CX, 1000, 600, 60, { lw: 5, col: warmGrad(c, 950, 1100), glow: 24, draw: sm2, lift: 18 });
    const dk = said(t, L10[3][1], 0.6); dimple(c, CX + 330, 975, 17, dk, '#fff0dc', 20); dimple(c, CX - 330, 975, 17, dk, '#fff0dc', 20);
    T(c, 'şirin zənəxdan', CX, 640, { ff: FR, it: true, wt: 400, sz: 84, col: warmGrad(c, 570, 650), a: said(t, L10[3][1], 0.6) });
    const er = p(t, L10[6][1] - 0.1, L10[8][1] + 0.4);
    if (er > 0 && er < 1) { const x = lerp(-150, W + 150, eio(er)); const g = c.createLinearGradient(x - 120, 0, x + 120, 0); g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(0.5, 'rgba(255,240,225,0.18)'); g.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = g; c.fillRect(x - 120, 860, 240, 260); c.save(); c.globalAlpha = 0.6; c.fillStyle = '#e9ddd2'; c.beginPath(); c.roundRect(x - 50, 1120, 100, 40, 8); c.fill(); c.restore(); }
    const keep = said(t, L10[8][1], 0.6);
    T(c, 'heç vaxt silinməsin', CX, 1250, { ff: FR, it: true, wt: 300, sz: 62, col: CREAM, a: keep });
    glw(c, CX, 1000, 420, '255,214,165', 0.25 * keep * (0.8 + 0.2 * Math.sin(t * 3)));
  }
}
// Z8 — the word falls into place on a smiling baseline; sign-off
function z8(c, t) {
  const L = LINES[11].w; c.__t = t;
  dawn(c, { warm: 0.6, gy: 1000 }); specks(c, t, 0.45);
  const base = 1010, draw = eo(p(t, 49.6, 50.5));
  const P0 = [CX - 450, base - 60], P1 = [CX, base + 90], P2 = [CX + 450, base - 60];
  fineLine(c, CX, base + 25 - 60 + 60, 900, 75 - 0, { lw: 3, col: PEACH, glow: 12, draw, lift: 60 });
  const word = 'ZƏNƏXDAN', n = [...word].length;
  // each letter sits on the curve, tilted to its tangent: the word smiles
  c.save(); font(c, { ff: FR, wt: 600, sz: 128, ls: 6 }); const total = c.measureText(word).width; c.restore();
  let acc = 0; const chars = [...word];
  chars.forEach((ch, i) => {
    c.save(); font(c, { ff: FR, wt: 600, sz: 128, ls: 6 }); const cw = c.measureText(ch).width; c.restore();
    const u = clamp((acc + cw / 2) / total * 0.86 + 0.07); acc += cw;
    const q = qpt(P0, P1, P2, u), tg = qtan(P0, P1, P2, u), ang = Math.atan2(tg[1], tg[0]);
    const st = 50.45 + i * 0.19, f = p(t, st, st + 0.6), fall = 1 - eo(f);
    c.save(); c.translate(q[0], q[1] - 14 - fall * 900); c.rotate(ang * eo(f) + (1 - f) * (i % 2 ? 0.3 : -0.3));
    T(c, ch, 0, 0, { ff: FR, wt: 600, sz: 128, col: warmGrad(c, -110, 0), a: f > 0 ? 1 : 0, glow: 16, glowCol: 'rgba(243,190,150,0.5)' });
    c.restore();
  });
  const ta = 1 - sm(p(t, 54.3, 54.9));
  wordsLine(c, [{ s: 'Söz', t: L[0][1] }, { s: 'yerinə', t: L[1][1] }, { s: 'düşdü.', t: L[2][1] }], CX, 1240, { ff: FR, it: true, wt: 300, sz: 62, col: CREAM, a: ta });
  wordsLine(c, [{ s: 'Gələn', t: L[3][1] }, { s: 'sözlərə', t: L[4][1] }, { s: 'qədər.', t: L[5][1] }], CX, 1325, { ff: FR, it: true, wt: 300, sz: 48, col: SUN, a: ta * 0.9 });
}

const SCENES = [
  [0, 8.4, 0, 0.0, z1],
  [8.4, 12.5, 0, 0.0, z2],
  [12.5, 18.4, 0, 0.45, z3],
  [18.3, 24.6, 0.3, 0.4, z4],
  [24.5, 33.0, 0.35, 0.4, z5],
  [33.0, 39.6, 0.35, 0.4, z6],
  [39.5, 49.6, 0.4, 0.45, z7],
  [49.4, 60, 0.4, 0, z8],
];
function render(t, fr = 0) {
  X.save(); X.fillStyle = '#000'; X.fillRect(0, 0, W, H);
  for (const [a, b, fi, fo, fn] of SCENES) {
    if (t < a - fi || t > b + fo) continue;
    const al = Math.min(fi ? sm(p(t, a - fi, a + fi * 0.2)) : 1, fo ? 1 - sm(p(t, b - fo * 0.2, b + fo)) : 1);
    if (al <= 0) continue;
    LC.setTransform(1, 0, 0, 1, 0, 0); LC.globalAlpha = 1; LC.globalCompositeOperation = 'source-over'; LC.filter = 'none'; LC.clearRect(0, 0, W, H);
    LC.save(); fn(LC, t); LC.restore();
    X.globalAlpha = al; X.drawImage(layer, 0, 0); X.globalAlpha = 1;
  }
  const onPaper = t < 9 ? 1 : 1 - eio(p(t, 8.9, 10.4));
  branding(X, t, t < 10.4 ? onPaper : 0);
  captions(X, t);
  finish(X, t, fr);
  const fa = sm(p(t, DUR - 0.8, DUR));
  if (fa > 0) { X.fillStyle = `rgba(0,0,0,${fa})`; X.fillRect(0, 0, W, H); }
  X.restore();
}
window.render = render; window.DUR = DUR;
window.frameJPEG = (t, fr) => { render(t, fr); return cv.toDataURL('image/png'); };
