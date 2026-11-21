"""Round 27, final: the defects of the checker "eyes" (A to O) and C of the checker "arithmetic", each looked for
again on dist/r27-final.html. Clicks and pointer moves are events made by script.

  python out/r27/final/mk/eyes.py wide     1400x950 dark: A, K, C/O, E, C, D, I, J, F, G, H, L, N, O, words
  python out/r27/final/mk/eyes.py phone    390x800 dark: A and B (B also on the frozen page)
  -> logs/eyes-<part>.txt, shots/eyes-*.png
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import run

H = run.HEAD + """
const notes = sel => [...document.querySelectorAll(sel)].filter(vis).map(e => e.textContent.trim()).filter(Boolean);
const tb = id => { const e = typeof id === 'string' ? $(id) : id; if (!e) return 'missing'; if (!vis(e)) return 'not shown'; const b = e.getBoundingClientRect(); return [Math.round(b.top), Math.round(b.bottom)]; };
const inWin = id => { const e = $(id); if (!vis(e)) return false; const b = e.getBoundingClientRect(); return b.top >= 0 && b.bottom <= innerHeight && b.left >= 0 && b.right <= innerWidth; };
const sentences = s => s.replace(/\\([^)]*\\)/g, '').split(/[.!?](?:\\s|$)/).filter(x => x.trim()).length;
"""
PIECES = "['stage', 'kleinGroup', 'ballsNote', 'ballsSize', 'ballsGrid', 'ballsDepth', 'ballsFrame']"
MENU = H + """
const b = $('apMenuBtn'); if (innerWidth < 700) { b.scrollIntoView({ block: 'center' }); await sleep(300); }
const y0 = Math.round(scrollY); b.click(); await sleep(450);
const rows = [...document.querySelectorAll('#rules .rule')], lb = $('rules').getBoundingClientRect();
return JSON.stringify({ step: 'menu open', scrollBefore: y0, scrollNow: Math.round(scrollY), win: [innerWidth, innerHeight], menu: tb('apPop'), list: tb('rules'), listHeight: Math.round(lb.height),
  approaches: rows.length, approachesWhollyInTheList: rows.filter(r => { const q = r.getBoundingClientRect(); return q.top >= lb.top - 0.5 && q.bottom <= lb.bottom + 0.5; }).length,
  heading: $('apgh-cousin') ? [$('apgh-cousin').textContent, tb('apgh-cousin')] : 'no heading', row: $('ap-balls') ? [$('ap-balls').innerText.replace(/\\n/g, ' / '), tb('ap-balls'), inWin('ap-balls')] : 'no row' });
"""
ROW = H + """
$('ap-balls').click(); await settle(); await sleep(300);
const P = %s, o = {}; for (const id of P) o[id] = [tb(id), inWin(id)];
return JSON.stringify({ step: 'right after the click on the row (no scrolling by the script)', mode: S.mode, group: S.k.group, t: S.k.bt, grid: S.k.bgrid, depth: S.k.bit, scrollY: Math.round(scrollY), win: [innerWidth, innerHeight],
  pieces: o, allInTheWindow: P.every(inWin), pictureColumn: tb(document.querySelector('.bench-main')), approachSection: tb('secApproach'), menuStillOpen: vis($('apPop')), pageWiderThanWindow: document.documentElement.scrollWidth > innerWidth });
