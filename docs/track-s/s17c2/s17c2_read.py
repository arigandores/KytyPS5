"""Track S link S17c2 (HPP-640; ROADMAP s122 item 524 (z) K1-K6, item 561 (g)(1)-(3), (d), (e), item 565 (g), item 566 (v)(g)): the reader
of the S-replay tags of seal edition 4 on the S17a5 binary 43ef1cc1 (code c0057ccb = 9238a182 + 5bd93ea1).  Port of the S17c reader
s17c_read.py edition 3 (C:/kyty/s288/s17c) for the eight new tags of item 561 (d)(2): Sky Garden s17c_r3b, s17c_rsb, s17c_ks2, s17c_kn2;
hoover_beach s17c_c2h, s17c_n0h, s17c_r3h, s17c_e3h.  The tags carried without a repeat by item 561 (d)(1) (S17b5 PASS, item 566) are read
by edition 3 (their runs/<tag>/read.json under the edition 3 root) and appear in the table only.  Changed against edition 3:
  K4 key   - the member rb_hit / live_perms >= 0.90 and rb_live_mismatch = 0 by the LOOKUP KEY of the emulator (item 561 (g)(1)): the cache
             file name, every field of ResourceSpecialization compared by its default operator== (Buffer: 3 fields; Image: 12 fields, the
             5 padding bytes excluded; the vector lengths) and the push-data start; the raw-bytes key of edition 3 is a reference row;
  K6       - the close path member of item 566 (v) (RC1) on s17c_ks2 and the remainder member of item 565 (g) with the identity admission of
             item 566 (g) (RC2) on s17c_kn2;
  seed     - every tag runs with KYTY_SHADER_SEED=0 (item 561 (d)(3)); admission row: 0 lines 'ShaderSeed: installed' (log, stdout).
Rows and a READING word per tag, the member table; NO verdict (the lead's, S17d2 HPP-641).  Definitions - seal docs/track-s/s17c.md edition 4
(= pred/s17c2_seal.md).  Raw word values of reject lines never reach the output (item 548 (v)(2)).
usage: python s17c2_read.py <tag> [--json <out>]       read one made tag (runs/<tag>, log_<tag>.txt, <tag>.json, state/...)
       python s17c2_read.py --table                   the member table: carried tags (edition 3 reading) and the edition 4 tags
       python s17c2_read.py --k4x <live folder> <rebuilt folder> <manifest> [--stand <file> <index>]   the K4 comparison alone
  Paths: ROOT (default C:/kyty/s288/s17c2), ED3 (default C:/kyty/s288/s17c); the fixtures set S17C2_ROOT, S17C2_ED3, S17C2_SEAL,
  S17C2_BIN.  ASCII output only.
READING  NOT_ADMITTED (admission row NO: interference of the run, item 273 (z)) -> FORM_FAIL (installed binary or manifest after the return)
         -> MEMBERS_FAIL (a member NO) -> NOT_EVALUABLE (a member not determined) -> MEMBERS_PASS.  REPORT rows never change the word."""
import hashlib
import json
import os
import re
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tc_s17c  # noqa: E402
import state_s17c  # noqa: E402

ROOT = os.environ.get('S17C2_ROOT', 'C:/kyty/s288/s17c2')
ED3 = os.environ.get('S17C2_ED3', 'C:/kyty/s288/s17c')
SEAL_PATH = os.environ.get('S17C2_SEAL', 'C:/kyty/s288/s17c2/pred/s17c2_seal.md')
BIN_PATH = os.environ.get('S17C2_BIN', 'C:/kyty/s288/bin/kyty_emulator_43ef1cc1.exe')
BIN_EXPECT = '43ef1cc14ec2c116fdcce9ac71f9d854d0ec6498bd6e538fa479b1ecdf57fbb3'
VERSION = b'KytyPS5-2026-09-15-6a2987a-2337-gc0057ccb'
REV = 'c0057cc'
FS8 = '2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b'
INSTALLED_OK = (FS8,)     # the installed binary at the print (items 545, 564)
SIG1 = 'KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz:cbank:fixb26:fixb1b:fixf10:fixf19'   # KYTY_FIX_F19=1 (rebuild)
SIG0 = 'KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz:cbank:fixb26:fixb1b:fixf10'          # KYTY_FIX_F19=0 (capture)
DIR1 = 'variant_fixb26_fixb1b_fixf10_fixf19'
DIR0 = 'variant_fixb26_fixb1b_fixf10'
SKY = 'underwater_aerial_garden'
HOOVER = 'hoover_beach'
SHARE_MIN = 0.90          # item 524 (z) K4, item 531 (v)(3), item 561 (e)
HIT_MIN = 0.90            # item 524 (z) K4, item 561 (g)(1)
PREP_MAX_MS = 180000      # item 524 (z) K5, item 229 (d)(2)
VIDEO_MIN = 3000
HOLD_MIN_US = 300000000
K2_US = 1000000
KEEP_BIG = 0x10000        # item 532 (e) reference row
REJECT_KINDS = ('self', 'residual', 'base', 'big')
SPEC_BUFFER = 12          # ResourceSpecialization::Buffer: packed_stride, descriptor_format, descriptor_swizzle (3 x u32)
SPEC_IMAGE = 44           # ResourceSpecialization::Image: 8 x u32, cube, manual_depth_compare, pad 2, depth_compare_op, fmask, pad 3
ORDER = ('s17c_r3b', 's17c_rsb', 's17c_ks2', 's17c_kn2', 's17c_c2h', 's17c_n0h', 's17c_r3h', 's17c_e3h')
CARRIED = ('s17c_v0', 's17c_w0', 's17c_c2', 's17c_ca', 's17c_cc', 's17c_n0', 's17c_e3', 's17c_ew', 's17c_kc')   # item 561 (d)(1)
GROUP_ED3 = {'s17c_v0': 'K2(2)', 's17c_w0': 'K2(2)', 's17c_c2': 'K3', 's17c_ca': 'K3', 's17c_cc': 'K3', 's17c_n0': 'K4/K5',
             's17c_e3': 'K5', 's17c_ew': 'K5', 's17c_kc': 'K6'}
SEED = {'KYTY_SHADER_SEED': '0'}   # item 561 (d)(3)
R3 = {'KYTY_S_REPLAY': '3', 'KYTY_FIX_F19': '1', 'KYTY_AV_TRACE': '1'}
SPEC = {
    's17c_r3b': dict(level=SKY, form='p', hold=0, state='cat_c2', env=dict(R3), group='K4'),
    's17c_rsb': dict(level=SKY, form='p', hold=0, state='cat_c2', env=dict(R3, KYTY_S_REPLAY_TEST='spec'), group='K4'),
    's17c_ks2': dict(level=SKY, form='p', hold=0, state='cat_c2', env=dict(R3, KYTY_S_REPLAY_TEST='stop'), group='K6'),
    's17c_kn2': dict(level=SKY, form='n', hold=60, state='k_ks2', env=dict(R3), group='K6'),
    's17c_c2h': dict(level=HOOVER, form='v', hold=330, state='empty_f10', env={'KYTY_S_REPLAY': '2', 'KYTY_FIX_F19': '0'}, group='K3'),
    's17c_n0h': dict(level=HOOVER, form='v', hold=330, state='empty_f19', env={'KYTY_S_REPLAY': '0', 'KYTY_FIX_F19': '1', 'KYTY_AV_TRACE': '1'},
                     group='K4/K5'),
    's17c_r3h': dict(level=HOOVER, form='p', hold=0, state='cat_c2h', env=dict(R3), group='K4'),
    's17c_e3h': dict(level=HOOVER, form='v', hold=330, state='rb_r3h', env=dict(R3), group='K5'),
}
for _t in SPEC:
    SPEC[_t]['env'].update(SEED)
# input state -> (root of the saved state, tag): the replay folder (and for rb_r3h / k_ks2 the f19 folder) of that tag
STATE_SRC = {'cat_c2': ('ed3', 's17c_c2'), 'k_ks2': ('root', 's17c_ks2'), 'cat_c2h': ('root', 's17c_c2h'), 'rb_r3h': ('root', 's17c_r3h')}
# per level: the capture tag of the catalogue and the live (=0) tag of K4 (root, tag)
LEVEL_SRC = {SKY: dict(cat=('ed3', 's17c_c2'), live=('ed3', 's17c_n0')), HOOVER: dict(cat=('root', 's17c_c2h'), live=('root', 's17c_n0h'))}
BASE_ENV = {'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_QUEUE_TRACE': '1', 'KYTY_GPU_CLOCK_PIN': '1',
            'KYTY_GPU_MARKERS': '0'}

RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
RX_DRAWS = re.compile(rb' draws=(\d+)')
RX_WIN = re.compile(rb'Window \d+ (minimized|restored|resized|size changed|lost keyboard focus)\b')
RX_GL = re.compile(r'one-frame glitches: (\d+)')
RX_AV = re.compile(rb'AvTrace: shader (.+?) hash=0x([0-9a-fA-F]+) translate_us=')
RX_KV = re.compile(rb'([a-z_]+)=([^ \r\n]*)')
RX_PREP = re.compile(rb'ShaderPreparation: startup wait finished in (\d+) ms')
RX_CULPRIT = re.compile(r'culprit=(\d+):role(\d+):([0-9a-f]{8})->([0-9a-f]{8})')
RX_CULPRIT_RES = re.compile(r'culprit=(\d+):role(\d+)(?![0-9:])')
RX_WHY = re.compile(r'^capture reject why=(.*?) hash=(0x[0-9a-fA-F]+) words=(\d+)$')
RX_ROW = re.compile(r'((?:vs|ps|cs)_[0-9a-f]{16}_[0-9a-f]{16}\.bin)\t(\d+)\t([0-9a-f]{16})\t(\d+)\t([0-9a-f]{16})$')
M_SR = b'ShaderReplay:'
M_GUEST = b'GuestOut:'
M_START = b'GuestOut: Level has started: '
M_FORK = b'Fork build arigandores/KytyPS5 '
M_GIT = b', git = '
M_SPECFAIL = b'shader resource specialization failed'
M_SEED = b'ShaderSeed: installed'
M_QUIT = b'Event: quit'
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')


# ----------------------------------------------------------------------------------------------------------------- small helpers

def asc(s):
    return s.encode('ascii', 'replace').decode('ascii') if isinstance(s, str) else s


def text(path):
    if not path or not os.path.exists(path):
        return None
    return open(path, 'rb').read().decode('utf-8', 'replace')


def first_line(t):
    return (t or '').split('\n')[0].strip()


