// Araz FM TV banner v2 — animated national concepts. Canvas 1920x1080, transparent.
// window.renderFrame(ctx, variant, t, assets, timeline)
const TEAL = '#095D6A', TEAL_D = '#06424B', TEAL_L = '#7FD1D6';
const FLAG = ['#00B5E2', '#EF3340', '#509E2F'];
const GOLD = '#D9B45A', IVORY = '#F6EBD2', RUBY = '#B3202E', INDIGO = '#1E2C58';

const LINES = [
  { text: 'Azərbaycanın səsi bu dalğada!', tag: '103.3 FM' },
  { text: 'Bizə rəqəmsalda da qoşul!', social: true },
  { text: 'Milli musiqinin dəyişməz ünvanı!', flag: true },
  { logo: true, text: 'QOVUŞDURAN RADİO!' },
];

const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eOut = p => 1 - Math.pow(1 - p, 3);
const eIO = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const eBack = p => { const c = 1.7; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
const hash = (i, j) => { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); };
const rr = (ctx, x, y, w, h, r) => { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); };
const mix = (a, b, p) => { const pa = parseInt(a.slice(1), 16), pb = parseInt(b.slice(1), 16);
  const c = k => Math.round(((pa >> k) & 255) * (1 - p) + ((pb >> k) & 255) * p);
  return `rgb(${c(16)},${c(8)},${c(0)})`; };

function star8(ctx, cx, cy, r, fill) {
  ctx.save(); ctx.translate(cx, cy); ctx.fillStyle = fill;
  for (let k = 0; k < 2; k++) { ctx.save(); ctx.rotate(k * Math.PI / 4); ctx.fillRect(-r * .72, -r * .72, r * 1.44, r * 1.44); ctx.restore(); }
  ctx.restore();
}
function star8Path(ctx, cx, cy, r) {
  ctx.beginPath();
  for (let i = 0; i < 16; i++) {
    const a = i * Math.PI / 8 - Math.PI / 2, rad = i % 2 ? r * .76 : r;
    const px = cx + Math.cos(a) * rad, py = cy + Math.sin(a) * rad; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py);
  }
  ctx.closePath();
}
function octagon(ctx, cx, cy, r) {
  ctx.beginPath();
  for (let i = 0; i < 8; i++) { const a = i * Math.PI / 4 + Math.PI / 8; const px = cx + Math.cos(a) * r, py = cy + Math.sin(a) * r; i ? ctx.lineTo(px, py) : ctx.moveTo(px, py); }
  ctx.closePath();
}
function rhombus(ctx, cx, cy, rx, ry) { ctx.beginPath(); ctx.moveTo(cx, cy - ry); ctx.lineTo(cx + rx, cy); ctx.lineTo(cx, cy + ry); ctx.lineTo(cx - rx, cy); ctx.closePath(); }
function butaPath(ctx) {
  ctx.beginPath(); ctx.moveTo(0, 30);
  ctx.bezierCurveTo(24, 30, 32, 6, 24, -12);
  ctx.bezierCurveTo(17, -28, 2, -40, -14, -42);
  ctx.bezierCurveTo(-22, -43, -24, -34, -16, -30);
  ctx.bezierCurveTo(-8, -26, -6, -18, -14, -10);
  ctx.bezierCurveTo(-28, 4, -24, 30, 0, 30); ctx.closePath();
}

function socialIcons(ctx, x, cy, s, col) {
  ctx.save(); ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = s * .09;
  ctx.font = `800 ${s}px Montserrat`; ctx.textBaseline = 'middle'; ctx.textAlign = 'center';
  ctx.fillText('f', x + s * .3, cy + s * .04);
  const ix = x + s * 1.75; rr(ctx, ix - s / 2, cy - s / 2, s, s, s * .28); ctx.stroke();
  ctx.beginPath(); ctx.arc(ix, cy, s * .22, 0, 7); ctx.stroke();
  ctx.beginPath(); ctx.arc(ix + s * .26, cy - s * .26, s * .06, 0, 7); ctx.fill();
  const yx = x + s * 3.55; rr(ctx, yx - s * .68, cy - s * .46, s * 1.36, s * .92, s * .26); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(yx - s * .16, cy - s * .22); ctx.lineTo(yx + s * .24, cy); ctx.lineTo(yx - s * .16, cy + s * .22); ctx.closePath(); ctx.fill();
  ctx.restore(); return s * 4.3;
}

