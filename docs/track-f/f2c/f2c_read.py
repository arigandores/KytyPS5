"""f2c_read.py - F2c (HPP-310), track F: the reading of one F2c tag - ROADMAP p.237(g)(5)(a)-(g), p.254(e); F2b RC2-RC4, RC6.

The s142 reading is NOT copied and NOT changed: sc142.py is imported from C:/kyty/s142 after its sha256 is checked
(SC142_SHA; another sha -> rc 2, no reading), and only its functions scan / derive / markers / validation / read_glitch /
idx_count and constants K2_US / K3_US / ENTRY_WIN / SCENE_DRAWS are called.  The B26 profile is f2c_b26.py (sha checked the
same way).  Everything F2c adds (admission of the F2c run, the 5-hash attribution of the hold frames >= 100 ms, the knob
print lines of the 22 other commits, the arm verdict) is in this file.

  python f2c_read.py --tag f2c_a|f2c_b|f2c_c [--root <dir>] [--json <out.json>]
  python f2c_read.py --check-seal <pred.md>     (rc 0 every 'seal:' line matches and every sealed name has one line)

Tags (p.237(g)(5)):
  f2c_a  (a) KYTY_FIX_B26=1, no validation, video; hold: sum dt_us after the first scene frame >= 300 s (as V of sc142)
  f2c_b  (b) KYTY_FIX_B26=1, --vulkan-validation true, KYTY_PIPELINE_PRECACHE=0 (p.254(e)), no video; hold >= 300 s -
         letter of sc142 for W: hold_s of <tag>.json; the sum of dt_us is printed beside it (variant of the executor)
  f2c_c  (v) KYTY_FIX_B26=0, no validation, no video; hold >= 120 s (hold_s of <tag>.json and sum dt_us after the entry
         line, as the census of sc142)
Every tag: (g) the B26a reopen check of p.237(v)(2) (f2c_b26.py), the count of death markers (sc142.markers: log, then stdout),
the knob print lines of the 22 commits 4fc501f4..20b39318 (F2b RC2; expectation 0 at defaults).
Hold frames (p.237(g)(5)(a)): every FrameTrace row with dt_us >= 100 000 after the entry window (sc142: the 599 rows after the
first scene frame) - its byte interval (the row before it .. the row) and the lines inside it that name one of the 5 B26b
hashes; a frame is attributed to the fix only with such a line.
Output: ASCII only.  rc 0 - read (verdict in the text); rc 1 - no log / no json; rc 2 - usage or a sha mismatch.
"""
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SC142 = 'C:/kyty/s142/sc142.py'
SC142_SHA = '1ce612cdd036e2382ce5c5aae6bd25836062830dc0952da8512a9f2a74bb38c3'
B26 = os.path.join(HERE, 'f2c_b26.py')
B26_SHA = 'ec19f7120b26b62050638bc3b5e0a21f7ed122984495de392b77824e7c6f95bd'
LEVEL = 'underwater_aerial_garden'
ROOT = 'C:/kyty/f287/f2c'
CHUNK = 1 << 26
TAGS = {
    'f2c_a': dict(fix='1', arm='V', val=False, video=True, hold_s=300),
    'f2c_b': dict(fix='1', arm='W', val=True, video=False, hold_s=300),
    'f2c_c': dict(fix='0', arm='V', val=False, video=False, hold_s=120),
}
FRAMES_V = 3000
KNOB_NAMES = ('ArmCopy', 'ArmCopyClass', 'ArmCopyHist', 'ArmCopyLoss', 'ArmCopyLossCtl', 'ArmCopyLossLate', 'ArmCopyVerify',
              'ArmInline', 'B2Reuse', 'B2ReuseVerify', 'BindLean', 'BindLeanVerify', 'DispCeil', 'LossWin', 'PbCheck',
              'ProtCeil', 'RbCen', 'RbSlow', 'RbSlowVerify')
