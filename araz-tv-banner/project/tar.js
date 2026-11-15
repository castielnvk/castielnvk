// Araz FM TV banner — "TAR" concept, thick full-width version. Canvas 1920x1080, transparent.
// window.renderTar(ctx, t, A, TL)   TL = { changes:[...], lines:[...], loopLen? }
const TEAL = '#095D6A', TEAL_L = '#7FD1D6', GOLD = '#D9B45A', IVORY = '#F6EBD2';
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
const eBack = p => { const c = 1.9; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
const hash = (i, j = 0) => { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); };
const rr = (c, x, y, w, h, r) => { c.beginPath(); c.roundRect(x, y, w, h, r); };
const seg = (t, a, b) => clamp((t - a) / (b - a));

// ---- geometry
const BY = 888, CY = 984;
const BODY = [[165, 92], [302, 68]];
const NECK0 = 362, NECK1 = 1770, NH = 124;
const STR = [-44, -38, -4, 4, 38, 44], SX0 = 66, SX1 = 1786;
const AREA = [404, 1740], FS = 54;

function star8(c, cx, cy, r, fill) {
  c.save(); c.translate(cx, cy); c.fillStyle = fill;
  for (let k = 0; k < 2; k++) { c.save(); c.rotate(k * Math.PI / 4); c.fillRect(-r * .72, -r * .72, r * 1.44, r * 1.44); c.restore(); }
  c.restore();
}
function note(c, x, y, s, col, rot, dbl) {
  c.save(); c.translate(x, y); c.rotate(rot); c.scale(s, s); c.fillStyle = col; c.strokeStyle = col;
  c.save(); c.rotate(-.35); c.beginPath(); c.ellipse(0, 0, 7, 5, 0, 0, 7); c.fill(); c.restore();
  c.lineWidth = 2.2; c.beginPath(); c.moveTo(6, -2); c.lineTo(6, -26); c.stroke();
  if (dbl) { c.beginPath(); c.ellipse(20, -4, 7, 5, -.35, 0, 7); c.fill(); c.beginPath(); c.moveTo(26, -6); c.lineTo(26, -30); c.stroke(); c.lineWidth = 5; c.beginPath(); c.moveTo(6, -24); c.lineTo(26, -28); c.stroke(); }
  else { c.beginPath(); c.moveTo(6, -26); c.quadraticCurveTo(16, -20, 13, -10); c.lineWidth = 2.4; c.stroke(); }
  c.restore();
}
function mizrab(c, x, y, rot, a) { // tar plectrum: small teardrop of brass with a wax bead
  c.save(); c.globalAlpha = a; c.translate(x, y); c.rotate(rot);
  c.beginPath(); c.moveTo(0, -30); c.bezierCurveTo(12, -12, 10, 14, 0, 22); c.bezierCurveTo(-10, 14, -12, -12, 0, -30); c.closePath();
  const g = c.createLinearGradient(-10, 0, 10, 0); g.addColorStop(0, '#B8892E'); g.addColorStop(.5, '#F2D58A'); g.addColorStop(1, '#9C7224');
  c.fillStyle = g; c.shadowColor = 'rgba(0,0,0,.4)'; c.shadowBlur = 8; c.fill(); c.shadowColor = 'transparent';
  c.beginPath(); c.arc(0, -18, 6, 0, 7); c.fillStyle = '#5A2E1A'; c.fill();
  c.restore();
}
function socialIcon(c, k, cx, cy, s, col) {
  c.save(); c.strokeStyle = col; c.fillStyle = col; c.lineWidth = s * .09;
  if (k === 0) { c.font = `800 ${s * 1.05}px Montserrat`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('f', cx, cy + s * .04); }
  if (k === 1) { rr(c, cx - s / 2, cy - s / 2, s, s, s * .28); c.stroke(); c.beginPath(); c.arc(cx, cy, s * .22, 0, 7); c.stroke(); c.beginPath(); c.arc(cx + s * .26, cy - s * .26, s * .06, 0, 7); c.fill(); }
  if (k === 2) { rr(c, cx - s * .68, cy - s * .46, s * 1.36, s * .92, s * .26); c.stroke(); c.beginPath(); c.moveTo(cx - s * .16, cy - s * .22); c.lineTo(cx + s * .24, cy); c.lineTo(cx - s * .16, cy + s * .22); c.closePath(); c.fill(); }
  c.restore();
}

