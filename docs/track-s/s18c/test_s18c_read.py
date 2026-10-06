"""S18c (HPP-644): fixtures of the S18c reader s18c_read.py (seal docs/track-s/s18c.md; ROADMAP s122 item 569 (d)(3)-(4), item 571 (g)(3),
item 576 (e), item 579 (v)).  One synthetic root with the 25 tags made (19 capture tags with an accumulating catalogue, s18_ks, s18_r, s18_e1,
s18_e2, s18_v, s18_w); the baseline reads MEMBERS_PASS everywhere; then one change per admission row, form row and member, and every edge:
the accumulation of item 569 (d)(3) (compat, generation = replay.cur of the previous tag, the generation file, catalogue_sources /
catalogue_specs not decreasing, gen=0 without a save), the ACCUMULATION and SIGNATURE_571G3 gate lines, the close path of item 566 (v) on
s18_ks, the share 0.90 and the screen 180 s of s18_r, SCENE_OK with 0 frames >= 1 s, the video, the catalogue translations, the line of
s18_v, the W layer control, KYTY_S_REPLAY_TEST at the shipment tags (item 576 (e)(3)), the chain admission (no return between s18_r,
s18_e1, s18_e2).
The mutlib early-exit form: the only bindings of the flag are `ok = True` and `ok &= ...`, the last statement is `sys.exit(0 if ok else 1)`.
The first output line names the suite and the targets with sha256; the output ends with ALL OK.  Synthetic files only, no game.  ASCII only.
usage: python test_s18c_read.py [<s18c_read.py under test>]"""
import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import struct
import sys
from pathlib import Path

import xxhash

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 's18c_read.py')
sys.path.insert(0, HERE)
import r_addr  # noqa: E402


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


print('suite test_s18c_read.py sha256 %s target s18c_read.py sha256 %s state_s17c.py sha256 %s r_addr.py sha256 %s'
      % (sha(os.path.abspath(__file__)), sha(SRC), sha(os.path.join(HERE, 'state_s17c.py')), sha(os.path.join(HERE, 'r_addr.py'))))
_spec = importlib.util.spec_from_file_location('s18c_read_under_test', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)
N = [0]


def check(cond, name):
    N[0] += 1
    print(('ok   ' if cond else 'FAIL ') + name)
    return bool(cond)


# ------------------------------------------------------------------------------------------------ builders: catalogue

L = r_addr.LAYOUT
SRC_HASHES = (0xAAAA000000000001, 0xAAAA000000000002)
CANON = [(0x100, 2), (0, 3), (7, 0), (0x20000, 0), (1, 6), (0, 9)]
RAW = [(0x12345678, 2), (2, 3), (7, 0), (0x20000, 0), (0x40000, 6), (0x1234, 9)]


def catalogue_bytes(gen, words, compat=b'KytyReplay1:PPSA21564:01.000:key1:canon1:input1:pod1.2.3', hashes=SRC_HASHES):
    body = b''
    for k, h in enumerate(hashes):
        src = bytearray(L['src'])
        struct.pack_into('<Q', src, L['src.src_id'], 100 + k)
        struct.pack_into('<Q', src, L['src.hash'], h)
        struct.pack_into('<I', src, L['src.static_words'], 1)
        struct.pack_into('<I', src, L['src.code_words'], 2)
        body += bytes(src) + struct.pack('<3I', 1, 2, 3)
    spec = bytearray(L['spec'])
    struct.pack_into('<Q', spec, L['spec.spec_id'], 0x16)
    struct.pack_into('<I', spec, L['spec.words'], len(words))
    body += bytes(spec)
    for value, role in words:
        w = bytearray(L['word'])
        struct.pack_into('<I', w, L['word.value'], value)
        w[L['word.role']] = role
        body += bytes(w)
    body += bytes(bytearray(L['pipe']))
    head = bytearray(L['file'])
    head[0:8] = r_addr.MAGIC
    struct.pack_into('<I', head, L['file.format'], 1)
    struct.pack_into('<I', head, L['file.compat_size'], len(compat))
    bh = bytearray(L['body'])
    struct.pack_into('<QQIII', bh, 0, gen, xxhash.xxh3_64_intdigest(body), len(hashes), 1, 1)
    return bytes(head) + compat + bytes(bh) + body


def write_replay(d, gen, words=CANON, hashes=SRC_HASHES):
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    open(os.path.join(d, 'replay.cur'), 'wb').write(b'%d\n' % gen)
    open(os.path.join(d, 'replay.%d.bin' % gen), 'wb').write(catalogue_bytes(gen, words, hashes=hashes))


def state_text(f10=None, f19=None, replay_dir=None):
    out = ['dir f10 absent' if f10 is None else 'dir f10 present files 3 cache_files 2 pipelines_bin %s' % f10,
           'dir f19 absent' if f19 is None else 'dir f19 present files 4 cache_files 3 pipelines_bin %s' % f19]
    if replay_dir is None:
        out.append('dir replay absent')
    else:
        names = sorted(os.listdir(replay_dir))
        out.append('dir replay present files %d cache_files 0 pipelines_bin absent' % len(names))
        out.append('replay.cur %s' % open(os.path.join(replay_dir, 'replay.cur')).read().strip())
        for n in names:
            p = os.path.join(replay_dir, n)
            out.append('file %s %d %s' % (n, os.path.getsize(p), sha(p)))
    return '\n'.join(out) + '\n'


# ------------------------------------------------------------------------------------------------ builders: logs

SKY, MGG = R.SKY, R.MGG
CAPS = R.CAPS


def gen_of(k):          # the generation saved by capture tag k (1-based)
    return k + 2


def cs_of(k):
    return 5 + k


def cp_of(k):
    return 6 + k


def siglines(sig):
    return 'ShaderSeed: compatibility=KytySeed1:PPSA21564:01.007.000:%s::10288:376:216:44:516:125:000010de:00002c59' % sig


def cap_line(k, at, gen=None, cs=None, cp=None, cm=0, dq=0):
    return ('ShaderReplay: capture sources=3 specs=4 pipes=5 canon_mismatch=%d dropped_queue=%d bytes=100 gen=%d canon_self=0 '
            'canon_residual=0 canon_base=0 canon_big=0 pipes_waiting=2 catalogue_sources=%d catalogue_specs=%d catalogue_pipes=%d at=%s' % (
                cm, dq, gen_of(k) if gen is None else gen, cs_of(k) if cs is None else cs, cp_of(k) if cp is None else cp, 7 + k, at))


def mode2(k):
    if k == 1:
        return 'ShaderReplay: mode=2 dir=_ShaderCache\\PPSA21564\\replay compat=absent generation=0 corrupt=0 sources=0 specs=0 pipes=0 test=none'
    return ('ShaderReplay: mode=2 dir=_ShaderCache\\PPSA21564\\replay compat=ok generation=%d corrupt=0 sources=%d specs=%d pipes=%d '
            'test=none' % (gen_of(k - 1), cs_of(k - 1), cp_of(k - 1), 7 + k - 1))


MODE3 = 'ShaderReplay: mode=3 dir=_ShaderCache\\PPSA21564\\replay compat=ok generation=%d corrupt=0 sources=24 specs=25 pipes=26 test=%s'
PNO = 'PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10\\pipelines.bin yet'
AVL = 'AvTrace: shader ShaderRecompiler VS hash=0x%016x translate_us=5 compile_us=6 permutations=1'
APPLIED = 'ShaderReplay: stand stop applied processed=5 records=10'
REQ = 'ShaderReplay: close stop requested precache_active=1'
SEEN = 'ShaderReplay: stand stop seen waited_ms=40 processed=5 records=10'
JOINED = 'ShaderReplay: close stop joined wait_ms=12'
SKIP_RC = 'ShaderReplay: rebuild skipped reason=recipes_current'
DUAL = 'DualSrcBlend: supported=1 enabled=1'
G19 = gen_of(19)


def rb_line(records=10, prepared=9, rejected=1, pending=0, fused=1, perms_new=8, cached=0, pb='written'):
    return ('ShaderReplay: rebuild records=%d prepared=%d rejected=%d pending=%d rej_src=0 rej_fused=%d rej_key=0 rej_version=0 rej_shape=0 '
            'rej_translate=0 rej_emit=0 rej_val=0 rej_write=0 rej_ref=0 translate_ms=10 wall_ms=20 perms_new=%d perms_cached=%d '
            'rb_push_moved=0 rb_spec_changed=0 groups_same_pc=1 group_sources=3 pipelines_bin=%s' % (
                records, prepared, rejected, pending, fused, perms_new, cached, pb))


STOPPED = rb_line(prepared=5, rejected=0, pending=5, fused=0, perms_new=3, pb='stopped')