function content(ctx, L, x0, x1, cy, o) {
  const fs = o.fs || 44;
  ctx.save(); ctx.textBaseline = 'middle';
  if (o.shadow) { ctx.shadowColor = o.shadow; ctx.shadowBlur = 8; ctx.shadowOffsetY = 2; }
  if (L.logo) {
    const img = o.logoImg, lh = o.logoH, lw = img.width * lh / img.height;
    ctx.font = `800 ${fs * .9}px Montserrat`;
    const tw = ctx.measureText(L.text).width, gap = 32, W = lw + gap * 2 + tw, sx = (x0 + x1) / 2 - W / 2;
    ctx.drawImage(img, sx, cy - lh / 2, lw, lh);
    ctx.fillStyle = o.accent; ctx.fillRect(sx + lw + gap - 1.5, cy - lh * .42, 3, lh * .84);
    ctx.fillStyle = o.col; ctx.textAlign = 'left'; ctx.fillText(L.text, sx + lw + gap * 2, cy + 2);
    ctx.restore(); return;
  }
  ctx.font = `700 ${fs}px Montserrat`;
  const tw = ctx.measureText(L.text).width;
  let extra = 0, tagW = 0;
  if (L.tag) { ctx.font = `800 ${fs * .72}px Montserrat`; tagW = ctx.measureText(L.tag).width + 44; extra = 88 + tagW; }
  if (L.social) { ctx.font = `700 ${fs * .72}px Montserrat`; extra = 60 + fs * .62 * 4.3 + 24 + ctx.measureText('arazfm.az').width; }
  const sx = (x0 + x1) / 2 - (tw + extra) / 2;
  if (L.flag) { star8(ctx, sx - 40, cy, 13, FLAG[0]); star8(ctx, sx + tw + 40, cy, 13, FLAG[2]); }
  ctx.font = `700 ${fs}px Montserrat`; ctx.fillStyle = o.col; ctx.textAlign = 'left'; ctx.fillText(L.text, sx, cy + 2);
  let x = sx + tw;
  if (L.tag) {
    x += 30; star8(ctx, x + 14, cy, 12, o.accent); x += 58;
    ctx.shadowColor = 'transparent';
    rr(ctx, x, cy - fs * .62, tagW, fs * 1.24, fs * .62); ctx.fillStyle = o.tagBg; ctx.fill();
    ctx.font = `800 ${fs * .72}px Montserrat`; ctx.fillStyle = o.tagCol; ctx.textAlign = 'center'; ctx.fillText(L.tag, x + tagW / 2, cy + 2);
  }
  if (L.social) {
    x += 60; x += socialIcons(ctx, x, cy, fs * .62, o.col) + 24;
    ctx.font = `700 ${fs * .72}px Montserrat`; ctx.fillStyle = o.col; ctx.textAlign = 'left'; ctx.fillText('arazfm.az', x, cy + 2);
  }
  ctx.restore();
}

// ============================================================ VARIANTS
const X0 = 96, X1 = 1824;