RX_KNOB = re.compile(rb'\b(' + b'|'.join(n.encode() for n in KNOB_NAMES) + rb'):')


def sha_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def load(path, want, name):
    got = sha_file(path)
    if got != want:
        raise SystemExit('sha mismatch %s: %s != %s' % (path, got, want))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def scan_extra(path, hashes):
    """Positions of the lines naming one of the 5 hashes (any case) and counts of the knob print lines."""
    pats = []
    for h in hashes:
        pats += [h.lower().encode(), h.upper().encode()]
    res = dict(hash_lines=[], knob={})
    off = 0
    tail = b''
    with open(path, 'rb') as f:
        while True:
            b = f.read(CHUNK)
            buf = tail + b
            if b:
                cut = buf.rfind(b'\n') + 1
                if cut == 0:
                    tail = buf
                    continue
                whole, tail = buf[:cut], buf[cut:]
            else:
                whole, tail = buf, b''
            if not whole:
                break
            base = off
            off += len(whole)
            seen = set()
            for p in pats:
                i = whole.find(p)
                while i >= 0:
                    s = whole.rfind(b'\n', 0, i) + 1
                    if s not in seen:
                        seen.add(s)
                        e = whole.find(b'\n', i)
                        res['hash_lines'].append((base + s, whole[s:e if e >= 0 else len(whole)][:160].decode('latin1')))
                    i = whole.find(p, i + 1)
            for m in RX_KNOB.finditer(whole):
                k = m.group(1).decode()
                res['knob'][k] = res['knob'].get(k, 0) + 1
            if not b:
                break
    res['hash_lines'].sort()
    return res


def hold_frames(sc142, log, entry_pos, hash_lines):
    """Rows >= K3_US after the entry window (before a scene change), each with its interval and the 5-hash lines in it."""
    if entry_pos is None:
        return None
    later = [p for name, p in log['starts'] if p > entry_pos]
    cpos = later[0] if later else None
    after = [r for r in log['rows'] if r[3] > entry_pos and (cpos is None or r[3] < cpos)]
    fi = next((i for i, r in enumerate(after) if r[2] >= sc142.SCENE_DRAWS), None)
    if fi is None:
        return None
    post = after[fi + 1:]
    out = []
    for j in range(sc142.ENTRY_WIN, len(post)):
        r = post[j]
        if r[1] >= sc142.K3_US:
            lo = post[j - 1][3]
            inside = [t for p, t in hash_lines if lo < p < r[3]]
            out.append(dict(n=r[0], dt_us=r[1], lo=lo, hi=r[3], k2=r[1] >= sc142.K2_US, hash_lines=len(inside),
                            first=inside[:2]))
    return out


