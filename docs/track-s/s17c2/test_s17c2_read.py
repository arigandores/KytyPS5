"""S17c2 (HPP-640): fixtures of the S17c2 reader s17c2_read.py (seal edition 4; ROADMAP s122 item 561 (g)(1)-(3), (d), item 565 (g), item 566
(v)(g)).  Two synthetic roots: ED3 (the edition 3 states the new tags read: the Sky Garden catalogue s17c_c2, the live folder s17c_n0, the
read.json of s17c_c2 and of carried tags) and ROOT with the eight tags of edition 4 made; the baseline reads MEMBERS_PASS everywhere; then one
change per admission row, form row and member, and every edge: the K4 lookup key field by field (3 Buffer fields, 12 Image fields, the
push-data start, the vector lengths, the padding bytes), the 0.90 shares, the close path of item 566 (v) line by line and the permutation of
stand stop seen / close stop requested, the remainder a + b = N of item 565 (g) at a = 0, b = 0, a + b != N, different records, a timeout line,
the identity admission of item 566 (g) (a cache return between s17c_ks2 and s17c_kn2, different manifests before s17c_ks2 and s17c_r3b, the
KYTY_S_REPLAY and KYTY_SHADER_SEED of the three tags), the seed line and environment of item 561 (d)(3), K3 / K5 on hoover_beach.
The mutlib early-exit form: the only bindings of the flag are `ok = True` and `ok &= ...`, the last statement is `sys.exit(0 if ok else 1)`.
The first output line names the suite and the targets with sha256; the output ends with ALL OK.  Synthetic files only, no game.  ASCII only.
usage: python test_s17c2_read.py [<s17c2_read.py under test>]"""
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
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 's17c2_read.py')
sys.path.insert(0, HERE)
import r_addr  # noqa: E402
import tc_s17c  # noqa: E402


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


print('suite test_s17c2_read.py sha256 %s target s17c2_read.py sha256 %s tc_s17c.py sha256 %s state_s17c.py sha256 %s r_addr.py sha256 %s'
      % (sha(os.path.abspath(__file__)), sha(SRC), sha(os.path.join(HERE, 'tc_s17c.py')), sha(os.path.join(HERE, 'state_s17c.py')),
         sha(os.path.join(HERE, 'r_addr.py'))))
_spec = importlib.util.spec_from_file_location('s17c2_read_under_test', SRC)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)
N = [0]


def check(cond, name):
    N[0] += 1
    print(('ok   ' if cond else 'FAIL ') + name)
    return bool(cond)


# ------------------------------------------------------------------------------------------------ builders: translation cache

MAGIC = 0x07230203


def u32(v):
    return struct.pack('<I', v)


def shader_info_empty():
    return u32(0) + u32(0) + u32(0) + u32(0) + u32(0) + u32(0) + b'\x00' * 32 + struct.pack('<ii', -1, -1) + b'\x00\x00'


def plan_bytes():
    b = u32(0) + struct.pack('<Q', 0x1234) + u32(0) + u32(4)
    b += u32(0) + u32(0) + u32(0) + u32(0) + u32(0) + u32(0)
    b += b'\x01\x01\x01'
    b += u32(0)
    b += b'\x00' * tc_s17c.SZ_UNIFORM_FILL + (u32(3) + struct.pack('<Q', 0)) * 4
    b += shader_info_empty()
    return b


IMG0 = (1, 2, 3, 4, 5, 6, 7, 8, 1, 0, 3, 1)
IMG1 = (9, 1, 1, 0x30, 0x688, 0xffffffff, 0, 0, 0, 1, 4, 0)


def img(f, pad=b'\x00' * 5):
    return struct.pack('<8I', *f[:8]) + bytes([f[8], f[9]]) + pad[0:2] + struct.pack('<I', f[10]) + bytes([f[11]]) + pad[2:5]


def spec_b(bufs, imgs, pads=None):
    b = u32(len(bufs)) + b''.join(struct.pack('<3I', *x) for x in bufs) + u32(len(imgs))
    for i, f in enumerate(imgs):
        b += img(f, (pads or {}).get(i, b'\x00' * 5))
    return b


def cache_bytes(sig, perms, phash):
    pay = u32(0) + struct.pack('<Q', phash) + u32(4) + u32(16) + u32(2) + u32(1) + u32(2)
    pay += plan_bytes()
    pay += u32(len(perms))
    for (spec, start, words) in perms:
        pay += spec
        pay += u32(0) + struct.pack('<Q', phash) + u32(64) + u32(0) + u32(4) + u32(0) + u32(0)
        pay += shader_info_empty()
        pay += u32(start) + u32(0) + u32(0) + u32(0) + u32(0)
        pay += u32(len(words)) + b''.join(u32(x) for x in words)
    return (sig + '\n').encode() + struct.pack('<Q', xxhash.xxh3_64_intdigest(pay)) + pay


def spirv_xxh(words):
    return xxhash.xxh3_64_intdigest(b''.join(u32(x) for x in words))


FA = 'vs_00000000000000a1_0000000000000001.bin'
FB = 'ps_00000000000000b1_0000000000000002.bin'
FC = 'cs_00000000000000c1_0000000000000003.bin'
LIVE = {
    FA: [(spec_b([(1, 2, 3)], []), 0, [MAGIC, 1]), (spec_b([(4, 5, 6)], []), 4, [MAGIC, 2]), (spec_b([(7, 8, 9)], []), 0, [MAGIC, 3]),
         (spec_b([(1, 2, 3), (4, 5, 6)], []), 0, [MAGIC, 4])],
    FB: [(spec_b([], [IMG0]), 8, [MAGIC, 5]), (spec_b([], [IMG1]), 8, [MAGIC, 6]), (spec_b([(1, 1, 1)], [IMG0, IMG1]), 12, [MAGIC, 7])],
    FC: [(spec_b([(9, 9, 9)], []), 0, [MAGIC, 8]), (spec_b([(9, 9, 9)], []), 4, [MAGIC, 9]), (spec_b([], []), 0, [MAGIC, 10])],
}


def rebuilt(padded=True, change=None):
    """The rebuilt folder: every live permutation in reverse order per file; the first image of FB[0] carries padding bytes 0x11 (the
    raw-bytes key misses it, the lookup key hits it); change(files) may edit the result."""
    files = dict((n, list(reversed(p))) for n, p in LIVE.items())
    if padded:
        fb = list(files[FB])
        fb[2] = (spec_b([], [IMG0], {0: b'\x11' * 5}), 8, [MAGIC, 5])
        files[FB] = fb
    if change:
        change(files)
    return files


def write_folder(d, files, sig=None, pipelines=True):
    shutil.rmtree(d, ignore_errors=True)
    os.makedirs(d)
    for name, perms in files.items():
        open(os.path.join(d, name), 'wb').write(cache_bytes(sig or R.SIG1, perms, int(name[3:19], 16)))
    if pipelines:
        open(os.path.join(d, 'pipelines.bin'), 'wb').write(b'KRCP')


def manifest_of(files, skip=(), sig=None):
    lines = ['%s\t%d\t%016x\t%d\t%016x' % (n, i, 0x55, p[1], spirv_xxh(p[2])) for n in sorted(files) for i, p in enumerate(files[n])
             if (n, i) not in skip]
    return '# ShaderReplay rebuild manifest; signature ' + (sig or R.SIG1) + '\n' + '\n'.join(lines) + '\n'


# ------------------------------------------------------------------------------------------------ builders: catalogue

L = r_addr.LAYOUT
SRC_HASHES = (0xAAAA000000000001, 0xAAAA000000000002)
CANON = [(0x100, 2), (0, 3), (7, 0), (0x20000, 0), (1, 6), (0, 9)]
RAW = [(0x12345678, 2), (2, 3), (7, 0), (0x20000, 0), (0x40000, 6), (0x1234, 9)]


def catalogue_bytes(gen, words, compat=b'KytyReplay1:PPSA21564:01.000:key1:canon1:input1:pod1.2.3'):
    body = b''
    for k, h in enumerate(SRC_HASHES):
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
    struct.pack_into('<QQIII', bh, 0, gen, xxhash.xxh3_64_intdigest(body), len(SRC_HASHES), 1, 1)
    return bytes(head) + compat + bytes(bh) + body


def write_replay(d, gen, words=CANON, manifest=None):
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'replay.cur'), 'wb').write(b'%d\n' % gen)
    open(os.path.join(d, 'replay.%d.bin' % gen), 'wb').write(catalogue_bytes(gen, words))
    if manifest is not None:
        open(os.path.join(d, 'rebuild_manifest.tsv'), 'wb').write(manifest.encode())


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
    e['VK_SDK_PATH'] = 'C:/VulkanSDK'
    return e


