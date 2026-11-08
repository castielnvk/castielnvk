window.cover = function () {
  const c = X; c.save();
  dawn(c, { warm: 0.6, gy: 960, gr: 1000 }); specks(c, 3, 0.45);
  const ar = LOGO.naturalHeight / LOGO.naturalWidth, lw = 230, lh = lw * ar;
  c.drawImage(LOGO, CX - lw / 2, 345, lw, lh);
  T(c, 'SÖZÜMÜN CANI', CX, 345 + lh + 62, { ff: IN, wt: 500, sz: 30, ls: 12, col: GOLD_L });
  // the word sits on a smiling curve
  const base = 1010, P0 = [CX - 450, base - 60], P1 = [CX, base + 90], P2 = [CX + 450, base - 60];
  glw(c, CX, 960, 520, '255,214,165', 0.22);
  fineLine(c, CX, base + 25, 900, 75, { lw: 3, col: PEACH, glow: 12, lift: 60 });
  const word = 'ZƏNƏXDAN'; c.save(); font(c, { ff: FR, wt: 600, sz: 128, ls: 6 }); const total = c.measureText(word).width; c.restore();
  let acc = 0;
  [...word].forEach(ch => { c.save(); font(c, { ff: FR, wt: 600, sz: 128, ls: 6 }); const cw = c.measureText(ch).width; c.restore();
    const u = (acc + cw / 2) / total * 0.86 + 0.07; acc += cw; const q = qpt(P0, P1, P2, u), tg = qtan(P0, P1, P2, u);
    c.save(); c.translate(q[0], q[1] - 14); c.rotate(Math.atan2(tg[1], tg[0])); T(c, ch, 0, 0, { ff: FR, wt: 600, sz: 128, col: warmGrad(c, -110, 0), glow: 16, glowCol: 'rgba(243,190,150,0.5)' }); c.restore(); });
  T(c, 'güləndə üzdə yaranan o incə cizgi', CX, 1300, { ff: FR, it: true, wt: 300, sz: 50, col: CREAM, a: 0.95 });
  finish(c, 0, 5); c.restore();
};