// ---- layout of one line into animatable items (chars + units)
function layout(c, li, A) {
  const L = LINES[li], items = [], cy = CY + 2;
  c.font = `700 ${FS}px Montserrat`;
  const chars = (txt, x, font) => { c.font = font; let w = 0; for (const ch of txt) { const cw = c.measureText(ch).width; items.push({ ch, x: x + w + cw / 2, font }); w += cw; } c.font = font; return c.measureText(txt).width; };
  const fMain = `700 ${FS}px Montserrat`;
  if (L.logo) {
    const img = A.white, lh = 74, lw = img.width * lh / img.height, fT = `800 ${FS * .9}px Montserrat`;
    c.font = fT; const tw = c.measureText(L.text).width, gap = 36, W = lw + gap * 2 + tw, sx = 1072 - W / 2;
    items.push({ unit: (c) => c.drawImage(img, -lw / 2, -lh / 2, lw, lh), x: sx + lw / 2, w: lw });
    items.push({ unit: (c) => { c.fillStyle = GOLD; c.fillRect(-1.5, -lh * .42, 3, lh * .84); }, x: sx + lw + gap });
    chars(L.text, sx + lw + gap * 2, fT);
    return { items, cy };
  }
  c.font = fMain; const tw = c.measureText(L.text).width;
  let extra = 0, tagW = 0; const fTag = `800 ${FS * .7}px Montserrat`, fUrl = `700 ${FS * .7}px Montserrat`;
  if (L.tag) { c.font = fTag; tagW = c.measureText(L.tag).width + 48; extra = 92 + tagW; }
  if (L.social) { c.font = fUrl; extra = 64 + 3 * 54 + 22 + c.measureText('arazfm.az').width; }
  const sx = (AREA[0] + AREA[1]) / 2 - (tw + extra) / 2;
  if (L.flag) { items.push({ unit: c => star8(c, 0, 0, 16, FLAG[0]), x: sx - 46 }); }
  chars(L.text, sx, fMain);
  let x = sx + tw;
  if (L.flag) items.push({ unit: c => star8(c, 0, 0, 16, FLAG[2]), x: x + 46 });
  if (L.tag) {
    x += 30; items.push({ unit: c => star8(c, 0, 0, 13, GOLD), x: x + 16 }); x += 62;
    const tx = x + tagW / 2;
    items.push({ unit: c => { rr(c, -tagW / 2, -FS * .64, tagW, FS * 1.28, FS * .64); c.fillStyle = IVORY; c.fill(); c.font = fTag; c.fillStyle = '#06424B'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(L.tag, 0, 2); }, x: tx });
  }
  if (L.social) {
    x += 64; for (let k = 0; k < 3; k++) items.push({ unit: c => socialIcon(c, k, 0, 0, 34, '#fff'), x: x + 20 + k * 54 });
    x += 3 * 54 + 22; chars('arazfm.az', x, fUrl);
  }
  return { items, cy };
}

// draw items with per-item animation fn(i,n) -> {dy, a, rot, s}
function drawItems(c, L, anim) {
  const n = L.items.length;
  L.items.forEach((it, i) => {
    const m = anim(i, n); if (m.a <= 0.002) return;
    c.save(); c.globalAlpha = clamp(m.a); c.translate(it.x, L.cy + m.dy); c.rotate(m.rot || 0); c.scale(m.s || 1, m.s || 1);
    c.shadowColor = 'rgba(0,0,0,.55)'; c.shadowBlur = 10; c.shadowOffsetY = 3;
    if (it.unit) it.unit(c);
    else { c.font = it.font; c.fillStyle = '#fff'; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText(it.ch, 0, 2); }
    c.restore();
  });
}

