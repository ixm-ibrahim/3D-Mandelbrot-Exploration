# List every occurrence of some words in the built page with context. Run from the project root.
import re, sys
sys.stdout.reconfigure(encoding='utf-8')
page = open('dist/r12-check-page.html', encoding='utf-8').read()
# the page is wrapped for local viewing: find out whether the text is escaped
print('length', len(page))

def ctx(pat, skip=None, before=110, after=110, flags=0):
    n = 0
    for m in re.finditer(pat, page, flags):
        a, b = max(0, m.start() - before), min(len(page), m.end() + after)
        s = page[a:b].replace('\n', ' ')
        if skip and re.search(skip, page[max(0, m.start() - 30):m.end() + 30]):
            continue
        n += 1
        line = page.count('\n', 0, m.start()) + 1
        print('  [%d] ...%s...' % (line, s))
    print('  ->', n, 'shown for', pat)

what = sys.argv[1] if len(sys.argv) > 1 else 'lathe'
if what == 'lathe':
    ctx(r'Lathe', skip=r'Quaternion square \(Lathe\)|GL_LATHE|MATH\.lathe|uiLathe')
elif what == 'planes':
    ctx(r'[Pp]lanes (dial|at|to|set|=|is|of 1|1\b)')
    ctx(r'one setting|two settings|Planes\b[^.]{0,40}\b1\b')
elif what == 'dash':
    ctx('—', before=80, after=80)
    ctx('–', before=60, after=60)
elif what == 'internal':
    ctx(r'\b(mercator|softfold|axisbulb|pillowboth|pillowsmooth|GL_[A-Z_]+|uA\b|S\.param)', before=60, after=60)
else:
    ctx(what)
