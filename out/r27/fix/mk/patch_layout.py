"""Round 27, fixer: make my copy of the builder's layout.py fit the page after the fixes. The Approach section is put
away while Balls on balls is on show, so the open menu with its row is measured BEFORE the row is clicked (from the
Mandelbrot view, where the menu is on the page), and the row is not marked there. Run once.
  python out/r27/fix/mk/patch_layout.py
"""
import io, os
HERE = os.path.dirname(os.path.abspath(__file__))
p = os.path.join(HERE, 'layout.py')
s = io.open(p, encoding='utf-8', newline='').read()


def rep(old, new):
    global s
    assert s.count(old) == 1, (s.count(old), old[:90])
    s = s.replace(old, new)


rep("""$('kleinPanel').scrollIntoView({ block: 'start' }); await sleep(200);
$('apMenuBtn').scrollIntoView({ block: 'center' }); await sleep(200);
$('apMenuBtn').click(); await sleep(300);""", """$('apMenuBtn').scrollIntoView({ block: 'center' }); await sleep(200);
$('apMenuBtn').dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 1 })); await sleep(300);""")
rep("""if (!$('apBallsRow').classList.contains('is-on')) bad.push('the row is not marked as the one on show');
return (bad.length ? 'PROBLEMS: ' + bad.join('; ') : 'open menu fits, the row is whole and marked') + ' | menu '""",
    """const list = $('rules').getBoundingClientRect(), whole = [...document.querySelectorAll('#rules .rule')].filter(r => { const b = r.getBoundingClientRect(); return b.top >= list.top - 0.5 && b.bottom <= list.bottom + 0.5; }).length;
if (whole < 4) bad.push('the list shows only ' + whole + ' whole approaches');
return (bad.length ? 'PROBLEMS: ' + bad.join('; ') : 'open menu fits, the row is whole, the list above it shows ' + whole + ' whole approaches') + ' | menu '""")
rep("""            steps = [run.UP,
                     dict(js=H + "$('apMenuBtn').click(); await sleep(200); $('ap-balls').click(); await sleep(150); await settle(); window.scrollTo(0, 0); await sleep(200); return 'Balls on balls on show, ' + $('status').textContent;", wait='done', timeout=600, shot=P + '-top.png'),
                     dict(js=H + "$('kleinPanel').scrollIntoView({ block: 'start' }); await sleep(300); return 'panel in view';", shot=P + '-panel.png'),
                     dict(js=CHECK),
                     dict(js=MENU, shot=P + '-menu.png'),
                     dict(js=H + "$('ap-balls').focus(); document.dispatchEvent(new PointerEvent('pointerdown', { bubbles: true })); await sleep(150); window.scrollTo(0, 0); $('flat').click(); await sleep(200); await settle(); return '2D view';", wait='done', timeout=600, shot=P + '-flat.png', clip='#stage')]""",
    """            steps = [run.UP,
                     dict(js=MENU, shot=P + '-menu.png'),
                     dict(js=H + "$('ap-balls').click(); await sleep(150); await settle(); await sleep(200); return 'Balls on balls on show, ' + $('status').textContent + '; right after the click: picture top ' + Math.round($('stage').getBoundingClientRect().top) + ', choice of group ' + Math.round($('kleinGroup').getBoundingClientRect().top) + ', first dial ' + Math.round($('ballsSize').getBoundingClientRect().top) + ' (window ' + innerHeight + ' high)';", wait='done', timeout=600, shot=P + '-after-the-row.png'),
                     dict(js=H + "$('kleinPanel').scrollIntoView({ block: 'start' }); await sleep(300); return 'panel in view';", shot=P + '-panel.png'),
                     dict(js=CHECK),
                     dict(js=H + "window.scrollTo(0, 0); $('flat').click(); await sleep(200); await settle(); return '2D view';", wait='done', timeout=600, shot=P + '-flat.png', clip='#stage')]""")
io.open(p, 'w', encoding='utf-8', newline='').write(s)
print('layout.py patched')