def log_lines(level, before=(), after=(), entry=True, ft=True, dirname=None, prep=12000, av_after=(), rev=None, sig=None, pre_guest=(),
              ft_rows=None, long=False):
    """long - 3 000 rows of 100 ms after the first scene frame (300 s; the tags whose hold is a member); else one row (light fixtures)."""
    out = ['Fork build arigandores/KytyPS5 %s, test' % (rev or R.REV),
           'Shader translation cache: _ShaderCache' + chr(92) + 'PPSA21564' + chr(92) + (dirname or R.DIR1),
           siglines(sig or R.SIG1)]
    out += list(before)
    if prep is not None:
        out.append('ShaderPreparation: startup wait finished in %d ms presents_other=0 presents_main=0' % prep)
    out += list(av_after)
    out += list(pre_guest)
    out.append('GuestOut: hello')
    if entry:
        out.append('GuestOut: Level has started: ' + level)
    if ft:
        out += ft_rows if ft_rows is not None else (['FrameTrace: n=9 dt_us=16000 draws=50', 'FrameTrace: n=10 dt_us=16000 draws=500'] +
                                                    ['FrameTrace: n=%d dt_us=100000 draws=500' % (11 + k) for k in range(3000 if long else 1)])
    out += list(after)
    return out


def cap_log(k):
    return log_lines(R.LEVELS[k - 1], dirname=R.DIR0, sig=R.SIG0, before=[mode2(k), PNO],
                     after=[cap_line(k, 'save'), cap_line(k, 'stop')])


def logs_all():
    d = dict((CAPS[k - 1], cap_log(k)) for k in range(1, 20))
    d['s18_ks'] = log_lines(SKY, entry=False, ft=False, prep=None, before=[MODE3 % (G19, 'stop'), APPLIED, REQ, SEEN, STOPPED, JOINED])
    d['s18_r'] = log_lines(SKY, entry=False, ft=False, before=[MODE3 % (G19, 'none'), rb_line()])
    d['s18_e1'] = log_lines(SKY, prep=500, before=[MODE3 % (G19, 'none'), SKIP_RC], av_after=[AVL % 0xBBBB], after=[AVL % 0xCCCC], long=True)
    d['s18_e2'] = log_lines(MGG, prep=500, before=[MODE3 % (G19, 'none'), SKIP_RC], av_after=[AVL % 0xBBBB], long=True)
    d['s18_v'] = log_lines(SKY, prep=500, before=[MODE3 % (G19, 'none'), SKIP_RC], long=True)
    d['s18_w'] = log_lines(SKY, prep=90000, before=[MODE3 % (G19, 'none'), rb_line(), '[Vulkan][W] some warning'], pre_guest=[DUAL])
    return d


# ------------------------------------------------------------------------------------------------ builders: one tag

def env_for(tag):
    spec = R.SPEC[tag]
    e = dict(R.BASE_ENV)
    e['KYTY_GUEST_ARGS'] = '-lvl ' + spec['level']
    e.update(spec['env'])
    e['KYTY_GATE_FILE'] = 'C:/x/gates.req'
    e['KYTY_SAMPLE_GATE'] = 'C:/x/sample.req'
    if spec['form'] == 'v':
        e['KYTY_REC'] = 'C:/x/rec_%s.mp4' % tag
    if spec['form'] == 'w':
        e['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
        e['VK_LAYER_DUPLICATE_MESSAGE_LIMIT'] = '100000000'
    e['VK_SDK_PATH'] = 'C:/VulkanSDK'
    return e


def att_for(tag):
    spec = R.SPEC[tag]
    a = dict(label='attempt 1', outcome='prep' if spec['form'] == 'p' else 'ok', hold_exit=None, hold_s=float(spec['hold']), close_rc=0,
             close_killed=False, close_s=2.0, detail=None)
    if tag == 's18_ks':
        a.update(outcome='exited', detail='exit code 0', close_rc=None, close_killed=None)
    return a


def make_root(root):
    shutil.rmtree(root, ignore_errors=True)
    os.makedirs(os.path.join(root, 'runs'))
    seal = os.path.join(root, 'seal.md')
    open(seal, 'wb').write(b'seal S18c of the fixtures\n')
    open(os.path.join(root, 'bin.exe'), 'wb').write(b'MZ...' + R.VERSION + b'...')
    st = os.path.join(root, 'state')
    for k in range(1, 20):
        write_replay(os.path.join(st, CAPS[k - 1], 'replay'), gen_of(k))
    write_replay(os.path.join(st, 's18_ks', 'replay'), G19)
    for t in ('s18_r', 's18_e1'):
        write_replay(os.path.join(st, t, 'replay'), G19)
        for d in ('_ShaderCache', 'GLCache'):
            os.makedirs(os.path.join(st, t, 'all', d))
    c19 = os.path.join(st, CAPS[-1], 'replay')
    logs = logs_all()
    for i, tag in enumerate(R.ORDER):
        spec = R.SPEC[tag]
        d = os.path.join(root, 'runs', tag)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(root, 'log_%s.txt' % tag), 'w', newline='\n').write('\n'.join(logs[tag]) + '\n')
        open(os.path.join(root, 'stdout_%s.txt' % tag), 'w', newline='\n').write('Shaders: VS 1 | PS 1\nKytyPS5 git = %s, x\n' % R.REV)
        run = dict(tag=tag, binary_sha256=R.BIN_EXPECT, env=env_for(tag),
                   cmdline=['kyty_emulator.exe', '--vulkan-validation', 'true' if spec['form'] == 'w' else 'false'],
                   prereg=dict(sha256=sha(seal)), attempts=[att_for(tag)])
        json.dump(run, open(os.path.join(root, '%s.json' % tag), 'w'))
        if spec['form'] == 'v':
            open(os.path.join(root, 'rec_%s.mp4.idx' % tag), 'w').write('f\n' * 3000)
        w = lambda n, t: open(os.path.join(d, n), 'w', newline='\n').write(t)  # noqa: E731
        w('installed_sha.txt', R.BIN_EXPECT + '\n')
        w('installed_before.txt', R.FS8 + '\n')
        w('installed_after.txt', R.FS8 + '\n')
        w('manifest_cmp.txt', 'manifest cmp EQUAL files 9 listsha 00\n')
        if spec['form'] == 'v':
            w('glitch.txt', 'one-frame glitches: 0\n')
            w('sheet.txt', 'sheet: C:/x/sheet.png\n')
        w('state_in_name.txt', spec['state'] + '\n')
        s = spec['state']
        if s == 'cap0':
            sin = state_text()
        elif s == 'cap_acc':
            sin = state_text(f19='10 def', replay_dir=os.path.join(st, spec['prev'], 'replay'))
        elif s == 'cat_full':
            sin = state_text(f10='10 abc', replay_dir=c19)
        elif s == 'inst_cat':
            sin = state_text(f10='10 abc', f19='10 def', replay_dir=c19)
        else:
            sin = state_text(f10='10 abc', f19='10 def', replay_dir=os.path.join(st, spec['prev'], 'replay'))
            w('chain_cmp.txt', 'manifest cmp EQUAL files 20 listsha 11\n')
        w('state_in.txt', sin)
        w('state_out.txt', 'dir f10 present files 3 cache_files 2 pipelines_bin 10 abc\ndir f19 present files 3 cache_files 3 pipelines_bin '
                           '%s\ndir replay absent\n' % ('absent' if tag == 's18_ks' else '10 def'))


def use(root):
    R.ROOT = root
    R.SEAL_PATH = os.path.join(root, 'seal.md')
    R.BIN_PATH = os.path.join(root, 'bin.exe')


def read_tags(root, tags):
    use(root)
    out = {}
    for tag in tags:
        rows, meta = R.read_tag(tag)
        json.dump(R.to_json(tag, rows, meta), open(os.path.join(root, 'runs', tag, 'read.json'), 'w'))
        out[tag] = rows
    return out


def rowval(rows, prefix, kind='m'):
    lst = {'m': rows.mem, 'a': rows.adm, 'f': rows.form}[kind]
    for name, ok_, det in lst:
        if name.startswith(prefix):
            return ok_
    return 'MISSING'


BASE = Path('C:/kyty/s288/s18c/fx_s18c')   # mutlib gives every job its own copy of this directory
shutil.rmtree(BASE, ignore_errors=True)
BASE.mkdir(parents=True)
TMP = str(BASE)
B0 = os.path.join(TMP, 'base')
make_root(B0)
WB = read_tags(B0, R.ORDER)
K = [0]


