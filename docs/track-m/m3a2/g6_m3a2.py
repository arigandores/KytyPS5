"""Track M link M3a2 (HPP-861; ROADMAP s122 item 778 (d)(6), port of M3a g6_m3a.py): G6 - the patch by choice on MS2.  One V of Sky
Garden m3w2_g6 on MS2 c630327b in the FORM F of P24 (KYTY_GAME_PATCH = patches/PPSA21564_pvar.txt of the seal, KYTY_POKE=27e46c:909090909090, the keys line of
the seal = the keys of 02_p4.md, hold 330 s, video).  The reading of track P is IMPORTED, not copied: C:/kyty/p283/p24/scp24.py (sha256
SCP24_SHA; it loads the sealed scp19.py and scp15.py) - its driver m24(), the X arm ia_A3 of P24 with its stop-check against qa_A2 of
P21 (active_x24), G1' of item 312 (d)(1) with the gates of item 326 (scp19.g1p) and RATCHET / R2 (scp15.g2) are the sealed code.  This
file only rebinds (seal pred.md section 7):
  - TAG_V = ('m3w2_g6',) on the instance of X and on the scp19 module; 'm3w2_g6' joins FILE_TAGS of scp24 (the env / poke / GamePatch rows of
    the form F); the run of m3w2_g6 is read from the root C:/kyty/m657/m3a2 with the seal C:/kyty/m657/m3a2/pred.md (its lines 'pvar binary:'
    = MS2, 'patch file:', 'keys:'); the run of X from the root and seal of P24;
  - env_same of the pair X / m3w2_g6: the root folder of the harness (C:\\kyty\\p283\\p24 / C:\\kyty\\m657\\m3a2, both slash forms) is the
    same token in both env before the sealed comparison (the gate files KYTY_GATE_FILE / KYTY_SAMPLE_GATE live in the root);
  - one V instead of two: the sealed g1_word over one outcome prints TWO_OF_TWO when it is SPEED_OK - read as ONE_OF_ONE; the sealed
    ratchet_word over one flag prints NONE / DEFECT (with the qa band) - read as is.
  - the files the sealed run_of reads under the root (glitch_m3w2_g6.txt, sheet_m3w2_g6.png, eboot_m3w2_g6.txt) are made by 'stage' from
    runs/m3w2_g6 (copies) and the sha256 of games/PPSA21564-app/eboot.bin.
The words for M3b: G6 SPEED_OK / OVERRUN / SPEED_LOW / NOT_DETERMINED (the G1' outcome of m3w2_g6 and the RC2 flag), RATCHET NONE /
DEFECT / UNDETERMINED / NOT_EVALUABLE; 'G6 PASS' printed only when SPEED_OK and RATCHET NONE (the letter of item 778 (d)(6)).
  python g6_m3a2.py stage                 make the three files (outside the lock)
  python g6_m3a2.py run [--v <tag>] [--root <dir>] [--seal <file>]   the reading (default m3w2_g6, C:/kyty/m657/m3a2, pred.md)
  python g6_m3a2.py regress               the same driver on iv_5 of P24 (root and seal of P24, no rebinding of the root): its speed
                                         1.0001 SPEED_OK and RATCHET flag False of verdict_p24.txt are reproduced -> ALL OK
ASCII only.  Refuses under the lock (exit 3) and with the stop file C:/kyty/m657/STOP (exit 4)."""
import hashlib
import importlib.util
import os
import re
import shutil
import sys

if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('lock held - exit 3')
    sys.exit(3)
if os.path.exists('C:/kyty/m657/STOP'):
    print('STOP - exit 4')
    sys.exit(4)
G = 'C:/kyty/m657/m3a2'
SEAL = G + '/pred.md'
SCP24_PATH = 'C:/kyty/p283/p24/scp24.py'
SCP24_SHA = None  # filled below from the file; the seal names it (section 7) and test_g6 checks it
TAG = 'm3w2_g6'
EBOOT = 'C:/kyty/KytyPS5/ps5 em/games/PPSA21564-app/eboot.bin'
ROOTS = ('C:\\kyty\\m657\\m3a2', 'C:/kyty/m657/m3a2')
P24ROOTS = ('C:\\kyty\\p283\\p24', 'C:/kyty/p283/p24')


def sha_file(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 22), b''):
            h.update(c)
    return h.hexdigest()


