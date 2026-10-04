"""Track S, link S12c (HPP-496; ROADMAP "SESSION 122" item 408 (l) S12c, item 414 (b), (g)(2), item 419 (v) Z1-Z3): the scorer of the
shipping arms of S-pcw on the S12 copy adb0c82f - s12_w, s12_v, the blob growth pair s12_gw / s12_gr, the reference s12_v0.
Seal pred/08_s.md; harness s12/go_s12.sh.  ASCII only (item 175 (v)).  Logs are read as streams in binary mode.

ARMS (constants below; the harness takes them from --plan):
  s12_w   W Sky Garden, validation of item 295 (b): --vulkan-validation true, VK_LAYER_PATH, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=100000000,
          no VK_LAYER_MESSAGE_ID_FILTER, precache by default, no video; caches as found (copied before, returned after); hold 310.
          Members: entered; hold >= 300 s after the first scene frame; 0 [Vulkan][E] (log and stdout); [Vulkan][W] > 0 (positive
          control of the layer); 0 layer limit lines; DualSrcBlend: supported=1 enabled=1 before the first line carrying GuestOut;
          0 death markers.
  s12_v   V Sky Garden, video, caches as found, hold 330.  Members: entered; hold >= 300 s; video index records >= 3000; 0 one-frame
          glitches (s51_vidglitch.py 4 6); the sheet made; 0 death markers; 0 frames >= 1 s after the first scene frame.
  s12_gw  hero_kratos, class T, full return (snap0 + snap0_drv: the form APP - precache by default, no salt), video, hold 330; after
          the arm the app caches and GLCache are copied to s12/app_post/s12_gw and s12/glc_post/s12_gw.  Members: entered;
          PipelineCache/PPSA21564.bin present in the post manifest, its sha256 != snap0 (cc5b747c) and its size > 94 435 713; 0 death
          markers.  Z2: the manifest names PPSA21564.bin (present, sha, size) and PPSA21564.bin.tmp (present); ".bin absent, .tmp
          present" = INTERFERENCE of the run (window (g) of the review), not a member outcome.
  s12_gr  hero_kratos, class T, integrity (the form pcw_int: app and GLCache restored from the post copies of s12_gw, no snapshot),
          video, hold 120.  Members (Z1): exactly one line "Vulkan pipeline cache: loading", exactly one "loaded N bytes"; 0 lines
          initializing / initialized empty / invalidating / driver rejected / disabled (one row each); N = the last "saved N bytes"
          of s12_gw; N = the size of PPSA21564.bin in the post manifest of s12_gw - 76 (signature + 8 bytes of the hash); without a
          loaded line the row fails with its cause named (never None); 0 death markers; 0 one-frame glitches; the sheet made.
  s12_v0  REFERENCE: s12_v with KYTY_S_PCW=0 (rows printed, word REFERENCE_PASS / REFERENCE_FAIL, not a shipping member).
Every arm names KYTY_S_PCW explicitly (Z3: s12_v0 0, the others 1) and the line "S-pcw: KYTY_S_PCW=<v> KYTY_S_PCW_FORCE_MS=0" of the
log must equal it (form of sc_s9.py).  The binary of an arm is the field binary_sha256 of <tag>.json (item 414 (b), (d)(1)); the
row installed_before is the installed binary before the arm, not the arm's binary.
DATA (not members): the save lines of every arm (saved, forced, save failed, failed to write, failed to create cache directory), the
load classes of every arm, the translation cache directories, the first PipelinePrecache line, skipped draws, frames >= 100 ms; on the
T arms (s12_gw, s12_gr) the line of item 414 (g)(2): the "AvTrace: pcw recipes" lines (count, sum / max hold_us, max lock_us) and the
held frames >= 100 ms after the first scene frame with the class of item 241 (v)(3) (sc_s.classify, unchanged) and the hold_us of
the pcw recipes lines in their groups i .. i+1 - NOT_EVALUABLE when there is none (never 0).
WORDS: NOT_EVALUABLE (a file missing, not entered, a member unreadable), NOT_ADMITTED (an admission row fails), INTERFERENCE (window
minimized, Recovering Vulkan swapchain, a GamePatch: line; s12_gw ".bin absent, .tmp present"), PASS / FAIL (REFERENCE_* for s12_v0).
ORDER: s12_w s12_v s12_gw s12_gr s12_v0; --allowed refuses (rc 6) after a made arm with a death marker or the word INTERFERENCE, and
s12_gr unless s12_gw is PASS or FAIL with its post copies recorded.
usage: sc_s12.py --plan <tag> | --allowed <tag> | --check-seal [--seal <path>] | --tag <tag> | --summary
"""
import hashlib
import importlib.util
import json
import os
import re
import sys

