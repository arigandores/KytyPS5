"""rt143_pair.py - Red Team s143 step 1 (HPP-298): the profile-143 path of sc143.py (pair SCENE_OK, census rows, forms)
on REAL logs of session 142, without the game.  Reads C:/kyty/s142 logs in place (binary, streaming via sc143.scan);
writes only into C:/kyty/s143/step1/fxroot (small copies: glitch, idx, sheet, mp4 and a mapped step2/times.txt).
Scenarios (LEVELS patched; tags of s143):
  S1 pair v143_01 <- v142, w143_01 <- w142, level underwater_aerial_garden: expect PENDING_SHEET, with viewed -> YES
  S2 mixed: v143_02 <- c142_01 (bumper_enemy_snowy_canyon), w143_02 <- w142 (Sky Garden W): expect NO, rows that fail
  S3 W stopped early: v143_03 <- v142, w143_03 <- w142 with attempts[0].hold_s 299.0: expect NO by the W hold row only
  S4 V missing: w143_04 <- w142, no v143_04: expect NO
  S5 census: v143_05..v143_10 <- c142_05..c142_10 - the per-entry block must equal the s142 block of the same log
     (tag renamed; the EXTRA K3-120 line dropped)
  S6 W hold 305 s: v143_01 pair with w hold_s 305: YES by the letter, info line NO (305)
ASCII output.
"""
import copy
import hashlib
import json
import os
import shutil
import sys

sys.path.insert(0, 'C:/kyty/s143')
import sc143 as S

S142 = 'C:/kyty/s142'
FX = 'C:/kyty/s143/step1/fxroot'
SKY = 'underwater_aerial_garden'
C142 = dict(S.CENSUS142)
PRED142 = 'C:/kyty/s142/pred/02_sc142.md'


def scans(tag):
    lp, sp, ep = ['%s/%s' % (S142, x % tag) for x in ('log_%s.txt', 'stdout_%s.txt', '%s.stdout.txt')]
    return tuple(S.scan(p) if os.path.isfile(p) else None for p in (lp, sp, ep))


def js_as(src, newtag, hold_s=None):
    js = copy.deepcopy(json.load(open('%s/%s.json' % (S142, src), encoding='utf-8')))
    env = js.get('env') or {}
    if 'KYTY_REC' in env:
        env['KYTY_REC'] = env['KYTY_REC'].replace('rec_%s.mp4' % src, 'rec_%s.mp4' % newtag)
    if hold_s is not None:
        js['attempts'][0]['hold_s'] = hold_s
    return js


