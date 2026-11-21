"""Build the kleinian test pages.

  python out/r4/kleinian/mk.py                 -> dist/r4-kleinian.html: base4 + out/r4/kleinian/GL_KLEIN.js pasted into a copy
                                                  of base4's 30-shaders.js + the stand-in 25-colour.js (trap-solid uniforms)
  python out/r4/kleinian/mk.py NAME FILE       -> dist/r4-kleinian-NAME.html with the GL_KLEIN statement taken from FILE
  python out/r4/kleinian/mk.py --base          -> dist/r4-kleinian-base.html: base4 untouched (for comparisons)
  extra arguments after "--" go to build.py (for instance --use src/js/25-colour.js)
"""
import os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))

def splice(klein_file, out_file):
    src = open(os.path.join(ROOT, 'base4', 'js', '30-shaders.js'), encoding='utf-8').read()
    new = open(klein_file, encoding='utf-8').read().strip()
    pat = re.compile(r"const GL_KLEIN = `.*?`;", re.S)
    assert len(pat.findall(src)) == 1 and len(pat.findall(new)) == 1 and pat.fullmatch(new), "GL_KLEIN statement not found exactly once"
    with open(out_file, 'w', encoding='utf-8', newline='\n') as f:
        f.write(pat.sub(lambda m: new, src))

def main():
    args = sys.argv[1:]
    extra = []
    if '--' in args:
        i = args.index('--'); extra = args[i + 1:]; args = args[:i]
    if args and args[0] == '--base':
        cmd = ['--name', 'r4-kleinian-base', '--base', 'base4']
    else:
        name = 'r4-kleinian' + ('-' + args[0] if args else '')
        kf = os.path.join(ROOT, args[1]) if len(args) > 1 else os.path.join(HERE, 'GL_KLEIN.js')
        out = os.path.join(HERE, '30-shaders%s.js' % ('-' + args[0] if args else ''))
        splice(kf, out)
        swaps = ['js/30-shaders.js=' + '/'.join(os.path.relpath(out, ROOT).split(os.sep))]
        if not any('25-colour' in e for e in extra):
            swaps.append('js/25-colour.js=out/r4/kleinian/25-colour.js')
        cmd = ['--name', name, '--base', 'base4', '--swap'] + swaps
    r = subprocess.run([sys.executable, os.path.join(ROOT, 'build.py')] + cmd + extra, cwd=ROOT)
    sys.exit(r.returncode)

if __name__ == '__main__':
    main()
