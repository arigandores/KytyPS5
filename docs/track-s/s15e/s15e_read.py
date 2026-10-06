"""Track S link S15e (HPP-636; ROADMAP s122 item 557 (d), item 560): the reader of the tag s15_i - the FIRST launch of the installed state
"known scenes" (the catalogue s15/seeds installed into _ShaderSeeds/PPSA21564 by S15d, the variant pipelines.bin of FS8 moved to backup).
Form = the warm-up fs8_i of FS8e (C:/kyty/f287/fs8e, V Sky Garden -lvl underwater_aerial_garden, hold 330 s after the first scene frame,
video) on the INSTALLED FS8 2c9b69b9; the caches NOT returned after the tag.  Rows and a READING word by the seal C:/kyty/s288/pred/17_s.md;
the acceptance or the rollback is the lead's (S15f, HPP-637).
usage: python s15e_read.py s15_i [--json <out.json>]
       python s15e_read.py --pre <out.txt>          (inside the lock before the tag: the pre-state, exit 0 only when it is the S15d state)
       python s15e_read.py --after <out.json>       (inside the lock right after the run: the state of member (2))
       python s15e_read.py --dir <fixture dir>      (fixtures: log.txt, stdout.txt, es.json, rec.idx, glitch.txt, sheet.txt, installed_before.txt,
           installed_sha.txt, installed_after.txt, pre.txt, after.json, seal.md, bin.exe, compat.txt)
The scanning functions are imported from C:/kyty/f287/fs8c/fs8c_read.py (FS8c HPP-573) without a change (sealed sha256, = the line of the
FS8e seal): entry, first scene frame (the first FrameTrace row after the entry with draws >= 100), hold (sum dt_us of the rows after it,
before a scene change), death markers (log and stdout), revision texts, translation cache lines, window lines, env_admit of the form fs8_v.
Members of item 557 (d) (before the data):
  (1a) exactly 1 log line 'ShaderSeed: installed (728 shaders)';
  (1b) >= 1 log line 'ShaderSeed: compatibility=<c>' and every <c> = the first line of C:/kyty/s288/s15/seeds/PPSA21564/compatibility.txt;
  (2a) after the tag <variant>/pipelines.bin present (variant = variant_fixb26_fixb1b_fixf10_fixf19);
  (2b) its signature header (magic 'KytyPR1\\n', u32 size, size bytes of the signature) = the header of the catalogue pipelines.bin;
  (2c) its size >= 20 430 720 bytes;
  (2d) every translation file of the catalogue (.bin of seeds_manifest.txt without pipelines.bin; 728) present in the variant directory
       with the sha256 of the manifest (728 of 728, and the manifest carries exactly 728);
  (3a) 0 death markers (log and stdout); (3b) video index records >= 3000; (3c) 0 one-frame glitches (s51_vidglitch.py 4 6);
  (3d) sheet for the lead made.
Data (item 557 (d)(4), never a member): after the first scene frame (to a scene change) 'AsyncPipelines: skipped draw' lines, 'flip N held'
lines, FrameTrace rows with dt_us >= 100 000 and >= 1 000 000; the lines 'ShaderPreparation: ready' and 'PipelinePrecache: all pipelines
created, <ms> ms' (line numbers, their texts; the log has no clock on these lines - the time is the ms of the precache line and the
FrameTrace rows before them).
ADMIT rows (a NO -> NOT_ADMITTED, interference of the run): installed before the tag = binary of the tag = json binary_sha256 = installed
after the tag = 2c9b69b9; version string ...-1889-g302347b4 in the installed binary file; every revision text = 302347b; json prereg = sha256
of the seal; environment and command line of the form fs8_v (env_admit) and none of KYTY_SHADER_SEED, KYTY_SHADER_SEED_PATH,
KYTY_CACHE_MODE; pre-state (pre.txt 'PRE-STATE OK': _ShaderSeeds/PPSA21564 = seeds_manifest.txt, its compatibility first line = the
catalogue's, the variant pipelines.bin absent); every translation cache line ends with the variant; no window minimized / Recovering Vulkan
swapchain / GamePatch line.
FORM rows (a NO -> NOT_EVALUABLE unless a member is NO; executor variant): entered; hold >= 300 s; the process lived to the end of the hold.
READING  NOT_ADMITTED -> MEMBERS_FAIL (a member NO) -> NOT_EVALUABLE (a member not determined or a FORM row not YES) -> MEMBERS_PASS.
READING VARIANT (variant of the executor, printed beside, question to the lead): the catalogue holds 727 translation files, not 728
  (seeds_manifest.txt: 730 = 727 .bin + compatibility.txt + manifest.json + pipelines.bin; manifest.json "shaders": 727; the 19 U logs of
  S15 'ShaderSeed: installed (727 shaders)'); members (1a) and (2d) with n = the count of translation .bin of seeds_manifest.txt; the same
  ladder.  The letter word (READING) is the last line.
ASCII output only."""
import hashlib, json, os, re, struct, sys

