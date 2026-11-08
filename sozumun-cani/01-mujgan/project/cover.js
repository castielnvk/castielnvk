window.cover = function () {
  const c = X; c.save();
  bg(c, 'night', 0, { gy: 860, gr: 950 }); dust(c, 3.2, { a: 0.55 });
  // logo + series title
  const ar = LOGO.naturalHeight / LOGO.naturalWidth, lw = 230, lh = lw * ar;
  c.drawImage(LOGO, CX - lw / 2, 345, lw, lh);
  T(c, 'SÖZÜMÜN CANI', CX, 345 + lh + 62, { ff: 'CSC', wt: 500, sz: 40, ls: 13, col: GOLD_L, glow: 10 });
  // the eye: lashes, two of them already turning into arrows
  glow0(c, CX, 820);
  const an = eye(c, CX, 830, { w: 660, h: 78, open: 0.8, lw: 3.2, col: GOLD_L, glow: 16, iris: 0.95, lashes: 19, lashLen: 92, lashW: 3.4, skip: k => k === 13 || k === 15 });
  [[13, 120], [15, 190]].forEach(([k, d]) => { const A = an[k]; arrow(c, A.x + Math.cos(A.ang) * (A.len + d), A.y + Math.sin(A.ang) * (A.len + d), A.ang, 110, { hs: 14, w: 2.4, glow: 12 }); });
  // the word
  T(c, 'MÜJGAN', CX, 1170, { wt: 500, sz: 210, ls: 14, col: gradGold(c, 1020, 1175), glow: 26 });
  T(c, 'aşiqin qəlbinə sancılan ox', CX, 1275, { it: true, wt: 300, sz: 54, col: CREAM, a: 0.92 });
  finish(c, 0, 5); c.restore();
};
function glow0(c, x, y) { const g = c.createRadialGradient(x, y, 0, x, y, 520); g.addColorStop(0, 'rgba(214,176,108,0.16)'); g.addColorStop(1, 'rgba(0,0,0,0)'); c.fillStyle = g; c.fillRect(0, 0, W, H); }