def log_lines(level, before=(), after=(), entry=True, ft=True, dirname=None, prep=12000, av_after=(), rev=None):
    out = ['Fork build arigandores/KytyPS5 %s, test' % (rev or R.REV),
           'Shader translation cache: _ShaderCache' + chr(92) + 'PPSA21564' + chr(92) + (dirname or R.DIR1)]
    out += list(before)
    if prep is not None:
        out.append('ShaderPreparation: startup wait finished in %d ms presents_other=0 presents_main=0' % prep)
    out += list(av_after)
    out.append('GuestOut: hello')
    if entry:
        out.append('GuestOut: Level has started: ' + level)
    if ft:
        out.append('FrameTrace: n=10 dt_us=16000 draws=500')
        out += ['FrameTrace: n=%d dt_us=75000000 draws=500' % (11 + k) for k in range(4)]
    out += list(after)
    return out


def rb_line(records=10, prepared=9, rejected=1, pending=0, fused=1, perms_new=8, cached=0, pb='written'):
    return ('ShaderReplay: rebuild records=%d prepared=%d rejected=%d pending=%d rej_src=0 rej_fused=%d rej_key=0 rej_version=0 rej_shape=0 '
            'rej_translate=0 rej_emit=0 rej_val=0 rej_write=0 rej_ref=0 translate_ms=10 wall_ms=20 perms_new=%d perms_cached=%d '
            'rb_push_moved=0 rb_spec_changed=0 groups_same_pc=1 group_sources=3 pipelines_bin=%s' % (
                records, prepared, rejected, pending, fused, perms_new, cached, pb))


CAP = 'ShaderReplay: capture sources=5 specs=6 pipes=10 canon_mismatch=0 dropped_queue=0 bytes=100 gen=3 canon_self=0 canon_residual=0 ' \
      'canon_base=0 canon_big=0 pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=%s'
MODE2 = 'ShaderReplay: mode=2 dir=_ShaderCache\\PPSA21564\\replay compat=absent generation=0 corrupt=0 sources=0 specs=0 pipes=0 test=none'
MODE3 = 'ShaderReplay: mode=3 dir=_ShaderCache\\PPSA21564\\replay compat=ok generation=%d corrupt=0 sources=5 specs=6 pipes=10 test=%s'
PNO = 'PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10\\pipelines.bin yet'
AVL = 'AvTrace: shader ShaderRecompiler VS hash=0x%016x translate_us=5 compile_us=6 permutations=1'
APPLIED = 'ShaderReplay: stand stop applied processed=5 records=10'
REQ = 'ShaderReplay: close stop requested precache_active=1'
SEEN = 'ShaderReplay: stand stop seen waited_ms=40 processed=5 records=10'
STOPPED = rb_line(prepared=5, rejected=0, pending=5, fused=0, perms_new=3, pb='stopped')
JOINED = 'ShaderReplay: close stop joined wait_ms=12'
SKY, HB = R.SKY, R.HOOVER


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


def logs_of(ed3, root):
    return {
        's17c_r3b': log_lines(SKY, entry=False, ft=False, before=[MODE3 % (3, 'none'), rb_line(), 'ShaderReplay: hits rb_used=0'],
                              av_after=[AVL % 0xBBBB]),
        's17c_rsb': log_lines(SKY, entry=False, ft=False, before=[MODE3 % (3, 'spec'),
                                                                  'ShaderReplay: stand spec applied file=%s permutation=2' % FB, rb_line()]),
        's17c_ks2': log_lines(SKY, entry=False, ft=False, prep=None, before=[MODE3 % (3, 'stop'), APPLIED, REQ, SEEN, STOPPED, JOINED]),
        's17c_kn2': log_lines(SKY, ft=False, before=[MODE3 % (3, 'none'), rb_line(perms_new=5, cached=4)]),
        's17c_c2h': log_lines(HB, dirname=R.DIR0, before=[MODE2, PNO], after=[CAP % 'save', CAP % 'stop']),
        's17c_n0h': log_lines(HB, av_after=[AVL % SRC_HASHES[0], AVL % 0xBBBB]),
        's17c_r3h': log_lines(HB, entry=False, ft=False, before=[MODE3 % (3, 'none'), rb_line()], av_after=[AVL % 0xBBBB]),
        's17c_e3h': log_lines(HB, prep=20000, before=[MODE3 % (3, 'none'), 'ShaderReplay: rebuild skipped reason=recipes_current'],
                              av_after=[AVL % 0xBBBB]),
    }


def att_for(tag):
    spec = R.SPEC[tag]
    a = dict(label='attempt 1', outcome='prep' if spec['form'] == 'p' else 'ok', hold_exit=None, hold_s=float(spec['hold']), close_rc=0,
             close_killed=False, close_s=2.0, detail=None)
    if tag == 's17c_ks2':
        a.update(outcome='exited', detail='exit code 0', close_rc=None, close_killed=None)
    return a


def make_ed3(ed3):
    st = os.path.join(ed3, 'state')
    write_replay(os.path.join(st, 's17c_c2', 'replay'), 3)
    write_folder(os.path.join(st, 's17c_n0', 'f19'), LIVE)
    for tag in R.CARRIED:
        os.makedirs(os.path.join(ed3, 'runs', tag), exist_ok=True)
        d = dict(reading='MEMBERS_PASS', members=[['K member of %s' % tag, True, 'x']], extra={})
        if tag == 's17c_c2':
            d['extra'] = dict(pipes_waiting=0)
        json.dump(d, open(os.path.join(ed3, 'runs', tag, 'read.json'), 'w'))


def make_root(root, ed3):
    os.makedirs(os.path.join(root, 'runs'), exist_ok=True)
    seal = os.path.join(root, 'seal.md')
    open(seal, 'wb').write(b'seal edition 4 of the fixtures\n')
    open(os.path.join(root, 'bin.exe'), 'wb').write(b'MZ...' + R.VERSION + b'...')
    st = os.path.join(root, 'state')
    rb = rebuilt()
    write_folder(os.path.join(st, 's17c_r3b', 'f19'), rb)
    write_replay(os.path.join(st, 's17c_r3b', 'replay'), 3, manifest=manifest_of(rb))
    rbs = rebuilt(change=lambda f: f[FB].__setitem__(2, (f[FB][2][0], 8, [MAGIC, 55])))
    write_folder(os.path.join(st, 's17c_rsb', 'f19'), rbs)
    write_replay(os.path.join(st, 's17c_rsb', 'replay'), 3, manifest=manifest_of(rbs))
    write_folder(os.path.join(st, 's17c_ks2', 'f19'), {FA: LIVE[FA]}, pipelines=False)
    write_replay(os.path.join(st, 's17c_ks2', 'replay'), 3)
    write_replay(os.path.join(st, 's17c_c2h', 'replay'), 3)
    write_folder(os.path.join(st, 's17c_c2h', 'f10'), {FA: LIVE[FA]}, sig=R.SIG0)
    write_folder(os.path.join(st, 's17c_n0h', 'f19'), LIVE)
    write_folder(os.path.join(st, 's17c_r3h', 'f19'), rb)
    write_replay(os.path.join(st, 's17c_r3h', 'replay'), 3, manifest=manifest_of(rb))
    c2rp = os.path.join(ed3, 'state', 's17c_c2', 'replay')
    states_in = {
        'cat_c2': state_text(f10='10 abc', replay_dir=c2rp),
        'k_ks2': state_text(f10='10 abc', f19='absent', replay_dir=os.path.join(st, 's17c_ks2', 'replay')),
        'empty_f10': state_text(),
        'empty_f19': state_text(f10='10 abc'),
        'cat_c2h': state_text(f10='10 abc', replay_dir=os.path.join(st, 's17c_c2h', 'replay')),
        'rb_r3h': state_text(f10='10 abc', f19='10 def', replay_dir=os.path.join(st, 's17c_r3h', 'replay')),
    }
    logs = logs_of(ed3, root)
    for tag in R.ORDER:
        spec = R.SPEC[tag]
        d = os.path.join(root, 'runs', tag)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(root, 'log_%s.txt' % tag), 'w', newline='\n').write('\n'.join(logs[tag]) + '\n')
        open(os.path.join(root, 'stdout_%s.txt' % tag), 'w', newline='\n').write('Shaders: VS 1 | PS 1\nKytyPS5 git = %s, x\n' % R.REV)
        run = dict(tag=tag, binary_sha256=R.BIN_EXPECT, env=env_for(tag), cmdline=['kyty_emulator.exe', '--vulkan-validation', 'false'],
                   prereg=dict(sha256=sha(seal)), attempts=[att_for(tag)])
        json.dump(run, open(os.path.join(root, '%s.json' % tag), 'w'))
        open(os.path.join(root, 'rec_%s.mp4.idx' % tag), 'w').write('f\n' * 3000)
        w = lambda n, t: open(os.path.join(d, n), 'w', newline='\n').write(t)  # noqa: E731
        w('installed_sha.txt', R.BIN_EXPECT + '\n')
        w('installed_before.txt', R.FS8 + '\n')
        w('installed_after.txt', R.FS8 + '\n')
        w('manifest_cmp.txt', 'manifest cmp EQUAL files 9 listsha 00\n')
        w('glitch.txt', 'one-frame glitches: 0\n')
        w('sheet.txt', 'sheet: C:/x/sheet.png\n')
        w('state_in_name.txt', spec['state'] + '\n')
        w('state_in.txt', states_in[spec['state']])
        w('state_out.txt', 'dir f10 present files 3 cache_files 2 pipelines_bin 10 abc\ndir f19 present files 3 cache_files 3 pipelines_bin '
                           '%s\ndir replay absent\n' % ('absent' if tag == 's17c_ks2' else '10 def'))
    for tag, name, t in (('s17c_r3b', 'mf_in.tsv', 'f19\t<MISSING>\t0\t-\nreplay\treplay.cur\t2\taa\n'),
                         ('s17c_ks2', 'mf_in.tsv', 'f19\t<MISSING>\t0\t-\nreplay\treplay.cur\t2\taa\n'),
                         ('s17c_ks2', 'mf_out.tsv', 'f19\tvs_a.bin\t9\tbb\nreplay\treplay.cur\t2\taa\n'),
                         ('s17c_kn2', 'mf_in.tsv', 'f19\tvs_a.bin\t9\tbb\nreplay\treplay.cur\t2\taa\n')):
        open(os.path.join(root, 'runs', tag, name), 'w', newline='\n').write(t)