def variant(change, tag, start=None):
    """A copy of the baseline root with the change; the tags from start (default: tag) up to tag re-read in order."""
    K[0] += 1
    root = os.path.join(TMP, 'v%03d' % K[0])
    lo0 = R.ORDER.index(start or tag)
    need = set(R.ORDER[lo0:R.ORDER.index(tag) + 1])
    need |= set(R.SPEC[t]['prev'] for t in list(need) if R.SPEC[t]['prev']) | {R.LAST_CAP}
    os.makedirs(os.path.join(root, 'runs'))
    os.makedirs(os.path.join(root, 'state'))
    for f in ('seal.md', 'bin.exe'):
        shutil.copy(os.path.join(B0, f), root)
    for t in need:   # only the tags the reading touches (the target range, their previous tags, the catalogue tag)
        for f in ('log_%s.txt' % t, 'stdout_%s.txt' % t, '%s.json' % t, 'rec_%s.mp4.idx' % t):
            if os.path.exists(os.path.join(B0, f)):
                shutil.copy(os.path.join(B0, f), root)
        shutil.copytree(os.path.join(B0, 'runs', t), os.path.join(root, 'runs', t))
        if os.path.isdir(os.path.join(B0, 'state', t)):
            shutil.copytree(os.path.join(B0, 'state', t), os.path.join(root, 'state', t))
    if change is not None:
        change(root)
    lo = R.ORDER.index(start or tag)
    rows = read_tags(root, [t for t in R.ORDER[lo:R.ORDER.index(tag) + 1]])[tag]
    use(B0)
    shutil.rmtree(root, ignore_errors=True)
    return rows


def edit(root, rel, old, new, count=1):
    p = os.path.join(root, rel)
    t = open(p, encoding='ascii').read()
    assert t.count(old) >= 1, (rel, old)
    open(p, 'w', newline='\n').write(t.replace(old, new) if count is None else t.replace(old, new, count))


def edit_json(root, tag, fn):
    p = os.path.join(root, '%s.json' % tag)
    d = json.load(open(p))
    fn(d)
    json.dump(d, open(p, 'w'))


def put(root, rel, text):
    open(os.path.join(root, rel), 'w', newline='\n').write(text)


def logput(root, tag, lines):
    put(root, 'log_%s.txt' % tag, '\n'.join(lines) + '\n')


def logedit(tag, old, new, count=1):
    return lambda root: edit(root, 'log_%s.txt' % tag, old, new, count)


def one(tag, change, prefix, want, kind='m', name=None, start=None):
    rows = variant(change, tag, start)
    got = rowval(rows, prefix, kind)
    return check(got == want, '%s: %s -> %s (got %s, reading %s)' % (tag, name or prefix[:70], R.yn(want) if want != 'MISSING' else want,
                                                                   R.yn(got) if got in (True, False, None) else got, rows.word()))


def word(tag, change, want, name, start=None):
    rows = variant(change, tag, start)
    return check(rows.word() == want, '%s: %s -> %s (got %s)' % (tag, name, want, rows.word()))


def lines_of(tag, change, start=None):
    return variant(change, tag, start).lines


def setenv(tag, key, value):
    def ch(root):
        def f(d):
            if value is None:
                d['env'].pop(key, None)
            else:
                d['env'][key] = value
        edit_json(root, tag, f)
    return ch


def setatt(tag, **kw):
    def ch(root):
        edit_json(root, tag, lambda d: d['attempts'][0].update(kw))
    return ch


def multi(*chs):
    def ch(root):
        for c in chs:
            c(root)
    return ch


ok = True
for _t in R.ORDER:
    _w = WB[_t]
    ok &= check(_w.word() == 'MEMBERS_PASS', 'baseline %s reads MEMBERS_PASS (got %s %s)' % (
        _t, _w.word(), [x for x in _w.adm + _w.form + _w.mem if x[1] is not True][:2]))
ok &= check(all(('ACCUMULATION %s OK' % t) in WB[t].lines for t in CAPS), 'baseline: ACCUMULATION <tag> OK on the 19 capture tags')
ok &= check('SIGNATURE_571G3 s18_c01 OK' in WB['s18_c01'].lines and 'SIGNATURE_571G3 s18_ks OK' in WB['s18_ks'].lines and
            not any('SIGNATURE' in x for t in CAPS[1:] for x in WB[t].lines), 'baseline: SIGNATURE_571G3 lines on s18_c01 and s18_ks only')

# ------------------------------------------------------------------------------------------------ constants of the print
ok &= check(R.BIN_EXPECT == 'b3cee576138a15530eadd9afe1d67290adf12d281c09ec7c6ebf3b04ffec305a', 'binary S18a2 b3cee576 (item 579)')
ok &= check(R.VERSION == b'KytyPS5-2026-09-15-6a2987a-1897-g0005e11f' and R.REV == '0005e11', 'version string and revision of 0005e11f')
ok &= check(R.INSTALLED_OK == ('2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b',), 'installed FS8 only')
ok &= check(R.SIG1 == 'KytySC3:9177b4267de1fb8bac7d1113afd8733210addfac:robust:ftz:cbank:fixb26:fixb1b:fixf10:fixf19' and
            R.SIG0 + ':fixf19' == R.SIG1 and R.DIR1 == R.DIR0 + '_fixf19' and R.DIR0 == 'variant_fixb26_fixb1b_fixf10',
            'signatures of item 571 (g)(3) and the folders')
ok &= check(R.LEVELS == ('title_controller_ship', 'intro_next', 'worldmap', 'ps_logo', 'hub_crashsite', 'underwater_aerial_garden',
                         'penguin_atlantis', 'time_stopper_ghost_world', 'rotating_level_day_and_night', 'bumper_enemy_snowy_canyon',
                         'big_hand_pirate_island', 'timestop_casino', 'mini_giants_garden', 'ice_iceberg', 'sponge_dirty_bath', 'hoover_beach',
                         'volcano_mountain', 'voxel_world', 'enemy_gorilla'), 'the 19 levels of the S15 U arms in the order of 16_s.md section 2')
ok &= check(R.ORDER == tuple('s18_c%02d' % i for i in range(1, 20)) + ('s18_ks', 's18_r', 's18_e1', 's18_e2', 's18_v', 's18_w'),
            '25 tags in order')
ok &= check(all(R.SPEC[t]['env'] == {'KYTY_S_REPLAY': '2', 'KYTY_FIX_F19': '0', 'KYTY_SHADER_SEED': '0'} for t in CAPS),
            'capture form: KYTY_S_REPLAY=2 KYTY_FIX_F19=0 KYTY_SHADER_SEED=0 (item 569 (d)(3))')
ok &= check(R.SPEC['s18_ks']['env'] == {'KYTY_S_REPLAY': '3', 'KYTY_FIX_F19': '1', 'KYTY_AV_TRACE': '1', 'KYTY_SHADER_SEED': '0',
                                        'KYTY_S_REPLAY_TEST': 'stop'}, 's18_ks form s17c_ks2 (item 576 (e)(2))')
ok &= check(R.SPEC['s18_r']['env'] == {'KYTY_SHADER_SEED': '0'} and R.SPEC['s18_e1']['env'] == {'KYTY_SHADER_SEED': '0', 'KYTY_AV_TRACE': '1'}
            and R.SPEC['s18_e2']['env'] == R.SPEC['s18_e1']['env'] and R.SPEC['s18_v']['env'] == {} and R.SPEC['s18_w']['env'] == {},
            'shipment tags at the default: no KYTY_S_REPLAY, no KYTY_FIX_F19, no KYTY_S_REPLAY_TEST')
ok &= check([(R.SPEC[t]['form'], R.SPEC[t]['hold'], R.SPEC[t]['state'], R.SPEC[t]['prev'], R.SPEC[t]['level']) for t in R.ORDER[19:]] == [
    ('p', 0, 'cat_full', 's18_c19', SKY), ('p', 0, 'cat_full', 's18_ks', SKY), ('v', 330, 'chain', 's18_r', SKY),
    ('v', 330, 'chain', 's18_e1', MGG), ('v', 330, 'inst_cat', 's18_e2', SKY), ('w', 310, 'cat_full', 's18_v', SKY)],
    'forms, holds, input states, previous tags and levels of the six shipment tags')
ok &= check(all(R.SPEC[t]['form'] == 'c' and R.SPEC[t]['hold'] == 330 for t in CAPS) and R.SPEC['s18_c01']['state'] == 'cap0' and
            all(R.SPEC[t]['state'] == 'cap_acc' and R.SPEC[t]['prev'] == CAPS[i] for i, t in enumerate(CAPS[1:])), 'capture forms and chain of prev')