ROOT = 'C:/kyty/s288'
LD = 'C:/kyty/s288/s12'
PRED_PATH = 'C:/kyty/s288/pred/08_s.md'
SC_S_PATH = 'C:/kyty/s288/sc_s.py'
SC_S_SHA = '8b0e0aff407cc82ad0a98542676764b5a0c8a867266075aa81a92a09316dc5a4'
BIN_S12 = 'adb0c82f1a752805af2cebadf892ef63639eb6862fde3eb79b6dda961c611421'
INST_FS4 = '31cbfee8261f7ea51d5552670359b07682d2524954d2e828b2097ae091e2eaa5'
INST_FS5 = '631ff98723f08112755137fdb12b993aa94d3169fb872affd96c7a3c6eaa9c17'
INST_OK = (INST_FS4, INST_FS5)
SNAP_APP = 'd8ca8c8efb60b43b37c14a274a4738c83a9dc5866cc784e649e97314c5fd45c4'
SNAP_DRV = '1767ca0a975f26c1cb90eff80e6cccb959dc507f2a1178506a6ef1dbcac97028'
SNAP_BIN_SHA = 'cc5b747c5bece91e2de2ff99e4e8d8999a98bb46fa651b0220ca7074bf8f92fd'
SNAP_BIN_SIZE = 94435713
BLOB_PREFIX = 76
BLOB_NAME = 'PipelineCache/PPSA21564.bin'
TMP_NAME = 'PipelineCache/PPSA21564.bin.tmp'
SKY = 'underwater_aerial_garden'
GW_LEVEL = 'hero_kratos'
HOLD_MIN_US = 300000000
FRAMES_VIDEO = 3000
K2_US = 1000000
K3_US = 100000
SCENE_DRAWS = 100
VK_LIMIT = '100000000'
VK_LAYER = 'C:/VulkanSDK/1.4.357.0/Bin'
ORDER = ('s12_w', 's12_v', 's12_gw', 's12_gr', 's12_v0')
STOP_WORDS = ('INTERFERENCE',)
GR_SRC_WORDS = ('PASS', 'FAIL')


def arm(level, cls, mode, hold, pcw, src, sdraws, tout, rec, val, kind):
    return dict(level=level, cls=cls, mode=mode, hold=hold, pcw=pcw, src=src, sdraws=sdraws, tout=tout, rec=rec, val=val, kind=kind)


ARMS = {
    's12_w': arm(SKY, 'M', 'asis', 310, '1', '-', 300, 600, 0, 1, 'w'),
    's12_v': arm(SKY, 'M', 'asis', 330, '1', '-', 300, 480, 1, 0, 'v'),
    's12_gw': arm(GW_LEVEL, 'T', 'full', 330, '1', '-', 100, 480, 1, 0, 'gw'),
    's12_gr': arm(GW_LEVEL, 'T', 'integrity', 120, '1', 's12_gw', 100, 480, 1, 0, 'gr'),
    's12_v0': arm(SKY, 'M', 'asis', 330, '0', '-', 300, 480, 1, 0, 'v0'),
}
SEALED_NAMES = ('s12/go_s12.sh', 's12/sc_s12.py', 's12/test_sc_s12.py', 's12/mut_sc_s12.py', 's12/test_go_s12.py',
                's9/enter_scene_s9.py', 'sc_s.py', 'cachex_s.py', 'procload.py', 'idle142.py', 'fgcpu143.py', 'sheet142.py',
                'gates_default.txt', 'run_safety99.py', 'launch_run.py', 'C:/kyty/s142/sc142.py', 'C:/kyty/scripts/s51_vidglitch.py')

RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_DUAL = re.compile(rb'DualSrcBlend: supported=(\d+) enabled=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
RX_SAVED = re.compile(rb'Vulkan pipeline cache: saved (\d+) bytes')
RX_LOADED = re.compile(rb'Vulkan pipeline cache: loaded (\d+) bytes')
RX_REC = re.compile(rb'AvTrace: pcw recipes copied=(\d+) count=(\d+) lock_us=(\d+) hold_us=(\d+)')
RX_SEAL = re.compile(r'^seal: ([0-9a-f]{64}) (\S+)$')
RX_BIN = re.compile(r'^s12 binary: ([0-9a-f]{64}) (\S+)$')
M_START = b'GuestOut: Level has started: '
M_VC = b'Vulkan pipeline cache: '
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
# Z1: the load classes of the review table (4d9e8ab7 pipelineCache.cpp:4713-4786) and the save classes (:4928-4957)
LOAD_BAD = ('initializing', 'initialized empty', 'invalidating', 'driver rejected', 'disabled')
CLASSES = ('loading', 'loaded', 'initializing', 'initialized empty', 'invalidating', 'driver rejected', 'disabled',
           'saved', 'save failed', 'failed to write', 'failed to create cache directory')


def asc(s):
    return s.encode('ascii', 'replace').decode('ascii') if isinstance(s, str) else s


def sha_file(p):
    if not p or not os.path.isfile(p):
        return None
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def read_json(p):
    if not p or not os.path.isfile(p):
        return None
    with open(p, 'rb') as f:
        return json.loads(f.read().decode('utf-8'))


def plan(tag):
    a = ARMS[tag]
    return 's12 %s %s %s %d %s %s %d %d %d %d %s' % (a['level'], a['cls'], a['mode'], a['hold'], a['pcw'], a['src'], a['sdraws'],
                                                     a['tout'], a['rec'], a['val'], a['kind'])


def vc_class(rest):
    """The class of one 'Vulkan pipeline cache: ' line (rest = the text after the prefix); None for an unknown text."""
    for c in CLASSES:
        if rest.startswith(c.encode()):
            return c
    return None


def new_scan():
    return dict(lines=0, sha256=None, entry_line=None, scene_change_line=None, guest_first=None, first_scene_n=None, hold_us=0,
                k2_after=0, k3_after=0, dt_max_after=0, ft_rows=0, death=[], vke=0, vkw=0, vk_limit=0, dual=[], skipped=0, win={},
                recovering=0, gamepatch=0, spcw=[], vc=dict((c, 0) for c in CLASSES), vc_unknown=0, saved=[], loaded=[], forced=0,
                rec=[], stc=[], precache_first=None)


def scan(path, level):
    """One streaming pass over the log in binary mode; None when the log is missing."""
    if not path or not os.path.isfile(path):
        return None
    r = new_scan()
    h = hashlib.sha256()
    after_entry = in_scene = False
    with open(path, 'rb') as f:
        for raw in f:
            h.update(raw)
            r['lines'] += 1
            ln = r['lines']
            if b'FrameTrace: n=' in raw:
                m = RX_FT.search(raw)
                if m:
                    n, dt = int(m.group(1)), int(m.group(2))
                    r['ft_rows'] += 1
                    if after_entry and r['scene_change_line'] is None:
                        if not in_scene:
                            md = RX_DRAWS.search(m.group(3))
                            if md and int(md.group(1)) >= SCENE_DRAWS:
                                in_scene = True
                                r['first_scene_n'] = n
                        else:
                            r['hold_us'] += dt
                            r['dt_max_after'] = max(r['dt_max_after'], dt)
                            if dt >= K2_US:
                                r['k2_after'] += 1
                            if dt >= K3_US:
                                r['k3_after'] += 1
                continue
            if M_START in raw:
                name = raw.split(M_START, 1)[1].strip().decode('ascii', 'replace')
                if r['entry_line'] is None:
                    if name == level:
                        r['entry_line'] = ln
                        after_entry = True
                elif r['scene_change_line'] is None:
                    r['scene_change_line'] = ln
            if r['guest_first'] is None and b'GuestOut' in raw:
                r['guest_first'] = ln
            if b'DualSrcBlend:' in raw:
                m = RX_DUAL.search(raw)
                if m:
                    r['dual'].append((ln, int(m.group(1)), int(m.group(2))))
            if b'[Vulkan][' in raw:
                if b'[Vulkan][E]' in raw:
                    r['vke'] += 1
                if b'[Vulkan][W]' in raw:
                    r['vkw'] += 1
            if b'this will be the last time reporting it' in raw:
                r['vk_limit'] += 1
            if raw.startswith(b'AsyncPipelines: skipped draw'):
                r['skipped'] += 1
            if b'Recovering Vulkan swapchain' in raw:
                r['recovering'] += 1
            if raw.startswith(b'GamePatch:'):
                r['gamepatch'] += 1
            if b'Window ' in raw:
                m = RX_WIN.search(raw)
                if m:
                    k = m.group(1).decode()
                    r['win'][k] = r['win'].get(k, 0) + 1
            if raw.startswith(b'S-pcw:'):
                r['spcw'].append(raw.strip().decode('latin1'))
            if raw.startswith(M_VC):
                rest = raw[len(M_VC):]
                c = vc_class(rest)
                if c is None:
                    r['vc_unknown'] += 1
                else:
                    r['vc'][c] += 1
                    if c == 'saved':
                        m = RX_SAVED.match(raw)
                        r['saved'].append(int(m.group(1)) if m else -1)
                        if raw.rstrip().endswith(b' forced'):
                            r['forced'] += 1
                    elif c == 'loaded':
                        m = RX_LOADED.match(raw)
                        r['loaded'].append(int(m.group(1)) if m else -1)
            if raw.startswith(b'AvTrace: pcw recipes'):
                m = RX_REC.search(raw)
                if m:
                    r['rec'].append(tuple(int(m.group(i)) for i in (1, 2, 3, 4)))
            if b'Shader translation cache: ' in raw and len(r['stc']) < 8:
                r['stc'].append(raw.split(b'Shader translation cache: ', 1)[1].strip()[:200].decode('ascii', 'replace'))
            if r['precache_first'] is None and raw.startswith(b'PipelinePrecache: '):
                r['precache_first'] = raw.strip()[:200].decode('ascii', 'replace')
            for d in DEATH:
                if d in raw:
                    r['death'].append(('log', d.decode(), ln))
    r['sha256'] = h.hexdigest()
    return r


def scan_stdout(path):
    """(death markers, [Vulkan][E] lines, layer limit lines, sha256) of the emulator stdout; None when missing."""
    if not path or not os.path.isfile(path):
        return None
    death, vke, lim = [], 0, 0
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for i, raw in enumerate(f, 1):
            h.update(raw)
            if b'[Vulkan][E]' in raw:
                vke += 1
            if b'this will be the last time reporting it' in raw:
                lim += 1
            for d in DEATH:
                if d in raw:
                    death.append(('stdout', d.decode(), i))
    return dict(death=death, vke=vke, limit=lim, sha256=h.hexdigest())


def blob_state(post_dir):
    """Z2: PPSA21564.bin (present, size, sha256) and PPSA21564.bin.tmp (present) of a post copy's MANIFEST.txt."""
    p = os.path.join(post_dir, 'MANIFEST.txt')
    r = dict(manifest=os.path.isfile(p), bin=False, size=None, sha=None, tmp=False)
    if not r['manifest']:
        return r
    with open(p, 'rb') as f:
        for raw in f:
            parts = raw.decode('ascii', 'replace').strip().split(' ')
            if len(parts) != 3:
                continue
            if parts[0] == BLOB_NAME:
                r.update(bin=True, size=int(parts[1]), sha=parts[2])
            elif parts[0] == TMP_NAME:
                r['tmp'] = True
    return r


def glitches(path):
    if not path or not os.path.isfile(path):
        return None
    with open(path, 'rb') as f:
        m = RX_GL.search(f.read().decode('utf-8', 'replace'))
    return int(m.group(1)) if m else None


def sheet_made(path):
    if not path or not os.path.isfile(path):
        return False
    with open(path, 'rb') as f:
        return any(x.startswith(b'sheet: ') for x in f)


def idx_records(path):
    if not path or not os.path.isfile(path):
        return None
    with open(path, 'rb') as f:
        return sum(1 for _ in f)


def expected_env(tag, ld=LD):
    """Every KYTY_* and VK_* key of the arm's environment (enter_scene_s9.py json 'env'): value, or a path suffix."""
    a = ARMS[tag]
    e = dict(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8', KYTY_QUEUE_TRACE='1', KYTY_GUEST_ARGS='-lvl %s' % a['level'],
             KYTY_GPU_CLOCK_PIN='1', KYTY_GPU_MARKERS='0', KYTY_S_PCW=a['pcw'])
    if a['cls'] == 'T':
        e.update(KYTY_AV_TRACE='1', KYTY_SHADER_REGISTER_TRACE='1')
    if a['val']:
        e.update(VK_LAYER_PATH=VK_LAYER, VK_LAYER_DUPLICATE_MESSAGE_LIMIT=VK_LIMIT)
    paths = dict(KYTY_GATE_FILE='/gates.req', KYTY_SAMPLE_GATE='/sample.req')
    if a['rec']:
        paths['KYTY_REC'] = '/rec_%s.mp4' % tag
    return e, paths


def env_row(tag, env):
    e, paths = expected_env(tag)
    want = set(e) | set(paths)
    have = set(env)
    bad = sorted(have ^ want)
    for k, v in e.items():
        if k in env and env[k] != v:
            bad.append('%s=%s' % (k, env[k]))
    for k, suf in paths.items():
        if k in env and not (env[k] or '').replace('\\', '/').endswith(suf):
            bad.append('%s=%s' % (k, env[k]))
    return not bad, ('every KYTY_* / VK_* key = the seal' if not bad else 'differs: %s' % ', '.join(bad)[:300])


def last_value(cmd, flag):
    v = None
    for i, x in enumerate(cmd):
        if x == flag and i + 1 < len(cmd):
            v = cmd[i + 1]
    return v


def jget(d, key, sub):
    return ((d or {}).get(key) or {}).get(sub)


def admit(tag, js, cj, cjs_of, pred_sha, pred_path=PRED_PATH):
    a = ARMS[tag]
    rows = []

    def add(name, ok, detail=''):
        rows.append((name, bool(ok), str(detail)))
    at = js.get('attempts') or []
    env = js.get('env') or {}
    add('one attempt (--attempts 1, no warmup)', len(at) == 1 and at[0].get('label') == 'attempt 1', len(at))
    add('the binary of the arm (binary_sha256 of the json, item 414 (b)) = S12 adb0c82f', js.get('binary_sha256') == BIN_S12,
        (js.get('binary_sha256') or '-')[:16])
    pr = js.get('prereg') or {}
    add('prereg = the seal 08', pred_sha is not None and pr.get('sha256') == pred_sha
        and (pr.get('path') or '').replace('\\', '/') == pred_path, (pr.get('sha256') or '-')[:16])
    add('guest args -lvl %s' % a['level'], js.get('guest_args') == '-lvl %s' % a['level'], js.get('guest_args'))
    add('gates empty (shipped defaults)', js.get('gates') == '', repr(js.get('gates'))[:40])
    ok, d = env_row(tag, env)
    add('environment: every KYTY_* and VK_* key = the seal (KYTY_S_PCW=%s named, Z3)' % a['pcw'], ok, d)
    vv = last_value(js.get('cmdline') or [], '--vulkan-validation')
    add('--vulkan-validation %s' % ('true' if a['val'] else 'false'), vv == ('true' if a['val'] else 'false'), vv)
    add('hold --hold %d' % a['hold'], js.get('hold_s') == a['hold'], js.get('hold_s'))
    add('no pipeline-cache retry', not any(x.get('pipeline_cache_off') for x in at), '')
    if cj is None:
        add('cache protocol json present', False, 'missing')
        return rows
    ib = jget(cj, 'installed_before', 'sha')
    ia = jget(cj, 'installed_after', 'sha')
    add('installed binary before the arm in {FS4 31cbfee8, FS5 631ff987} (a row of the return, not the arm binary)',
        ib in INST_OK, (ib or '-')[:16])
    add('installed binary after the arm = before the arm', ib is not None and ia == ib, '%s / %s' % ((ia or '-')[:16], (ib or '-')[:16]))
    add('return_prev_ok (no guard before the arm)', jget(cj, 'return_prev', 'ok') == '1', jget(cj, 'return_prev', 'ok') or '-')
    for key in ('return_app', 'return_glc'):
        r = cj.get(key) or {}
        add('%s after the arm = its copy before the arm' % key, r.get('got') is not None and r.get('got') == r.get('expected'),
            '%s / %s' % ((r.get('got') or '-')[:16], (r.get('expected') or '-')[:16]))
    ra, rg = cj.get('restore_app') or {}, cj.get('restore_glc') or {}
    ml = jget(cj, 'man_launch_glc', 'sha')
    if a['mode'] == 'asis':
        add('caches as found: no restore before the arm', not ra and not rg, '%s %s' % (bool(ra), bool(rg)))
        add('man_launch_glc = man_pre_glc (GLCache as found)', ml is not None and ml == jget(cj, 'man_pre_glc', 'sha'),
            (ml or '-')[:16])
    else:
        if a['mode'] == 'full':
            wa, wg, what = SNAP_APP, SNAP_DRV, 'snap0 d8ca8c8e / snap0_drv 1767ca0a'
        else:
            src = cjs_of(a['src']) or {}
            wa, wg, what = jget(src, 'app_post_copy', 'sha'), jget(src, 'glc_post_copy', 'sha'), 'the post copies of %s' % a['src']
        add('restore of the app caches = %s' % what, wa is not None and ra.get('got') == wa and ra.get('expected') == wa,
            '%s / %s' % ((ra.get('got') or '-')[:16], (wa or '-')[:16]))
        add('restore of GLCache = %s' % what, wg is not None and rg.get('got') == wg and rg.get('expected') == wg,
            '%s / %s' % ((rg.get('got') or '-')[:16], (wg or '-')[:16]))
        add('man_launch_glc = restore_glc.got', ml is not None and ml == rg.get('got'), (ml or '-')[:16])
    if tag == 's12_gw':
        for key in ('app_post_copy', 'glc_post_copy'):
            add('%s recorded (s12_gr restores it)' % key, bool(jget(cj, key, 'sha')), (jget(cj, key, 'sha') or '-')[:16])
    return rows


def spcw_row(tag, sc):
    want = 'S-pcw: KYTY_S_PCW=%s KYTY_S_PCW_FORCE_MS=0' % ARMS[tag]['pcw']
    ok = len(sc['spcw']) >= 1 and all(x == want for x in sc['spcw'])
    return ('the knob line "%s" = the environment of the arm (Z3)' % want, ok, ';'.join(sc['spcw'][:2]) or 'none')


def interference(sc):
    out = []
    if sc['win'].get('minimized'):
        out.append('window minimized %d' % sc['win']['minimized'])
    if sc['recovering']:
        out.append('Recovering Vulkan swapchain %d' % sc['recovering'])
    if sc['gamepatch']:
        out.append('GamePatch: lines %d (item 342 (e))' % sc['gamepatch'])
    return out


def load_sc_s(path=SC_S_PATH, want=SC_S_SHA):
    if sha_file(path) != want:
        raise SystemExit('sc_s.py sha256 %s != %s' % (sha_file(path), want))
    spec = importlib.util.spec_from_file_location('sc_s_for_s12', path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def held_data(lp, sp, level, A=None):
    """Item 414 (g)(2): the held frames >= 100 ms after the first scene frame with the class of item 241 (v)(3) (sc_s.classify) and
    the pcw recipes lines of their groups i .. i+1.  Attribution: T-3 of sc_s and T-4 read with 'no queued line and 0 precache
    lines' as the identity (the cold variant directory has no recipes file).  None when the arm is not entered."""
    A = A or load_sc_s()
    s = A.scan_s(lp)
    std = A.scan_stdout(sp)
    eg, end, fi = A.locate(s, level)
    if fi is None:
        return None
    pre = sum(1 for e in s['pipe'] if e[2] == 'precache')
    q = s['queued']
    t3 = std['present'] and len(s['sh']) == std['shaders']
    t4 = (q is None and pre == 0) or (q is not None and pre == q[1] + q[2])
    attr_ok = bool(t3 and t4)
    prep = A.assign_prep(s)
    rows = []
    shown = 0
    for i in range(fi + 1, end):
        dt = s['rows'][i][1]
        if dt < K3_US:
            continue
        if not A.held(s, i):
            shown += 1
            continue
        c = A.classify(s, i, prep, attr_ok)
        rec = [e for e in s['pcw_rec'] if e[0] in (i, i + 1)]
        rows.append(dict(n=s['rows'][i][0], dt_ms=round(dt / 1000.0, 1), cls=c[0], attr=c[1],
                         rec_n=len(rec), rec_hold_us=sum((e[4] or 0) for e in rec),
                         rsave=any(e[0] in (i, i + 1) for e in s['rsave'])))
    return dict(attr_ok=attr_ok, t3=bool(t3), t4=bool(t4), rows=rows, shown=shown)


def fmt_held(h):
    if h is None:
        return 'NOT_EVALUABLE (not entered)'
    if not h['rows']:
        return 'NOT_EVALUABLE (no held frame >= 100 ms after the first scene frame; shown >= 100 ms %d)' % h['shown']
    return '%d held: %s; shown >= 100 ms %d; attribution %s (T-3 %s, T-4 %s)' % (
        len(h['rows']), '; '.join('n %d %.1f ms %s/%s recipes-lines %d hold_us %d%s' % (
            x['n'], x['dt_ms'], x['cls'], x['attr'], x['rec_n'], x['rec_hold_us'], ' +recipes-save' if x['rsave'] else '')
            for x in h['rows'][:12]), h['shown'], 'on' if h['attr_ok'] else 'off', h['t3'], h['t4'])


def fmt_rec(rec):
    if not rec:
        return 'NOT_EVALUABLE (no "AvTrace: pcw recipes" line)'
    hs = [x[3] for x in rec]
    return 'lines %d, hold_us sum %d max %d, lock_us max %d, copied sum %d' % (len(rec), sum(hs), max(hs), max(x[2] for x in rec),
                                                                          sum(x[0] for x in rec))


def score(tag, ld=LD, pred_path=PRED_PATH, A=None):
    a = ARMS[tag]
    k = a['kind']
    r = dict(tag=tag, kind=k, level=a['level'], admit=[], members=[], data=[], word=None, why='', death=0, binary=None,
             installed_before=None, log_sha256=None)
    js = read_json(os.path.join(ld, '%s.json' % tag))
    cj = read_json(os.path.join(ld, 'runs_s', '%s.cache.json' % tag))

    def cjs_of(t):
        return read_json(os.path.join(ld, 'runs_s', '%s.cache.json' % t))
    lp = os.path.join(ld, 'log_%s.txt' % tag)
    sp = os.path.join(ld, 'stdout_%s.txt' % tag)
    sc = scan(lp, a['level'])
    so = scan_stdout(sp)
    if js is None or sc is None or so is None:
        r['word'], r['why'] = 'NOT_EVALUABLE', 'missing: %s' % ', '.join(
            n for n, v in (('json', js), ('log', sc), ('stdout', so)) if v is None)
        return r
    r['binary'] = js.get('binary_sha256')
    r['installed_before'] = jget(cj, 'installed_before', 'sha')
    r['log_sha256'] = sc['sha256']
    pred_sha = sha_file(pred_path)
    r['admit'] = admit(tag, js, cj, cjs_of, pred_sha, pred_path) + [spcw_row(tag, sc)]
    death = sc['death'] + so['death']
    r['death'] = len(death)
    D = r['data'].append
    D('log %s sha256 %s lines %d; stdout sha256 %s' % (lp, sc['sha256'], sc['lines'], so['sha256']))
    D('entry line %s; scene change line %s; first scene frame n %s; hold %.1f s; frames >= 1 s after it %d, >= 100 ms %d (max dt_us %d)'
      % (sc['entry_line'], sc['scene_change_line'], sc['first_scene_n'], sc['hold_us'] / 1e6, sc['k2_after'], sc['k3_after'],
         sc['dt_max_after']))
    D('death markers %d %s' % (len(death), death[:3]))
    D('window %s; Recovering Vulkan swapchain %d; GamePatch lines %d; skipped draw lines %d' % (
        sc['win'] or 'none', sc['recovering'], sc['gamepatch'], sc['skipped']))
    D('Vulkan pipeline cache lines by class: %s; unknown %d' % (', '.join('%s %d' % (c, sc['vc'][c]) for c in CLASSES),
                                                                sc['vc_unknown']))
    D('saves: %d, last %s bytes, forced %d, save failed %d, failed to write %d, failed to create cache directory %d; loaded %s' % (
        len(sc['saved']), sc['saved'][-1] if sc['saved'] else None, sc['forced'], sc['vc']['save failed'],
        sc['vc']['failed to write'], sc['vc']['failed to create cache directory'], sc['loaded']))
    D('translation cache directories %s; first PipelinePrecache line %r' % (sc['stc'][:2], sc['precache_first']))
    D('[Vulkan][E] log %d stdout %d; [Vulkan][W] %d; limit lines %d / %d; DualSrcBlend %s (first GuestOut line %s)' % (
        sc['vke'], so['vke'], sc['vkw'], sc['vk_limit'], so['limit'], sc['dual'][:2], sc['guest_first']))
    vid = None
    if a['rec']:
        vid = dict(idx=idx_records(os.path.join(ld, 'rec_%s.mp4.idx' % tag)),
                   gl=glitches(os.path.join(ld, 'glitch_%s.txt' % tag)),
                   sheet=sheet_made(os.path.join(ld, 'sheet_%s.txt' % tag)))
        D('video: index records %s; one-frame glitches %s; sheet %s' % (vid['idx'], vid['gl'], vid['sheet']))
    blob = None
    if k == 'gw':
        blob = blob_state(os.path.join(ld, 'app_post', tag))
        D('Z2 manifest after the arm (app_post/%s/MANIFEST.txt %s): PPSA21564.bin present %s sha256 %s size %s; '
          'PPSA21564.bin.tmp present %s' % (tag, blob['manifest'], blob['bin'], blob['sha'], blob['size'], blob['tmp']))
    if a['cls'] == 'T':
        D('item 414 (g)(2) pcw recipes: %s' % fmt_rec(sc['rec']))
        h = held_data(lp, sp, a['level'], A)
        D('item 414 (g)(2) held frames >= 100 ms with the class of item 241 (v)(3): %s' % fmt_held(h))
    M = r['members'].append
    entered = sc['entry_line'] is not None and sc['first_scene_n'] is not None
    M(('entered (entry line of %s and a first scene frame)' % a['level'], entered))
    nodeath = not death
    if k == 'w':
        M(('hold >= 300 s after the first scene frame', sc['hold_us'] >= HOLD_MIN_US))
        M(('0 [Vulkan][E] (log and stdout)', sc['vke'] == 0 and so['vke'] == 0))
        M(('positive control of the layer: [Vulkan][W] > 0', sc['vkw'] > 0))
        M(('0 layer limit lines (log and stdout)', sc['vk_limit'] == 0 and so['limit'] == 0))
        M(('DualSrcBlend: supported=1 enabled=1 before the first GuestOut line',
           any(s == 1 and e == 1 and (sc['guest_first'] is None or ln < sc['guest_first']) for ln, s, e in sc['dual'])))
        M(('0 death markers', nodeath))
    elif k in ('v', 'v0'):
        M(('hold >= 300 s after the first scene frame', sc['hold_us'] >= HOLD_MIN_US))
        M(('video index records >= %d' % FRAMES_VIDEO, None if vid['idx'] is None else vid['idx'] >= FRAMES_VIDEO))
        M(('0 one-frame glitches', None if vid['gl'] is None else vid['gl'] == 0))
        M(('the sheet for the lead made', vid['sheet']))
        M(('0 death markers', nodeath))
        M(('0 frames >= 1 s after the first scene frame', entered and sc['k2_after'] == 0))
    elif k == 'gw':
        M(('PPSA21564.bin present after the arm (Z2)', blob['bin']))
        M(('its sha256 != snap0 cc5b747c', blob['bin'] and blob['sha'] != SNAP_BIN_SHA))
        M(('its size > snap0 %d bytes' % SNAP_BIN_SIZE, blob['bin'] and blob['size'] is not None and blob['size'] > SNAP_BIN_SIZE))
        M(('0 death markers', nodeath))
    elif k == 'gr':
        gw = scan(os.path.join(ld, 'log_s12_gw.txt'), GW_LEVEL)
        gb = blob_state(os.path.join(ld, 'app_post', 's12_gw'))
        last_saved = gw['saved'][-1] if gw and gw['saved'] else None
        D('s12_gw: last saved %s bytes (saves %s); post PPSA21564.bin size %s -> payload %s' % (
            last_saved, len(gw['saved']) if gw else None, gb['size'], None if gb['size'] is None else gb['size'] - BLOB_PREFIX))
        n = sc['loaded'][0] if len(sc['loaded']) == 1 else None
        if not sc['loaded']:
            cause = 'no loaded line: %s' % (', '.join('%s %d' % (c, sc['vc'][c]) for c in ('loading',) + LOAD_BAD
                                                       if sc['vc'][c]) or 'no load line of any class')
        else:
            cause = 'loaded %s' % sc['loaded']
        M(('exactly one "loading" line', sc['vc']['loading'] == 1))
        M(('exactly one "loaded N bytes" line (%s)' % cause, len(sc['loaded']) == 1))
        for c in LOAD_BAD:
            M(('0 "%s" lines' % c, sc['vc'][c] == 0))
        M(('N = the last "saved" of s12_gw (%s / %s)' % (n, last_saved), n is not None and last_saved is not None and n == last_saved))
        M(('N = size of PPSA21564.bin after s12_gw - %d (%s / %s)' % (BLOB_PREFIX, n, gb['size']),
           n is not None and gb['size'] is not None and n == gb['size'] - BLOB_PREFIX))
        M(('0 death markers', nodeath))
        M(('0 one-frame glitches', None if vid['gl'] is None else vid['gl'] == 0))
        M(('the sheet for the lead made', vid['sheet']))
    ref = k == 'v0'
    itf = interference(sc)
    if not all(x[1] for x in r['admit']):
        r['word'], r['why'] = 'NOT_ADMITTED', '; '.join(x[0] for x in r['admit'] if not x[1])
    elif itf:
        r['word'], r['why'] = 'INTERFERENCE', '; '.join(itf)
    elif blob is not None and not blob['bin'] and blob['tmp']:
        r['word'], r['why'] = 'INTERFERENCE', '.bin absent, .tmp present (window (g) of the review, item 419 (v) Z2)'
    elif not entered:
        r['word'], r['why'] = 'NOT_EVALUABLE', 'not entered'
    elif any(v is None for _, v in r['members']):
        r['word'], r['why'] = 'NOT_EVALUABLE', 'unread: %s' % '; '.join(x[0] for x in r['members'] if x[1] is None)
    elif all(v for _, v in r['members']):
        r['word'] = 'REFERENCE_PASS' if ref else 'PASS'
    else:
        r['word'] = 'REFERENCE_FAIL' if ref else 'FAIL'
        r['why'] = '; '.join(x[0] for x in r['members'] if not x[1])
    return r


def yn(v):
    return 'NOT_READ' if v is None else ('PASS' if v else 'FAIL')


def lines_of(r):
    out = ['ARM %s level %s kind %s: %s%s' % (r['tag'], r['level'], r['kind'], r['word'], (' (%s)' % r['why']) if r['why'] else '')]
    out.append('  binary of the arm (binary_sha256) %s; installed before %s' % (r['binary'], r['installed_before']))
    for name, ok, d in r['admit']:
        out.append('  ADMIT %s %s (%s)' % (yn(ok), name, d))
    for name, ok in r['members']:
        out.append('  MEMBER %s %s' % (yn(ok), name))
    for d in r['data']:
        out.append('  DATA %s' % d)
    return [asc(x) for x in out]


def allowed(tag, ld=LD):
    """(rc, text): 0 allowed; 6 a condition is not met (no run, report to the lead); 1 order / made."""
    if tag not in ORDER:
        return 1, 'unknown tag'
    if os.path.isfile(os.path.join(ld, '%s.json' % tag)):
        return 1, 'made'
    for t in ORDER[:ORDER.index(tag)]:
        if not os.path.isfile(os.path.join(ld, '%s.json' % t)):
            return 1, 'order: %s not made' % t
        sj = read_json(os.path.join(ld, 'runs_s', '%s.score.json' % t))
        if sj is None:
            return 6, '%s not scored' % t
        if sj.get('death'):
            return 6, 'stop: %d death markers in %s' % (sj['death'], t)
        if sj.get('word') in STOP_WORDS:
            return 6, 'stop: %s is %s (%s)' % (t, sj['word'], sj.get('why'))
    if tag == 's12_gr':
        sj = read_json(os.path.join(ld, 'runs_s', 's12_gw.score.json')) or {}
        if sj.get('word') not in GR_SRC_WORDS:
            return 6, 's12_gw is %s' % sj.get('word')
        for d in ('app_post', 'glc_post'):
            if not os.path.isfile(os.path.join(ld, d, 's12_gw', 'MANIFEST.txt')):
                return 6, 'no %s/s12_gw' % d
    return 0, 'ok'


def check_seal(seal, root=ROOT):
    rows = []
    seen = set()
    binl = None
    if not os.path.isfile(seal):
        return False, [('seal file', False, seal)]
    with open(seal, 'rb') as f:
        for raw in f:
            line = raw.decode('utf-8', 'replace').rstrip('\r\n')
            m = RX_SEAL.match(line)
            if m:
                path = m.group(2) if ':' in m.group(2) else os.path.join(root, m.group(2)).replace('\\', '/')
                got = sha_file(path)
                rows.append((m.group(2), got == m.group(1), (got or 'missing')[:16]))
                seen.add(m.group(2))
            m = RX_BIN.match(line)
            if m:
                binl = (m.group(1), m.group(2))
    for name in SEALED_NAMES:
        if name not in seen:
            rows.append((name, False, 'no seal line'))
    rows.append(('s12 binary line = BIN_S12', binl is not None and binl[0] == BIN_S12, binl))
    return all(x[1] for x in rows), rows


def main(argv):
    if '--plan' in argv:
        t = argv[argv.index('--plan') + 1]
        if t not in ARMS:
            print('unknown tag %s' % asc(t))
            return 2
        print(plan(t))
        return 0
    if '--allowed' in argv:
        t = argv[argv.index('--allowed') + 1]
        rc, txt = allowed(t, LD)
        print('ALLOWED %s: %s (%s)' % (asc(t), 'yes' if rc == 0 else 'no', asc(txt)))
        return rc
    if '--check-seal' in argv:
        seal = argv[argv.index('--seal') + 1] if '--seal' in argv else PRED_PATH
        ok, rows = check_seal(seal, ROOT)
        for name, good, d in rows:
            print(asc('SEAL %s %s (%s)' % ('ok' if good else 'BAD', name, d)))
        print('CHECK SEAL: %s' % ('OK' if ok else 'FAILED'))
        return 0 if ok else 1
    if '--tag' in argv:
        t = argv[argv.index('--tag') + 1]
        if t not in ARMS:
            print('unknown tag %s' % asc(t))
            return 2
        r = score(t, LD, PRED_PATH)
        print('\n'.join(lines_of(r)))
        os.makedirs(os.path.join(LD, 'runs_s'), exist_ok=True)
        with open(os.path.join(LD, 'runs_s', '%s.score.json' % t), 'w') as f:
            json.dump(dict(tag=t, word=r['word'], why=r['why'], death=r['death'], binary=r['binary'],
                           installed_before=r['installed_before'], log_sha256=r['log_sha256'],
                           admit=r['admit'], members=r['members'], data=r['data']), f, indent=1)
        return 0
    if '--summary' in argv:
        words = {}
        for t in ORDER:
            sj = read_json(os.path.join(LD, 'runs_s', '%s.score.json' % t))
            words[t] = (sj or {}).get('word') or 'NOT_MADE'
            print(asc('TAG %s %s binary %s installed_before %s log %s death %s' % (
                t, words[t], ((sj or {}).get('binary') or '-')[:8], ((sj or {}).get('installed_before') or '-')[:8],
                ((sj or {}).get('log_sha256') or '-')[:16], (sj or {}).get('death'))))
        pair = 'PASS' if words['s12_gw'] == 'PASS' and words['s12_gr'] == 'PASS' else 'NOT PASS'
        print('S12C (1) s12_w %s; (2) s12_v %s; (3) pair s12_gw / s12_gr %s; (4) reference s12_v0 %s' % (
            words['s12_w'], words['s12_v'], pair, words['s12_v0']))
        return 0
    print(__doc__.split('\n')[-2])
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
