
// ---------- what a list entry does
// An entry sets only what it is about. A Julia entry sets the point c. A Kleinian entry sets the group (mu, L,
// the third map) and its turning-out sphere. The camera, the iterations, the depth of the search, the quality and
// the approach are the user's and stay as they are. "Frame it" is the separate, camera-only step.
const presetSame = (a, b) => Math.abs(a - b) < 1e-9;
// Preset cameras were chosen on a wide stage with the starting field of view. On a tall, narrow stage the camera
// backs off so that wide sets are not cut off at the sides (Julia) or hidden behind the zoom slider (Kleinian).
const presetNarrow = () => Math.max(1, 1.2 * stage.clientHeight / Math.max(1, stage.clientWidth));
const presetNarrowK = () => (stage.clientWidth < stage.clientHeight ? 1.2 : 1);
// Move the camera, and the frame of the 2D view, to a recommended view. `hint` is { yaw, pitch, dist, target? } or
// nothing (then the mode's own starting view is used); `back` is the narrow-stage factor; `flatH` is the height of
// the 2D picture that holds the whole object. The camera mode (arcball or fly) is left as it is.
function presetFrame(hint, back, flatH) {
  if (!hint) { resetCam(); touch(); return; }
  resetCam({ cam: { yaw: hint.yaw, pitch: hint.pitch, dist: clampDist(hint.dist * back * 0.32 / S.view.fov), target: hint.target || [0, 0, 0] } });
  S.v2.x = 0; S.v2.y = 0; S.v2.h = clamp(flatH, S.v2.hmin, S.v2.hmax);
  touch();
}

// ----- Julia points. A key names an entry: 'p3' is the fourth shipped one, 's0' the first saved one.
const juliaEntry = key => (!key ? null : key[0] === 's' ? juliaSaved[+key.slice(1)] : key[0] === 'p' ? JULIA_PRESETS[+key.slice(1)] : null) || null;
const juliaFits = p => !!p && p.c.every((x, i) => presetSame(x, S.c[i]));
// The key of the entry the point c stands on: `prefer` while it still fits (two entries may share a point), else
// the first saved point that fits, else the first shipped one, else 'own'.
function juliaKeyAt(prefer) {
  if (juliaFits(juliaEntry(prefer))) return prefer;
  let i = juliaSaved.findIndex(juliaFits);
  if (i >= 0) return 's' + i;
  i = JULIA_PRESETS.findIndex(juliaFits);
  return i >= 0 ? 'p' + i : 'own';
}
const juliaPresetAt = () => juliaEntry(juliaKeyAt());
function applyJuliaPreset(p) {
  S.c = p.c.slice(0, 3);   // a copy, because the c dials write into S.c in place
  syncControls();
  uiJuliaMark();
  touch();
}
// Distances that replace an entry's own for "Frame it". The Airplane's spine ran out of the picture at its 4.0.
const JULIA_FRAME_DIST = { Airplane: 5.2 };
// Camera only. A saved point, or a point that is in no list, gets the Julia view the page starts with.
function frameJuliaPreset(p) {
  const k = p && p.cam;
  presetFrame(k ? { ...k, dist: JULIA_FRAME_DIST[p.name] || k.dist } : null, presetNarrow(), 3.6);
}
// The note of a shipped entry. Some end with advice that only fits the Sphere inversions approach ("Best with one
// plane and about 24 iterations."). An entry no longer sets those dials, so the advice is shown as advice, and
// only while that approach is the one in use.
function juliaNoteFor(p) {
  const m = /^(.*?)\s*Best with ([^.]*)\.$/.exec(p.note || '');
  if (!m) return p.note || '';
  return ap().id === 'mercator' ? `${m[1]} With this approach it looks best with ${m[2]}.` : m[1];
}

