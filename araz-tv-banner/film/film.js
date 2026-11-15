// Araz FM — cinematic lower-third film. Canvas 1920x1080, transparent above the band.
// One continuous journey: radio dial → river glint → phone glass → saz string → bridge → logo lockup.
// window.renderFilm(ctx, t, A)   t in seconds, loops every DUR seconds.

// ───────────── EDITABLE COPY (each line is its own text layer) ─────────────
const COPY = {
  s1: 'Azərbaycanın səsi bu dalğada!', s1dash: '—', s1freq: '103.3', s1fm: 'FM',
  s2: 'Bizə rəqəmsalda da qoşul!', s2url: 'arazfm.az',
  s3: 'Milli musiqinin dəyişməz ünvanı!',
  s4: 'Qovuşduran radio!',            // sits right of the official logo and a fine divider
};
const FONT = 'Montserrat';
const TEAL = '#095D6A', IVORY = '#F5EEDC', WARM = '#FFC98A';
const FLAGC = ['#00B5E2', '#EF3340', '#509E2F'];
// ────────────────────────────────────────────────────────────────────────────

const DUR = 20, T = [0, 4.7, 9.7, 14.6];       // scene start times
const BY = 864, BH = 216, LY = 62;             // band top, band height, the matched line (string / bridge)
const clamp = (v, a = 0, b = 1) => Math.max(a, Math.min(b, v));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eOut = p => 1 - Math.pow(1 - p, 3), eOut5 = p => 1 - Math.pow(1 - p, 5), eIn = p => p * p * p;
const eIO = p => p < .5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2;
const eBack = p => { const c = 1.4; return 1 + (c + 1) * Math.pow(p - 1, 3) + c * Math.pow(p - 1, 2); };
const hash = (i, j = 0) => { const x = Math.sin(i * 127.1 + j * 311.7) * 43758.5453; return x - Math.floor(x); };
const rr = (c, x, y, w, h, r) => { c.beginPath(); c.roundRect(x, y, w, h, r); };
const mk = (w, h) => { const cv = document.createElement('canvas'); cv.width = w; cv.height = h; return cv; };