ok &= check((R.SHARE_MIN, R.PREP_MAX_MS, R.VIDEO_MIN, R.HOLD_MIN_US, R.K2_US, R.LIMIT) == (0.90, 180000, 3000, 300000000, 1000000, '100000000'),
            'constants of item 569 (d)(4): 0.90, 180 000 ms, 3 000 records, 300 s, 1 s; layer limit 100000000')
ok &= check(R.SEED0_TAGS == CAPS + ('s18_ks', 's18_r', 's18_e1', 's18_e2'), 'seed admission tags')

# ------------------------------------------------------------------------------------------------ admission rows
C5 = 's18_c05'
ok &= one(C5, setatt(C5), 'run record', True, 'a', 'one attempt (baseline)')
ok &= one(C5, lambda r: edit_json(r, C5, lambda d: d['attempts'].append(dict(d['attempts'][0]))), 'run record', False, 'a', 'two attempts')
ok &= one(C5, lambda r: os.remove(os.path.join(r, '%s.json' % C5)), 'run record', False, 'a', 'no json')
ok &= one(C5, lambda r: edit_json(r, C5, lambda d: d.update(binary_sha256='0' * 64)), 'binary of the run', False, 'a', 'json binary other')
ok &= one(C5, lambda r: put(r, 'runs/%s/installed_sha.txt' % C5, '1' * 64 + '\n'), 'binary of the run', False, 'a', 'installed_sha other')
ok &= one(C5, lambda r: open(os.path.join(r, 'bin.exe'), 'wb').write(b'MZ no version'), 'version string', False, 'a')
ok &= one(C5, logedit(C5, 'arigandores/KytyPS5 %s' % R.REV, 'arigandores/KytyPS5 302347b'), 'revision texts', False, 'a', 'other revision')
ok &= one(C5, multi(logedit(C5, 'Fork build arigandores/KytyPS5 %s, test' % R.REV, 'nothing'),
                    lambda r: put(r, 'stdout_%s.txt' % C5, 'none\n')), 'revision texts', False, 'a', 'no revision text')
ok &= one(C5, lambda r: edit_json(r, C5, lambda d: d.update(prereg=dict(sha256='2' * 64))), 'prereg sha256', False, 'a')
ok &= one(C5, setenv(C5, 'KYTY_PIPELINE_PRECACHE', '0'), 'environment', False, 'a', 'extra KYTY key')
ok &= one(C5, setenv(C5, 'KYTY_SHADER_SEED', None), 'environment', False, 'a', 'KYTY_SHADER_SEED missing')
ok &= one(C5, setenv(C5, 'KYTY_FIX_F19', '1'), 'environment', False, 'a', 'capture at F19=1')
ok &= one(C5, setenv(C5, 'KYTY_GUEST_ARGS', '-lvl ' + SKY), 'environment', False, 'a', 'other level in KYTY_GUEST_ARGS')
ok &= one(C5, setenv(C5, 'KYTY_GATE_FILE', None), 'environment', False, 'a', 'no gate file')
ok &= one(C5, setenv(C5, 'VK_LAYER_PATH', 'C:/x'), 'environment', False, 'a', 'VK_LAYER at a non-W tag')
ok &= one(C5, setenv(C5, 'KYTY_REC', 'C:/x.mp4'), 'environment', False, 'a', 'KYTY_REC at a capture tag (form c)')
for _t in ('s18_r', 's18_e1', 's18_e2', 's18_v', 's18_w'):
    ok &= one(_t, setenv(_t, 'KYTY_S_REPLAY_TEST', 'stop'), 'environment', False, 'a', 'KYTY_S_REPLAY_TEST at %s (item 576 (e)(3))' % _t)
    ok &= one(_t, setenv(_t, 'KYTY_S_REPLAY', '3'), 'environment', False, 'a', 'explicit KYTY_S_REPLAY at %s (the default is read)' % _t)
ok &= one('s18_e1', setenv('s18_e1', 'KYTY_REC', None), 'environment', False, 'a', 'no KYTY_REC at a v tag')
ok &= one('s18_ks', setenv('s18_ks', 'KYTY_S_REPLAY_TEST', None), 'environment', False, 'a', 'stand missing at s18_ks')
ok &= one('s18_w', setenv('s18_w', 'VK_LAYER_PATH', None), 'environment', False, 'a', 'W without VK_LAYER_PATH')
ok &= one('s18_w', setenv('s18_w', 'VK_LAYER_DUPLICATE_MESSAGE_LIMIT', '1000000'), 'environment', False, 'a', 'W limit other')
ok &= one('s18_w', setenv('s18_w', 'VK_LAYER_MESSAGE_ID_FILTER', 'x'), 'environment', False, 'a', 'W with a message filter')
ok &= one('s18_w', setenv('s18_w', 'VK_LAYER_SETTINGS_PATH', 'x'), 'environment', False, 'a', 'W with an extra VK_LAYER key')
ok &= one('s18_w', lambda r: edit_json(r, 's18_w', lambda d: d.update(cmdline=['k', '--vulkan-validation', 'false'])), 'command line',
          False, 'a', 'W without validation')
ok &= one(C5, lambda r: edit_json(r, C5, lambda d: d.update(cmdline=['k', '--vulkan-validation', 'true'])), 'command line', False, 'a',
          'capture with validation')
ok &= one(C5, logedit(C5, 'GuestOut: hello', 'ShaderSeed: installed (5 shaders)\nGuestOut: hello'), '0 lines ShaderSeed', False, 'a',
          'seed line in the log')
ok &= one(C5, lambda r: put(r, 'stdout_%s.txt' % C5, 'ShaderSeed: installed\nKytyPS5 git = %s, x\n' % R.REV), '0 lines ShaderSeed', False,
          'a', 'seed line in stdout')
for _t in ('s18_r', 's18_e1', 's18_e2', 's18_ks'):
    ok &= one(_t, logedit(_t, 'GuestOut: hello', 'ShaderSeed: installed\nGuestOut: hello'), '0 lines ShaderSeed', False, 'a',
              'seed line at %s' % _t)
ok &= word('s18_v', logedit('s18_v', 'GuestOut: hello', 'ShaderSeed: installed\nGuestOut: hello'), 'MEMBERS_PASS',
           'a seed line at s18_v (seed at the default) is a report row')
ok &= one(C5, logedit(C5, 'GuestOut: hello', 'Window 1 minimized\nGuestOut: hello'), 'no window minimized', False, 'a', 'minimized')
ok &= one(C5, logedit(C5, 'GuestOut: hello', 'Recovering Vulkan swapchain\nGuestOut: hello'), 'no window minimized', False, 'a', 'recovering')
ok &= one(C5, logedit(C5, 'GuestOut: hello', 'GamePatch: x\nGuestOut: hello'), 'no window minimized', False, 'a', 'GamePatch')
ok &= one(C5, lambda r: put(r, 'runs/%s/state_in_name.txt' % C5, 'cap0\n'), 'input state name', False, 'a')
ok &= one(C5, lambda r: os.remove(os.path.join(r, 'runs', C5, 'state_in.txt')), 'input state described', False, 'a', 'no state_in')
ok &= one('s18_c01', lambda r: put(r, 'runs/s18_c01/state_in.txt', state_text(f10='1 a')), 'input state cap0', False, 'a', 'cap0 with f10')
ok &= one('s18_c01', lambda r: put(r, 'runs/s18_c01/state_in.txt', state_text(replay_dir=os.path.join(r, 'state', 's18_c01', 'replay'))),
          'input state cap0', False, 'a', 'cap0 with a replay folder')


def corrupt_saved(tag):
    def ch(root):
        p = os.path.join(root, 'state', tag, 'replay', 'replay.%d.bin' % (gen_of(CAPS.index(tag) + 1) if tag in CAPS else G19))
        b = bytearray(open(p, 'rb').read())
        b[-1] ^= 0x55
        open(p, 'wb').write(bytes(b))
    return ch


ok &= one(C5, corrupt_saved('s18_c04'), 'input state cap_acc: replay', False, 'a', 'cap_acc replay differs from state/s18_c04 by one byte')
ok &= one(C5, lambda r: put(r, 'runs/%s/state_in.txt' % C5, state_text(replay_dir=os.path.join(B0, 'state', 's18_c03', 'replay'))),
          'input state cap_acc: replay', False, 'a', 'cap_acc replay of an earlier tag')
ok &= one(C5, lambda r: put(r, 'runs/%s/state_in.txt' % C5, state_text(f10='1 a', replay_dir=os.path.join(r, 'state', 's18_c04', 'replay'))),
          'input state cap_acc: %s absent' % R.DIR0, False, 'a', 'cap_acc with f10 present')
