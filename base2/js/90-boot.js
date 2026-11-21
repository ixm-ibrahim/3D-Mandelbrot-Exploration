// ---------- start. The only file that runs code at load time.
// window.squaringLab is the handle tests and the console use. idle() is true once the picture is fully drawn
// and the scorecard has finished measuring. The names after setBusy are there for the modules' own test scripts.
window.squaringLab = {
  S, cam, touch, refresh, syncControls, R, idle: () => renderIdle() && cardIdle(), measure, setBusy,
  renderIdle, cardIdle, cardRun, updateCard, MATH, APPROACHES, PRESETS, compileFormula, inversionPower,
  basis, resetCam, resetZoomLimits, setCamMode, pick, hooks, CV, viewChanged, clampDist, camChan,
  resetGroup, JULIA_PRESETS, KLEIN_PRESETS, applyJuliaPreset, applyKleinPreset,
  juliaSaved: () => juliaSaved, juliaSavePoint, juliaDeletePoint,
};
boot();