FS8C = 'C:/kyty/f287/fs8c'
sys.path.insert(0, FS8C)
import fs8c_read as C  # noqa: E402

G = 'C:/kyty/s288/s15e'
TAG = 's15_i'
FORM = 'fs8_v'
LEVEL = C.SKY
HOLD = C.SPEC[FORM]['hold']
BIN_EXPECT = C.BIN_EXPECT
VERSION = C.VERSION
REV = C.REV
DIR_FIX = C.DIR_FIX
EMU = 'C:/kyty/KytyPS5/ps5 em'
INSTALLED = EMU + '/kyty_emulator.exe'
VARIANT = EMU + '/_ShaderCache/PPSA21564/' + DIR_FIX
SEEDS = EMU + '/_ShaderSeeds/PPSA21564'
CAT = 'C:/kyty/s288/s15/seeds/PPSA21564'
MANIFEST = 'C:/kyty/s288/s15/seeds_manifest.txt'
SEAL_PATH = 'C:/kyty/s288/pred/17_s.md'
N_SHADERS = 728
PB_MIN = 20430720
MAGIC = b'KytyPR1\n'
INSTALLED_LINE = b'ShaderSeed: installed (728 shaders)'
M_SEED = b'ShaderSeed: '
M_COMPAT = b'ShaderSeed: compatibility='
M_READY = b'ShaderPreparation: ready'
M_CREATED = b'PipelinePrecache: all pipelines created'
M_SKIP = b'AsyncPipelines: skipped draw'
RX_INSTALLED = re.compile(rb'^installed \((\d+) shaders\)$')
RX_HELD = re.compile(rb'flip (\d+) held')
RX_MS = re.compile(rb'all pipelines created, (\d+) ms')
BAN_ENV = ('KYTY_SHADER_SEED', 'KYTY_SHADER_SEED_PATH', 'KYTY_CACHE_MODE')
F100_US = 100000


def sha_file(p):
    return C.sha_file(p)


def first_text_line(path):
    if not path or not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        ln = f.readline()
    return ln.rstrip(b'\n').rstrip(b'\r')


def pb_header(path):
    """The signature header of a recipe file: MAGIC + u32 size + size bytes; None when absent or not of the form."""
    if not path or not os.path.exists(path):
        return None
    with open(path, 'rb') as f:
        m = f.read(len(MAGIC))
        s = f.read(4)
        if m != MAGIC or len(s) != 4:
            return None
        n = struct.unpack('<I', s)[0]
        body = f.read(n)
        if len(body) != n:
            return None
    return m + s + body


def load_manifest(path):
    """name -> (size, sha256) of seeds_manifest.txt ('<name> <size> <sha>' per line)."""
    out = {}
    if not path or not os.path.exists(path):
        return None
    for raw in open(path, 'rb').read().decode('utf-8', 'replace').split('\n'):
        p = raw.strip().split(' ')
        if len(p) == 3 and re.match(r'^[0-9a-f]{64}$', p[2]):
            out[p[0]] = (int(p[1]), p[2])
    return out


def dir_matches_manifest(d, man):
    """(ok, detail): the directory d holds exactly the names of man with their size and sha256."""
    if man is None or not os.path.isdir(d):
        return False, 'manifest %s, directory %s' % (man is not None, os.path.isdir(d))
    names = sorted(os.listdir(d))
    bad = []
    if sorted(man) != names:
        bad.append('names differ: only dir %s only manifest %s' % (sorted(set(names) - set(man))[:3], sorted(set(man) - set(names))[:3]))
    for n in names:
        if n in man:
            p = os.path.join(d, n)
            if os.path.getsize(p) != man[n][0] or sha_file(p) != man[n][1]:
                bad.append('differs %s' % n)
    return not bad, 'files %d manifest %d; %s' % (len(names), len(man), bad[:3] or 'equal')