// ---------- 1. XALÇA: carpet woven stitch by stitch, göl medallions, loom-shuttle wipe
const XALCA = {
  y: 900, h: 128,
  area: [X0 + 200, X1 - 200],
  opts: A => ({ col: IVORY, accent: GOLD, tagBg: IVORY, tagCol: TEAL_D, logoImg: A.white, logoH: 64, fs: 44, shadow: 'rgba(0,0,0,.35)' }),
  medallion(ctx, cx, cy, s, rot, flagMix) {
    ctx.save(); ctx.translate(cx, cy); ctx.scale(s, s); ctx.rotate(rot);
    // hooks around
    for (let i = 0; i < 8; i++) { ctx.save(); ctx.rotate(i * Math.PI / 4); rhombus(ctx, 0, -84, 7, 10); ctx.fillStyle = GOLD; ctx.fill(); ctx.restore(); }
    octagon(ctx, 0, 0, 76); ctx.fillStyle = INDIGO; ctx.fill(); ctx.lineWidth = 4; ctx.strokeStyle = GOLD; ctx.stroke();
    octagon(ctx, 0, 0, 62); ctx.fillStyle = flagMix ? mix('#B3202E', '#EF3340', flagMix) : RUBY; ctx.fill();
    for (let i = 0; i < 8; i++) { ctx.save(); ctx.rotate(i * Math.PI / 4 + Math.PI / 8); rhombus(ctx, 0, -52, 5, 7); ctx.fillStyle = IVORY; ctx.fill(); ctx.restore(); }
    star8Path(ctx, 0, 0, 44); ctx.fillStyle = IVORY; ctx.fill();
    star8Path(ctx, 0, 0, 30); ctx.fillStyle = flagMix ? mix(TEAL, FLAG[0], flagMix) : TEAL; ctx.fill();
    rhombus(ctx, 0, 0, 10, 14); ctx.fillStyle = GOLD; ctx.fill();
    ctx.restore();
  },
  bar(ctx, t, ip, st) {
    const { y, h } = this, w = X1 - X0;
    // weave reveal mask: columns of stitches from centre outward, rows filling bottom→top
    ctx.save();
    if (ip < 1) {
      ctx.beginPath();
      const cw = 16, rh = 8, rows = Math.ceil(h / rh);
      for (let cx = X0; cx < X1; cx += cw) {
        const d = Math.abs((cx + cw / 2) - 960) / (w / 2);
        const cp = clamp((ip * 1.6 - d * .75) / .45);
        const n = Math.floor(cp * rows + 1e-6);
        if (n > 0) ctx.rect(cx, y + h - n * rh, cw + .5, n * rh);
      }
      ctx.clip();
    }
    ctx.shadowColor = 'rgba(0,0,0,.35)'; ctx.shadowBlur = 22; ctx.shadowOffsetY = 6;
    rr(ctx, X0, y, w, h, 6); ctx.fillStyle = RUBY; ctx.fill(); ctx.shadowColor = 'transparent';
    // ivory border bands
    ctx.fillStyle = IVORY; ctx.fillRect(X0 + 4, y + 4, w - 8, 18); ctx.fillRect(X0 + 4, y + h - 22, w - 8, 18);
    for (const by of [y + 13, y + h - 13]) {
      for (let i = 0, bx = X0 + 18; bx < X1 - 10; bx += 26, i++) {
        rhombus(ctx, bx, by, 9, 6); ctx.fillStyle = i % 2 ? RUBY : INDIGO; ctx.fill();
        ctx.fillStyle = GOLD; ctx.fillRect(bx + 12, by - 1.5, 3, 3);
      }
    }
    // field
    const g = ctx.createLinearGradient(0, y + 26, 0, y + h - 26);
    g.addColorStop(0, '#0B6874'); g.addColorStop(1, '#074650');
    ctx.fillStyle = g; ctx.fillRect(X0 + 4, y + 26, w - 8, h - 52);
    ctx.save(); ctx.beginPath(); ctx.rect(X0 + 4, y + 26, w - 8, h - 52); ctx.clip();
    ctx.strokeStyle = 'rgba(246,235,210,.08)'; ctx.lineWidth = 2;
    for (let i = 0, px = X0 + 20; px < X1; px += 52, i++) {
      rhombus(ctx, px, y + h / 2, 18, 30); ctx.stroke();
      rhombus(ctx, px, y + h / 2, 8, 14); ctx.stroke();
    }
    ctx.restore();
    ctx.restore();
    // medallions (spin-in)
    const mp = clamp((ip - .35) / .55);
    if (mp > 0) {
      const s = eBack(mp) * .82, rot = (1 - eOut(mp)) * -Math.PI + Math.sin(t * .8) * .03;
      this.medallion(ctx, X0 + 86, y + h / 2, s, rot, st.flag);
      this.medallion(ctx, X1 - 86, y + h / 2, s, -rot, st.flag);
    }
  },
  wiper(ctx, X, p, li) {
    const { y, h } = this, bw = 46;
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,.4)'; ctx.shadowBlur = 14;
    rr(ctx, X - bw / 2, y + 22, bw, h - 44, 3); ctx.fillStyle = IVORY; ctx.fill(); ctx.shadowColor = 'transparent';
    if (li === 2) { for (let k = 0; k < 3; k++) { ctx.fillStyle = FLAG[k]; ctx.fillRect(X - bw / 2 + 4, y + 26 + k * (h - 52) / 3, bw - 8, (h - 52) / 3); } star8(ctx, X, y + h / 2, 9, '#fff'); }
    else for (let k = 0; k < 4; k++) { rhombus(ctx, X, y + 36 + k * 19, 14, 9); ctx.fillStyle = k % 2 ? INDIGO : RUBY; ctx.fill(); }
    ctx.restore();
  },
};

