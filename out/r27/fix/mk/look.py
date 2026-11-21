"""Round 27, fixer: pictures to look at after the fixes of the checker "eyes" (C, D, E, F, I, J, K) and what the page
says in each place.
  python out/r27/fix/mk/look.py <page> <tag> [size] [theme]   -> shots/look-<tag>-*.png, logs/look-<tag>.txt
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

H = run.HEAD + """
const vis = e => !!e && e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
const notes = sel => [...document.querySelectorAll(sel)].filter(vis).map(e => e.textContent.trim()).filter(Boolean);
const pickSel = (id, v) => { const e = $(id); e.value = String(v); e.dispatchEvent(new Event('change', { bubbles: true })); };
"""


def steps(tag):
    P = 'out/r27/fix/shots/look-%s-' % tag
    S = []
    add = lambda js, shot=None, clip=None: S.append(dict(js=H + js, timeout=600, **({'shot': P + shot + '.png'} if shot else {}), **({'clip': clip} if clip and shot else {})))
    S.append(run.UP)
    # K: the explanation beside the open list with the pointer on the row
    add("""$('apMenuBtn').dispatchEvent(new MouseEvent('click', { bubbles: true, detail: 1 })); await sleep(300);
      document.querySelector('#rules .rule[data-ap="bulb"] .name').dispatchEvent(new PointerEvent('pointerover', { bubbles: true, pointerType: 'mouse' })); await sleep(100);
      const a = $('apInfo').textContent.slice(0, 60);
      document.querySelector('#ap-balls .name').dispatchEvent(new PointerEvent('pointerover', { bubbles: true, pointerType: 'mouse' })); await sleep(100);
      return JSON.stringify({ K_overMandelbulb: a, K_overTheRow: $('apInfo').textContent, shown: vis($('apInfo')) });""", 'k-hover-on-the-row')
    add("""$('apPop').dispatchEvent(new PointerEvent('pointerleave', { pointerType: 'mouse' })); await sleep(50); const gone = !vis($('apInfo'));
      $('ap-balls').click(); await settle(); await sleep(200);
      return JSON.stringify({ K_afterLeaving_boxGone: gone, mode: S.mode, group: S.k.group, approachSectionShown: vis($('secApproach')), bodyClass: document.body.className });""", 'start')
    # E: the table under the picture
    add("""document.querySelector('section.score').scrollIntoView({ block: 'center' }); await sleep(200);
      return JSON.stringify({ E_scoreSectionSays: notes('section.score > *').map(s => s.slice(0, 140)), cardShown: vis($('card')) });""", 'e-table-under-the-picture')
    # C, D: Colour and light
    add("""const sec = $('secColour'); sec.open = true; sec.scrollIntoView({ block: 'start' }); await sleep(200);
      const r = { CD_solidChoiceShown: vis($('col-solid')), examplesShown: vis($('trapExamples')), notes: notes('#colDials .note') };
      S.colour.solid = 1; go(); await settle(); r.withSolidSetFromElsewhere = notes('#colDials .note'); r.solidChoiceShownThen = vis($('col-solid')); r.thicknessShown = vis($('col-thick'));
      S.colour.trap = 7; go(); await settle(); r.withThreeTones = notes('#colDials .note'); S.colour.trap = 5; S.colour.solid = 0; go(); await settle();
      return JSON.stringify(r);""", 'cd-colour-section')
    # I: colour by the direction of the last step, 3D and 2D
    add("scrollTo(0, 0); S.colour.mode = 5; go(); await settle(); return JSON.stringify({ I_notes3D: notes('#colDials .note') });", 'i-last-step-3d', '#stage')
    add("S.flat = true; go(); await settle(); return JSON.stringify({ I_notes2D: notes('#colDials .note') });", 'i-last-step-2d', '#stage')
    # J: inside colours by orbit trap, 2D
    add("S.colour.mode = 0; S.colour.inMode = 1; go(); await settle(); return JSON.stringify({ J_notes: notes('#colDials .note') });", 'j-inside-trap-2d', '#stage')
    # F: neighbours at 100
    add("S.colour.inMode = 0; S.flat = false; S.k.bt = 1; L.ballsFrame(); go(); await settle(); return JSON.stringify({ F_warn3D_square: $('ballsWarn').textContent, status: $('status').textContent });", 'f-100-square-3d', '#stage')
    add("$('kleinPanel').scrollIntoView({ block: 'start' }); await sleep(200); return 'panel at 100';", 'f-100-panel')
    add("S.k.bgrid = 2; L.ballsFrame(); go(); await settle(); return JSON.stringify({ F_warn3D_line: $('ballsWarn').textContent });", 'f-100-line-3d', '#stage')
    add("S.k.bgrid = 0; S.flat = true; go(); await settle(); return JSON.stringify({ F_warn2D: $('ballsWarn').textContent });", 'f-100-2d', '#stage')
    add("S.k.bgrid = 1; S.flat = false; L.ballsFrame(); go(); await settle(); return JSON.stringify({ F_warn3D_hex: $('ballsWarn').textContent });", 'f-100-hex-3d', '#stage')
    add("S.k.bgrid = 0; S.k.bt = 1.02; L.ballsFrame(); go(); await settle(); return JSON.stringify({ at98: $('ballsWarn').textContent, shown: vis($('ballsWarn')) });", 'f-98-square-3d', '#stage')
    # G: the depth dial's lowest stop
    add("""S.k.bt = 1.4; S.k.bit = 16; L.ballsFrame(); go(); await settle(); const e = $('ballsDepth'), n = $('ballsDepthNum');
      const r = { G_sliderMin: e.min, sliderMax: e.max };
      if (n) { n.value = '1'; n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); n.dispatchEvent(new Event('change', { bubbles: true })); await sleep(100); r.typed1Gives = S.k.bit; }
      e.value = e.min; e.dispatchEvent(new Event('input', { bubbles: true })); await settle(); r.atSliderMin = S.k.bit;
      return JSON.stringify(r);""", 'g-depth-lowest', '#stage')
    # L, N: the helps and the tooltip
    add("""S.k.bit = 16; go(); await settle();
      return JSON.stringify({ L_helps: ['ballsSize', 'ballsGrid', 'ballsDepth'].map(id => { const h = $(id + 'Help') || $(id).closest('.dial, .field, div').querySelector('.help, .dial-help'); return h ? h.textContent : '?'; }),
        N_frameTitle: $('ballsFrame').title, stepHelp: [...document.querySelectorAll('#qDials .help, #qDials .dial-help')].map(e => e.textContent).filter(t => /Balls on balls/.test(t)) });""")
    # O: Learn from the two groups
    add("""const g = () => ({ approachHiddenAttr: $('secApproach').hidden, approachShown: vis($('secApproach')), name: $('apMenuName').textContent, tableShown: vis($('card')), tableNote: vis($('ballsCardNote')) });
      const r = {}; if (!$('mode-l')) return JSON.stringify({ O: 'no Learn tab on this page' });
      $('mode-l').click(); await sleep(600); r.learnFromBalls = g(); $('mode-k').click(); await settle(); r.backToBalls = { group: S.k.group, learn: !!S.learn, tableNote: vis($('ballsCardNote')) };
      $('kleinGroup0').click(); await settle(); r.firstGroup = g(); $('mode-l').click(); await sleep(600); r.learnFromFirstGroup = g(); $('mode-k').click(); await settle();
      $('kleinGroup1').click(); await settle(); r.ballsAgain = g();
      return JSON.stringify({ O: r });""")
    return S


if __name__ == '__main__':
    page, tag = sys.argv[1], sys.argv[2]
    size = sys.argv[3] if len(sys.argv) > 3 else '1400x950'; theme = sys.argv[4] if len(sys.argv) > 4 else 'dark'
    code, text, vals = run.shot(page, steps(tag), 'look-' + tag, size, theme)
    lines = ['%s %s %s: exit %d, %s' % (page, size, theme, code, 'no console errors' if 'no console errors' in text else 'SEE THE LOG')]
    for v in vals:
        try:
            d = json.loads(v)
        except ValueError:
            lines.append(str(v)[:300]); continue
        for k, w in d.items():
            lines.append('  %s: %s' % (k, json.dumps(w, ensure_ascii=False, indent=1) if isinstance(w, (list, dict)) else w))
    out = '\n'.join(lines) + '\n'
    run.write('look-%s.txt' % tag, out); print(out)
    if code != 0:
        print(text[-2500:])