def main():
    out = []
    os.makedirs(FX + '/step2', exist_ok=True)
    levels = list(S.LEVELS)
    levels[0] = SKY
    levels[1] = 'bumper_enemy_snowy_canyon'
    levels[2] = SKY
    levels[3] = SKY
    for i, t in enumerate(('c142_05', 'c142_06', 'c142_07', 'c142_08', 'c142_09', 'c142_10')):
        levels[4 + i] = C142[t]
    levels = tuple(levels)
    pairs = tuple(('v143_%02d' % (i + 1), 'w143_%02d' % (i + 1), lv) for i, lv in enumerate(levels))
    S.profile(dict(LEVELS=levels, PAIRS=pairs, CENSUS=tuple((v, lv) for v, _, lv in pairs),
                   SEQ=tuple(t for v, w, _ in pairs for t in (v, w)), V_TAGS=tuple(v for v, _, _ in pairs),
                   W_TAGS=tuple(w for _, w, _ in pairs), PRED_PATH=PRED142.replace('\\', '/')))
    pred_sha = S.sha_file(PRED142)
    # small files of the V tags built from v142 / c142_NN
    times = []
    src_of = {'v143_01': 'v142', 'v143_02': 'c142_01', 'v143_03': 'v142'}
    for i, t in enumerate(('c142_05', 'c142_06', 'c142_07', 'c142_08', 'c142_09', 'c142_10')):
        src_of['v143_%02d' % (5 + i)] = t
    for nt, src in sorted(src_of.items()):
        for a, b in (('glitch_%s.txt', 'glitch_%s.txt'), ('rec_%s.mp4.idx', 'rec_%s.mp4.idx'),
                     ('sheet_%s.png', 'sheet_%s.png')):
            if os.path.isfile('%s/%s' % (S142, a % src)):
                shutil.copyfile('%s/%s' % (S142, a % src), '%s/%s' % (FX, b % nt))
        if nt in ('v143_01', 'v143_03'):
            dst = '%s/rec_%s.mp4' % (FX, nt)
            if not os.path.isfile(dst):
                shutil.copyfile('%s/rec_%s.mp4' % (S142, src), dst)
            for line in open('%s/step2/times.txt' % S142, encoding='utf-8', errors='replace'):
                if (' go142a %s sheet ' % src) in line or (' go142a %s s51_vidglitch ' % src) in line:
                    times.append(line.replace('go142a %s ' % src, 'go143a %s ' % nt)
                                 .replace('_%s.' % src, '_%s.' % nt))
    open(FX + '/step2/times.txt', 'w', encoding='utf-8').write(''.join(times))
    sc = {}
    for t in ('v142', 'w142', 'c142_01') + tuple('c142_%02d' % k for k in range(5, 11)):
        sc[t] = scans(t)
        out.append('SCAN %s log sha %s' % (t, sc[t][0]['sha256'][:16] if sc[t][0] else 'MISSING'))

    def ent(nt, src, hold_s=None):
        lv = S.level_of(nt)
        js = js_as(src, nt, hold_s)
        return S.build(nt, lv, js, sc[src][0], sc[src][1], sc[src][2], FX, pred_sha)

    def show(name, v, w, pair, sheet, expect):
        word, rows = S.scene_ok(v, w, sheet, pair)
        fails = [r[0] for r in rows if not r[1]]
        out.append('%s %s sheet=%s -> %s (expect %s) %s; failing rows: %s' % (
            name, pair[2], sheet, word, expect, 'OK' if word == expect else 'MISMATCH', ' | '.join(fails) or 'none'))
        return word
    v1 = ent('v143_01', 'v142')
    w1 = ent('w143_01', 'w142')
    show('S1a', v1, w1, pairs[0], None, 'PENDING_SHEET')
    show('S1b', v1, w1, pairs[0], 'viewed', 'YES')
    show('S1c', v1, w1, pairs[0], 'not-viewed', 'NO')
    v2 = ent('v143_02', 'c142_01')
    w2 = ent('w143_02', 'w142')
    show('S2', v2, w2, pairs[1], 'viewed', 'NO')
    v3 = ent('v143_03', 'v142')
    w3 = ent('w143_03', 'w142', hold_s=299.0)
    show('S3', v3, w3, pairs[2], 'viewed', 'NO')
    w4 = ent('w143_04', 'w142')
    show('S4', None, w4, pairs[3], 'viewed', 'NO')
    w6 = ent('w143_01', 'w142', hold_s=305.0)
    show('S6', v1, w6, pairs[0], 'viewed', 'YES')
    out.append('S6 info: W hold_s %s -> info line would print %s' % (
        w6['hold_s'], 'yes' if w6['hold_s'] >= S.HOLD_W_HARNESS_S else 'NO (%s)' % w6['hold_s']))
    # S5: census blocks against the s142 summary blocks
    ref = open('C:/kyty/s142/step4/summary142_viewed.txt', 'rb').read().decode('ascii').replace('\r\n', '\n').split('\n')
    blocks = {}
    cur = None
    for line in ref:
        if line.startswith('TAG '):
            cur = line.split()[1]
            blocks[cur] = [line]
        elif line.startswith('  ') and cur is not None and not line.startswith('  PASS') and not line.startswith('  FAIL'):
            blocks[cur].append(line)
        else:
            cur = None
    ents5 = []
    for k, t in enumerate(('c142_05', 'c142_06', 'c142_07', 'c142_08', 'c142_09', 'c142_10')):
        nt = 'v143_%02d' % (5 + k)
        e = ent(nt, t)
        ents5.append(e)
        new = [x.replace(nt, t) for x in S.fmt_entry(e) if 'executor variant, the s142 census hold' not in x]
        old = blocks.get(t, [])
        # the s142 block holds no sheet-sha line for census tags; the V-tag block of s143 prints one (V_TAGS)
        new_cmp = [x for x in new if not x.startswith('  sheet and video sha256')]
        same = new_cmp == old
        out.append('S5 %s as %s: block lines %d vs s142 %d -> %s' % (t, nt, len(new_cmp), len(old),
                                                                      'IDENTICAL' if same else 'DIFFERENT'))
        if not same:
            for a, b in zip(old, new_cmp):
                if a != b:
                    out.append('   s142: %s' % a[:220])
                    out.append('   s143: %s' % b[:220])
        out.append('S5 %s k3h (letter) %d, k3h120 (variant) %d, k2 %s' % (
            nt, len(e['derive']['k3h']), len(e['derive']['k3h120']), e['derive']['k2'] or 'none'))
    # B5a over the full V hold vs the first 120 s (the s142 census window): on the V of Sky Garden
    d = v1['derive']
    out.append('V v142 as v143_01: frames after first %d, %.1f s; K2 %s; K3 hold %d; K3 hold within 120 s %d' % (
        d['frames_after_first'], d['dt_after_first_us'] / 1e6, d['k2'] or 'none', len(d['k3h']), len(d['k3h120'])))
    print('\n'.join(out))
    return 0


if __name__ == '__main__':
    sys.exit(main())