// ---------- 2. TİRMƏ: gold buta draws itself, termeh pattern drifts, flying buta wipe
const TIRME = {
  y: 910, h: 112,
  area: [X0 + 190, X1 - 110],
  opts: A => ({ col: '#fff', accent: GOLD, tagBg: GOLD, tagCol: '#073740', logoImg: A.white, logoH: 62, fs: 44, shadow: 'rgba(0,0,0,.35)' }),
  bigButa(ctx, x, y, s, rot, dp, fp, flag) {
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
    butaPath(ctx);
    if (fp > 0) { const g = ctx.createLinearGradient(0, -42, 0, 30); g.addColorStop(0, '#0C6A77'); g.addColorStop(1, '#063A43'); ctx.globalAlpha = fp; ctx.fillStyle = g; ctx.fill(); ctx.globalAlpha = 1; }
    ctx.setLineDash([260, 260]); ctx.lineDashOffset = 260 * (1 - dp);
    ctx.lineWidth = 2.6; ctx.strokeStyle = GOLD; ctx.stroke();
    ctx.save(); ctx.translate(2, 6); ctx.scale(.6, .6); butaPath(ctx); ctx.lineWidth = 3; ctx.stroke(); ctx.restore();
    ctx.save(); ctx.translate(3, 10); ctx.scale(.3, .3); butaPath(ctx); ctx.fillStyle = flag ? mix('#D9B45A', FLAG[1], flag) : GOLD; ctx.globalAlpha = dp; ctx.fill(); ctx.restore();
    ctx.setLineDash([]);
    // bead dots along outline
    if (fp > 0) for (let i = 0; i < 9; i++) { const a = -2.2 + i * .55; ctx.beginPath(); ctx.arc(Math.cos(a) * 34 + 2, Math.sin(a) * 30 + 4, 1.8, 0, 7); ctx.fillStyle = GOLD; ctx.globalAlpha = fp; ctx.fill(); }
    ctx.restore();
  },
  bar(ctx, t, ip, st) {
    const { y, h } = this, bx = X0 + 60, w = X1 - bx;
    const lp = eOut(clamp((ip - .3) / .6));
    ctx.save();
    ctx.beginPath(); ctx.rect(bx, y - 30, w * lp, h + 60); ctx.clip();
    ctx.shadowColor = 'rgba(0,0,0,.35)'; ctx.shadowBlur = 22; ctx.shadowOffsetY = 6;
    rr(ctx, bx, y, w, h, [0, 14, 14, 0]);
    const g = ctx.createLinearGradient(bx, 0, X1, 0); g.addColorStop(0, '#0A5864'); g.addColorStop(1, '#06363F');
    ctx.fillStyle = g; ctx.fill(); ctx.shadowColor = 'transparent';
    // termeh buta pattern drifting
    ctx.save(); rr(ctx, bx, y, w, h, [0, 14, 14, 0]); ctx.clip();
    ctx.globalAlpha = .12; ctx.strokeStyle = GOLD; ctx.lineWidth = 2.2;
    const off = (t * 10) % 64;
    for (let r = 0; r < 3; r++) for (let px = bx - 64 + off + (r % 2) * 32; px < X1 + 40; px += 64) {
      ctx.save(); ctx.translate(px, y + 18 + r * 38); ctx.scale(.42, .42); ctx.rotate(r % 2 ? .5 : -.5); if (r % 2) ctx.scale(-1, 1); butaPath(ctx); ctx.stroke(); ctx.restore();
    }
    ctx.restore();
    // double gold hairlines
    ctx.fillStyle = GOLD; for (const yy of [y + 5, y + 10, y + h - 11, y + h - 6]) ctx.fillRect(bx, yy, w, yy === y + 10 || yy === y + h - 11 ? 1 : 2);
    // right-end buta pair
    ctx.save(); ctx.translate(X1 - 52, y + h / 2); ctx.scale(-1, 1);
    this.bigButa(ctx, 0, 0, .9, -.3, 1, 1, st.flag); ctx.restore();
    ctx.restore();
    // emblem draws itself
    const dp = eIO(clamp(ip / .55)), fp = clamp((ip - .4) / .4);
    this.bigButa(ctx, X0 + 70, y + h / 2 - 6, 2.0, -.28 + Math.sin(t * 1.1) * .03, dp, fp, st.flag);
  },
  wiper(ctx, X, p, li) {
    const { y, h } = this, cy = y + h / 2;
    ctx.save();
    for (let k = 1; k < 7; k++) { ctx.beginPath(); ctx.arc(X - k * 18, cy + Math.sin(k * 1.3 + p * 9) * 8, 3.2 - k * .4, 0, 7); ctx.fillStyle = li === 2 ? FLAG[k % 3] : GOLD; ctx.globalAlpha = 1 - k / 7; ctx.fill(); }
    ctx.globalAlpha = 1; ctx.translate(X, cy); ctx.rotate(Math.PI / 2 + Math.sin(p * Math.PI) * .6);
    butaPath(ctx);
    if (li === 2) { const g = ctx.createLinearGradient(0, -42, 0, 30); g.addColorStop(0, FLAG[0]); g.addColorStop(.33, FLAG[0]); g.addColorStop(.34, FLAG[1]); g.addColorStop(.66, FLAG[1]); g.addColorStop(.67, FLAG[2]); g.addColorStop(1, FLAG[2]); ctx.fillStyle = g; }
    else ctx.fillStyle = GOLD;
    ctx.scale(1.25, 1.25);
    ctx.shadowColor = 'rgba(217,180,90,.8)'; ctx.shadowBlur = 18; ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.lineWidth = 2; ctx.strokeStyle = '#073740';
    ctx.save(); ctx.translate(2, 6); ctx.scale(.58, .58); butaPath(ctx); ctx.lineWidth = 3.4; ctx.stroke(); ctx.restore();
    ctx.beginPath(); ctx.arc(3, 12, 4, 0, 7); ctx.fillStyle = '#073740'; ctx.fill();
    ctx.restore();
  },
};