def pre_state(seeds=SEEDS, variant=VARIANT, cat=CAT, manifest=MANIFEST):
    """Lines of the pre-state (S15d state, item 560 (b)); the last line PRE-STATE OK | PRE-STATE BAD."""
    man = load_manifest(manifest)
    ok1, d1 = dir_matches_manifest(seeds, man)
    c_inst = first_text_line(os.path.join(seeds, 'compatibility.txt'))
    c_cat = first_text_line(os.path.join(cat, 'compatibility.txt'))
    ok2 = c_inst is not None and c_inst == c_cat
    pb = os.path.join(variant, 'pipelines.bin')
    ok3 = not os.path.exists(pb)
    lines = ['manifest %s sha256 %s entries %s' % (manifest, sha_file(manifest), None if man is None else len(man)),
             'seeds dir %s = manifest: %s (%s)' % (seeds, 'YES' if ok1 else 'NO', d1),
             'compatibility first line of the seeds dir = of the catalogue: %s' % ('YES' if ok2 else 'NO'),
             'variant pipelines.bin %s absent: %s' % (pb, 'YES' if ok3 else 'NO'),
             'variant directory files %s' % (len(os.listdir(variant)) if os.path.isdir(variant) else 'ABSENT'),
             'PRE-STATE %s' % ('OK' if ok1 and ok2 and ok3 else 'BAD')]
    return lines


def after_state(variant=VARIANT, cat=CAT, manifest=MANIFEST):
    """The state of member (2) right after the run (dict, json)."""
    man = load_manifest(manifest) or {}
    pb = os.path.join(variant, 'pipelines.bin')
    trans = sorted(n for n in man if n.endswith('.bin') and n != 'pipelines.bin')
    match, miss, differ = 0, [], []
    for n in trans:
        p = os.path.join(variant, n)
        if not os.path.exists(p):
            miss.append(n)
        elif sha_file(p) != man[n][1]:
            differ.append(n)
        else:
            match += 1
    h_v = pb_header(pb)
    h_c = pb_header(os.path.join(cat, 'pipelines.bin'))
    return dict(variant=variant, manifest=manifest, manifest_sha256=sha_file(manifest), pb_present=os.path.exists(pb),
                pb_size=os.path.getsize(pb) if os.path.exists(pb) else None, pb_sha256=sha_file(pb),
                pb_header_sha256=hashlib.sha256(h_v).hexdigest() if h_v else None,
                cat_header_sha256=hashlib.sha256(h_c).hexdigest() if h_c else None,
                header_equal=h_v is not None and h_c is not None and h_v == h_c,
                n_trans_manifest=len(trans), n_trans_match=match, missing=miss[:5], n_missing=len(miss), differ=differ[:5],
                n_differ=len(differ), variant_files=len(os.listdir(variant)) if os.path.isdir(variant) else None)


