// ---------- start. The only file that runs code at load time.
// window.squaringLab is the handle tests and the console use. idle() is true once the live picture is fully drawn
// and the scorecard has finished measuring; it does not wait for background jobs (exportBusy and meshBusy say
// whether one is running). The names after setBusy are there for the modules' own test scripts.
window.squaringLab = {
  S, cam, touch, refresh, syncControls, R, idle: () => renderIdle() && cardIdle(), measure, setBusy,
  renderIdle, cardIdle, cardRun, updateCard, MATH, APPROACHES, PRESETS, compileFormula, inversionPower,
  basis, resetCam, resetZoomLimits, setCamMode, pick, hooks, CV, viewChanged, clampDist, camChan,
  resetGroup, JULIA_PRESETS, KLEIN_PRESETS, applyJuliaPreset, applyKleinPreset, frameJuliaPreset, frameKleinPreset,
  juliaSaved: () => juliaSaved, juliaSavePoint, juliaDeletePoint, juliaKeyAt, kleinPresetAt, kleinTrouble,
  resetAll: uiResetAll, saveFile, showFigure4: uiFigure4, onePlane: uiOnePlane, showTwin: uiTwin, twinOff: uiTwinOff, juliaFoundDiff, applyJuliaFound,
  showQuaternionSquare: () => uiQuat('lathe'), showTwistedSquare: () => uiQuat('tilt'), juliaFoundWords,
  EXAMPLES, applyExample, exampleAt, kleinReach, kleinSwallowed,
};
// What this round's other modules add, each only when that module is part of the page.
if (typeof APPROACH_GROUPS !== 'undefined') window.squaringLab.APPROACH_GROUPS = APPROACH_GROUPS;
if (typeof CARRY !== 'undefined') window.squaringLab.CARRY = CARRY;
if (typeof takeSnapshot === 'function') window.squaringLab.takeSnapshot = takeSnapshot;
if (typeof releaseSnapshot === 'function') window.squaringLab.releaseSnapshot = releaseSnapshot;
if (typeof sampleSlice === 'function') window.squaringLab.sampleSlice = sampleSlice;
if (typeof exportBusy === 'function') window.squaringLab.exportBusy = exportBusy;
if (typeof meshBusy === 'function') window.squaringLab.meshBusy = meshBusy;
if (typeof zipStore === 'function') window.squaringLab.zipStore = zipStore;
if (typeof setExtreme === 'function') window.squaringLab.setExtreme = setExtreme;
if (typeof isExtreme === 'function') window.squaringLab.isExtreme = isExtreme;
boot();
// Modules that start after the page is up, each only when it is part of the page.
if (typeof learnInit === 'function') learnInit();
if (typeof pinInit === 'function') pinInit();
window.squaringLab.learn = typeof LEARN !== 'undefined' ? LEARN : null;
window.squaringLab.learnPlan = typeof learnPlan === 'function' ? learnPlan : null;