def use(root, ed3):
    R.ROOT = root
    R.ED3 = ed3
    R.SEAL_PATH = os.path.join(root, 'seal.md')
    R.BIN_PATH = os.path.join(root, 'bin.exe')


def read_tags(root, ed3, tags):
    use(root, ed3)
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


def rowdet(rows, prefix):
    for name, ok_, det in rows.mem + rows.adm + rows.form:
        if name.startswith(prefix):
            return det
    for name, det in rows.rep:
        if name.startswith(prefix):
            return det
    return ''


BASE = Path('C:/kyty/s288/s17c2/fx_s17c2')   # mutlib gives every job its own copy of this directory
shutil.rmtree(BASE, ignore_errors=True)
BASE.mkdir(parents=True)
TMP = str(BASE)
ED3B = os.path.join(TMP, 'ed3')
B0 = os.path.join(TMP, 'base')
make_ed3(ED3B)
make_root(B0, ED3B)
WB = read_tags(B0, ED3B, R.ORDER)
K = [0]


def variant(change, tag, ed3_change=None):
    """A copy of the baseline root (and of ED3 when ed3_change is given) with the changes; the tags up to tag re-read in order."""
    K[0] += 1
    root = os.path.join(TMP, 'v%03d' % K[0])
    shutil.copytree(B0, root)
    ed3 = ED3B
    if ed3_change is not None:
        ed3 = os.path.join(TMP, 'e%03d' % K[0])
        shutil.copytree(ED3B, ed3)
        ed3_change(ed3)
    if change is not None:
        change(root)
    return read_tags(root, ed3, [t for t in R.ORDER if R.ORDER.index(t) <= R.ORDER.index(tag)])[tag]


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


def one(tag, change, prefix, want, kind='m', name=None, ed3_change=None):
    rows = variant(change, tag, ed3_change)
    got = rowval(rows, prefix, kind)
    return check(got == want, '%s: %s -> %s (got %s, reading %s)' % (tag, name or prefix[:70], R.yn(want) if want != 'MISSING' else want,
                                                                   R.yn(got) if got in (True, False, None) else got, rows.word()))


def word(tag, change, want, name, ed3_change=None):
    rows = variant(change, tag, ed3_change)
    return check(rows.word() == want, '%s: %s -> %s (got %s)' % (tag, name, want, rows.word()))


def setenv(tag, key, value):
    def ch(root):
        def f(d):
            if value is None:
                d['env'].pop(key, None)
            else:
                d['env'][key] = value
        edit_json(root, tag, f)
    return ch


ok = True
for _t in R.ORDER:
    _w = WB[_t]
    ok &= check(_w.word() == 'MEMBERS_PASS', 'baseline %s reads MEMBERS_PASS (got %s %s)' % (
        _t, _w.word(), [x for x in _w.adm + _w.form + _w.mem if x[1] is not True][:2]))

# ------------------------------------------------------------------------------------------------ constants of the print
ok &= check(R.BIN_EXPECT == '43ef1cc14ec2c116fdcce9ac71f9d854d0ec6498bd6e538fa479b1ecdf57fbb3', 'binary S17a5 43ef1cc1 (item 565 (b))')
ok &= check(R.VERSION == b'KytyPS5-2026-09-15-6a2987a-2337-gc0057ccb' and R.REV == 'c0057cc', 'version string and revision of c0057ccb')
ok &= check(R.INSTALLED_OK == ('2c9b69b906f882ce4d2e45862c870d491469fd9101cc53ba26e6ec43c8e3013b',), 'installed FS8 only')
ok &= check(R.ORDER == ('s17c_r3b', 's17c_rsb', 's17c_ks2', 's17c_kn2', 's17c_c2h', 's17c_n0h', 's17c_r3h', 's17c_e3h'),
            'eight tags of item 561 (d)(2) in order')
ok &= check(R.CARRIED == ('s17c_v0', 's17c_w0', 's17c_c2', 's17c_ca', 's17c_cc', 's17c_n0', 's17c_e3', 's17c_ew', 's17c_kc'),
            'carried tags of item 561 (d)(1)')
ok &= check(all(R.SPEC[t]['env'].get('KYTY_SHADER_SEED') == '0' for t in R.ORDER), 'KYTY_SHADER_SEED=0 in the form of every tag')
ok &= check((R.HIT_MIN, R.SHARE_MIN, R.PREP_MAX_MS, R.VIDEO_MIN, R.HOLD_MIN_US, R.K2_US) == (0.90, 0.90, 180000, 3000, 300000000, 1000000),
            'constants of item 524 (z) / 561: 0.90, 0.90, 180 000 ms, 3 000 records, 300 s, 1 s')
ok &= check(R.SIG1.endswith(':fixb26:fixb1b:fixf10:fixf19') and R.SIG0 + ':fixf19' == R.SIG1 and R.DIR1 == R.DIR0 + '_fixf19' and
            R.SKY == 'underwater_aerial_garden' and R.HOOVER == 'hoover_beach', 'signatures, folders and levels')
ok &= check([R.SPEC[t]['level'] for t in R.ORDER] == [SKY] * 4 + [HB] * 4, 'levels: Sky Garden x4, hoover_beach x4')
ok &= check(R.SPEC['s17c_c2h']['env'] == {'KYTY_S_REPLAY': '2', 'KYTY_FIX_F19': '0', 'KYTY_SHADER_SEED': '0'} and
            R.SPEC['s17c_n0h']['env'] == {'KYTY_S_REPLAY': '0', 'KYTY_FIX_F19': '1', 'KYTY_AV_TRACE': '1', 'KYTY_SHADER_SEED': '0'} and
            R.SPEC['s17c_ks2']['env'].get('KYTY_S_REPLAY_TEST') == 'stop' and R.SPEC['s17c_rsb']['env'].get('KYTY_S_REPLAY_TEST') == 'spec'
            and 'KYTY_S_REPLAY_TEST' not in R.SPEC['s17c_kn2']['env'] and R.SPEC['s17c_e3h']['env']['KYTY_S_REPLAY'] == '3',
            'forms of the tags (capture =2 F19=0, control =0 F19=1, stands, =3)')
ok &= check([(R.SPEC[t]['form'], R.SPEC[t]['hold'], R.SPEC[t]['state']) for t in R.ORDER] == [
    ('p', 0, 'cat_c2'), ('p', 0, 'cat_c2'), ('p', 0, 'cat_c2'), ('n', 60, 'k_ks2'), ('v', 330, 'empty_f10'), ('v', 330, 'empty_f19'),
    ('p', 0, 'cat_c2h'), ('v', 330, 'rb_r3h')], 'forms, holds and input states')

# ------------------------------------------------------------------------------------------------ K4 lookup key field by field
SB = spec_b([(10, 20, 30)], [IMG0])
PB = dict(spec=SB, start=8)
KB = R.perm_key(FB, PB, 'lookup')
ok &= check(KB is not None and R.perm_key(FB, dict(spec=spec_b([(10, 20, 30)], [IMG0], {0: b'\x7f\x01\xff\x02\x03'}), start=8), 'lookup') == KB,
            'lookup key: a difference only in the 5 padding bytes of an image is a hit (item 561 (g)(1))')
ok &= check(R.perm_key(FB, dict(spec=spec_b([(10, 20, 30)], [IMG0], {0: b'\x7f\x01\xff\x02\x03'}), start=8), 'raw') !=
            R.perm_key(FB, PB, 'raw'), 'raw key (reference): the padding difference is a miss')
