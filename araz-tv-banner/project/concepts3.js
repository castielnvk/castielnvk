// Araz FM TV banner — round 3 concepts (NO buta anywhere). Canvas 1920x1080, transparent.
// window.render3(ctx, concept, t, A, TL); concepts: SILK, EQ, GIRIH, DIAL, SILKEQ
const GOLD = '#D9B45A', IVORY = '#F6EBD2', RUBY = '#B3202E', INDIGO = '#1E2C58', TEAL = '#095D6A', TEAL_L = '#7FD1D6';
const FLAG = ['#00B5E2', '#EF3340', '#509E2F'];
const LINES = [
  { text: 'Azərbaycanın səsi bu dalğada!', tag: '103.3 FM' },
  { text: 'Bizə rəqəmsalda da qoşul!', social: true },
  { text: 'Milli musiqinin dəyişməz ünvanı!', flag: true },
  { logo: true, text: 'QOVUŞDURAN RADİO!' },
];
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eOut = p => 1 - Math.pow(1 - p, 3), eIn = p => p * p * p;
const eIO = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const eBack = p => { const c = 1.7; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
const hash = (i, j = 0) => { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); };
const seg = (t, a, b) => clamp((t - a) / (b - a));
const rr = (c, x, y, w, h, r) => { c.beginPath(); c.roundRect(x, y, w, h, r); };
const mixc = (a, b, p) => { const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
  const f = k => Math.round(((pa >> k) & 255) * (1 - p) + ((pb >> k) & 255) * p); return `rgb(${f(16)},${f(8)},${f(0)})`; };

function star8(c, cx, cy, r, fill) {
  c.save(); c.translate(cx, cy); c.fillStyle = fill;
  for (let k = 0; k < 2; k++) { c.save(); c.rotate(k * Math.PI / 4); c.fillRect(-r * .72, -r * .72, r * 1.44, r * 1.44); c.restore(); }
  c.restore();
}
function star8Path(c, cx, cy, r, inner = .76) {
  c.beginPath();
  for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8 - Math.PI / 2, rad = i % 2 ? r * inner : r;
    const x = cx + Math.cos(a) * rad, y = cy + Math.sin(a) * rad; i ? c.lineTo(x, y) : c.moveTo(x, y); }
  c.closePath();
}
function rhombus(c, cx, cy, rx, ry) { c.beginPath(); c.moveTo(cx, cy - ry); c.lineTo(cx + rx, cy); c.lineTo(cx, cy + ry); c.lineTo(cx - rx, cy); c.closePath(); }
function socialIcon(c, k, s, col) {
  c.save(); c.strokeStyle = col; c.fillStyle = col; c.lineWidth = s * .09;
  if (k === 0) { c.font = `800 ${s * 1.05}px Montserrat`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('f', 0, s * .04); }
  if (k === 1) { rr(c, -s / 2, -s / 2, s, s, s * .28); c.stroke(); c.beginPath(); c.arc(0, 0, s * .22, 0, 7); c.stroke(); c.beginPath(); c.arc(s * .26, -s * .26, s * .06, 0, 7); c.fill(); }
  if (k === 2) { rr(c, -s * .68, -s * .46, s * 1.36, s * .92, s * .26); c.stroke(); c.beginPath(); c.moveTo(-s * .16, -s * .22); c.lineTo(s * .24, 0); c.lineTo(-s * .16, s * .22); c.closePath(); c.fill(); }
  c.restore();
}

