// Start-up. The only file that runs code when the page loads.

// The page's handle for the console and for the tools in tools/. idle() is true once the live picture is fully
// drawn and the scorecard has finished measuring; it does not wait for a picture or a model that is being saved.
window.squaringLab = {
  S, cam, MATH, CARRY, APPROACHES, APPROACH_GROUPS, JULIA_PRESETS, KLEIN_PRESETS, LEARN,
  refresh, syncControls, touch, viewChanged, resetCam,
  applyJuliaPreset, frameJuliaPreset, applyKleinPreset, frameKleinPreset, ballsFrame,
  idle: () => renderIdle() && cardIdle(), exportBusy, meshBusy,
};

// The font sheet is added after the page has loaded, so a slow or blocked font request cannot hold up the script.
addEventListener('load', () => {
  const l = document.createElement('link');
  l.rel = 'stylesheet';
  l.href = 'https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Sans+Condensed:wght@500;600&display=swap';
  document.head.appendChild(l);
}, { once: true });

boot();
learnInit();
pinInit();