""" % PIECES


def wide():
    P = run.OUT + '/shots/eyes-wd-'
    S = [run.UP]
    add = lambda js, shot=None, clip=None: S.append(dict(js=H + js, timeout=110, **({'shot': P + shot + '.png'} if shot else {}), **({'clip': clip} if clip and shot else {})))
    # K: the explanation box with the pointer on the row (after it stood on another approach)
    S.append(dict(js=MENU, shot=P + 'a0-menu-open.png'))
    add("""document.querySelector('#rules .rule[data-ap="bulb"] .name').dispatchEvent(new PointerEvent('pointerover', { bubbles: true, pointerType: 'mouse' })); await sleep(120);
      const a = $('apInfo').textContent.slice(0, 70);
      document.querySelector('#ap-balls .name').dispatchEvent(new PointerEvent('pointerover', { bubbles: true, pointerType: 'mouse' })); await sleep(120);
      return JSON.stringify({ K_boxOverAnApproach: a, K_boxOverTheRow: $('apInfo').textContent, K_boxShown: vis($('apInfo')), K_boxInWindow: inWin('apInfo') });""", 'k-pointer-on-the-row')
    # A: the landing
    S.append(dict(js=ROW, shot=P + 'a1-right-after-the-row.png'))
    # C (arithmetic) and the first half of O: the Approach section while Balls on balls is on show
    add("""const r = { C_approachSectionShown_balls: vis($('secApproach')), bodyClass: document.body.className, status: $('status').textContent };
      r.E_underThePicture = notes('section.score > *').map(s => s.slice(0, 150)); r.E_tableShown = vis($('card')); r.E_noteShown = vis($('ballsCardNote'));
      document.querySelector('section.score').scrollIntoView({ block: 'center' }); await sleep(200);
      return JSON.stringify(r);""", 'e-under-the-picture')
    # C, D (eyes): Colour and light
    add("""const sec = $('secColour'); sec.open = true; sec.scrollIntoView({ block: 'start' }); await sleep(250);
      const r = { CD_trapShape: S.colour.trap, CD_solidChoiceShown: vis($('col-solid')), D_examplesShown: vis($('trapExamples')), CD_notes: notes('#colDials .note') };
      S.colour.solid = 1; go(); await settle(); r.C_notes_withATrapSolidSetFromElsewhere = notes('#colDials .note'); r.solidChoiceShownThen = vis($('col-solid')); r.examplesShownThen = vis($('trapExamples'));
      r.threeTonesSentence = notes('#colDials .note').filter(t => /Three tones/.test(t));
      S.colour.solid = 2; go(); await settle(); r.C_notes_addedToTheSolid = notes('#colDials .note'); r.pictureStillDraws = $('status').textContent;
      S.colour.solid = 0; go(); await settle();
      return JSON.stringify(r);""", 'cd-colour-section')
    # I: colour by the direction of the last step, 3D then 2D; J: inside by orbit trap, 2D
    add("scrollTo(0, 0); S.colour.mode = 5; go(); await settle(); return JSON.stringify({ I_notes3D: notes('#colDials .note') });", 'i-last-step-3d', '#stage')
    add("S.flat = true; go(); await settle(); return JSON.stringify({ I_notes2D: notes('#colDials .note') });", 'i-last-step-2d', '#stage')
    add("S.colour.mode = 0; S.colour.inMode = 1; go(); await settle(); return JSON.stringify({ J_notes: notes('#colDials .note') });", 'j-inside-trap-2d', '#stage')
    # F: neighbours at 100
    add("S.colour.inMode = 0; S.flat = false; S.k.bt = 1; L.ballsFrame(); go(); await settle(); return JSON.stringify({ F_warn3D_square: $('ballsWarn').textContent, F_shown: vis($('ballsWarn')), status: $('status').textContent });", 'f-100-square-3d', '#stage')
    add("$('kleinPanel').scrollIntoView({ block: 'start' }); await sleep(250); return JSON.stringify({ F_panelAt100: 'see the picture', warnInWindow: inWin('ballsWarn') });", 'f-100-panel')
    add("S.k.bgrid = 2; L.ballsFrame(); go(); await settle(); return JSON.stringify({ F_warn3D_line: $('ballsWarn').textContent });", 'f-100-line-3d', '#stage')
    add("S.k.bgrid = 0; S.flat = true; go(); await settle(); return JSON.stringify({ F_warn2D: $('ballsWarn').textContent });", 'f-100-2d', '#stage')
    add("S.flat = false; S.k.bt = 1.02; L.ballsFrame(); go(); await settle(); const a = [$('ballsWarn').textContent, vis($('ballsWarn'))]; $('ballsFrame').click(); await settle(); return JSON.stringify({ F_at98: a, F_at98_afterFrameIt: [$('ballsWarn').textContent, vis($('ballsWarn'))] });")
    # G: the lowest stop of the depth dial
    add("""S.k.bt = 1.4; S.k.bit = 16; L.ballsFrame(); go(); await settle(); const e = $('ballsDepth'), n = $('ballsDepthNum');
      const r = { G_sliderMin: e.min, G_sliderMax: e.max, numberBox: !!n };
      if (n) { n.value = '1'; n.dispatchEvent(new Event('input', { bubbles: true })); n.dispatchEvent(new KeyboardEvent('keydown', { key: 'Enter', bubbles: true })); n.dispatchEvent(new Event('change', { bubbles: true })); await sleep(150); r.G_typed1Gives = S.k.bit; }
      e.value = e.min; e.dispatchEvent(new Event('input', { bubbles: true })); await settle(); r.G_atTheSliderMin = S.k.bit;
      return JSON.stringify(r);""", 'g-depth-lowest', '#stage')
    # H, L, N: the helps and the tooltip
    add("""S.k.bit = 16; go(); await settle();
      const helps = ['ballsSize', 'ballsGrid', 'ballsDepth'].map(id => { const h = $(id + 'Help') || $(id).closest('.dial, .field, div').querySelector('.help, .dial-help'); return h ? h.textContent.trim() : '?'; });
      return JSON.stringify({ L_helps: helps, L_sentencesInEach: helps.map(sentences), L_labels: ['ballsSize', 'ballsGrid', 'ballsDepth'].map(id => { const l = document.querySelector('label[for="' + id + '"]'); return l ? l.textContent.trim() : '?'; }),
        N_frameItTooltip: $('ballsFrame').title, note: $('ballsNote').textContent, noteSentences: sentences($('ballsNote').textContent),
        gridChoices: [...$('ballsGrid').options].map(o => o.textContent), sizeNow: $('ballsSize').value, depthNow: $('ballsDepth').value });""")
    # O: Learn from the two groups
    add("""const g = () => ({ approachSectionShown: vis($('secApproach')), tableShown: vis($('card')), tableNoteShown: vis($('ballsCardNote')), learn: !!S.learn, mode: S.mode, group: S.k.group });
      const r = {}; if (!$('mode-l')) return JSON.stringify({ O: 'no Learn tab on this page' });
      r.ballsBefore = g(); $('mode-l').click(); await sleep(700); r.learnFromBalls = g(); $('mode-k').click(); await settle(); r.backToBalls = g();
      $('kleinGroup0').click(); await settle(); r.firstGroup = g(); $('mode-l').click(); await sleep(700); r.learnFromFirstGroup = g(); $('mode-k').click(); await settle(); r.backToFirstGroup = g();
      $('kleinGroup1').click(); await settle(); r.ballsAgain = g();
      const same = (a, b) => ['approachSectionShown', 'tableShown', 'learn', 'mode'].every(k => a[k] === b[k]);
      r.O_learnTheSameFromBothGroups = same(r.learnFromBalls, r.learnFromFirstGroup) && r.backToBalls.approachSectionShown === r.backToFirstGroup.approachSectionShown;
      return JSON.stringify({ O: r });""")
    # the row chosen under Learn leaves Learn; the old group's warnings stay silent; Reset everything
    add("""$('mode-m').click(); await settle(); $('mode-l').click(); await sleep(600); const inLearn = !!S.learn;
      $('ap-balls').click(); await settle();
      const r = { rowUnderLearn: { wasInLearn: inLearn, learnNow: !!S.learn, mode: S.mode, group: S.k.group }, kleinTrouble: L.kleinTrouble ? L.kleinTrouble() : 'not on the handle', kleinSwallowed: L.kleinSwallowed ? L.kleinSwallowed() : 'not on the handle',
        oldWarningShown: vis($('kleinWarn')), startFromListShown: vis($('kleinPresetHost')), kleinReach: L.kleinReach ? L.kleinReach() : 'not on the handle' };
      $('resetAll').click(); await settle(); r.afterResetEverything = { mode: S.mode, group: S.k.group, bt: S.k.bt, bgrid: S.k.bgrid, bit: S.k.bit, approach: L.APPROACHES[S.approach].id };
      return JSON.stringify(r);""")
    # words: every text the new group shows, against the list of section 4
    add("""$('ap-balls').click(); await settle(); $('secColour').open = true; S.colour.mode = 5; S.colour.inMode = 1; S.k.bt = 1; go(); await settle();
      const texts = new Set(); const take = e => { if (e) for (const t of e.innerText.split('\\n')) if (t.trim()) texts.add(t.trim()); };
      take($('kleinGroup')); take($('ballsPart')); take($('apg-cousin')); take($('ballsCardNote')); $('ap-balls').dispatchEvent(new PointerEvent('pointerover', { bubbles: true, pointerType: 'mouse' })); await sleep(80); take($('apInfo'));
      for (const e of document.querySelectorAll('.note, .help, .dial-help')) if (/Balls on balls|the balls|chain/.test(e.textContent)) texts.add(e.textContent.trim());
      for (const e of document.querySelectorAll('#ballsPart [title], #apg-cousin [title], #kleinGroup [title]')) texts.add(e.title);
      S.flat = true; go(); await settle(); take($('ballsPart')); S.k.bgrid = 2; S.flat = false; go(); await settle(); take($('ballsPart'));
      const bad = /\\b(page|sheet|hinge|door|cone copy|critical|covers|winding|jacobian|stretch ratio|latitude|cusp|parabolic|loxodromic|moebius|möbius|mobius|lattice|discrete|limit set|pearl tree|skew pillow|twin_tri|kfix|maskit|picard|gaussian|eisenstein|subgroup|generator|conjugat\\w*|isometr\\w*|fuchsian|schottky)\\b/i;
      const all = [...texts], hits = all.filter(t => bad.test(t)).map(t => t.slice(0, 200));
      S.k.bgrid = 0; S.k.bt = 1.4; S.colour.mode = 0; S.colour.inMode = 0; go(); await settle();
      return JSON.stringify({ words_textsRead: all.length, words_forbiddenFound: hits, words_all: all });""")
    code, text, vals = run.shot(run.PAGE, S, 'eyes-wide', '1400x950', 'dark')
    return code, text, vals


def phone():
    out = []
    for tag, page in (('new', run.PAGE), ('old', run.BASE)):
        P = run.OUT + '/shots/eyes-ph-%s-' % tag
        S = [run.UP, dict(js=MENU, shot=P + 'b-menu-open.png')]
        if tag == 'new':
            S.append(dict(js=ROW, shot=P + 'a-right-after-the-row.png'))
        code, text, vals = run.shot(page, S, 'eyes-phone-' + tag, '390x800', 'dark')
        out.append((page, code, text, vals))
    return out


def show(lines, vals):
    for v in vals:
        try:
            d = json.loads(v)
        except ValueError:
            lines.append('  ' + str(v)[:300]); continue
        for k, w in d.items():
            lines.append('  %s: %s' % (k, json.dumps(w, ensure_ascii=False, indent=1) if isinstance(w, (list, dict)) else w))


if __name__ == '__main__':
    part = sys.argv[1] if len(sys.argv) > 1 else 'wide'
    os.makedirs(os.path.join(run.ENTRY, 'shots'), exist_ok=True)
    lines = []
    if part == 'wide':
        code, text, vals = wide()
        run.write('eyes-wide.log', text + 'exit %d\n' % code)
        lines.append('%s 1400x950 dark: exit %d, %s' % (run.PAGE, code, 'no console errors' if run.clean(text) else 'SEE logs/eyes-wide.log'))
        show(lines, vals)
        if code != 0:
            lines.append(text[-2500:])
    else:
        for page, code, text, vals in phone():
            lines.append('%s 390x800 dark: exit %d, %s' % (page, code, 'no console errors' if run.clean(text) else 'SEE THE LOG'))
            show(lines, vals)
            if code != 0:
                lines.append(text[-2500:])
    out = '\n'.join(lines) + '\n'
    run.write('eyes-%s.txt' % part, out); print(out)