// ---------- shared text layout → items (chars + units)
function layout(c, li, A, o) {
  const L = LINES[li], items = [], FS = o.fs, cy = o.cy, [x0, x1] = o.area, mid = (x0 + x1) / 2;
  const chars = (txt, x, font) => { c.font = font; let w = 0; for (const ch of txt) { const cw = c.measureText(ch).width; items.push({ ch, x: x + w + cw / 2, font }); w += cw; } };
  const fMain = `700 ${FS}px Montserrat`, fTag = `800 ${FS * .7}px Montserrat`, fUrl = `700 ${FS * .7}px Montserrat`;
  if (L.logo) {
    const img = o.logo, lh = o.logoH, lw = img.width * lh / img.height, fT = `800 ${FS * .9}px Montserrat`;
    c.font = fT; const tw = c.measureText(L.text).width, gap = 34, W = lw + gap * 2 + tw, sx = mid - W / 2;
    items.push({ unit: c => c.drawImage(img, -lw / 2, -lh / 2, lw, lh), x: sx + lw / 2 });
    items.push({ unit: c => { c.fillStyle = o.accent; c.fillRect(-1.5, -lh * .42, 3, lh * .84); }, x: sx + lw + gap });
    chars(L.text, sx + lw + gap * 2, fT); return { items, cy };
  }
  c.font = fMain; const tw = c.measureText(L.text).width; let extra = 0, tagW = 0;
  if (L.tag) { c.font = fTag; tagW = c.measureText(L.tag).width + 46; extra = 90 + tagW; }
  if (L.social) { c.font = fUrl; extra = 62 + 3 * 52 + 20 + c.measureText('arazfm.az').width; }
  const sx = mid - (tw + extra) / 2;
  if (L.flag) items.push({ unit: c => star8(c, 0, 0, 15, FLAG[0]), x: sx - 44 });
  chars(L.text, sx, fMain); let x = sx + tw;
  if (L.flag) items.push({ unit: c => star8(c, 0, 0, 15, FLAG[2]), x: x + 44 });
  if (L.tag) {
    x += 30; items.push({ unit: c => star8(c, 0, 0, 12, o.accent), x: x + 15 }); x += 60;
    items.push({ unit: c => { rr(c, -tagW / 2, -FS * .62, tagW, FS * 1.24, FS * .62); c.fillStyle = o.tagBg; c.fill(); c.font = fTag; c.fillStyle = o.tagCol; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(L.tag, 0, 2); }, x: x + tagW / 2 });
  }
  if (L.social) { x += 62; for (let k = 0; k < 3; k++) items.push({ unit: c => socialIcon(c, k, 32, o.col), x: x + 18 + k * 52 }); x += 3 * 52 + 20; chars('arazfm.az', x, fUrl); }
  return { items, cy };
}
function drawItems(c, L, o, anim) {
  const n = L.items.length;
  L.items.forEach((it, i) => {
    const m = anim(i, n, it); if (!m || m.a <= .003) return;
    c.save(); c.globalAlpha = clamp(m.a); c.translate(it.x + (m.dx || 0), L.cy + (m.dy || 0)); c.rotate(m.rot || 0); c.scale(m.s || 1, m.s || 1);
    if (o.shadow) { c.shadowColor = o.shadow; c.shadowBlur = 10; c.shadowOffsetY = 3; }
    if (it.unit) it.unit(c);
    else { c.font = it.font; c.fillStyle = m.fill || o.col; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(it.ch, 0, 2); }
    c.restore();
  });
}
// state of the line timeline
function lineState(t, TL) {
  let k = -1; for (let i = 0; i < TL.changes.length; i++) if (t >= TL.changes[i]) k = i;
  const tc = k >= 0 ? t - TL.changes[k] : -1;
  const newL = k >= 0 ? TL.lines[k] : null, oldL = k > 0 ? TL.lines[k - 1] : null;
  const flag = newL === 2 ? eOut(seg(tc, .1, .8)) : (oldL === 2 && tc >= 0 ? 1 - eOut(seg(tc, .1, .8)) : 0);
  return { k, tc, newL, oldL, flag };
}

