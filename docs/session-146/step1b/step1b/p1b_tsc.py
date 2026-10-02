"""s146 link 1b (HPP-395; ROADMAP s122 item 316 (d)): the edits of test_sc146.py - the seal path of F2, the lines of F13 with the
V key, the new cases F13b-F13k of item 316 (b)-(d) (every member and edge, the cases A and B of rt146_skipfx), their lines
in the ASCII case F22, the header.  LF in, LF out (write_bytes)."""
import hashlib

P = 'C:/kyty/s146/test_sc146.py'
t = open(P, 'rb').read().decode('ascii')
assert '\r' not in t
n = 0


def rep(old, new):
    global t, n
    c = t.count(old)
    assert c == 1, (c, old[:80])
    t = t.replace(old, new)
    n += 1


rep("the real log of the warm-up i146_v, ASCII.  Cases F1-F22.\n",
    "the real log of the warm-up i146_v, ASCII.  Cases F1-F22.  Link 1b (HPP-395, item 316 (b)-(d)): the seal pred/02_sc146.md\n"
    "(F2), the skip of a W only on positive evidence and only on the V key attempt:<outcome> - F13 with the key, F13b-F13k (no\n"
    "log in the log and the json reading, 0 bytes with the old and the empty sha line, another sha in both readings, no\n"
    "times.txt, another attempt outcome, the death marker keys K1 / K2 / VALIDATION_STOP in the log, the stdout and the json\n"
    "reading, the cases A and B of the Red Team experiment rt146_skipfx), their lines in F22.\n")
rep("S.PRED_PATH == 'C:/kyty/s146/pred/01_sc146.md' and S.CHAIN == 'go146a' and",
    "S.PRED_PATH == 'C:/kyty/s146/pred/02_sc146.md' and S.CHAIN == 'go146a' and")
