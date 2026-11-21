// ---------- (round 29) dots with a colour of their own, and the choice Show: A grid of points
// Is the stage dark (the dark theme)? The dots' colours are light on a dark stage and deep on a light one.
function learnVDark() {
  try { const v = hexRgb(LEARN.col.stage); return 0.3 * v[0] + 0.59 * v[1] + 0.11 * v[2] < 0.5; } catch (err) { return true; }
}
// A dot's colour for good, from where it starts: the hue from which way it lies from the centre (in space: round
// the z-axis; on a line: from left to right), and how light from how far out it lies (in space: how high). So the
// eye can follow a dot, and a turn or a stretch of the whole grid shows in the colours.
function learnVDotColour(p, space, dark) {
  if (space === 1) return `hsl(${Math.round(clamp((p[0] + 2) / 4, 0, 1) * 300)}, ${dark ? 88 : 82}%, ${dark ? 66 : 38}%)`;
  const hue = Math.round((Math.atan2(p[1], p[0]) * 180 / PI + 360) % 360);
  const t = space === 3 ? clamp((2 - p[2]) / 4, 0, 1) : clamp(Math.hypot(p[0], p[1]) / 2, 0, 1);
  return dark ? `hsl(${hue}, 88%, ${Math.round(80 - 26 * t)}%)` : `hsl(${hue}, 84%, ${Math.round(26 + 18 * t)}%)`;
}
// An even grid of points over the big circle (everything no further than 2 from the centre; in space the big ball;
// on a line a row from −2 to 2), with the gap h between neighbours. The grid is shifted off the centre: half a gap
// along x and a quarter along y on the page, so that no two dots are mirror twins through the centre (squaring
// would lay them on top of each other); half, half and a quarter in space, so that no dot sits on an axis or in
// the flat plane, where many of the 3D rules have a special case. "A whole shape" lays its dots out the same way
// (learnShapeDots in 67-learn-shape.js).
const LEARN_V_GRID = { 1: 0.1, 2: 0.25, 3: 0.5 };
function learnVGridPoints(space, gap) {
  const h = gap || LEARN_V_GRID[space], m = Math.ceil(2 / h) + 1, out = [];
  if (space === 1) { const n = Math.round(2 / h); for (let i = -n; i <= n; i++) out.push([i * h + 0, 0, 0]); return out; }
  if (space === 2) {
    for (let j = m - 1; j >= -m; j--) for (let i = -m; i < m; i++) { const p = [(i + 0.5) * h, (j + 0.25) * h, 0]; if (p[0] * p[0] + p[1] * p[1] <= 4) out.push(p); }
    return out;
  }
  for (let k = m - 1; k >= -m; k--) for (let j = m - 1; j >= -m; j--) for (let i = -m; i < m; i++) {
    const p = [(i + 0.5) * h, (j + 0.5) * h, (k + 0.25) * h];
    if (p[0] * p[0] + p[1] * p[1] + p[2] * p[2] <= 4) out.push(p);
  }
  return out;
}
// A handful of the grid's dots to draw larger, so that single ones can be followed: the ones nearest to five
// places spread round the centre.
function learnVGridMarked(start, space) {
  const want = space === 1 ? [[-1.5, 0, 0], [-0.7, 0, 0], [0.4, 0, 0], [1.1, 0, 0], [1.8, 0, 0]]
    : space === 2 ? [20, 95, 165, 235, 310].map((d, i) => { const a = d * PI / 180, r = i % 2 ? 0.75 : 1.3; return [r * Math.cos(a), r * Math.sin(a), 0]; })
      : [[1, 0.3, 0.5], [-0.4, 1, -0.5], [-1, -0.5, 0.6], [0.3, -1.1, -0.4], [0.2, 0.3, 1.3]];
  const out = [];
  for (const t of want) {
    let best = -1, bd = Infinity;
    start.forEach((p, i) => { const d = Math.hypot(p[0] - t[0], p[1] - t[1], p[2] - t[2]); if (d < bd && !out.includes(i)) { bd = d; best = i; } });
    if (best >= 0) out.push(best);
  }
  return out;
}
// The words of the select Show for the space on show: its choices, its help, and the line under it.
function learnVShowOptions(space) {
  return [['point', 'The point alone'], ['circle', 'A small circle round the point'],
    ['all', space === 1 ? 'A row of points along the line' : space === 2 ? 'One point for every direction (a ring)' : 'One point for every direction (a ball)'],
    ['grid', 'A grid of points']];
}
function learnVShowHelp(space) {
  const head = 'The extra points take the same moves as your point, each by its own amount, so you see what a move does to everything around the point. ';
  const tail = 'These are not laid out afresh: each goes on from where the last step left it.';
  if (space === 1) return head + 'A small circle: on a line, a short row of points close around your point. A row of points along the line: points laid out evenly from −2 to 2. Both of these are laid out afresh at the start of every step. A grid of points: on a line, a row of dots from −2 to 2. ' + tail;
  return head + 'A small circle: points close around your point. One point for every direction: a direction is which way a point lies from the centre, without how far. These points all lie 1 from the centre, one in each direction, so they show what a move does to every direction at once. Both of these are laid out afresh at the start of every step. A grid of points: dots laid out evenly over the picture. ' + tail;
}
// One short line under the select, on show while extra points are: what they are right now, and whether they are
// laid out afresh.
function learnVShowLine() {
  const L = LEARN, sp = L.space, k = L.k, afresh = ' Laid out afresh at each step.';
  if (L.show === 'circle') return (sp === 1 ? 'Short row: points close around your point.' : 'Small circle: points close around your point.') + afresh;
  if (L.show === 'all') return (sp === 1 ? 'Row: points along the line, from −2 to 2.' : (sp === 2 ? 'Ring' : 'Ball') + ': one point for every direction, all 1 from the centre.') + afresh;
  if (L.show === 'grid') {
    return k > 0 ? `Grid: each dot goes on from where the last step left it. This is where they are after ${k} step${k === 1 ? '' : 's'}.`
      : `Grid: dots laid out evenly ${sp === 1 ? 'along the line, from −2 to 2' : sp === 2 ? 'over the big circle' : 'over the big ball'}. Each dot goes on from where the last step left it.`;
  }
  return '';
}
function learnVShowPaint() {
  const L = LEARN, c = L.showCtl, line = L.el.showLine;
  if (!c || !line) return;
  if (L.showSig !== L.space) {
    L.showSig = L.space;
    c.setOptions(learnVShowOptions(L.space));
    const help = document.getElementById('learn-showHelp');
    if (help) help.textContent = learnVShowHelp(L.space);
  }
  const text = learnVShowLine();
  if (line.textContent !== text) line.textContent = text;
  line.hidden = !text;
}