// ---------- 3. TAR: the banner is a tar — body, neck, strings; strings pluck on every change
const TAR = {
  y: 922, h: 92,
  area: [X0 + 300, X1 - 90],
  opts: A => ({ col: '#fff', accent: '#E8E0CF', tagBg: '#EFE6D2', tagCol: TEAL_D, logoImg: A.white, logoH: 58, fs: 42, shadow: 'rgba(0,0,0,.5)' }),
  strings: [-30, -25, -3, 3, 25, 30],
  bar(ctx, t, ip, st) {
    const { y, h } = this, cy = y + h / 2, bx = X0 + 80;
    const bp = eBack(clamp(ip / .45)), np = eOut(clamp((ip - .25) / .5)), sp = eOut(clamp((ip - .5) / .45));
    const neck0 = bx + 150, neckEnd = X1 - 70, nW = (neckEnd - neck0) * np;
    // neck
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,.4)'; ctx.shadowBlur = 20; ctx.shadowOffsetY = 6;
    if (nW > 1) {
      rr(ctx, neck0, y, nW, h, [0, 8, 8, 0]);
      const g = ctx.createLinearGradient(0, y, 0, y + h); g.addColorStop(0, '#0B5F6B'); g.addColorStop(.5, '#084852'); g.addColorStop(1, '#05323A');
      ctx.fillStyle = g; ctx.fill(); ctx.shadowColor = 'transparent';
      ctx.save(); ctx.beginPath(); ctx.rect(neck0, y, nW, h); ctx.clip();
      // frets (tar-style, closer toward the body), nacre dots
      for (let k = 0; k < 22; k++) {
        const fx = neckEnd - (neckEnd - neck0) * (1 - Math.pow(2, -k / 9));
        ctx.fillStyle = 'rgba(217,180,90,.22)'; ctx.fillRect(fx, y + 4, 2, h - 8);
        if ([3, 5, 7, 10, 12].includes(k)) { ctx.beginPath(); ctx.arc(fx - 14, y + h - 9, 3, 0, 7); ctx.fillStyle = 'rgba(232,240,240,.45)'; ctx.fill(); }
      }
      ctx.fillStyle = GOLD; ctx.fillRect(neck0, y, nW, 2); ctx.fillRect(neck0, y + h - 2, nW, 2);
      ctx.restore();
    }
    // peg head
    if (np > .95) {
      const px = neckEnd - 4, a = clamp((ip - .7) / .3);
      ctx.globalAlpha = a; ctx.shadowColor = 'transparent';
      for (let k = 0; k < 3; k++) for (const s of [-1, 1]) {
        rr(ctx, px + 10 + k * 20, s < 0 ? y - 18 : y + h + 2, 10, 16, 4); ctx.fillStyle = '#4A2A1A'; ctx.fill();
        ctx.beginPath(); ctx.arc(px + 15 + k * 20, s < 0 ? y - 18 : y + h + 18, 6, 0, 7); ctx.fillStyle = IVORY; ctx.fill();
      }
      rr(ctx, px, y - 4, 72, h + 8, 8); const g2 = ctx.createLinearGradient(px, 0, px + 72, 0); g2.addColorStop(0, '#5A3322'); g2.addColorStop(1, '#3A1F14'); ctx.fillStyle = g2; ctx.fill();
      star8(ctx, px + 36, cy, 12, GOLD); ctx.globalAlpha = 1;
    }
    ctx.restore();
    // body: double bowl in mulberry wood with nacre trim and membranes
    if (bp > 0) {
      ctx.save(); ctx.translate(bx + 60, cy); ctx.scale(bp, bp); ctx.translate(-(bx + 60), -cy);
      ctx.shadowColor = 'rgba(0,0,0,.4)'; ctx.shadowBlur = 20; ctx.shadowOffsetY = 6;
      const lobes = [[bx, 66], [bx + 96, 50]];
      for (const [lx, r] of lobes) { ctx.beginPath(); ctx.arc(lx, cy, r + 4, 0, 7); ctx.fillStyle = GOLD; ctx.fill(); }
      ctx.shadowColor = 'transparent';
      for (const [lx, r] of lobes) { ctx.beginPath(); ctx.arc(lx, cy, r, 0, 7); const g = ctx.createRadialGradient(lx - r * .3, cy - r * .3, 4, lx, cy, r); g.addColorStop(0, '#7A452C'); g.addColorStop(1, '#3E2015'); ctx.fillStyle = g; ctx.fill(); }
      // nacre dots on rim
      for (const [lx, r] of lobes) for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8; ctx.beginPath(); ctx.arc(lx + Math.cos(a) * (r - 6), cy + Math.sin(a) * (r - 6), 2.2, 0, 7); ctx.fillStyle = 'rgba(230,242,240,.85)'; ctx.fill(); }
      // membranes
      for (const [lx, r] of lobes) { ctx.beginPath(); ctx.arc(lx, cy, r - 13, 0, 7); const g = ctx.createRadialGradient(lx - 8, cy - 8, 2, lx, cy, r - 13); g.addColorStop(0, '#FBF3E2'); g.addColorStop(1, '#E3D3B3'); ctx.fillStyle = g; ctx.fill(); }
      // bridge
      rr(ctx, bx + 6, cy - 34, 7, 68, 3); ctx.fillStyle = '#3A1F14'; ctx.fill();
      // tail piece
      rr(ctx, bx - 72, cy - 10, 14, 20, 4); ctx.fillStyle = GOLD; ctx.fill();
      ctx.restore();
    }
    // strings
    if (sp > 0) {
      const sx0 = bx - 64, sx1 = sx0 + (neckEnd + 6 - sx0) * sp;
      this.strings.forEach((dy, i) => {
        ctx.beginPath();
        for (let x = sx0; x <= sx1; x += 6) {
          const u = (x - sx0) / (neckEnd - sx0);
          const vib = st.pluck * Math.sin(Math.PI * u) * Math.sin(t * 70 + i * 1.7) * (i % 2 ? 1 : .8);
          x === sx0 ? ctx.moveTo(x, cy + dy + vib) : ctx.lineTo(x, cy + dy + vib);
        }
        const flagC = st.flag > 0 ? FLAG[Math.floor(i / 2)] : null;
        ctx.strokeStyle = flagC ? flagC : (i < 2 || i > 3 ? 'rgba(232,224,207,.55)' : 'rgba(217,180,90,.65)');
        ctx.lineWidth = i % 2 ? 1.4 : 1.8; ctx.stroke();
      });
    }
  },
  // custom change: pluck — old text sinks/fades, strings vibrate, new rises
  swap(ctx, p, oldL, newL, draw) {
    const o = clamp(p / .4), n = eOut(clamp((p - .3) / .7));
    if (oldL !== null && o < 1) { ctx.save(); ctx.globalAlpha = 1 - o; ctx.translate(0, o * 18); ctx.filter = `blur(${o * 6}px)`; draw(oldL); ctx.restore(); }
    if (n > 0) { ctx.save(); ctx.globalAlpha = n; ctx.translate(0, (1 - n) * -20); ctx.filter = `blur(${(1 - n) * 6}px)`; draw(newL); ctx.restore(); }
  },
};