def read_tag(tag, root=ROOT, sc142=None, b26=None):
    cfg = TAGS[tag]
    sc142 = sc142 or load(SC142, SC142_SHA, 'sc142')
    b26 = b26 or load(B26, B26_SHA, 'f2c_b26')
    lp = os.path.join(root, 'log_%s.txt' % tag)
    sp = os.path.join(root, 'stdout_%s.txt' % tag)
    jp = os.path.join(root, '%s.json' % tag)
    if not os.path.isfile(lp) or not os.path.isfile(jp):
        return None
    with open(jp, encoding='utf-8') as f:
        js = json.load(f)
    at = (js.get('attempts') or [{}])[0]
    env = js.get('env') or {}
    log = sc142.scan(lp)
    std = sc142.scan(sp) if os.path.isfile(sp) else None
    d = sc142.derive(log, LEVEL)
    marks = sc142.markers(log, std, d['entry_pos'], log['quit'])
    val = sc142.validation(log, std)
    h96, h5 = b26.load_hashes()
    bres = b26.scan(lp, h96, h5)
    bout = b26.judge(bres, cfg['fix'], h5, cfg['arm'])
    ex = scan_extra(lp, sorted(h5))
    r = dict(tag=tag, cfg=cfg, log_sha=log['sha256'], binary=js.get('binary_sha256'), b26=bout, b26_text=b26.report(bres, bout))
    adm = []

    def add(name, ok, detail=''):
        adm.append((name, bool(ok), str(detail)))
    add('one attempt', len(js.get('attempts') or []) == 1, len(js.get('attempts') or []))
    add('guest args -lvl %s' % LEVEL, js.get('guest_args') == '-lvl %s' % LEVEL, js.get('guest_args'))
    add('KYTY_FIX_B26=%s exactly (RC6)' % cfg['fix'], env.get('KYTY_FIX_B26') == cfg['fix'], repr(env.get('KYTY_FIX_B26')))
    add('KYTY_GPU_CLOCK_PIN=1', env.get('KYTY_GPU_CLOCK_PIN') == '1', env.get('KYTY_GPU_CLOCK_PIN'))
    add('no KYTY_GPU_CHECKPOINTS', 'KYTY_GPU_CHECKPOINTS' not in env, '')
    pc = env.get('KYTY_PIPELINE_PRECACHE')
    add('KYTY_PIPELINE_PRECACHE %s' % ('=0 (p.254(e))' if cfg['val'] else 'not set'),
        pc == '0' if cfg['val'] else pc is None, repr(pc))
    rec = env.get('KYTY_REC')
    if cfg['video']:
        add('video KYTY_REC rec_%s.mp4' % tag, rec is not None and rec.replace('\\', '/').endswith('/rec_%s.mp4' % tag), rec)
    else:
        add('no video', rec is None, rec)
    vv = sc142.last_value(js.get('cmdline') or [], '--vulkan-validation')
    add('--vulkan-validation %s' % ('true' if cfg['val'] else 'false'), vv == ('true' if cfg['val'] else 'false'), vv)
    if cfg['val']:
        add('validation active (p.224: 0 no-layer, >= 1 validation_features, >= 1 [Vulkan][)', val['ok'],
            '%d/%d/%d' % (val['noval'], val['valfeat'], val['vkany']))
    r['admit'] = adm
    r['admitted'] = all(ok for _, ok, _ in adm)
    r['entered'] = d['entered']
    r['first'] = d['first']
    r['dt_after_first_s'] = d['dt_after_first_us'] / 1e6
    r['dt_after_entry_s'] = d['dt_after_entry_us'] / 1e6
    r['hold_s_json'] = at.get('hold_s')
    r['hold_exit'] = at.get('hold_exit')
    r['scene_change'] = d['change_pos'] is not None
    r['marks'] = [(m['kind'], m['cls'], m['src'], m['at_exit']) for m in marks]
    r['deaths'] = len(marks)
    r['deaths_before_quit'] = sum(1 for m in marks if not m['at_exit'])
    r['vke'] = len(log['vke']) + (len(std['vke']) if std else 0)
    r['vke_first'] = [x[2] for x in (log['vke'] + (std['vke'] if std else []))[:3]]
    r['val'] = val
    r['knob_lines'] = ex['knob']
    r['hash_lines'] = len(ex['hash_lines'])
    r['hold_frames'] = hold_frames(sc142, log, d['entry_pos'], ex['hash_lines'])
    r['k2_after_first'] = len(d['k2'])
    r['skip_lines'] = log['skip_lines']
    r['rows_total'] = len(log['rows'])
    g = sc142.read_glitch(os.path.join(root, 'glitch_%s.txt' % tag))
    r['glitch'] = g
    r['sheet'] = os.path.isfile(os.path.join(root, 'sheet_%s.png' % tag)) and os.path.getsize(os.path.join(root, 'sheet_%s.png' % tag)) > 0
    # hold by arm
    if tag == 'f2c_a':
        hold_ok = r['dt_after_first_s'] >= cfg['hold_s']
        hold_vx = hold_ok
    elif tag == 'f2c_b':
        hold_ok = (r['hold_s_json'] or 0) >= cfg['hold_s']
        hold_vx = r['dt_after_first_s'] >= cfg['hold_s']
    else:
        hold_ok = (r['hold_s_json'] or 0) >= cfg['hold_s'] and r['dt_after_entry_s'] >= cfg['hold_s']
        hold_vx = r['dt_after_first_s'] >= cfg['hold_s']
    r['hold_ok'], r['hold_vx'] = hold_ok, hold_vx
    base = r['admitted'] and d['entered'] and not r['scene_change'] and r['deaths'] == 0 and r['hold_exit'] is None

    def held(ok, hold):
        # p.256(d): (a) and (b) with a hold below 300 s (and nothing else failed) -> NOT EVALUABLE, a repeat only by the lead
        return 'FAIL' if not ok else ('PASS' if hold else 'NOT EVALUABLE')
    if tag == 'f2c_a':
        vid = g is not None and g['video_frames'] >= FRAMES_V and g['glitches'] == 0 and r['sheet']
        r['video_ok'] = vid
        crit = base and vid and not bout['reopen_any']
        r['verdict_letter'] = held(crit and bout['verdict_letter'] == 'PASS', hold_ok)
        r['verdict_variant'] = held(crit and bout['verdict_variant'] == 'PASS', hold_ok)
    elif tag == 'f2c_b':
        crit = base and val['ok'] and r['vke'] == 0 and bout['knob_ok'] and bout['form_ok'] is True and not bout['reopen_any']
        r['verdict_letter'] = held(crit, hold_ok)
        r['verdict_variant'] = held(crit, hold_vx)
    else:
        crit = base and bout['verdict_letter'] == 'CONTROL RETURNS' and not bout['reopen_any']
        r['verdict_letter'] = 'PASS' if crit and hold_ok else 'FAIL'
        r['verdict_variant'] = 'PASS' if crit and hold_vx else 'FAIL'
    if not r['admitted']:
        r['verdict_letter'] = r['verdict_variant'] = 'NOT ADMITTED'
    return r