// =====================================================================
// 1. SILK — kəlağayı: geometric-print silk band, waving; wave carries the text change
const SILK = {
  pat: null,
  makePattern(base1, base2) {
    const W = 1920, H = 236, cv = document.createElement('canvas'); cv.width = W; cv.height = H; const c = cv.getContext('2d');
    const g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, base1); g.addColorStop(1, base2); c.fillStyle = g; c.fillRect(0, 0, W, H);
    // diagonal lattice print
    c.strokeStyle = 'rgba(217,180,90,.22)'; c.lineWidth = 1.5;
    for (let x = -H; x < W + H; x += 46) { c.beginPath(); c.moveTo(x, 30); c.lineTo(x + 176, H - 30); c.stroke(); c.beginPath(); c.moveTo(x + 176, 30); c.lineTo(x, H - 30); c.stroke(); }
    // rosettes at lattice nodes
    for (let x = 0; x < W + 46; x += 46) for (let r = 0; r < 4; r++) {
      const cx = x + (r % 2) * 23, cy = 30 + 22 + r * 44;
      if (cy > H - 34) continue;
      star8Path(c, cx, cy, 7, .55); c.fillStyle = 'rgba(246,235,210,.30)'; c.fill();
      c.beginPath(); c.arc(cx, cy, 2, 0, 7); c.fillStyle = 'rgba(217,180,90,.6)'; c.fill();
    }
    // printed borders (top & bottom): stripes + triangle teeth + dots
    for (const [y0, dir] of [[0, 1], [H, -1]]) {
      c.fillStyle = 'rgba(246,235,210,.92)'; c.fillRect(0, dir > 0 ? y0 + 4 : y0 - 7, W, 3);
      c.fillStyle = GOLD; c.fillRect(0, dir > 0 ? y0 + 10 : y0 - 12, W, 2);
      for (let x = 0; x < W; x += 18) { c.beginPath(); const yb = dir > 0 ? y0 + 13 : y0 - 13; c.moveTo(x, yb); c.lineTo(x + 9, yb + dir * 11); c.lineTo(x + 18, yb); c.closePath(); c.fillStyle = 'rgba(246,235,210,.85)'; c.fill(); }
      for (let x = 9; x < W; x += 36) { c.beginPath(); c.arc(x, dir > 0 ? y0 + 30 : y0 - 30, 2.2, 0, 7); c.fillStyle = 'rgba(217,180,90,.8)'; c.fill(); }
    }
    return cv;
  },
  opts(A) { return { fs: 54, cy: 984, area: [160, 1760], col: '#FFFDF6', accent: GOLD, tagBg: IVORY, tagCol: '#073F48', logo: A.white, logoH: 74, shadow: 'rgba(0,0,0,.55)' }; },
  wave(x, t, extra) { return 5 * Math.sin(x / 170 - t * 2.1) + 3 * Math.sin(x / 63 - t * 3.3 + 1) * .4 + extra(x); },
  drawCloth(c, t, ip, bump, top = 872) {
    if (!this.pat) { this.pat = this.makePattern('#0C6A77', '#063A43'); this.patFlag = this.makePattern('#0C6A77', '#063A43'); }
    const sw = 6;
    for (let x = 0; x < 1920; x += sw) {
      const d = seg(ip, x / 1920 * .55, x / 1920 * .55 + .45); if (d <= 0) continue;
      const unf = (1 - eOut(d));
      const ext = xx => bump(xx) + unf * 70 * Math.sin(xx / 60 + t * 6);
      const off = this.wave(x, t, ext), slope = this.wave(x + 3, t, ext) - this.wave(x - 3, t, ext);
      const y = top + off + unf * 40;
      c.globalAlpha = eOut(d);
      c.drawImage(this.pat, x, 0, sw, 236, x, y, sw + .6, 236);
      const sh = clamp(slope / 6, -1, 1);
      c.fillStyle = sh > 0 ? `rgba(255,248,230,${sh * .22})` : `rgba(0,0,0,${-sh * .30})`; c.fillRect(x, y, sw + .6, 236);
      c.globalAlpha = 1;
    }
  },
  render(c, t, A, TL) {
    const ip = TL.noIntro ? 1 : seg(t, 0, 1.6), S = lineState(t, TL), o = this.opts(A);
    const Xw = S.tc >= 0 ? -300 + 2500 * eIO(seg(S.tc, 0, 1.4)) : -9999;
    const bump = x => S.tc >= 0 && S.tc < 1.5 ? 16 * Math.exp(-Math.pow((x - Xw) / 150, 2)) * Math.sin((x - Xw) / 40) : 0;
    c.save(); c.shadowColor = 'rgba(0,0,0,.35)'; c.shadowBlur = 0; this.drawCloth(c, t, ip, bump); c.restore();
    // flag sheen ribbon riding the wave on flag line
    if (S.flag > 0) for (let k = 0; k < 3; k++) { c.globalAlpha = S.flag * .9; c.fillStyle = FLAG[k]; for (let x = 0; x < 1920; x += 6) c.fillRect(x, 872 + this.wave(x, t, bump) + 18 + k * 4, 6.6, 4); c.globalAlpha = 1; }
    if (S.k < 0) return;
    const dyAt = x => this.wave(x, t, bump) * .6;
    if (S.tc < 1.5) {
      const Ln = layout(c, S.newL, A, o);
      c.save(); c.beginPath(); c.rect(0, 0, Math.max(0, Xw - 60), 1080); c.clip();
      drawItems(c, Ln, o, (i, n, it) => { const p = clamp((Xw - 60 - it.x) / 220); return { a: eOut(p), dy: dyAt(it.x) + (1 - eOut(p)) * 16 }; }); c.restore();
      if (S.oldL !== null) { const Lo = layout(c, S.oldL, A, o); c.save(); c.beginPath(); c.rect(Xw - 60, 0, 1920, 1080); c.clip();
        drawItems(c, Lo, o, (i, n, it) => { const p = clamp((it.x - (Xw - 60)) / 220); return { a: eOut(p), dy: dyAt(it.x) - (1 - eOut(p)) * 16 }; }); c.restore(); }
      // sheen on crest
      const g = c.createLinearGradient(Xw - 120, 0, Xw + 120, 0); g.addColorStop(0, 'rgba(255,245,220,0)'); g.addColorStop(.5, 'rgba(255,245,220,.28)'); g.addColorStop(1, 'rgba(255,245,220,0)');
      c.globalCompositeOperation = 'lighter'; c.fillStyle = g; c.fillRect(Xw - 120, 880, 240, 200); c.globalCompositeOperation = 'source-over';
    } else drawItems(c, layout(c, S.newL, A, o), o, (i, n, it) => ({ a: 1, dy: dyAt(it.x) }));
  },
};

