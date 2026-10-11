"""Track F link F46c (HPP-800; ROADMAP s122 item 702 (g), (d); item 711 (b)(1), (v) N1): the reader of ONE tag of the pair series F26 on
Sky Garden, binary T 9c1b268f (F46a: worktree 7e8481e5 = FS12a 730ed40a + 6 commits of the KYTY_FIX_F26 chain + 1398d44d; version
KytyPS5-2026-09-15-6a2987a-1921-g7e8481e5); installed FS13 abab2196 before and after.  Rows only, NO VERDICT (the reading is F46d).
Port of C:/kyty/f287/f44c/f44c_read.py (the form fs12_v, admission) with the event lines of C:/kyty/f287/f16q/f16q_read.py (identity of
item 507 (b)(4)) and the lines of F46a 1398d44d (dcc_stale_apply result= cleared|declined|dropped site=, f26_first_exec, F26Tint).
ASCII only.

    python f46c_read.py <tag> [--json <out>]                        one tag (files of C:/kyty/f287/f46c)
    python f46c_read.py --dir <fixture dir> --tag <tag> [--json <out>]
        fixture form: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt, installed_before.txt, installed_after.txt,
        installed_sha.txt, manifest_cmp.txt, level.txt, seal.md, bin.exe
    python f46c_read.py --table [--runs <dir>]                      the table over every runs/<tag>/read.json

TAGS (item 702 (g)(2)); common knobs KYTY_DIAG_F5=1 KYTY_DIAG_F5ID=1 KYTY_DCC_TRACE=1 KYTY_GPU_CLOCK_PIN=1 KYTY_GPU_MARKERS=0:
  f26s_0   KYTY_FIX_F26=0                  f26s_1, f26s_1b   KYTY_FIX_F26=1 (f26s_1b - the null pair)
  f26s_t<k> KYTY_FIX_F26=1 KYTY_F26_TINT=1 KYTY_F26_TINT_DCC=<dcc of S<k>>    f26s_c<k>  the same with KYTY_F26_TINT=2   (k = 1..4)
  a repeat _r1.._r3 has the knobs of its base tag.
EVENTS S1..S4 (F45a section 2.1, keys of 5 of 5 FS12-line logs): (image, dcc, fill, size) below in FS12_KEYS; S<k> of a tag - the FIRST
  'DiagF5Ev: dcc_stale' line after the entry line with (image, dcc) of S<k>.
DEFINITIONS (seal docs/track-f/f46c.md section 4):
  entry line      the first line ending 'GuestOut: Level has started: underwater_aerial_garden'; first GuestOut - the first line with 'GuestOut'.
  first scene     the first 'FrameTrace: n=' line after the entry line with draws >= 100; hold - sum dt_us of the FrameTrace lines after it.
  class           of an event (item 702 (v)(1), 711 (b)(1)): fix=kept_applied -> 'kept_applied'; fix=kept why=X -> 'kept why=X'; any other
                  fix -> its fix (with why).  MARK classes - 'kept why=decode', 'kept why=deferred' (F46a: the mark M1 by address).
  cleared / declined / dropped   'DiagF5Ev: dcc_stale_apply' lines of the event: n = the event n and dcc = the event dcc.
  first_exec      'DiagF5Ev: f26_first_exec' of the event: n = the event n and dcc = the event dcc (first one).
  NO_APPLY        item 702 (d)(2): an event of a MARK class without a cleared line to the end of the log (the end of the hold).
  F26Tint         'F26Tint: mode=<m> dcc=0x<hex>' (F46a diagF5.cpp, printed at device creation when KYTY_F26_TINT != 0): the key is
                  compared AS A NUMBER with the env value (item 711 (v) N1: 16 digits with leading zeros vs '0x...' of the env).
ADMISSION (item 702 (g)(4); a failed member - NOT_ADMITTED and one repeat _r1, item 273 (z); a second NOT_ADMITTED - the events of the tag
  'undetermined'):  the form members of F44c (json; binary_sha256 = T; installed during the tag = T; installed before = after = FS13;
  prereg = seal sha256; env = the form of the tag exactly; no KYTY_TEST_*; last --vulkan-validation false; --shader-validation false;
  no --rd; -lvl underwater_aerial_garden; hold option 330; log; stdout; outcome ok; entry line; window minimized / Recovering 0;
  signature 9177b426 and the variant dir; GamePatch 0; DiagB32 0; TestLogStall 0; manifest cmp EQUAL; LogAsync summary once)
  + the letter of item 702 (g)(4): hold >= 300 s after the first scene frame; 0 death markers (log and stdout); video index >= 3 000;
  'FixF26: mode=1' lines <=> KYTY_FIX_F26=1 (=1: >= 1 line, every line exactly 'FixF26: mode=1', the first before the first GuestOut;
  =0: 0 lines 'FixF26:'); 'F26Tint:' = the env (tint tags: >= 1 line, every line mode = env mode and dcc = env key as numbers, the first
  before the first GuestOut; other tags: 0 lines 'F26Tint:' and f26_tint_applied = 0 on every DiagF5 line - the negative control);
  the 4 keys of S1..S4 after the entry line (a dcc_stale line with (image, dcc); fill and size - on the 'stale pending DCC fill ignored'
  line of (image, dcc) after the entry when the arm prints it - EXECUTOR READING, the letter count is a row); field site= on every
  dcc_stale line (unparsable DiagF5Ev lines 0); 0 'skipped draw' lines in the whole log; identities of F45a section 2.2 (below) - 0
  violations.
IDENTITIES (F45a section 2.2 with item 507 (b)(4) and the F46a changes, section 6.2 of its report):  on EVERY DiagF5 line:
  f26_kept_applied <= f26_kept, f26_deferred_declined <= f26_kept; at KYTY_FIX_F26=1 f26_kept = dcc_stale_bucket_only; at =0 all f26_*
  of F16o / F16o2 (f26_kept, f26_kept_applied, f26_exact_stale, f26_fallback, f26_deferred_declined) = 0 and 0 dcc_stale_apply lines;
  at KYTY_F26_TINT=0: f26_tint_applied = f26_tint_skip = 0 and 0 'F26Tint:' lines.  Line counts against the LAST DiagF5 line (the VARIANT
  of item 502 (b): event lines before the last DiagF5 line; the whole-log letter printed): lines fix in {kept, kept_applied} = f26_kept;
  lines fix=kept_applied + lines result=cleared = f26_kept_applied; lines fix=exact_stale = f26_exact_stale; lines fix=fallback =
  f26_fallback; lines result=declined = f26_deferred_declined; lines site=adopt fix=kept_applied = 0; per event n at most one cleared
  line.  A kind that exhausted its line limit (dcc_stale n = 256) makes the line-count identities LIMIT (not a member).
  The letter 'cleared lines site=prepare <= events kept why=decode' (F45a 2.2, written before F46a) is a ROW (F46a: a deferred mark may
  be cleared at prepare too, report section 3.2 T1); the member is 'cleared lines <= events of a MARK class, at most one per n'.
ROWS: frames >= 1 s after the first scene frame; one-frame glitches; sheet; [Vulkan][E]; the 14 + 4 'stale pending' lines (before / after
  the entry); every dcc_stale event after the entry; apply / first_exec lines; the last DiagF5 f26_* and f26_tint_*; DiagF5Id mode line;
  the form group fs12_v of F44c (FixF21, FixB12, Event: quit, LogAsync, FixB13, FixB12Stat) as rows.
"""
import hashlib
import json
import os
import re
import sys

