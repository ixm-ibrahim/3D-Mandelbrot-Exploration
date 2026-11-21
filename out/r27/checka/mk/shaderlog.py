"""Round 27, checker A: shader compile messages. Every shader the page compiles after it is up is caught (a hook on
compileShader that reads the compiler's message at once), on my page and on the frozen page, through the same clicks.
  python shaderlog.py -> ../logs/shaderlog.txt
"""
import json, os
import drive as D

HOOK = D.HEAD + """
const P = WebGL2RenderingContext.prototype, seen = [];
const oc = P.compileShader;
P.compileShader = function (s) {
  const r = oc.call(this, s);
  const src = this.getShaderSource(s) || '';
  seen.push({ len: src.length, balls: /uBGrid/.test(src), klein: /uKMu/.test(src) && /kde|kpearl/.test(src), frag: this.getShaderParameter(s, this.SHADER_TYPE) === this.FRAGMENT_SHADER,
    ok: this.getShaderParameter(s, this.COMPILE_STATUS), log: this.getShaderInfoLog(s) || '' });
  return r;
};
const ol = P.linkProgram;
P.linkProgram = function (p) { const r = ol.call(this, p); seen.push({ link: true, ok: this.getProgramParameter(p, this.LINK_STATUS), log: this.getProgramInfoLog(p) || '' }); return r; };
window.__seen = seen;
return 'hooked';
"""
WALK = D.HEAD + """
const out = {};
const take = () => { const a = window.__seen.splice(0); return { shaders: a.filter(x => !x.link).length, balls: a.filter(x => x.balls).length, links: a.filter(x => x.link).length,
  notOk: a.filter(x => !x.ok).length, messages: a.filter(x => x.log.trim()).map(x => (x.link ? 'link: ' : (x.balls ? 'balls ' : '') + 'shader: ') + x.log.trim().slice(0, 600)) }; };
$('mode-k').click(); await settle(); out.kleinian_first_group = take();
S.flat = true; go(); await settle(); S.flat = false; go(); await settle(); out.first_group_2d_and_back = take();
if ($('ap-balls')) {
  $('ap-balls').click(); await settle(); out.balls = take();
  S.flat = true; go(); await settle(); out.balls_2d = take(); S.flat = false; go(); await settle();
  S.cutOn = true; S.cut = 0.05; go(); await settle(); out.balls_cut = take(); S.cutOn = false; go(); await settle();
  S.k.bgrid = 1; go(); await settle(); S.k.bgrid = 2; go(); await settle(); S.k.bt = 1; go(); await settle(); out.balls_dials = take();
  const snap = L.takeSnapshot(); const a = await L.sampleSlice(snap, 0, 0, 2, 0, 8); L.releaseSnapshot(snap); out.balls_model_samples = take(); out.sample_ok = !!a;
}
$('mode-j').click(); await settle(); out.julia = take();
out.failed = L.R.failed || '';
return JSON.stringify(out);
"""
lines = []
for tag, page in (('new', D.PAGE), ('old', D.BASE)):
    code, vals, text = D.run(page, [D.UP, {'js': HOOK}, {'js': WALK, 'wait': 'done'}], 'shaderlog-' + tag)
    lines.append('%s page (%s), exit %d: %s' % (tag, page, code, json.dumps(vals[2] if len(vals) > 2 else text[-600:], ensure_ascii=False)))
    lines.append('   console: ' + (text[text.find('PAGE PROBLEMS'):][:800] if 'PAGE PROBLEMS' in text else 'no console errors'))
with open(os.path.join(D.LOGS, 'shaderlog.txt'), 'w', encoding='utf-8', newline='\n') as f:
    f.write('\n'.join(lines) + '\n')
print('\n'.join(lines))
