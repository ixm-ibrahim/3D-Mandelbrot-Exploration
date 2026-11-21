// ---------- start. TEST STAND-IN for the mesh engineer (out/r4/mesh): the frozen boot file plus what the mesh
// tests need. The real section and call are the page engineer's.
window.squaringLab = {
  S, cam, touch, refresh, syncControls, R, idle: () => renderIdle() && cardIdle(), measure, setBusy,
  renderIdle, cardIdle, cardRun, updateCard, MATH, APPROACHES, PRESETS, compileFormula, inversionPower,
  basis, resetCam, resetZoomLimits, setCamMode, pick, hooks, CV, viewChanged, clampDist, camChan,
  resetGroup, JULIA_PRESETS, KLEIN_PRESETS, applyJuliaPreset, applyKleinPreset,
  juliaSaved: () => juliaSaved, juliaSavePoint, juliaDeletePoint,
  buildMeshPanel, meshBusy, zipStore, MESH, saveFile,
};
if (typeof takeSnapshot === 'function') Object.assign(window.squaringLab, { takeSnapshot, sampleSlice, releaseSnapshot });
boot();
{
  const d = document.createElement('details');
  d.className = 'sec'; d.id = 'secMesh'; d.open = true;
  d.innerHTML = '<summary class="label">Save a 3D model</summary><div class="sec-body"><div id="meshPanel"></div></div>';
  $('sections').appendChild(d);
  buildMeshPanel('meshPanel');
}