for _j in range(12):
    _f = list(IMG0)
    _f[_j] = _f[_j] + 1 if _f[_j] < 255 else 0
    ok &= check(R.perm_key(FB, dict(spec=spec_b([(10, 20, 30)], [tuple(_f)]), start=8), 'lookup') != KB,
                'lookup key: Image field %d differs -> miss' % _j)
for _j in range(3):
    _b = [10, 20, 30]
    _b[_j] += 1
    ok &= check(R.perm_key(FB, dict(spec=spec_b([tuple(_b)], [IMG0]), start=8), 'lookup') != KB, 'lookup key: Buffer field %d differs -> miss' % _j)
ok &= check(R.perm_key(FB, dict(spec=SB, start=9), 'lookup') != KB, 'lookup key: push-data start differs -> miss')
ok &= check(R.perm_key(FA, PB, 'lookup') != KB, 'lookup key: cache file name differs -> miss')
ok &= check(R.perm_key(FB, dict(spec=spec_b([(10, 20, 30)], [IMG0, IMG0]), start=8), 'lookup') != KB, 'lookup key: one more image -> miss')
ok &= check(R.perm_key(FB, dict(spec=spec_b([(10, 20, 30), (10, 20, 30)], [IMG0]), start=8), 'lookup') != KB,
            'lookup key: one more buffer -> miss')
ok &= check(R.spec_fields(SB) == (((10, 20, 30),), (IMG0,)), 'spec_fields: buffers and the 12 image fields in their order')
ok &= check(R.spec_fields(SB[:-1]) is None and R.spec_fields(SB + b'\x00') is None and R.spec_fields(b'\x01\x00') is None and
            R.spec_fields(u32(5) + b'\x00' * 8) is None, 'spec_fields: None for a short, long or truncated specialization')
ok &= check(R.SPEC_BUFFER == 12 and R.SPEC_IMAGE == 44, 'POD sizes Buffer 12, Image 44')

# ------------------------------------------------------------------------------------------------ admission and form
ok &= word('s17c_r3b', lambda r: edit_json(r, 's17c_r3b', lambda d: d.update(binary_sha256='0' * 64)), 'NOT_ADMITTED', 'other binary in json')
ok &= word('s17c_r3b', lambda r: put(r, 'runs/s17c_r3b/installed_sha.txt', 'ed2686da\n'), 'NOT_ADMITTED', 'installed_sha.txt not 43ef1cc1')
ok &= word('s17c_r3b', lambda r: open(os.path.join(r, 'bin.exe'), 'wb').write(b'MZ KytyPS5-2026-09-15-6a2987a-2336-g9238a182'),
           'NOT_ADMITTED', 'version string of S17a4 in the binary copy')
ok &= word('s17c_r3b', lambda r: edit(r, 'log_s17c_r3b.txt', 'KytyPS5 c0057cc,', 'KytyPS5 9238a18,'), 'NOT_ADMITTED', 'revision 9238a18 in the log')
ok &= word('s17c_r3b', lambda r: (edit(r, 'log_s17c_r3b.txt', 'Fork build arigandores/KytyPS5 c0057cc, test', 'x'),
                                  put(r, 'stdout_s17c_r3b.txt', 'nothing\n')), 'NOT_ADMITTED', 'no revision text at all')
ok &= word('s17c_r3b', lambda r: edit_json(r, 's17c_r3b', lambda d: d.update(prereg=dict(sha256='1' * 64))), 'NOT_ADMITTED', 'prereg of other seal')
ok &= word('s17c_r3b', setenv('s17c_r3b', 'KYTY_SHADER_SEED', None), 'NOT_ADMITTED', 'KYTY_SHADER_SEED absent (item 561 (d)(3))')
ok &= word('s17c_c2h', setenv('s17c_c2h', 'KYTY_SHADER_SEED', None), 'NOT_ADMITTED', 'KYTY_SHADER_SEED absent on the capture tag')
ok &= word('s17c_n0h', setenv('s17c_n0h', 'KYTY_SHADER_SEED', '1'), 'NOT_ADMITTED', 'KYTY_SHADER_SEED=1')
ok &= word('s17c_e3h', setenv('s17c_e3h', 'KYTY_SHADER_PREPARE', '0'), 'NOT_ADMITTED', 'extra KYTY_SHADER_PREPARE')
ok &= word('s17c_ks2', setenv('s17c_ks2', 'KYTY_S_REPLAY_TEST', 'spec'), 'NOT_ADMITTED', 'stand of the tag other than stop')
ok &= word('s17c_kn2', setenv('s17c_kn2', 'KYTY_S_REPLAY_TEST', 'stop'), 'NOT_ADMITTED', 'stand on the next start')
ok &= word('s17c_r3b', setenv('s17c_r3b', 'VK_LAYER_PATH', 'C:/x'), 'NOT_ADMITTED', 'VK_LAYER_PATH present')
ok &= word('s17c_c2h', setenv('s17c_c2h', 'KYTY_GUEST_ARGS', '-lvl ' + SKY), 'NOT_ADMITTED', 'guest args of the other level')
ok &= word('s17c_c2h', setenv('s17c_c2h', 'KYTY_REC', None), 'NOT_ADMITTED', 'v form without KYTY_REC')
ok &= word('s17c_r3b', setenv('s17c_r3b', 'KYTY_REC', 'C:/x/r.mp4'), 'NOT_ADMITTED', 'p form with KYTY_REC')
ok &= word('s17c_r3b', setenv('s17c_r3b', 'KYTY_GATE_FILE', None), 'NOT_ADMITTED', 'no KYTY_GATE_FILE')
ok &= word('s17c_r3b', lambda r: edit_json(r, 's17c_r3b', lambda d: d.update(cmdline=['x', '--vulkan-validation', 'true'])), 'NOT_ADMITTED',
           '--vulkan-validation true')
ok &= word('s17c_r3b', lambda r: edit(r, 'log_s17c_r3b.txt', 'GuestOut: hello', 'ShaderSeed: installed (727 shaders)\nGuestOut: hello'),
           'NOT_ADMITTED', 'one ShaderSeed: installed line in the log (item 561 (d)(3))')
ok &= word('s17c_n0h', lambda r: put(r, 'stdout_s17c_n0h.txt', 'KytyPS5 git = c0057cc, x\nShaderSeed: installed (727 shaders)\n'),
           'NOT_ADMITTED', 'one ShaderSeed: installed line in stdout')
ok &= word('s17c_e3h', lambda r: edit(r, 'log_s17c_e3h.txt', 'GuestOut: hello', 'Window 1 minimized\nGuestOut: hello'), 'NOT_ADMITTED',
           'window minimized')
ok &= word('s17c_e3h', lambda r: edit(r, 'log_s17c_e3h.txt', 'GuestOut: hello', 'GamePatch: x\nGuestOut: hello'), 'NOT_ADMITTED', 'GamePatch')
ok &= word('s17c_r3b', lambda r: put(r, 'runs/s17c_r3b/state_in_name.txt', 'cat_c2h\n'), 'NOT_ADMITTED', 'input state name other')
ok &= word('s17c_r3b', lambda r: os.remove(os.path.join(r, 'runs/s17c_r3b/state_in.txt')), 'NOT_ADMITTED', 'state_in.txt missing')
ok &= word('s17c_r3b', lambda r: edit(r, 'runs/s17c_r3b/state_in.txt', 'replay.cur 3', 'replay.cur 4'), 'MEMBERS_PASS',
           'replay.cur text is a report (files decide)')
ok &= word('s17c_r3b', None, 'NOT_ADMITTED', 'cat_c2: the edition 3 saved catalogue differs from the input replay',
           ed3_change=lambda e: open(os.path.join(e, 'state/s17c_c2/replay/replay.cur'), 'wb').write(b'3 \n'))
ok &= word('s17c_ks2', lambda r: edit(r, 'runs/s17c_ks2/state_in.txt', 'dir f19 absent', 'dir f19 present files 1 cache_files 1 pipelines_bin absent'),
           'NOT_ADMITTED', 'cat_c2: f19 present')
ok &= word('s17c_r3h', lambda r: edit(r, 'runs/s17c_r3h/state_in.txt', 'dir f19 absent', 'dir f19 present files 1 cache_files 1 pipelines_bin absent'),
           'NOT_ADMITTED', 'cat_c2h: f19 present')
ok &= word('s17c_c2h', lambda r: put(r, 'runs/s17c_c2h/state_in.txt', state_text(f19='1 a')), 'MEMBERS_PASS', 'empty_f10 with f19 present')
ok &= word('s17c_c2h', lambda r: put(r, 'runs/s17c_c2h/state_in.txt', state_text(replay_dir=os.path.join(r, 'state/s17c_c2h/replay'))),
           'NOT_ADMITTED', 'empty_f10: replay present')
