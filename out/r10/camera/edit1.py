"""Engineer "camera", round 10: the edits to src/js/50-camera.js, each applied exactly once (kept as a record)."""
import io, sys
p = 'src/js/50-camera.js'
s = io.open(p, encoding='utf-8', newline='').read()
nl = '\r\n' if '\r\n' in s else '\n'
s = s.replace('\r\n', '\n')


def rep(old, new, count=1):
    global s
    if s.count(old) != count:
        sys.exit('expected %d of: %r, found %d' % (count, old[:70], s.count(old)))
    s = s.replace(old, new)


# 1. constants
rep("""const CAM_ROW = 520;                       // a stage narrower than this many pixels (a phone) has no room for the zoom column beside the solid: the zoom becomes a row under the picture
""", """const CAM_ROW = 520;                       // a stage narrower than this many pixels (a phone) has no room for the zoom column beside the solid: the zoom becomes a row under the picture
const CAM_PINCH_PAST = 0.1;                // a pinch must ask for this much more than a zoom limit allows (a tenth, on a log scale) before the note about the limit shows
const CAM_LOOK_WAIT = 15000;               // milliseconds the start view waits for a picture it has to look at (camLookLater)
""")
# 2. bookkeeping
rep("""  raf: 0, tmr: 0, last: 0, railPtr: null, speedTmr: 0, noteTmr: 0,
};""", """  raf: 0, tmr: 0, last: 0, railPtr: null, speedTmr: 0, noteTmr: 0,
  past: 0,              // how far the pinch under way has asked to go past a zoom limit, on a log scale (camPinchPast)
  look: null,           // a look at the picture that waits for the picture: the camera as the start view left it, and its timers (camLookLater)
};""")
# 3. camHome says whether the camera was used as given
rep("""// of 0.32, so they are scaled to fit the solid the same way at the current one.
function camHome(preset) {""", """// of 0.32, so they are scaled to fit the solid the same way at the current one. `given` is true in the result when
// the camera was used exactly as given.
function camHome(preset) {""")
rep("""    v.dist = Math.max(v.dist, camTrapDist(v.target));
  }
  return v;
}""", """    v.dist = Math.max(v.dist, camTrapDist(v.target));
  }
  v.given = asGiven;
  return v;
}""")
# 4. the look that waits
rep("""// Put the view back to the start for what is on show (see camHome for `preset`).""", """// The start view of a Kleinian trap solid has no rule to stand back by (camTrapBall), so it must look at the picture
// as Reset view does. When a start view is set (a change of mode) that picture may not exist yet: its program can
// still be in the making, and pick() sees nothing until it is ready. So the look waits for the picture, and takes
// place only if the camera is still exactly where the start view put it. Once the user has pressed on the picture,
// dragged, scrolled, used the slider or a key, typed a zoom limit or switched the camera or the view, the camera
// is theirs and the look is dropped for good.
// Can pick() see the picture for the settings as they are now? The renderer keeps the state of its programs to
// itself (40-render.js), so its names are asked for, never assumed: without them only a finished picture counts.
function camCanSee() {
  try {
    if (typeof sceneNow === 'function' && typeof progs === 'object') { const w = sceneNow(), P = w && progs.get(w.key); return !!P && P.state === 'ready'; }
  } catch (err) { /* fall through to the public answer */ }
  return renderIdle();
}
function camLookDrop() {
  const k = CV.look;
  if (k) { clearTimeout(k.tmr); cancelAnimationFrame(k.raf); CV.look = null; }
}
function camLookLater() {
  camLookDrop();
  const k = CV.look = { yaw: cam.yaw, pitch: cam.pitch, dist: cam.dist, target: cam.target.slice(), kind: camKind(), lo: S.view.zmin, hi: S.view.zmax, t0: performance.now(), tmr: 0, raf: 0 };
  k.tmr = setTimeout(camLookTick, 0);   // first when the caller has finished changing the settings; a picture that is ready is then looked at before it is drawn
}
function camLookTick() {
  const k = CV.look;
  if (!k) return;
  clearTimeout(k.tmr); cancelAnimationFrame(k.raf);
  const t = cam.target, mine = cam.yaw === k.yaw && cam.pitch === k.pitch && cam.dist === k.dist && t[0] === k.target[0] && t[1] === k.target[1] && t[2] === k.target[2] &&
    camKind() === k.kind && S.mode === 'k' && S.view.zmin === k.lo && S.view.zmax === k.hi;
  if (!mine || CV.ptr.size || CV.keys.size || CV.goal || CV.railPtr !== null || performance.now() - k.t0 > CAM_LOOK_WAIT) { CV.look = null; return; }
  if (!camCanSee()) {   // look again on the next frame, or by the timer when frames are paused
    k.raf = requestAnimationFrame(camLookTick); k.tmr = setTimeout(camLookTick, 250);
    return;
  }
  CV.look = null;
  camStepBack();
  if (cam.dist !== k.dist) touch();
}
// Put the view back to the start for what is on show (see camHome for `preset`).""")
rep("""  if (only !== '3d') { S.v2.x = v.target[0]; S.v2.y = v.target[1]; S.v2.h = clamp(v.h, S.v2.hmin, S.v2.hmax); }
  CV.goal = null; CV.vel = [0, 0, 0];
}""", """  if (only !== '3d') { S.v2.x = v.target[0]; S.v2.y = v.target[1]; S.v2.h = clamp(v.h, S.v2.hmin, S.v2.hmax); }
  CV.goal = null; CV.vel = [0, 0, 0];
  // a Kleinian trap solid on show: look at the picture as soon as there is one. A camera that was given is left as it is.
  camLookDrop();
  if (only !== '2d' && !v.given && S.mode === 'k' && !S.flat && camTrapBall(cam.target) > 0) camLookLater();
}""")
rep("""function resetView() { resetCam(undefined, S.flat ? '2d' : '3d'); camStepBack(); touch(); }""",
    """// The look at the picture happens at once when the picture can be seen. When its program is still in the making
// the look that resetCam() left waiting takes place once it is ready.
function resetView() {
  resetCam(undefined, S.flat ? '2d' : '3d');
  if (camCanSee()) camLookDrop();
  camStepBack(); touch();
}""")
# 5. the note at a limit, shared by the wheel, the buttons and the pinch
rep("""  if (asked !== v && camAim(ch) === v) {
    const why = CAM_TEXT[camKind()].stop[v === ch.lo ? 0 : 1];
    // as a row under the picture the slider has its boxes at the left and right ends
    camNote(CV.ui && CV.ui.row ? why.replace('at the top', 'at the left end').replace('at the bottom', 'at the right end') : why);
  }
""", """  if (asked !== v && camAim(ch) === v) camStopNote(v === ch.lo ? 0 : 1);
""")
rep("""// Scroll by a factor: above 1 backs away""", """// The note that says the zoom rests on its nearest (end 0) or farthest (end 1) limit, and where that limit is set.
function camStopNote(end) {
  const why = CAM_TEXT[camKind()].stop[end];
  // as a row under the picture the slider has its boxes at the left and right ends
  camNote(CV.ui && CV.ui.row ? why.replace('at the top', 'at the left end').replace('at the bottom', 'at the right end') : why);
}
// Scroll by a factor: above 1 backs away""")
# 6. the pinch
rep("""function camPinch(f, at) {      // fingers moved apart (f < 1) or together. No easing here: the fingers are the easing.
  const g = CV.goal;
  if (S.flat) {
    const h = clamp(S.v2.h * f, S.v2.hmin, S.v2.hmax), u = camFlatUv(at[0], at[1]), k = (S.v2.h - h) / 2;
    S.v2.x += u[0] * k; S.v2.y += u[1] * k; S.v2.h = h;
    if (g) g.h = g.at = null;
  } else if (S.view.fly) cam.target = add(cam.target, scl(basis().f, -1.5 * Math.log(f) * S.view.speed));
  else { cam.dist = clampDist(cam.dist * f); if (g) g.dist = null; }
}""", """// A pinch that pushes on against a zoom limit gets the note the wheel and the buttons give there. `asked` is what
// the fingers asked for, `v` what the limits allowed. Fingers are never quite steady, and two that slide the picture
// change their spread a little as they go, so the note waits until the pinch has asked for a tenth more than the
// limit allows (CAM_PINCH_PAST). Moving inside the limits pays that off again, and lifting a finger clears it.
function camPinchPast(asked, v, f) {
  if (asked === v) { CV.past = Math.max(0, CV.past - Math.abs(Math.log(f))); return; }
  CV.past = Math.min(2 * CAM_PINCH_PAST, CV.past + Math.abs(Math.log(asked / v)));
  if (CV.past >= CAM_PINCH_PAST) camStopNote(asked < v ? 0 : 1);
}
function camPinch(f, at) {      // fingers moved apart (f < 1) or together. No easing here: the fingers are the easing.
  const g = CV.goal;
  if (S.flat) {
    const h = clamp(S.v2.h * f, S.v2.hmin, S.v2.hmax), u = camFlatUv(at[0], at[1]), k = (S.v2.h - h) / 2;
    camPinchPast(S.v2.h * f, h, f);
    S.v2.x += u[0] * k; S.v2.y += u[1] * k; S.v2.h = h;
    if (g) g.h = g.at = null;
  } else if (S.view.fly) cam.target = add(cam.target, scl(basis().f, -1.5 * Math.log(f) * S.view.speed));
  else { const d = cam.dist * f; cam.dist = clampDist(d); camPinchPast(d, cam.dist, f); if (g) g.dist = null; }
}""")
rep("""    const p = CV.ptr.get(e.pointerId), now = performance.now();
    CV.ptr.delete(e.pointerId);
""", """    const p = CV.ptr.get(e.pointerId), now = performance.now();
    CV.ptr.delete(e.pointerId);
    CV.past = 0;   // a pinch has ended
""")
io.open(p, 'w', encoding='utf-8', newline='').write(s.replace('\n', nl))
print('edited', p, 'newline', repr(nl))