def scan_s15e(log_path, level):
    """Own pass for the seed lines and the data rows (4); the scene domain is the rule of fs8c_read.scan (entry, first scene frame,
    a scene change ends it)."""
    r = dict(seed=[], installed=0, installed_ns=[], compat=[], ready=[], created=[], created_ms=None, scene_line=None, skip_after=0, held_after=0,
             f100_after=0, f1s_after=0, skip_all=0, held_all=0, ft_before_created=0, dt_before_created=0, held_first=[])
    if not log_path or not os.path.exists(log_path):
        return r
    after_entry = in_scene = ended = False
    with open(log_path, 'rb') as f:
        for ln, raw in enumerate(f, 1):
            if b'FrameTrace: n=' in raw:
                m = C.RX_FT.search(raw)
                if m:
                    dt = int(m.group(2))
                    if not r['created']:
                        r['ft_before_created'] += 1
                        r['dt_before_created'] += dt
                    if after_entry and not ended:
                        if not in_scene:
                            md = C.RX_DRAWS.search(m.group(3))
                            if md and int(md.group(1)) >= 100:
                                in_scene = True
                                r['scene_line'] = ln
                        else:
                            if dt >= F100_US:
                                r['f100_after'] += 1
                            if dt >= C.K2_US:
                                r['f1s_after'] += 1
                    continue
            if C.M_START in raw:
                name = raw.split(C.M_START, 1)[1].strip().decode('ascii', 'replace')
                if not after_entry:
                    if name == level:
                        after_entry = True
                else:
                    ended = True
            if M_SEED in raw:
                t = raw.rstrip(b'\r\n')
                if len(r['seed']) < 20:
                    r['seed'].append((ln, t[:300].decode('ascii', 'replace')))
                mi = RX_INSTALLED.match(t.split(M_SEED, 1)[1])
                if mi:
                    r['installed_ns'].append(int(mi.group(1)))
                if t.split(M_SEED, 1)[1] == INSTALLED_LINE[len(M_SEED):]:
                    r['installed'] += 1
                if M_COMPAT in t:
                    r['compat'].append((ln, t.split(M_COMPAT, 1)[1]))
            if M_READY in raw:
                r['ready'].append((ln, raw.rstrip(b'\r\n')[:200].decode('ascii', 'replace')))
            if M_CREATED in raw:
                m = RX_MS.search(raw)
                r['created'].append((ln, raw.rstrip(b'\r\n')[:200].decode('ascii', 'replace')))
                if m and r['created_ms'] is None:
                    r['created_ms'] = int(m.group(1))
            if M_SKIP in raw:
                r['skip_all'] += 1
                if in_scene and not ended:
                    r['skip_after'] += 1
            if b' held' in raw:
                m = RX_HELD.search(raw)
                if m:
                    r['held_all'] += 1
                    if in_scene and not ended:
                        r['held_after'] += 1
                        if len(r['held_first']) < 5:
                            r['held_first'].append((ln, int(m.group(1))))
    return r


def paths(base=None):
    names = ('installed_sha', 'installed_before', 'installed_after', 'pre', 'glitch', 'sheet')
    if base is not None:
        p = dict((n, os.path.join(base, n + '.txt')) for n in names)
        p.update(log=os.path.join(base, 'log.txt'), stdout=os.path.join(base, 'stdout.txt'), run=os.path.join(base, 'es.json'),
                 idx=os.path.join(base, 'rec.idx'), seal=os.path.join(base, 'seal.md'), bin=os.path.join(base, 'bin.exe'),
                 after=os.path.join(base, 'after.json'), compat=os.path.join(base, 'compat.txt'), manifest=os.path.join(base, 'manifest.txt'))
        return p
    d = os.path.join(G, 'runs', TAG)
    p = dict((n, os.path.join(d, n + '.txt')) for n in names)
    p.update(log=os.path.join(G, 'log_%s.txt' % TAG), stdout=os.path.join(G, 'stdout_%s.txt' % TAG), run=os.path.join(G, '%s.json' % TAG),
             idx=os.path.join(G, 'rec_%s.mp4.idx' % TAG), seal=SEAL_PATH, bin=INSTALLED, after=os.path.join(d, 'after.json'),
             compat=os.path.join(CAT, 'compatibility.txt'), manifest=MANIFEST)
    return p


