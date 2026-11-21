// ---------- test-only boot: exposes internals so shader tests can time compiles and pick points.
const testSet = (h, o, k, t) => ({ GL_HEAD: h, GL_ORBIT: o, GL_KLEIN: k, GL_TAIL: t });
window.squaringLab = { S, cam, touch, refresh, syncControls, R, idle: renderIdle, measure, setBusy,
  gl: () => gl,
  GLSL: () => ({ GL_HEAD, GL_COLOUR, GL_ORBIT, GL_KLEIN, GL_TAIL, VERT,
    ALT: typeof ALT_TAILS === 'undefined' ? null : ALT_TAILS,
    OLD: typeof OLD_GL_HEAD === 'undefined' ? null : testSet(OLD_GL_HEAD, OLD_GL_ORBIT, OLD_GL_KLEIN, OLD_GL_TAIL),
    V2: typeof V2_GL_HEAD === 'undefined' ? null : testSet(V2_GL_HEAD, V2_GL_ORBIT, V2_GL_KLEIN, V2_GL_TAIL) }),
  makeProgram, sceneProgram, setScene, progs, pick, APPROACHES, compileFormula, resetCam };
boot();
