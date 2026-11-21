// ---------- core: helpers, the one state object, hooks, the busy indicator, theme colours.
// Every module may read and write S. This file belongs to the orchestrator: other modules do not edit it.
const $ = id => document.getElementById(id);
const PI = Math.PI;

// Fonts are an extra, never a gate: the sheet is added only after the page has loaded, so a slow or
// blocked font request cannot hold up the script. Until it arrives the fallback fonts in the CSS show.
addEventListener('load', () => {
  const l = document.createElement('link');
  l.rel = 'stylesheet';
  l.href = 'https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Sans+Condensed:wght@500;600&display=swap';
  document.head.appendChild(l);
}, { once: true });

// small vector kit (points are plain [x, y, z] arrays)
const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
const len = a => Math.hypot(a[0], a[1], a[2]);
const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
const scl = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
const norm = a => { const l = len(a) || 1; return [a[0] / l, a[1] / l, a[2] / l]; };
const clamp = (x, a, b) => Math.max(a, Math.min(b, x));

// A control spec describes one control as data (see buildControls in 70-dial.js). `def` is its default value.
const specDefaults = specs => Object.fromEntries(specs.filter(s => s.key !== undefined).map(s => [s.key, s.def]));

// ---------- state
const S = {
  mode: 'm',                // 'm' Mandelbrot set, 'j' Julia set, 'k' Kleinian group
  flat: false,              // true: draw only the slice z = S.cut as a flat picture (the 2D view)
  mosaic: false,            // Mandelbrot mode only: draw a small Julia set in every cell of a grid
  mosaicCell: 0.3,          // width of one mosaic cell
  approach: 0,              // index into APPROACHES
  param: {},                // S.param[approachId][key], filled from each approach's `params` specs by initState()
  n: 2, iter: 14, eq: 'z^n + c', z0: '0',
  c: [-1, 0, 0],            // the Julia constant
  abs: [0, 0, 0], flip: [0, 0],   // modifiers: |x| |y| |z| and flip y, flip z (each 0 or 1)
  cutOn: false, cut: 0,     // the cut plane z = S.cut; in the 2D view S.cut is the slice height whether or not cutOn is set
  colour: {},               // filled from COLOUR_CONTROLS by initState()
  lightAz: 250, lightEl: 48,
  q: { res: 1, aa: 12, steps: 260, detail: 1, stepk: 0.8, smooth: 1, normals: 'sharp', ao: true, shadow: true,
       de: 3 },             // de: how the distance is estimated. 3 = three neighbouring orbits (exact slope), 1 = one, 0 = none (fastest)
  view: { fov: 0.32,        // tangent of half the vertical field of view
          bound: 8,         // radius of the sphere outside which nothing is drawn
          zmin: 0.005, zmax: 24,   // nearest and farthest camera distance the zoom may reach
          fly: false,       // false: turn around a point (arcball). true: first-person fly
          speed: 1 },       // fly speed, in scene units per second
  v2: { x: -0.5, y: 0, h: 3.2 },   // 2D view: centre of the picture and its visible height, in scene units
  k: { mx: 0, my: 2, mz: 0, three: true, L: 1, iter: 150, invR: 1.2, cx: 1, cy: 1, cz: 0,   // iter: depth of the search; starts at the top of its ordinary range
       group: 0, bt: 1.4, bgrid: 0, bit: 16 },   // the second group, Balls on balls (32-balls.js): group 1 chooses it; its dial t, its grid, its rounds
  extreme: false,           // "extreme ranges": while on, dials that define wide limits (xmin, xmax, xlo, xhi) use them
};
const ap = () => APPROACHES[S.approach];
const apP = () => S.param[ap().id];          // the current approach's parameters, as an object keyed by spec key
const apVec = () => {                        // the same as four numbers, in spec order: this is the shader uniform uA
  const a = ap(), p = S.param[a.id], v = [0, 0, 0, 0];
  (a.params || []).filter(s => s.key !== undefined).forEach((s, i) => { if (i < 4) v[i] = +p[s.key]; });
  return v;
};
function initState() {
  APPROACHES.forEach(a => { S.param[a.id] = specDefaults(a.params || []); });
  S.colour = specDefaults(COLOUR_CONTROLS);
}

// ---------- hooks other modules register with (push a function)
const hooks = {
  view: [],     // called at most once per frame after the camera or the view changed (overlays redraw here)
  refresh: [],  // called at the end of refresh(), after an approach, power or mode change
};