def load24():
    spec = importlib.util.spec_from_file_location('scp24_m3a2', SCP24_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stage(root=G, tag=TAG):
    d = os.path.join(root, 'runs', tag)
    out = []
    for src, dst in ((os.path.join(d, 'glitch.txt'), 'glitch_%s.txt' % tag), (os.path.join(d, 'sheet_%s.png' % tag), 'sheet_%s.png' % tag)):
        if os.path.exists(src):
            shutil.copyfile(src, os.path.join(root, dst))
            out.append('%s %s' % (dst, sha_file(os.path.join(root, dst))[:16]))
        else:
            out.append('%s MISSING' % dst)
    e = sha_file(EBOOT)
    with open(os.path.join(root, 'eboot_%s.txt' % tag), 'w', encoding='ascii', newline='\n') as f:
        f.write('%s eboot.bin\n' % e)
    out.append('eboot_%s.txt %s' % (tag, e[:16]))
    print('G6 stage: ' + '; '.join(out))


def norm_json(js, roots, to):
    if not js:
        return js
    js = dict(js)
    env = dict(js.get('env') or {})
    for k, v in env.items():
        for r in roots:
            v = v.replace(r, to)
        env[k] = v
    js['env'] = env
    cmd = []
    for a in js.get('cmdline') or []:
        a = str(a)
        for r in roots:
            a = a.replace(r, to)
        cmd.append(a)
    js['cmdline'] = cmd
    return js


def drive(vtag, vroot, vseal, out, rebind=True):
    P = load24()
    M = P.m24()
    xl = []
    o = P.subst24(out)
    ref = P.ref_of('p24', xl.append)
    x, x_ok = P.active_x24(M, P.ROOT, P.PRED_PATH, ref, xl.append, P.REF_LABEL, P.ROOT)
    xl.append(M.NEWB + 'X of the pairs (item 326 (e)(2)): %s, its stop-check %s' % (x, 'PASS' if x_ok else 'FAIL'))
    S = M.inst(x)
    S.TAG_V = (vtag,)
    M.TAG_V = (vtag,)
    if rebind:
        P.FILE_TAGS = tuple(P.FILE_TAGS) + (vtag,)
        es1 = S.env_same

        def env_same(ja, ta, jb, tb, *a, **k):
            return es1(norm_json(ja, ROOTS + P24ROOTS, '<ROOT>'), ta, norm_json(jb, ROOTS + P24ROOTS, '<ROOT>'), tb, *a, **k)
        S.env_same = env_same
    runs = {x: S.run_of(x, P.ROOT, P.PRED_PATH), vtag: S.run_of(vtag, vroot, vseal)}
    s1 = S.stage1_arms()
    lines = []
    a, rep, old = M.g1p(S, vroot, vseal, lines.append, runs, s1, ref=ref, x_ok=x_ok, xlines=xl)
    b, r2 = S.g2(vroot, vseal, out=lines.append, runs=runs)
    for line in lines:
        o(line)
    r = rep.get(vtag) or {}
    oc = r.get('oc') if isinstance(r, dict) else None
    if oc is None:
        m = [l for l in lines if l.startswith("G1' VERDICT_PAIR ") and l.rstrip().endswith(tuple(['SPEED_OK', 'OVERRUN', 'SPEED_LOW',
                                                                                                    'NOT_EVALUABLE', 'TAG_UNDETERMINED',
                                                                                                    'NAMES_UNDETERMINED', 'CLOCK_UNDETERMINED',
                                                                                                    'PATCH_INACTIVE']))]
        oc = m[-1].split()[-1] if m else None
    speed = None
    for l in lines:
        mm = re.match(r"^G1' speed %s ([0-9.]+) " % re.escape(vtag), l)
        if mm:
            speed = float(mm.group(1))
    vr = runs.get(vtag)
    rows_bad = [n for n, c, v in (vr or {}).get('rows', []) if not c] if vr else ['not made']
    rf = [l for l in lines if l.startswith('RATCHET %s:' % vtag)]
    out('G6 ROWS %s: X %s (stop-check %s); config rows of %s %s; G1\' word %s (one V: TWO_OF_TWO reads ONE_OF_ONE); outcome %s; speed %s; '
        'RATCHET %s; R2 %s' % (vtag, x, 'PASS' if x_ok else 'FAIL', vtag, 'all ok' if not rows_bad else 'FAIL: %s' % rows_bad[:5], a, oc,
                               speed, b, r2))
    if rf:
        out('G6 RATCHET line: %s' % rf[-1][:220])
    g6 = 'PASS' if (oc == 'SPEED_OK' and a == 'TWO_OF_TWO' and b == 'NONE') else 'NOT PASS'
    out('G6 %s (item 778 (d)(6): G1\' in [0.95; 1.05] - SPEED_OK, RATCHET NONE)' % g6)
    return oc, speed, b, rf


def main(argv):
    global SCP24_SHA
    SCP24_SHA = sha_file(SCP24_PATH)
    print('g6_m3a2: scp24.py sha256 %s' % SCP24_SHA)
    c = argv[0] if argv else ''
    if c == 'stage':
        stage()
        return 0
    if c == 'run':
        v = argv[argv.index('--v') + 1] if '--v' in argv else TAG
        root = argv[argv.index('--root') + 1] if '--root' in argv else G
        seal = argv[argv.index('--seal') + 1] if '--seal' in argv else SEAL
        drive(v, root, seal, print)
        return 0
    if c == 'regress':
        allok = True
        for rb in (False, True):
            got = []
            oc, speed, b, rf = drive('iv_5', 'C:/kyty/p283/p24', 'C:/kyty/p283/pred/06_p24.md', got.append, rebind=rb)
            for l in got:
                if l.startswith(('G6 ', "G1' speed iv_5", "G1' VERDICT_PAIR", 'RATCHET iv_5')):
                    print(l[:240])
            ok = oc == 'SPEED_OK' and speed == 1.0001 and b == 'NONE' and bool(rf) and '(> 5 p.p.: False)' in rf[-1]
            allok = allok and ok
            print('REGRESS iv_5 (rebind %s): outcome %s speed %s RATCHET %s, flag line "(> 5 p.p.: False)" %s -> %s' % (
                rb, oc, speed, b, bool(rf) and '(> 5 p.p.: False)' in rf[-1], 'ok' if ok else 'FAIL'))
        print('ALL OK' if allok else 'FAILED')
        return 0 if allok else 1
    print(__doc__.split('python g6_m3a2.py stage')[0][-200:])
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