G = 'C:/kyty/f287/f46c'
SEAL_PATH = G + '/pred/f46c_seal.md'
BIN_PATH = 'C:/kyty/f287/bin/kyty_emulator_9c1b268f.exe'
BIN_TAG = '9c1b268ffffebcbf26e3ce33de94fb24c9b555fe89441fafcf40b7197d03ae69'
BIN_INST = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'
VERSION = b'KytyPS5-2026-09-15-6a2987a-1921-g7e8481e5'
SIG = '9177b4267de1fb8bac7d1113afd8733210addfac'
VARIANT_DIR = 'variant_fixb26_fixb1b_fixf10_fixf19'
SKY = 'underwater_aerial_garden'
TAG_RX = re.compile(r'^(f26s_0|f26s_1|f26s_1b|f26s_t[1-4]|f26s_c[1-4])(_r[1-3])?$')
FS12_KEYS = [('S1', '000000051c630000', '0000000571006000', '00000000', '38000'),
             ('S2', '0000000511650000', '0000000570aee000', '20202020', '1e000'),
             ('S3', '00000005168c0000', '0000000570b24000', '00000000', '1e000'),
             ('S4', '0000000510d10000', '000000056d898000', '20202020', '14000')]
ALLOWED = ('kept_applied', 'kept why=decode', 'kept why=deferred')
MARK = ('kept why=decode', 'kept why=deferred')
K2_US = 1000000
HOLD_V_US = 300000000
HOLD_OPT = 330
VIDEO_MIN = 3000
LIM_DCC = 256
F5_NAMES = ['rt_resolves', 'dcc_rt', 'rtcheck_meta', 'dcc_rt_pending', 'dcc_rt_cleared', 'dcc_rt_skip_levels', 'dcc_rt_skip_partial',
            'dcc_rt_skip_decode', 'dcc_rt_skip_layers', 'dcc_mat_pending', 'dcc_mat_cleared', 'dcc_mat_undecoded', 'dcc_fce',
            'dcc_fce_image', 'dcc_fce_no_image', 'dcc_fill_all', 'dcc_fill_meta', 'dcc_fill_clear', 'dcc_fill_uncompressed',
            'dcc_fill_unknown', 'dcc_reset_stale', 'dcc_reset_type', 'meta_refused_known', 'meta_cs_tracked', 'meta_cs_untracked',
            'meta_dma_untracked', 'meta_dma_noclear', 'cmask_rt_pending', 'cmask_rt_cleared', 'cmask_rt_skip_value',
            'cmask_rt_skip_partial', 'cmask_rt_skip_decode', 'cmask_rt_skip_layers', 'cmask_fce', 'cmask_fce_noimage', 'cmask_fce_meta',
            'cmask_fce_msaa', 'cmask_fce_layout', 'cmask_fce_nofill', 'cmask_fce_drawn', 'cmask_fce_b42', 'cmask_fce_unapplied',
            'fmask_read', 'round_unorm', 'round_float', 'round_other', 'ds_unbound', 'ds_unbound_clear', 'stereo_writes',
            'stereo_nonzero', 'zero_disp', 'f5cmu_kept', 'f5cmu_kept_applied', 'f5cmu_exact_stale', 'f5cmu_fallback',
            'dcc_stale_bucket_only', 'dcc_stale_fallback', 'cmask_rt_bucket_only', 'f5cmu_exact_cpu',
            'f26_kept', 'f26_kept_applied', 'f26_exact_stale', 'f26_fallback', 'f26_deferred_declined',
            'f26_tint_applied', 'f26_tint_skip']
F26C = ['f26_kept', 'f26_kept_applied', 'f26_exact_stale', 'f26_fallback', 'f26_deferred_declined']
TINT = ['f26_tint_applied', 'f26_tint_skip']
RX_F5 = re.compile(rb'DiagF5: frame=(\d+)' + b''.join(rb' ' + n.encode() + rb'=(\d+)' for n in F5_NAMES) + rb'(?=\s|$)')
RX_DS = re.compile(rb'DiagF5Ev: dcc_stale site=(prepare|adopt) n=(\d+) present=(\d+) gpu=(\d+) image=0x([0-9a-f]+) dcc=0x([0-9a-f]+) '
                   rb'extent=(\d+)x(\d+) exact=(stale|fresh|fallback|na) fix=([a-z_]+)(?: why=([a-z]+))?\s*$')