rep("""ok &= case('F13 --skip-w: a V without its entry line -> rc 0 SKIPPED_V_NOT_ENTERED (from the log before --tag, from score.json '
           'after it); an entered V -> rc 1 RUN; a V not made -> rc 1 (no reading); the control W and a V tag -> usage rc 2',
           rcA == 0 and outA.startswith('SKIPPED_V_NOT_ENTERED w146_05: its V v146_05 outcome NOT_ENTERED (log (no score.json)') and
           rcB == 0 and outB.startswith('SKIPPED_V_NOT_ENTERED w146_05: its V v146_05 outcome NOT_ENTERED (json;') and
""", """L13 = (R13 / 'log_v146_05.txt').read_bytes()
T13 = ('; log_v146_05.txt %d bytes sha256 %s = the enter_scene end line of step2/times.txt, no entry line (item 309 (k)(1), '
       '316 (b)-(d))\\n' % (len(L13), _h.sha256(L13).hexdigest()[:16]))
ok &= case('F13 --skip-w: a V without its entry line, no marker, its log = the times.txt line -> rc 0 SKIPPED_V_NOT_ENTERED '
           'with the V key attempt:ok and the log evidence (from the log before --tag, from score.json after it); an entered V '
           '-> rc 1 RUN; a V not made -> rc 1 (no reading); the control W and a V tag -> usage rc 2',
           rcA == 0 and outA == 'SKIPPED_V_NOT_ENTERED w146_05: its V v146_05 outcome NOT_ENTERED key attempt:ok (log (no '
           'score.json))' + T13 and
           rcB == 0 and outB == 'SKIPPED_V_NOT_ENTERED w146_05: its V v146_05 outcome NOT_ENTERED key attempt:ok (json)' + T13 and
""")
rep("""# the stop-check source (item 309 (k)(2)): json when its log sha = times.txt, else the log
R15 = BASE / 'F15'
""", """# link 1b (item 316 (b)-(d)): the skip only on positive evidence and only on the V key attempt:<outcome>
NE = [PRE] + [ft(i, 20000, 5) for i in range(1, 50)]
HD = 'w146_05: its V v146_05 outcome NOT_ENTERED key '
NOEV = ' - no positive evidence (item 316 (b))'
EMPTY = _h.sha256(b'').hexdigest()
o1b = []


def sk(root):
    rc, o = run6(['--skip-w', 'w146_05'], root)
    o1b.append(o)
    return rc, o.rstrip('\\n')


def tline(root, sh):
    with open(Path(root) / 'step2' / 'times.txt', 'a', encoding='utf-8') as f:
        f.write('2026-10-02T00:00:01Z go146a v146_05 enter_scene end rc 0 log_v146_05.txt sha256 %s\\n' % sh)


r = Path(mk146(BASE / 'F13b', 'v146_05', lines=NE))
(r / 'log_v146_05.txt').unlink()
rcx, ox = sk(r)
ok &= case('F13b no log of the V (log reading, RC1 case A) -> rc 1 RUN, the key named, no positive evidence',
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (log (no score.json)); no log_v146_05.txt' + NOEV)
r = Path(mk146(BASE / 'F13c', 'v146_05', lines=NE))
run6(['--tag', 'v146_05'], r)
(r / 'log_v146_05.txt').unlink()
rcx, ox = sk(r)
ok &= case('F13c no log of the V after its score.json (json reading: the json log sha = times.txt) -> rc 1 RUN',
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (json); no log_v146_05.txt' + NOEV)
r = Path(mk146(BASE / 'F13d', 'v146_05', lines=NE))
(r / 'log_v146_05.txt').write_bytes(b'')
rcx, ox = sk(r)
ok &= case('F13d the V log is 0 bytes, times.txt names the sha of the log written (RC1 case B) -> rc 1 RUN',
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (log (no score.json)); log_v146_05.txt 0 bytes' + NOEV)
tline(r, EMPTY)
rcx, ox = sk(r)
ok &= case('F13e the V log is 0 bytes and the last times.txt line names the sha of 0 bytes (the sha alone would pass) -> rc 1 '
           'RUN by the size member',
           S.times_log_sha(str(r), 'v146_05') == EMPTY and
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (log (no score.json)); log_v146_05.txt 0 bytes' + NOEV)
r = Path(mk146(BASE / 'F13f', 'v146_05', lines=NE))
lf = _h.sha256((r / 'log_v146_05.txt').read_bytes()).hexdigest()
tline(r, 'cd' * 32)
rcx, ox = sk(r)
ok &= case('F13f the V log sha != the last enter_scene end line of times.txt (log reading) -> rc 1 RUN, both sha named',
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (log (no score.json)); log_v146_05.txt sha256 %s != the enter_scene '
           'end line of step2/times.txt cdcdcdcdcdcdcdcd' % lf[:16] + NOEV)
r = Path(mk146(BASE / 'F13g', 'v146_05', lines=NE))
ts = _h.sha256((r / 'log_v146_05.txt').read_bytes()).hexdigest()
run6(['--tag', 'v146_05'], r)
with open(r / 'log_v146_05.txt', 'ab') as f:
    f.write(b'tail written after the score\\n')
lf = _h.sha256((r / 'log_v146_05.txt').read_bytes()).hexdigest()
rcx, ox = sk(r)
ok &= case('F13g the V log changed after its score.json (json reading taken: the json log sha = times.txt; the file now '
           'differs) -> rc 1 RUN',
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (json); log_v146_05.txt sha256 %s != the enter_scene end line of '
           'step2/times.txt %s' % (lf[:16], ts[:16]) + NOEV)
r = Path(mk146(BASE / 'F13h', 'v146_05', lines=NE))
(r / 'step2' / 'times.txt').unlink()
lf = _h.sha256((r / 'log_v146_05.txt').read_bytes()).hexdigest()
rcx, ox = sk(r)
ok &= case('F13h no step2/times.txt (no enter_scene end line) -> rc 1 RUN',
           rcx == 1 and ox == 'RUN ' + HD + 'attempt:ok (log (no score.json)); log_v146_05.txt sha256 %s != the enter_scene '
           'end line of step2/times.txt none' % lf[:16] + NOEV)
r = Path(mk146(BASE / 'F13i', 'v146_05', lines=NE, js=js146('v146_05', attempt=dict(outcome='no_stable'))))
lb = (r / 'log_v146_05.txt').read_bytes()
rcx, ox = sk(r)
ok &= case('F13i another attempt outcome, no marker, the log = times.txt -> rc 0 SKIPPED with the key attempt:no_stable',
           rcx == 0 and ox == 'SKIPPED_V_NOT_ENTERED ' + HD + 'attempt:no_stable (log (no score.json)); log_v146_05.txt %d '
           'bytes sha256 %s = the enter_scene end line of step2/times.txt, no entry line (item 309 (k)(1), 316 (b)-(d))' % (
               len(lb), _h.sha256(lb).hexdigest()[:16]))
VREP = ['--- Build ---', 'v0.0.0 label', '--- Error ---', '[Vulkan][E][1]: Validation Error: [ VUID-x ] bad', ' in x.cpp:1']
MK = (('k1err', NE + ['--- Error ---'], (), 'K1'), ('k1av', NE + ['Unhandled exception: 0xc0000005'], (), 'K1'),
      ('k1fatal', NE + ['--- Fatal Error ---'], (), 'K1'), ('k2hang', NE + ['GpuHangAbort: requested=6000'], (), 'K2'),
      ('k2lost', NE + ['[Vulkan] ErrorDeviceLost'], (), 'K2'), ('k2std', NE, ('vkQueueSubmit failed: ErrorDeviceLost',), 'K2'),
      ('vstop', NE + VREP, (), 'VALIDATION_STOP'))
res = []
for nm, lines, std, cls in MK:
    r = Path(mk146(BASE / ('F13j_' + nm), 'v146_05', lines=lines, std=std))
    e = S.entry_of('v146_05', str(r), SH6)
    rcx, ox = sk(r)
    run6(['--tag', 'v146_05'], r)
    rcy, oy = sk(r)
    res.append((nm, e['outcome'] == 'NOT_ENTERED' and e['marks'][0]['cls'] == cls and not e['key'].startswith('attempt:') and
                rcx == 1 and ox == 'RUN ' + HD + '%s (log (no score.json)); a death marker before the entry line - the W runs '
                '(item 316 (c))' % e['key'] and
                rcy == 1 and oy == 'RUN ' + HD + '%s (json); a death marker before the entry line - the W runs (item 316 (c))'
                % e['key']))
ok &= case('F13j (item 316 (c), RC2) a V NOT_ENTERED whose key is a death marker - K1 (--- Error ---, access violation, '
           '--- Fatal Error ---), K2 (GpuHangAbort:, ErrorDeviceLost in the log and in the emulator stdout), VALIDATION_STOP '
           '- with the log = times.txt -> rc 1 RUN with the key, from the log and from score.json: %s' % (
               ', '.join(nm for nm, x in res if not x) or 'all'), all(x for _, x in res) and len(res) == 7)
SRC145 = Path('C:/kyty/s145/v145_02.json')
jx = json.loads(SRC145.read_text(encoding='utf-8')) if SRC145.is_file() else js146('v146_05')
r = BASE / 'F13k'
r.mkdir(parents=True)
(r / 'v146_05.json').write_text(json.dumps(jx), encoding='utf-8')
rcx, ox = sk(r)
(r / 'log_v146_05.txt').write_bytes(b'')
rcy, oy = sk(r)
kx = 'attempt:%s' % jx['attempts'][0].get('outcome')
ok &= case('F13k the experiment rt146_skipfx of the Red Team on a synthetic root (only the V json, a copy of the real '
           'C:/kyty/s145/v145_02.json; no times.txt, no score.json): case A no log, case B a log of 0 bytes -> rc 1 RUN both',
           rcx == 1 and ox == 'RUN ' + HD + kx + ' (log (no score.json)); no log_v146_05.txt' + NOEV and
           rcy == 1 and oy == 'RUN ' + HD + kx + ' (log (no score.json)); log_v146_05.txt 0 bytes' + NOEV)
# the stop-check source (item 309 (k)(2)): json when its log sha = times.txt, else the log
R15 = BASE / 'F15'
""")
rep("    ('\\n'.join(f11 + S.fmt_entry(e12) + o13 + o17v + o19 + o19b + [out15, out15b, outA, outB, outC])).encode('cp1250',\n",
    "    ('\\n'.join(f11 + S.fmt_entry(e12) + o13 + o17v + o19 + o19b + [out15, out15b, outA, outB, outC] + o1b)).encode('cp1250',\n")
open(P, 'wb').write(t.encode('ascii'))
print('edits %d; test_sc146.py sha256 %s' % (n, hashlib.sha256(t.encode('ascii')).hexdigest()))
