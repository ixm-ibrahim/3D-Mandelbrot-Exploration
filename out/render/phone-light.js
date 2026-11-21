//// wait=done
const L = window.squaringLab; L.R.warmOn = false; return 'ready';
//// wait=!document.getElementById('drawProgress').hidden&&parseFloat(document.getElementById('drawProgress').firstChild.style.transform.slice(7))>0.25 shot=out/render/phone-light.png clip=#stage
const L = window.squaringLab; L.S.q.aa = 200; L.touch(); return 'long drawing started';
//// 
const b = document.getElementById('drawProgress').getBoundingClientRect(), s = document.getElementById('stage').getBoundingClientRect();
return `bar box: left ${b.left - s.left}, width ${b.width} of stage ${s.width}, bottom gap ${s.bottom - b.bottom}, height ${b.height}; page scroll width ${document.documentElement.scrollWidth} of ${window.innerWidth}`;
