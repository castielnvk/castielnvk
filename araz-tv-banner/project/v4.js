// Araz FM TV banner v4 — in the language of the original: white band, Araz teal only,
// faint national-instrument line art, motion-blur text swaps, waving flag reveal.
// window.renderV4(ctx, t, A, TL)   Canvas 1920x1080, transparent.
const T = '#095D6A', T2 = '#0B7482', TL1 = '#5FA9B1', TL2 = '#CFE5E7';
const FLAGC = ['#00B5E2', '#EF3340', '#509E2F'];
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const eOut = p => 1 - Math.pow(1 - p, 3), eIn = p => p * p * p;
const eIO = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const seg = (t, a, b) => clamp((t - a) / (b - a));
const rr = (c, x, y, w, h, r) => { c.beginPath(); c.roundRect(x, y, w, h, r); };

const BY = 866, BH = 214, CY = BY + BH / 2 + 4;

function star8Path(c, cx, cy, r, inner = .72) {
  c.beginPath();
  for (let i = 0; i < 16; i++) { const a = i * Math.PI / 8 - Math.PI / 2, rad = i % 2 ? r * inner : r;
    const x = cx + Math.cos(a) * rad, y = cy + Math.sin(a) * rad; i ? c.lineTo(x, y) : c.moveTo(x, y); }
  c.closePath();
}

// ---------- faint line-art of national instruments (tar, kamança, saz, nağara, qaval, balaban)
const INSTR = {
  tar(c) { c.beginPath(); c.arc(0, 40, 30, 0, 7); c.stroke(); c.beginPath(); c.arc(0, -4, 21, 0, 7); c.stroke();
    c.beginPath(); c.arc(0, 40, 19, 0, 7); c.stroke(); c.strokeRect(-5, -150, 10, 128);
    c.strokeRect(-9, -184, 18, 34); for (let k = 0; k < 3; k++) { c.beginPath(); c.moveTo(-9, -178 + k * 11); c.lineTo(-17, -178 + k * 11); c.moveTo(9, -178 + k * 11); c.lineTo(17, -178 + k * 11); c.stroke(); }
    for (let k = 0; k < 7; k++) { c.beginPath(); c.moveTo(-5, -140 + k * 16); c.lineTo(5, -140 + k * 16); c.stroke(); } },
  kamanca(c) { c.beginPath(); c.arc(0, 20, 28, 0, 7); c.stroke(); c.beginPath(); c.arc(0, 20, 18, 0, 7); c.stroke();
    c.beginPath(); c.moveTo(0, 48); c.lineTo(0, 86); c.stroke(); c.strokeRect(-4, -112, 8, 104); c.beginPath(); c.arc(0, -120, 8, 0, 7); c.stroke();
    c.beginPath(); c.moveTo(-40, -90); c.quadraticCurveTo(-58, 0, -40, 90); c.stroke(); c.beginPath(); c.moveTo(-40, -90); c.lineTo(-40, 90); c.stroke(); },
  saz(c) { c.beginPath(); c.moveTo(0, 70); c.bezierCurveTo(-46, 66, -40, 4, 0, -12); c.bezierCurveTo(40, 4, 46, 66, 0, 70); c.stroke();
    c.beginPath(); c.arc(0, 30, 8, 0, 7); c.stroke(); c.strokeRect(-4, -190, 8, 178);
    for (let k = 0; k < 9; k++) { c.beginPath(); c.moveTo(-4, -180 + k * 18); c.lineTo(4, -180 + k * 18); c.stroke(); } },
  nagara(c) { c.beginPath(); c.ellipse(0, -40, 46, 13, 0, 0, 7); c.stroke(); c.beginPath(); c.moveTo(-46, -40); c.lineTo(-46, 40); c.moveTo(46, -40); c.lineTo(46, 40); c.stroke();
    c.beginPath(); c.ellipse(0, 40, 46, 13, 0, 0, Math.PI); c.stroke();
    c.beginPath(); for (let k = 0; k <= 8; k++) { const x = -46 + k * 11.5; c.lineTo(x, k % 2 ? 36 : -30); } c.stroke(); },
  qaval(c) { c.beginPath(); c.arc(0, 0, 44, 0, 7); c.stroke(); c.beginPath(); c.arc(0, 0, 37, 0, 7); c.stroke();
    for (let k = 0; k < 12; k++) { const a = k / 12 * Math.PI * 2; c.beginPath(); c.arc(Math.cos(a) * 40.5, Math.sin(a) * 40.5, 4, 0, 7); c.stroke(); } },
  balaban(c) { c.strokeRect(-6, -90, 12, 180); c.beginPath(); c.ellipse(0, -96, 10, 6, 0, 0, 7); c.stroke();
    for (let k = 0; k < 6; k++) { c.beginPath(); c.arc(0, -50 + k * 20, 2.5, 0, 7); c.stroke(); } },
};
let PAT = null;
function makePattern() {
  const W = 2400, H = BH, cv = document.createElement('canvas'); cv.width = W; cv.height = H; const c = cv.getContext('2d');
  c.strokeStyle = 'rgba(9,93,106,.075)'; c.lineWidth = 2; c.lineJoin = 'round';
  const order = ['tar', 'qaval', 'kamanca', 'nagara', 'saz', 'balaban'], step = W / 12;
  for (let i = 0; i < 12; i++) {
    const name = order[i % 6], x = step * i + step / 2, y = H / 2 + (i % 2 ? 18 : -10), rot = [-.55, .4, -.35, .2, .6, -.7][i % 6] * (i % 4 < 2 ? 1 : -1);
    for (const dx of [0, W]) { c.save(); c.translate(x + dx - (x > W - step ? W : 0) * 0, y); c.rotate(rot); c.scale(.82, .82); INSTR[name](c); c.restore(); }
    // small eight-point ornaments between instruments
    star8Path(c, x + step / 2, i % 2 ? 40 : H - 40, 7); c.stroke();
  }
  return cv;
}