let SC = null, TMP = null, TMP2 = null;       // scene buffers
function tile(c, img, ox, y, h, w = img.width * h / img.height) {
  ox = ((ox % w) + w) % w;
  for (let x = -ox; x < 1920; x += w) c.drawImage(img, x, y, w, h);
}
function tileMirror(c, img, ox, y, h) {
  const w = img.width * h / img.height, per = w * 2; ox = ((ox % per) + per) % per;
  for (let x = -ox, k = 0; x < 1920; x += w, k++) {
    if (k % 2) { c.save(); c.translate(x + w, 0); c.scale(-1, 1); c.drawImage(img, 0, y, w, h); c.restore(); } else c.drawImage(img, x, y, w, h);
  }
}
// water: base + caustic net + sparkle (two caustic layers multiplied), all drifting
function water(c, A, t, x, y, w, h, flowX = 30, flowY = 0, amt = 1) {
  c.save(); c.beginPath(); c.rect(x, y, w, h); c.clip();
  tile(c, A.waterBase, t * flowX * .4, y, 432);
  const b = TMP.getContext('2d'); b.globalCompositeOperation = 'source-over'; b.clearRect(0, 0, 1920, 432);
  tile(b, A.c0, t * flowX, -((t * flowY) % 432), 432); tile(b, A.c0, t * flowX, 432 - ((t * flowY) % 432), 432);
  b.globalCompositeOperation = 'multiply';
  tile(b, A.c1, -t * flowX * .6 + 300, -(((t * flowY * .6) % 432) + 432) % 432, 432); tile(b, A.c1, -t * flowX * .6 + 300, 432 - (((t * flowY * .6) % 432) + 432) % 432, 432);
  c.globalCompositeOperation = 'lighter';
  c.globalAlpha = amt; for (let k = 0; k < 3; k++) c.drawImage(TMP, 0, 0, 1920, 432, 0, y, 1920, 432);
  c.globalAlpha = .16 * amt; tile(c, A.c0, t * flowX * .8 + 90, y, 432);
  c.restore();
}
function plate(c, x, y, w, h, r, a = 1) { // stable, high-contrast reading surface (frosted deep-teal glass)
  if (a <= 0) return;
  const b = TMP2.getContext('2d'); b.clearRect(0, 0, 1920, BH); b.drawImage(c.canvas, 0, 0);
  c.save(); c.globalAlpha = a; rr(c, x, y, w, h, r); c.clip();
  c.filter = 'blur(14px)'; c.drawImage(TMP2, 0, 0); c.filter = 'none';
  const g = c.createLinearGradient(0, y, 0, y + h); g.addColorStop(0, 'rgba(6,58,67,.80)'); g.addColorStop(1, 'rgba(3,34,40,.88)'); c.fillStyle = g; c.fillRect(x, y, w, h);
  const hg = c.createLinearGradient(0, y, 0, y + h * .5); hg.addColorStop(0, 'rgba(255,255,255,.10)'); hg.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = hg; c.fillRect(x, y, w, h * .5);
  c.restore();
  c.save(); c.globalAlpha = a; rr(c, x + .5, y + .5, w - 1, h - 1, r); c.strokeStyle = 'rgba(245,238,220,.30)'; c.lineWidth = 1; c.stroke(); c.restore();
}
function ivoryText(c, txt, x, y, font, a = 1, align = 'left') {
  if (a <= 0) return; c.save(); c.globalAlpha = clamp(a); c.font = font; c.textAlign = align; c.textBaseline = 'middle';
  c.shadowColor = 'rgba(0,0,0,.55)'; c.shadowBlur = 8; c.shadowOffsetY = 2; c.fillStyle = IVORY; c.fillText(txt, x, y); c.restore();
}
// left-to-right soft wipe reveal of a text line
function wipeText(c, txt, x, y, font, p, align = 'left') {
  if (p <= 0) return; c.font = font; const w = c.measureText(txt).width, x0 = align === 'center' ? x - w / 2 : x;
  c.save(); c.beginPath(); c.rect(x0 - 12, y - 60, (w + 24) * eOut(p), 120); c.clip();
  ivoryText(c, txt, x, y + (1 - eOut(p)) * 6, font, 1, align); c.restore();
  if (p < 1) { const ex = x0 - 12 + (w + 24) * eOut(p), g = c.createRadialGradient(ex, y, 0, ex, y, 44); g.addColorStop(0, 'rgba(255,214,160,.55)'); g.addColorStop(1, 'rgba(255,214,160,0)');
    c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = g; c.fillRect(ex - 44, y - 44, 88, 88); c.restore(); }
}
function glassSheen(c, t, a = 1) { // slow reflections living in a sheet of glass
  c.save(); c.globalCompositeOperation = 'lighter';
  for (let k = 0; k < 2; k++) {
    const x = ((t * (38 + k * 22) + k * 900) % 2700) - 400, g = c.createLinearGradient(x, 0, x + 260 + k * 120, 0);
    g.addColorStop(0, 'rgba(255,255,255,0)'); g.addColorStop(.5, `rgba(255,250,235,${(.07 - k * .02) * a})`); g.addColorStop(1, 'rgba(255,255,255,0)');
    c.save(); c.transform(1, 0, -.7, 1, 0, 0); c.fillStyle = g; c.fillRect(x + 80, 0, 400, BH); c.restore();
  }
  const tg = c.createLinearGradient(0, 0, 0, 26); tg.addColorStop(0, `rgba(255,255,255,${.16 * a})`); tg.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = tg; c.fillRect(0, 0, 1920, 26);
  c.restore();
}
function vignette(c, k = .5) {
  const h = c.createLinearGradient(0, 0, 1920, 0); h.addColorStop(0, `rgba(1,18,22,${k})`); h.addColorStop(.14, 'rgba(1,18,22,0)'); h.addColorStop(.86, 'rgba(1,18,22,0)'); h.addColorStop(1, `rgba(1,18,22,${k})`);
  c.fillStyle = h; c.fillRect(0, 0, 1920, BH);
}