// ----- Kleinian entries
const KLEIN_KEYS = ['mx', 'my', 'mz', 'three', 'L', 'cx', 'cy', 'cz', 'invR'];   // what an entry sets, and all it sets
function kleinFits(p) {
  if (!p) return false;
  return KLEIN_KEYS.every(key => (key === 'three' ? !!S.k.three === !!p.k.three
    : key === 'L' && !p.k.three ? true                // without the third map L does nothing
    : p.k[key] === undefined || presetSame(S.k[key], p.k[key])));
}
function applyKleinPreset(p) {
  KLEIN_KEYS.forEach(key => { if (p.k[key] !== undefined) S.k[key] = p.k[key]; });
  syncControls();
  uiKleinMark();
  touch();
}
// Index of the entry the Kleinian dials stand at (`prefer` first, while it still fits), or -1 when they are the user's own.
function kleinPresetAt(prefer) {
  return kleinFits(KLEIN_PRESETS[prefer]) ? prefer : KLEIN_PRESETS.findIndex(kleinFits);
}
function frameKleinPreset(p) { presetFrame(p && p.cam, presetNarrowK(), 4.5); }
// Wording kept out of the data files: "the family" is explained nowhere on the page.
const kleinNoteFor = p => String(p.note || '').replace(/from the (\S+) cusp into the family/, 'above the $1 cusp');
// What is wrong with the group as the dials stand, in plain words, or ''. The limits are where the testers'
// pictures broke up: none of the shipped entries is inside them.
function kleinTrouble() {
  const k = S.k, out = [];
  if (k.my < 1.45 || Math.hypot(k.my, k.mz) < 1.6) out.push('The walls are so close together that the pearls overlap and the picture breaks up. The known pictures keep the i part of μ between about 1.6 and 2.');
  if (k.three && k.L < 1) out.push('With L below 1 the rows of pearls overlap in depth, which punches holes in them.');
  if (k.cy <= 0 || k.cy >= k.my) out.push('The centre of the turning-out sphere is inside a wall, so the solid fills the picture. Keep centre y between 0 and the i part of μ.');
  return out.join(' ');
}

// ---------- saved Julia points: a name and the point c, nothing else. Kept in localStorage where the page is
// allowed to; where it is not (a locked-down frame), every access throws and the list simply lives until the
// page is closed.
const JULIA_SAVED_KEY = 'squaringLab.juliaPoints.v1', JULIA_SAVED_MOST = 200;
let juliaSaved = [];
function juliaSavedLoad() {
  try {
    const list = JSON.parse(localStorage.getItem(JULIA_SAVED_KEY) || '[]');
    if (!Array.isArray(list)) return;
    const num = x => typeof x === 'number' && isFinite(x);
    // points saved by an earlier build also carry a camera and a plane count: those are dropped here
    juliaSaved = list.filter(p => p && Array.isArray(p.c) && p.c.length === 3 && p.c.every(num)).slice(0, JULIA_SAVED_MOST)
      .map(p => ({ name: String(p.name || 'Saved point').slice(0, 60), note: '', c: p.c.slice(), source: 'saved' }));
  } catch (err) { /* no storage, or something else wrote under this key: start with an empty list */ }
}
// -> true when the list reached storage, false when it will be gone after this visit
function juliaSavedStore() {
  try { localStorage.setItem(JULIA_SAVED_KEY, JSON.stringify(juliaSaved.map(p => ({ name: p.name, c: p.c })))); return true; } catch (err) { return false; }
}
// Save the current Julia point. -> { ok, kept, at, dup }: ok false when the list is full; kept false when storage
// is blocked; at is the index of the entry; dup true when this point was already saved under this name.
function juliaSavePoint(name) {
  const c = S.c.slice(0, 3);
  let label = String(name || '').trim().slice(0, 60) || `c = (${c.map(x => dialFmt(+(+x).toFixed(4))).join(', ')})`;
  const same = juliaSaved.findIndex(p => p.name === label && p.c.every((x, i) => presetSame(x, c[i])));
  if (same >= 0) return { ok: true, kept: juliaSavedStore(), at: same, dup: true };
  if (juliaSaved.length >= JULIA_SAVED_MOST) return { ok: false, kept: false };
  // the same name on another point gets a number, so the two can be told apart in the list
  if (juliaSaved.some(p => p.name === label)) {
    let k = 2;
    while (juliaSaved.some(p => p.name === `${label} (${k})`)) k++;
    label = `${label} (${k})`;
  }
  juliaSaved.push({ name: label, note: '', c, source: 'saved' });
  return { ok: true, kept: juliaSavedStore(), at: juliaSaved.length - 1, dup: false };
}
function juliaDeletePoint(i) {
  if (i < 0 || i >= juliaSaved.length) return false;
  juliaSaved.splice(i, 1);
  juliaSavedStore();
  return true;
}
