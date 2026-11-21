import io, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
path = os.path.join(ROOT, 'out', 'r4', 'page', 'make_smoke.py')
src = io.open(path, encoding='utf-8').read()
old = "const groups = L.APPROACH_GROUPS, A = L.APPROACHES;\n"
new = "$('mode-m').click(); await sleep(100);   // the Approach section is put away in the Kleinian view\n" + old
if src.count(old) != 1:
    sys.exit('no single match')
io.open(path, 'w', encoding='utf-8', newline='\n').write(src.replace(old, new))
print('ok')
