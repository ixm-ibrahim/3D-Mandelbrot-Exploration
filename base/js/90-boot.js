// ---------- start. The only file that runs code at load time.
// window.squaringLab is the handle tests and the console use; idle() is true once the picture is fully drawn.
window.squaringLab = { S, cam, touch, refresh, syncControls, R, idle: renderIdle, measure, setBusy };
boot();