// ---------- line content, pre-rendered to an offscreen canvas (so it can be motion-blurred)
const LINES = [
  { text: 'Azərbaycanın səsi bu dalğada!', tag: '103.3 FM' },
  { text: 'Bizə rəqəmsalda da qoşul!', social: true },
  { text: 'Milli musiqinin dəyişməz ünvanı!' },
  { logo: true },
];
const CACHE = {};
function lineImage(li, A) {
  if (CACHE[li]) return CACHE[li];
  const cv = document.createElement('canvas'); cv.width = 1920; cv.height = 200; const c = cv.getContext('2d');
  const cy = 100, L = LINES[li], FS = 62; c.textBaseline = 'middle';
  if (L.logo) {
    const img = A.teal, lw = img.width, lh = img.height; // native size, unscaled
    c.font = `700 40px Montserrat`; const tw = Math.max(c.measureText('QOVUŞDURAN').width, c.measureText('RADİO!').width);
    const gap = 30, W = lw + gap * 2 + tw, sx = 960 - W / 2;
    c.drawImage(img, Math.round(sx), Math.round(cy - lh / 2));
    c.fillStyle = T; c.fillRect(sx + lw + gap - 1.5, cy - 44, 3, 88);
    c.fillStyle = T; c.textAlign = 'left'; c.fillText('QOVUŞDURAN', sx + lw + gap * 2, cy - 22); c.fillText('RADİO!', sx + lw + gap * 2, cy + 24);
  } else {
    c.font = `600 ${FS}px Montserrat`; const tw = c.measureText(L.text).width;
    let extra = 0, tagW = 0;
    if (L.tag) { c.font = `800 ${FS * .62}px Montserrat`; tagW = c.measureText(L.tag).width + 50; extra = 46 + tagW; }
    if (L.social) { c.font = `600 ${FS * .62}px Montserrat`; extra = 66 + 3 * 54 + 18 + c.measureText('arazfm.az').width; }
    let x = 960 - (tw + extra) / 2;
    c.font = `600 ${FS}px Montserrat`; c.fillStyle = T; c.textAlign = 'left'; c.fillText(L.text, x, cy + 3); x += tw;
    if (L.tag) { x += 46; rr(c, x, cy - 34, tagW, 68, 34); c.fillStyle = T; c.fill(); c.font = `800 ${FS * .62}px Montserrat`; c.fillStyle = '#fff'; c.textAlign = 'center'; c.fillText(L.tag, x + tagW / 2, cy + 2); }
    if (L.social) {
      x += 66; const s = 34; c.strokeStyle = T; c.fillStyle = T; c.lineWidth = 3.2;
      c.font = `800 ${s * 1.05}px Montserrat`; c.textAlign = 'center'; c.fillText('f', x + 10, cy + 2); x += 54;
      rr(c, x - s / 2 + 8, cy - s / 2, s, s, 9); c.stroke(); c.beginPath(); c.arc(x + 8, cy, 7.5, 0, 7); c.stroke(); c.beginPath(); c.arc(x + 17, cy - 9, 2, 0, 7); c.fill(); x += 54;
      rr(c, x - 15, cy - 15, 46, 31, 9); c.stroke(); c.beginPath(); c.moveTo(x + 3, cy - 7); c.lineTo(x + 16, cy); c.lineTo(x + 3, cy + 7); c.closePath(); c.fill(); x += 54;
      c.font = `600 ${FS * .62}px Montserrat`; c.textAlign = 'left'; c.fillText('arazfm.az', x, cy + 2);
    }
  }
  return (CACHE[li] = cv);
}
// motion-blurred draw: dx offset, spread = blur length in px (to the trailing side), a = alpha
function drawBlurred(c, img, dx, spread, a, dir) {
  if (a <= .002) return;
  const n = spread > 2 ? Math.min(40, Math.ceil(spread / 6) + 4) : 1;
  for (let i = 0; i < n; i++) {
    const f = n === 1 ? 0 : i / (n - 1);
    c.globalAlpha = a * (n === 1 ? 1 : (1.6 / n) * (1 - f * .6));
    c.drawImage(img, dx - dir * spread * f, CY - 100 - 2);
  }
  c.globalAlpha = 1;
}

