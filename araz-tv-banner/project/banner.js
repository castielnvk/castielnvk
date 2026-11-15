// Araz FM TV banner — design variants (canvas 1920x1080, transparent).
// draw(ctx, variant, lineIdx, t) ; t = 0..1 progress used later for animation (1 = settled).

const TEAL = '#095D6A', TEAL_D = '#06424B', TEAL_L = '#7FD1D6';
const FLAG = ['#00B5E2', '#EF3340', '#509E2F'];

const LINES = [
  { text: 'Azərbaycanın səsi bu dalğada!', tag: '103.3 FM' },
  { text: 'Bizə rəqəmsalda da qoşul!', social: true },
  { text: 'Milli musiqinin dəyişməz ünvanı!', flag: true },
  { logo: true, text: 'QOVUŞDURAN RADİO!' },
];

function rr(ctx, x, y, w, h, r) {
  ctx.beginPath(); ctx.roundRect(x, y, w, h, r);
}

// 8-pointed star (Azerbaijani flag star / carpet motif)
function star8(ctx, cx, cy, r, fill) {
  ctx.save(); ctx.translate(cx, cy); ctx.fillStyle = fill;
  for (let k = 0; k < 2; k++) {
    ctx.save(); ctx.rotate(k * Math.PI / 4);
    ctx.fillRect(-r * 0.72, -r * 0.72, r * 1.44, r * 1.44); ctx.restore();
  }
  ctx.restore();
}
function star8Outline(ctx, cx, cy, r, stroke, lw) {
  ctx.save(); ctx.translate(cx, cy); ctx.strokeStyle = stroke; ctx.lineWidth = lw;
  ctx.beginPath();
  for (let i = 0; i < 16; i++) {
    const a = i * Math.PI / 8 - Math.PI / 2, rad = i % 2 ? r * 0.62 : r;
    i ? ctx.lineTo(Math.cos(a) * rad, Math.sin(a) * rad) : ctx.moveTo(Math.cos(a) * rad, Math.sin(a) * rad);
  }
  ctx.closePath(); ctx.stroke(); ctx.restore();
}

// buta (paisley) with curled tip and inner motif
function butaPath(ctx) {
  ctx.beginPath();
  ctx.moveTo(0, 30);
  ctx.bezierCurveTo(24, 30, 32, 6, 24, -12);
  ctx.bezierCurveTo(17, -28, 2, -40, -14, -42);
  ctx.bezierCurveTo(-22, -43, -24, -34, -16, -30);
  ctx.bezierCurveTo(-8, -26, -6, -18, -14, -10);
  ctx.bezierCurveTo(-28, 4, -24, 30, 0, 30);
  ctx.closePath();
}
function buta(ctx, x, y, s, fill, rot = 0, inner) {
  ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s);
  butaPath(ctx); ctx.fillStyle = fill; ctx.fill();
  if (inner) {
    ctx.save(); ctx.translate(2, 6); ctx.scale(0.55, 0.55); butaPath(ctx);
    ctx.strokeStyle = inner; ctx.lineWidth = 4; ctx.stroke(); ctx.restore();
    ctx.beginPath(); ctx.arc(3, 12, 4, 0, 7); ctx.fillStyle = inner; ctx.fill();
  }
  ctx.restore();
}

// social glyphs (generic)
function socialIcons(ctx, x, cy, size, col) {
  ctx.save(); ctx.strokeStyle = col; ctx.fillStyle = col; ctx.lineWidth = size * 0.09;
  const s = size;
  // f
  ctx.font = `800 ${s * 1.0}px Montserrat`; ctx.textBaseline = 'middle'; ctx.textAlign = 'center';
  ctx.fillText('f', x + s * 0.3, cy + s * 0.04);
  // instagram
  let ix = x + s * 1.75;
  rr(ctx, ix - s / 2, cy - s / 2, s, s, s * 0.28); ctx.stroke();
  ctx.beginPath(); ctx.arc(ix, cy, s * 0.22, 0, 7); ctx.stroke();
  ctx.beginPath(); ctx.arc(ix + s * 0.26, cy - s * 0.26, s * 0.06, 0, 7); ctx.fill();
  // youtube
  let yx = x + s * 3.55;
  rr(ctx, yx - s * 0.68, cy - s * 0.46, s * 1.36, s * 0.92, s * 0.26); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(yx - s * 0.16, cy - s * 0.22); ctx.lineTo(yx + s * 0.24, cy); ctx.lineTo(yx - s * 0.16, cy + s * 0.22); ctx.closePath(); ctx.fill();
  ctx.restore();
  return s * 4.3; // width used
}

