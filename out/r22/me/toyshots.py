"""Pictures of the hop toy's test page, taken with headless Chrome (no GPU, its own profile).
    python out/r22/me/toyshots.py   -> out/r22/me/toy-*.png and toy-sheet.png"""
import os, subprocess, sys, tempfile
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
CHROMES = [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
           r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]
SHOTS = [('lathe', 0, 28, ''), ('lathe', 1, 28, ''), ('oneplane', 1, 28, ''), ('oneplane', 24, 28, ''), ('along', 1, 28, ''), ('along', 24, 28, ''),
         ('alongonce', 24, -50, ''), ('along', 1, 28, '1')]


def main():
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    if not chrome:
        sys.exit('no browser found')
    prof = tempfile.mkdtemp(prefix='toyshot-'); files = []
    for rule, hops, view, dark in SHOTS:
        out = os.path.join(HERE, 'toy-%s-%d%s.png' % (rule, hops, '-dark' if dark else ''))
        url = 'http://localhost:8765/hop-toy-test.html?rule=%s&hops=%d&view=%d%s' % (rule, hops, view, '&dark=1' if dark else '')
        subprocess.run([chrome, '--headless=new', '--disable-gpu', '--user-data-dir=' + prof, '--hide-scrollbars', '--force-device-scale-factor=1',
                        '--window-size=720,580', '--virtual-time-budget=4000', '--screenshot=' + out, url], timeout=90,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(out, os.path.exists(out)); files.append(out)
    ims = [Image.open(f).convert('RGB') for f in files if os.path.exists(f)]
    if ims:
        w, h = ims[0].size; cols = 2; rows = (len(ims) + 1) // 2; sheet = Image.new('RGB', (cols * w, rows * h), (255, 255, 255))
        for i, im in enumerate(ims):
            sheet.paste(im, ((i % cols) * w, (i // cols) * h))
        sheet.save(os.path.join(HERE, 'toy-sheet.png')); print('sheet', sheet.size)


if __name__ == '__main__':
    main()