def text(r):
    L = ['f2c_read tag %s arm %s fix %s log sha256 %s binary %s' % (r['tag'], r['cfg']['arm'], r['cfg']['fix'], r['log_sha'],
                                                                    (r['binary'] or '')[:16])]
    for name, ok, det in r['admit']:
        L.append('admit %-4s %s [%s]' % ('ok' if ok else 'FAIL', name, det))
    L.append('entered %s first scene frame %s scene change %s' % (r['entered'], r['first'], r['scene_change']))
    L.append('hold: sum dt after first %.1f s, after entry %.1f s, json hold_s %s, hold_exit %s -> letter %s, variant %s' % (
        r['dt_after_first_s'], r['dt_after_entry_s'], r['hold_s_json'], r['hold_exit'], r['hold_ok'], r['hold_vx']))
    L.append('death markers %d (before quit %d) %s' % (r['deaths'], r['deaths_before_quit'], r['marks'][:4]))
    L.append('K2 frames after first scene frame %d; AsyncPipelines skipped draw lines %d; FrameTrace rows %d' % (
        r['k2_after_first'], r['skip_lines'], r['rows_total']))
    L.append('validation noval/valfeat/vkany %d/%d/%d active %s; [Vulkan][E] %d %s' % (
        r['val']['noval'], r['val']['valfeat'], r['val']['vkany'], r['val']['ok'], r['vke'], r['vke_first'][:1]))
    L.append('knob print lines of the 22 commits (RC2, expect 0): %d %s' % (sum(r['knob_lines'].values()), sorted(r['knob_lines'].items())))
    L.append('lines naming one of the 5 B26b hashes: %d' % r['hash_lines'])
    hf = r['hold_frames']
    if hf is None:
        L.append('hold frames >= 100 ms: not evaluable (no entry or no first scene frame)')
    else:
        L.append('hold frames >= 100 ms (after the entry window): %d, with a 5-hash line in the interval: %d' % (
            len(hf), sum(1 for x in hf if x['hash_lines'])))
        for x in hf:
            L.append('  frame n=%d dt_us=%d %s interval [%d,%d] 5-hash lines %d %s' % (
                x['n'], x['dt_us'], 'K2' if x['k2'] else 'K3', x['lo'], x['hi'], x['hash_lines'], x['first'][:1]))
    g = r['glitch']
    L.append('video: %s glitches %s sheet %s%s' % (g['video_frames'] if g else None, g['glitches'] if g else None, r['sheet'],
                                                  (' -> ok %s' % r['video_ok']) if 'video_ok' in r else ''))
    L.append('--- B26 profile (f2c_b26.py) ---')
    L.append(r['b26_text'])
    L.append('F2C VERDICT %s letter: %s' % (r['tag'], r['verdict_letter']))
    L.append('F2C VERDICT %s RC1/executor variant (rule of p.256(a),(d) - verdict of record): %s' % (r['tag'], r['verdict_variant']))
    return '\n'.join(L)


