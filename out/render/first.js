//// shot=out/render/first-1-light-loading.png clip=#stage
const L = window.squaringLab; return `at load: idle ${L.idle()}, status "${document.getElementById('status').textContent}", busy "${document.getElementById('busy') && !document.getElementById('busy').hidden ? document.getElementById('busy').textContent : ''}", painted ${L.R.painted}`;
//// wait=!document.getElementById('drawProgress').hidden shot=out/render/first-2-light-drawing.png clip=#stage
return 'drawing';
//// wait=done shot=out/render/first-3-light-done.png clip=#stage
return document.getElementById('status').textContent;