RX_DA = re.compile(rb'DiagF5Ev: dcc_stale_apply n=(\d+) present=(\d+) gpu=(\d+) image=0x([0-9a-f]+) dcc=0x([0-9a-f]+) '
                   rb'result=(cleared|declined|dropped) layers=0x([0-9a-f]{8}) site=(prepare|mat|fill|unmap|delete|retype|remark)\s*$')
RX_FX = re.compile(rb'DiagF5Ev: f26_first_exec n=(\d+) present=(\d+) dcc=0x([0-9a-f]+) image=0x([0-9a-f]+) site=([a-z]+)\s*$')
RX_ST = re.compile(rb'TextureCache: stale pending DCC fill ignored image=0x([0-9a-f]+) dcc=0x([0-9a-f]+) fill=0x([0-9a-f]+) '
                   rb'size=0x([0-9a-f]+)')
RX_TINT = re.compile(rb'F26Tint: mode=(\d+) dcc=0x([0-9a-f]+)\s*$')
RX_FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_SUM = re.compile(rb'^LogAsync: full_waits=\d+ ')
RX_B13 = re.compile(rb'FixB13: mode=(\d+)')
RX_B12 = re.compile(rb'FixB12: mode=(\d+)\s*$')
RX_F21 = re.compile(rb'FixF21: mode=(\d+) wait_ms=(\d+)\s*$')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_SKIP = re.compile(rb'skipped draw')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
SEED = re.compile(rb':KytySC3:([0-9a-f]{40}):')
M_FORK = b'Fork build arigandores/KytyPS5 '
M_QUIT = b'Event: quit'
M_FATAL = b'--- Fatal Error ---'
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
SUM_KEYS = ('full_waits', 'full_wait_us', 'stalls', 'stall_cut', 'lines', 'bytes', 'max_queued_bytes', 'sync_lines', 'drain_timeouts')


