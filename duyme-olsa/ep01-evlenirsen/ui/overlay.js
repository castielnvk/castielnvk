// Düymə olsa — UI timeline. window.EPISODE (episode.json) is injected by compose.js.
// window.setT(seconds) poses the interface deterministically for one frame.
(function () {
  const E = window.EPISODE, U = E.ui;
  const $ = id => document.getElementById(id);
  const get = p => p.split('.').reduce((o, k) => o[k], U);
  document.querySelectorAll('[data-text]').forEach(el => { el.textContent = get(el.dataset.text); });
  document.querySelectorAll('[data-initial]').forEach(el => { el.textContent = get(el.dataset.initial).charAt(0); });

  const cl = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const seg = (t, [a, b]) => cl((t - a) / (b - a));
  const eo = x => 1 - Math.pow(1 - x, 3);
  const eio = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
  const back = x => { const c = 1.6; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); };
  const lerp = (a, b, p) => a + (b - a) * p;

  const H = E.height, L = U.card_left, W = U.card_width, B = U.stack_bottom, GAP = 22;
  const ask = $('ask'), askC = $('askContent'), bw = $('buttonsWrap'), pill = $('pillContent');
  const group = $('group'), gC = $('groupContent'), follow = $('follow'), tap = $('tap'), bp = $('btnPrimary');

  // ── measure layout once ──
  ask.style.left = L + 'px'; ask.style.width = W + 'px'; ask.style.bottom = (H - B) + 'px';
  const askFull = askC.offsetHeight;
  bw.style.display = 'none'; const askShort = askC.offsetHeight; bw.style.display = '';
  const pillW = Math.ceil(pill.offsetWidth) + 2, pillH = pill.offsetHeight;
  pill.style.width = pillW + 'px';
  group.style.left = L + 'px'; group.style.width = W + 'px';
  group.style.bottom = (H - B + pillH + GAP) + 'px';
  const gFull = gC.offsetHeight;
  follow.style.display = 'none'; const gShort = gC.offsetHeight; follow.style.display = '';
  const pillLeft = L + (W - pillW) / 2;
  // primary button centre (for the tap marker), measured with buttons shown
  ask.style.height = askFull + 'px';
  const r = bp.getBoundingClientRect();
  const tapX = r.left + r.width * 0.56, tapY = r.top + r.height / 2;

  window.setBg = src => new Promise(res => { const im = $('bg'); im.onload = () => im.decode().then(res, res); im.src = src; });

  window.setT = function (t) {
    // 2D camera push over the whole scene
    const push = (E.composite && E.composite.push) || 0.045;
    $('bg').style.transform = `scale(${1 + push * eio(cl(t / U.end_card))})`;

    // ── card 1: settle ──
    const s = eo(seg(t, U.ask.settle));
    // buttons reveal grows the card upward from its fixed bottom
    const rv = eo(seg(t, U.buttons.reveal));
    let h = lerp(askShort, askFull, rv);
    bw.style.opacity = rv; bw.style.transform = `translateY(${(1 - rv) * 24}px)`;

    // press: compress, release with a small overshoot
    const P = U.buttons.press, d = U.buttons.press_down, u = U.buttons.press_up;
    let sc = 1, pressed = false;
    if (t >= P && t < P + d) { sc = lerp(1, .92, eio((t - P) / d)); pressed = true; }
    else if (t >= P + d && t < P + d + u) { const q = (t - P - d) / u; sc = q < .6 ? lerp(.92, 1.03, eo(q / .6)) : lerp(1.03, 1, eio((q - .6) / .4)); }
    bp.style.transform = `scale(${sc})`; bp.classList.toggle('pressed', pressed);
    // tap marker (the viewer's finger)
    const tq = cl((t - (P - .06)) / .45);
    tap.style.left = tapX + 'px'; tap.style.top = tapY + 'px';
    tap.style.opacity = tq <= 0 || tq >= 1 ? 0 : (tq < .2 ? tq / .2 : 1 - (tq - .2) / .8) * .9;
    tap.style.transform = `scale(${lerp(1.25, .75, eo(cl(tq / .3))) + (tq > .3 ? (tq - .3) * .9 : 0)})`;

    // collapse into the muted pill
    const c = eio(seg(t, U.muted.collapse));
    const left = lerp(L, pillLeft, c), width = lerp(W, pillW, c);
    h = lerp(h, pillH, c);
    ask.style.left = left + 'px'; ask.style.width = width + 'px'; ask.style.height = h + 'px';
    ask.style.borderRadius = lerp(46, pillH / 2, c) + 'px';
    askC.style.opacity = 1 - cl(c / .45);
    askC.style.transform = `scale(${lerp(1, .9, c)})`; askC.style.transformOrigin = '50% 100%';
    pill.style.opacity = cl((c - .45) / .45);
    // when Ana's message lands, the 'muted' pill gives a tiny ironic wobble
    const wq = seg(t, [U.group.slide_in[1] - .05, U.group.slide_in[1] + .55]);
    const wob = wq > 0 && wq < 1 ? Math.sin(wq * Math.PI * 5) * (1 - wq) * 2.2 : 0;
    ask.style.transform = `translateY(${(1 - s) * -34}px) rotate(${wob}deg) scale(${lerp(.975, 1, s) * (c > 0 && c < 1 ? lerp(1, .985, Math.sin(c * Math.PI)) : 1)})`;

    // ── card 2: group chat slides in above the pill, then grows upward for the follow-up ──
    const g = seg(t, U.group.slide_in), gi = eo(g);
    group.style.opacity = cl(g * 2.2);
    group.style.transform = `translateY(${(1 - gi) * -70}px) scale(${lerp(.96, 1, back(g))})`;
    group.style.visibility = g > 0 ? 'visible' : 'hidden';
    const f = seg(t, U.group.followup_in);
    group.style.height = lerp(gShort, gFull, eio(f)) + 'px';
    follow.style.opacity = cl((f - .25) / .75);
    follow.style.transform = `translateY(${(1 - eo(f)) * 18}px)`;
  };
  window.setT(0);
  window.UI_READY = true;
})();