def read(p):
    r = C.scan(p['log'], LEVEL)
    s = scan_s15e(p['log'], LEVEL)
    sd, srev, ssha = C.stdout_scan(p['stdout'])
    rj = C.text(p['run'])
    run = json.loads(rj) if rj else None
    att = ((run or {}).get('attempts') or [{}])[0]
    sha = C.first_line(C.text(p['installed_sha'])) or None
    sha_b = C.first_line(C.text(p['installed_before'])) or None
    sha_a = C.first_line(C.text(p['installed_after'])) or None
    pre_t = C.text(p['pre']) or ''
    at = C.text(p['after'])
    after = json.loads(at) if at else None
    cat_c = first_text_line(p['compat'])
    idx_n = None
    if p.get('idx') and os.path.exists(p['idx']):
        with open(p['idx'], 'rb') as f:
            idx_n = sum(1 for _ in f)
    gl = None
    gt = C.text(p['glitch'])
    if gt:
        m = C.RX_GL.search(gt)
        gl = int(m.group(1)) if m else None
    st = C.text(p['sheet'])
    sheet = next((x.strip() for x in st.split('\n') if x.startswith('sheet: ')), None) if st else None
    rev = r['rev'] + srev
    death = r['death'] + (sd or [])
    env_ok, env_info = C.env_admit(FORM, run)
    env = (run or {}).get('env') or {}
    ban = [k for k in BAN_ENV if k in env]
    seal_sha = C.sha_file(p['seal'])
    pre = ((run or {}).get('prereg') or {}).get('sha256')
    ended_ok = None
    if run is not None:
        ended_ok = (att.get('outcome') == 'ok' and att.get('hold_exit') is None and att.get('hold_s') is not None
                    and att.get('hold_s') >= HOLD)
    stc = r['stc']
    res = dict(tag=TAG, level=LEVEL, log=p['log'], log_sha256=r['sha256'], log_lines=r['lines'], stdout_sha256=ssha,
               stdout_present=sd is not None, rev=rev[:6], json_binary=(run or {}).get('binary_sha256'), installed_sha=sha,
               installed_before=sha_b, installed_after=sha_a, version_in_bin=C.has_bytes(p['bin'], VERSION), prereg=pre, seal_sha=seal_sha,
               env_info=env_info, ban_env=ban, stc=stc, pre_last=(pre_t.strip().split('\n') or [''])[-1][:80],
               seed=s['seed'], installed_lines=s['installed'], compat_n=len(s['compat']),
               compat_cat=cat_c.decode('ascii', 'replace') if cat_c is not None else None, after=after,
               ready=s['ready'][:3], created=s['created'][:3], created_ms=s['created_ms'], ft_before_created=s['ft_before_created'],
               dt_before_created_s=round(s['dt_before_created'] / 1e6, 2), scene_line=s['scene_line'], skip_after=s['skip_after'],
               held_after=s['held_after'], held_first=s['held_first'], f100_after=s['f100_after'], f1s_after=s['f1s_after'],
               skip_all=s['skip_all'], held_all=s['held_all'],
               attempt=dict((k, att.get(k)) for k in ('outcome', 'detail', 'hold_exit', 'hold_s', 'stable_s', 'close_rc', 'close_killed')),
               entry_line=r['entry_line'], scene_change_line=r['scene_change_line'], first_scene_n=r['first_scene_n'], hold_us=r['hold_us'],
               hold_s=round(r['hold_us'] / 1e6, 2), k2_after=r['k2_after'], dt_max_after=r['dt_max_after'], ft_rows=r['ft_rows'],
               death=death, win=r['win'], recovering=r['recovering'], gamepatch=r['gamepatch'], quit_line=r['quit_line'],
               fixl=r['fixl'], first_guest=r['first_guest'], idx_records=idx_n, glitches=gl, sheet=sheet)
    rev_ok = bool(rev) and all(t in (REV, VERSION.decode()) for _, _, t in rev)
    a = after or {}
    adm = [('binary: installed before = of the tag = json binary_sha256 = installed after = 2c9b69b9 (FS8)',
            sha_b == BIN_EXPECT and sha == BIN_EXPECT and res['json_binary'] == BIN_EXPECT and sha_a == BIN_EXPECT),
           ('version string ...-1889-g302347b4 in the installed binary file (N1)', bool(res['version_in_bin'])),
           ('every revision text of the log and stdout = %s (N1; SDL_REVISION never read)' % REV, rev_ok),
           ('json prereg sha256 = sha256 of the seal file', bool(pre) and pre == seal_sha),
           ('environment and command line of the form fs8_v (no KYTY_FIX_*, KYTY_GAME_PATCH, KYTY_GPU_CHECKPOINTS, VK_LAYER_*; KYTY_REC; '
            'validation false; -lvl %s)' % LEVEL, env_ok),
           ('none of KYTY_SHADER_SEED, KYTY_SHADER_SEED_PATH, KYTY_CACHE_MODE in the environment (offending %s)' % ban, not ban),
           ('pre-state of S15d before the tag (pre.txt: %s)' % res['pre_last'], res['pre_last'] == 'PRE-STATE OK'),
           ('translation cache directory %s in every line (>= 1 line)' % DIR_FIX,
            len(stc) >= 1 and all(x.replace('/', '\\').endswith('\\' + DIR_FIX) for x in stc)),
           ('no window minimized / Recovering Vulkan swapchain / GamePatch line',
            not r['win'].get('minimized') and not r['recovering'] and not r['gamepatch'])]
    compat_ok = None
    if cat_c is not None:
        compat_ok = len(s['compat']) >= 1 and all(c == cat_c for _, c in s['compat'])
    man = load_manifest(p['manifest'])
    n_cat = None if man is None else sum(1 for n in man if n.endswith('.bin') and n != 'pipelines.bin')
    res['n_cat'] = n_cat
    res['installed_ns'] = s['installed_ns'][:5]
    mem = [('(1a) exactly 1 log line "ShaderSeed: installed (<n> shaders)" and it is "ShaderSeed: installed (728 shaders)" (n of the lines %s)'
            % s['installed_ns'][:5], s['installed_ns'] == [N_SHADERS]),
           ('(1b) "ShaderSeed: compatibility=" lines %d, every value = the first line of the catalogue compatibility.txt' % len(s['compat']),
            compat_ok),
           ('(2a) %s/pipelines.bin present after the tag' % DIR_FIX, None if after is None else bool(a.get('pb_present'))),
           ('(2b) its signature header = the header of the catalogue pipelines.bin', None if after is None else bool(a.get('header_equal'))),
           ('(2c) its size %s >= %d bytes' % (a.get('pb_size'), PB_MIN),
            None if after is None else (a.get('pb_size') is not None and a.get('pb_size') >= PB_MIN)),
           ('(2d) %d translation files of the catalogue in the variant directory = seeds_manifest.txt by sha256 (match %s of %s)'
            % (N_SHADERS, a.get('n_trans_match'), a.get('n_trans_manifest')),
            None if after is None else (a.get('n_trans_manifest') == N_SHADERS and a.get('n_trans_match') == N_SHADERS)),
           ('(3a) 0 death markers (log and stdout)', None if not res['stdout_present'] else not death),
           ('(3b) video index records >= 3000', (idx_n or 0) >= C.VIDEO_MIN),
           ('(3c) 0 one-frame glitches (s51_vidglitch.py 4 6)', None if gl is None else gl == 0),
           ('(3d) sheet for the lead made', sheet is not None)]
    form = [('entered (entry line of %s)' % LEVEL, r['entry_line'] is not None),
            ('hold >= 300 s (sum dt after the first scene frame)', r['hold_us'] >= C.HOLD_MIN_US),
            ('the process lived to the end of the hold (outcome ok, hold_exit null, hold_s >= %d)' % HOLD, ended_ok)]
    data = [('(4) after the first scene frame (log line %s, to a scene change): AsyncPipelines: skipped draw lines %d; flip N held lines %d '
             '(first %s); frames >= 100 ms %d; frames >= 1 s %d (max dt_us %d); whole log: skipped draw %d, held %d'
             % (s['scene_line'], s['skip_after'], s['held_after'], s['held_first'], s['f100_after'], s['f1s_after'], r['dt_max_after'],
                s['skip_all'], s['held_all'])),
            ('(4) ShaderPreparation: ready %s; PipelinePrecache: all pipelines created %s (ms %s); FrameTrace rows before the latter %d '
             '(sum dt %.2f s)' % (s['ready'][:2], s['created'][:2], s['created_ms'], s['ft_before_created'], res['dt_before_created_s'])),
            ('ShaderSeed lines %s' % s['seed'][:6]),
            ('FixB4 %s FixF8 %s FixB24 %s; first GuestOut line %s' % (r['fixl']['B4'][:2], r['fixl']['F8'][:2], r['fixl']['B24'][:2],
                                                                    r['first_guest']))]
    # Variant of the executor (seal section 2): the number of translation files is the count of the catalogue manifest
    # (.bin without pipelines.bin), not the constant 728 of item 557 (d); members (1a) and (2d) replaced, the rest the same.
    var = [('(1a) exactly 1 log line "ShaderSeed: installed (<n> shaders)" with n = %s (translation .bin of seeds_manifest.txt)' % n_cat,
            None if n_cat is None else s['installed_ns'] == [n_cat]),
           ('(2d) %s translation files of the catalogue in the variant directory = seeds_manifest.txt by sha256 (match %s of %s)'
            % (n_cat, a.get('n_trans_match'), a.get('n_trans_manifest')),
            None if after is None or n_cat is None else (a.get('n_trans_manifest') == n_cat and a.get('n_trans_match') == n_cat))]
    mem_v = [var[0]] + mem[1:5] + [var[1]] + mem[6:]
    res['rows'] = dict(ADMIT=adm, MEMBER=mem, FORM=form, VARIANT=var)
    res['data'] = data
    res['reading'] = word_of(adm, mem, form)
    res['reading_variant'] = word_of(adm, mem_v, form)
    return res