// ---------- waving flag (with crescent and eight-point star)
let FLAGIMG = null;
function makeFlag() {
  const W = 600, H = 300, cv = document.createElement('canvas'); cv.width = W; cv.height = H; const c = cv.getContext('2d');
  FLAGC.forEach((col, k) => { c.fillStyle = col; c.fillRect(0, k * H / 3, W, H / 3 + 1); });
  const cx = W / 2, cy = H / 2;
  c.beginPath(); c.arc(cx - 12, cy, 45, 0, 7); c.fillStyle = '#fff'; c.fill();
  c.beginPath(); c.arc(cx - 1, cy, 37.5, 0, 7); c.fillStyle = FLAGC[1]; c.fill();
  star8Path(c, cx + 47, cy, 22, .55); c.fillStyle = '#fff'; c.fill();
  return cv;
}
function drawFlag(c, t, open, cx, cy) {
  if (open <= 0) return;
  const W = 330, H = 165, w = W * open, x0 = cx - w / 2, sw = 3;
  for (let x = 0; x < w; x += sw) {
    const u = x / w, gx = x0 + x;
    const ph = gx / 70 - t * 5.2, amp = 7 * (0.35 + u * .65);
    const off = Math.sin(ph) * amp, sl = Math.cos(ph);
    const srcX = (x / w) * 600;
    c.drawImage(FLAGIMG, srcX, 0, Math.max(1, sw / w * 600), 300, gx, cy - H / 2 + off, sw + .5, H);
    c.fillStyle = sl > 0 ? `rgba(255,255,255,${sl * .16})` : `rgba(0,0,0,${-sl * .18})`; c.fillRect(gx, cy - H / 2 + off, sw + .5, H);
  }
}