// ---------- busy indicator. setBusy('compile', 'Preparing the formula') shows it; setBusy('compile', null) clears that task.
const busyTasks = new Map();
function setBusy(key, label) {
  if (label) busyTasks.set(key, label); else busyTasks.delete(key);
  let el = $('busy');
  if (!el) {
    el = document.createElement('div');
    el.id = 'busy'; el.className = 'busy'; el.hidden = true; el.setAttribute('role', 'status');
    el.innerHTML = '<span class="busy-spin" aria-hidden="true"></span><span class="busy-text"></span>';
    $('stage').appendChild(el);
  }
  const labels = [...busyTasks.values()];
  el.hidden = labels.length === 0;
  if (labels.length) el.querySelector('.busy-text').textContent = labels[labels.length - 1];
}

// ---------- saving a file the page has made (a picture, a 3D model)
// On the published page a plain download link does nothing: the host has to hand the file to the viewer, and it
// asks them to confirm each one. Opened as an ordinary file (the local preview, the tests) there is no host, so a
// download link is used. Only these endings are accepted by the host: png jpg jpeg webp gif txt json md csv svg
// pdf html zip. Anything else (a 3D model, for instance) has to travel inside a zip.
// Resolves { ok: true } or { ok: false, code, message }; message is a plain sentence that can be shown as it is.
// Tests can set window.squaringLabSaveHook = (filename, blob) => {...} to receive the file instead.
const SAVE_WORDS = {
  declined: 'The file was not saved, because the save was declined.',
  rate_limited: 'Another save is still waiting for an answer. Try again in a moment.',
  rejected_extension: 'This kind of file cannot be saved from here.',
  extension_not_enabled: 'This kind of file cannot be saved from here.',
  too_large: 'The file is too large to save from here. Try a smaller size.',
  unavailable: 'Saving files is not available in this view.',
  failed: 'The file could not be saved.',
};
// Which failures another press of the button can cure. The rest would only give the same answer again.
const SAVE_AGAIN = { declined: true, rate_limited: true, failed: true };
let saveHost;   // undefined: not asked yet. null: the host cannot save. Otherwise the host's downloads object.
// Never throws. A failure comes back as { ok: false, code, message, again }: message is a plain sentence to show,
// and again says whether pressing the button once more can help (so the caller knows whether to offer that).
async function saveFile(filename, data) {
  const blob = data instanceof Blob ? data : new Blob([data]);
  const no = code => ({ ok: false, code, message: SAVE_WORDS[code], again: !!SAVE_AGAIN[code] });
  if (typeof window.squaringLabSaveHook === 'function') {
    try { await window.squaringLabSaveHook(filename, blob); return { ok: true }; }
    catch (e) { return no('failed'); }
  }
  const hosted = !!(window.claude && typeof window.claude.use === 'function');
  if (hosted) {
    // an answer is kept only when the host gave one: a call that threw is asked again on the next press
    if (saveHost === undefined) { try { saveHost = await window.claude.use('downloads'); } catch (e) { return no('failed'); } }
    if (!saveHost) return no('unavailable');
    try { await saveHost.save({ filename, data: blob }); return { ok: true }; }
    catch (e) { return no(e && SAVE_WORDS[e.code] ? e.code : 'failed'); }
  }
  try {
    const a = document.createElement('a'), url = URL.createObjectURL(blob);
    a.href = url; a.download = filename; a.hidden = true;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 60000);
    return { ok: true };
  } catch (e) { return no('failed'); }
}

// ---------- theme tokens, read back for the canvases
const theme = {};
function hexRgb(h) {
  h = h.trim();
  if (h.length === 4) h = '#' + h[1] + h[1] + h[2] + h[2] + h[3] + h[3];
  const v = parseInt(h.slice(1), 16);
  return [(v >> 16 & 255) / 255, (v >> 8 & 255) / 255, (v & 255) / 255];
}
const lin = rgb => rgb.map(x => Math.pow(x, 2.2));
function readTheme() {
  const cs = getComputedStyle(document.documentElement), g = k => cs.getPropertyValue(k).trim();
  theme.stage = hexRgb(g('--stage')); theme.cut = hexRgb(g('--cut')); theme.cutInk = hexRgb(g('--cut-ink'));
  theme.ink = g('--ink'); theme.ink2 = g('--ink-2'); theme.line = g('--line'); theme.brass = g('--brass');
  theme.dark = (theme.stage[0] + theme.stage[1] + theme.stage[2]) / 3 < 0.4;
}