// =====================================================================
// 2. EQ — equalizer whose bars are built from carpet blocks, rising above the band
const EQ = {
  opts(A) { return { fs: 54, cy: 990, area: [140, 1780], col: '#fff', accent: GOLD, tagBg: GOLD, tagCol: '#062B31', logo: A.white, logoH: 74, shadow: 'rgba(0,0,0,.5)' }; },
  N: 60,
  level(i, t, S, ip) {
    const n = this.N, u = i / n, beat = Math.pow(Math.max(0, Math.sin(t * Math.PI * 2 * 2.08)), 8);
    let h = .25 + .32 * Math.abs(Math.sin(t * (2.1 + hash(i) * 2.6) + hash(i, 3) * 6)) + .22 * Math.abs(Math.sin(t * 5.3 + u * 9)) + .2 * beat * (1 - Math.abs(u - .5));
    if (S.tc >= 0 && S.tc < 1.4) { const X = -0.2 + 1.4 * eIO(seg(S.tc, 0, 1.2)); h += .9 * Math.exp(-Math.pow((u - X) * 9, 2)); }
    const intro = seg(ip, u * .5, u * .5 + .5);
    return clamp(h, 0, 1.15) * eOut(intro);
  },
  drawBars(c, t, S, ip, top, palette, maxH = 112, refl = true) {
    const n = this.N, bw = 1920 / n, seg_h = 10;
    for (let i = 0; i < n; i++) {
      const lv = this.level(i, t, S, ip), segs = Math.round(lv * maxH / seg_h), x = i * bw + 4, w = bw - 8;
      for (let s = 0; s < segs; s++) {
        const y = top - (s + 1) * seg_h, fr = s / (maxH / seg_h);
        let col = fr < .35 ? palette[0] : fr < .6 ? palette[1] : fr < .82 ? palette[2] : palette[3];
        if (S.flag > 0) col = mixc(col.startsWith('#') ? col : '#000000', fr < .33 ? FLAG[2] : fr < .66 ? FLAG[1] : FLAG[0], S.flag);
        c.fillStyle = col;
        // carpet block: stepped notch shape
        c.beginPath(); c.moveTo(x, y + 2); c.lineTo(x + w * .25, y + 2); c.lineTo(x + w * .25, y); c.lineTo(x + w * .75, y); c.lineTo(x + w * .75, y + 2); c.lineTo(x + w, y + 2);
        c.lineTo(x + w, y + seg_h - 2); c.lineTo(x, y + seg_h - 2); c.closePath(); c.fill();
        if (refl) { c.globalAlpha = .13 * (1 - s / 8); if (s < 8) c.fillRect(x, top + 4 + s * seg_h, w, seg_h - 4); c.globalAlpha = 1; }
      }
      // cap: small rhombus floating on top
      if (segs > 0) { rhombus(c, x + w / 2, top - segs * seg_h - 9, w * .32, 5); c.fillStyle = S.flag > .5 ? '#fff' : IVORY; c.fill(); }
    }
  },
  render(c, t, A, TL) {
    const ip = TL.noIntro ? 1 : seg(t, 0, 1.8), S = lineState(t, TL), o = this.opts(A);
    const bp = eOut(seg(ip, 0, .4)), top = 900 + (1 - bp) * 200;
    // band
    const g = c.createLinearGradient(0, top, 0, 1080); g.addColorStop(0, '#0A4C56'); g.addColorStop(1, '#03222A');
    c.fillStyle = g; c.fillRect(0, top, 1920, 1080 - top);
    // carpet border under the bars
    c.fillStyle = GOLD; c.fillRect(0, top, 1920, 3);
    for (let x = 0, i = 0; x < 1920; x += 24, i++) { rhombus(c, x + 12, top + 13, 8, 6); c.fillStyle = i % 2 ? RUBY : IVORY; c.globalAlpha = .9; c.fill(); }
    c.globalAlpha = 1; c.fillStyle = 'rgba(217,180,90,.6)'; c.fillRect(0, top + 24, 1920, 1);
    this.drawBars(c, t, S, seg(ip, .25, 1), top, [TEAL_L, IVORY, GOLD, RUBY]);
    if (S.k < 0) return;
    const Ln = layout(c, S.newL, A, o);
    if (S.tc < 1.4) {
      if (S.oldL !== null) drawItems(c, layout(c, S.oldL, A, o), o, (i, n, it) => { const p = seg(S.tc, i * .004, .2 + i * .004); return { a: 1 - p, dy: 26 * eIn(p) }; });
      drawItems(c, Ln, o, (i, n, it) => { const p = seg(S.tc, .38 + i * .018, .78 + i * .018); return { a: p * 1.5, dy: -30 * (1 - eBack(p)), s: .7 + .3 * eBack(p) }; });
    } else drawItems(c, Ln, o, () => ({ a: 1 }));
  },
};