ok &= word('s17c_c2h', lambda r: put(r, 'runs/s17c_c2h/state_in.txt', state_text(f10='1 a')), 'NOT_ADMITTED', 'empty_f10: f10 present')
ok &= word('s17c_n0h', lambda r: put(r, 'runs/s17c_n0h/state_in.txt', state_text(f19='1 a')), 'NOT_ADMITTED', 'empty_f19: f19 present')
ok &= word('s17c_e3h', lambda r: edit(r, 'runs/s17c_e3h/state_in.txt', 'pipelines_bin 10 def', 'pipelines_bin absent'), 'NOT_ADMITTED',
           'rb_r3h: f19 without pipelines.bin')
ok &= word('s17c_r3h', lambda r: open(os.path.join(r, 'state/s17c_c2h/replay/replay.cur'), 'wb').write(b'3 \n'), 'NOT_ADMITTED',
           'cat_c2h: replay differs from state/s17c_c2h')
ok &= word('s17c_kn2', lambda r: open(os.path.join(r, 'state/s17c_ks2/replay/replay.cur'), 'wb').write(b'3 \n'), 'NOT_ADMITTED',
           'k_ks2: replay differs from state/s17c_ks2')
ok &= word('s17c_r3b', lambda r: edit_json(r, 's17c_r3b', lambda d: d.update(attempts=[att_for('s17c_r3b')] * 2)), 'NOT_ADMITTED', 'two attempts')
ok &= word('s17c_r3b', lambda r: os.remove(os.path.join(r, 'log_s17c_r3b.txt')), 'NOT_ADMITTED', 'log missing')
ok &= word('s17c_c2h', lambda r: edit(r, 'log_s17c_c2h.txt', PNO, 'x'), 'NOT_ADMITTED', 'K3 fitness: no PipelinePrecache: no ... yet')
ok &= word('s17c_r3b', lambda r: put(r, 'runs/s17c_r3b/installed_after.txt', '0' * 64 + '\n'), 'FORM_FAIL', 'installed before != after')
ok &= word('s17c_r3b', lambda r: (put(r, 'runs/s17c_r3b/installed_after.txt', '9' * 64 + '\n'),
                                  put(r, 'runs/s17c_r3b/installed_before.txt', '9' * 64 + '\n')), 'FORM_FAIL', 'installed not FS8')
ok &= word('s17c_r3b', lambda r: put(r, 'runs/s17c_r3b/manifest_cmp.txt', 'manifest cmp DIFFER\n'), 'FORM_FAIL', 'manifest DIFFER')

# ------------------------------------------------------------------------------------------------ K4 (s17c_r3b, s17c_rsb, s17c_r3h)
ok &= check('10 / 10 / 10 / 0 / 0' in rowdet(WB['s17c_r3b'], 'lookup key') and '10 / 10 / 9 / 1 / 0' in rowdet(WB['s17c_r3b'], 'raw-bytes key'),
            'baseline r3b: lookup key 10/10 hit 10, raw key 9 hit 1 dead (the padding difference)')
H = 'K4 rb_hit / live_perms >= 0.90 by the lookup key'
M = 'K4 rb_live_mismatch = 0'
MAN = 'state/s17c_r3b/replay/rebuild_manifest.tsv'
ok &= one('s17c_r3b', lambda r: put(r, MAN, manifest_of(rebuilt(), skip=((FC, 0),))), H, True, name='rb_hit 9 / 10 = 0.90 edge')
ok &= one('s17c_r3b', lambda r: put(r, MAN, manifest_of(rebuilt(), skip=((FC, 0), (FA, 1)))), H, False, name='rb_hit 8 / 10 = 0.80')


def _field_change(root):
    rb = rebuilt(change=lambda f: f[FB].__setitem__(2, (spec_b([], [IMG0[:8] + (0,) + IMG0[9:]], {0: b'\x11' * 5}), 8, [MAGIC, 5])))
    write_folder(os.path.join(root, 'state/s17c_r3b/f19'), rb)
    put(root, MAN, manifest_of(rb))


_rows = variant(_field_change, 's17c_r3b')
ok &= check('10 / 10 / 9 / 1 / 0' in rowdet(_rows, 'lookup key') and rowval(_rows, H) is True,
            'r3b: the cube field of one rebuilt image differs -> one lookup miss (9 / 10), rb_dead 1')
ok &= one('s17c_r3b', lambda r: (write_folder(os.path.join(r, 'state/s17c_r3b/f19'),
                                              rebuilt(change=lambda f: f[FA].__setitem__(0, (f[FA][0][0], 0, [MAGIC, 99])))),
                                 put(r, MAN, manifest_of(rebuilt(change=lambda f: f[FA].__setitem__(0, (f[FA][0][0], 0, [MAGIC, 99])))))),
          M, False, name='one hit with another SPIR-V -> rb_live_mismatch 1')
ok &= one('s17c_r3b', lambda r: put(r, MAN, manifest_of(rebuilt()) + '%s\t9\t%016x\t0\t%016x\n' % (FA, 0x55, 1)),
          'K4 comparison self-checks', False, name='manifest row without its permutation')
ok &= one('s17c_r3b', lambda r: put(r, MAN, manifest_of(rebuilt(), sig=R.SIG0)), 'K4 comparison self-checks', False, name='manifest signature F19=0')
ok &= one('s17c_r3b', lambda r: put(r, MAN, manifest_of(rebuilt()) + 'garbage line\n'), 'K4 comparison self-checks', False,
          name='a bad manifest line')
ok &= one('s17c_r3b', lambda r: put(r, MAN, manifest_of(rebuilt()) + 'garbage line\n'), H, None, name='self-check failed -> share not determined')


def _bad_spec(root):
    rb = rebuilt(change=lambda f: f[FC].__setitem__(0, (u32(0) + u32(1) + b'\x00' * 40, 0, [MAGIC, 10])))
    write_folder(os.path.join(root, 'state/s17c_r3b/f19'), rb)
    put(root, MAN, manifest_of(rb))


ok &= one('s17c_r3b', _bad_spec, 'K4 comparison self-checks', False, name='a specialization that does not parse into the lookup fields')
ok &= one('s17c_r3b', None, 'K4 comparison self-checks', False, name='live folder of other signature',
          ed3_change=lambda e: write_folder(os.path.join(e, 'state/s17c_n0/f19'), LIVE, sig=R.SIG0))
ok &= one('s17c_r3b', lambda r: shutil.rmtree(os.path.join(r, 'state/s17c_r3b/f19')), 'K4 comparison with the live', None,
          name='rebuilt folder missing')
ok &= one('s17c_r3b', lambda r: edit(r, 'log_s17c_r3b.txt', 'generation=3', 'generation=2'), 'K4 mode line', False, name='generation != replay.cur')
ok &= one('s17c_r3b', lambda r: edit(r, 'log_s17c_r3b.txt', 'compat=ok', 'compat=absent'), 'K4 mode line', False, name='compat absent')
ok &= one('s17c_r3b', lambda r: edit(r, 'log_s17c_r3b.txt', 'GuestOut: hello', 'ShaderReplay: rebuild skipped reason=x\nGuestOut: hello'),
          'K4 a rebuild line', False, name='rebuild skipped line')
ok &= one('s17c_r3b', lambda r: edit(r, 'log_s17c_r3b.txt', 'GuestOut: hello', 'GpuHangAbort: x\nGuestOut: hello'), 'K4 0 death', False,
          name='death marker')
ok &= one('s17c_r3b', lambda r: edit_json(r, 's17c_r3b', lambda d: d['attempts'][0].update(outcome='exited')), 'K4 the process reached',
          False, name='outcome exited')
ok &= one('s17c_r3b', lambda r: edit(r, 'log_s17c_r3b.txt', 'pipelines_bin=written', 'pipelines_bin=stopped'), 'K4 pipelines_bin=written',
          False, name='pipelines_bin=stopped')
ok &= one('s17c_r3b', lambda r: edit(r, 'log_s17c_r3b.txt', 'pending=0', 'pending=1'), 'K4 identity', False, name='identity broken')
ok &= one('s17c_r3b', lambda r: edit(r, 'log_s17c_r3b.txt', 'rej_fused=1', 'rej_fused=0'), 'K4 partition', False, name='partition broken')
ok &= one('s17c_r3b', lambda r: edit(r, 'log_s17c_r3b.txt', 'rej_ref=0', 'rej_ref=1'), 'K4 partition', False, name='rej_ref counted')
ok &= one('s17c_r3b', None, 'K4 share prepared', True, name='share 9 / 10 = 0.90 edge')
ok &= one('s17c_r3b', lambda r: edit(r, 'log_s17c_r3b.txt', 'prepared=9 rejected=1 pending=0 rej_src=0 rej_fused=1',
                                     'prepared=8 rejected=2 pending=0 rej_src=0 rej_fused=2'), 'K4 share prepared', False, name='share 0.80')