ok &= one(C5, lambda r: put(r, 'runs/%s/state_in.txt' % C5, state_text()), 'input state cap_acc: replay', False, 'a', 'cap_acc without replay')
for _t in ('s18_ks', 's18_r', 's18_w'):
    ok &= one(_t, lambda r, t=_t: put(r, 'runs/%s/state_in.txt' % t, state_text(f19='1 x', replay_dir=os.path.join(r, 'state', 's18_c19', 'replay'))),
              'input state cat_full: %s absent' % R.DIR1, False, 'a', 'cat_full with f19 present')
    ok &= one(_t, corrupt_saved('s18_c19'), 'input state cat_full: replay', False, 'a', 'cat_full replay differs from state/s18_c19')
ok &= one('s18_v', lambda r: put(r, 'runs/s18_v/state_in.txt', state_text(replay_dir=os.path.join(r, 'state', 's18_c19', 'replay'))),
          'input state inst_cat: %s present' % R.DIR1, False, 'a', 'inst_cat without f19')
ok &= one('s18_v', lambda r: put(r, 'runs/s18_v/state_in.txt', state_text(f19='absent', replay_dir=os.path.join(r, 'state', 's18_c19', 'replay'))),
          'input state inst_cat: %s present' % R.DIR1, False, 'a', 'inst_cat f19 without pipelines.bin')
ok &= one('s18_v', corrupt_saved('s18_c19'), 'input state inst_cat: replay', False, 'a', 'inst_cat replay differs')
for _t in ('s18_e1', 's18_e2'):
    ok &= one(_t, lambda r, t=_t: put(r, 'runs/%s/chain_cmp.txt' % t, 'manifest cmp DIFFER only before 1\n'), 'input state chain: manifest',
              False, 'a', 'chain manifest differs')
    ok &= one(_t, lambda r, t=_t: os.remove(os.path.join(r, 'runs', t, 'chain_cmp.txt')), 'input state chain: manifest', False, 'a',
              'chain_cmp missing')
    ok &= one(_t, lambda r, t=_t: put(r, 'runs/%s/state_in.txt' % t, state_text(replay_dir=os.path.join(r, 'state', R.SPEC[t]['prev'], 'replay'))),
              'input state chain: %s present' % R.DIR1, False, 'a', 'chain without f19')
ok &= one('s18_e2', corrupt_saved('s18_e1'), 'input state chain: replay', False, 'a', 'chain replay differs from state/s18_e1')
ok &= one(C5, lambda r: os.remove(os.path.join(r, 'log_%s.txt' % C5)), 'emulator log present', False, 'a')
ok &= one(C5, logedit(C5, PNO, 'PipelinePrecache: started'), 'capture fitness', False, 'a', 'no PipelinePrecache: no ... yet')
# form rows
ok &= one(C5, lambda r: put(r, 'runs/%s/installed_after.txt' % C5, '3' * 64 + '\n'), 'installed binary before = after', False, 'f')
ok &= one(C5, multi(lambda r: put(r, 'runs/%s/installed_after.txt' % C5, '3' * 64 + '\n'),
                    lambda r: put(r, 'runs/%s/installed_before.txt' % C5, '3' * 64 + '\n')), 'installed binary before = after', False, 'f',
          'not FS8 on both sides')
ok &= one(C5, lambda r: put(r, 'runs/%s/manifest_cmp.txt' % C5, 'manifest cmp DIFFER\n'), 'manifest of the caches', False, 'f')
ok &= word(C5, lambda r: put(r, 'runs/%s/manifest_cmp.txt' % C5, 'manifest cmp DIFFER\n'), 'FORM_FAIL', 'word FORM_FAIL')
ok &= word(C5, setenv(C5, 'KYTY_FIX_F19', '1'), 'NOT_ADMITTED', 'word NOT_ADMITTED')

# ------------------------------------------------------------------------------------------------ capture members
ok &= one(C5, logedit(C5, 'GuestOut: Level has started: ' + R.LEVELS[4], 'GuestOut: Level has started: ' + SKY), 'CAP entered', False,
          name='entry of another level')
ok &= one(C5, logedit(C5, 'GuestOut: Level has started: ' + R.LEVELS[4], 'GuestOut: x'), 'CAP entered', False, name='no entry line')
ok &= one(C5, setatt(C5, outcome='timeout'), 'CAP entered', False, name='outcome timeout')
ok &= one(C5, setatt(C5, hold_exit=3), 'CAP the process lived', False, name='died inside the hold')
ok &= one(C5, setatt(C5, hold_s=329.9), 'CAP the process lived', False, name='hold 329.9 s')
ok &= one(C5, setatt(C5, hold_s=330.0), 'CAP the process lived', True, name='hold 330.0 s (edge)')
ok &= one(C5, logedit(C5, 'GuestOut: hello', 'Unhandled exception: x\nGuestOut: hello'), 'CAP 0 death', False, name='death in the log')
ok &= one(C5, lambda r: put(r, 'stdout_%s.txt' % C5, '--- Fatal Error ---\nKytyPS5 git = %s, x\n' % R.REV), 'CAP 0 death', False,
          name='death in stdout')
ok &= one(C5, logedit(C5, R.DIR0 + '\n', R.DIR1 + '\n'), 'CAP translation cache directory', False, name='directory of F19=1')
ok &= one(C5, logedit(C5, R.DIR0 + '\n', 'variant_fixf10\n'), 'CAP translation cache directory', False,
          name='another folder ending in fixf10')
ok &= one('s18_c01', logedit('s18_c01', 'compat=absent', 'compat=ok'), 'CAP accumulation: mode', False, name='first tag compat=ok')
ok &= one('s18_c01', logedit('s18_c01', 'compat=absent generation=0', 'compat=absent generation=1'), 'CAP accumulation: mode', False,
          name='first tag generation 1')
ok &= one('s18_c01', logedit('s18_c01', 'mode=2 dir', 'mode=3 dir'), 'CAP accumulation: mode', False, name='first tag mode 3')
ok &= one(C5, logedit(C5, 'compat=ok', 'compat=absent'), 'CAP accumulation: mode', False, name='later tag compat=absent')
ok &= one(C5, logedit(C5, 'compat=ok', 'compat=mismatch'), 'CAP accumulation: mode', False, name='later tag compat=mismatch')
ok &= one(C5, logedit(C5, 'generation=%d ' % gen_of(4), 'generation=%d ' % gen_of(3)), 'CAP accumulation: mode', False,
          name='generation = replay.cur of an earlier tag')
ok &= one(C5, logedit(C5, 'ShaderReplay: mode=2', 'ShaderReplay: model=2'), 'CAP accumulation: mode', False, name='no mode line')
ok &= one(C5, lambda r: put(r, 'state/s18_c04/replay/replay.cur', '%d\n' % gen_of(5)), 'CAP accumulation: mode', False,
          name='previous replay.cur other than the mode line', start='s18_c04')
ok &= one(C5, lambda r: put(r, 'state/%s/replay/replay.cur' % C5, '%d\n' % gen_of(4)), 'CAP accumulation: generation file', False,
          name='replay.cur != gen of the stop line')
ok &= one(C5, lambda r: write_replay(os.path.join(r, 'state', C5, 'replay'), gen_of(5) + 1), 'CAP accumulation: generation file', False,
          name='replay.cur = gen + 1 with a readable file of its own')
ok &= one(C5, lambda r: os.remove(os.path.join(r, 'state', C5, 'replay', 'replay.%d.bin' % gen_of(5))), 'CAP accumulation: generation file',
          False, name='generation file missing')
ok &= one(C5, lambda r: shutil.rmtree(os.path.join(r, 'state', C5)), 'CAP accumulation: generation file', False, name='no saved replay folder')


def gen0(cs_same=True):
    def ch(root):
        logput(root, C5, log_lines(R.LEVELS[4], dirname=R.DIR0, sig=R.SIG0, before=[mode2(5), PNO],
                                   after=[cap_line(5, 'stop', gen=0, cs=cs_of(4) if cs_same else cs_of(4) + 1, cp=cp_of(4))]))
        edit(root, 'log_%s.txt' % C5, 'catalogue_pipes=%d' % (7 + 5), 'catalogue_pipes=%d' % (7 + 4))
        write_replay(os.path.join(root, 'state', C5, 'replay'), gen_of(4))
    return ch


ok &= one(C5, gen0(True), 'CAP accumulation: generation file', True, name='gen=0, no save, replay.cur = previous, counts = mode line (variant)')
ok &= one(C5, gen0(False), 'CAP accumulation: generation file', False, name='gen=0 with counts other than the mode line')
ok &= one(C5, multi(gen0(True), lambda r: write_replay(os.path.join(r, 'state', C5, 'replay'), gen_of(5))), 'CAP accumulation: generation file',
          False, name='gen=0 with replay.cur other than the previous')