// =====================================================================
// 3. GIRIH — gold interlace (Shirvanshahs stone pattern) draws itself; light passes; sheen text
const GIRIH = {
  opts(A) { return { fs: 54, cy: 984, area: [360, 1560], col: '#fff', accent: GOLD, tagBg: GOLD, tagCol: '#04191D', logo: A.white, logoH: 74, shadow: 'rgba(0,0,0,.5)' }; },
  render(c, t, A, TL) {
    const ip = TL.noIntro ? 1 : seg(t, 0, 2.0), S = lineState(t, TL), o = this.opts(A);
    const top = 880, bp = eOut(seg(ip, 0, .35));
    c.save(); c.globalAlpha = bp;
    const g = c.createLinearGradient(0, top, 0, 1080); g.addColorStop(0, '#062F36'); g.addColorStop(1, '#021417'); c.fillStyle = g; c.fillRect(0, top, 1920, 200);
    c.restore();
    const s = 50, panel = x => x < 330 || x > 1590;
    c.save(); c.beginPath(); c.rect(0, top, 1920, 200); c.clip();
    for (let i = -1; i < 1920 / s + 1; i++) for (let j = 0; j < 5; j++) {
      const cx = i * s + (j % 2 ? s / 2 : 0), cy = top + 4 + j * s * .5 + 20, inP = panel(cx);
      const dist = inP ? (cx < 330 ? (330 - cx) : (cx - 1590)) / 330 : Math.abs(cx - 960) / 960;
      const p = eIO(seg(ip, .1 + dist * .5, .55 + dist * .5)); if (p <= 0) continue;
      const r = s * .5, L = r * 6.2;
      c.setLineDash([L, L]); c.lineDashOffset = L * (1 - p);
      star8Path(c, cx, cy, r, .74); c.lineWidth = inP ? 2.2 : 1.4;
      c.strokeStyle = inP ? `rgba(217,180,90,${.95})` : 'rgba(217,180,90,.13)'; c.stroke();
      if (inP) { c.setLineDash([]); octagonDot(c, cx, cy, p, S.flag, i + j); }
    }
    c.setLineDash([]);
    // light sweep
    const sw = S.tc >= 0 && S.tc < 1.2 ? seg(S.tc, 0, 1.1) : ((t % 5) / 1.6);
    if (sw > 0 && sw < 1 && ip >= 1) {
      const lx = -300 + 2520 * sw, lg = c.createLinearGradient(lx - 200, 0, lx + 200, 0);
      lg.addColorStop(0, 'rgba(255,230,170,0)'); lg.addColorStop(.5, 'rgba(255,230,170,.22)'); lg.addColorStop(1, 'rgba(255,230,170,0)');
      c.globalCompositeOperation = 'lighter'; c.fillStyle = lg; c.fillRect(lx - 200, top, 400, 200); c.globalCompositeOperation = 'source-over';
    }
    c.restore();
    // rules & panel dividers
    const rp = eOut(seg(ip, .05, .6));
    c.fillStyle = GOLD; c.fillRect(960 - 960 * rp, top, 1920 * rp, 3); c.fillRect(960 - 960 * rp, top + 8, 1920 * rp, 1);
    for (const x of [330, 1590]) { c.fillRect(x - 4, top + 14, 2, 186 * rp); c.fillRect(x + 2, top + 14, 1, 186 * rp); }
    if (S.k < 0) return;
    const sheenX = S.tc >= 0 ? -200 + 2300 * seg(S.tc, .3, 1.5) : -999;
    const sheen = it => { const d = Math.abs(it.x - sheenX); return d < 140 ? mixc('#FFFFFF', '#E9C46A', 1 - d / 140) : null; };
    const Ln = layout(c, S.newL, A, o);
    if (S.tc < 1.6) {
      if (S.oldL !== null) drawItems(c, layout(c, S.oldL, A, o), o, (i) => { const p = seg(S.tc, 0, .35); return { a: 1 - p, s: 1 - .06 * p }; });
      drawItems(c, Ln, o, (i, n, it) => { const p = seg(S.tc, .3 + (it.x - 360) / 1200 * .6, .7 + (it.x - 360) / 1200 * .6); return { a: p, s: 1.18 - .18 * eOut(p), fill: sheen(it) }; });
    } else drawItems(c, Ln, o, () => ({ a: 1 }));
  },
};
function octagonDot(c, cx, cy, p, flag, i) {
  const col = flag > 0 ? mixc('#D9B45A', FLAG[((i % 3) + 3) % 3], flag) : GOLD;
  star8(c, cx, cy, 6 * p, col);
}

