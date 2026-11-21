# Shared by the patch scripts of this folder: read a frozen file of base21a, replace exact pieces, write the overlay copy.
import io, os, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
BASE = os.path.join(ROOT, 'base21a')
OVER = os.path.join(ROOT, 'out', 'r29', 'learn', 'overlay')
FRAG = os.path.join(HERE, 'frag')


def read(path):
    return io.open(path, encoding='utf-8').read().replace('\r\n', '\n')


def frag(name):
    """A piece of new code kept as a file of its own in mk/frag/ (so that it can be written as plain JavaScript)."""
    return read(os.path.join(FRAG, name)).rstrip('\n') + '\n'


class Patch:
    def __init__(self, rel):
        self.rel = rel
        self.s = read(os.path.join(BASE, rel))
        self.n = 0

    def rep(self, a, b, count=1):
        if self.s.count(a) != count:
            sys.exit('%s: expected %d of %r, found %d' % (self.rel, count, a[:90], self.s.count(a)))
        self.s = self.s.replace(a, b)
        self.n += 1

    def before(self, a, new):
        self.rep(a, new + a)

    def after(self, a, new):
        self.rep(a, a + new)

    def write(self):
        dst = os.path.join(OVER, self.rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        io.open(dst, 'w', encoding='utf-8', newline='\n').write(self.s)
        print('%s: %d places patched' % (self.rel, self.n))