// ---------- 4. ŞƏBƏKƏ: Shaki stained-glass lattice assembles piece by piece, light sweeps through
const SEBEKE = {
  y: 902, h: 124,
  area: [X0 + 250, X1 - 250],
  opts: A => ({ col: '#0A4A54', accent: RUBY, tagBg: TEAL, tagCol: '#fff', logoImg: A.teal, logoH: 66, fs: 40 }),
  glass: ['#C0283A', '#1F5FBF', '#1E8E5A', '#E2A93B', '#0B7C8A'],
  bar(ctx, t, ip, st) {
    const { y, h } = this, w = X1 - X0, s = 41.33;
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,.4)'; ctx.shadowBlur = 22; ctx.shadowOffsetY = 6;
    const fp = clamp(ip / .25);
    rr(ctx, X0, y, w, h, 8); ctx.fillStyle = `rgba(42,26,16,${fp})`; ctx.fill(); ctx.shadowColor = 'transparent';
    ctx.save(); rr(ctx, X0 + 6, y + 6, w - 12, h - 12, 4); ctx.clip();
    ctx.fillStyle = '#16233F'; ctx.globalAlpha = fp; ctx.fillRect(X0, y, w, h); ctx.globalAlpha = 1;
    const cols = Math.ceil(w / s) + 1, rows = 4;
    for (let i = 0; i < cols; i++) for (let j = -1; j < 4; j++) {
      const cx = X0 + 6 + i * s, cy = y + h / 2 + (j - 1) * s;
      const hv = hash(i, j);
      const appear = eBack(clamp((ip - .1 - hv * .55 - Math.abs(cx - 960) / 960 * .2) / .25));
      if (appear <= 0) continue;
      let col = this.glass[Math.floor(hv * 5)];
      if (st.flag > 0) col = mix(col.length === 7 ? col : '#000000', FLAG[clamp(j, 0, 2)], st.flag);
      const glim = .85 + .15 * Math.sin(t * 1.6 + hv * 12);
      const r = s * .5 * appear;
      star8Path(ctx, cx, cy, r);
      const g = ctx.createRadialGradient(cx - r * .3, cy - r * .3, 1, cx, cy, r);
      g.addColorStop(0, '#ffffff'); g.addColorStop(.25, col); g.addColorStop(1, col);
      ctx.globalAlpha = glim; ctx.fillStyle = g; ctx.fill(); ctx.globalAlpha = 1;
      ctx.lineWidth = 3.2; ctx.strokeStyle = '#2A1A10'; ctx.stroke();
      // small cross pieces between stars
      if (appear > .9) { rhombus(ctx, cx + s / 2, cy + s / 2, 5, 5); ctx.fillStyle = '#E2A93B'; ctx.fill(); }
    }
    // light sweep (ambient every 6 s + during change)
    const sw = st.sweep >= 0 ? st.sweep : ((t % 6) / 1.4);
    if (sw >= 0 && sw <= 1) {
      const lx = X0 - 200 + (w + 400) * sw;
      ctx.globalCompositeOperation = 'lighter';
      const lg = ctx.createLinearGradient(lx - 120, 0, lx + 120, 0);
      lg.addColorStop(0, 'rgba(255,255,255,0)'); lg.addColorStop(.5, 'rgba(255,240,210,.35)'); lg.addColorStop(1, 'rgba(255,255,255,0)');
      ctx.fillStyle = lg; ctx.fillRect(lx - 120, y, 240, h); ctx.globalCompositeOperation = 'source-over';
    }
    ctx.restore();
    // central ivory panel
    const pp = eOut(clamp((ip - .55) / .4));
    if (pp > 0) {
      const [a0, a1] = [X0 + 230, X1 - 230], cxm = (a0 + a1) / 2, pw = (a1 - a0) * pp;
      ctx.shadowColor = 'rgba(0,0,0,.35)'; ctx.shadowBlur = 12;
      rr(ctx, cxm - pw / 2, y + 16, pw, h - 32, 6); ctx.fillStyle = 'rgba(250,245,233,.97)'; ctx.fill(); ctx.shadowColor = 'transparent';
      ctx.lineWidth = 3; ctx.strokeStyle = '#2A1A10'; ctx.stroke();
      ctx.lineWidth = 1.5; ctx.strokeStyle = GOLD; rr(ctx, cxm - pw / 2 + 6, y + 22, Math.max(0, pw - 12), h - 44, 4); ctx.stroke();
    }
    ctx.restore();
  },
  wiper(ctx, X, p, li) {
    const { y, h } = this;
    ctx.save();
    ctx.globalCompositeOperation = 'source-over';
    const g = ctx.createLinearGradient(X - 30, 0, X + 30, 0);
    g.addColorStop(0, 'rgba(255,240,210,0)'); g.addColorStop(.5, li === 2 ? 'rgba(0,181,226,.55)' : 'rgba(226,169,59,.55)'); g.addColorStop(1, 'rgba(255,240,210,0)');
    ctx.fillStyle = g; ctx.fillRect(X - 30, y + 20, 60, h - 40);
    star8(ctx, X, y + h / 2, 10, li === 2 ? FLAG[1] : RUBY);
    ctx.restore();
  },
};

