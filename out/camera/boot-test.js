// Throwaway test copy of 90-boot.js: the same start, with the camera's internals exposed for the test scripts.
window.squaringLab = { S, cam, touch, refresh, syncControls, R, idle: renderIdle, measure, setBusy,
  basis, resetCam, resetZoomLimits, pick, hooks, CV, setCamMode, viewChanged, clampDist, camChan, CAM_DEF, CAM_LIM };
boot();