ok &= one('s17c_r3b', None, 'K4 share prepared', False, name='pipes_waiting 1 of the edition 3 capture -> 9 / 11',
          ed3_change=lambda e: json.dump(dict(reading='MEMBERS_PASS', members=[], extra=dict(pipes_waiting=1)),
                                         open(os.path.join(e, 'runs/s17c_c2/read.json'), 'w')))
ok &= one('s17c_r3b', None, 'K4 share prepared', None, name='no pipes_waiting -> not determined',
          ed3_change=lambda e: os.remove(os.path.join(e, 'runs/s17c_c2/read.json')))
ok &= one('s17c_rsb', None, 'K4 stand spec: rb_live_mismatch > 0', True, name='baseline stand spec mismatch 1')
ok &= one('s17c_rsb', lambda r: edit(r, 'log_s17c_rsb.txt', 'stand spec applied', 'stand spek applied'), 'K4 stand spec: line', None,
          name='no stand line')
ok &= one('s17c_rsb', lambda r: edit(r, 'log_s17c_rsb.txt', 'permutation=2', 'permutation=7'), 'K4 stand spec: line', None,
          name='stand permutation not in the manifest')


def _stand_same(root):
    rb = rebuilt()
    write_folder(os.path.join(root, 'state/s17c_rsb/f19'), rb)
    put(root, 'state/s17c_rsb/replay/rebuild_manifest.tsv', manifest_of(rb))


ok &= one('s17c_rsb', _stand_same, 'K4 stand spec: rb_live_mismatch > 0', False, name='stand permutation equal -> mismatch 0')
ok &= one('s17c_rsb', lambda r: edit(r, 'log_s17c_rsb.txt', 'GuestOut: hello', 'GuestOut: hello'), 'K4 rb_hit', 'MISSING',
          name='the stand tag has no share member')
ok &= one('s17c_r3h', None, H, True, name='baseline hoover r3h lookup share')
ok &= one('s17c_r3h', lambda r: put(r, 'state/s17c_r3h/replay/rebuild_manifest.tsv', manifest_of(rebuilt(), skip=((FC, 0), (FA, 1)))), H, False,
          name='hoover rb_hit 8 / 10')
ok &= one('s17c_r3h', lambda r: put(r, 'state/s17c_c2h/replay/replay.cur', '2\n'), 'K4 mode line', False,
          name='hoover: generation of the hoover capture (c2h) is the reference')
ok &= one('s17c_r3h', lambda r: write_folder(os.path.join(r, 'state/s17c_n0h/f19'), dict(LIVE, **{FC: LIVE[FC] + [
    (spec_b([(5, 5, 5)], []), 0, [MAGIC, 11]), (spec_b([(6, 6, 6)], []), 0, [MAGIC, 12])]})), H, False,
          name='hoover live folder is s17c_n0h (12 live, 10 hit = 0.83)')
ok &= one('s17c_r3h', lambda r: edit(r, 'log_s17c_c2h.txt', 'pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop',
                                     'pipes_waiting=1 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop'),
          'K4 share prepared', False, name='hoover share uses pipes_waiting of s17c_c2h')

# ------------------------------------------------------------------------------------------------ K6 close path (item 566 (v))
CP = 'K6 the break by the real close path'
KS = 'log_s17c_ks2.txt'


def ks_lines(lines):
    return lambda r: logput(r, 's17c_ks2', log_lines(SKY, entry=False, ft=False, prep=None, before=[MODE3 % (3, 'stop')] + lines))


ok &= one('s17c_ks2', None, CP, True, name='baseline five lines in order')
ok &= one('s17c_ks2', ks_lines([APPLIED, REQ, SEEN, STOPPED, JOINED, 'ShaderReplay: stand stop timeout waited_ms=60000 processed=5 records=10']),
          CP, False, name='a stand stop timeout line -> NO')
for _i, _nm in enumerate(('applied', 'requested', 'seen', 'stopped', 'joined')):
    _ls = [APPLIED, REQ, SEEN, STOPPED, JOINED]
    del _ls[_i]
    ok &= one('s17c_ks2', ks_lines(_ls), CP, None, name='line %s missing -> not determined' % _nm)
ok &= one('s17c_ks2', ks_lines([APPLIED, SEEN, REQ, STOPPED, JOINED]), CP, None, name='seen before close requested -> not determined')
ok &= one('s17c_ks2', ks_lines([REQ, APPLIED, SEEN, STOPPED, JOINED]), CP, None, name='requested before applied -> not determined')
ok &= one('s17c_ks2', ks_lines([APPLIED, REQ, STOPPED, SEEN, JOINED]), CP, None, name='stopped before seen -> not determined')
ok &= one('s17c_ks2', ks_lines([APPLIED, REQ, SEEN, JOINED, STOPPED]), CP, None, name='joined before stopped -> not determined')
ok &= one('s17c_ks2', ks_lines([APPLIED, REQ, SEEN.replace('processed=5', 'processed=6'), STOPPED, JOINED]), CP, None, name='P differs')
ok &= one('s17c_ks2', ks_lines([APPLIED, REQ, SEEN.replace('records=10', 'records=11'), STOPPED, JOINED]), CP, None, name='R differs')
ok &= one('s17c_ks2', ks_lines([APPLIED.replace('processed=5', 'processed=10'), REQ, SEEN.replace('processed=5', 'processed=10'), STOPPED,
                                JOINED]), CP, None, name='P = R -> not determined')
ok &= one('s17c_ks2', ks_lines([APPLIED.replace('processed=5', 'processed=11'), REQ, SEEN.replace('processed=5', 'processed=11'), STOPPED,
                                JOINED]), CP, None, name='P > R -> not determined')
ok &= one('s17c_ks2', ks_lines([APPLIED.replace('processed=5', 'processed=9'), REQ, SEEN.replace('processed=5', 'processed=9'), STOPPED,
                                JOINED]), CP, True, name='P = R - 1 -> YES')
ok &= one('s17c_ks2', ks_lines([APPLIED, REQ.replace('precache_active=1', 'precache_active=0'), SEEN, STOPPED, JOINED]), CP, None,
          name='precache_active=0')
ok &= one('s17c_ks2', ks_lines([APPLIED, REQ, SEEN, STOPPED, JOINED, 'Event: quit']), CP, None, name='one Event: quit line')
ok &= one('s17c_ks2', lambda r: edit_json(r, 's17c_ks2', lambda d: d['attempts'][0].update(detail='exit code 1')), CP, None, name='exit code 1')
ok &= one('s17c_ks2', lambda r: edit_json(r, 's17c_ks2', lambda d: d['attempts'][0].update(outcome='prep', detail=None)), CP, None,
          name='the harness closed it (outcome prep, no exit code)')
ok &= one('s17c_ks2', ks_lines([APPLIED, REQ, SEEN, STOPPED.replace('pipelines_bin=stopped', 'pipelines_bin=written'), JOINED]), CP, None,
          name='rebuild written instead of stopped -> not determined')
ok &= one('s17c_ks2', ks_lines([APPLIED, REQ, SEEN, STOPPED.replace('pipelines_bin=stopped', 'pipelines_bin=written'), JOINED]),
          'K6 sign of the break', False, name='no stopped line -> sign NO')
ok &= one('s17c_ks2', ks_lines([STOPPED, APPLIED, REQ, SEEN, JOINED]), 'K6 sign of the break', False, name='stopped before the stand -> NO')
ok &= one('s17c_ks2', ks_lines([REQ, SEEN, STOPPED, JOINED]), 'K6 sign of the break', None, name='no stand line -> not determined')
ok &= one('s17c_ks2', lambda r: edit(r, 'runs/s17c_ks2/state_out.txt', 'pipelines_bin absent', 'pipelines_bin 4 aa'), 'K6 pipelines.bin', False,
          name='pipelines.bin written at the break')
ok &= one('s17c_ks2', lambda r: os.remove(os.path.join(r, 'runs/s17c_ks2/state_out.txt')), 'K6 pipelines.bin', None, name='no state_out')
ok &= one('s17c_ks2', lambda r: put(r, 'stdout_s17c_ks2.txt', 'KytyPS5 git = c0057cc, x\n--- Fatal Error ---\n'), 'K6 0 death', False,
          name='death marker in stdout')
ok &= check(R.exit_code(dict(outcome='exited', detail='exit code 0')) == 0 and R.exit_code(dict(outcome='ok', detail='exit code 0')) is None
            and R.exit_code(dict(outcome='exited', detail='exit code -3')) == -3 and R.exit_code(dict(outcome='exited', detail='x')) is None,
            'exit_code: only an exited process with the detail exit code <n>')