// ═════════════════════════ SCENE 1 — the dial ═════════════════════════
const PPM = 168; // pixels per MHz (macro)
function dialFreq(u) { return u <= 0 ? 88 : 88 + 15.3 * eIO(seg(u, 0, 1.35)) + (u > 1.3 ? .22 * Math.sin((u - 1.3) * 20) * Math.exp(-(u - 1.3) * 7) : 0); }
function s1Layout(c) {
  c.font = `600 48px ${FONT}`; const wA = c.measureText(COPY.s1).width;
  c.font = `500 48px ${FONT}`; const wD = c.measureText(COPY.s1dash).width;
  c.font = `800 112px ${FONT}`; const wF = c.measureText(COPY.s1freq).width;
  c.font = `700 40px ${FONT}`; const wM = c.measureText(COPY.s1fm).width;
  const total = wA + 34 + wD + 34 + wF + 14 + wM, x0 = (1920 - total) / 2;
  return { xA: x0, xD: x0 + wA + 34, xF: x0 + wA + 34 + wD + 34, wF, xM: x0 + wA + 34 + wD + 34 + wF + 14 };
}
function sceneDial(c, u, t, A) {
  const L = s1Layout(c), NX = L.xF + L.wF / 2, f = dialFreq(u);
  tile(c, A.metal, 0, 0, BH);
  const dg = c.createLinearGradient(0, 70, 0, BH); dg.addColorStop(0, 'rgba(2,26,31,0)'); dg.addColorStop(1, 'rgba(2,26,31,.62)'); c.fillStyle = dg; c.fillRect(0, 70, 1920, BH - 70);
  // recessed scale window
  c.fillStyle = 'rgba(2,28,34,.62)'; c.fillRect(0, 12, 1920, 72);
  const ig = c.createLinearGradient(0, 12, 0, 30); ig.addColorStop(0, 'rgba(0,0,0,.55)'); ig.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = ig; c.fillRect(0, 12, 1920, 18);
  c.fillStyle = 'rgba(255,255,255,.14)'; c.fillRect(0, 84, 1920, 1.2); c.fillStyle = 'rgba(0,0,0,.45)'; c.fillRect(0, 11, 1920, 1.2);
  // warm backlight that travels along the scale, then rests behind the indicator
  const lx = u < 1.35 ? -200 + (NX + 200) * eIO(seg(u, 0, 1.35)) : NX;
  const wl = c.createRadialGradient(lx, 48, 0, lx, 48, 420); wl.addColorStop(0, 'rgba(255,196,128,.50)'); wl.addColorStop(.4, 'rgba(255,170,96,.16)'); wl.addColorStop(1, 'rgba(255,170,96,0)');
  c.save(); c.beginPath(); c.rect(0, 12, 1920, 72); c.clip(); c.globalCompositeOperation = 'lighter'; c.fillStyle = wl; c.fillRect(lx - 420, 12, 840, 72); c.restore();
  // engraved scale, with motion blur while it travels
  const speed = Math.abs(dialFreq(u) - dialFreq(u - .04)), sub = speed > .05 ? 5 : 1;
  c.save(); c.beginPath(); c.rect(0, 12, 1920, 72); c.clip();
  for (let s = 0; s < sub; s++) {
    const fs = dialFreq(u - s * .008); c.globalAlpha = 1 / sub;
    const f0 = Math.floor((fs - NX / PPM) * 10) / 10;
    for (let k = 0; k < 125; k++) {
      const fr = Math.round((f0 + k * .1) * 10) / 10, x = NX + (fr - fs) * PPM; if (x > 1940) break;
      const major = Math.abs(fr - Math.round(fr)) < .01, mid = !major && Math.abs(fr * 2 - Math.round(fr * 2)) < .01;
      const h = major ? 30 : mid ? 20 : 11, w = major ? 2.6 : 1.4;
      c.fillStyle = 'rgba(0,0,0,.55)'; c.fillRect(x - w / 2 - 1, 19, w, h);          // engraved shadow
      c.fillStyle = `rgba(245,238,220,${major ? .95 : .62})`; c.fillRect(x - w / 2, 20, w, h);
      if (major) { c.font = `600 21px ${FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle';
        c.fillStyle = 'rgba(0,0,0,.6)'; c.fillText(String(Math.round(fr)), x - 1, 67); c.fillStyle = 'rgba(245,238,220,.92)'; c.fillText(String(Math.round(fr)), x, 68); }
    }
  }
  c.restore(); c.globalAlpha = 1;
  // indicator
  const lock = seg(u, 1.25, 1.5);
  c.save(); c.shadowColor = 'rgba(255,170,90,.95)'; c.shadowBlur = 16 + 16 * Math.exp(-Math.pow((u - 1.35) / .15, 2));
  c.fillStyle = '#FFE2B4'; c.fillRect(NX - 1.6, 8, 3.2, 80); c.restore();
  c.beginPath(); c.moveTo(NX - 9, 6); c.lineTo(NX + 9, 6); c.lineTo(NX, 18); c.closePath(); c.fillStyle = '#FFE2B4'; c.fill();
  // TEXT LAYERS — the frequency is the largest element
  const fa = seg(u, .75, 1.2), fsz = .82 + .18 * eBack(seg(u, .75, 1.45));
  if (fa > 0) {
    c.save(); c.translate(NX, 150); c.scale(fsz, fsz); c.translate(-NX, -150);
    const shown = u < 1.42 ? f.toFixed(1) : COPY.s1freq;
    c.save(); c.globalAlpha = fa; c.font = `800 112px ${FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle';
    c.shadowColor = `rgba(255,180,100,${.35 + .4 * Math.exp(-Math.pow((u - 1.4) / .2, 2))})`; c.shadowBlur = 26; c.fillStyle = IVORY; c.fillText(shown, NX, 152); c.restore();
    ivoryText(c, COPY.s1fm, L.xM, 172, `700 40px ${FONT}`, seg(u, 1.35, 1.7));
    c.restore();
  }
  wipeText(c, COPY.s1, L.xA, 152, `600 48px ${FONT}`, seg(u, 1.5, 2.3));
  ivoryText(c, COPY.s1dash, L.xD, 150, `500 48px ${FONT}`, seg(u, 2.15, 2.5) * .8);
  glassSheen(c, t); vignette(c, .45);
}

// ═════════════════════════ SCENE 2 — the phone ═════════════════════════
function glyph(c, k, s) {
  c.save(); c.strokeStyle = IVORY; c.fillStyle = IVORY; c.lineWidth = s * .09; c.lineJoin = 'round';
  if (k === 0) { c.font = `800 ${s * 1.1}px ${FONT}`; c.textAlign = 'center'; c.textBaseline = 'middle'; c.fillText('f', 0, s * .06); }
  if (k === 1) { rr(c, -s / 2, -s / 2, s, s, s * .28); c.stroke(); c.beginPath(); c.arc(0, 0, s * .22, 0, 7); c.stroke(); c.beginPath(); c.arc(s * .26, -s * .26, s * .06, 0, 7); c.fill(); }
  if (k === 2) { rr(c, -s * .66, -s * .44, s * 1.32, s * .88, s * .26); c.stroke(); c.beginPath(); c.moveTo(-s * .14, -s * .2); c.lineTo(s * .22, 0); c.lineTo(-s * .14, s * .2); c.closePath(); c.fill(); }
  c.restore();
}
function scenePhone(c, u, t, A) {
  // the river first; the phone glides in over it and the reflection continues inside its glass
  water(c, A, t, 0, 0, 1920, BH, 46, 0, 1);
  const dim = seg(u, .9, 2.0); c.fillStyle = `rgba(2,22,27,${.72 * dim})`; c.fillRect(0, 0, 1920, BH);
  const px = 70 + (1 - eIO(seg(u, 0, 1.5))) * 2000, top = 14;
  // body + metal frame
  c.save();
  c.shadowColor = 'rgba(0,0,0,.6)'; c.shadowBlur = 30; c.shadowOffsetY = 10;
  rr(c, px, top, 2600, 420, 78); c.fillStyle = '#0A1417'; c.fill(); c.shadowColor = 'transparent';
  const fg = c.createLinearGradient(0, top, 0, top + 16); fg.addColorStop(0, '#F3EEE2'); fg.addColorStop(.35, '#9FB9BC'); fg.addColorStop(.7, '#3F7E87'); fg.addColorStop(1, '#14454C');
  rr(c, px + 3, top + 3, 2594, 414, 75); c.strokeStyle = fg; c.lineWidth = 6; c.stroke();
  // moving highlight on the frame edge
  const hx = px + ((t * 180) % 2400); const hgr = c.createLinearGradient(hx - 120, 0, hx + 120, 0); hgr.addColorStop(0, 'rgba(255,255,255,0)'); hgr.addColorStop(.5, 'rgba(255,244,220,.9)'); hgr.addColorStop(1, 'rgba(255,255,255,0)');
  c.fillStyle = hgr; c.fillRect(hx - 120, top + 1, 240, 3);
  // screen
  const sx = px + 20, sy = top + 20;
  rr(c, sx, sy, 2560, 380, 60); c.clip();
  const sg = c.createLinearGradient(0, sy, 0, BH); sg.addColorStop(0, '#0B5661'); sg.addColorStop(1, '#042F36'); c.fillStyle = sg; c.fillRect(sx, sy, 2560, 380);
  const refl = 1 - .85 * seg(u, 1.0, 2.1);
  c.globalAlpha = refl; water(c, A, t, sx, sy, 1920, BH, 46, 0, 1); c.globalAlpha = 1;
  c.fillStyle = `rgba(4,40,47,${.55 * seg(u, 1.0, 2.1)})`; c.fillRect(sx, sy, 2560, 380);
  // front camera
  c.beginPath(); c.arc(sx + 46, 108, 10, 0, 7); c.fillStyle = '#020809'; c.fill(); c.beginPath(); c.arc(sx + 46, 108, 10, 0, 7); c.strokeStyle = 'rgba(160,200,205,.35)'; c.lineWidth = 1.5; c.stroke();
  c.beginPath(); c.arc(sx + 43, 105, 2.5, 0, 7); c.fillStyle = 'rgba(190,230,235,.6)'; c.fill();
  // UI: the three icons arrive together
  const ip = seg(u, 1.25, 1.75), GX = 430;
  for (let k = 0; k < 3; k++) {
    const cx = GX + 56 + k * 128, cy = 112, s = .7 + .3 * eBack(ip);
    if (ip <= 0) break;
    c.save(); c.globalAlpha = clamp(ip * 2); c.translate(cx, cy); c.scale(s, s);
    c.shadowColor = 'rgba(0,0,0,.45)'; c.shadowBlur = 14; c.shadowOffsetY = 5;
    rr(c, -52, -52, 104, 104, 26); const tg = c.createLinearGradient(0, -52, 0, 52); tg.addColorStop(0, '#128595'); tg.addColorStop(1, TEAL); c.fillStyle = tg; c.fill(); c.shadowColor = 'transparent';
    const hl = c.createLinearGradient(0, -52, 0, 0); hl.addColorStop(0, 'rgba(255,255,255,.22)'); hl.addColorStop(1, 'rgba(255,255,255,0)'); c.fillStyle = hl; c.fill();
    c.strokeStyle = 'rgba(245,238,220,.45)'; c.lineWidth = 1.2; c.stroke();
    glyph(c, k, 44); c.restore();
  }
  // TEXT LAYERS
  const TX = GX + 3 * 128 + 44;
  wipeText(c, COPY.s2, TX, 66, `600 42px ${FONT}`, seg(u, 1.55, 2.2));
  const fp = seg(u, 1.9, 2.7);
  if (fp > 0) { c.save(); c.filter = `blur(${(1 - eOut(fp)) * 18}px)`; c.globalAlpha = clamp(fp * 1.6);
    c.font = `800 86px ${FONT}`; c.textBaseline = 'middle'; c.shadowColor = 'rgba(0,0,0,.5)'; c.shadowBlur = 10; c.fillStyle = IVORY; c.fillText(COPY.s2url, TX - 3, 148); c.restore();
    c.font = `800 86px ${FONT}`; const uw = c.measureText(COPY.s2url).width;
    c.fillStyle = WARM; c.globalAlpha = .9; c.fillRect(TX, 194, uw * eOut(seg(u, 2.5, 3.1)), 3); c.globalAlpha = 1; }
  glassSheen(c, t, 1.3);
  c.restore();
  vignette(c, .4);
}

// ═════════════════════════ SCENE 3 — the saz string ═════════════════════════
const STRINGS = [[34, 2.6], [43, 2.6], [LY, 5.6], [78, 3.4], [91, 3.0]];   // [y, thickness] — LY is the plucked, wound string
function sceneSaz(c, u, t, A) {
  const drift = t * 9;
  // deep teal lacquer surface, shallow depth of field
  tile(c, A.metal, drift, 0, BH);
  c.fillStyle = 'rgba(2,30,36,.62)'; c.fillRect(0, 0, 1920, BH);
  const kl = c.createRadialGradient(520, -40, 20, 520, -40, 1100); kl.addColorStop(0, 'rgba(255,206,150,.26)'); kl.addColorStop(.5, 'rgba(120,200,205,.08)'); kl.addColorStop(1, 'rgba(0,0,0,0)');
  c.save(); c.globalCompositeOperation = 'lighter'; c.fillStyle = kl; c.fillRect(0, 0, 1920, BH);
  for (let k = 0; k < 14; k++) { // out-of-focus points of light drifting behind the strings
    const h1 = hash(k, 1), h2 = hash(k, 2), h3 = hash(k, 3), per = 2300;
    const x = (((h1 * per - t * (10 + h3 * 16)) % per) + per) % per - 190, y = 20 + h2 * 190, r = 22 + h3 * 34;
    const g = c.createRadialGradient(x, y, r * .55, x, y, r); const col = k % 3 === 0 ? '255,214,160' : '150,215,220';
    g.addColorStop(0, `rgba(${col},${.10 + .05 * Math.sin(t * 1.3 + k)})`); g.addColorStop(.85, `rgba(${col},${.13 + .05 * Math.sin(t * 1.3 + k)})`); g.addColorStop(1, `rgba(${col},0)`);
    c.fillStyle = g; c.fillRect(x - r, y - r, r * 2, r * 2);
  }
  c.restore();
  const sh = c.createLinearGradient(0, 96, 0, BH); sh.addColorStop(0, 'rgba(2,20,24,0)'); sh.addColorStop(1, 'rgba(2,20,24,.6)'); c.fillStyle = sh; c.fillRect(0, 96, 1920, BH - 96);
  // travelling light in the flag colours (the national transition)
  c.save(); c.globalCompositeOperation = 'lighter';
  FLAGC.forEach((col, k) => {
    const p = seg(u, 1.1 + k * .32, 2.9 + k * .32); if (p <= 0 || p >= 1) return;
    const x = -420 + 2760 * p, g = c.createRadialGradient(x, 70, 0, x, 70, 420); g.addColorStop(0, col); g.addColorStop(1, 'rgba(0,0,0,0)');
    c.globalAlpha = .62 * Math.sin(Math.PI * p); c.save(); c.scale(1, .62); c.fillStyle = g; c.fillRect(x - 420, -200, 840, 760); c.restore();
  });
  c.restore();
  // strings: shadow, steel body, specular; the matched string is plucked and rings out
  const amp = 11 * eOut(seg(u, .55, .8)) * Math.exp(-Math.max(0, u - .8) * .95);
  STRINGS.forEach(([y, w], i) => {
    const main = y === LY, a = main ? amp : amp * (.12 + .1 * hash(i));
    const shape = (ph) => { c.beginPath(); for (let x = -10; x <= 1930; x += 12) { const env = Math.sin(Math.PI * clamp((x + 300) / 2500)); const yy = y + Math.sin(ph) * a * env * (.92 + .08 * Math.sin(t * 5 + i)) + Math.sin(x / 120 - t * 6 + i) * a * .05; x < 0 ? c.moveTo(x, yy) : c.lineTo(x, yy); } };
    c.save(); c.filter = 'blur(3px)'; c.globalAlpha = .5; c.translate(10, 14); shape(0); c.strokeStyle = '#000'; c.lineWidth = w * 1.7; c.stroke(); c.restore();
    const n = a > .25 ? 9 : 1; // vibration fan = optical motion blur of a ringing string
    for (let k = 0; k < n; k++) {
      const ph = n === 1 ? Math.PI / 2 * 0 : (k / (n - 1)) * Math.PI - Math.PI / 2;   // fixed fan = the blurred spindle of a ringing string
      c.globalAlpha = n === 1 ? 1 : .3;
      shape(ph); c.strokeStyle = main ? '#5E7C80' : '#3D5F64'; c.lineWidth = w; c.stroke();
      shape(ph); c.strokeStyle = main ? '#E6DCC4' : '#A9CDD0'; c.lineWidth = w * .62; c.stroke();
      c.save(); c.translate(0, -w * .22); shape(ph); c.strokeStyle = main ? '#FFE9C2' : '#FFFFFF'; c.lineWidth = Math.max(.8, w * .24); c.stroke(); c.restore();
    }
    c.globalAlpha = 1;
    if (main && a < 1.2) { shape(0); c.setLineDash([1.8, 2.6]); c.lineDashOffset = -drift; c.strokeStyle = 'rgba(255,236,200,.55)'; c.lineWidth = w * .72; c.stroke(); c.setLineDash([]); }
  });
  // one string very close to the lens, far out of focus
  c.save(); c.filter = 'blur(7px)'; c.globalAlpha = .55; c.fillStyle = '#CFE6E6'; c.fillRect(-20, 8, 1960, 9 + amp * .3); c.restore();
  // TEXT LAYER on a stable plate
  const pa = eOut(seg(u, .7, 1.3));
  plate(c, 330, 114, 1260, 86, 18, pa);
  wipeText(c, COPY.s3, 960, 158, `600 50px ${FONT}`, seg(u, .95, 1.8), 'center');
  vignette(c, .55);
}

// ═════════════════════════ SCENE 4 — the bridge, the two shores, the lockup ═════════════════════════
function sceneBridge(c, u, t, A) {
  const z = 1 + 1.15 * (1 - eIO(seg(u, -.4, 2.3)));    // pull back
  c.save(); c.translate(960, LY); c.scale(z, z); c.translate(-960, -LY);
  // land (both shores)
  c.save(); c.translate(0, -108); tile(c, A.land, 120, 0, 432); c.restore();
  c.fillStyle = 'rgba(2,24,29,.42)'; c.fillRect(-400, -200, 2800, 700);
  // river running between the shores
  const bankL = y => 700 + Math.sin(y / 70 + 1) * 26 + Math.sin(y / 23) * 6, bankR = y => 1220 + Math.sin(y / 60 + 2.4) * 30 + Math.sin(y / 19 + 1) * 6;
  const riverPath = (pad = 0) => { c.beginPath(); for (let y = -140; y <= 360; y += 10) { const x = bankL(y) - pad; y === -140 ? c.moveTo(x, y) : c.lineTo(x, y); } for (let y = 360; y >= -140; y -= 10) c.lineTo(bankR(y) + pad, y); c.closePath(); };
  riverPath(20); c.fillStyle = 'rgba(214,204,170,.42)'; c.fill();                 // sand bars
  riverPath(6); c.fillStyle = 'rgba(245,238,220,.85)'; c.fill();                   // shoreline foam
  c.save(); riverPath(0); c.clip();
  c.save(); c.translate(0, -140); water(c, A, t, 0, 0, 1920, 520, 4, 55, 1); c.fillStyle = 'rgba(40,150,165,.22)'; c.fillRect(0, 0, 1920, 520); c.restore();
  const dp = c.createLinearGradient(700, 0, 1220, 0); dp.addColorStop(0, 'rgba(2,24,30,.45)'); dp.addColorStop(.2, 'rgba(2,24,30,0)'); dp.addColorStop(.8, 'rgba(2,24,30,0)'); dp.addColorStop(1, 'rgba(2,24,30,.45)'); c.fillStyle = dp; c.fillRect(600, -140, 720, 520);
  // warm sun glint on the water
  const sgx = 960 + Math.sin(t * .6) * 30, sg = c.createRadialGradient(sgx, 120, 0, sgx, 120, 200); sg.addColorStop(0, 'rgba(255,206,140,.35)'); sg.addColorStop(1, 'rgba(255,206,140,0)');
  c.globalCompositeOperation = 'lighter'; c.fillStyle = sg; c.fillRect(sgx - 200, -80, 400, 400); c.globalCompositeOperation = 'source-over';
  c.restore();
  // roads continuing on both shores, then the bridge (the saz string's line)
  c.fillStyle = 'rgba(245,238,220,.55)'; c.fillRect(-200, LY - 2, 2400, 4);
  c.save(); c.shadowColor = 'rgba(0,0,0,.55)'; c.shadowBlur = 8; c.shadowOffsetX = 7; c.shadowOffsetY = 10;
  c.fillStyle = IVORY; c.fillRect(676, LY - 5, 568, 10); c.restore();
  c.fillStyle = 'rgba(9,93,106,.9)'; for (let x = 690; x < 1240; x += 22) c.fillRect(x, LY - .8, 11, 1.6);   // lane marks
  for (let x = 760; x <= 1160; x += 100) { c.fillStyle = 'rgba(0,0,0,.35)'; c.fillRect(x - 4 + 7, LY - 12 + 10, 10, 24); c.fillStyle = '#D9D2BE'; c.fillRect(x - 5, LY - 12, 10, 24); } // piers
  c.fillStyle = IVORY; c.fillRect(676, LY - 5, 568, 10);
  c.restore();
  const sh = c.createLinearGradient(0, 96, 0, BH); sh.addColorStop(0, 'rgba(2,22,27,0)'); sh.addColorStop(1, 'rgba(2,22,27,.5)'); c.fillStyle = sh; c.fillRect(0, 96, 1920, BH - 96);
  // LOCKUP: official logo | fine divider | closing line
  const la = eOut(seg(u, 1.7, 2.3));
  if (la > 0) {
    const img = A.logoWhite, lh = 62, lw = img.width * lh / img.height;
    c.font = `600 44px ${FONT}`; const tw = c.measureText(COPY.s4).width, gap = 30, W = lw + gap * 2 + tw, x0 = 960 - W / 2, cy = 158;
    plate(c, x0 - 44, 114, W + 88, 88, 18, la);
    c.save(); c.globalAlpha = la; c.drawImage(img, x0 - (1 - la) * 20, cy - lh / 2, lw, lh);
    const dh = 56 * eOut(seg(u, 2.0, 2.5)); c.fillStyle = 'rgba(245,238,220,.8)'; c.fillRect(x0 + lw + gap - .75, cy - dh / 2, 1.5, dh); c.restore();
    wipeText(c, COPY.s4, x0 + lw + gap * 2, cy + 1, `600 44px ${FONT}`, seg(u, 2.15, 2.9));
  }
  vignette(c, .5);
}

// ═════════════════════════ DIRECTOR: timeline, matched transitions ═════════════════════════
window.renderFilm = function (ctx, tAbs, A) {
  if (!SC) { SC = [0, 1, 2, 3].map(() => mk(1920, BH)); TMP = mk(1920, 432); TMP2 = mk(1920, BH); }
  const t = ((tAbs % DUR) + DUR) % DUR;
  const scenes = [sceneDial, scenePhone, sceneSaz, sceneBridge];
  const draw = (i, u, tt = tAbs) => { const c = SC[i].getContext('2d'); c.setTransform(1, 0, 0, 1, 0, 0); c.globalAlpha = 1; c.globalCompositeOperation = 'source-over'; c.filter = 'none'; c.clearRect(0, 0, 1920, BH); c.save(); scenes[i](c, u, tt, A); c.restore(); };
  let i = 0; for (let k = 0; k < 4; k++) if (t >= T[k]) i = k;
  const u = t - T[i], FADE = [0, 0, .9, .9][i];
  ctx.save(); ctx.beginPath(); ctx.rect(0, BY, 1920, BH); ctx.clip();
  // outgoing scene underneath while the new one arrives
  const prev = (i + 3) % 4, a = FADE ? eIO(seg(u, 0, FADE)) : 1;
  if (a < 1) { draw(prev, t - T[prev] + (i === 0 ? DUR : 0)); ctx.drawImage(SC[prev], 0, BY); }
  if (i === 0 && t < .9) { draw(3, DUR - T[3] + t, tAbs + DUR); ctx.drawImage(SC[3], 0, BY); }
  draw(i, u);
  ctx.globalAlpha = i === 0 ? eIO(seg(t, 0, .9)) : a; ctx.drawImage(SC[i], 0, BY); ctx.globalAlpha = 1;

  // 1 → 2 : a glint in the dial glass opens into the river
  const g12 = seg(t, T[1] - 1.0, T[1]);
  if (g12 > 0 && g12 < 1) {
    const w = TMP2; // river grows out of the glint
    const gx = 1180, r = 20 + 2300 * eIO(g12);
    ctx.save(); ctx.beginPath(); ctx.ellipse(gx, BY + 40, r, r * .5, 0, 0, 7); ctx.clip(); ctx.translate(0, BY); water(ctx, A, tAbs, 0, 0, 1920, BH, 46, 0, 1); vignette(ctx, .4); ctx.restore();
  }
  const gl = Math.exp(-Math.pow((t - (T[1] - .95)) / .28, 2));
  if (gl > .01) { const g = ctx.createRadialGradient(1180, BY + 40, 0, 1180, BY + 40, 260); g.addColorStop(0, `rgba(255,236,200,${.95 * gl})`); g.addColorStop(1, 'rgba(255,236,200,0)'); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.fillRect(900, BY, 560, BH); ctx.globalCompositeOperation = 'source-over'; }

  // 2 → 3 → 4 : one thin line of light — highlight on the phone glass → saz string → bridge
  const lineA = Math.max(seg(t, T[2] - .9, T[2] - .3) * (1 - seg(t, T[2] + .35, T[2] + .8)), seg(t, T[3] - .5, T[3] - .1) * (1 - seg(t, T[3] + .45, T[3] + .9)));
  if (lineA > 0) {
    const grow = t < T[2] + 1 ? eOut5(seg(t, T[2] - .9, T[2] - .2)) : 1, half = 1000 * grow;
    const thick = t > T[3] - .6 ? 3 + 7 * eIO(seg(t, T[3] - .2, T[3] + .6)) : 3;
    ctx.save(); ctx.globalAlpha = lineA; ctx.shadowColor = 'rgba(255,214,160,.9)'; ctx.shadowBlur = 14;
    const lg = ctx.createLinearGradient(960 - half, 0, 960 + half, 0); lg.addColorStop(0, 'rgba(255,240,214,0)'); lg.addColorStop(.12, 'rgba(255,240,214,1)'); lg.addColorStop(.88, 'rgba(255,240,214,1)'); lg.addColorStop(1, 'rgba(255,240,214,0)');
    ctx.fillStyle = lg; ctx.fillRect(960 - half, BY + LY - thick / 2, half * 2, thick); ctx.restore();
  }
  // 4 → 1 : sun glint on the river folds back into the dial glass (loop)
  const g41 = Math.exp(-Math.pow((t < 2 ? t + DUR - (DUR - .1) : t - (DUR - .1)) / .3, 2));
  if (g41 > .01) { const g = ctx.createRadialGradient(960, BY + 100, 0, 960, BY + 100, 520); g.addColorStop(0, `rgba(255,232,196,${.7 * g41})`); g.addColorStop(1, 'rgba(255,232,196,0)'); ctx.globalCompositeOperation = 'lighter'; ctx.fillStyle = g; ctx.fillRect(400, BY, 1120, BH); ctx.globalCompositeOperation = 'source-over'; }

  // band edge: fine ivory hairline, soft contact shadow onto the picture above
  ctx.restore();
  const es = ctx.createLinearGradient(0, BY - 22, 0, BY); es.addColorStop(0, 'rgba(0,0,0,0)'); es.addColorStop(1, 'rgba(0,0,0,.30)'); ctx.fillStyle = es; ctx.fillRect(0, BY - 22, 1920, 22);
  ctx.fillStyle = 'rgba(245,238,220,.85)'; ctx.fillRect(0, BY, 1920, 1.5);
};