def word_of(adm, mem, form):
    if not all(v for _, v in adm):
        return 'NOT_ADMITTED'
    if any(v is False for _, v in mem):
        return 'MEMBERS_FAIL'
    if any(v is None for _, v in mem) or not all(v is True for _, v in form):
        return 'NOT_EVALUABLE'
    return 'MEMBERS_PASS'


def rows(res):
    out = ['S15E %s level %s log sha256 %s lines %d stdout sha256 %s' % (res['tag'], res['level'], res['log_sha256'], res['log_lines'],
                                                                       res['stdout_sha256'])]
    add = out.append
    add('  binary: installed before %s, of the tag %s, json %s, installed after %s (expected %s); version string in the binary %s; '
        'revision texts %s' % (res['installed_before'], res['installed_sha'], res['json_binary'], res['installed_after'], BIN_EXPECT,
                               res['version_in_bin'], res['rev']))
    add('  prereg %s seal %s; %s; banned env %s' % (res['prereg'], res['seal_sha'], res['env_info'], res['ban_env']))
    add('  Shader translation cache lines %d %s; pre-state: %s' % (len(res['stc']), res['stc'][:2], res['pre_last']))
    add('  catalogue compatibility first line: %s' % res['compat_cat'])
    add('  after state: %s' % (None if res['after'] is None else dict((k, res['after'].get(k)) for k in (
        'pb_present', 'pb_size', 'pb_sha256', 'pb_header_sha256', 'cat_header_sha256', 'header_equal', 'n_trans_manifest', 'n_trans_match',
        'n_missing', 'missing', 'n_differ', 'differ', 'variant_files', 'manifest_sha256'))))
    add('  entry line %s; scene change line %s; first scene frame n %s; hold %.2f s; FrameTrace rows %d'
        % (res['entry_line'], res['scene_change_line'], res['first_scene_n'], res['hold_s'], res['ft_rows']))
    add('  death markers: %d %s; emulator stdout %s' % (len(res['death']), res['death'][:3], 'present' if res['stdout_present'] else 'MISSING'))
    add('  window: %s, Recovering Vulkan swapchain %d; GamePatch lines %d' % (res['win'] or 'none', res['recovering'], res['gamepatch']))
    add('  video: index records %s; one-frame glitches %s; %s' % (res['idx_records'], res['glitches'], res['sheet']))
    add('  EXIT (report): %s; Event: quit line %s' % (res['attempt'], res['quit_line']))
    add('  catalogue manifest: translation .bin %s; installed lines n %s' % (res['n_cat'], res['installed_ns']))
    for cls in ('ADMIT', 'MEMBER', 'FORM', 'VARIANT'):
        for name, val in res['rows'][cls]:
            add('  %s %s: %s' % (cls, name, C.yn(val)))
    for x in res['data']:
        add('  DATA %s' % x)
    add('READING VARIANT %s: %s (variant of the executor: n of the catalogue manifest for (1a), (2d))' % (res['tag'], res['reading_variant']))
    add('READING %s: %s' % (res['tag'], res['reading']))
    return out


def main(argv):
    if '--pre' in argv:
        lines = pre_state()
        with open(argv[argv.index('--pre') + 1], 'w') as f:
            f.write('\n'.join(C.asc(x) for x in lines) + '\n')
        print('\n'.join(C.asc(x) for x in lines))
        return 0 if lines[-1] == 'PRE-STATE OK' else 9
    if '--after' in argv:
        st = after_state()
        with open(argv[argv.index('--after') + 1], 'w') as f:
            json.dump(st, f, indent=1)
        print(C.asc('after: pb_present %s size %s header_equal %s trans %s/%s' % (st['pb_present'], st['pb_size'], st['header_equal'],
                                                                              st['n_trans_match'], st['n_trans_manifest'])))
        return 0
    if '--dir' in argv:
        p = paths(argv[argv.index('--dir') + 1])
    else:
        if not argv or argv[0] != TAG:
            raise SystemExit('usage: s15e_read.py s15_i [--json <out>] | --pre <out> | --after <out> | --dir <fixture dir>')
        p = paths()
    res = read(p)
    print('\n'.join(C.asc(x) for x in rows(res)))
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w') as f:
            json.dump(res, f, indent=1, default=list)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