# ------------------------------------------------------------------------------------------------ K6 remainder (items 565 (g), 566 (g))
RM = 'K6 the next start rebuilds the remainder'
KN = 'log_s17c_kn2.txt'
ok &= check('3 / 5 / 8' in rowdet(WB['s17c_kn2'], 'a / b / N'), 'baseline a 3 b 5 N 8')
ok &= one('s17c_kn2', None, RM, True, name='baseline a + b = N')
ok &= one('s17c_kn2', ks_lines([APPLIED, REQ, SEEN, STOPPED.replace('perms_new=3', 'perms_new=0'), JOINED]), RM, False, name='a = 0')
ok &= one('s17c_kn2', lambda r: (ks_lines([APPLIED, REQ, SEEN, STOPPED.replace('perms_new=3', 'perms_new=0'), JOINED])(r),
                                 edit(r, KN, 'perms_new=5', 'perms_new=8')), RM, False, name='a = 0 and b = N')
ok &= one('s17c_kn2', lambda r: (ks_lines([APPLIED, REQ, SEEN, STOPPED.replace('perms_new=3', 'perms_new=8'), JOINED])(r),
                                 edit(r, KN, 'perms_new=5', 'perms_new=0')), RM, False, name='b = 0 and a = N')
ok &= one('s17c_kn2', lambda r: edit(r, KN, 'perms_new=5', 'perms_new=4'), RM, False, name='a + b = N - 1')
ok &= one('s17c_kn2', lambda r: edit(r, KN, 'perms_new=5', 'perms_new=6'), RM, False, name='a + b = N + 1')
ok &= one('s17c_kn2', lambda r: (ks_lines([APPLIED, REQ, SEEN, STOPPED.replace('perms_new=3', 'perms_new=1'), JOINED])(r),
                                 edit(r, KN, 'perms_new=5', 'perms_new=7')), RM, True, name='a = 1, b = N - 1 -> YES')
ok &= one('s17c_kn2', lambda r: edit(r, KN, 'records=10', 'records=11'), RM, None, name='records of kn2 differ')
ok &= one('s17c_kn2', ks_lines([APPLIED, REQ, SEEN, STOPPED.replace('records=10', 'records=9'), JOINED]), RM, None, name='records of ks2 differ')
ok &= one('s17c_kn2', lambda r: edit(r, 'log_s17c_r3b.txt', 'records=10', 'records=12'), RM, None, name='records of r3b differ')
ok &= one('s17c_kn2', ks_lines([APPLIED, REQ, SEEN, STOPPED, JOINED, 'ShaderReplay: stand stop timeout waited_ms=60000 processed=5 records=10']),
          RM, False, name='a timeout line at ks2 -> NO')
ok &= one('s17c_kn2', ks_lines([APPLIED, REQ, STOPPED, JOINED]), RM, None, name='no stand stop seen at ks2')
ok &= one('s17c_kn2', ks_lines([APPLIED, REQ, SEEN, JOINED]), RM, None, name='no stopped rebuild line at ks2')
ok &= one('s17c_kn2', lambda r: edit(r, KN, 'GuestOut: hello', 'ShaderReplay: rebuild skipped reason=recipes_current\nGuestOut: hello'), RM,
          False, name='kn2 with a skipped line')
ok &= one('s17c_kn2', lambda r: edit(r, KN, 'pipelines_bin=written', 'pipelines_bin=stopped'), RM, False, name='kn2 not written')
ok &= one('s17c_kn2', lambda r: edit(r, KN, 'ShaderReplay: rebuild records', 'ShaderReplay: rebuildx records'), RM, False, name='kn2 no rebuild line')
ok &= one('s17c_kn2', lambda r: edit(r, 'log_s17c_r3b.txt', 'perms_new=8', 'perms_new=x'), RM, None, name='no N')
ok &= one('s17c_kn2', lambda r: put(r, 'runs/s17c_kn2/mf_in.tsv', 'f19\t<MISSING>\t0\t-\nreplay\treplay.cur\t2\taa\n'), RM, None,
          name='caches returned between ks2 and kn2 (manifest after ks2 != before kn2)')
ok &= one('s17c_kn2', lambda r: put(r, 'runs/s17c_ks2/mf_in.tsv', 'f19\tx.bin\t1\tcc\nreplay\treplay.cur\t2\taa\n'), RM, None,
          name='manifest before ks2 != before r3b')
ok &= one('s17c_kn2', lambda r: os.remove(os.path.join(r, 'runs/s17c_r3b/mf_in.tsv')), RM, None, name='manifest before r3b missing')
ok &= one('s17c_kn2', lambda r: os.remove(os.path.join(r, 'runs/s17c_ks2/mf_out.tsv')), RM, None, name='manifest after ks2 missing')
ok &= one('s17c_kn2', setenv('s17c_r3b', 'KYTY_S_REPLAY', '1'), RM, None, name='KYTY_S_REPLAY differs at r3b')
ok &= one('s17c_kn2', setenv('s17c_ks2', 'KYTY_SHADER_SEED', None), RM, None, name='KYTY_SHADER_SEED absent at ks2')
ok &= one('s17c_kn2', setenv('s17c_r3b', 'KYTY_SHADER_SEED', '1'), RM, None, name='KYTY_SHADER_SEED=1 at r3b')
ok &= one('s17c_kn2', lambda r: os.remove(os.path.join(r, 's17c_ks2.json')), RM, None, name='ks2 run record missing')
ok &= check(R.remainder(dict(timeout=1, seen=False, a=None, records=None), dict(), dict(), dict()) == (False, R.remainder(
    dict(timeout=1, seen=False, a=None, records=None), dict(), dict(), dict())[1]), 'remainder: a timeout wins over everything')
ok &= one('s17c_kn2', lambda r: edit(r, KN, 'compat=ok', 'compat=absent'), 'K6 mode line', False, name='kn2 mode compat absent')
ok &= one('s17c_kn2', lambda r: edit(r, KN, 'GuestOut: Level has started', 'GuestOut: Level has startedx'), 'K6 entered', False, name='kn2 not entered')
ok &= one('s17c_kn2', lambda r: edit_json(r, 's17c_kn2', lambda d: d['attempts'][0].update(hold_s=59.0)), 'K6 the process lived', False,
          name='kn2 hold 59 s')
ok &= one('s17c_kn2', lambda r: edit(r, KN, 'GuestOut: hello', 'Unhandled exception: x\nGuestOut: hello'), 'K6 0 death', False, name='kn2 death')
ok &= one('s17c_kn2', lambda r: edit(r, KN, 'perms_cached=4', 'perms_cached=0'), RM, True, name='perms_cached 0 is only a reference')

# ------------------------------------------------------------------------------------------------ K3 on hoover_beach (s17c_c2h)
C2 = 'log_s17c_c2h.txt'
ok &= one('s17c_c2h', lambda r: edit(r, C2, 'compat=absent', 'compat=ok'), 'K3 mode line', False, name='compat ok')
ok &= one('s17c_c2h', lambda r: edit(r, C2, 'variant_fixb26_fixb1b_fixf10' + chr(10), 'variant_fixb26_fixb1b_fixf10_fixf19' + chr(10)),
          'K3 translation cache directory', False, name='directory of F19=1')
ok &= one('s17c_c2h', lambda r: edit(r, C2, 'canon_mismatch=0 dropped_queue=0 bytes=100 gen=3 canon_self=0 canon_residual=0 canon_base=0 '
                                     'canon_big=0 pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop',
                                     'canon_mismatch=1 dropped_queue=0 bytes=100 gen=3 canon_self=1 canon_residual=0 canon_base=0 '
                                     'canon_big=0 pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop'),
          'K3 canon_mismatch', False, name='canon_mismatch 1')
ok &= one('s17c_c2h', lambda r: edit(r, C2, 'canon_base=0 canon_big=0 pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop',
                                     'canon_base=1 canon_big=0 pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop'),
          'K3 canon_base', False, name='canon_base 1')
ok &= one('s17c_c2h', lambda r: edit(r, C2, 'dropped_queue=0 bytes=100 gen=3 canon_self=0 canon_residual=0 canon_base=0 canon_big=0 pipes_waiting=0 '
                                     'catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop',
                                     'dropped_queue=2 bytes=100 gen=3 canon_self=0 canon_residual=0 canon_base=0 canon_big=0 pipes_waiting=0 '
                                     'catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop'), 'K3 dropped_queue', False,
          name='dropped_queue 2 at a soft close')
ok &= one('s17c_c2h', lambda r: edit_json(r, 's17c_c2h', lambda d: d['attempts'][0].update(close_killed=True)), 'K3 dropped_queue', None,
          name='hard close -> not determined')