def sha_file(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def text(path):
    if not path or not os.path.exists(path):
        return None
    return open(path, 'rb').read().decode('utf-8', 'replace')


def last_flag(cmd, flag):
    v = None
    for i, a in enumerate(cmd or []):
        if a == flag:
            v = cmd[i + 1] if i + 1 < len(cmd) else ''
    return v


def hexnum(s):
    """item 711 (v) N1: a key as a number - '0x' optional, leading zeros any; None when not a whole hex number."""
    if s is None:
        return None
    t = s.strip().lower()
    if t.startswith('0x'):
        t = t[2:]
    if not t or any(c not in '0123456789abcdef' for c in t):
        return None
    return int(t, 16)


def base_of(tag):
    return re.sub(r'_r[1-3]$', '', tag)


def knobs(tag):
    """The KYTY_* knobs of the tag form beyond the common form (values exact; the TINT_DCC value is compared as a number)."""
    b = base_of(tag)
    k = dict(KYTY_DIAG_F5='1', KYTY_DIAG_F5ID='1', KYTY_DCC_TRACE='1', KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0')
    k['KYTY_FIX_F26'] = '0' if b == 'f26s_0' else '1'
    if b.startswith('f26s_t') or b.startswith('f26s_c'):
        k['KYTY_F26_TINT'] = '1' if b.startswith('f26s_t') else '2'
        k['KYTY_F26_TINT_DCC'] = '0x%x' % int(FS12_KEYS[int(b[-1]) - 1][2], 16)
    return k


def expected_env(tag):
    e = dict(KYTY_GUEST_ARGS='-lvl ' + SKY, KYTY_FRAME_TRACE='lite', KYTY_GATE_FILE=None, KYTY_SAMPLE_GATE=None, KYTY_QUEUE_TRACE='1',
             KYTY_GPU_HANG_ABORT_S='8', KYTY_REC=None)
    e.update(knobs(tag))
    return e


def env_diff(env, want):
    bad = []
    for key in sorted(set(env) | set(want)):
        if key not in env:
            bad.append('missing %s' % key)
        elif key not in want:
            bad.append('extra %s=%s' % (key, env[key]))
        elif key == 'KYTY_F26_TINT_DCC':
            if hexnum(env[key]) is None or hexnum(env[key]) != hexnum(want[key]):
                bad.append('%s=%s (want %s as a number)' % (key, env[key], want[key]))
        elif want[key] is not None and env[key] != want[key]:
            bad.append('%s=%s (want %s)' % (key, env[key], want[key]))
    return bad


def parse_f5(raw):
    i = raw.find(b'DiagF5: frame=')
    m = RX_F5.match(raw, i) if i >= 0 else None
    if not m:
        return None
    v = [int(x) for x in m.groups()]
    d = dict(zip(F5_NAMES, v[1:]))
    d['frame'] = v[0]
    return d


def class_of(fix, why):
    if fix == 'kept_applied':
        return 'kept_applied'
    if fix == 'kept':
        return 'kept why=%s' % why
    return fix if not why else '%s why=%s' % (fix, why)


def scan(path):
    """One pass over the log."""
    import lzma
    fh = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    r = dict(summary=[], summary_bad=0, mode=[], ft=[], entry_ln=None, first_guest_ln=None, death=[], minimized=0, recovering=0, win={},
             b13=[], b12=[], f21=[], quit_ln=None, fatal_after_quit=0, vke=0, lines=0, sig=[], variant_dir=[], gamepatch=0, diagb32=0,
             stall_lines=0, fork=None, skipped=0, skipped_first=None, f26_any=[], f26_bad=0, tint=[], tint_bad=0, id_mode=[],
             f5=[], f5_bad=0, ds=[], da=[], fx=[], ev_bad=0, ev_bad_first=None, stale=[])
    lvl = ('GuestOut: Level has started: %s' % SKY).encode()
    ln = 0
    for line in fh:
        ln += 1
        if line.startswith(b'FrameTrace: n='):
            m = RX_FT.match(line)
            if m:
                d = RX_DRAWS.search(line)
                r['ft'].append((int(m.group(1)), int(m.group(2)), int(d.group(1)) if d else None, ln))
            continue
        if line.startswith(b'FrameTrace'):
            continue
        scene = r['entry_ln'] is not None
        if b'DiagF5: frame=' in line:
            d = parse_f5(line)
            if d is None:
                r['f5_bad'] += 1
            else:
                d['ln'] = ln
                r['f5'].append(d)
            continue
        if b'DiagF5Ev:' in line:
            m = RX_DS.search(line)
            if m:
                g = m.groups()
                r['ds'].append(dict(site=g[0].decode(), n=int(g[1]), present=int(g[2]), gpu=int(g[3]), image=g[4].decode(),
                                    dcc=g[5].decode(), extent='%sx%s' % (g[6].decode(), g[7].decode()), exact=g[8].decode(),
                                    fix=g[9].decode(), why=g[10].decode() if g[10] else None, ln=ln, scene=scene))
                continue
            m = RX_DA.search(line)
            if m:
                g = m.groups()
                r['da'].append(dict(n=int(g[0]), present=int(g[1]), gpu=int(g[2]), image=g[3].decode(), dcc=g[4].decode(),
                                    result=g[5].decode(), layers=g[6].decode(), site=g[7].decode(), ln=ln, scene=scene))
                continue
            m = RX_FX.search(line)
            if m:
                g = m.groups()
                r['fx'].append(dict(n=int(g[0]), present=int(g[1]), dcc=g[2].decode(), image=g[3].decode(), site=g[4].decode(), ln=ln,
                                    scene=scene))
                continue
            if b'DiagF5Ev: dcc_stale' in line or b'DiagF5Ev: f26_first_exec' in line:
                r['ev_bad'] += 1
                if r['ev_bad_first'] is None:
                    r['ev_bad_first'] = line.decode('ascii', 'replace').strip()[:200]
            continue
        if b'stale pending DCC fill ignored' in line:
            m = RX_ST.search(line)
            if m:
                r['stale'].append(dict(image=m.group(1).decode(), dcc=m.group(2).decode(), fill=m.group(3).decode(),
                                       size=m.group(4).decode(), scene=scene, ln=ln))
            continue
        if RX_SKIP.search(line):
            r['skipped'] += 1
            if r['skipped_first'] is None:
                r['skipped_first'] = line.decode('ascii', 'replace').strip()[:160]
        if b'FixF26:' in line:
            r['f26_any'].append((line.decode('ascii', 'replace').strip()[:80], ln))
            if line.rstrip(b'\r\n').split(b'FixF26:', 1)[1].strip() != b'mode=1':
                r['f26_bad'] += 1
        if b'F26Tint:' in line:
            m = RX_TINT.search(line)
            if m:
                r['tint'].append((int(m.group(1)), m.group(2).decode(), ln))
            else:
                r['tint_bad'] += 1
        if b'DiagF5Id: mode=' in line:
            r['id_mode'].append((line.decode('ascii', 'replace').strip()[:80], ln))
        if line.startswith(b'DiagB32'):
            r['diagb32'] += 1
        if line.startswith(b'TestLogStall:'):
            r['stall_lines'] += 1
        if line.startswith(b'LogAsync:'):
            if line.startswith(b'LogAsync: mode='):
                r['mode'].append((line.decode('ascii', 'replace').strip()[:160], ln))
            elif RX_SUM.match(line):
                f = dict(tok.split('=', 1) for tok in line.decode('ascii', 'replace').strip().split(' ')[1:] if '=' in tok)
                if all(k in f for k in SUM_KEYS):
                    r['summary'].append(dict((k, int(f[k]) if f[k].isdigit() else None) for k in SUM_KEYS))
                else:
                    r['summary_bad'] += 1
        if b'FixF21: mode=' in line:
            m = RX_F21.search(line)
            if m:
                r['f21'].append((int(m.group(1)), ln))
        if b'FixB12: mode=' in line:
            m = RX_B12.search(line)
            if m:
                r['b12'].append((int(m.group(1)), ln))
        m = RX_B13.search(line)
        if m:
            r['b13'].append((int(m.group(1)), ln))
        if r['quit_ln'] is None and M_QUIT in line:
            r['quit_ln'] = ln
        if M_FATAL in line and r['quit_ln'] is not None:
            r['fatal_after_quit'] += 1
        if r['entry_ln'] is None and line.rstrip(b'\r\n').endswith(lvl):
            r['entry_ln'] = ln
        if r['first_guest_ln'] is None and b'GuestOut' in line:
            r['first_guest_ln'] = ln
        if b'[Vulkan][E]' in line:
            r['vke'] += 1
        if line.startswith(b'GamePatch:'):
            r['gamepatch'] += 1
        if r['fork'] is None and M_FORK in line:
            r['fork'] = line.decode('ascii', 'replace').strip()[:160]
        if line.startswith(b'ShaderSeed: compatibility=') and len(r['sig']) < 4:
            mm = SEED.search(line)
            r['sig'].append(mm.group(1).decode('ascii') if mm else '?')
        if line.startswith(b'Shader translation cache: ') and len(r['variant_dir']) < 4:
            r['variant_dir'].append(line.decode('ascii', 'replace').strip().replace('\\', '/').rsplit('/', 1)[-1])
        for dm in DEATH:
            if dm in line and len(r['death']) < 20:
                r['death'].append(dm.decode())
        if b'Recovering Vulkan swapchain' in line:
            r['recovering'] += 1
        mw = RX_WIN.search(line)
        if mw:
            k = mw.group(1).decode()
            r['win'][k] = r['win'].get(k, 0) + 1
            if k == 'minimized':
                r['minimized'] += 1
    r['lines'] = ln
    fh.close()
    return r


def stdout_scan(path):
    if not path or not os.path.exists(path):
        return None
    death = []
    with open(path, 'rb') as f:
        for line in f:
            for dm in DEATH:
                if dm in line and len(death) < 20:
                    death.append(dm.decode())
    return dict(death=death)


def scene(x):
    ent = x['entry_ln']
    i = None
    if ent is not None:
        for j, (n, dt, draws, ln) in enumerate(x['ft']):
            if ln > ent and draws is not None and draws >= 100:
                i = j
                break
    after = x['ft'][i + 1:] if i is not None else []
    hold = sum(dt for (n, dt, d, ln) in after)
    ge1 = sum(1 for (n, dt, d, ln) in after if dt >= K2_US)
    return i, hold, ge1, dict(first_scene_n=None if i is None else x['ft'][i][0], hold_s=round(hold / 1e6, 1), frames_ge1s=ge1,
                               scene_frames=len(after), max_dt=max([dt for (n, dt, d, ln) in after] or [0]))


def events_of(x):
    """S1..S4 of the tag: the first dcc_stale line after the entry with (image, dcc) of S<k>, its class, apply and first_exec lines."""
    out = []
    for lab, img, dcc, fill, size in FS12_KEYS:
        e = None
        for d in x['ds']:
            if d['scene'] and d['image'] == img and d['dcc'] == dcc:
                e = d
                break
        st = [s for s in x['stale'] if s['scene'] and s['image'] == img and s['dcc'] == dcc]
        row = dict(k=int(lab[1]), label=lab, image=img, dcc=dcc, found=e is not None, stale_lines=len(st),
                   stale_fill_size_ok=all(s['fill'] == fill and s['size'].lstrip('0') == size for s in st),
                   occurrences=sum(1 for d in x['ds'] if d['scene'] and d['image'] == img and d['dcc'] == dcc))
        if e is not None:
            cls = class_of(e['fix'], e['why'])
            ap = [a for a in x['da'] if a['n'] == e['n'] and a['dcc'] == dcc]
            cl = [a for a in ap if a['result'] == 'cleared']
            fx = [f for f in x['fx'] if f['n'] == e['n'] and f['dcc'] == dcc]
            row.update(n=e['n'], present=e['present'], gpu=e['gpu'], site=e['site'], exact=e['exact'], fix=e['fix'], why=e['why'],
                       extent=e['extent'], cls=cls, mark=cls in MARK, allowed=cls in ALLOWED,
                       cleared=[dict(present=a['present'], gpu=a['gpu'], image=a['image'], site=a['site']) for a in cl],
                       declined=sum(1 for a in ap if a['result'] == 'declined'), dropped=[a['site'] for a in ap if a['result'] == 'dropped'],
                       first_exec=[dict(present=f['present'], image=f['image'], site=f['site']) for f in fx],
                       no_apply=(cls in MARK and not cl),
                       exec_present=(e['present'] if cls == 'kept_applied' else (cl[0]['present'] if cl else None)))
        out.append(row)
    return out


def identities(x, fix_on, tint_on):
    """(member rows [(text, ok)], limit flag, letter rows)."""
    rows = []
    bad = []
    for d in x['f5']:
        if d['f26_kept_applied'] > d['f26_kept'] or d['f26_deferred_declined'] > d['f26_kept']:
            bad.append('ln %d kept_applied %d declined %d > kept %d' % (d['ln'], d['f26_kept_applied'], d['f26_deferred_declined'],
                                                                         d['f26_kept']))
        if fix_on and d['f26_kept'] != d['dcc_stale_bucket_only']:
            bad.append('ln %d f26_kept %d != dcc_stale_bucket_only %d' % (d['ln'], d['f26_kept'], d['dcc_stale_bucket_only']))
        if not fix_on and any(d[n] for n in F26C):
            bad.append('ln %d f26_* != 0 at =0' % d['ln'])
        if not tint_on and any(d[n] for n in TINT):
            bad.append('ln %d f26_tint_* != 0 at TINT=0' % d['ln'])
    rows.append(('every DiagF5 line: f26_kept_applied, f26_deferred_declined <= f26_kept; %s; %s (%d lines, unparsable %d; bad %s)' % (
        'f26_kept = dcc_stale_bucket_only' if fix_on else 'f26_* = 0', 'f26_tint_* = 0' if not tint_on else 'tint free',
        len(x['f5']), x['f5_bad'], bad[:2]), not bad and x['f5_bad'] == 0 and len(x['f5']) >= 1))
    if not fix_on:
        rows.append(('KYTY_FIX_F26=0: 0 dcc_stale_apply lines (%d)' % len(x['da']), len(x['da']) == 0))
    if not tint_on:
        rows.append(('KYTY_F26_TINT=0: 0 F26Tint lines (%d, unparsable %d)' % (len(x['tint']), x['tint_bad']),
                     len(x['tint']) == 0 and x['tint_bad'] == 0))
    last = x['f5'][-1] if x['f5'] else None
    limit = any(d['n'] >= LIM_DCC for d in x['ds'])
    cut = last['ln'] if last else None
    ds_v = [d for d in x['ds'] if cut is not None and d['ln'] < cut]
    da_v = [a for a in x['da'] if cut is not None and a['ln'] < cut]

    def counts(ds, da):
        return dict(f26_kept=sum(1 for d in ds if d['fix'] in ('kept', 'kept_applied')),
                    f26_kept_applied=sum(1 for d in ds if d['fix'] == 'kept_applied') + sum(1 for a in da if a['result'] == 'cleared'),
                    f26_exact_stale=sum(1 for d in ds if d['fix'] == 'exact_stale'),
                    f26_fallback=sum(1 for d in ds if d['fix'] == 'fallback'),
                    f26_deferred_declined=sum(1 for a in da if a['result'] == 'declined'))
    cv, cl = counts(ds_v, da_v), counts(x['ds'], x['da'])
    adopt_applied = sum(1 for d in x['ds'] if d['site'] == 'adopt' and d['fix'] == 'kept_applied')
    per_n = {}
    for a in x['da']:
        if a['result'] == 'cleared':
            per_n[a['n']] = per_n.get(a['n'], 0) + 1
    marks = sum(1 for d in x['ds'] if class_of(d['fix'], d['why']) in MARK)
    cleared = sum(per_n.values())
    if last is None:
        rows.append(('line counts = the last DiagF5 line: no DiagF5 line', False))
    elif limit:
        rows.append(('line counts = the last DiagF5 line: LIMIT (dcc_stale n = 256) - not a member', True))
    else:
        diff = ['%s lines %d != %d' % (k, cv[k], last[k]) for k in F26C if cv[k] != last[k]]
        rows.append(('line counts (lines before the last DiagF5 line, variant 502 (b)) = the last DiagF5 line (%s)' % (diff[:3] or 'equal'),
                     not diff))
    rows.append(('site=adopt fix=kept_applied lines 0 (%d)' % adopt_applied, adopt_applied == 0))
    rows.append(('cleared lines <= events of a MARK class (%d <= %d), at most one per n (%s)' % (
        cleared, marks, sorted(n for n, c in per_n.items() if c > 1)[:3] or 'yes'), cleared <= marks and all(c <= 1 for c in per_n.values())))
    letter = dict(counts_whole_log=cl, counts_last_line=None if last is None else dict((k, last[k]) for k in F26C),
                  cleared_prepare=sum(1 for a in x['da'] if a['result'] == 'cleared' and a['site'] == 'prepare'),
                  decode_events=sum(1 for d in x['ds'] if d['fix'] == 'kept' and d['why'] == 'decode'))
    letter['f45a_letter_cleared_prepare_le_decode'] = letter['cleared_prepare'] <= letter['decode_events']
    return rows, limit, letter


def members(tag, x, att, idx_n, so):
    k = knobs(tag)
    fix_on = k['KYTY_FIX_F26'] == '1'
    tint_on = 'KYTY_F26_TINT' in k
    g = x['first_guest_ln']
    i, hold, ge1, info = scene(x)
    death = x['death'] + ((so or {}).get('death') or [])
    m = [('hold >= 300 s after the first scene frame (%.1f s)' % (hold / 1e6), hold >= HOLD_V_US),
         ('0 death markers (log and stdout) %s' % death[:3], not death and so is not None),
         ('video index records >= 3000 (%s)' % idx_n, (idx_n or 0) >= VIDEO_MIN)]
    if fix_on:
        ok = bool(x['f26_any']) and x['f26_bad'] == 0 and g is not None and x['f26_any'][0][1] < g
        m.append(("'FixF26: mode=1' (every FixF26 line exactly) before the first GuestOut (%s; bad %d; first GuestOut %s)" % (
            x['f26_any'][:2], x['f26_bad'], g), ok))
    else:
        m.append(("KYTY_FIX_F26=0: 0 lines 'FixF26:' (%d)" % len(x['f26_any']), not x['f26_any']))
    if tint_on:
        wm, wk = int(k['KYTY_F26_TINT']), hexnum(k['KYTY_F26_TINT_DCC'])
        ok = (bool(x['tint']) and x['tint_bad'] == 0 and all(t[0] == wm and int(t[1], 16) == wk for t in x['tint']) and g is not None
              and x['tint'][0][2] < g)
        m.append(("'F26Tint: mode= dcc=' = env as numbers (mode %d, key 0x%x) before the first GuestOut (%s; bad %d)" % (
            wm, wk, x['tint'][:2], x['tint_bad']), ok))
    else:
        ta = [d['f26_tint_applied'] for d in x['f5']]
        m.append(("no tint: 0 lines 'F26Tint:' (%d, bad %d) and f26_tint_applied 0 on every DiagF5 line (max %s)" % (
            len(x['tint']), x['tint_bad'], max(ta) if ta else None), not x['tint'] and x['tint_bad'] == 0 and bool(ta) and max(ta) == 0))
    ev = events_of(x)
    keys_ok = all(e['found'] and e['stale_fill_size_ok'] for e in ev)
    m.append(('the 4 keys S1..S4 after the entry line: dcc_stale (image, dcc) found %s; fill/size of the stale lines of the key equal '
              '(executor reading) %s' % ([e['found'] for e in ev], [e['stale_fill_size_ok'] for e in ev]), keys_ok))
    sites_ok = all(d['site'] in ('prepare', 'adopt') for d in x['ds']) and x['ev_bad'] == 0
    m.append(('field site= on every dcc_stale line; unparsable DiagF5Ev dcc lines 0 (%d; first %s)' % (x['ev_bad'], x['ev_bad_first']),
              sites_ok))
    m.append(("0 'skipped draw' lines in the whole log (%d; first %s)" % (x['skipped'], x['skipped_first']), x['skipped'] == 0))
    idr, limit, letter = identities(x, fix_on, tint_on)
    m += [('identity: ' + a, b) for a, b in idr]
    info.update(limit=limit, identities_letter=letter)
    return m, info, ev


def form_rows(x, att):
    g = x['first_guest_ln']
    return dict(fixf21=x['f21'][:2], fixb12=x['b12'][:2], fixb13=x['b13'][:2], quit_ln=x['quit_ln'], fatal_after_quit=x['fatal_after_quit'],
                logasync_mode=[t[:30] for t, l in x['mode'][:2]], logasync_mode_before_guest=bool(x['mode']) and g is not None and
                x['mode'][0][1] < g, summary=x['summary'][-1] if x['summary'] else None, close_killed=att.get('close_killed'),
                close_rc=att.get('close_rc'), close_s=att.get('close_s'))


def paths(tag, base=None):
    names = ('installed_before', 'installed_after', 'manifest_cmp', 'glitch', 'installed_sha', 'level', 'sheet')
    if base is not None:
        p = dict((nm, os.path.join(base, nm + '.txt')) for nm in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'), bin=os.path.join(base, 'bin.exe'))
        return p
    d = os.path.join(G, 'runs', tag)
    p = dict((nm, os.path.join(d, nm + '.txt')) for nm in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % tag), stdout=os.path.join(G, 'stdout_%s.txt' % tag), run=os.path.join(G, '%s.json' % tag),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % tag), seal=SEAL_PATH, bin=BIN_PATH)
    return p


def read_tag(tag, p):
    res = dict(tag=tag, base=base_of(tag), level=SKY, reader_sha256=sha_file(os.path.abspath(__file__)), knobs=knobs(tag))
    run = json.load(open(p['run'], encoding='utf-8')) if os.path.exists(p['run']) else None
    jbin = (run or {}).get('binary_sha256')
    res['binary_sha256'] = jbin
    inst_b = (text(p['installed_before']) or '').strip() or None
    inst_a = (text(p['installed_after']) or '').strip() or None
    inst_t = (text(p['installed_sha']) or '').strip() or None
    seal_sha = sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    env = (run or {}).get('env') or {}
    cmd = (run or {}).get('cmdline') or []
    att = ((run or {}).get('attempts') or [{}])[-1]
    mcmp = (text(p['manifest_cmp']) or '').strip().splitlines()
    hlev = (text(p['level']) or '').strip() or None
    ga = (run or {}).get('guest_args') or ''
    have_log = os.path.exists(p['log'])
    x = scan(p['log']) if have_log else None
    kenv = dict((k, v) for k, v in env.items() if k.startswith(('KYTY_', 'VK_')))
    ebad = env_diff(kenv, expected_env(tag))
    test_keys = sorted(k for k in env if k.startswith('KYTY_TEST_'))
    so = stdout_scan(p['stdout'])
    adm = [
        ('tag json present', run is not None),
        ('json binary_sha256 = T 9c1b268f (%s)' % (jbin or '-')[:16], jbin == BIN_TAG),
        ('installed during the tag = T 9c1b268f (%s)' % (inst_t or '-')[:16], inst_t == BIN_TAG),
        ('installed before = after = FS13 abab2196 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),
         inst_b == BIN_INST and inst_a == BIN_INST),
        ('json prereg sha256 = seal sha256 (%s / %s)' % ((pre or '-')[:16], (seal_sha or '-')[:16]), pre is not None and pre == seal_sha),
        ('env = the form of the tag (%s)' % (ebad[:6] or 'exact'), run is not None and not ebad),
        ('no KYTY_TEST_* in the env (%s)' % (test_keys or 'none'), run is not None and not test_keys),
        ('last --vulkan-validation false (%s)' % last_flag(cmd, '--vulkan-validation'), last_flag(cmd, '--vulkan-validation') == 'false'),
        ('last --shader-validation false (%s)' % last_flag(cmd, '--shader-validation'), last_flag(cmd, '--shader-validation') == 'false'),
        ('no --rd', run is not None and '--rd' not in cmd),
        ('guest args -lvl %s (%s; harness %s)' % (SKY, ga, hlev), ga == '-lvl ' + SKY and hlev == SKY),
        ('hold option %d s (%s)' % (HOLD_OPT, (run or {}).get('hold_s')), (run or {}).get('hold_s') == HOLD_OPT),
        ('log present', have_log),
        ('stdout present', so is not None),
        ('entry outcome ok (%s)' % att.get('outcome'), att.get('outcome') == 'ok'),
        ('entry line present (%s)' % (x or {}).get('entry_ln'), x is not None and x['entry_ln'] is not None),
        ('window events: minimized %s, Recovering Vulkan swapchain %s (all %s)' % ((x or {}).get('minimized'), (x or {}).get('recovering'),
                                                                                  (x or {}).get('win')),
         x is not None and x['minimized'] == 0 and x['recovering'] == 0),
        ('translation signature 9177b426 and cache dir %s (%s / %s)' % (VARIANT_DIR, [z[:8] for z in (x or {}).get('sig') or []],
                                                                       (x or {}).get('variant_dir')),
         x is not None and x['sig'] == [SIG] and x['variant_dir'] == [VARIANT_DIR]),
        ('no GamePatch: line (%s)' % (x or {}).get('gamepatch'), x is not None and x['gamepatch'] == 0),
        ('no DiagB32 line (%s)' % (x or {}).get('diagb32'), x is not None and x['diagb32'] == 0),
        ('no TestLogStall line (%s)' % (x or {}).get('stall_lines'), x is not None and x['stall_lines'] == 0),
        ('caches returned (manifest_cmp: %s)' % (mcmp[0][:40] if mcmp else '-'), bool(mcmp) and mcmp[0].startswith('manifest cmp EQUAL')),
    ]
    if x is not None:
        adm.append(('summary line LogAsync: full_waits= present once, all fields (%d, bad %d) - absent: killed (item 615 (b)(6))' % (
            len(x['summary']), x['summary_bad']), len(x['summary']) == 1 and x['summary_bad'] == 0))
    idx_n = None
    idx_last = None
    if os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as fi:
            for raw in fi:
                parts = raw.split()
                if len(parts) >= 2:
                    idx_n = (idx_n or 0) + 1
                    idx_last = int(parts[1])
    res['members'] = None
    res['events'] = None
    res['info'] = None
    if x is not None:
        m, info, ev = members(tag, x, att, idx_n, so)
        res['members'] = [[a, bool(b)] for a, b in m]
        res['events'] = ev
        res['info'] = info
        adm += [('702 (g)(4): ' + a, b) for a, b in m]
    res['admission'] = [[a, bool(b)] for a, b in adm]
    admitted = all(b for _, b in adm)
    res['status'] = 'ADMITTED' if admitted else 'NOT_ADMITTED'
    res['admitted'] = admitted
    res['failed'] = [a for a, b in adm if not b]
    gl = None
    gt = text(p['glitch'])
    if gt:
        mg = RX_GL.search(gt)
        gl = int(mg.group(1)) if mg else None
    sheet = (text(p['sheet']) or '').strip()[:120] or None
    binv = VERSION in open(p['bin'], 'rb').read() if os.path.exists(p['bin']) else None
    res['idx'] = dict(records=idx_n, last_present=idx_last)
    res['ref'] = dict(glitches=gl, sheet=sheet, bin_version_string=binv, fork_line=(x or {}).get('fork'), lines=(x or {}).get('lines'),
                      vke=(x or {}).get('vke'), env_keys=sorted(kenv), outcome=att.get('outcome'), hold_exit=att.get('hold_exit'))
    if x is not None:
        last = x['f5'][-1] if x['f5'] else None
        res['rows'] = dict(
            stale_lines_before=sum(1 for s in x['stale'] if not s['scene']), stale_lines_after=sum(1 for s in x['stale'] if s['scene']),
            dcc_stale_after=[dict((k, d[k]) for k in ('n', 'present', 'gpu', 'site', 'image', 'dcc', 'exact', 'fix', 'why'))
                             for d in x['ds'] if d['scene']][:40],
            dcc_stale_before=sum(1 for d in x['ds'] if not d['scene']),
            apply=[dict((k, a[k]) for k in ('n', 'present', 'gpu', 'image', 'dcc', 'result', 'layers', 'site')) for a in x['da']][:60],
            first_exec=[dict((k, f[k]) for k in ('n', 'present', 'dcc', 'image', 'site')) for f in x['fx']][:60],
            last_f5=None if last is None else dict((k, last[k]) for k in F26C + TINT + ['frame', 'dcc_stale_bucket_only']),
            diagf5id_mode=x['id_mode'][:2], f26tint_lines=x['tint'][:3], form_fs12_v=form_rows(x, att))
    else:
        res['rows'] = None
    res['reading'] = ('ADMITTED (no verdict; reading - F46d by item 702 (d))' if admitted else
                      'NOT_ADMITTED: %s' % res['failed'][:3])
    return res


def rows_out(res):
    out = ['tag %s (base %s, level %s)  reader sha256 %s' % (res['tag'], res['base'], res['level'], res['reader_sha256'])]
    out.append('  knobs %s' % ' '.join('%s=%s' % kv for kv in sorted(res['knobs'].items())))
    out.append('  ADMISSION %s; STATUS %s' % ('PASS' if res['admitted'] else 'FAIL', res['status']))
    for a, b in res['admission']:
        out.append('    [%s] %s' % ('ok' if b else 'NO', a))
    out.append('  binary_sha256 %s' % res['binary_sha256'])
    for e in res['events'] or []:
        if not e['found']:
            out.append('  EVENT %s image %s dcc %s: NOT FOUND after the entry' % (e['label'], e['image'], e['dcc']))
            continue
        out.append('  EVENT %s n %d present %d gpu %d site %s fix %s why %s class "%s" allowed %s NO_APPLY %s exec_present %s cleared %s '
                   'declined %d dropped %s first_exec %s occurrences %d stale_lines %d' % (
                       e['label'], e['n'], e['present'], e['gpu'], e['site'], e['fix'], e['why'], e['cls'], e['allowed'], e['no_apply'],
                       e['exec_present'], [c['present'] for c in e['cleared']], e['declined'], e['dropped'],
                       [(f['present'], f['site']) for f in e['first_exec']], e['occurrences'], e['stale_lines']))
    if res['info'] is not None:
        out.append('  INFO %s' % json.dumps(res['info'], sort_keys=True, default=list)[:1400])
    if res['rows'] is not None:
        r = res['rows']
        out.append('  ROW stale pending lines before / after the entry: %d / %d; dcc_stale lines before the entry %d; last DiagF5 %s' % (
            r['stale_lines_before'], r['stale_lines_after'], r['dcc_stale_before'], r['last_f5']))
        out.append('  ROW DiagF5Id mode %s; F26Tint %s; form fs12_v %s' % (r['diagf5id_mode'], r['f26tint_lines'],
                                                                       json.dumps(r['form_fs12_v'], sort_keys=True)[:400]))
    out.append('  IDX %s' % res['idx'])
    out.append('  REFERENCE: %s' % json.dumps(res['ref'], sort_keys=True))
    out.append('  READING %s' % res['reading'])
    return out


def table(rd):
    out = ['| tag | status | S1 class | S2 class | S3 class | S4 class | NO_APPLY | hold_s | idx | glitches | f26_tint_applied |',
           '|' + '---|' * 11]
    if os.path.isdir(rd):
        for t in sorted(os.listdir(rd)):
            js = os.path.join(rd, t, 'read.json')
            if TAG_RX.match(t) and os.path.exists(js):
                r = json.load(open(js, encoding='utf-8'))
                ev = r.get('events') or []
                cl = [(e.get('cls') if e.get('found') else 'NOT FOUND') for e in ev] + ['-'] * (4 - len(ev))
                na = [e['label'] for e in ev if e.get('no_apply')]
                lf = (r.get('rows') or {}).get('last_f5') or {}
                out.append('| %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |' % (
                    t, r['status'], cl[0], cl[1], cl[2], cl[3], na or '-', (r.get('info') or {}).get('hold_s'), r['idx']['records'],
                    r['ref']['glitches'], lf.get('f26_tint_applied')))
    return out


def main(argv):
    if '--table' in argv:
        rd = argv[argv.index('--runs') + 1] if '--runs' in argv else os.path.join(G, 'runs')
        print('reader f46c_read.py sha256 %s' % sha_file(os.path.abspath(__file__)))
        for l in table(rd):
            print(l)
        return 0
    js = argv[argv.index('--json') + 1] if '--json' in argv else None
    if '--dir' in argv:
        tag = argv[argv.index('--tag') + 1]
        p = paths(tag, argv[argv.index('--dir') + 1])
    else:
        tag = argv[0] if argv else ''
        p = paths(tag)
    if not TAG_RX.match(tag):
        print('usage: f46c_read.py <tag> | --dir D --tag T | --table')
        return 2
    res = read_tag(tag, p)
    for l in rows_out(res):
        print(l)
    if js:
        with open(js, 'w', encoding='ascii', newline='\n') as f:
            json.dump(res, f, ensure_ascii=True, sort_keys=True, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
