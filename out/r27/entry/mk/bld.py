"""Round 27, entry: build the test page from base18a plus every file in out/r27/entry/overlay/.
  python out/r27/entry/mk/bld.py [name]     (default name: r27-entry)  -> dist/<name>.html
It is the command of BUILD.txt, written out from the files that are in the overlay folder."""
import os, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
OV = os.path.join(ROOT, 'out', 'r27', 'entry', 'overlay')


def pairs():
    out = []
    for d, _, files in os.walk(OV):
        for f in sorted(files):
            rel = os.path.relpath(os.path.join(d, f), OV).replace('\\', '/')
            out.append('%s=out/r27/entry/overlay/%s' % (rel, rel))
    return sorted(out)


if __name__ == '__main__':
    name = sys.argv[1] if len(sys.argv) > 1 else 'r27-entry'
    assert name.startswith('r27-')
    cmd = [sys.executable, 'build.py', '--name', name, '--base', 'base18a', '--swap'] + pairs()
    print(' '.join(cmd[1:]))
    sys.exit(subprocess.call(cmd, cwd=ROOT))