const VARIANTS = { XALCA, TIRME, TAR, SEBEKE };

// timeline: intro 0..1.6 s; line changes at CH[k]; each change lasts DUR
window.renderFrame = function (ctx, v, t, A, TL) {
  const V = VARIANTS[v], CH = TL.changes, DUR = TL.dur || .9;
  const ip = clamp(t / (TL.intro || 1.6));
  let k = -1; for (let i = 0; i < CH.length; i++) if (t >= CH[i]) k = i;
  const lineOf = i => TL.lines[i];
  const p = k >= 0 ? clamp((t - CH[k]) / DUR) : 0;
  const newL = k >= 0 ? lineOf(k) : null, oldL = k > 0 ? lineOf(k - 1) : null;
  // state for national-element reactions
  const flagNow = newL === 2 ? (p < 1 ? eOut(p) : 1) : (oldL === 2 && p < 1 ? 1 - eOut(p) : 0);
  const pluck = k >= 0 ? 10 * Math.pow(1 - clamp((t - CH[k]) / 1.6), 2) : 0;
  const st = { flag: flagNow, pluck, sweep: (k >= 0 && p < 1) ? p : -1 };
  V.bar(ctx, t, ip, st);
  if (k < 0) return;
  const o = V.opts(A), [a0, a1] = V.area, cy = V.y + V.h / 2 + 1;
  const draw = li => content(ctx, LINES[li], a0, a1, cy, o);
  if (p >= 1) { draw(newL); return; }
  if (V.swap) { V.swap(ctx, p, oldL, newL, draw); return; }
  const X = a0 - 40 + (a1 - a0 + 80) * eIO(p);
  ctx.save(); ctx.beginPath(); ctx.rect(0, 0, X, 1080); ctx.clip(); draw(newL); ctx.restore();
  if (oldL !== null) { ctx.save(); ctx.beginPath(); ctx.rect(X, 0, 1920, 1080); ctx.clip(); draw(oldL); ctx.restore(); }
  V.wiper(ctx, X, p, newL);
};