ok &= one(C5, logedit(C5, 'catalogue_sources=%d catalogue_specs=%d catalogue_pipes=%d at=stop' % (cs_of(5), cp_of(5), 12),
                      'catalogue_sources=%d catalogue_specs=%d catalogue_pipes=%d at=stop' % (cs_of(4) - 1, cp_of(5), 12)),
          'CAP accumulation: catalogue_sources', False, name='catalogue_sources decrease by 1')
ok &= one(C5, logedit(C5, 'catalogue_sources=%d catalogue_specs=%d catalogue_pipes=%d at=stop' % (cs_of(5), cp_of(5), 12),
                      'catalogue_sources=%d catalogue_specs=%d catalogue_pipes=%d at=stop' % (cs_of(5), cp_of(4) - 1, 12)),
          'CAP accumulation: catalogue_sources', False, name='catalogue_specs decrease by 1')
ok &= one(C5, logedit(C5, 'catalogue_sources=%d catalogue_specs=%d catalogue_pipes=%d at=stop' % (cs_of(5), cp_of(5), 12),
                      'catalogue_sources=%d catalogue_specs=%d catalogue_pipes=%d at=stop' % (cs_of(4), cp_of(4), 12)),
          'CAP accumulation: catalogue_sources', True, name='catalogue_sources and specs equal to the previous (edge)')
ok &= one(C5, lambda r: edit(r, 'runs/s18_c04/read.json', '"catalogue_sources": %d' % cs_of(4), '"catalogue_sources": null'),
          'CAP accumulation: catalogue_sources', None, name='previous read without catalogue_sources')
ok &= one(C5, logedit(C5, 'at=stop', 'at=save'), 'CAP accumulation: generation file', None, name='no at=stop line - ondisk')
ok &= one(C5, logedit(C5, 'at=stop', 'at=save'), 'CAP accumulation: catalogue_sources', None, name='no at=stop line - nondec')
ok &= one(C5, logedit(C5, 'at=stop', 'at=save'), 'CAP canon_mismatch', None, name='no at=stop line - canon')
ok &= one(C5, logedit(C5, 'canon_mismatch=0 dropped_queue=0 bytes=100 gen=%d canon_self=0 canon_residual=0 canon_base=0 canon_big=0 '
                      'pipes_waiting=2 catalogue_sources=%d catalogue_specs=%d catalogue_pipes=12 at=stop' % (gen_of(5), cs_of(5), cp_of(5)),
                      'canon_mismatch=1 dropped_queue=0 bytes=100 gen=%d canon_self=1 canon_residual=0 canon_base=0 canon_big=0 '
                      'pipes_waiting=2 catalogue_sources=%d catalogue_specs=%d catalogue_pipes=12 at=stop' % (gen_of(5), cs_of(5), cp_of(5))),
          'CAP canon_mismatch', False, name='canon_mismatch 1')
ok &= one(C5, logedit(C5, 'dropped_queue=0 bytes=100 gen=%d canon_self=0 canon_residual=0 canon_base=0 canon_big=0 pipes_waiting=2 '
                      'catalogue_sources=%d catalogue_specs=%d catalogue_pipes=12 at=stop' % (gen_of(5), cs_of(5), cp_of(5)),
                      'dropped_queue=1 bytes=100 gen=%d canon_self=0 canon_residual=0 canon_base=0 canon_big=0 pipes_waiting=2 '
                      'catalogue_sources=%d catalogue_specs=%d catalogue_pipes=12 at=stop' % (gen_of(5), cs_of(5), cp_of(5))),
          'CAP dropped_queue', False, name='dropped_queue 1')
ok &= one(C5, setatt(C5, close_killed=True), 'CAP dropped_queue', None, name='hard close')
ok &= one(C5, setatt(C5, close_rc=None), 'CAP dropped_queue', None, name='no close rc')
ok &= one('s18_c01', multi(logedit('s18_c01', 'catalogue_sources=%d catalogue_specs=%d catalogue_pipes=8 at=stop' % (cs_of(1), cp_of(1)),
                                   'catalogue_sources=0 catalogue_specs=%d catalogue_pipes=8 at=stop' % cp_of(1))),
          'CAP catalogue_sources > 0', False, name='empty catalogue sources')
ok &= one('s18_c01', multi(logedit('s18_c01', 'catalogue_sources=%d catalogue_specs=%d catalogue_pipes=8 at=stop' % (cs_of(1), cp_of(1)),
                                   'catalogue_sources=%d catalogue_specs=0 catalogue_pipes=8 at=stop' % cs_of(1))),
          'CAP catalogue_sources > 0', False, name='empty catalogue specs')
ok &= one(C5, lambda r: write_replay(os.path.join(r, 'state', C5, 'replay'), gen_of(5), words=RAW), 'CAP offline R_ADDR', False,
          name='raw address words in the catalogue')
ok &= one(C5, lambda r: shutil.rmtree(os.path.join(r, 'state', C5)), 'CAP offline R_ADDR', None, name='catalogue missing - R_ADDR')
# the ACCUMULATION line and the stop rule
ok &= check('ACCUMULATION s18_c05 BREACH' in lines_of(C5, logedit(C5, 'compat=ok', 'compat=absent')), 'ACCUMULATION BREACH on a mode NO')
ok &= check('ACCUMULATION s18_c05 BREACH' in lines_of(C5, lambda r: put(r, 'state/%s/replay/replay.cur' % C5, '%d\n' % gen_of(4))),
            'ACCUMULATION BREACH on an ondisk NO')
ok &= check('ACCUMULATION s18_c05 UNDETERMINED' in lines_of(C5, logedit(C5, 'at=stop', 'at=save')),
            'ACCUMULATION UNDETERMINED without an at=stop line')
ok &= check('ACCUMULATION s18_c05 OK' in lines_of(C5, logedit(C5, 'canon_mismatch=0 dropped_queue=0 bytes=100 gen=%d canon_self=0' % gen_of(5),
                                                             'canon_mismatch=1 dropped_queue=0 bytes=100 gen=%d canon_self=1' % gen_of(5))),
            'ACCUMULATION OK with canon_mismatch 1 (not an accumulation member)')
ok &= check(R.acc_word([('a', True, ''), ('b', None, ''), ('c', False, '')]) == 'BREACH' and
            R.acc_word([('a', True, ''), ('b', None, '')]) == 'UNDETERMINED' and R.acc_word([('a', True, '')]) == 'OK', 'acc_word order')
# the signature of item 571 (g)(3)
ok &= one('s18_c01', logedit('s18_c01', R.SIG0 + '::', R.SIG1 + '::'), 'CAP signature line', False, name='first tag with the F19=1 string')
ok &= one('s18_c01', logedit('s18_c01', '9177b4267de1fb8bac7d1113afd8733210addfac', 'ed2686da' + '0' * 32), 'CAP signature line', False,
          name='other translator hash')
ok &= one('s18_c01', logedit('s18_c01', 'ShaderSeed: compatibility=', 'ShaderSeed: compat='), 'CAP signature line', False,
          name='no signature line')
ok &= one('s18_c01', logedit('s18_c01', 'GuestOut: hello', siglines(R.SIG1) + '\nGuestOut: hello'), 'CAP signature line', False,
          name='a second signature line differs')
ok &= one('s18_c01', logedit('s18_c01', 'GuestOut: hello', 'ShaderSeed: compatibility=garbage\nGuestOut: hello'), 'CAP signature line',
          False, name='a second, unparsed compatibility line')
ok &= check('SIGNATURE_571G3 s18_c01 BREACH' in lines_of('s18_c01', logedit('s18_c01', R.SIG0 + '::', R.SIG1 + '::')),
            'SIGNATURE_571G3 s18_c01 BREACH line')
ok &= check(R.signature_ok(dict(sig=[R.SIG0]), R.SIG0) and not R.signature_ok(dict(sig=[]), R.SIG0) and
            not R.signature_ok(dict(sig=[R.SIG0, R.SIG1]), R.SIG0), 'signature_ok: one line, none, mixed')
ok &= one('s18_c19', logedit('s18_c19', 'compat=ok generation=%d' % gen_of(18), 'compat=ok generation=%d' % gen_of(17)),
          'CAP accumulation: mode', False, name='last capture tag generation of an earlier tag')