// =====================================================================
// 4. DIAL — vintage radio dial with carpet-ornament scale; needle tunes to 103.3
const DIAL = {
  opts(A) { return { fs: 50, cy: 1012, area: [300, 1620], col: '#FFF6E3', accent: '#F2B54A', tagBg: '#F2B54A', tagCol: '#2A1606', logo: A.white, logoH: 66, shadow: 'rgba(0,0,0,.6)' }; },
  fx: f => 330 + (f - 87.5) / (108 - 87.5) * 1260,
  render(c, t, A, TL) {
    const ip = TL.noIntro ? 1 : seg(t, 0, 2.2), S = lineState(t, TL), o = this.opts(A), top = 880;
    const bp = eOut(seg(ip, 0, .35));
    c.save(); c.translate(0, (1 - bp) * 200);
    // cabinet
    const g = c.createLinearGradient(0, top, 0, 1080); g.addColorStop(0, '#2A1A12'); g.addColorStop(.08, '#3B2418'); g.addColorStop(1, '#140B07'); c.fillStyle = g; c.fillRect(0, top, 1920, 200);
    c.fillStyle = GOLD; c.fillRect(0, top, 1920, 3);
    // fabric speaker grille texture (subtle lozenge weave)
    c.strokeStyle = 'rgba(217,180,90,.06)'; c.lineWidth = 1;
    for (let x = -200; x < 2100; x += 14) { c.beginPath(); c.moveTo(x, top + 960 - 880 + 70); c.lineTo(x + 120, 1080); c.stroke(); }
    // needle frequency
    let f = 103.3;
    const tune = seg(ip, .35, 1.6);
    if (tune < 1) f = 88 + (103.3 - 88) * eOut(tune) + Math.sin(tune * 18) * 1.2 * (1 - tune) * (tune > .5 ? 1 : 0);
    let detune = 0; if (S.tc >= 0 && S.tc < 1) { detune = Math.sin(S.tc * 14) * 2.2 * Math.pow(1 - S.tc, 2); f += detune; }
    const flagOn = S.flag;
    // dial glass
    const wx0 = 300, wx1 = 1620, wy0 = top + 16, wy1 = top + 72;
    rr(c, wx0, wy0, wx1 - wx0, wy1 - wy0, 8);
    const gl = c.createLinearGradient(wx0, 0, wx1, 0);
    if (flagOn > 0) { gl.addColorStop(0, mixc('#E9A93A', FLAG[0], flagOn * .6)); gl.addColorStop(.5, mixc('#F7C766', FLAG[1], flagOn * .6)); gl.addColorStop(1, mixc('#E9A93A', FLAG[2], flagOn * .6)); }
    else { gl.addColorStop(0, '#C98A2A'); gl.addColorStop(.5, '#F7C766'); gl.addColorStop(1, '#C98A2A'); }
    c.fillStyle = gl; c.globalAlpha = .25 + .75 * eOut(seg(ip, .1, .5)); c.fill(); c.globalAlpha = 1;
    c.strokeStyle = GOLD; c.lineWidth = 2; c.stroke();
    // glow around needle
    const nx = this.fx(f);
    const rg = c.createRadialGradient(nx, (wy0 + wy1) / 2, 0, nx, (wy0 + wy1) / 2, 160); rg.addColorStop(0, 'rgba(255,240,200,.55)'); rg.addColorStop(1, 'rgba(255,240,200,0)');
    c.save(); rr(c, wx0, wy0, wx1 - wx0, wy1 - wy0, 8); c.clip(); c.fillStyle = rg; c.fillRect(wx0, wy0, wx1 - wx0, wy1 - wy0);
    // carpet ornament band at top & bottom edge of glass
    for (let x = wx0 + 6, i = 0; x < wx1; x += 16, i++) {
      c.fillStyle = 'rgba(58,34,14,.75)'; c.beginPath(); c.moveTo(x, wy0); c.lineTo(x + 8, wy0 + 7); c.lineTo(x + 16, wy0); c.fill();
      c.beginPath(); c.moveTo(x, wy1); c.lineTo(x + 8, wy1 - 7); c.lineTo(x + 16, wy1); c.fill();
    }
    // scale
    const sp = seg(ip, .15, .7);
    for (let fr = 88; fr <= 108; fr += .5) {
      const x = this.fx(fr), major = fr % 2 === 0; if ((x - wx0) / (wx1 - wx0) > sp) continue;
      c.fillStyle = '#3A220E';
      if (major) { rhombus(c, x, wy0 + 22, 5, 8); c.fill(); c.font = '700 17px Montserrat'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(String(fr), x, wy0 + 42); }
      else c.fillRect(x - 1, wy0 + 16, 2, 10);
    }
    c.restore();
    // 103.3 marker star above glass
    const mx = this.fx(103.3); star8(c, mx, wy0 - 2, 7, '#EF3340');
    // needle
    c.save(); c.shadowColor = 'rgba(255,60,50,.9)'; c.shadowBlur = 14; c.fillStyle = '#E8302A'; c.fillRect(nx - 2, wy0 - 6, 4, wy1 - wy0 + 12); c.restore();
    // knobs
    for (const [kx, dir] of [[150, 1], [1770, -1]]) {
      const kr = 64, ang = (f - 88) * .35 * dir, kp = eBack(seg(ip, .2 + (dir < 0 ? .1 : 0), .7 + (dir < 0 ? .1 : 0))); if (kp <= 0) continue;
      c.save(); c.translate(kx, top + 100); c.scale(kp, kp); c.rotate(ang);
      c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 16; c.beginPath(); c.arc(0, 0, kr, 0, 7);
      const kg = c.createRadialGradient(-20, -20, 4, 0, 0, kr); kg.addColorStop(0, '#E6CF97'); kg.addColorStop(.6, '#A9813A'); kg.addColorStop(1, '#5E4318'); c.fillStyle = kg; c.fill(); c.shadowColor = 'transparent';
      for (let i = 0; i < 40; i++) { c.save(); c.rotate(i / 40 * Math.PI * 2); c.fillStyle = 'rgba(40,24,8,.45)'; c.fillRect(-1.2, -kr, 2.4, 9); c.restore(); }
      c.beginPath(); c.arc(0, 0, kr - 16, 0, 7); c.fillStyle = '#2A1A12'; c.fill();
      star8Path(c, 0, 0, kr - 24, .72); c.strokeStyle = GOLD; c.lineWidth = 2; c.stroke();
      star8(c, 0, 0, 10, flagOn > 0 ? FLAG[1] : GOLD);
      c.fillStyle = '#F6EBD2'; c.fillRect(-2, -kr + 18, 4, 12);
      c.restore();
    }
    // ON AIR lamp
    const on = ip >= 1 ? (.7 + .3 * Math.sin(t * 4)) : 0;
    c.font = '800 15px Montserrat'; c.textAlign = 'left'; c.textBaseline = 'middle';
    c.beginPath(); c.arc(318, top + 88 + 6, 6, 0, 7); c.fillStyle = `rgba(239,51,64,${on})`; c.shadowColor = '#EF3340'; c.shadowBlur = 12 * on; c.fill(); c.shadowColor = 'transparent';
    c.fillStyle = `rgba(246,235,210,${.4 + .5 * on})`; c.fillText('EFİRDƏ', 332, top + 95);
    c.restore();
    if (S.k < 0) return;
    // static noise over text area while detuned
    const nz = Math.abs(detune) / 2.2 + (S.tc >= 0 && S.tc < .5 ? .6 * (1 - S.tc / .5) : 0);
    if (nz > .02) { for (let q = 0; q < 900 * nz; q++) { const h1 = hash(q, Math.floor(t * 50)), h2 = hash(q + 99, Math.floor(t * 50)); c.fillStyle = `rgba(255,240,210,${.5 * h2})`; c.fillRect(300 + h1 * 1320, 970 + h2 * 80, 3, 2); } }
    const Ln = layout(c, S.newL, A, o);
    if (S.tc < 1.2) {
      if (S.oldL !== null) drawItems(c, layout(c, S.oldL, A, o), o, (i) => { const on = hash(i, Math.floor(t * 30)) > seg(S.tc, 0, .35) * 1.2; return { a: on ? 1 - seg(S.tc, 0, .35) * .5 : 0, dx: (hash(i, Math.floor(t * 40)) - .5) * 10 * seg(S.tc, 0, .35) }; });
      drawItems(c, Ln, o, (i) => { const p = seg(S.tc, .3, 1.0); const on = hash(i + 50, Math.floor(t * 30)) < p * 1.3; return { a: on ? .4 + .6 * p : 0, dx: (hash(i, Math.floor(t * 40)) - .5) * 8 * (1 - p) }; });
    } else drawItems(c, Ln, o, () => ({ a: 1 }));
  },
};

// =====================================================================
// 5. SILKEQ — kəlağayı silk band + carpet equalizer above it
const SILKEQ = {
  render(c, t, A, TL) {
    const ip = TL.noIntro ? 1 : seg(t, 0, 1.8), S = lineState(t, TL);
    const top = 896;
    EQ.drawBars(c, t, S, seg(ip, .3, 1), top + 4, [IVORY, GOLD, '#E2A93B', RUBY], 96, false);
    SILK.render(c, t, A, TL);
  },
};

const CONCEPTS = { SILK, EQ, GIRIH, DIAL, SILKEQ };
window.render3 = (c, name, t, A, TL) => CONCEPTS[name].render(c, t, A, TL);