def sha_file(path):
    if not path or not os.path.exists(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def kv(raw):
    """'a=1 b=x' fields of a ShaderReplay line -> dict of str."""
    return dict((k.decode(), v.decode('ascii', 'replace')) for k, v in RX_KV.findall(raw))


def num(d, k):
    try:
        return int(d[k])
    except (KeyError, ValueError, TypeError):
        return None


def rev_text(raw):
    for m in (M_FORK, M_GIT):
        if m in raw:
            return raw.split(m, 1)[1].split(b',', 1)[0].strip()[:80].decode('ascii', 'replace')
    return None


def base_of(which):
    return ED3 if which == 'ed3' else ROOT


def paths(tag, base=None):
    b = base or ROOT
    d = os.path.join(b, 'runs', tag)
    p = dict((n, os.path.join(d, n + '.txt')) for n in ('installed_sha', 'installed_before', 'installed_after', 'manifest_cmp', 'glitch',
                                                       'sheet', 'state_in', 'state_out', 'state_in_name'))
    p.update(dir=d, log=os.path.join(b, 'log_%s.txt' % tag), stdout=os.path.join(b, 'stdout_%s.txt' % tag),
             run=os.path.join(b, '%s.json' % tag), idx=os.path.join(b, 'rec_%s.mp4.idx' % tag),
             state=os.path.join(b, 'state', tag), readjson=os.path.join(d, 'read.json'),
             mf_in=os.path.join(d, 'mf_in.tsv'), mf_out=os.path.join(d, 'mf_out.tsv'))
    return p


def reject_parse(body):
    """A 'capture reject why=<why> hash=<h> words=<n>' line -> dict (edition 3, item 541 (g), 548 (v)(2)); raw word values are read only into
    canon_zero and never returned."""
    d = dict(kind='?', branch=None, culprit=None, role=None, canon_zero=None, n=None, ok=None, complete=None, hash=None, words=None)
    m = RX_WHY.match(body.strip())
    if not m:
        return d
    why = m.group(1)
    d['hash'], d['words'] = m.group(2), m.group(3)
    toks = why.split()
    if toks and re.match(r'^[a-z_]+$', toks[0]):
        d['kind'] = toks[0]
    f = dict(x.split('=', 1) for x in toks[1:] if '=' in x)
    if f.get('branch') in ('addr', 'exact'):
        d['branch'] = f['branch']
    for k in ('ok', 'complete', 'n'):
        if re.match(r'^\d+$', f.get(k, '')):
            d[k] = f[k]
    c = RX_CULPRIT.search(why)
    if c:
        d['culprit'], d['role'], d['canon_zero'] = c.group(1), c.group(2), 1 if c.group(4) == '00000000' else 0
    else:
        c = RX_CULPRIT_RES.search(why)
        if c:
            d['culprit'], d['role'] = c.group(1), c.group(2)
    return d


def reject_clean(body):
    d = reject_parse(body)
    out = ['why=%s' % d['kind']]
    for k in ('branch', 'ok', 'complete'):
        if d[k] is not None:
            out.append('%s=%s' % (k, d[k]))
    if d['culprit'] is not None:
        out.append('culprit=%s:role%s' % (d['culprit'], d['role']))
    if d['canon_zero'] is not None:
        out.append('canon_zero=%d' % d['canon_zero'])
    if d['n'] is not None:
        out.append('n=%s' % d['n'])
    out.append('hash=%s words=%s' % (d['hash'], d['words']))
    return ' '.join(out)


def reject_summary(rejects):
    kinds, res = {}, {}
    for _, body in rejects:
        d = reject_parse(body)
        k = d['kind'] if d['kind'] in REJECT_KINDS else 'other'
        kinds[k] = kinds.get(k, 0) + 1
        if d['kind'] == 'residual':
            key = '%s:role%s' % (d['branch'] or 'none', d['role'] if d['role'] is not None else '-')
            res[key] = res.get(key, 0) + 1
    return dict(sorted(kinds.items())), dict(sorted(res.items()))


# ----------------------------------------------------------------------------------------------------------------- log scan

def scan(log_path, level):
    """One streaming pass over the emulator log; every row the members need.  The entry is the first 'Level has started: <level>'."""
    r = dict(lines=0, sha256=None, sr=0, mode=[], capture=[], reject=[], stand=[], rebuild=[], skipped=[], hits=[], close_req=[],
             close_joined=[], precache_no=[], prep=None, prep_line=None, stc=[], av=[], first_guest=None, entry_line=None,
             scene_change_line=None, first_scene_n=None, hold_us=0, k2_after=0, ft_rows=0, death=[], skipped_draw=0, win={}, recovering=0,
             gamepatch=0, specfail=0, rev=[], seed=0, quit=[])
    if not log_path or not os.path.exists(log_path):
        return r
    h = hashlib.sha256()
    after_entry = in_scene = False
    with open(log_path, 'rb') as f:
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
                            if md and int(md.group(1)) >= 100:
                                in_scene = True
                                r['first_scene_n'] = n
                        else:
                            r['hold_us'] += dt
                            if dt >= K2_US:
                                r['k2_after'] += 1
                    continue
            if M_SR in raw:
                r['sr'] += 1
                body = raw.split(M_SR, 1)[1].strip()
                d = kv(body)
                if body.startswith(b'mode='):
                    r['mode'].append((ln, d))
                elif body.startswith(b'capture reject '):
                    r['reject'].append((ln, body.decode('ascii', 'replace')))
                elif body.startswith(b'capture sources='):
                    r['capture'].append((ln, d))
                elif body.startswith(b'stand '):
                    r['stand'].append((ln, body.decode('ascii', 'replace'), d))
                elif body.startswith(b'rebuild skipped '):
                    r['skipped'].append((ln, d.get('reason')))
                elif body.startswith(b'rebuild '):
                    r['rebuild'].append((ln, d))
                elif body.startswith(b'hits '):
                    r['hits'].append((ln, d))
                elif body.startswith(b'close stop requested'):
                    r['close_req'].append((ln, d))
                elif body.startswith(b'close stop joined'):
                    r['close_joined'].append((ln, d))
            if b'AvTrace: shader ' in raw:
                m = RX_AV.search(raw)
                if m:
                    r['av'].append((ln, int(m.group(2), 16), m.group(1).decode('ascii', 'replace')))
            if b'PipelinePrecache: no ' in raw and raw.rstrip().endswith(b' yet'):
                r['precache_no'].append(ln)
            if r['prep'] is None and b'ShaderPreparation: startup wait finished' in raw:
                m = RX_PREP.search(raw)
                r['prep'] = int(m.group(1)) if m else None
                r['prep_line'] = ln
            if b'Shader translation cache: ' in raw:
                r['stc'].append(raw.split(b'Shader translation cache: ', 1)[1].strip()[:200].decode('ascii', 'replace'))
            rv = rev_text(raw)
            if rv is not None and len(r['rev']) < 20:
                r['rev'].append(('log', ln, rv))
            if M_START in raw:
                name = raw.split(M_START, 1)[1].strip().decode('ascii', 'replace')
                if r['entry_line'] is None:
                    if name == level:
                        r['entry_line'] = ln
                        after_entry = True
                elif r['scene_change_line'] is None:
                    r['scene_change_line'] = ln
            if r['first_guest'] is None and M_GUEST in raw:
                r['first_guest'] = ln
            if M_SEED in raw:
                r['seed'] += 1
            if M_QUIT in raw:
                r['quit'].append(ln)
            if b'AsyncPipelines: skipped draw' in raw:
                r['skipped_draw'] += 1
            if b'Recovering Vulkan swapchain' in raw:
                r['recovering'] += 1
            if b'GamePatch:' in raw:
                r['gamepatch'] += 1
            if M_SPECFAIL in raw:
                r['specfail'] += 1
            if b'Window ' in raw:
                m = RX_WIN.search(raw)
                if m:
                    k = m.group(1).decode()
                    r['win'][k] = r['win'].get(k, 0) + 1
            for dm in DEATH:
                if dm in raw:
                    r['death'].append(('log', dm.decode(), ln))
    r['sha256'] = h.hexdigest()
    return r


def stdout_scan(path):
    r = dict(present=False, death=[], sr=0, specfail=0, rev=[], sha256=None, seed=0)
    if not path or not os.path.exists(path):
        return r
    r['present'] = True
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for i, raw in enumerate(f, 1):
            h.update(raw)
            if M_SR in raw:
                r['sr'] += 1
            if M_SPECFAIL in raw:
                r['specfail'] += 1
            if M_SEED in raw:
                r['seed'] += 1
            rv = rev_text(raw)
            if rv is not None and len(r['rev']) < 20:
                r['rev'].append(('stdout', i, rv))
            for dm in DEATH:
                if dm in raw:
                    r['death'].append(('stdout', dm.decode(), i))
    r['sha256'] = h.hexdigest()
    return r


# ----------------------------------------------------------------------------------------------------------------- catalogue

def catalogue(path):
    """Offline rows of one generation file (edition 3): r_addr.py scan plus the program hashes of R-SRC and the KEEP words >= 0x10000."""
    import r_addr
    data = open(path, 'rb').read()
    base = r_addr.scan(data)
    L = r_addr.LAYOUT
    compat_size = struct.unpack_from('<I', data, L['file.compat_size'])[0]
    compat = data[L['file']:L['file'] + compat_size].decode('ascii', 'replace')
    pos = L['file'] + compat_size
    generation, _checksum, n_src, n_spec, _n_pipe = struct.unpack_from('<QQIII', data, pos)
    pos += L['body']
    hashes = []
    for _ in range(n_src):
        hashes.append(struct.unpack_from('<Q', data, pos + L['src.hash'])[0])
        sw, cw, bw = struct.unpack_from('<III', data, pos + L['src.static_words'])
        pos += L['src'] + 4 * (sw + cw + bw)
    keep_big = 0
    spec_ids = []
    for _ in range(n_spec):
        spec_ids.append(struct.unpack_from('<Q', data, pos + L['spec.spec_id'])[0])
        (n_words,) = struct.unpack_from('<I', data, pos + L['spec.words'])
        pos += L['spec']
        for k in range(n_words):
            at = pos + k * L['word']
            if data[at + L['word.role']] == 0 and struct.unpack_from('<I', data, at + L['word.value'])[0] >= KEEP_BIG:
                keep_big += 1
        pos += n_words * L['word']
    base.update(compat=compat, src_hashes=sorted(set(hashes)), keep_big=keep_big, spec_ids=spec_ids)
    return base


def catalogue_of(which, tag):
    """(generation number of replay.cur, path of its file, catalogue dict or None, error) of the saved state of a tag."""
    rp = os.path.join(paths(tag, base_of(which))['state'], 'replay')
    cur = os.path.join(rp, 'replay.cur')
    if not os.path.exists(cur):
        return None, None, None, 'no %s' % cur
    try:
        g = int(open(cur, 'rb').read().split()[0])
    except (ValueError, IndexError):
        return None, None, None, 'replay.cur unreadable'
    f = os.path.join(rp, 'replay.%d.bin' % g)
    if not os.path.exists(f):
        return g, f, None, 'generation file missing'
    try:
        return g, f, catalogue(f), None
    except (ValueError, struct.error) as e:
        return g, f, None, 'unreadable: %s' % e


# ----------------------------------------------------------------------------------------------------------------- K4 comparison

def read_manifest(path):
    """rebuild_manifest.tsv -> (header signature or None, rows [(file, index, spec_hash, start, xxh)], bad lines) (edition 3, item 532 (g))."""
    sig, rows, bad = None, [], 0
    data = open(path, 'rb').read().decode('ascii', 'replace')
    for line in data.split('\n'):
        line = line.rstrip('\r')
        if not line:
            continue
        if line.startswith('#'):
            rest = line.split(' signature ', 1)[1] if ' signature ' in line else ''
            m = RX_ROW.search(rest)
            if m:
                sig = rest[:m.start()]
                rows.append((m.group(1), int(m.group(2)), m.group(3), int(m.group(4)), m.group(5)))
            else:
                sig = rest
            continue
        m = RX_ROW.match(line)
        if m:
            rows.append((m.group(1), int(m.group(2)), m.group(3), int(m.group(4)), m.group(5)))
        else:
            bad += 1
    return sig, rows, bad


def spec_fields(spec):
    """The fields of ResourceSpecialization compared by its default operator== (item 561 (g)(1)): (buffers, images), every buffer the
    3-tuple (packed_stride, descriptor_format, descriptor_swizzle), every image the 12-tuple (numeric_class, dimension, mip_count,
    conversion_format, shader_swizzle, indirect_root, indirect_mapping_offset, indirect_search_iterations, cube, manual_depth_compare,
    depth_compare_op, fmask); the padding bytes 34-35 and 41-43 of an image are not read.  The vector lengths are part of the tuple.
    None when the bytes are not exactly two PodVec of these sizes."""
    if len(spec) < 4:
        return None
    nb = struct.unpack_from('<I', spec, 0)[0]
    o = 4 + SPEC_BUFFER * nb
    if o + 4 > len(spec):
        return None
    bufs = tuple(struct.unpack_from('<3I', spec, 4 + SPEC_BUFFER * i) for i in range(nb))
    ni = struct.unpack_from('<I', spec, o)[0]
    o += 4
    if o + SPEC_IMAGE * ni != len(spec):
        return None
    imgs = []
    for i in range(ni):
        b = spec[o + SPEC_IMAGE * i: o + SPEC_IMAGE * (i + 1)]
        imgs.append(struct.unpack_from('<8I', b, 0) + (b[32], b[33], struct.unpack_from('<I', b, 36)[0], b[40]))
    return bufs, tuple(imgs)


def perm_key(name, p, mode):
    """The key of one permutation: 'lookup' - (file, fields of operator==, push-data start), the member of item 561 (g)(1); 'raw' - (file,
    specialization bytes, start), the edition 3 key (reference).  None when the lookup fields do not parse."""
    if mode == 'raw':
        return name, p['spec'], p['start']
    f = spec_fields(p['spec'])
    return None if f is None else (name, f, p['start'])


def k4x(live_dir, rb_dir, manifest_path, stand, mode):
    """The comparison of K4 (item 524 (z); item 561 (g)(1)).  live_perms = distinct keys of the live folder (cold =0 of the same
    signature); rebuilt = the keys of the manifest rows (file, index -> that permutation of the rebuilt folder); rb_hit = live keys among
    rebuilt; rb_dead = rebuilt keys not live; rb_live_mismatch = rb_hit keys whose SPIR-V XXH3 differ.  Self-checks: every manifest row finds
    its permutation with its start and XXH3 (manifest_bad), every file parses (live_bad, rb_bad), every specialization parses into the lookup
    fields (spec_bad), signatures."""
    out = dict(ok=False, error=None, mode=mode)
    if not (os.path.isdir(live_dir) and os.path.isdir(rb_dir) and os.path.isfile(manifest_path)):
        out['error'] = 'input missing: live %s rebuilt %s manifest %s' % (os.path.isdir(live_dir), os.path.isdir(rb_dir),
                                                                         os.path.isfile(manifest_path))
        return out
    live, live_bad = tc_s17c.read_folder(live_dir)
    rb, rb_bad = tc_s17c.read_folder(rb_dir)
    sig, rows, mbad = read_manifest(manifest_path)
    live_keys = {}
    dup = spec_bad = 0
    for name, f in live.items():
        for p in f['perms']:
            k = perm_key(name, p, mode)
            if k is None:
                spec_bad += 1
                continue
            if k in live_keys:
                dup += 1
            live_keys[k] = p['spirv_xxh3']
    rb_keys = {}
    manifest_bad = 0
    row_key = {}
    for (name, index, _sh, start, xxh) in rows:
        f = rb.get(name)
        if f is None or index >= len(f['perms']):
            manifest_bad += 1
            continue
        p = f['perms'][index]
        if p['start'] != start or ('%016x' % p['spirv_xxh3']) != xxh:
            manifest_bad += 1
        k = perm_key(name, p, mode)
        if k is None:
            spec_bad += 1
            continue
        rb_keys[k] = p['spirv_xxh3']
        row_key[(name, index)] = k
    hit = [k for k in live_keys if k in rb_keys]
    mism = [k for k in hit if live_keys[k] != rb_keys[k]]
    out.update(ok=True, live_files=len(live), live_perms=len(live_keys), live_dup=dup, live_bad=len(live_bad), rb_files=len(rb),
               rb_bad=len(rb_bad), manifest_rows=len(rows), manifest_bad_lines=mbad, manifest_bad=manifest_bad, spec_bad=spec_bad,
               rebuilt=len(rb_keys), rb_hit=len(hit), rb_dead=len([k for k in rb_keys if k not in live_keys]), rb_live_mismatch=len(mism),
               manifest_sig=sig, live_sigs=sorted(set(f['signature'] for f in live.values())),
               rb_sigs=sorted(set(f['signature'] for f in rb.values())),
               hit_share=(len(hit) / len(live_keys)) if live_keys else None)
    if stand is not None:
        try:
            sk = row_key.get((stand[0], int(stand[1])))
        except (TypeError, ValueError):
            sk = None
        out['stand_in_manifest'] = sk is not None
        out['stand_in_live'] = sk is not None and sk in live_keys
        out['stand_mismatch'] = sk is not None and sk in live_keys and live_keys[sk] != rb_keys[sk]
    return out


# ----------------------------------------------------------------------------------------------------------------- K6 (items 565 (g), 566)

def first_stand(r, prefix):
    for ln, t, d in r['stand']:
        if t.startswith(prefix):
            return ln, d
    return None


def stop_facts(r):
    """The K6 rows of the stop tag from one scan: the five lines of item 566 (v), the timeout lines, the stopped rebuild line (a = its
    perms_new, its records)."""
    stopped = [(ln, d) for ln, d in r['rebuild'] if d.get('pipelines_bin') == 'stopped']
    return dict(applied=first_stand(r, 'stand stop applied'), seen=first_stand(r, 'stand stop seen'),
                timeout=sum(1 for _, t, _d in r['stand'] if t.startswith('stand stop timeout')),
                req=r['close_req'][0] if r['close_req'] else None, joined=r['close_joined'][0] if r['close_joined'] else None,
                stopped=stopped[0] if stopped else None, quit=len(r['quit']))


def close_path(f, exit_code):
    """Item 566 (v) (RC1), K6 member 'the break by the real close path' on s17c_ks2: YES only for the lines in the order stand stop applied
    processed=P records=R -> close stop requested precache_active=1 -> stand stop seen ... processed=P records=R -> rebuild ...
    pipelines_bin=stopped -> close stop joined wait_ms=..., one P in both lines and P < R, 0 stand stop timeout lines, 0 Event: quit lines,
    exit code 0.  A timeout line -> NO; any other difference (a missing line, the order, P, R, precache_active, Event: quit, the exit code)
    -> NOT DETERMINED.  -> (ok, detail)."""
    if f['timeout'] > 0:
        return False, 'stand stop timeout lines %d' % f['timeout']
    a, q, s, b, j = f['applied'], f['req'], f['seen'], f['stopped'], f['joined']
    det = 'applied %s requested %s seen %s stopped %s joined %s quit %d exit %s' % (
        a and a[0], q and q[0], s and s[0], b and b[0], j and j[0], f['quit'], exit_code)
    if None in (a, q, s, b, j):
        return None, 'missing line: ' + det
    if not (a[0] < q[0] < s[0] < b[0] < j[0]):
        return None, 'order: ' + det
    pa, ra, ps, rs = num(a[1], 'processed'), num(a[1], 'records'), num(s[1], 'processed'), num(s[1], 'records')
    if None in (pa, ra, ps, rs) or pa != ps or ra != rs or not pa < ra:
        return None, 'P/R: applied %s/%s seen %s/%s; %s' % (pa, ra, ps, rs, det)
    if q[1].get('precache_active') != '1':
        return None, 'precache_active=%s; %s' % (q[1].get('precache_active'), det)
    if f['quit'] != 0:
        return None, 'Event: quit lines %d; %s' % (f['quit'], det)
    if exit_code != 0:
        return None, 'exit code %s; %s' % (exit_code, det)
    return True, 'P %d R %d; %s' % (pa, ra, det)


def remainder(ks, kn, n_full, adm):
    """Item 565 (g) with item 566 (g) (RC2), K6 member 'the next start rebuilds the remainder' on s17c_kn2.
    ks = dict(timeout, seen (bool), a (perms_new of the stopped rebuild line of s17c_ks2), records);
    kn = dict(rebuild (a rebuild line), skipped (a rebuild skipped line), written (pipelines_bin=written), b (perms_new), records);
    n_full = dict(N (perms_new of the full rebuild of s17c_r3b), records);
    adm = dict(mf_before (manifest before s17c_ks2 = before s17c_r3b), mf_between (after s17c_ks2 = before s17c_kn2), replay_same
    (KYTY_S_REPLAY one value at the three tags), seed0 (KYTY_SHADER_SEED=0 at the three tags)) - True / False / None.
    In this order: a stand stop timeout line at s17c_ks2 -> NO; no stand stop seen or no stopped line at s17c_ks2 -> NOT DETERMINED; an
    identity admission not True -> NOT DETERMINED; s17c_kn2 without a rebuild line, with a skipped line or not written -> NO; records not equal
    at the three tags or no N -> NOT DETERMINED; else YES iff a >= 1, b >= 1 and a + b = N.  -> (ok, detail)."""
    a, b, n = ks.get('a'), kn.get('b'), n_full.get('N')
    det = 'a %s b %s N %s records ks2/kn2/r3b %s/%s/%s admission %s' % (a, b, n, ks.get('records'), kn.get('records'), n_full.get('records'),
                                                                       dict(sorted(adm.items())))
    if ks.get('timeout'):
        return False, 'stand stop timeout at s17c_ks2; ' + det
    if not ks.get('seen') or a is None:
        return None, 'no stand stop seen or no stopped rebuild line at s17c_ks2; ' + det
    if any(adm.get(k) is not True for k in ('mf_before', 'mf_between', 'replay_same', 'seed0')):
        return None, 'identity admission of item 566 (g) not met; ' + det
    if not kn.get('rebuild') or kn.get('skipped') or not kn.get('written') or b is None:
        return False, 'the next start did not rebuild (rebuild %s skipped %s written %s); %s' % (kn.get('rebuild'), kn.get('skipped'),
                                                                                                 kn.get('written'), det)
    recs = (ks.get('records'), kn.get('records'), n_full.get('records'))
    if None in recs or len(set(recs)) != 1:
        return None, 'records differ (item 565 (g)); ' + det
    if n is None:
        return None, 'no N (s17c_r3b not read); ' + det
    return (a >= 1 and b >= 1 and a + b == n), det


def files_equal(p1, p2):
    """True when both files exist and are byte-equal, False when both exist and differ, None when one is missing."""
    if not (p1 and p2 and os.path.isfile(p1) and os.path.isfile(p2)):
        return None
    return open(p1, 'rb').read() == open(p2, 'rb').read()


def run_env(tag):
    t = text(paths(tag)['run'])
    try:
        return (json.loads(t) or {}).get('env') or {} if t else None
    except ValueError:
        return None


def identity_admission():
    """Item 566 (g): the four conditions of the remainder identity -> dict of True / False / None."""
    pr, pk, pn = paths('s17c_r3b'), paths('s17c_ks2'), paths('s17c_kn2')
    envs = [run_env(t) for t in ('s17c_r3b', 's17c_ks2', 's17c_kn2')]
    if any(e is None for e in envs):
        rs = sd = None
    else:
        vals = [e.get('KYTY_S_REPLAY') for e in envs]
        rs = vals[0] is not None and len(set(vals)) == 1
        sd = all(e.get('KYTY_SHADER_SEED') == '0' for e in envs)
    return dict(mf_before=files_equal(pk['mf_in'], pr['mf_in']), mf_between=files_equal(pk['mf_out'], pn['mf_in']), replay_same=rs,
                seed0=sd)


# ----------------------------------------------------------------------------------------------------------------- members

class Rows:
    def __init__(self):
        self.adm, self.form, self.mem, self.rep = [], [], [], []

    def a(self, name, ok, detail=''):
        self.adm.append((name, ok, asc(str(detail))))

    def f(self, name, ok, detail=''):
        self.form.append((name, ok, asc(str(detail))))

    def m(self, name, ok, detail=''):
        self.mem.append((name, ok, asc(str(detail))))

    def r(self, name, detail):
        self.rep.append((name, asc(str(detail))))

    def word(self):
        if any(ok is not True for _, ok, _ in self.adm):
            return 'NOT_ADMITTED'
        if any(ok is not True for _, ok, _ in self.form):
            return 'FORM_FAIL'
        if any(ok is False for _, ok, _ in self.mem):
            return 'MEMBERS_FAIL'
        if any(ok is None for _, ok, _ in self.mem):
            return 'NOT_EVALUABLE'
        return 'MEMBERS_PASS'


def yn(ok):
    return {True: 'YES', False: 'NO', None: 'NOT DETERMINED'}[ok]


def env_rows(rows, tag, run):
    spec = SPEC[tag]
    env = (run or {}).get('env') or {}
    want = dict(BASE_ENV)
    want['KYTY_GUEST_ARGS'] = '-lvl ' + spec['level']
    want.update(spec['env'])
    kyty = dict((k, v) for k, v in env.items() if k.startswith('KYTY_'))
    bad = []
    for k, v in want.items():
        if kyty.get(k) != v:
            bad.append('%s=%s want %s' % (k, kyty.get(k), v))
    allowed = set(want) | {'KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE'} | ({'KYTY_REC'} if spec['form'] == 'v' else set())
    for k in kyty:
        if k not in allowed:
            bad.append('extra %s' % k)
    for k in ('KYTY_GATE_FILE', 'KYTY_SAMPLE_GATE'):
        if not kyty.get(k):
            bad.append('no %s' % k)
    if spec['form'] == 'v' and not kyty.get('KYTY_REC'):
        bad.append('no KYTY_REC')
    vk = sorted(k for k in env if k.startswith('VK_LAYER_'))
    if vk:
        bad.append('VK_LAYER_* %s' % vk)
    rows.a('environment = the form of the tag with KYTY_SHADER_SEED=0 (seal section 2; item 561 (d)(3); KYTY_SHADER_PREPARE absent)', not bad,
           'offending %s' % bad if bad else 'KYTY keys %s' % sorted(kyty))
    val = None
    cmd = (run or {}).get('cmdline') or []
    for i, x in enumerate(cmd):
        if x == '--vulkan-validation':
            val = cmd[i + 1] if i + 1 < len(cmd) else None
    rows.a('command line --vulkan-validation (last) = false', val == 'false', val)


def state_rows(rows, tag, p, sin):
    spec = SPEC[tag]
    name = first_line(text(p['state_in_name']))
    rows.a('input state name = %s' % spec['state'], name == spec['state'], name)
    if sin is None:
        rows.a('input state described (state_in.txt)', False, 'missing')
        return
    st = spec['state']
    f10, f19, rp = sin.get('f10', {}), sin.get('f19', {}), sin.get('replay', {})
    if st == 'empty_f10':
        rows.a('input state empty_f10: %s absent and replay absent' % DIR0, f10.get('present') is False and rp.get('present') is False,
               (f10, rp))
    elif st == 'empty_f19':
        rows.a('input state empty_f19: %s absent and replay absent' % DIR1, f19.get('present') is False and rp.get('present') is False,
               (f19, rp))
    else:
        which, src = STATE_SRC[st]
        saved = os.path.join(paths(src, base_of(which))['state'], 'replay')
        want = {}
        if os.path.isdir(saved):
            for n in sorted(os.listdir(saved)):
                fp = os.path.join(saved, n)
                if os.path.isfile(fp):
                    want[n] = (os.path.getsize(fp), sha_file(fp))
        same = rp.get('present') is True and rp.get('replay_files') == want and len(want) > 0
        rows.a('input state %s: replay = %s state/%s/replay byte for byte' % (st, which, src), same,
               'files %d / saved %d' % (len(rp.get('replay_files') or {}), len(want)))
        if st in ('cat_c2', 'cat_c2h'):
            rows.a('input state %s: %s absent (empty variant folder of the rebuild signature)' % (st, DIR1), f19.get('present') is False, f19)
        elif st == 'rb_r3h':
            rows.a('input state rb_r3h: %s present with pipelines.bin (the folder of s17c_r3h)' % DIR1,
                   f19.get('present') is True and f19.get('pipelines_bin') is True, f19)
        else:
            rows.r('input state k_ks2: %s' % DIR1, f19)


def common(tag, p, r, so, run):
    rows = Rows()
    att = ((run or {}).get('attempts') or [{}])[0] if run else {}
    rows.a('run record <tag>.json present, one attempt', run is not None and len((run or {}).get('attempts') or []) == 1,
           'attempts %s' % (len((run or {}).get('attempts') or []) if run else None))
    sha = first_line(text(p['installed_sha'])) or None
    rows.a('binary of the run = S17a5 43ef1cc1 (json and installed_sha.txt)', (run or {}).get('binary_sha256') == BIN_EXPECT and
           sha == BIN_EXPECT, '%s / %s' % ((run or {}).get('binary_sha256'), sha))
    vb = None
    if os.path.exists(BIN_PATH):
        vb = VERSION in open(BIN_PATH, 'rb').read()
    rows.a('version string %s in the binary copy' % VERSION.decode(), vb is True, vb)
    revs = r['rev'] + so['rev']
    badrev = [x for x in revs if REV not in x[2]]
    rows.a('revision texts of log / stdout name %s' % REV, not badrev and len(revs) > 0, 'texts %d, other %s' % (len(revs), badrev[:3]))
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    rows.a('prereg sha256 = the seal file (%s)' % os.path.basename(SEAL_PATH), pre is not None and pre == sha_file(SEAL_PATH),
           '%s / %s' % (pre, sha_file(SEAL_PATH)))
    env_rows(rows, tag, run)
    rows.a('0 lines ShaderSeed: installed (log, stdout; item 561 (d)(3))', r['seed'] == 0 and so['seed'] == 0,
           '%d / %d' % (r['seed'], so['seed']))
    win = r['win'].get('minimized', 0)
    rows.a('no window minimized, no Recovering Vulkan swapchain, no GamePatch line', win == 0 and r['recovering'] == 0 and
           r['gamepatch'] == 0, 'minimized %d recovering %d gamepatch %d' % (win, r['recovering'], r['gamepatch']))
    sin_t = text(p['state_in'])
    sin = state_s17c.parse(sin_t) if sin_t is not None else None
    state_rows(rows, tag, p, sin)
    rows.a('emulator log present', r['sha256'] is not None, r['sha256'])
    b = first_line(text(p['installed_before'])) or None
    a = first_line(text(p['installed_after'])) or None
    rows.f('installed binary before = after, FS8', b is not None and b == a and b in INSTALLED_OK, '%s / %s' % (b, a))
    mc = first_line(text(p['manifest_cmp']))
    rows.f('manifest of the caches after the return EQUAL', mc.startswith('manifest cmp EQUAL'), mc[:120])
    rows.r('window lines', r['win'])
    rows.r('death markers log / stdout', '%d / %d %s' % (len(r['death']), len(so['death']), (r['death'] + so['death'])[:3]))
    rows.r('skipped draw lines', r['skipped_draw'])
    rows.r('translation cache directory lines', r['stc'][:4])
    rows.r('exit', 'outcome %s detail %s hold_exit %s hold_s %s close_rc %s close_killed %s close_s %s' % (
        att.get('outcome'), att.get('detail'), att.get('hold_exit'), att.get('hold_s'), att.get('close_rc'), att.get('close_killed'),
        att.get('close_s')))
    rows.r('preparation screen (startup wait finished)', '%s ms at line %s' % (r['prep'], r['prep_line']))
    return rows, att, sin


def exit_code(att):
    """The exit code of a process that ended by itself (outcome exited, detail 'exit code <n>'), else None."""
    m = re.match(r'^exit code (-?\d+)$', str(att.get('detail') or ''))
    return int(m.group(1)) if att.get('outcome') == 'exited' and m else None


def lived(att, hold):
    return att.get('outcome') == 'ok' and att.get('hold_exit') is None and (att.get('hold_s') or 0) >= hold


def entered(r, att):
    return r['entry_line'] is not None and att.get('outcome') == 'ok'


def directory_ok(r, want):
    return len(r['stc']) >= 1 and all(x.replace(chr(92), '/').endswith(want) for x in r['stc'])


def deaths(r, so):
    return len(r['death']) + len(so['death'])


def video_rows(rows, p, r, so, group, report=False):
    add = (lambda name, ok, det: rows.r(name, '%s %s' % (yn(ok), det))) if report else rows.m
    idx_n = None
    if os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as f:
            idx_n = sum(1 for _ in f)
    add('%s video index records >= %d' % (group, VIDEO_MIN), None if idx_n is None else idx_n >= VIDEO_MIN, idx_n)
    gt = text(p['glitch'])
    gl = None
    if gt:
        m = RX_GL.search(gt)
        gl = int(m.group(1)) if m else None
    add('%s 0 one-frame glitches (s51_vidglitch.py 4 6)' % group, None if gl is None else gl == 0, gl)
    st = text(p['sheet'])
    sheet = next((x.strip() for x in st.split('\n') if x.startswith('sheet: ')), None) if st else None
    add('%s sheet of the lead made' % group, None if st is None else sheet is not None, sheet)
    add('%s 0 death markers (log, stdout)' % group, deaths(r, so) == 0, deaths(r, so))


def hold_rows(rows, r, att, hold, group, level, frame_hold=True):
    rows.m('%s entered (Level has started: %s, outcome ok)' % (group, level), entered(r, att), 'entry line %s' % r['entry_line'])
    rows.m('%s the process lived to the end of the hold (%d s)' % (group, hold), lived(att, hold),
           'outcome %s hold_exit %s hold_s %s' % (att.get('outcome'), att.get('hold_exit'), att.get('hold_s')))
    if frame_hold:
        rows.m('%s shown hold after the first scene frame >= 300 s' % group, r['hold_us'] >= HOLD_MIN_US, '%.1f s' % (r['hold_us'] / 1e6))
    rows.r('frames >= 1 s after the first scene frame', r['k2_after'])


def last_capture(r):
    stops = [d for _, d in r['capture'] if d.get('at') == 'stop']
    return stops[-1] if stops else None


def soft_close(att):
    return att.get('close_killed') is False and att.get('close_rc') is not None


def av_catalogue(r, hashes, after_line):
    if after_line is None:
        return None, None
    hs = set(hashes)
    after = [x for x in r['av'] if x[0] > after_line]
    return sum(1 for x in after if x[1] in hs), len(after)


def read_json_of(tag, which='root'):
    t = text(paths(tag, base_of(which))['readjson'])
    return json.loads(t) if t else None


def read_tag(tag):
    if tag not in SPEC:
        raise SystemExit('unknown tag %s' % tag)
    p = paths(tag)
    spec = SPEC[tag]
    lv = spec['level']
    r = scan(p['log'], lv)
    so = stdout_scan(p['stdout'])
    rt = text(p['run'])
    run = json.loads(rt) if rt else None
    rows, att, sin = common(tag, p, r, so, run)
    sout_t = text(p['state_out'])
    sout = state_s17c.parse(sout_t) if sout_t is not None else None
    extra = {}
    g = spec['group']
    if tag == 's17c_c2h':
        capture_rows(rows, tag, p, r, so, att, extra)
    elif tag == 's17c_n0h':
        hold_rows(rows, r, att, spec['hold'], 'K4/K5', lv)
        rows.m('K4 translation cache directory = %s (signature of KYTY_FIX_F19=1)' % DIR1, directory_ok(r, DIR1), r['stc'][:2])
        _g, _f, cat, cerr = catalogue_of(*LEVEL_SRC[lv]['cat'])
        n_cat, n_all = av_catalogue(r, cat['src_hashes'] if cat else [], r['prep_line']) if cat else (None, None)
        rows.m('K5 null control: translations of catalogue programs in the game > 0 (cold =0, empty variant folder)',
               None if n_cat is None else n_cat > 0, 'catalogue programs %s of new permutations %s after the preparation line %s; %s' % (
                   n_cat, n_all, r['prep_line'], cerr))
        live = os.path.join(p['state'], 'f19')
        files, bad = tc_s17c.read_folder(live) if os.path.isdir(live) else ({}, [('<folder>', 'missing')])
        rows.m('K4 live folder saved (state/s17c_n0h/f19) and every file readable', os.path.isdir(live) and not bad and len(files) > 0,
               'files %d bad %s' % (len(files), bad[:3]))
        rows.r('ShaderReplay: lines (log / stdout)', '%d / %d' % (r['sr'], so['sr']))
        video_rows(rows, p, r, so, 'control (report)', report=True)
        extra['catalogue_translations'] = n_cat
    elif tag in ('s17c_r3b', 's17c_rsb', 's17c_r3h'):
        rebuild_rows(rows, tag, p, r, so, att, extra)
    elif tag == 's17c_e3h':
        entry_rows(rows, tag, p, r, so, att, extra)
    elif tag == 's17c_ks2':
        stop_rows(rows, r, so, att, sout, extra)
    else:
        next_rows(rows, r, so, att, extra)
    return rows, dict(tag=tag, group=g, level=lv, log_sha256=r['sha256'], stdout_sha256=so['sha256'], extra=extra)


def capture_rows(rows, tag, p, r, so, att, extra):
    """K3 on the second level (item 561 (d)(2): the members of s17c_c2)."""
    hold_rows(rows, r, att, SPEC[tag]['hold'], 'K3', SPEC[tag]['level'])
    rows.a('K3 fitness: line PipelinePrecache: no <path> yet (item 532 (v))', len(r['precache_no']) >= 1, r['precache_no'][:2])
    md = r['mode'][0][1] if r['mode'] else {}
    rows.m('K3 mode line mode=2 compat=absent (a new catalogue)', md.get('mode') == '2' and md.get('compat') == 'absent', md)
    rows.m('K3 translation cache directory = %s (signature of KYTY_FIX_F19=0)' % DIR0, directory_ok(r, DIR0), r['stc'][:2])
    lc = last_capture(r)
    rows.r('capture lines (save / stop)', '%d / %d' % (sum(1 for _, d in r['capture'] if d.get('at') == 'save'),
                                                      sum(1 for _, d in r['capture'] if d.get('at') == 'stop')))
    rows.r('last capture at=stop', lc)
    kinds, res = reject_summary(r['reject'])
    rows.r('capture reject lines logged by kind', kinds)
    rows.r('residual branch:role of the first culprit (diagnostics, not a member)', res)
    rows.r('capture reject lines (first 5; committed form without raw values)', [reject_clean(x[1]) for x in r['reject'][:5]])
    rows.r('shader resource specialization failed in _kyty.txt / stdout', '%d / %d' % (r['specfail'], so['specfail']))
    g_c, gf, cat, cerr = catalogue_of('root', tag)
    rows.r('saved catalogue', 'replay.cur %s file %s error %s' % (g_c, gf and os.path.basename(gf), cerr))
    if lc is None:
        for nm in ('canon_mismatch = 0', 'canon_base = 0', 'dropped_queue = 0', 'sources > 0', 'specs > 0', 'generation file on disk',
                   'offline R_ADDR = 0'):
            rows.m('K3 %s (no capture at=stop line - not determined, item 531 (v)(3))' % nm, None)
    else:
        cm, cb = num(lc, 'canon_mismatch'), num(lc, 'canon_base')
        rows.m('K3 canon_mismatch = 0 (canon_self + canon_residual)', cm == 0, 'canon_mismatch %s self %s residual %s' % (
            cm, lc.get('canon_self'), lc.get('canon_residual')))
        rows.m('K3 canon_base = 0 (item 531 (v)(2))', cb == 0, cb)
        dq = num(lc, 'dropped_queue')
        rows.m('K3 dropped_queue = 0 (read at a soft close, item 532 (z) N4)', (dq == 0) if soft_close(att) else None,
               'dropped_queue %s soft close %s' % (dq, soft_close(att)))
        rows.m('K3 sources > 0', (num(lc, 'sources') or 0) > 0, lc.get('sources'))
        rows.m('K3 specs > 0', (num(lc, 'specs') or 0) > 0, lc.get('specs'))
        gen = num(lc, 'gen')
        rows.m('K3 generation file on disk = gen of the last capture line and readable', cat is not None and g_c == gen,
               'replay.cur %s gen %s error %s' % (g_c, gen, cerr))
        rows.m('K3 offline R_ADDR = 0 ("the role layout agrees", item 532 (e))', None if cat is None else cat['R_ADDR'] == 0,
               None if cat is None else cat['R_ADDR'])
        rows.r('canon_big, canon_self, canon_residual (reference)', '%s %s %s' % (lc.get('canon_big'), lc.get('canon_self'),
                                                                               lc.get('canon_residual')))
        rows.r('pipes, pipes_waiting (denominator of K4), catalogue_*', '%s %s %s/%s/%s' % (
            lc.get('pipes'), lc.get('pipes_waiting'), lc.get('catalogue_sources'), lc.get('catalogue_specs'), lc.get('catalogue_pipes')))
        extra['pipes_waiting'] = num(lc, 'pipes_waiting')
        extra['last_capture'] = lc
    f10 = os.path.join(p['state'], 'f10')
    if os.path.isdir(f10):
        files, bad = tc_s17c.read_folder(f10)
        sigs = sorted(set(x['signature'] for x in files.values()))
        rows.r('signature of the capture folder state/%s/f10 (reference; = %s)' % (tag, SIG0),
               'files %d bad %d signatures %s equal %s' % (len(files), len(bad), sigs, sigs == [SIG0]))
    else:
        rows.r('signature of the capture folder (reference)', 'folder not saved')
    if cat is not None:
        rows.r('KEEP words >= 0x10000 (reference)', cat['keep_big'])
        rows.r('catalogue sources / specs / pipes / words / keep', '%d %d %d %d %d' % (cat['sources'], cat['specs'], cat['pipes'],
                                                                                 cat['words'], cat['keep']))
        extra['catalogue_programs'] = len(cat['src_hashes'])
    rows.r('video (report)', 'see glitch.txt / sheet.txt')


def rebuild_rows(rows, tag, p, r, so, att, extra):
    lv = SPEC[tag]['level']
    md = r['mode'][0][1] if r['mode'] else {}
    cw, ct = LEVEL_SRC[lv]['cat']
    g_c, _f, cat, cerr = catalogue_of(cw, ct)
    rows.m('K4 mode line mode=3 compat=ok generation = replay.cur of %s' % ct, md.get('mode') == '3' and md.get('compat') == 'ok' and
           g_c is not None and num(md, 'generation') == g_c, '%s / %s %s' % (md, ct, g_c))
    rb = r['rebuild'][-1][1] if r['rebuild'] else None
    rows.m('K4 a rebuild line and no rebuild skipped line', rb is not None and not r['skipped'], 'rebuild %d skipped %s' % (
        len(r['rebuild']), r['skipped'][:1]))
    rows.m('K4 0 death markers on the rebuild tag (item 531 (d)(4))', deaths(r, so) == 0, (r['death'] + so['death'])[:3])
    rows.m('K4 the process reached the end of the preparation screen (--until-prep outcome prep)', att.get('outcome') == 'prep',
           att.get('outcome'))
    rb = rb or {}
    rows.m('K4 pipelines_bin=written', rb.get('pipelines_bin') == 'written', rb.get('pipelines_bin'))
    recs, prep, rej, pend = num(rb, 'records'), num(rb, 'prepared'), num(rb, 'rejected'), num(rb, 'pending')
    ident = None if None in (recs, prep, rej, pend) else prep + rej + pend == recs
    rows.m('K4 identity prepared + rejected + pending = records', ident, '%s + %s + %s = %s' % (prep, rej, pend, recs))
    parts = [num(rb, k) for k in ('rej_src', 'rej_fused', 'rej_key', 'rej_version', 'rej_shape', 'rej_translate', 'rej_emit', 'rej_val',
                                  'rej_write', 'rej_ref')]
    part = None if None in parts or rej is None else sum(parts) == rej
    rows.m('K4 partition of the reasons: sum rej_* (rej_ref included) = rejected', part, '%s = %s' % (parts, rej))
    cj = read_json_of(ct, cw) or {}
    pw = (cj.get('extra') or {}).get('pipes_waiting')
    share = None if (prep is None or recs is None or pw is None or recs + pw == 0) else prep / float(recs + pw)
    rows.m('K4 share prepared / (records + pipes_waiting of %s) >= 0.90 (item 531 (v)(3), item 561 (e))' % ct, None if share is None else
           share >= SHARE_MIN, 'share %s = %s / (%s + %s)' % (None if share is None else round(share, 4), prep, recs, pw))
    rows.r('pending', pend)
    rows.r('rej_ref (> 0 = code defect)', rb.get('rej_ref'))
    rows.r('records vs catalogue pipes of %s' % ct, '%s / %s' % (recs, None if cat is None else cat['pipes']))
    for k in ('perms_new', 'perms_cached', 'rb_push_moved', 'rb_spec_changed', 'groups_same_pc', 'group_sources', 'translate_ms', 'wall_ms'):
        rows.r(k, rb.get(k))
    rows.r('hits lines', [d for _, d in r['hits']][-2:])
    n_cat, n_all = av_catalogue(r, cat['src_hashes'] if cat else [], r['prep_line']) if cat else (None, None)
    rows.r('new permutations after the preparation line: catalogue programs / all (input of K5)', '%s / %s' % (n_cat, n_all))
    extra['guest_catalogue_translations'] = n_cat
    extra['rebuild'] = dict((k, rb.get(k)) for k in ('records', 'prepared', 'rejected', 'pending', 'perms_new', 'perms_cached',
                                                     'pipelines_bin'))
    lw, lt = LEVEL_SRC[lv]['live']
    live = os.path.join(paths(lt, base_of(lw))['state'], 'f19')
    rbdir = os.path.join(p['state'], 'f19')
    man = os.path.join(p['state'], 'replay', 'rebuild_manifest.tsv')
    stand = None
    if tag == 's17c_rsb':
        st = [x for x in r['stand'] if x[1].startswith('stand spec applied')]
        stand = (st[0][2].get('file'), st[0][2].get('permutation')) if st else None
    x = k4x(live, rbdir, man, stand, 'lookup')
    xr = k4x(live, rbdir, man, stand, 'raw')
    extra['k4x'] = dict((k, v) for k, v in x.items() if k not in ('live_sigs', 'rb_sigs'))
    extra['k4x_raw'] = dict((k, v) for k, v in xr.items() if k not in ('live_sigs', 'rb_sigs'))
    if not x['ok']:
        rows.m('K4 comparison with the live translation (%s): inputs present' % lt, None, x['error'])
        return
    sig_ok = x['manifest_sig'] == SIG1 and x['live_sigs'] == [SIG1] and x['rb_sigs'] == [SIG1]
    clean = x['live_bad'] == 0 and x['rb_bad'] == 0 and x['manifest_bad'] == 0 and x['manifest_bad_lines'] == 0 and x['spec_bad'] == 0
    rows.m('K4 comparison self-checks: every file readable, every manifest row found with its start and XXH3, every specialization parsed '
           'into the lookup fields, signatures = %s' % SIG1, sig_ok and clean,
           'live_bad %d rb_bad %d manifest_bad %d bad_lines %d spec_bad %d manifest_sig %s live_sigs %s rb_sigs %s' % (
               x['live_bad'], x['rb_bad'], x['manifest_bad'], x['manifest_bad_lines'], x['spec_bad'], x['manifest_sig'], x['live_sigs'],
               x['rb_sigs']))
    det = sig_ok and clean
    rows.r('lookup key: live_perms / rebuilt / rb_hit / rb_dead / rb_live_mismatch / live_dup', '%d / %d / %d / %d / %d / %d' % (
        x['live_perms'], x['rebuilt'], x['rb_hit'], x['rb_dead'], x['rb_live_mismatch'], x['live_dup']))
    rows.r('raw-bytes key (edition 3, reference): live_perms / rebuilt / rb_hit / rb_dead / rb_live_mismatch',
           '%s / %s / %s / %s / %s' % tuple(xr.get(k) for k in ('live_perms', 'rebuilt', 'rb_hit', 'rb_dead', 'rb_live_mismatch')))
    if tag in ('s17c_r3b', 's17c_r3h'):
        rows.m('K4 rb_hit / live_perms >= 0.90 by the lookup key (item 561 (g)(1))', None if not det or not x['live_perms'] else
               x['hit_share'] >= HIT_MIN, '%s / %s = %s' % (x['rb_hit'], x['live_perms'], None if x['hit_share'] is None else
                                                            round(x['hit_share'], 4)))
        rows.m('K4 rb_live_mismatch = 0 on rb_hit by the lookup key (item 561 (g)(1))', None if not det else x['rb_live_mismatch'] == 0,
               x['rb_live_mismatch'])
    else:
        st_ok = stand is not None and x.get('stand_in_live') is True
        rows.m('K4 stand spec: line stand spec applied and its (file, index) among live_perms of %s by the lookup key' % lt,
               None if not st_ok else True, 'stand %s in manifest %s in live %s' % (stand, x.get('stand_in_manifest'), x.get('stand_in_live')))
        rows.m('K4 stand spec: rb_live_mismatch > 0 by the lookup key', None if (not st_ok or not det) else x['rb_live_mismatch'] > 0,
               '%d (stand permutation differs: %s)' % (x['rb_live_mismatch'], x.get('stand_mismatch')))


def entry_rows(rows, tag, p, r, so, att, extra):
    """K5 on the second level: the members of s17c_e3 (item 561 (d)(2))."""
    lv = SPEC[tag]['level']
    hold_rows(rows, r, att, SPEC[tag]['hold'], 'K5', lv)
    sk = [x for x in r['skipped'] if x[1] == 'recipes_current']
    rows.m('K5 fitness: rebuild skipped reason=recipes_current (the folder of s17c_r3h)', len(sk) >= 1 and not r['rebuild'],
           'skipped %s rebuild lines %d' % (r['skipped'][:2], len(r['rebuild'])))
    _g, _f, cat, cerr = catalogue_of(*LEVEL_SRC[lv]['cat'])
    n_cat, n_all = av_catalogue(r, cat['src_hashes'] if cat else [], r['prep_line']) if cat else (None, None)
    r3 = read_json_of('s17c_r3h') or {}
    n0 = read_json_of('s17c_n0h') or {}
    cont = (r3.get('extra') or {}).get('guest_catalogue_translations')
    ok = None if (n_cat is None or cont is None) else (None if cont != 0 else n_cat == 0)
    rows.m('K5 translations of catalogue programs in the game = 0 (not determined when s17c_r3h translated catalogue programs after its '
           'preparation screen)', ok, 'e3h %s of %s; r3h after its preparation %s; %s' % (n_cat, n_all, cont, cerr))
    ctl = (n0.get('extra') or {}).get('catalogue_translations')
    rows.m('K5 null control s17c_n0h > 0', None if ctl is None else ctl > 0, ctl)
    rows.m('K5 preparation screen <= 180 s (startup wait finished)', None if r['prep'] is None else r['prep'] <= PREP_MAX_MS,
           '%s ms' % r['prep'])
    rows.r('new permutations before the preparation line', sum(1 for x in r['av'] if r['prep_line'] and x[0] < r['prep_line']))
    video_rows(rows, p, r, so, 'K5')
    extra['catalogue_translations'] = n_cat


def stop_rows(rows, r, so, att, sout, extra):
    """K6 stand stop of edition 4 (s17c_ks2; item 561 (g)(2), item 566 (v))."""
    f = stop_facts(r)
    ec = exit_code(att)
    ok, det = close_path(f, ec)
    rows.m('K6 the break by the real close path: applied -> close requested precache_active=1 -> stand stop seen -> rebuild '
           'pipelines_bin=stopped -> close joined, one P < R, 0 timeout, 0 Event: quit, exit code 0 (item 566 (v))', ok, det)
    sl = f['applied'][0] if f['applied'] else None
    rows.m('K6 sign of the break: rebuild ... pipelines_bin=stopped after stand stop applied (item 532 (b))', None if sl is None else
           (f['stopped'] is not None and f['stopped'][0] > sl), 'stand line %s stopped line %s' % (sl, f['stopped'] and f['stopped'][0]))
    f19 = (sout or {}).get('f19', {})
    rows.m('K6 pipelines.bin is not written at the break (state_out.txt, %s)' % DIR1, None if sout is None else
           f19.get('pipelines_bin') is not True, f19)
    rows.m('K6 0 death markers (item 561 (g)(2))', deaths(r, so) == 0, deaths(r, so))
    sd = f['stopped'][1] if f['stopped'] else {}
    a = num(sd, 'perms_new')
    rows.r('a = perms_new of the stopped rebuild line (item 565 (g))', a)
    rows.r('stopped rebuild line', dict((k, sd.get(k)) for k in ('records', 'prepared', 'rejected', 'pending', 'perms_new', 'perms_cached',
                                                                 'pipelines_bin')))
    rows.r('waited_ms of stand stop seen / wait_ms of close stop joined', '%s / %s' % (f['seen'] and f['seen'][1].get('waited_ms'),
                                                                                    f['joined'] and f['joined'][1].get('wait_ms')))
    rows.r('translation cache files after the break (saved by code)', f19.get('cache_files'))
    rows.r('no startup wait line (the close path)', r['prep_line'] is None)
    extra['ks'] = dict(timeout=f['timeout'], seen=f['seen'] is not None, a=a, records=num(sd, 'records'))


def next_rows(rows, r, so, att, extra):
    """K6 next start (s17c_kn2): mode line, the game path as before, 0 deaths, the remainder member of item 565 (g) / 566 (g)."""
    hold_rows(rows, r, att, SPEC['s17c_kn2']['hold'], 'K6', SKY, frame_hold=False)
    rows.m('K6 0 death markers (the game path as before)', deaths(r, so) == 0, deaths(r, so))
    md = r['mode'][0][1] if r['mode'] else {}
    rows.m('K6 mode line mode=3 compat=ok', md.get('mode') == '3' and md.get('compat') == 'ok', md)
    rb = r['rebuild'][-1][1] if r['rebuild'] else {}
    kn = dict(rebuild=bool(r['rebuild']), skipped=bool(r['skipped']), written=rb.get('pipelines_bin') == 'written', b=num(rb, 'perms_new'),
              records=num(rb, 'records'))
    ks = ((read_json_of('s17c_ks2') or {}).get('extra') or {}).get('ks') or {}
    r3 = (((read_json_of('s17c_r3b') or {}).get('extra') or {}).get('rebuild') or {})
    n_full = dict(N=num(r3, 'perms_new'), records=num(r3, 'records'))
    adm = identity_admission()
    ok, det = remainder(ks, kn, n_full, adm)
    rows.m('K6 the next start rebuilds the remainder: a + b = N, a >= 1, b >= 1 (item 565 (g); identity admission item 566 (g))', ok, det)
    rows.r('a / b / N', '%s / %s / %s' % (ks.get('a'), kn['b'], n_full['N']))
    rows.r('perms_cached of the next start (reference, item 565 (g))', rb.get('perms_cached'))
    rows.r('rebuild line', dict((k, rb.get(k)) for k in ('records', 'prepared', 'rejected', 'pending', 'perms_new', 'perms_cached',
                                                         'pipelines_bin')))
    extra['kn'] = kn


# ----------------------------------------------------------------------------------------------------------------- output

def print_rows(tag, rows, meta):
    print('S17c2 reader tag %s group %s level %s' % (tag, meta['group'], meta['level']))
    print('  log sha256 %s stdout sha256 %s' % (meta['log_sha256'], meta['stdout_sha256']))
    for title, lst in (('ADMISSION', rows.adm), ('FORM', rows.form), ('MEMBERS', rows.mem)):
        print('  %s' % title)
        for name, ok, det in lst:
            print('    %-15s %s | %s' % (yn(ok), asc(name), det[:400]))
    print('  REPORT')
    for name, det in rows.rep:
        print('    %s: %s' % (asc(name), det[:400]))
    print('  READING %s' % rows.word())


def to_json(tag, rows, meta):
    return dict(meta, reading=rows.word(), admission=[list(x) for x in rows.adm], form=[list(x) for x in rows.form],
                members=[list(x) for x in rows.mem], report=[list(x) for x in rows.rep])


def table():
    print('S17c2 member table K2(2)-K6, seal edition 4 (no verdict - S17d2)')
    print('  carried without a repeat (item 561 (d)(1); edition 3 reading of %s)' % ED3)
    for tag in CARRIED:
        d = read_json_of(tag, 'ed3')
        if d is None:
            print('  %-9s %-6s NOT READ' % (tag, GROUP_ED3[tag]))
            continue
        print('  %-9s %-6s READING %s' % (tag, GROUP_ED3[tag], d['reading']))
        for name, ok, det in d['members']:
            print('      %-15s %s | %s' % (yn(ok), asc(name), asc(det)[:200]))
    print('  edition 4 tags (item 561 (d)(2))')
    for tag in ORDER:
        d = read_json_of(tag)
        if d is None:
            print('  %-9s %-6s NOT READ' % (tag, SPEC[tag]['group']))
            continue
        print('  %-9s %-6s READING %s' % (tag, SPEC[tag]['group'], d['reading']))
        for name, ok, det in d['members']:
            print('      %-15s %s | %s' % (yn(ok), asc(name), asc(det)[:200]))
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == '--table':
        return table()
    if argv[0] == '--k4x':
        stand = (argv[5], argv[6]) if len(argv) > 6 and argv[4] == '--stand' else None
        for mode in ('lookup', 'raw'):
            x = k4x(argv[1], argv[2], argv[3], stand, mode)
            for k in sorted(x):
                print('%s %s %s' % (mode, k, asc(str(x[k]))))
        return 0
    tag = argv[0]
    rows, meta = read_tag(tag)
    print_rows(tag, rows, meta)
    if '--json' in argv:
        out = argv[argv.index('--json') + 1]
        with open(out, 'w') as f:
            json.dump(to_json(tag, rows, meta), f, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