# ------------------------------------------------------------------------------------------------ s18_ks (item 566 (v))
KS = 's18_ks'
ok &= one(KS, logedit(KS, 'generation=%d' % G19, 'generation=%d' % (G19 - 1)), 'KS mode line', False, name='generation other than c19')
ok &= one(KS, logedit(KS, 'compat=ok', 'compat=mismatch'), 'KS mode line', False, name='compat mismatch')
ok &= one(KS, lambda r: edit(r, 'runs/s18_c19/read.json', '"replay_cur": %d' % G19, '"replay_cur": null'), 'KS mode line', False,
          name='c19 read without replay_cur')
for _ln, _nm in ((APPLIED, 'applied'), (REQ, 'requested'), (SEEN, 'seen'), (STOPPED, 'stopped'), (JOINED, 'joined')):
    ok &= one(KS, logedit(KS, _ln + '\n', ''), 'KS the break', None, name='missing line %s' % _nm)
ok &= one(KS, lambda r: logput(r, KS, log_lines(SKY, entry=False, ft=False, prep=None, before=[MODE3 % (G19, 'stop'), APPLIED, SEEN, REQ,
                                                                                              STOPPED, JOINED])),
          'KS the break', None, name='seen before requested')
ok &= one(KS, lambda r: logput(r, KS, log_lines(SKY, entry=False, ft=False, prep=None, before=[MODE3 % (G19, 'stop'), REQ, APPLIED, SEEN,
                                                                                              STOPPED, JOINED])),
          'KS the break', None, name='requested before applied')
ok &= one(KS, lambda r: logput(r, KS, log_lines(SKY, entry=False, ft=False, prep=None, before=[MODE3 % (G19, 'stop'), APPLIED, REQ, STOPPED,
                                                                                              SEEN, JOINED])),
          'KS the break', None, name='stopped before seen')
ok &= one(KS, lambda r: logput(r, KS, log_lines(SKY, entry=False, ft=False, prep=None, before=[MODE3 % (G19, 'stop'), APPLIED, REQ, SEEN,
                                                                                              JOINED, STOPPED])),
          'KS the break', None, name='joined before stopped')
ok &= one(KS, logedit(KS, 'seen waited_ms=40 processed=5', 'seen waited_ms=40 processed=6'), 'KS the break', None, name='P differs')
ok &= one(KS, logedit(KS, 'processed=5 records=10\nShaderReplay: close', 'processed=5 records=11\nShaderReplay: close'), 'KS the break', None,
          name='R differs')
ok &= one(KS, logedit(KS, 'processed=5 records=10', 'processed=10 records=10', None), 'KS the break', None, name='P = R')
ok &= one(KS, logedit(KS, 'precache_active=1', 'precache_active=0'), 'KS the break', None, name='precache_active 0')
ok &= one(KS, logedit(KS, JOINED, JOINED + '\nEvent: quit'), 'KS the break', None, name='Event: quit line')
ok &= one(KS, setatt(KS, detail='exit code 1'), 'KS the break', None, name='exit code 1')
ok &= one(KS, setatt(KS, outcome='ok', detail=None), 'KS the break', None, name='closed by the harness')
ok &= one(KS, logedit(KS, JOINED, JOINED + '\nShaderReplay: stand stop timeout waited_ms=60000 processed=5 records=10'), 'KS the break', False,
          name='timeout line')
ok &= one(KS, lambda r: logput(r, KS, log_lines(SKY, entry=False, ft=False, prep=None, before=[MODE3 % (G19, 'stop'), STOPPED, APPLIED, REQ,
                                                                                              SEEN, JOINED])),
          'KS sign of the break', False, name='stopped line before the stand line')
ok &= one(KS, logedit(KS, APPLIED + '\n', ''), 'KS sign of the break', None, name='no stand line')
ok &= one(KS, lambda r: edit(r, 'runs/%s/state_out.txt' % KS, 'pipelines_bin absent', 'pipelines_bin 10 ff'), 'KS pipelines.bin', False,
          name='pipelines.bin written')
ok &= one(KS, lambda r: os.remove(os.path.join(r, 'runs', KS, 'state_out.txt')), 'KS pipelines.bin', None, name='no state_out')
ok &= one(KS, logedit(KS, JOINED, JOINED + '\nGpuHangAbort: x'), 'KS 0 death', False, name='death')
ok &= one(KS, logedit(KS, R.SIG1 + '::', R.SIG0 + '::'), 'KS signature line', False, name='F19=0 string at s18_ks')
ok &= check('SIGNATURE_571G3 s18_ks BREACH' in lines_of(KS, logedit(KS, R.SIG1 + '::', R.SIG0 + '::')), 'SIGNATURE_571G3 s18_ks BREACH line')
ok &= check(R.exit_code(dict(outcome='exited', detail='exit code 0')) == 0 and R.exit_code(dict(outcome='ok', detail='exit code 0')) is None
            and R.exit_code(dict(outcome='exited', detail='x')) is None, 'exit_code: only an exited outcome with the detail')

# ------------------------------------------------------------------------------------------------ s18_r
RT = 's18_r'
ok &= one(RT, logedit(RT, 'mode=3 dir', 'mode=2 dir'), 'R mode line', False, name='mode 2')
ok &= one(RT, logedit(RT, 'compat=ok', 'compat=mismatch'), 'R mode line', False, name='compat mismatch')
ok &= one(RT, logedit(RT, 'generation=%d' % G19, 'generation=%d' % (G19 + 1)), 'R mode line', False, name='generation other')
ok &= one(RT, logedit(RT, R.DIR1 + '\n', R.DIR0 + '\n'), 'R translation cache directory', False, name='directory of F19=0')
ok &= one(RT, logedit(RT, 'ShaderReplay: rebuild records', 'ShaderReplay: rebuildx records'), 'R a rebuild line', False, name='no rebuild')
ok &= one(RT, logedit(RT, 'ShaderPreparation', SKIP_RC + '\nShaderPreparation'), 'R a rebuild line', False, name='a skipped line too')
ok &= one(RT, logedit(RT, 'ShaderPreparation', 'ErrorDeviceLost\nShaderPreparation'), 'R 0 death', False, name='death')
ok &= one(RT, setatt(RT, outcome='timeout'), 'R the process reached', False, name='outcome timeout')
ok &= one(RT, logedit(RT, 'pipelines_bin=written', 'pipelines_bin=stopped'), 'R pipelines_bin=written', False, name='stopped')
ok &= one(RT, logedit(RT, 'pending=0 rej_src', 'pending=1 rej_src'), 'R identity', False, name='identity broken')
ok &= one(RT, logedit(RT, 'rej_fused=1', 'rej_fused=0'), 'R partition', False, name='partition broken')
ok &= one(RT, logedit(RT, 'rej_ref=0', 'rej_ref=1'), 'R partition', False, name='rej_ref counted in the partition')
ok &= one(RT, logedit(RT, rb_line(), rb_line(records=100, prepared=90, rejected=10, fused=10)), 'R share', True, name='share 0.90 (edge)')
ok &= one(RT, logedit(RT, rb_line(), rb_line(records=100, prepared=89, rejected=11, fused=11)), 'R share', False, name='share 0.89')
ok &= one(RT, logedit(RT, rb_line(), rb_line(records=0, prepared=0, rejected=0, fused=0)), 'R share', None, name='records 0')
ok &= one(RT, logedit(RT, 'finished in 12000 ms', 'finished in 180000 ms'), 'R preparation screen', True, name='180 000 ms (edge)')
ok &= one(RT, logedit(RT, 'finished in 12000 ms', 'finished in 180001 ms'), 'R preparation screen', False, name='180 001 ms')
ok &= one(RT, logedit(RT, 'ShaderPreparation: startup wait finished', 'ShaderPreparation: other'), 'R preparation screen', None,
          name='no startup wait line')

