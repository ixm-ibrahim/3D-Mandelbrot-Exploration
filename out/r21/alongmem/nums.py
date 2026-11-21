"""python out/r21/alongmem/numbers.py name [name ...]     numbers for the named rules (bench:along etc. for the bench)
Results are added to out/r21/alongmem/numbers.json and printed as one line each."""
import os, sys, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import tools as T, myrules as R
M = T.M


def rule(name):
    return M.bench(name[6:]) if name.startswith('bench:') else R.get(name)


if __name__ == '__main__':
    names = [a for a in sys.argv[1:] if a != 'quick']; full = 'quick' not in sys.argv
    path = os.path.join(HERE, 'numbers.json')
    db = json.load(open(path)) if os.path.exists(path) else {}
    for nm in names:
        o = T.numbers(rule(nm), full=full); o['name'] = nm; db[nm] = o
        print(T.line(o), ' [%.0f s]' % o['secs']); sys.stdout.flush()
        json.dump(db, open(path, 'w'), indent=1)
