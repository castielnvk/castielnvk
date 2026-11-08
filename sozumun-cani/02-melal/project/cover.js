window.cover = function () {
  const c = X; c.save();
  sky(c, { gy: 980, gr: 950 }); motes(c, 2, 0.4);
  const ar = LOGO.naturalHeight / LOGO.naturalWidth, lw = 230, lh = lw * ar;
  c.drawImage(LOGO, CX - lw / 2, 345, lw, lh);
  T(c, 'SÖZÜMÜN CANI', CX, 345 + lh + 60, { ff: IN, wt: 500, sz: 30, ls: 12, col: MIST });
  const wy = 960, water = 1000;
  AC.clearRect(0, 0, W, H);
  glow(AC, CX, 760, 60, '255,228,190', 0.9); glow(AC, CX, 760, 340, '231,169,100', 0.22);   // the single ember
  T(AC, 'MƏLAL', CX, wy, { ff: PF, wt: 600, sz: 250, ls: 22, col: silverGrad(AC, wy - 190, wy), glow: 18, glowCol: 'rgba(200,220,240,0.35)' });
  c.drawImage(above, 0, 0);
  waterLine(c, water, 900, 1); reflect(c, above, water, 1.3, { a: 0.38, h: 420 });
  rainRings(c, 1.7, water, 0.8, 300); rain(c, 0.9, 0.8, water);
  T(c, 'kədər · sıxıntı · qəlb yorğunluğu', CX, 1450, { ff: LO, it: true, sz: 46, col: AMBER_L, a: 0.95 });
  finish(c, 0, 5); c.restore();
};
