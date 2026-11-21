"""Still pictures of the second hop toy's test page (headless Chrome, no GPU, its own profile), and the status text
after 72 moves (24 hops) for each rule.
    python out/r23/me/toy2shots.py   -> out/r23/me/toy2-*.png, toy2-sheet.png"""
import os, re, subprocess, sys, tempfile
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
PAGE = 'file:///C:/Users/IBRAHI~1/AppData/Local/Temp/claude/8398cb0dc43ad43f/e5663631-12dd-4d44-80a0-26a1ab33a9ae/scratchpad/preview/hop2-test.html'
CHROMES = [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
           r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]
SHOTS = [('lathe', 0, 28, ''), ('lathe', 1, 28, ''), ('lathe', 2, 28, ''), ('lathe', 3, 28, ''), ('oneplane', 1, 28, ''), ('twoplane', 1, 28, ''),
         ('along', 1, 28, ''), ('along', 3, 28, ''), ('twoplane', 72, 28, ''), ('along', 2, -40, '1')]


def main():
    chrome = next((c for c in CHROMES if os.path.exists(c)), None)
    if not chrome:
        sys.exit('no browser found')
    prof = tempfile.mkdtemp(prefix='toyshot-'); files = []
    for rule, moves, view, dark in SHOTS:
        out = os.path.join(HERE, 'toy2-%s-%d%s.png' % (rule, moves, '-dark' if dark else ''))
        url = PAGE + '?rule=%s&moves=%d&view=%d%s' % (rule, moves, view, '&dark=1' if dark else '')
        subprocess.run([chrome, '--headless=new', '--disable-gpu', '--user-data-dir=' + prof, '--hide-scrollbars', '--force-device-scale-factor=1', '--allow-file-access-from-files',
                        '--window-size=720,680', '--virtual-time-budget=5000', '--screenshot=' + out, url], timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(out, os.path.exists(out)); files.append(out)
    for rule in ('lathe', 'oneplane', 'twoplane', 'along'):
        r = subprocess.run([chrome, '--headless=new', '--disable-gpu', '--user-data-dir=' + prof, '--virtual-time-budget=8000', '--dump-dom', PAGE + '?rule=%s&moves=72' % rule],
                           timeout=120, capture_output=True, text=True, encoding='utf-8', errors='replace')
        m = re.search(r'<title>(.*?)</title>', r.stdout or '', re.S); print(rule, '->', m.group(1) if m else 'no title')
    ims = [Image.open(f).convert('RGB') for f in files if os.path.exists(f)]
    if ims:
        w, h = ims[0].size; cols = 2; rows = (len(ims) + 1) // 2; sheet = Image.new('RGB', (cols * w, rows * h), (255, 255, 255))
        for i, im in enumerate(ims):
            sheet.paste(im, ((i % cols) * w, (i // cols) * h))
        sheet.save(os.path.join(HERE, 'toy2-sheet.png')); print('sheet', sheet.size)


if __name__ == '__main__':
    main()
