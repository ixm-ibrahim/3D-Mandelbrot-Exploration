"""layout-2: shorten the Kleinian entry names that do not fit the closed list (room 307 px on a phone at 13.5 px mono,
about 37 characters). Only the name changes; the copy before is out/r7/page/klein-presets.before.json.
Run once, then python notes/ui_embed.py."""
import io, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
PATH = os.path.join(ROOT, 'data', 'klein-presets.json')
NEW = {
    '0/1 cusp with the third map, sphere moved in depth': '0/1 cusp, third map: moved back',
    '0/1 cusp with the third map, sphere moved across and in depth': '0/1 cusp, third map: across and back',
    '0/1 cusp with the third map, sphere close to a wall': '0/1 cusp, third map: close to a wall',
    '1/2 cusp, through the gap under the upper wall': '1/2 cusp, gap under the upper wall',
    '1/2 cusp, small sphere in a narrow gap': '1/2 cusp, small sphere, narrow gap',
    '1/3 cusp, small sphere beside the large pearls': '1/3 cusp, beside the large pearls',
    '1/4 cusp, small sphere between the strings': '1/4 cusp, between the strings',
    'Leaning 30°, sphere lifted off the plane': 'Leaning 30°, lifted off the plane',
    'Leaning 30° with the third map, sphere moved across and in depth': 'Leaning 30°, third map: moved back',
}
raw = io.open(PATH, encoding='utf-8').read()
items = json.loads(raw)
done = 0
for p in items:
    if p['name'] in NEW:
        old = p['name']; p['name'] = NEW[old]; done += 1
        # change the text in place, so that nothing else in the file moves
        assert raw.count(json.dumps(old, ensure_ascii=False)) == 1, old
        raw = raw.replace(json.dumps(old, ensure_ascii=False), json.dumps(NEW[old], ensure_ascii=False))
assert json.loads(raw) == items
names = [p['name'] for p in items]
assert len(set(names)) == len(names)
io.open(PATH, 'w', encoding='utf-8', newline='\n').write(raw)
print('%d names changed; longest now %d characters: %s' % (done, max(map(len, names)), max(names, key=len)))
