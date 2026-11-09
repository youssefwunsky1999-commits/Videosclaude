// arcoiris.js: «El arcoíris», 7 s for the TikTok about the four tools. Clawd, holding a brush, conducts a rainbow
// into the sky stroke by stroke, takes it in (proud), bounces with joy and waves to camera. Cheap paint (washes and a
// few fills) so it renders in software GL. The action stays in the centre 1080 px: the video crops it to a square.
(() => {
  const G = 860, X = 960, U = 30;
  const BANDS = ['#E0645A', '#F0A848', '#F2D35E', '#7DBE7A', '#5B9BD5', '#8A6CC8'];
  const tPaint0 = 1.0, tPaint1 = 3.0, tProud = 3.25, tJoy = 4.1, tWave = 5.6;

  function backdrop(t) {
    boilSeed('sky');
    paint(rectPts(-300, -300, W + 600, G + 300), { wash: '#CFE3EE', ink: null });
    paint(ellPts(W / 2, G - 40, 900, 420, 30, 10), { fill: '#F6E7C8', fillOp: 120, bleed: .25, tex: .5, ink: null });
    for (let i = 0; i < 3; i++) {   // three slow clouds
      boilSeed('cloud' + i);
      const cx = 380 + i * 600 + 30 * Math.sin(t * .4 + i), cy = 170 + 60 * hash(i + 7);
      paint(ellPts(cx, cy, 120 + 40 * hash(i), 44, 18, 4), { wash: PAL.cream, washOp: 235, ink: PAL.ink, sw: .5 });
    }
    boilSeed('ground');
    paint(rectPts(-300, G - 10, W + 600, 500, 3), { wash: '#9CC58A', ink: null });
    inkLine([[-200, G - 8], [W / 2, G - 14], [W + 200, G - 6]], 1, PAL.ink, 'ink', .5);
  }

  // the rainbow: each band grows from left to right along a half circle while Clawd conducts
  function rainbow(t) {
    const k = ease(seg(t, tPaint0, tPaint1));
    if (k <= 0) return null;
    let tip = null;
    BANDS.forEach((c, i) => {
      const kb = clamp((k - i * .05) / (1 - .05 * (BANDS.length - 1)));
      if (kb <= 0) return;
      const r = 470 - i * 34, P = [];
      const n = Math.max(2, Math.round(28 * kb));
      for (let j = 0; j <= n; j++) { const a = Math.PI - Math.PI * kb * j / n; P.push([X + Math.cos(a) * r, G - 40 - Math.sin(a) * r * .92]); }
      boilSeed('band' + i);
      paint(ribbon(P, 32, 32), { wash: c, ink: PAL.ink, sw: .5 });
      if (i === 0) tip = P[P.length - 1];
    });
    return tip;
  }
  const sparkle = (x, y, r, k) => { if (k > 0 && k < 1) paint(starPts(x, y, r * backOut(k) * (1 - k * .6), .25, 4, k * 2), { wash: PAL.cream, washOp: 255 * (1 - k * k), ink: null }); };

  function shot(t) {
    camBegin(960 + 10 * Math.sin(t * .7), kf(t, [[0, 560], [3, 520], [7, 560]]), kf(t, [[0, 1.08], [3.1, 1.0], [4.2, 1.06], [7, 1.12]]));
    backdrop(t);
    const tip = rainbow(t);
    boilSeed('fx');
    if (tip && t < tPaint1 + .1) { glow(tip[0], tip[1], 70, '#FFE9A8', .7); for (let i = 0; i < 3; i++) sparkle(tip[0] + 30 * Math.sin(t * 9 + i * 2), tip[1] - 20 * i, 22, frac(t * 2.5 + i / 3)); }
    if (t > tPaint1) for (let i = 0; i < 6; i++) { const a = Math.PI * (i + .5) / 6, r = 500; sparkle(X + Math.cos(a) * r, G - 40 - Math.sin(a) * r * .92, 34, seg(t, tPaint1 + i * .06, tPaint1 + .6 + i * .06)); }

    const mood = emotions(t, [[0, 'thinking', { lookX: .2, lookY: -.6 }], [tPaint0 - .2, 'determined', { lookY: -.7 }], [tProud, 'proud'],
                              [tJoy, 'excited', { emote: 'hearts' }], [tWave, 'happy']]);
    let pose = {};
    if (t > tPaint0 - .25 && t < tPaint1 + .15) {   // conducting: the brush arm sweeps left → up → right with the paint
      const k = ease(seg(t, tPaint0, tPaint1)), wig = .25 * Math.sin(t * 10);
      pose = { aR: lerp(.1, 1.45, Math.sin(Math.PI * k)) + wig * .5, aL: -.3, lookX: lerp(-.8, .8, k), dx: lerp(-.4, .4, k) };
    }
    let dy = mood.dy || 0, sq = mood.sq || 0;
    if (t > tJoy) { const j = jump(t, tJoy + .05, tJoy + .75, 2.2); dy += j.dy; sq += j.sq; }
    const cl = { ...mood, ...pose, dy, sq };
    if (t > tWave) cl.aL = lerp(cl.aL ?? .2, 1.2 + .5 * Math.sin((t - tWave) * 13), ease(seg(t, tWave, tWave + .2)));
    cl.armR = (u, sw) => {   // the brush: a wooden handle with a wet clay tip, held at the arm tip
      paint(ribbon([[-u * .2, 0], [u * 2.4, 0]], u * .28, u * .2), { wash: '#B9854F', ink: PAL.ink, sw });
      paint(ellPts(u * 2.9, 0, u * .7, u * .42, 14), { wash: t < tPaint1 ? BANDS[Math.min(5, Math.floor(seg(t, tPaint0, tPaint1) * 6))] : PAL.clayDk, ink: PAL.ink, sw });
    };
    clawd(X, G, U, cl);
    camEnd();
  }

  shots([[0, shot]]);
})();
