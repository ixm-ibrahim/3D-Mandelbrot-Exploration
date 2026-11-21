//// wait=done
const L = window.squaringLab; L.R.warmOn = false; L.S.q.aa = 2; L.touch(); return 'ready';
//// wait=done
const L = window.squaringLab; L.S.mode = 'k'; L.touch(); return 'Kleinian view with a broken shader (one console error is expected)';
//// shot=out/render/fail-1-shader.png clip=#stage
const L = window.squaringLab, g = document.getElementById('glfail'), b = document.getElementById('busy');
return `broken shader: message shown ${!g.hidden} ("${g.textContent}"), busy label hidden ${!b || b.hidden}, idle ${L.idle()}, status "${document.getElementById('status').textContent}", compiles ${L.R.compiles}`;
//// wait=done
const L = window.squaringLab; L.cam.yaw += 0.1; L.touch(); await new Promise(r => setTimeout(r, 200)); return 'touch again while failed: compiles ' + L.R.compiles + ', idle ' + L.idle();
//// wait=done shot=out/render/fail-2-recovered.png clip=#stage
const L = window.squaringLab; L.S.mode = 'm'; L.touch(); return 'back to the Mandelbrot view';
//// 
return 'message hidden ' + document.getElementById('glfail').hidden + ', status ' + document.getElementById('status').textContent;
