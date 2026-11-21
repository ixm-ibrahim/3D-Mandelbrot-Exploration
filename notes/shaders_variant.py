"""Make a renamed copy of a shader file so two versions can sit in one test page.
  python notes/shaders_variant.py src.js out.js PREFIX     (GL_HEAD -> PREFIX_GL_HEAD, and so on)"""
import re, sys
src, out, pre = sys.argv[1:4]
s = open(src, encoding='utf-8').read()
for n in ['VERT', 'GL_HEAD', 'GL_ORBIT', 'GL_KLEIN', 'GL_TAIL', 'BLIT']:
    s = re.sub(r'const %s = ' % n, 'const %s_%s = ' % (pre, n), s)
open(out, 'w', encoding='utf-8', newline='\n').write(s)