SEALED = ('go_f2c.sh', 'f2c_read.py', 'f2c_b26.py', 'shalist_f2c.py', 'win332_f2c.py', 'test_f2c_read.py', 'test_f2c_b26.py',
          'test_go_f2c.py', 'enter_scene.py',
          'launch_run.py', 'run_safety99.py', 'idle142.py', 'procload.py', 'sheet142.py', 'cachemf143.py', 'fgcpu143.py',
          'gates_default.txt', SC142, 'C:/kyty/scripts/s51_vidglitch.py', 'C:/kyty/f287/f1a/b26_shaders.tsv')
RX_SEAL = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)$')


def check_seal(pred, root=ROOT, names=SEALED):
    """Every 'seal: <sha256> <path>' line of the seal must match the file now (a path without 'C:/' is under root), and every
    name of SEALED must have exactly one line.  Returns (ok, lines)."""
    if not os.path.isfile(pred):
        return False, ['no seal %s' % pred]
    got = {}
    out = []
    ok = True
    with open(pred, encoding='utf-8') as f:
        for line in f:
            m = RX_SEAL.match(line.rstrip('\r\n'))
            if not m:
                continue
            name = m.group(2)
            path = name if name.startswith('C:/') else os.path.join(root, name)
            now = sha_file(path) if os.path.isfile(path) else None
            good = now == m.group(1)
            got[name] = got.get(name, 0) + 1
            ok &= good
            out.append('seal %s %s %s' % ('ok' if good else 'MISMATCH', name, (now or 'missing')[:16]))
    for n in names:
        if got.get(n, 0) != 1:
            ok = False
            out.append('seal line count %s = %d (want 1)' % (n, got.get(n, 0)))
    return ok, out


def main(argv=None):
    a = list(sys.argv[1:] if argv is None else argv)
    if '--check-seal' in a and a.index('--check-seal') + 1 < len(a):
        ok, lines = check_seal(a[a.index('--check-seal') + 1])
        print('\n'.join(lines))
        print('check-seal %s' % ('OK' if ok else 'FAILED'))
        return 0 if ok else 1
    if '--tag' not in a or a.index('--tag') + 1 >= len(a) or a[a.index('--tag') + 1] not in TAGS:
        print('usage: f2c_read.py --tag f2c_a|f2c_b|f2c_c [--root <dir>] [--json <out>]')
        return 2
    tag = a[a.index('--tag') + 1]
    root = a[a.index('--root') + 1] if '--root' in a else ROOT
    try:
        r = read_tag(tag, root)
    except SystemExit as e:
        print('refused: %s' % e)
        return 2
    if r is None:
        print('no log_%s.txt or %s.json in %s' % (tag, tag, root))
        return 1
    print(text(r))
    if '--json' in a:
        with open(a[a.index('--json') + 1], 'w', encoding='ascii') as f:
            json.dump({k: v for k, v in r.items() if k != 'b26_text'}, f, indent=1, default=str)
    return 0


if __name__ == '__main__':
    sys.exit(main())