// generic content layout: returns nothing, draws centered content within [x0,x1]
function content(ctx, L, x0, x1, cy, o) {
  const fs = o.fs || 46;
  ctx.save(); ctx.textBaseline = 'middle';
  if (L.logo) {
    const img = o.logoImg, lh = o.logoH, lw = img.width * lh / img.height;
    ctx.font = `800 ${fs * 0.9}px Montserrat`;
    const tw = ctx.measureText(L.text).width, gap = 34;
    const W = lw + gap * 2 + tw, sx = (x0 + x1) / 2 - W / 2;
    ctx.drawImage(img, sx, cy - lh / 2, lw, lh);
    ctx.fillStyle = o.accent; ctx.fillRect(sx + lw + gap - 1.5, cy - lh * 0.42, 3, lh * 0.84);
    ctx.fillStyle = o.col; ctx.textAlign = 'left';
    if (o.letterSp) ctx.letterSpacing = o.letterSp;
    ctx.fillText(L.text, sx + lw + gap * 2, cy + 2);
    ctx.restore(); return;
  }
  ctx.font = `700 ${fs}px Montserrat`;
  const tw = ctx.measureText(L.text).width;
  let extra = 0, tagW = 0;
  if (L.tag) { ctx.font = `800 ${fs * 0.72}px Montserrat`; tagW = ctx.measureText(L.tag).width + 44; extra = 30 + 28 + 30 + tagW; }
  if (L.social) { ctx.font = `700 ${fs * 0.72}px Montserrat`; extra = 60 + (fs * 0.62) * 4.3 + 24 + ctx.measureText('arazfm.az').width; }
  if (L.flag) extra = 0;
  const W = tw + extra; let sx = (x0 + x1) / 2 - W / 2;
  if (L.flag && o.flagStars !== false) {
    star8(ctx, sx - 40, cy, 13, FLAG[0]);
    star8(ctx, sx + tw + 40, cy, 13, FLAG[2]);
  }
  ctx.font = `700 ${fs}px Montserrat`; ctx.fillStyle = o.col; ctx.textAlign = 'left';
  ctx.fillText(L.text, sx, cy + 2);
  let x = sx + tw;
  if (L.tag) {
    x += 30; star8(ctx, x + 14, cy, 12, o.accent); x += 28 + 30;
    rr(ctx, x, cy - fs * 0.62, tagW, fs * 1.24, fs * 0.62); ctx.fillStyle = o.tagBg; ctx.fill();
    ctx.font = `800 ${fs * 0.72}px Montserrat`; ctx.fillStyle = o.tagCol; ctx.textAlign = 'center';
    ctx.fillText(L.tag, x + tagW / 2, cy + 2);
  }
  if (L.social) {
    x += 60; const isz = fs * 0.62;
    x += socialIcons(ctx, x, cy, isz, o.col) + 24;
    ctx.font = `700 ${fs * 0.72}px Montserrat`; ctx.fillStyle = o.col; ctx.textAlign = 'left';
    ctx.fillText('arazfm.az', x, cy + 2);
  }
  ctx.restore();
}

