//#
const { L, G, fill, table } = window.T;
const A = L.APPROACHES[1].glsl, O = fill(G.GL_ORBIT, 'z^n + c', '0', 2), H = G.GL_HEAD + G.GL_COLOUR + A + O;
return 'lathe: ' + table({ 'march loop only': H + G.ALT.march, 'march + shading': H + G.ALT.m1, 'march + slope loop': H + G.ALT.m2, 'march + light loop': H + G.ALT.m3 });