// ---------------------------------------------------------------- scene
window.renderTar = function (c, t, A, TL) {
  const CH = TL.changes;
  let k = -1; for (let i = 0; i < CH.length; i++) if (t >= CH[i]) k = i;
  const tc = k >= 0 ? t - CH[k] : -1;               // time since last change
  const newL = k >= 0 ? TL.lines[k] : null, oldL = k > 0 ? TL.lines[k - 1] : (TL.prevLine ?? null);
  const flag = newL === 2 ? eOut(seg(tc, .15, .8)) : (oldL === 2 && tc >= 0 ? 1 - eOut(seg(tc, .15, .8)) : 0);
  const pluck = tc >= 0 ? 12 * Math.pow(1 - seg(tc, .12, 2.0), 2) * (tc > .12 ? 1 : 0) : 0;
  const it = TL.noIntro ? 99 : t; // intro clock

  // ---- 0. light streak (intro)
  const ls = seg(it, 0, .55);
  if (ls > 0 && ls < 1) {
    const x = -200 + 2300 * eIO(ls);
    const g = c.createLinearGradient(x - 500, 0, x, 0); g.addColorStop(0, 'rgba(217,180,90,0)'); g.addColorStop(1, 'rgba(255,236,180,.95)');
    c.fillStyle = g; c.fillRect(x - 500, CY - 2, 500, 4);
    c.beginPath(); c.arc(x, CY, 7, 0, 7); c.fillStyle = '#FFF4D0'; c.shadowColor = GOLD; c.shadowBlur = 24; c.fill(); c.shadowColor = 'transparent';
  }

  // ---- 1. backdrop band (full width, thick)
  const bp = eOut(seg(it, .2, .9));
  if (bp > 0) {
    const top = BY + (1 - bp) * 60;
    c.save(); c.globalAlpha = bp;
    const g = c.createLinearGradient(0, top, 0, 1080); g.addColorStop(0, '#0A4F59'); g.addColorStop(1, '#042A31');
    c.fillStyle = g; c.fillRect(0, top, 1920, 1080 - top);
    // tirmə/buta-free subtle carpet lozenges
    c.strokeStyle = 'rgba(217,180,90,.07)'; c.lineWidth = 2;
    for (let x = 20; x < 1960; x += 60) { c.beginPath(); c.moveTo(x, top + 14); c.lineTo(x + 30, top + 96); c.lineTo(x, top + 178); c.lineTo(x - 30, top + 96); c.closePath(); c.stroke(); }
    // gold top rule with travelling glint
    c.fillStyle = GOLD; c.fillRect(0, top, 1920, 3); c.fillStyle = 'rgba(217,180,90,.5)'; c.fillRect(0, top + 7, 1920, 1);
    const gx = ((t * 260) % 2600) - 340; const gg = c.createLinearGradient(gx - 160, 0, gx + 160, 0);
    gg.addColorStop(0, 'rgba(255,240,200,0)'); gg.addColorStop(.5, 'rgba(255,240,200,.95)'); gg.addColorStop(1, 'rgba(255,240,200,0)');
    c.fillStyle = gg; c.fillRect(gx - 160, top - 1, 320, 5);
    c.restore();
  }

  // ---- 2. sound rings from the tar body (radio waves)
  const rings = [];
  if (tc >= 0) for (let r = 0; r < 3; r++) rings.push(seg(tc, .12 + r * .18, 1.5 + r * .18));
  rings.push(seg((t % 2.4), 0, 2.4) * (it > 2 ? 1 : 0) * .999);
  rings.forEach((rp, ri) => {
    if (rp <= 0 || rp >= 1) return;
    const R = 80 + rp * 210, faint = ri === rings.length - 1;
    c.beginPath(); c.arc(BODY[0][0], CY, R, Math.PI * .55, Math.PI * 1.45, false);
    c.strokeStyle = flag > .5 && !faint ? FLAG[ri % 3] : TEAL_L;
    c.globalAlpha = (1 - rp) * (faint ? .25 : .7); c.lineWidth = faint ? 2 : 3; c.stroke(); c.globalAlpha = 1;
  });

  // ---- 3. neck (extends from body), frets drop in
  const np = eOut(seg(it, .6, 1.35));
  if (np > 0) {
    const w = (NECK1 - NECK0) * np, y0 = CY - NH / 2;
    c.save(); c.shadowColor = 'rgba(0,0,0,.45)'; c.shadowBlur = 18; c.shadowOffsetY = 5;
    rr(c, NECK0, y0, w, NH, [0, 10, 10, 0]);
    const g = c.createLinearGradient(0, y0, 0, y0 + NH); g.addColorStop(0, '#0F6B78'); g.addColorStop(.5, '#0A5560'); g.addColorStop(1, '#073E47');
    c.fillStyle = g; c.fill(); c.shadowColor = 'transparent';
    c.beginPath(); c.rect(NECK0, y0 - 4, w, NH + 8); c.clip();
    for (let f = 0; f < 22; f++) {
      const fx = NECK1 - 30 - (NECK1 - NECK0 - 40) * (1 - Math.pow(2, -f / 8.5));
      const fp = eBack(seg(it, .75 + (NECK1 - fx) / (NECK1 - NECK0) * .6, 1.0 + (NECK1 - fx) / (NECK1 - NECK0) * .6));
      if (fp <= 0) continue;
      c.fillStyle = 'rgba(217,180,90,.30)'; c.fillRect(fx, y0 + 6 + (1 - fp) * -30, 2.5, NH - 12);
      if ([2, 4, 6, 9, 11, 14].includes(f)) {
        const tw = .55 + .45 * Math.sin(t * 2.2 + f);
        c.beginPath(); c.arc(fx - 16, y0 + NH - 13, 4, 0, 7); c.fillStyle = `rgba(232,244,242,${.55 * tw * fp})`; c.fill();
      }
    }
    c.fillStyle = GOLD; c.fillRect(NECK0, y0, w, 2.5); c.fillRect(NECK0, y0 + NH - 2.5, w, 2.5);
    c.restore();
  }

  // ---- 4. peg head with turning pegs
  const pp = seg(it, 1.1, 1.65);
  if (pp > 0) {
    const px = NECK1 - 6, a = eOut(pp);
    c.save(); c.globalAlpha = a;
    for (let k2 = 0; k2 < 3; k2++) for (const s of [-1, 1]) {
      const kx = px + 22 + k2 * 30, ky = CY + s * (NH / 2 + 24);
      c.save(); c.translate(kx, ky); c.rotate((1 - eBack(seg(it, 1.15 + k2 * .07, 1.6 + k2 * .07))) * 3);
      rr(c, -6, -14, 12, 28, 5); c.fillStyle = '#4A2A1A'; c.fill();
      c.beginPath(); c.arc(0, s * 14, 9, 0, 7); c.fillStyle = IVORY; c.fill(); c.strokeStyle = GOLD; c.lineWidth = 2; c.stroke();
      c.restore();
    }
    rr(c, px, CY - NH / 2 - 8, 104, NH + 16, 12);
    const g2 = c.createLinearGradient(px, 0, px + 104, 0); g2.addColorStop(0, '#6A3B26'); g2.addColorStop(1, '#3A1F14'); c.fillStyle = g2; c.fill();
    c.strokeStyle = GOLD; c.lineWidth = 2; c.stroke();
    star8(c, px + 52, CY, 18 * eBack(pp), GOLD); star8(c, px + 52, CY, 8 * eBack(pp), '#3A1F14');
    c.restore();
  }

  // ---- 5. tar body: double bowl, nacre trim popping in, membranes, bridge
  const bo = seg(it, .3, 1.1);
  if (bo > 0) {
    const s = eBack(bo), rot = (1 - eOut(bo)) * -.5;
    c.save(); c.translate(230, CY); c.rotate(rot); c.scale(s, s); c.translate(-230, -CY);
    c.shadowColor = 'rgba(0,0,0,.45)'; c.shadowBlur = 22; c.shadowOffsetY = 6;
    for (const [lx, r] of BODY) { c.beginPath(); c.arc(lx, CY, r + 5, 0, 7); c.fillStyle = GOLD; c.fill(); }
    c.shadowColor = 'transparent';
    for (const [lx, r] of BODY) { c.beginPath(); c.arc(lx, CY, r, 0, 7); const g = c.createRadialGradient(lx - r * .35, CY - r * .35, 4, lx, CY, r); g.addColorStop(0, '#8A4E31'); g.addColorStop(1, '#3E2015'); c.fillStyle = g; c.fill(); }
    BODY.forEach(([lx, r], bi) => {
      const nd = 22;
      for (let i = 0; i < nd; i++) {
        const dp = eBack(seg(it, .7 + i * .025 + bi * .1, .95 + i * .025 + bi * .1)); if (dp <= 0) continue;
        const a = i / nd * Math.PI * 2 - Math.PI / 2, tw = .7 + .3 * Math.sin(t * 3 + i * 1.7 + bi);
        c.beginPath(); c.arc(lx + Math.cos(a) * (r - 7), CY + Math.sin(a) * (r - 7), 2.6 * dp, 0, 7); c.fillStyle = `rgba(232,246,244,${tw})`; c.fill();
      }
    });
    // membranes pulse with the sound
    const pulse = 1 + .025 * pluck / 12 * Math.sin(t * 40);
    for (const [lx, r] of BODY) {
      c.beginPath(); c.arc(lx, CY, (r - 16) * pulse, 0, 7);
      const g = c.createRadialGradient(lx - 10, CY - 10, 2, lx, CY, r - 16); g.addColorStop(0, '#FFF8EA'); g.addColorStop(1, '#E2D0AC'); c.fillStyle = g; c.fill();
    }
    // flag star on big membrane (subtle)
    star8(c, BODY[0][0] - 36, CY, 9, flag > 0 ? `rgba(239,51,64,${.35 + .65 * flag})` : 'rgba(9,93,106,.35)');
    rr(c, 175, CY - 50, 9, 100, 4); c.fillStyle = '#3A1F14'; c.fill();
    rr(c, SX0 - 8, CY - 14, 16, 28, 5); c.fillStyle = GOLD; c.fill();
    c.restore();
  }

  // ---- 6. strings: stretch in, pluck with travelling wave, glint, flag colours
  const sp = eOut(seg(it, 1.2, 1.8));
  if (sp > 0) {
    const sx1 = SX0 + (SX1 - SX0) * sp;
    STR.forEach((dy, i) => {
      c.beginPath();
      for (let x = SX0; x <= sx1; x += 5) {
        const u = (x - SX0) / (SX1 - SX0);
        const travel = tc >= 0 ? Math.exp(-Math.pow((u - seg(tc, .12, .9)) * 7, 2)) : 0;
        const vib = pluck * (Math.sin(Math.PI * u) * Math.sin(t * 75 + i * 1.9) * .6 + travel * Math.sin(t * 50 + i) * .8);
        x === SX0 ? c.moveTo(x, CY + dy + vib) : c.lineTo(x, CY + dy + vib);
      }
      const base = i < 2 || i > 3 ? 'rgba(236,228,210,.6)' : 'rgba(217,180,90,.75)';
      c.strokeStyle = flag > .02 ? FLAG[Math.floor(i / 2)] : base; c.globalAlpha = flag > .02 ? .35 + .65 * flag : 1;
      c.lineWidth = i % 2 ? 1.5 : 2; c.stroke(); c.globalAlpha = 1;
    });
    // ambient glint running along one string
    const gp = (t % 3.2) / 1.4;
    if (it > 2.2 && gp < 1) {
      const si = Math.floor(hash(Math.floor(t / 3.2)) * 6), gx = SX0 + (SX1 - SX0) * eIO(gp);
      const g = c.createRadialGradient(gx, CY + STR[si], 0, gx, CY + STR[si], 26);
      g.addColorStop(0, 'rgba(255,245,215,.95)'); g.addColorStop(1, 'rgba(255,245,215,0)'); c.fillStyle = g; c.fillRect(gx - 26, CY + STR[si] - 26, 52, 52);
    }
  }

  // ---- 7. mizrab strike at each change
  if (tc >= 0 && tc < .55) {
    const m = seg(tc, 0, .3), a = tc < .3 ? clamp(tc / .08) : 1 - seg(tc, .3, .55);
    for (let g = 3; g >= 0; g--) { const mm = clamp(m - g * .06); mizrab(c, 420, CY - 70 + 140 * eIO(mm), .5 - mm * 1.0, a * (g ? .18 : 1)); }
  }

  // ---- 8. text: old letters jump off the strings, new letters drop onto them
  if (k >= 0) {
    if (oldL !== null && tc < .8) {
      const L = layout(c, oldL, A);
      drawItems(c, L, (i, n) => { const p = seg(tc, .1 + i * .012, .45 + i * .012), h = hash(i, k);
        return { dy: -70 * eIn(p) - Math.sin(p * Math.PI) * 10, a: 1 - p, rot: (h - .5) * 1.2 * p, s: 1 - .3 * p }; });
    }
    const L = layout(c, newL, A);
    drawItems(c, L, (i, n) => { const p = seg(tc, .45 + i * .022, .95 + i * .022), h = hash(i + 7, k);
      return { dy: -56 * (1 - eBack(p)), a: clamp(p * 2.5), rot: (h - .5) * .5 * (1 - p), s: .6 + .4 * eBack(p) }; });
  }

  // ---- 9. music notes rising from the strings at each change + ambient drift
  const drawNotes = (t0, cnt, seed, strong) => {
    for (let n = 0; n < cnt; n++) {
      const h1 = hash(n, seed), h2 = hash(n + 31, seed), life = 1.8 + h2 * .8;
      const p = seg(t - t0 - h1 * .5, 0, life); if (p <= 0 || p >= 1) continue;
      const x = 440 + h2 * 1300 + Math.sin(p * 6 + n) * 14, y = CY + STR[n % 6] - p * (150 + h1 * 60);
      const col = flag > .5 && strong ? FLAG[n % 3] : (n % 2 ? GOLD : IVORY);
      c.globalAlpha = Math.sin(p * Math.PI) * (strong ? .95 : .35); note(c, x, y, (strong ? 1 : .8) * (.8 + h1 * .5), col, (h2 - .5) * .6, n % 3 === 0); c.globalAlpha = 1;
    }
  };
  if (k >= 0) drawNotes(CH[k] + .15, 9, k + 1, true);
  if (it > 2.4) { const slot = Math.floor(t / 2.6); drawNotes(slot * 2.6, 2, 100 + slot, false); }
};
