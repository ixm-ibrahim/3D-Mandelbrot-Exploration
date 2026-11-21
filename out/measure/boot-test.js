// Test copy of 90-boot.js: the same start-up, plus a handle T on the scorecard's internals for the measure tests.
window.squaringLab = { S, cam, touch, refresh, syncControls, R, idle: renderIdle, measure, setBusy,
  T: { updateCard, buildCard, buildStep3d, drawStep2d, drawStep3d, MATH, APPROACHES, hooks, cardRun, cardIdle, cardPlane, cardSpace,
       stepCaption2d, stepCaption3d, ap, apP, fmtN, busyTasks, specDefaults, measureBegin, measureRun, measureEnd, basis } };
boot();
