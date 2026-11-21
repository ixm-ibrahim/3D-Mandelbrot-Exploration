import re, io
def rd(p): return io.open(p, encoding='utf-8').read()
sh = rd('src/js/30-shaders.js'); col = rd('src/js/25-colour.js'); rn = rd('src/js/40-render.js')
blit = sh[sh.index('const BLIT'):]
scene = sh[:sh.index('const BLIT')] + col
decl = set()
for m in re.finditer(r'uniform\s+\w+\s+([^;]+);', scene):
    for n in m.group(1).split(','):
        n = re.sub(r'\[.*', '', n.strip())
        if re.fullmatch(r'u[A-Z]\w*', n): decl.add(n)
setn = set(re.sub(r'\[.*', '', x) for x in re.findall(r"L\('([^']+)'\)", rn + col))
used = set(n for n in decl if len(re.findall(r'\b' + n + r'\b', scene)) > 1)
print('declared', len(decl), 'set', len(setn))
print('declared, never set:', sorted(decl - setn))
print('set, never declared:', sorted(setn - decl))
print('declared, never used in shader text:', sorted(decl - used))
bd = set()
for m in re.finditer(r'uniform\s+\w+\s+([^;]+);', blit):
    for n in m.group(1).split(','):
        if re.fullmatch(r'u[A-Z]\w*', n.strip()): bd.add(n.strip())
bs = set(re.findall(r"blitP\.l\('([^']+)'\)", rn))
print('blit declared-not-set:', sorted(bd - bs), 'set-not-declared:', sorted(bs - bd))
