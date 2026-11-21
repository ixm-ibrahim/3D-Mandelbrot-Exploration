"""Round 28, Track A, builder, test 5: pictures to LOOK at. Balls on balls with the neighbours past 100, in the 3D view
and the 2D view, on a wide window (1400x950) and a phone (390x800).

  python out/r28/dials/mk/looks.py [wide|phone] [light|dark] [set name ...]   -> out/r28/dials/shots/look-*.png, logs/looks-*.log

Each picture is reached the way a user reaches it: the row in the Approach list, then the dials (typed values), then
"Frame it". The whole window is saved (so the dials and the sentence show) and the stage alone.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run28 as run

TYPE = "const type = async (id, text) => { const n = $(id + 'Num'); n.focus(); n.value = text; n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); n.blur(); await sleep(60); };\n"
# name: (what to do after the row has been clicked)
SETS = {
    'p150': "await type('ballsSize', '150');",
    'p300': "await type('ballsSize', '300');",
    'p150-hex': "await type('ballsSize', '150'); S.k.bgrid = 1; go();",
    'p300-line': "await type('ballsSize', '300'); S.k.bgrid = 2; go();",
    'p400': "await type('ballsSize', '400');",
    'p101': "await type('ballsSize', '101');",
    'rho50-p200-touch': "await type('ballsRho', '50'); await type('ballsSize', '200');",
    'rho50-p190': "await type('ballsRho', '50'); await type('ballsSize', '190');",
    'rho50-p55': "await type('ballsRho', '50');",
    'rho25-p300': "await type('ballsRho', '25'); await type('ballsSize', '300');",
    'p1000': "await type('ballsSize', '1000');",
    'rho25-p400-touch': "await type('ballsRho', '25'); await type('ballsSize', '400');",
    'rho40-p250-touch': "await type('ballsRho', '40'); await type('ballsSize', '250');",
    'rho10-p1000-touch': "await type('ballsRho', '10'); await type('ballsSize', '1000');",
    'rho40-p240': "await type('ballsRho', '40'); await type('ballsSize', '240');",
    'depth3': "await type('ballsDepth', '3');",
    'p150-depth2': "await type('ballsSize', '150'); await type('ballsDepth', '2');",
}
DEFAULT = ['p150', 'p300']


def steps(names, tag):
    st = [run.UP, {'js': run.HEAD + "$('ap-balls').click(); await settle(); return 'row clicked: ' + $('status').textContent;", 'wait': 'done', 'timeout': 900}]
    for name in names:
        info = (" await settle(); return '%s' + ': p shows ' + $('ballsSizeNum').value + ', second sphere ' + $('ballsRhoNum').value + ', depth ' + S.k.bit + ', t ' + S.k.bt + ', rho ' + S.k.brho + ', reach ' + (+L.ballsReach().toFixed(3)) + ', cam dist ' + (+L.cam.dist.toFixed(3)) + ', drawing radius ' + S.view.bound + ', 2D height ' + (+S.v2.h.toFixed(3)) + ' | ' + $('status').textContent + ' | ' + warn();")
        # back to the defaults first, so that every set starts from the same place
        st.append({'js': run.HEAD + TYPE + "S.flat = false; document.querySelector('#ballsReset button').click(); await sleep(80); " + SETS[name] + " $('ballsFrame').click();" + info % (name + ' 3D'),
                   'wait': 'done', 'timeout': 900, 'shot': '%s/shots/look-%s-%s-3d-window.png' % (run.OUT, tag, name)})
        st.append({'js': "return 'stage';", 'shot': '%s/shots/look-%s-%s-3d.png' % (run.OUT, tag, name), 'clip': '#stage'})
        st.append({'js': run.HEAD + "S.flat = true; go(); $('ballsFrame').click();" + info % (name + ' 2D'),
                   'wait': 'done', 'timeout': 900, 'shot': '%s/shots/look-%s-%s-2d.png' % (run.OUT, tag, name), 'clip': '#stage'})
        st.append({'js': run.HEAD + "S.flat = false; go(); await settle(); return 'back in 3D';", 'wait': 'done', 'timeout': 900})
    return st


if __name__ == '__main__':
    a = sys.argv[1:]
    size = '390x800' if a and a[0] == 'phone' else '1400x950'
    if a and a[0] in ('wide', 'phone'):
        tag0 = a[0]; a = a[1:]
    else:
        tag0 = 'wide'
    theme = 'dark'
    if a and a[0] in ('light', 'dark'):
        theme = a[0]; a = a[1:]
    names = a or DEFAULT
    tag = tag0 + ('-light' if theme == 'light' else '')
    code, text, vals = run.shot(run.PAGE, steps(names, tag), 'looks-' + tag, size, theme)
    run.write('looks-%s-%s.log' % (tag, '+'.join(names)[:60]), text + 'exit %d\n' % code)
    for v in vals:
        print(v)
    print('exit', code, '| no console errors' if run.clean(text) else '| SEE THE LOG')
    if code != 0:
        print(text[-3000:])
