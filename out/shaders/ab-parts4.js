//#
const { L, G, fill, table, sub } = window.T;
const A = L.APPROACHES[1].glsl, O = fill(G.GL_ORBIT, 'z^n + c', '0', 2), H = G.GL_HEAD + G.GL_COLOUR + A + O;
const m1 = G.ALT.m1;
const noGB = s => s.split('gB[0] = rd;').join(';').split('gB[0] = L;').join(';').split('gB[0] = nor;').join(';');
return 'lathe, march + shading: ' + table({
  asis: H + m1,
  'gB never written': H + noGB(m1),
  'no flat branch': H + sub(m1, 'if (flat2){\n      if (gInsideOut', 'if (false){\n      if (gInsideOut'),
  'no probe': H + sub(m1, 'probing = ORBIT_SCENE;', 'probing = false;'),
  'flat colour shading': H + sub(m1, 'vec3 alb = surfaceColour(p, nor, t);', 'vec3 alb = vec3(0.8);'),
});
//#
const { L, G, fill, table, sub } = window.T;
const A = L.APPROACHES[1].glsl, O = fill(G.GL_ORBIT, 'z^n + c', '0', 2), H = G.GL_HEAD + G.GL_COLOUR + A + O;
const noGB = s => s.split('gB[0] = rd;').join(';').split('gB[0] = L;').join(';').split('gB[0] = nor;').join(';');
const T = G.GL_TAIL;
return 'lathe, state machine: ' + table({
  asis: H + T,
  'gB never written': H + noGB(T),
  'flat colour shading': H + sub(T, 'vec3 alb = surfaceColour(p, nor, t);', 'vec3 alb = vec3(0.8);'),
  'no trap calls': G.GL_HEAD + G.GL_COLOUR + A + O.split('trapStart();').join('').split('trapAdd(v, it);').join('') + T,
});