ok &= one('s17c_c2h', lambda r: edit(r, C2, 'capture sources=5 specs=6 pipes=10 canon_mismatch=0 dropped_queue=0 bytes=100 gen=3 canon_self=0 '
                                     'canon_residual=0 canon_base=0 canon_big=0 pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 '
                                     'catalogue_pipes=10 at=stop', 'capture sources=0 specs=6 pipes=10 canon_mismatch=0 dropped_queue=0 '
                                     'bytes=100 gen=3 canon_self=0 canon_residual=0 canon_base=0 canon_big=0 pipes_waiting=0 catalogue_sources=5 '
                                     'catalogue_specs=6 catalogue_pipes=10 at=stop'), 'K3 sources > 0', False, name='sources 0')
ok &= one('s17c_c2h', lambda r: edit(r, C2, 'specs=6 pipes=10 canon_mismatch=0 dropped_queue=0 bytes=100 gen=3 canon_self=0 canon_residual=0 '
                                     'canon_base=0 canon_big=0 pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop',
                                     'specs=0 pipes=10 canon_mismatch=0 dropped_queue=0 bytes=100 gen=3 canon_self=0 canon_residual=0 '
                                     'canon_base=0 canon_big=0 pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop'),
          'K3 specs > 0', False, name='specs 0')
ok &= one('s17c_c2h', lambda r: put(r, 'state/s17c_c2h/replay/replay.cur', '2\n'), 'K3 generation file', False, name='replay.cur != gen')
ok &= one('s17c_c2h', lambda r: write_replay(os.path.join(r, 'state/s17c_c2h/replay'), 3, RAW), 'K3 offline R_ADDR = 0', False, name='R_ADDR > 0')
ok &= one('s17c_c2h', lambda r: edit(r, C2, 'at=stop', 'at=save'), 'K3 canon_mismatch', None, name='no at=stop line -> not determined')
ok &= one('s17c_c2h', lambda r: edit(r, C2, 'dt_us=75000000', 'dt_us=74999999'), 'K3 shown hold', False, name='hold 299.999996 s')
ok &= one('s17c_c2h', lambda r: edit_json(r, 's17c_c2h', lambda d: d['attempts'][0].update(hold_s=329.0)), 'K3 the process lived', False,
          name='hold_s 329')
ok &= one('s17c_c2h', lambda r: edit(r, C2, 'Level has started: hoover_beach', 'Level has started: ' + SKY), 'K3 entered', False,
          name='entry of the other level')

# ------------------------------------------------------------------------------------------------ K4/K5 control s17c_n0h
ok &= one('s17c_n0h', lambda r: edit(r, 'log_s17c_n0h.txt', 'hash=0x%016x' % SRC_HASHES[0], 'hash=0x%016x' % 0xCCCC), 'K5 null control', False,
          name='no catalogue program translated after the preparation line')
ok &= one('s17c_n0h', lambda r: edit(r, 'log_s17c_n0h.txt', 'ShaderPreparation: startup wait finished', 'ShaderPreparation: x'),
          'K5 null control', None, name='no preparation line')
ok &= one('s17c_n0h', lambda r: shutil.rmtree(os.path.join(r, 'state/s17c_c2h/replay')), 'K5 null control', None, name='no hoover catalogue')
ok &= one('s17c_n0h', lambda r: shutil.rmtree(os.path.join(r, 'state/s17c_n0h/f19')), 'K4 live folder', False, name='live folder missing')
ok &= one('s17c_n0h', lambda r: open(os.path.join(r, 'state/s17c_n0h/f19', FA), 'ab').write(b'x'), 'K4 live folder', False,
          name='live file unreadable')
ok &= one('s17c_n0h', lambda r: edit(r, 'log_s17c_n0h.txt', 'fixf10_fixf19', 'fixf10'), 'K4 translation cache directory', False,
          name='directory F19=0')

# ------------------------------------------------------------------------------------------------ K5 entry s17c_e3h
E3 = 'log_s17c_e3h.txt'
ok &= one('s17c_e3h', lambda r: edit(r, E3, 'rebuild skipped reason=recipes_current', 'rebuild skipped reason=other'), 'K5 fitness', False,
          name='skipped for another reason')
ok &= one('s17c_e3h', lambda r: edit(r, E3, 'GuestOut: hello', rb_line() + '\nGuestOut: hello'), 'K5 fitness', False, name='a rebuild line')
ok &= one('s17c_e3h', lambda r: edit(r, E3, 'hash=0x%016x' % 0xBBBB, 'hash=0x%016x' % SRC_HASHES[1]), 'K5 translations of catalogue', False,
          name='one catalogue program translated in the game')
ok &= one('s17c_e3h', lambda r: edit(r, 'log_s17c_r3h.txt', 'hash=0x%016x' % 0xBBBB, 'hash=0x%016x' % SRC_HASHES[1]),
          'K5 translations of catalogue', None, name='r3h translated a catalogue program after its preparation -> not determined')
ok &= one('s17c_e3h', lambda r: edit(r, 'log_s17c_n0h.txt', 'hash=0x%016x' % SRC_HASHES[0], 'hash=0x%016x' % 0xCCCC), 'K5 null control', False,
          name='null control of n0h 0')
ok &= one('s17c_e3h', lambda r: edit(r, E3, 'finished in 20000 ms', 'finished in 180000 ms'), 'K5 preparation screen', True, name='180 000 ms edge')
ok &= one('s17c_e3h', lambda r: edit(r, E3, 'finished in 20000 ms', 'finished in 180001 ms'), 'K5 preparation screen', False, name='180 001 ms')
ok &= one('s17c_e3h', lambda r: edit(r, E3, 'ShaderPreparation: startup wait finished', 'ShaderPreparation: x'), 'K5 preparation screen', None,
          name='no preparation line')
ok &= one('s17c_e3h', lambda r: put(r, 'rec_s17c_e3h.mp4.idx', 'f\n' * 2999), 'K5 video index', False, name='2 999 records')
ok &= one('s17c_e3h', lambda r: os.remove(os.path.join(r, 'rec_s17c_e3h.mp4.idx')), 'K5 video index', None, name='no index')
ok &= one('s17c_e3h', lambda r: put(r, 'runs/s17c_e3h/glitch.txt', 'one-frame glitches: 1\n'), 'K5 0 one-frame', False, name='one glitch')
ok &= one('s17c_e3h', lambda r: put(r, 'runs/s17c_e3h/sheet.txt', 'error\n'), 'K5 sheet', False, name='no sheet line')
ok &= one('s17c_e3h', lambda r: os.remove(os.path.join(r, 'runs/s17c_e3h/sheet.txt')), 'K5 sheet', None, name='sheet not made')
ok &= one('s17c_e3h', lambda r: edit(r, E3, 'GuestOut: hello', 'ErrorDeviceLost\nGuestOut: hello'), 'K5 0 death', False, name='death marker')
ok &= one('s17c_e3h', lambda r: edit(r, E3, 'dt_us=75000000', 'dt_us=74999999'), 'K5 shown hold', False, name='hold below 300 s')
ok &= one('s17c_e3h', lambda r: edit(r, E3, 'Level has started: hoover_beach', 'Level has started: ' + SKY), 'K5 entered', False,
          name='entry of the other level')

# ------------------------------------------------------------------------------------------------ table and output (cp1250 strict, in process)


def run_main(args):
    buf = io.BytesIO()
    w = io.TextIOWrapper(buf, encoding='cp1250', errors='strict', newline='\n')
    use(B0, ED3B)
    try:
        with contextlib.redirect_stdout(w):
            rc = R.main(args)
        w.flush()
        return rc, buf.getvalue().decode('cp1250')
    except UnicodeEncodeError:
        return 'UnicodeEncodeError', ''


_rc, _o = run_main(['--table'])
ok &= check(_rc == 0 and 'carried without a repeat' in _o and 's17c_kc   K6     READING MEMBERS_PASS' in _o and
            's17c_e3h  K5     READING MEMBERS_PASS' in _o and 's17c_r3   ' not in _o, 'table: carried edition 3 tags and the 8 edition 4 tags')
_rc, _o = run_main(['s17c_kn2'])
ok &= check(_rc == 0 and 'READING MEMBERS_PASS' in _o and 'a / b / N: 3 / 5 / 8' in _o, 'main s17c_kn2 in strict cp1250')
_rc, _o = run_main(['s17c_ks2'])
ok &= check(_rc == 0 and 'READING MEMBERS_PASS' in _o, 'main s17c_ks2 in strict cp1250')
_rc, _o = run_main(['--k4x', os.path.join(ED3B, 'state/s17c_n0/f19'), os.path.join(B0, 'state/s17c_r3b/f19'),
                    os.path.join(B0, MAN)])
ok &= check(_rc == 0 and 'lookup rb_hit 10' in _o and 'raw rb_hit 9' in _o, '--k4x prints both keys')
ok &= check(all(b < 128 for b in open(SRC, 'rb').read()), 'ASCII only: s17c2_read.py')
print('checks %d' % N[0])
if ok:
    print('ALL OK')
sys.exit(0 if ok else 1)