# ------------------------------------------------------------------------------------------------ s18_e1 / s18_e2
for E in ('s18_e1', 's18_e2'):
    ok &= one(E, logedit(E, 'compat=ok', 'compat=absent'), 'E mode line', False, name='compat absent')
    ok &= one(E, logedit(E, SKIP_RC, 'ShaderReplay: rebuild skipped reason=no_catalogue'), 'E line rebuild skipped', False, name='no_catalogue')
    ok &= one(E, logedit(E, SKIP_RC, SKIP_RC + '\n' + rb_line()), 'E line rebuild skipped', False, name='a rebuild line as well')
    ok &= one(E, logedit(E, R.DIR1 + '\n', R.DIR0 + '\n'), 'E translation cache directory', False, name='directory of F19=0')
    ok &= one(E, logedit(E, 'GuestOut: Level has started: ', 'GuestOut: x: '), 'E entered', False, name='not entered')
    ok &= one(E, setatt(E, hold_exit=1), 'E the process lived', False, name='died in the hold')
    ok &= one(E, logedit(E, 'n=3010 dt_us=100000 ', 'n=3010 dt_us=99999 '), 'E shown hold', False,
              name='hold 299.999999 s (last row 99 999 us)')
    ok &= one(E, logedit(E, 'GuestOut: hello', '--- Error ---\nGuestOut: hello'), 'E 0 death', False, name='death')
    ok &= one(E, logedit(E, 'n=11 dt_us=100000 ', 'n=11 dt_us=100000 draws=500\nFrameTrace: n=99999 dt_us=1000000 '), 'E 0 frames >= 1 s',
              False, name='a frame of 1 000 000 us after the first scene frame (edge)')
    ok &= one(E, logedit(E, 'n=11 dt_us=100000 ', 'n=11 dt_us=100000 draws=500\nFrameTrace: n=99999 dt_us=999999 '), 'E 0 frames >= 1 s',
              True, name='a frame of 999 999 us')
    ok &= one(E, logedit(E, 'n=9 dt_us=16000 draws=50', 'n=9 dt_us=2000000 draws=50'), 'E 0 frames >= 1 s', True,
              name='a frame >= 1 s before the first scene frame (other reading, report)')
    ok &= one(E, logedit(E, 'draws=500', 'draws=50', None), 'E 0 frames >= 1 s', None, name='no first scene frame')
    ok &= one(E, lambda r, e=E: open(os.path.join(r, 'rec_%s.mp4.idx' % e), 'w').write('f\n' * 2999), 'E video index', False, name='2 999 records')
    ok &= one(E, lambda r, e=E: os.remove(os.path.join(r, 'rec_%s.mp4.idx' % e)), 'E video index', None, name='no index')
    ok &= one(E, lambda r, e=E: put(r, 'runs/%s/glitch.txt' % e, 'one-frame glitches: 1\n'), 'E 0 one-frame', False, name='1 glitch')
    ok &= one(E, lambda r, e=E: os.remove(os.path.join(r, 'runs', e, 'glitch.txt')), 'E 0 one-frame', None, name='no glitch file')
    ok &= one(E, lambda r, e=E: put(r, 'runs/%s/sheet.txt' % e, 'error\n'), 'E sheet', False, name='sheet not made')
    ok &= one(E, lambda r, e=E: os.remove(os.path.join(r, 'runs', e, 'sheet.txt')), 'E sheet', None, name='no sheet file')
    ok &= one(E, logedit(E, 'GuestOut: hello', (AVL % SRC_HASHES[1]) + '\nGuestOut: hello'), 'E translations in the game', False,
              name='a catalogue program translated after the preparation line')
    ok &= one(E, logedit(E, 'ShaderPreparation', (AVL % SRC_HASHES[0]) + '\nShaderPreparation'), 'E translations in the game', True,
              name='a catalogue program translated before the preparation line')
    ok &= one(E, logedit(E, 'ShaderPreparation: startup wait finished', 'ShaderPreparation: x'), 'E translations in the game', None,
              name='no preparation line')
    ok &= one(E, lambda r: shutil.rmtree(os.path.join(r, 'state', 's18_c19')), 'E translations in the game', None, name='catalogue missing')
    ok &= one(E, lambda r: write_replay(os.path.join(r, 'state', 's18_c19', 'replay'), G19, hashes=(0xBBBB, SRC_HASHES[0])),
              'E translations in the game', False, name='the program translated in the game is in the catalogue of s18_c19')

# ------------------------------------------------------------------------------------------------ s18_v
V = 's18_v'
ok &= one(V, logedit(V, 'compat=ok', 'compat=absent'), 'V mode line', False, name='compat absent')
ok &= one(V, logedit(V, SKIP_RC, rb_line()), 'V line rebuild skipped', True, name='a rebuild with a screen of 500 ms')
ok &= one(V, multi(logedit(V, SKIP_RC, rb_line()), logedit(V, 'finished in 500 ms', 'finished in 180001 ms')), 'V line rebuild skipped', False,
          name='a rebuild with a screen of 180 001 ms')
ok &= one(V, multi(logedit(V, SKIP_RC, rb_line()), logedit(V, 'finished in 500 ms', 'finished in 180000 ms')), 'V line rebuild skipped', True,
          name='a rebuild with a screen of 180 000 ms (edge)')
ok &= one(V, logedit(V, SKIP_RC, 'ShaderReplay: rebuild skipped reason=no_catalogue'), 'V line rebuild skipped', False, name='no_catalogue')
ok &= one(V, logedit(V, SKIP_RC, SKIP_RC + '\n' + rb_line()), 'V line rebuild skipped', False, name='both lines')
ok &= one(V, logedit(V, SKIP_RC, 'nothing'), 'V line rebuild skipped', False, name='neither line')
ok &= one(V, logedit(V, 'n=12 dt_us=100000 ', 'n=12 dt_us=100000 draws=500\nFrameTrace: n=99998 dt_us=1200000 '), 'V 0 frames >= 1 s', False,
          name='a long frame')
ok &= one(V, setatt(V, hold_s=329.0), 'V the process lived', False, name='hold 329 s')
ok &= one(V, lambda r: put(r, 'runs/%s/glitch.txt' % V, 'one-frame glitches: 2\n'), 'V 0 one-frame', False, name='2 glitches')

# ------------------------------------------------------------------------------------------------ s18_w
W = 's18_w'
ok &= one(W, logedit(W, 'GuestOut: hello', '[Vulkan][E] VUID x\nGuestOut: hello'), 'W 0 [Vulkan][E]', False, name='one error')
ok &= one(W, logedit(W, '[Vulkan][W] some warning', 'other'), 'W positive control', False, name='no warning line')
ok &= one(W, lambda r: logput(r, W, log_lines(SKY, prep=90000, before=[MODE3 % (G19, 'none'), rb_line(), '[Vulkan][W] w'],
                                             after=[DUAL])), 'W positive control', False, name='DualSrcBlend after the first GuestOut')
ok &= one(W, logedit(W, DUAL, 'DualSrcBlend: supported=1 enabled=0'), 'W positive control', False, name='dual enabled 0')
ok &= one(W, logedit(W, 'GuestOut: Level has started: ', 'GuestOut: y: '), 'W entered', False, name='not entered')
ok &= one(W, setatt(W, hold_s=309.9), 'W the process lived', False, name='hold 309.9 s')
ok &= one(W, setatt(W, hold_s=310.0), 'W the process lived', True, name='hold 310.0 s (edge)')

# ------------------------------------------------------------------------------------------------ output: gate lines, table, cp1250
use(B0)
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    R.main(['s18_c01'])
out = buf.getvalue().split('\n')
ok &= check('  ACCUMULATION s18_c01 OK' in out and '  SIGNATURE_571G3 s18_c01 OK' in out and '  READING MEMBERS_PASS' in out,
            'print_rows: gate lines exactly as go_s18c.sh greps them (two spaces, whole line)')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    R.main(['s18_c02'])
ok &= check('  ACCUMULATION s18_c02 OK' in buf.getvalue().split('\n') and 'SIGNATURE_571G3 s18_c02' not in buf.getvalue(),
            'print_rows: s18_c02 has its ACCUMULATION line and no SIGNATURE line')
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    R.main(['--table'])
tb = buf.getvalue()
ok &= check(tb.count('READING MEMBERS_PASS') == 25 and 'S18a2 ACCEPTED item 578' in tb and 'S18b2 ACCEPTED item 579' in tb,
            'table: 25 tags read, members (1)-(2) of item 569 (d)(5) by S18a2 / S18b2')
jp = os.path.join(TMP, 'w.json')
with contextlib.redirect_stdout(io.StringIO()):
    R.main(['s18_r', '--json', jp])
jd = json.load(open(jp))
ok &= check(jd['reading'] == 'MEMBERS_PASS' and jd['extra']['rebuild']['records'] == '10' and jd['lines'] == [], 'json output of s18_r')
raw = io.BytesIO()
wrap = io.TextIOWrapper(raw, encoding='cp1250', errors='strict')
try:
    with contextlib.redirect_stdout(wrap):
        for _t in ('s18_c01', 's18_ks', 's18_r', 's18_e1', 's18_v', 's18_w'):
            R.main([_t])
        R.main(['--table'])
    wrap.flush()
    cp_ok = True
except UnicodeEncodeError:
    cp_ok = False
ok &= check(cp_ok and len(raw.getvalue()) > 1000, 'output in strict cp1250 without PYTHONIOENCODING')
with contextlib.redirect_stdout(io.StringIO()):
    _rc = R.main([])
ok &= check(_rc == 2, 'no argument -> usage, rc 2')

print('checks %d' % N[0])
print('ALL OK' if ok else 'SOME FAILED')
sys.exit(0 if ok else 1)