// ---------------- variants ----------------
const VARIANTS = {
  // A — Firuzə dalğa: dark teal panel, white type, wave line, star pattern
  A(ctx, L, A) {
    const x = 96, y = 916, w = 1728, h = 108;
    ctx.save();
    ctx.shadowColor = 'rgba(0,0,0,0.35)'; ctx.shadowBlur = 24; ctx.shadowOffsetY = 6;
    rr(ctx, x, y, w, h, 16);
    const g = ctx.createLinearGradient(x, 0, x + w, 0);
    g.addColorStop(0, '#0B7381'); g.addColorStop(0.5, TEAL); g.addColorStop(1, TEAL_D);
    ctx.fillStyle = g; ctx.fill(); ctx.restore();
    // star pattern
    ctx.save(); rr(ctx, x, y, w, h, 16); ctx.clip();
    for (let px = x + 30; px < x + w; px += 62) for (let py = y + 22; py < y + h; py += 62)
      star8Outline(ctx, px + ((py - y) % 124 ? 31 : 0), py, 15, 'rgba(255,255,255,0.06)', 2);
    // wave line along top
    ctx.beginPath();
    for (let i = 0; i <= w; i += 4) {
      const yy = y + 10 + Math.sin(i / 38) * 4 * Math.sin(Math.PI * i / w);
      i ? ctx.lineTo(x + i, yy) : ctx.moveTo(x + i, yy);
    }
    ctx.strokeStyle = TEAL_L; ctx.lineWidth = 2.5; ctx.globalAlpha = 0.8; ctx.stroke();
    ctx.restore();
    // flag hairline at bottom
    for (let k = 0; k < 3; k++) { ctx.fillStyle = FLAG[k]; ctx.fillRect(x + w / 2 - 120 + k * 80, y + h - 5, 80, 5); }
    content(ctx, L, x, x + w, y + h / 2 + 2, { col: '#fff', accent: TEAL_L, tagBg: '#fff', tagCol: TEAL, logoImg: A.white, logoH: 66, fs: 46 });
  },

  // B — Xalça haşiyəsi: ivory bar with carpet border on top, teal type
  B(ctx, L, A) {
    const x = 96, y = 904, w = 1728, h = 120, bh = 18;
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.25)'; ctx.shadowBlur = 20; ctx.shadowOffsetY = 4;
    rr(ctx, x, y, w, h, 10); ctx.fillStyle = '#FBF8F1'; ctx.fill(); ctx.restore();
    ctx.save(); rr(ctx, x, y, w, h, 10); ctx.clip();
    // carpet border strip
    ctx.fillStyle = TEAL; ctx.fillRect(x, y, w, bh);
    const step = 36;
    for (let i = 0; i < w / step + 1; i++) {
      const cx = x + i * step + step / 2, cy = y + bh / 2;
      ctx.beginPath(); ctx.moveTo(cx, cy - 7); ctx.lineTo(cx + 9, cy); ctx.lineTo(cx, cy + 7); ctx.lineTo(cx - 9, cy); ctx.closePath();
      ctx.fillStyle = i % 2 ? '#B8323C' : '#F3E3C3'; ctx.fill();
      ctx.fillStyle = TEAL; ctx.fillRect(cx - 2, cy - 2, 4, 4);
      ctx.fillStyle = '#F3E3C3'; ctx.fillRect(cx + step / 2 - 1.5, cy - 1.5, 3, 3);
    }
    ctx.fillStyle = '#B8323C'; ctx.fillRect(x, y + bh, w, 3);
    // faint buta corners
    buta(ctx, x + 64, y + 72, 1.1, 'rgba(9,93,106,0.10)', -0.3);
    ctx.save(); ctx.translate(x + w - 64, 0); ctx.scale(-1, 1); buta(ctx, 0, y + 72, 1.1, 'rgba(9,93,106,0.10)', -0.3); ctx.restore();
    ctx.restore();
    content(ctx, L, x, x + w, y + bh + (h - bh) / 2 + 2, { col: TEAL, accent: '#B8323C', tagBg: TEAL, tagCol: '#fff', logoImg: A.teal, logoH: 66, fs: 44 });
  },

  // C — Kapsul: floating dark-glass pill with teal star badge
  C(ctx, L, A) {
    const w = 1560, h = 88, x = (1920 - w) / 2, y = 930;
    ctx.save(); ctx.shadowColor = 'rgba(0,0,0,0.4)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 8;
    rr(ctx, x, y, w, h, h / 2); ctx.fillStyle = 'rgba(6,30,36,0.86)'; ctx.fill(); ctx.restore();
    ctx.save(); rr(ctx, x, y, w, h, h / 2); ctx.strokeStyle = 'rgba(127,209,214,0.35)'; ctx.lineWidth = 1.5; ctx.stroke(); ctx.restore();
    // badge
    const bx = x + h / 2, by = y + h / 2;
    ctx.beginPath(); ctx.arc(bx, by, h / 2 - 6, 0, 7); ctx.fillStyle = TEAL; ctx.fill();
    star8(ctx, bx, by, 19, '#fff'); star8(ctx, bx, by, 9, TEAL);
    // flag ticks at right end
    for (let k = 0; k < 3; k++) { ctx.fillStyle = FLAG[k]; rr(ctx, x + w - 64 + k * 14, by - 14, 8, 28, 4); ctx.fill(); }
    content(ctx, L, x + h, x + w - 70, by + 1, { col: '#fff', accent: TEAL_L, tagBg: TEAL, tagCol: '#fff', logoImg: A.white, logoH: 56, fs: 40, flagStars: false });
  },

  // D — Bayraq xətti: full-width white band, tricolour top rule, buta at left
  D(ctx, L, A) {
    const y = 948, h = 132;
    const g = ctx.createLinearGradient(0, y, 0, 1080);
    g.addColorStop(0, 'rgba(255,255,255,0.97)'); g.addColorStop(1, 'rgba(244,250,250,0.97)');
    ctx.fillStyle = g; ctx.fillRect(0, y, 1920, h);
    for (let k = 0; k < 3; k++) { ctx.fillStyle = FLAG[k]; ctx.fillRect(0, y + k * 4, 1920, 4); }
    // buta ornaments both ends (mirrored)
    buta(ctx, 150, y + 70, 0.95, TEAL, -0.25, '#fff');
    ctx.save(); ctx.translate(1920, 0); ctx.scale(-1, 1); buta(ctx, 150, y + 70, 0.95, TEAL, -0.25, '#fff'); ctx.restore();
    content(ctx, L, 260, 1660, y + 12 + (h - 12) / 2 - 6, { col: TEAL, accent: '#EF3340', tagBg: TEAL, tagCol: '#fff', logoImg: A.teal, logoH: 66, fs: 44 });
  },
};

window.drawBanner = function (ctx, v, li, assets) {
  ctx.clearRect(0, 0, 1920, 1080);
  VARIANTS[v](ctx, LINES[li], assets);
};
