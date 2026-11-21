"""Print the round 22 workflow's result, field by field, cut to a readable length.
    python out/r22/me/peek.py <path to .output> [max chars per field] [only this top.sub path, e.g. entry.check]"""
import json, sys


def show(v, pre, cap):
    if isinstance(v, dict):
        for k, x in v.items():
            show(x, pre + '.' + k if pre else k, cap)
    elif isinstance(v, list):
        if all(not isinstance(x, (dict, list)) for x in v):
            s = ' | '.join(str(x) for x in v); print('[%s] (%d items) %s%s' % (pre, len(v), s[:cap], ' ...' if len(s) > cap else ''))
        else:
            for i, x in enumerate(v):
                show(x, '%s[%d]' % (pre, i), cap)
    else:
        s = str(v); print('[%s] %s%s' % (pre, s[:cap], ' ... (+%d)' % (len(s) - cap) if len(s) > cap else ''))


def main():
    raw = open(sys.argv[1], encoding='utf-8', errors='replace').read(); cap = int(sys.argv[2]) if len(sys.argv) > 2 else 700
    i = raw.find('{'); data = None
    for start in (i, 0):
        try:
            data = json.loads(raw[start:]); break
        except Exception:
            try:
                data, _ = json.JSONDecoder().raw_decode(raw[start:]); break
            except Exception:
                pass
    if data is None:
        print('not JSON; first 3000 chars:'); print(raw[:3000]); return
    if isinstance(data, dict) and 'result' in data and isinstance(data['result'], (dict, str)):
        data = data['result'] if isinstance(data['result'], dict) else json.loads(data['result'])
    if len(sys.argv) > 3:
        for k in sys.argv[3].split('.'):
            data = data[k]
        show(data, sys.argv[3], cap)
    else:
        show(data, '', cap)


if __name__ == '__main__':
    main()