// ---------- scene
// TL: { lines: [li...], at: [start times], flagAt: time the flag opens, flagDur, loop }
window.renderV4 = function (c, t, A, TL) {
  if (!PAT) PAT = makePattern();
  if (!FLAGIMG) FLAGIMG = makeFlag();
  const intro = TL.noIntro ? 1 : seg(t, 0, .8);
  // band (slides up on first appearance)
  const by = BY + (1 - eOut(intro)) * (BH + 10);
  c.save();
  c.shadowColor = 'rgba(0,0,0,.18)'; c.shadowBlur = 24; c.shadowOffsetY = -2;
  const g = c.createLinearGradient(0, by, 0, by + BH); g.addColorStop(0, '#FFFFFF'); g.addColorStop(1, '#EEF6F6');
  c.fillStyle = g; c.fillRect(0, by, 1920, 1080 - by + 2); c.shadowColor = 'transparent';
  // drifting instrument line-art
  const off = (t * 9) % 1200;
  c.drawImage(PAT, -off, by); c.drawImage(PAT, 2400 - off, by);
  // top edge: Araz teal rule + living sound-wave line
  c.fillStyle = T; c.fillRect(0, by, 1920, 4);
  c.beginPath();
  for (let x = 0; x <= 1920; x += 4) {
    const env = .55 + .45 * Math.sin(x / 300 - t * .9);
    const y = by + 13 + Math.sin(x / 26 - t * 6) * 3.2 * env + Math.sin(x / 9 + t * 3) * .8 * env;
    x ? c.lineTo(x, y) : c.moveTo(x, y);
  }
  c.strokeStyle = 'rgba(11,116,130,.55)'; c.lineWidth = 1.6; c.stroke();
  // soft teal glints travelling along the rule
  const gx = ((t * 340) % 2900) - 500, gg = c.createLinearGradient(gx - 220, 0, gx + 220, 0);
  gg.addColorStop(0, 'rgba(127,209,214,0)'); gg.addColorStop(.5, 'rgba(160,230,234,.95)'); gg.addColorStop(1, 'rgba(127,209,214,0)');
  c.fillStyle = gg; c.fillRect(gx - 220, by, 440, 4);
  c.restore();
  if (intro < 1) { /* text comes in after the band */ }

  // which line is on, and swap progress
  const at = TL.at; let k = -1; for (let i = 0; i < at.length; i++) if (t >= at[i]) k = i;
  if (k < 0) return;
  const li = TL.lines[k], prev = k > 0 ? TL.lines[k - 1] : (TL.loopPrev ?? null), tc = t - at[k];
  const yShift = by - BY;
  c.save(); c.translate(0, yShift);
  // clip text to band
  c.beginPath(); c.rect(0, BY + 6, 1920, BH); c.clip();

  const viaFlag = li === 3 && prev === 2;
  if (viaFlag) {
    // flag opens from centre over the old line, waves, then folds back revealing the logo line
    const D = TL.flagDur || 3.0;
    const open = tc < .7 ? eOut(seg(tc, 0, .7)) : (tc < D - .6 ? 1 : 1 - eIO(seg(tc, D - .6, D)));
    const oldA = 1 - seg(tc, .05, .5);
    if (oldA > 0) drawBlurred(c, lineImage(2, A), 0, 60 * (1 - oldA), oldA, 1);
    if (tc > D - .55) {
      const r = eOut(seg(tc, D - .55, D + .25)), half = 960 * r + 40;
      c.save(); c.beginPath(); c.rect(960 - half, 0, half * 2, 1080); c.clip();
      drawBlurred(c, lineImage(3, A), 0, 0, 1, 1); c.restore();
    }
    c.restore();
    drawFlag(c, t, open, 960, CY + yShift);
    // thin teal sparkle line that the flag "unzips" from
    if (tc < .35) { const a = 1 - tc / .35; c.fillStyle = `rgba(11,116,130,${a})`; c.fillRect(960 - 2, CY + yShift - 90 * eOut(tc / .35), 4, 180 * eOut(tc / .35)); }
    return;
  }
  // standard swap: horizontal motion-blur (old exits left, new arrives from right) with a light streak
  const S = .75, p = seg(tc, 0, S);
  if (prev !== null && p < 1) {
    const po = seg(tc, 0, .38);
    drawBlurred(c, lineImage(prev, A), -520 * eIn(po), 260 * po, 1 - po, -1);
  }
  const pn = seg(tc, .22, S);
  drawBlurred(c, lineImage(li, A), 520 * (1 - eOut(pn)), 260 * (1 - eOut(pn)), eOut(seg(tc, .22, .55)), 1);
  c.restore();
  if (p > 0 && p < 1) {
    const sx = 1920 * (1 - eIO(p)), sg = c.createLinearGradient(sx - 40, 0, sx + 700, 0);
    sg.addColorStop(0, 'rgba(255,255,255,0)'); sg.addColorStop(.08, 'rgba(95,169,177,.6)'); sg.addColorStop(1, 'rgba(95,169,177,0)');
    c.fillStyle = sg; c.fillRect(sx - 40, CY + yShift - 1.5, 740, 3);
  }
};
