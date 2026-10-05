"""S17c (HPP-613): fixtures of the S17c reader s17c_read.py, the translation cache reader tc_s17c.py, the state description
state_s17c.py and the copy of r_addr.py.  A synthetic root with all 13 tags made (logs, run records, state folders, caches, catalogue,
manifest) reads MEMBERS_PASS everywhere; then one change per admission row, form row and member (and every edge: 0.90 share, 0.90
rb_hit, 180 s, 3 000 records, 300 s) gives the named word.  The first line names the suite and the targets with sha256; the last line is
ALL OK.  ASCII only.
usage: python test_s17c_read.py"""
import hashlib
import json
import os
import shutil
import struct
import subprocess
import sys
import tempfile

import xxhash

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import r_addr  # noqa: E402
import s17c_read as R  # noqa: E402
import state_s17c  # noqa: E402
import tc_s17c  # noqa: E402


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


print('suite test_s17c_read.py sha256 %s target s17c_read.py sha256 %s tc_s17c.py sha256 %s state_s17c.py sha256 %s r_addr.py sha256 %s'
      % (sha(os.path.join(HERE, 'test_s17c_read.py')), sha(os.path.join(HERE, 's17c_read.py')), sha(os.path.join(HERE, 'tc_s17c.py')),
         sha(os.path.join(HERE, 'state_s17c.py')), sha(os.path.join(HERE, 'r_addr.py'))))
OK = [True]
N = [0]


def check(cond, name):
    N[0] += 1
    print(('ok   ' if cond else 'FAIL ') + name)
    if not cond:
        OK[0] = False


# ------------------------------------------------------------------------------------------------ builders: translation cache

MAGIC = 0x07230203


def u32(v):
    return struct.pack('<I', v)


def shader_info_empty(with_extra=False):
    b = u32(0)                                    # buffers
    if with_extra:
        b = u32(1) + b'\x01' * R.tc_s17c.SZ_BUFFER_RES
    img = b''
    if with_extra:
        img = u32(1) + u32(0) * 9 + b'\x00' * 7 + u32(0) * 4 + u32(2) + u32(5) + u32(6)
    else:
        img = u32(0)
    b += img
    b += u32(0) + u32(0)                          # samplers, pairs
    if with_extra:
        b += u32(1) + u32(1) + u32(2) + u32(3) + u32(3) + b'pos' + b'\x01'   # one input
        b += u32(1) + u32(1) + u32(0) + u32(0) + u32(2) + b'o0'              # one output
    else:
        b += u32(0) + u32(0)
    b += b'\x00' * 32 + struct.pack('<ii', -1, -1) + b'\x00\x00'
    return b


def plan_bytes(with_extra=False):
    b = u32(0) + struct.pack('<Q', 0x1234) + u32(0) + u32(4)
    if with_extra:
        b += u32(1) + u32(7) + struct.pack('<Q', 0) + u32(1) + u32(3) + struct.pack('<Q', 9)   # one instruction with one value
        b += u32(1) + b'\x00' * R.tc_s17c.SZ_MEMORY_INFO
        b += u32(1) + u32(4) + (u32(3) + struct.pack('<Q', 1)) * 8 + b'\x01' + b'\x00' * R.tc_s17c.SZ_INDIRECT
        b += u32(2) + u32(1) + u32(2)
        b += u32(1) + u32(3) + struct.pack('<Q', 1) + u32(4) + b'\x00'
        b += u32(3) + b'\x01\x02\x03'
    else:
        b += u32(0) + u32(0) + u32(0) + u32(0) + u32(0) + u32(0)
    b += b'\x01\x01\x01'
    if with_extra:
        b += u32(1) + u32(3) + struct.pack('<Q', 0) + u32(1) + u32(2) + u32(1) + u32(0)
    else:
        b += u32(0)
    b += b'\x00' * R.tc_s17c.SZ_UNIFORM_FILL + (u32(3) + struct.pack('<Q', 0)) * 4
    b += shader_info_empty(with_extra)
    return b


def spec_bytes(buffers, images):
    b = u32(len(buffers))
    for x in buffers:
        b += struct.pack('<III', *x)
    b += u32(len(images))
    for x in images:
        b += struct.pack('<I', x) + b'\x00' * (R.tc_s17c.SZ_SPEC_IMAGE - 4)
    return b


def cache_bytes(sig, perms, phash=0xA1, with_extra=False, trailing=b'', bad_magic=False):
    pay = u32(0) + struct.pack('<Q', phash) + u32(4) + u32(16) + u32(2) + u32(1) + u32(2)
    pay += plan_bytes(with_extra)
    pay += u32(len(perms))
    for (bufs, imgs, start, words) in perms:
        pay += spec_bytes(bufs, imgs)
        pay += u32(0) + struct.pack('<Q', phash) + u32(64) + u32(0) + u32(4) + u32(0) + u32(0)
        pay += shader_info_empty(with_extra)
        pay += u32(start) + u32(0) + u32(0) + u32(0) + u32(0)
        w = list(words)
        if bad_magic:
            w[0] = 0x1234
        pay += u32(len(w)) + b''.join(u32(x) for x in w)
    pay += trailing
    return (sig + '\n').encode() + struct.pack('<Q', xxhash.xxh3_64_intdigest(pay)) + pay


def spirv_xxh(words):
    return xxhash.xxh3_64_intdigest(b''.join(u32(x) for x in words))


FA = 'vs_00000000000000a1_0000000000000001.bin'
FB = 'ps_00000000000000b1_0000000000000002.bin'
FC = 'cs_00000000000000c1_0000000000000003.bin'
PA0 = ([(1, 2, 3)], [], 0, [MAGIC, 1, 2])
PA1 = ([(4, 5, 6)], [], 4, [MAGIC, 3])
PB0 = ([], [7], 8, [MAGIC, 5])
PC0 = ([(9, 9, 9)], [], 0, [MAGIC, 8])


def write_folder(d, files, sig=R.SIG1):
    shutil.rmtree(d, ignore_errors=True)   # the folder is exactly these files
    os.makedirs(d)
    for name, perms in files.items():
        open(os.path.join(d, name), 'wb').write(cache_bytes(sig, perms, phash=int(name[3:19], 16)))
    open(os.path.join(d, 'pipelines.bin'), 'wb').write(b'KRCP')


def manifest_text(rows, sig=R.SIG1, glued=False, crlf=False):
    nl = '\r\n' if crlf else '\n'
    lines = ['%s\t%d\t%016x\t%d\t%016x' % (f, i, 0x55, start, spirv_xxh(words)) for (f, i, start, words) in rows]
    if glued:
        return '# ShaderReplay rebuild manifest; signature ' + sig + nl.join(lines) + nl
    return '# ShaderReplay rebuild manifest; signature ' + sig + nl + nl + nl.join(lines) + nl


# ------------------------------------------------------------------------------------------------ builders: catalogue

L = r_addr.LAYOUT
SRC_HASHES = (0xAAAA000000000001, 0xAAAA000000000002)


def catalogue_bytes(gen, words, src_hashes=SRC_HASHES, spec_id=0x16, compat=b'KytyReplay1:PPSA21564:01.000:key1:canon1:input1:pod1.2.3'):
    body = b''
    for k, h in enumerate(src_hashes):
        src = bytearray(L['src'])
        struct.pack_into('<Q', src, L['src.src_id'], 100 + k)
        struct.pack_into('<Q', src, L['src.hash'], h)
        struct.pack_into('<I', src, L['src.static_words'], 1)
        struct.pack_into('<I', src, L['src.code_words'], 2)
        body += bytes(src) + struct.pack('<3I', 1, 2, 3)
    spec = bytearray(L['spec'])
    struct.pack_into('<Q', spec, L['spec.spec_id'], spec_id)
    struct.pack_into('<I', spec, L['spec.words'], len(words))
    body += bytes(spec)
    for value, role in words:
        w = bytearray(L['word'])
        struct.pack_into('<I', w, L['word.value'], value)
        w[L['word.role']] = role
        body += bytes(w)
    pipe = bytearray(L['pipe'])
    body += bytes(pipe)
    head = bytearray(L['file'])
    head[0:8] = r_addr.MAGIC
    struct.pack_into('<I', head, L['file.format'], 1)
    struct.pack_into('<I', head, L['file.compat_size'], len(compat))
    bh = bytearray(L['body'])
    struct.pack_into('<QQIII', bh, 0, gen, xxhash.xxh3_64_intdigest(body), len(src_hashes), 1, 1)
    return bytes(head) + compat + bytes(bh) + body


CANON = [(0x100, 2), (0, 3), (7, 0), (0x20000, 0), (1, 6), (0, 9)]
RAW = [(0x12345678, 2), (2, 3), (7, 0), (0x20000, 0), (0x40000, 6), (0x1234, 9)]


def write_replay(d, gen, words, manifest=None):
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'replay.cur'), 'wb').write(b'%d\n' % gen)
    open(os.path.join(d, 'replay.%d.bin' % gen), 'wb').write(catalogue_bytes(gen, words))
    open(os.path.join(d, 'replay.%d.bin' % (gen - 1)), 'wb').write(catalogue_bytes(gen - 1, words))
    if manifest is not None:
        open(os.path.join(d, 'rebuild_manifest.tsv'), 'wb').write(manifest.encode())


# ------------------------------------------------------------------------------------------------ builders: one tag

SEAL_TEXT = b'seal of the fixtures\n'


def env_for(tag):
    spec = R.SPEC[tag]
    e = dict(R.BASE_ENV)
    e.update(spec['env'])
    e['KYTY_GATE_FILE'] = 'C:/x/gates.req'
    e['KYTY_SAMPLE_GATE'] = 'C:/x/sample.req'
    if spec['form'] == 'v':
        e['KYTY_REC'] = 'C:/x/rec_%s.mp4' % tag
    if spec['form'] == 'w':
        e['VK_LAYER_PATH'] = 'C:/VulkanSDK/1.4.357.0/Bin'
        e['VK_LAYER_DUPLICATE_MESSAGE_LIMIT'] = R.LIMIT
    e['VK_SDK_PATH'] = 'C:/VulkanSDK'
    return e


def base_log(tag, extra_before_guest=(), extra=(), entry=True, ft=True, dirname=R.DIR1, prep=12000, av_after=()):
    L1 = ['Fork build arigandores/KytyPS5 a2fee0d, test',
          'Shader translation cache: _ShaderCache' + chr(92) + 'PPSA21564' + chr(92) + dirname]
    L1 += list(extra_before_guest)
    if prep is not None:
        L1.append('ShaderPreparation: startup wait finished in %d ms presents_other=0 presents_main=0' % prep)
    L1 += list(av_after)
    L1.append('GuestOut: hello')
    if entry:
        L1.append('GuestOut: Level has started: ' + R.SKY)
    if ft:
        L1.append('FrameTrace: n=10 dt_us=16000 draws=500')
        L1 += ['FrameTrace: n=%d dt_us=75000000 draws=500' % (11 + k) for k in range(4)]
    L1 += list(extra)
    return L1


def att_for(tag, outcome=None):
    spec = R.SPEC[tag]
    o = outcome or ('prep' if spec['form'] == 'p' else 'ok')
    a = dict(label='attempt 1', outcome=o, hold_exit=None, hold_s=float(spec['hold']), close_rc=0, close_killed=False, close_s=2.0)
    if tag == 's17c_ks':
        a.update(outcome='exited', close_rc=None, close_killed=None)
    return a


def state_text(f10=None, f19=None, replay_dir=None):
    out = []
    out.append('dir f10 absent' if f10 is None else 'dir f10 present files 3 cache_files 2 pipelines_bin %s' % f10)
    out.append('dir f19 absent' if f19 is None else 'dir f19 present files 4 cache_files 3 pipelines_bin %s' % f19)
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


CAP = 'ShaderReplay: capture sources=5 specs=6 pipes=10 canon_mismatch=0 dropped_queue=0 bytes=100 gen=3 canon_self=0 canon_residual=0 ' \
      'canon_base=0 canon_big=0 pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=%s'
RB = 'ShaderReplay: rebuild records=10 prepared=9 rejected=1 pending=0 rej_src=0 rej_fused=1 rej_key=0 rej_version=0 rej_shape=0 ' \
     'rej_translate=0 rej_emit=0 rej_val=0 rej_write=0 rej_ref=0 translate_ms=10 wall_ms=20 perms_new=3 perms_cached=%d rb_push_moved=0 ' \
     'rb_spec_changed=0 groups_same_pc=1 group_sources=3 pipelines_bin=%s'
MODE2 = 'ShaderReplay: mode=2 dir=_ShaderCache\\PPSA21564\\replay compat=absent generation=0 corrupt=0 sources=0 specs=0 pipes=0 test=%s'
MODE3 = 'ShaderReplay: mode=3 dir=_ShaderCache\\PPSA21564\\replay compat=ok generation=%d corrupt=%d sources=5 specs=6 pipes=10 test=%s'
PNO = 'PipelinePrecache: no _ShaderCache\\PPSA21564\\variant_fixb26_fixb1b_fixf10\\pipelines.bin yet'
AVL = 'AvTrace: shader ShaderRecompiler VS hash=0x%016x translate_us=5 compile_us=6 permutations=1'


def make_root(root):
    """The baseline: every tag made and read MEMBERS_PASS."""
    os.makedirs(os.path.join(root, 'runs'), exist_ok=True)
    seal = os.path.join(root, 'seal.md')
    open(seal, 'wb').write(SEAL_TEXT)
    binp = os.path.join(root, 'bin.exe')
    open(binp, 'wb').write(b'MZ...' + R.VERSION + b'...')
    st = os.path.join(root, 'state')
    write_replay(os.path.join(st, 's17c_c2', 'replay'), 3, CANON)
    write_folder(os.path.join(st, 's17c_c2', 'f10'), {FA: [PA0]}, sig=R.SIG0)
    write_replay(os.path.join(st, 's17c_ca', 'replay'), 3, RAW)
    write_replay(os.path.join(st, 's17c_cc', 'replay'), 3, CANON)
    write_folder(os.path.join(st, 's17c_n0', 'f19'), {FA: [PA0, PA1], FB: [PB0]})
    man = manifest_text([(FA, 0, PA1[2], PA1[3]), (FA, 1, PA0[2], PA0[3]), (FB, 0, PB0[2], PB0[3]), (FC, 0, PC0[2], PC0[3])])
    write_folder(os.path.join(st, 's17c_r3', 'f19'), {FA: [PA1, PA0], FB: [PB0], FC: [PC0]})
    write_replay(os.path.join(st, 's17c_r3', 'replay'), 3, CANON, manifest=man)
    PB0x = (PB0[0], PB0[1], PB0[2], [MAGIC, 6])
    man_s = manifest_text([(FA, 0, PA1[2], PA1[3]), (FA, 1, PA0[2], PA0[3]), (FB, 0, PB0x[2], PB0x[3])])
    write_folder(os.path.join(st, 's17c_rs', 'f19'), {FA: [PA1, PA0], FB: [PB0x]})
    write_replay(os.path.join(st, 's17c_rs', 'replay'), 3, CANON, manifest=man_s)
    os.makedirs(os.path.join(st, 's17c_ks', 'f19'))
    write_replay(os.path.join(st, 's17c_ks', 'replay'), 3, CANON)
    c2rp = os.path.join(st, 's17c_c2', 'replay')
    logs = {
        's17c_v0': base_log('s17c_v0'),
        's17c_w0': base_log('s17c_w0', extra_before_guest=['DualSrcBlend: supported=1 enabled=1', '[Vulkan][W] warning']),
        's17c_c2': base_log('s17c_c2', dirname=R.DIR0, extra_before_guest=[MODE2 % 'none', PNO],
                            extra=[CAP % 'save', CAP % 'stop']),
        's17c_ca': base_log('s17c_ca', dirname=R.DIR0, ft=False, extra_before_guest=[MODE2 % 'addr', PNO],
                            extra=['ShaderReplay: stand addr applied spec=0x0000000000000016', CAP % 'stop']),
        's17c_cc': base_log('s17c_cc', dirname=R.DIR0, ft=False, extra_before_guest=[MODE2 % 'canon', PNO],
                            extra=['ShaderReplay: stand canon applied hash=0x00000000000000ab rejected=0',
                                   'ShaderReplay: stand canon applied hash=0x00000000000000ab rejected=1',
                                   'ShaderReplay: capture reject why=self ok=1 complete=1 culprit=5:role6:12345678->00000000 '
                                   'hash=0x00000000000000ab words=9',
                                   (CAP % 'stop').replace('canon_mismatch=0', 'canon_mismatch=1').replace('canon_self=0', 'canon_self=1')]),
        's17c_n0': base_log('s17c_n0', av_after=[AVL % SRC_HASHES[0], AVL % 0xBBBB]),
        's17c_r3': base_log('s17c_r3', entry=False, ft=False, extra_before_guest=[MODE3 % (3, 0, 'none'), RB % (0, 'written'),
                                                                                  'ShaderReplay: hits rb_used=0 rb_marked=0'],
                            av_after=[AVL % 0xBBBB]),
        's17c_rs': base_log('s17c_rs', entry=False, ft=False, extra_before_guest=[
            MODE3 % (3, 0, 'spec'), 'ShaderReplay: stand spec applied file=%s permutation=0' % FB, RB % (0, 'written')]),
        's17c_e3': base_log('s17c_e3', prep=20000, extra_before_guest=[MODE3 % (3, 0, 'none'),
                                                                     'ShaderReplay: rebuild skipped reason=recipes_current'],
                            av_after=[AVL % 0xBBBB]),
        's17c_ew': base_log('s17c_ew', extra_before_guest=[MODE3 % (3, 0, 'none'), 'ShaderReplay: rebuild skipped reason=recipes_current',
                                                         'DualSrcBlend: supported=1 enabled=1', '[Vulkan][W] warning']),
        's17c_ks': base_log('s17c_ks', entry=False, ft=False, prep=None, extra_before_guest=[
            MODE3 % (3, 0, 'stop'), 'ShaderReplay: stand stop applied processed=5 records=10',
            'ShaderReplay: close stop requested precache_active=1', RB % (0, 'stopped'), 'ShaderReplay: close stop joined wait_ms=12']),
        's17c_kn': base_log('s17c_kn', ft=False, extra_before_guest=[MODE3 % (3, 0, 'none'), RB % (4, 'written')]),
        's17c_kc': base_log('s17c_kc', ft=False, extra_before_guest=['ShaderReplay: stand corrupt applied generation=3',
                                                                   MODE3 % (2, 3, 'corrupt'), RB % (0, 'written')]),
    }
    states_in = {
        'installed': state_text(f10='10 abc'),
        'empty_f10': state_text(),
        'empty_f19': state_text(f10='10 abc'),
        'cat_c2': state_text(f10='10 abc', replay_dir=c2rp),
        'rb_r3': state_text(f10='10 abc', f19='10 def', replay_dir=os.path.join(st, 's17c_r3', 'replay')),
        'k_ks': state_text(f10='10 abc', replay_dir=os.path.join(st, 's17c_ks', 'replay')),
    }
    for tag in R.ORDER:
        spec = R.SPEC[tag]
        d = os.path.join(root, 'runs', tag)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(root, 'log_%s.txt' % tag), 'w', newline='\n').write('\n'.join(logs[tag]) + '\n')
        open(os.path.join(root, 'stdout_%s.txt' % tag), 'w', newline='\n').write('Shaders: VS 1 | PS 1\n')
        cmd = ['kyty_emulator.exe', '--vulkan-validation', 'false']
        if spec['form'] == 'w':
            cmd += ['--vulkan-validation', 'true']
        run = dict(tag=tag, binary_sha256=R.BIN_EXPECT, env=env_for(tag), cmdline=cmd, prereg=dict(sha256=sha(seal)),
                   attempts=[att_for(tag)])
        json.dump(run, open(os.path.join(root, '%s.json' % tag), 'w'))
        open(os.path.join(root, 'rec_%s.mp4.idx' % tag), 'w').write('f\n' * 3000)
        w = lambda n, t: open(os.path.join(d, n + '.txt'), 'w', newline='\n').write(t)  # noqa: E731
        w('installed_sha', R.BIN_EXPECT + '\n')
        w('installed_before', R.FS6 + '\n')
        w('installed_after', R.FS6 + '\n')
        w('manifest_cmp', 'manifest cmp EQUAL files 9 listsha 00\n')
        w('glitch', 'one-frame glitches: 0\n')
        w('sheet', 'sheet: C:/x/sheet.png\n')
        w('state_in_name', spec['state'] + '\n')
        w('state_in', states_in[spec['state']])
        so = state_text(f10='10 abc', f19=None if tag in ('s17c_ks',) else '10 def',
                        replay_dir=None if tag in ('s17c_v0', 's17c_w0') else c2rp)
        if tag == 's17c_ks':
            so = 'dir f10 present files 3 cache_files 2 pipelines_bin 10 abc\ndir f19 present files 3 cache_files 3 pipelines_bin absent\n' \
                 'dir replay absent\n'
        w('state_out', so)


def use(root):
    R.ROOT = root
    R.SEAL_PATH = os.path.join(root, 'seal.md')
    R.BIN_PATH = os.path.join(root, 'bin.exe')


def read_all(root):
    use(root)
    words = {}
    for tag in R.ORDER:
        rows, meta = R.read_tag(tag)
        json.dump(R.to_json(tag, rows, meta), open(os.path.join(root, 'runs', tag, 'read.json'), 'w'))
        words[tag] = (rows.word(), rows)
    return words


def rowval(rows, prefix, kind='m'):
    lst = {'m': rows.mem, 'a': rows.adm, 'f': rows.form}[kind]
    for name, ok, det in lst:
        if name.startswith(prefix):
            return ok
    return 'MISSING'


TMP = tempfile.mkdtemp(prefix='s17c_fx_')
BASE = os.path.join(TMP, 'base')
make_root(BASE)
W = read_all(BASE)
for tag in R.ORDER:
    word, rows = W[tag]
    check(word == 'MEMBERS_PASS', 'baseline %s reads MEMBERS_PASS (got %s%s)' % (tag, word, '' if word == 'MEMBERS_PASS' else ': ' + str(
        [x for x in rows.adm + rows.form + rows.mem if x[1] is not True][:2])))
K = [0]


def variant(change, tags=None):
    """A copy of the baseline with change(root) applied; the tags re-read in order (all by default)."""
    K[0] += 1
    root = os.path.join(TMP, 'v%03d' % K[0])
    shutil.copytree(BASE, root)
    change(root)
    use(root)
    out = {}
    for tag in (tags or R.ORDER):
        rows, meta = R.read_tag(tag)
        json.dump(R.to_json(tag, rows, meta), open(os.path.join(root, 'runs', tag, 'read.json'), 'w'))
        out[tag] = rows
    return out


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


def one(tag, change, prefix, want, kind='m', name=None):
    rows = variant(change, [t for t in R.ORDER if R.ORDER.index(t) <= R.ORDER.index(tag)])[tag]
    got = rowval(rows, prefix, kind)
    check(got == want, '%s: %s -> %s (got %s, reading %s)' % (tag, name or prefix[:70], R.yn(want) if want != 'MISSING' else want,
                                                           R.yn(got) if got in (True, False, None) else got, rows.word()))
    return rows


def word(tag, change, want, name):
    rows = variant(change, [t for t in R.ORDER if R.ORDER.index(t) <= R.ORDER.index(tag)])[tag]
    check(rows.word() == want, '%s: %s -> %s (got %s)' % (tag, name, want, rows.word()))


# ------------------------------------------------------------------------------------------------ admission and form
word('s17c_v0', lambda r: edit_json(r, 's17c_v0', lambda d: d.update(binary_sha256='0' * 64)), 'NOT_ADMITTED', 'other binary in the json')
word('s17c_v0', lambda r: put(r, 'runs/s17c_v0/installed_sha.txt', 'x\n'), 'NOT_ADMITTED', 'installed_sha.txt not 2b5e2ce6')
word('s17c_v0', lambda r: open(os.path.join(r, 'bin.exe'), 'wb').write(b'MZ'), 'NOT_ADMITTED', 'version string missing in the binary')
word('s17c_v0', lambda r: edit(r, 'log_s17c_v0.txt', 'KytyPS5 a2fee0d,', 'KytyPS5 302347b,'), 'NOT_ADMITTED', 'other revision text')
word('s17c_v0', lambda r: open(os.path.join(r, 'seal.md'), 'ab').write(b'x'), 'NOT_ADMITTED', 'seal changed after the run')
word('s17c_r3', lambda r: edit_json(r, 's17c_r3', lambda d: d['env'].update(KYTY_SHADER_PREPARE='0')), 'NOT_ADMITTED',
     'KYTY_SHADER_PREPARE=0 at mode 3 (item 536 (v) N1)')
word('s17c_r3', lambda r: edit_json(r, 's17c_r3', lambda d: d['env'].pop('KYTY_FIX_F19')), 'NOT_ADMITTED', 'KYTY_FIX_F19 missing')
word('s17c_c2', lambda r: edit_json(r, 's17c_c2', lambda d: d['env'].update(KYTY_FIX_F19='1')), 'NOT_ADMITTED', 'capture at the rebuild signature')
word('s17c_v0', lambda r: edit_json(r, 's17c_v0', lambda d: d['env'].update(KYTY_GPU_CHECKPOINTS='1')), 'NOT_ADMITTED', 'KYTY_GPU_CHECKPOINTS')
word('s17c_v0', lambda r: edit_json(r, 's17c_v0', lambda d: d['env'].pop('KYTY_REC')), 'NOT_ADMITTED', 'V without KYTY_REC')
word('s17c_v0', lambda r: edit_json(r, 's17c_v0', lambda d: d['env'].update(KYTY_GUEST_ARGS='-lvl hub')), 'NOT_ADMITTED', 'other guest args')
word('s17c_w0', lambda r: edit_json(r, 's17c_w0', lambda d: d['env'].update(VK_LAYER_DUPLICATE_MESSAGE_LIMIT='10')), 'NOT_ADMITTED',
     'W duplicate limit not 100000000')
word('s17c_w0', lambda r: edit_json(r, 's17c_w0', lambda d: d['env'].update(VK_LAYER_MESSAGE_ID_FILTER='x')), 'NOT_ADMITTED', 'W id filter')
word('s17c_w0', lambda r: edit_json(r, 's17c_w0', lambda d: d.update(cmdline=['x', '--vulkan-validation', 'false'])), 'NOT_ADMITTED',
     'W without --vulkan-validation true')
word('s17c_v0', lambda r: edit_json(r, 's17c_v0', lambda d: d['env'].update(VK_LAYER_PATH='x')), 'NOT_ADMITTED', 'V with VK_LAYER_PATH')
word('s17c_v0', lambda r: edit(r, 'log_s17c_v0.txt', 'GuestOut: hello', 'Window 1 minimized\nGuestOut: hello'), 'NOT_ADMITTED',
     'window minimized')
word('s17c_v0', lambda r: edit(r, 'log_s17c_v0.txt', 'GuestOut: hello', 'Recovering Vulkan swapchain\nGuestOut: hello'), 'NOT_ADMITTED',
     'Recovering Vulkan swapchain')
word('s17c_v0', lambda r: edit(r, 'log_s17c_v0.txt', 'GuestOut: hello', 'GamePatch: x\nGuestOut: hello'), 'NOT_ADMITTED', 'GamePatch line')
word('s17c_v0', lambda r: put(r, 'runs/s17c_v0/state_in.txt', state_text(f10='1 a').replace('dir replay absent',
                                                                                          'dir replay present files 1 cache_files 0 pipelines_bin absent')),
     'NOT_ADMITTED', 'replay folder before the V')
word('s17c_c2', lambda r: put(r, 'runs/s17c_c2/state_in.txt', state_text(f10='10 abc')), 'NOT_ADMITTED',
     'capture with the f10 folder present (pipelines.bin, item 532 (v))')
word('s17c_c2', lambda r: put(r, 'runs/s17c_c2/state_in_name.txt', 'installed\n'), 'NOT_ADMITTED', 'other state name')
word('s17c_c2', lambda r: edit(r, 'log_s17c_c2.txt', PNO + '\n', ''), 'NOT_ADMITTED', 'no PipelinePrecache: no ... yet line (item 532 (v))')
word('s17c_n0', lambda r: put(r, 'runs/s17c_n0/state_in.txt', state_text(f19='1 a')), 'NOT_ADMITTED', 'null control with f19 present')
word('s17c_r3', lambda r: open(os.path.join(r, 'state/s17c_c2/replay/replay.cur'), 'w').write('2\n'), 'NOT_ADMITTED',
     'cat_c2 replay not byte for byte the saved catalogue')
word('s17c_r3', lambda r: put(r, 'runs/s17c_r3/state_in.txt', state_text(f10='1', f19='1 a', replay_dir=os.path.join(
    r, 'state/s17c_c2/replay'))), 'NOT_ADMITTED', 'rebuild with f19 present (not an empty variant folder)')
word('s17c_e3', lambda r: put(r, 'runs/s17c_e3/state_in.txt', state_text(f10='1', f19=None, replay_dir=os.path.join(
    r, 'state/s17c_r3/replay'))), 'NOT_ADMITTED', 'entry without the rebuilt folder')
word('s17c_v0', lambda r: os.remove(os.path.join(r, 'log_s17c_v0.txt')), 'NOT_ADMITTED', 'log missing')
word('s17c_v0', lambda r: put(r, 'runs/s17c_v0/installed_after.txt', R.FS8 + '\n'), 'FORM_FAIL', 'installed binary changed')
word('s17c_v0', lambda r: put(r, 'runs/s17c_v0/manifest_cmp.txt', 'manifest cmp DIFFER only-before 1 only-after 0\n'), 'FORM_FAIL',
     'manifest DIFFER after the return')
word('s17c_v0', lambda r: (put(r, 'runs/s17c_v0/installed_before.txt', R.FS8 + '\n'), put(r, 'runs/s17c_v0/installed_after.txt',
                                                                                        R.FS8 + '\n')), 'MEMBERS_PASS',
     'FS8 installed before and after is allowed')

# ------------------------------------------------------------------------------------------------ K2(2)
one('s17c_v0', lambda r: edit(r, 'log_s17c_v0.txt', 'GuestOut: hello', 'ShaderReplay: mode=0\nGuestOut: hello'), 'K2(2) 0 ShaderReplay', False)
one('s17c_v0', lambda r: open(os.path.join(r, 'stdout_s17c_v0.txt'), 'a').write('ShaderReplay: x\n'), 'K2(2) 0 ShaderReplay', False,
    name='ShaderReplay line in stdout')
one('s17c_v0', lambda r: put(r, 'runs/s17c_v0/state_out.txt', state_text(f10='1 a', replay_dir=os.path.join(r, 'state/s17c_c2/replay'))),
    'K2(2) no replay folder', False)
one('s17c_v0', lambda r: open(os.path.join(r, 'rec_s17c_v0.mp4.idx'), 'w').write('f\n' * 2999), 'K2(2) video index', False, name='2999 records')
one('s17c_v0', lambda r: open(os.path.join(r, 'rec_s17c_v0.mp4.idx'), 'w').write('f\n' * 3000), 'K2(2) video index', True, name='3000 records')
one('s17c_v0', lambda r: os.remove(os.path.join(r, 'rec_s17c_v0.mp4.idx')), 'K2(2) video index', None, name='no index')
one('s17c_v0', lambda r: put(r, 'runs/s17c_v0/glitch.txt', 'one-frame glitches: 1\n'), 'K2(2) 0 one-frame', False)
one('s17c_v0', lambda r: os.remove(os.path.join(r, 'runs/s17c_v0/glitch.txt')), 'K2(2) 0 one-frame', None, name='no glitch file')
one('s17c_v0', lambda r: put(r, 'runs/s17c_v0/sheet.txt', 'ffmpeg failed\n'), 'K2(2) sheet', False)
one('s17c_v0', lambda r: open(os.path.join(r, 'log_s17c_v0.txt'), 'a').write('Unhandled exception: x\n'), 'K2(2) 0 death', False)
one('s17c_v0', lambda r: open(os.path.join(r, 'stdout_s17c_v0.txt'), 'a').write('--- Fatal Error ---\n'), 'K2(2) 0 death', False,
    name='death marker in stdout')
one('s17c_v0', lambda r: edit(r, 'log_s17c_v0.txt', 'GuestOut: Level has started: ' + R.SKY, 'GuestOut: Level has started: hub'),
    'K2(2) entered', False)
one('s17c_v0', lambda r: edit_json(r, 's17c_v0', lambda d: d['attempts'][0].update(hold_exit=3)), 'K2(2) the process lived', False)
one('s17c_v0', lambda r: edit_json(r, 's17c_v0', lambda d: d['attempts'][0].update(hold_s=329.9)), 'K2(2) the process lived', False,
    name='hold_s below H')
one('s17c_v0', lambda r: edit(r, 'log_s17c_v0.txt', 'n=14 dt_us=75000000', 'n=14 dt_us=74999999'), 'K2(2) shown hold', False,
    name='shown hold 299.999999 s')
one('s17c_w0', lambda r: open(os.path.join(r, 'log_s17c_w0.txt'), 'a').write('[Vulkan][E] VUID-x\n'), 'K2(2) W 0 [Vulkan][E]', False)
one('s17c_w0', lambda r: edit(r, 'log_s17c_w0.txt', '[Vulkan][W] warning\n', ''), 'K2(2) W positive control', False, name='no [Vulkan][W]')
one('s17c_w0', lambda r: (edit(r, 'log_s17c_w0.txt', 'DualSrcBlend: supported=1 enabled=1\n', ''),
                          open(os.path.join(r, 'log_s17c_w0.txt'), 'a').write('DualSrcBlend: supported=1 enabled=1\n')),
    'K2(2) W positive control', False, name='DualSrcBlend after the first GuestOut')

# ------------------------------------------------------------------------------------------------ K3
one('s17c_c2', lambda r: edit(r, 'log_s17c_c2.txt', 'compat=absent', 'compat=ok'), 'K3 mode line', False)
one('s17c_c2', lambda r: edit(r, 'log_s17c_c2.txt', 'variant_fixb26_fixb1b_fixf10\n', 'variant_fixb26_fixb1b_fixf10_fixf19\n'),
    'K3 translation cache directory', False)
one('s17c_c2', lambda r: edit(r, 'log_s17c_c2.txt', 'at=stop', 'at=save'), 'K3 canon_mismatch = 0', None, name='no at=stop line')
one('s17c_c2', lambda r: edit(r, 'log_s17c_c2.txt', 'at=stop', 'at=save'), 'K3 offline R_ADDR', None, name='no at=stop line (R_ADDR)')
one('s17c_c2', lambda r: edit(r, 'log_s17c_c2.txt', 'canon_mismatch=0 dropped_queue=0 bytes=100 gen=3 canon_self=0 canon_residual=0 '
                                                   'canon_base=0 canon_big=0 pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 '
                                                   'catalogue_pipes=10 at=stop',
                              'canon_mismatch=1 dropped_queue=0 bytes=100 gen=3 canon_self=0 canon_residual=1 canon_base=0 canon_big=0 '
                              'pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop'), 'K3 canon_mismatch = 0', False)
LASTCAP = 'canon_base=0 canon_big=0 pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop'
one('s17c_c2', lambda r: edit(r, 'log_s17c_c2.txt', LASTCAP, LASTCAP.replace('canon_base=0', 'canon_base=2')), 'K3 canon_base = 0', False)
one('s17c_c2', lambda r: edit(r, 'log_s17c_c2.txt', 'canon_base=0 canon_big=0 pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 '
                                                   'catalogue_pipes=10 at=save', 'canon_base=4 canon_big=0 pipes_waiting=0 '
                                                   'catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=save'),
    'K3 canon_base = 0', True, name='only the last at=stop line counts')
CAPSTOP = CAP % 'stop'
one('s17c_c2', lambda r: edit(r, 'log_s17c_c2.txt', CAPSTOP, CAPSTOP.replace('dropped_queue=0', 'dropped_queue=3')), 'K3 dropped_queue', False)
one('s17c_c2', lambda r: edit_json(r, 's17c_c2', lambda d: d['attempts'][0].update(close_killed=True)), 'K3 dropped_queue', None,
    name='dropped_queue at a hard close (item 532 (z) N4)')
one('s17c_c2', lambda r: edit(r, 'log_s17c_c2.txt', CAPSTOP, CAPSTOP.replace('sources=5 specs=6', 'sources=0 specs=6')), 'K3 sources > 0', False)
one('s17c_c2', lambda r: edit(r, 'log_s17c_c2.txt', CAPSTOP, CAPSTOP.replace('sources=5 specs=6', 'sources=5 specs=0')), 'K3 specs > 0', False)
one('s17c_c2', lambda r: edit(r, 'log_s17c_c2.txt', CAPSTOP, CAPSTOP.replace('gen=3', 'gen=4')), 'K3 generation file', False,
    name='gen of the line != replay.cur')
one('s17c_c2', lambda r: os.remove(os.path.join(r, 'state/s17c_c2/replay/replay.3.bin')), 'K3 generation file', False,
    name='generation file missing')
one('s17c_c2', lambda r: write_replay(os.path.join(r, 'state/s17c_c2/replay'), 3, RAW), 'K3 offline R_ADDR = 0', False)
one('s17c_ca', lambda r: edit(r, 'log_s17c_ca.txt', 'ShaderReplay: stand addr applied spec=0x0000000000000016\n', ''),
    'K3 stand addr: line', None)
one('s17c_ca', lambda r: edit(r, 'log_s17c_ca.txt', 'ShaderReplay: stand addr applied spec=0x0000000000000016\n', ''),
    'K3 stand addr: offline', None, name='no stand line -> R_ADDR member not determined')
one('s17c_ca', lambda r: write_replay(os.path.join(r, 'state/s17c_ca/replay'), 3, CANON), 'K3 stand addr: offline R_ADDR > 0', False)
CANP = 'K3 stand canon'
one('s17c_cc', lambda r: edit(r, 'log_s17c_cc.txt', 'rejected=1', 'rejected=0'), CANP, None, name='only rejected=0 lines')
one('s17c_cc', lambda r: edit(r, 'log_s17c_cc.txt', ' culprit=5:role6:12345678->00000000', ''), CANP, None, name='self without culprit')
one('s17c_cc', lambda r: edit(r, 'log_s17c_cc.txt', 'role6:12345678->00000000', 'role7:12345678->00000000'), CANP, None,
    name='culprit of another role')
one('s17c_cc', lambda r: edit(r, 'log_s17c_cc.txt', 'role6:12345678->00000000', 'role6:12345678->00000001'), CANP, None,
    name='culprit role6 not ->00000000')
one('s17c_cc', lambda r: edit(r, 'log_s17c_cc.txt', 'ShaderReplay: capture reject why=self', 'ShaderReplay: capture rejectX why=self'),
    CANP, None, name='no reject line (the limit of 20 lines)')
one('s17c_cc', lambda r: edit(r, 'log_s17c_cc.txt', 'hash=0x00000000000000ab words=9', 'hash=0x00000000000000ac words=9'), CANP, None,
    name='reject line of another hash')
one('s17c_cc', lambda r: edit(r, 'log_s17c_cc.txt', 'canon_mismatch=1', 'canon_mismatch=0'), CANP, None, name='canon_mismatch 0')
one('s17c_cc', lambda r: edit(r, 'log_s17c_cc.txt', 'why=self ok=1 complete=1', 'why=residual'), CANP, None, name='reject not self')

# ------------------------------------------------------------------------------------------------ K4 / K5 null control
one('s17c_n0', lambda r: edit(r, 'log_s17c_n0.txt', AVL % SRC_HASHES[0] + '\n', ''), 'K5 null control', False)
one('s17c_n0', lambda r: (edit(r, 'log_s17c_n0.txt', AVL % SRC_HASHES[0] + '\n', ''),
                          edit(r, 'log_s17c_n0.txt', 'Shader translation cache', AVL % SRC_HASHES[0] + '\nShader translation cache')),
    'K5 null control', False, name='catalogue translation only before the preparation line')
one('s17c_n0', lambda r: edit(r, 'log_s17c_n0.txt', 'ShaderPreparation: startup wait finished', 'ShaderPreparationX'), 'K5 null control',
    None, name='no preparation line')
one('s17c_n0', lambda r: shutil.rmtree(os.path.join(r, 'state/s17c_c2')), 'K5 null control', None, name='no catalogue')
one('s17c_n0', lambda r: shutil.rmtree(os.path.join(r, 'state/s17c_n0/f19')), 'K4 live folder', False)
one('s17c_n0', lambda r: open(os.path.join(r, 'state/s17c_n0/f19', FA), 'ab').write(b'x'), 'K4 live folder', False, name='unreadable file')
one('s17c_n0', lambda r: edit(r, 'log_s17c_n0.txt', R.DIR1 + '\n', R.DIR0 + '\n'), 'K4 translation cache directory', False)

# ------------------------------------------------------------------------------------------------ K4 rebuild
RBW = RB % (0, 'written')
one('s17c_r3', lambda r: edit(r, 'log_s17c_r3.txt', 'generation=3 corrupt=0', 'generation=2 corrupt=0'), 'K4 mode line', False)
one('s17c_r3', lambda r: edit(r, 'log_s17c_r3.txt', 'compat=ok', 'compat=mismatch'), 'K4 mode line', False, name='compat mismatch')
one('s17c_r3', lambda r: edit(r, 'log_s17c_r3.txt', RBW, RBW + '\nShaderReplay: rebuild skipped reason=mode'), 'K4 a rebuild line', False)
one('s17c_r3', lambda r: edit(r, 'log_s17c_r3.txt', RBW + '\n', ''), 'K4 a rebuild line', False, name='no rebuild line')
one('s17c_r3', lambda r: open(os.path.join(r, 'log_s17c_r3.txt'), 'a').write('GpuHangAbort: x\n'), 'K4 0 death', False)
one('s17c_r3', lambda r: edit_json(r, 's17c_r3', lambda d: d['attempts'][0].update(outcome='exited')), 'K4 the process reached', False)
one('s17c_r3', lambda r: edit(r, 'log_s17c_r3.txt', 'pipelines_bin=written', 'pipelines_bin=empty'), 'K4 pipelines_bin=written', False)
one('s17c_r3', lambda r: edit(r, 'log_s17c_r3.txt', 'records=10 prepared=9', 'records=11 prepared=9'), 'K4 identity', False)
one('s17c_r3', lambda r: edit(r, 'log_s17c_r3.txt', 'rej_fused=1', 'rej_fused=0'), 'K4 partition', False)
one('s17c_r3', lambda r: edit(r, 'log_s17c_r3.txt', 'rej_fused=1 rej_key=0', 'rej_fused=0 rej_key=0', None) or
    edit(r, 'log_s17c_r3.txt', 'rej_ref=0', 'rej_ref=1'), 'K4 partition', True, name='rej_ref counts in the partition')
one('s17c_r3', lambda r: None, 'K4 share', True, name='share 9 / (10 + 0) = 0.90 (edge)')
one('s17c_r3', lambda r: edit(r, 'log_s17c_c2.txt', 'pipes_waiting=0 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop',
                              'pipes_waiting=1 catalogue_sources=5 catalogue_specs=6 catalogue_pipes=10 at=stop'), 'K4 share', False,
    name='share 9 / (10 + 1) < 0.90 (pipes_waiting of s17c_c2)')
one('s17c_r3', lambda r: edit(r, 'log_s17c_c2.txt', 'at=stop', 'at=save'), 'K4 share', None, name='no at=stop line in s17c_c2')
one('s17c_r3', lambda r: None, 'K4 rb_hit / live_perms', True, name='rb_hit 3 / live 3')
one('s17c_r3', lambda r: None, 'K4 rb_live_mismatch = 0', True, name='0 mismatches')
one('s17c_r3', lambda r: write_folder(os.path.join(r, 'state/s17c_r3/f19'), {FA: [PA1, PA0], FB: [(PB0[0], PB0[1], PB0[2], [MAGIC, 6])],
                                                                             FC: [PC0]}) or
    put(r, 'state/s17c_r3/replay/rebuild_manifest.tsv', manifest_text([(FA, 0, PA1[2], PA1[3]), (FA, 1, PA0[2], PA0[3]),
                                                                      (FB, 0, PB0[2], [MAGIC, 6]), (FC, 0, PC0[2], PC0[3])])),
    'K4 rb_live_mismatch = 0', False, name='one SPIR-V differs')
one('s17c_r3', lambda r: put(r, 'state/s17c_r3/replay/rebuild_manifest.tsv', manifest_text([(FA, 0, PA1[2], PA1[3]),
                                                                                           (FC, 0, PC0[2], PC0[3])])),
    'K4 rb_hit / live_perms', False, name='rb_hit 1 / live 3')
one('s17c_r3', lambda r: put(r, 'state/s17c_r3/replay/rebuild_manifest.tsv', manifest_text([(FA, 0, PA1[2], [MAGIC, 99]),
                                                                                           (FA, 1, PA0[2], PA0[3]), (FB, 0, PB0[2], PB0[3])])),
    'K4 comparison self-checks', False, name='manifest XXH3 != the file')
one('s17c_r3', lambda r: put(r, 'state/s17c_r3/replay/rebuild_manifest.tsv', manifest_text([(FA, 0, PA1[2], [MAGIC, 99]),
                                                                                           (FA, 1, PA0[2], PA0[3]), (FB, 0, PB0[2], PB0[3])])),
    'K4 rb_hit / live_perms', None, name='self-check failed -> members not determined')
one('s17c_r3', lambda r: put(r, 'state/s17c_r3/replay/rebuild_manifest.tsv', manifest_text([(FA, 0, PA1[2], PA1[3])], sig=R.SIG0)),
    'K4 comparison self-checks', False, name='manifest signature of F19=0')
one('s17c_r3', lambda r: write_folder(os.path.join(r, 'state/s17c_n0/f19'), {FA: [PA0, PA1], FB: [PB0]}, sig=R.SIG0),
    'K4 comparison self-checks', False, name='live folder of another signature')
one('s17c_r3', lambda r: os.remove(os.path.join(r, 'state/s17c_r3/replay/rebuild_manifest.tsv')), 'K4 comparison with the live', None,
    name='no manifest')
one('s17c_r3', lambda r: put(r, 'state/s17c_r3/replay/rebuild_manifest.tsv', manifest_text([(FA, 0, PA1[2], PA1[3]), (FA, 1, PA0[2], PA0[3]),
                                                                                           (FB, 0, PB0[2], PB0[3])], glued=True, crlf=True)),
    'K4 rb_hit / live_perms', True, name='old glued header with CRLF - the first row is kept')


def ten(root, hit):
    live = [([(k, 0, 0)], [], 0, [MAGIC, k]) for k in range(10)]
    write_folder(os.path.join(root, 'state/s17c_n0/f19'), {FA: live})
    write_folder(os.path.join(root, 'state/s17c_r3/f19'), {FA: live[:hit]})
    put(root, 'state/s17c_r3/replay/rebuild_manifest.tsv', manifest_text([(FA, k, 0, [MAGIC, k]) for k in range(hit)]))


one('s17c_r3', lambda r: ten(r, 9), 'K4 rb_hit / live_perms', True, name='rb_hit 9 / live 10 = 0.90 (edge)')
one('s17c_r3', lambda r: ten(r, 8), 'K4 rb_hit / live_perms', False, name='rb_hit 8 / live 10')
one('s17c_rs', lambda r: None, 'K4 stand spec: rb_live_mismatch > 0', True, name='stand permutation differs')
one('s17c_rs', lambda r: edit(r, 'log_s17c_rs.txt', 'ShaderReplay: stand spec applied file=%s permutation=0\n' % FB, ''),
    'K4 stand spec: line', None, name='no stand line')
one('s17c_rs', lambda r: edit(r, 'log_s17c_rs.txt', 'ShaderReplay: stand spec applied file=%s permutation=0\n' % FB, ''),
    'K4 stand spec: rb_live_mismatch', None, name='no stand line -> mismatch member not determined')
one('s17c_rs', lambda r: write_folder(os.path.join(r, 'state/s17c_n0/f19'), {FA: [PA0, PA1]}), 'K4 stand spec: rb_live_mismatch', None,
    name='stand permutation not among live_perms')
one('s17c_rs', lambda r: write_folder(os.path.join(r, 'state/s17c_rs/f19'), {FA: [PA1, PA0], FB: [PB0]}) or
    put(r, 'state/s17c_rs/replay/rebuild_manifest.tsv', manifest_text([(FA, 0, PA1[2], PA1[3]), (FA, 1, PA0[2], PA0[3]),
                                                                      (FB, 0, PB0[2], PB0[3])])),
    'K4 stand spec: rb_live_mismatch > 0', False, name='the stand changed nothing')

# ------------------------------------------------------------------------------------------------ K5
one('s17c_e3', lambda r: edit(r, 'log_s17c_e3.txt', 'ShaderReplay: rebuild skipped reason=recipes_current\n', ''), 'K5 fitness', False)
one('s17c_e3', lambda r: open(os.path.join(r, 'log_s17c_e3.txt'), 'a').write((AVL % SRC_HASHES[1]) + '\n'), 'K5 translations', False)
one('s17c_e3', lambda r: edit(r, 'log_s17c_r3.txt', AVL % 0xBBBB, AVL % SRC_HASHES[0]), 'K5 translations', None,
    name='s17c_r3 translated a catalogue program after its preparation screen')
one('s17c_e3', lambda r: edit(r, 'log_s17c_n0.txt', AVL % SRC_HASHES[0] + '\n', ''), 'K5 null control s17c_n0 > 0', False)
one('s17c_e3', lambda r: edit(r, 'log_s17c_e3.txt', 'finished in 20000 ms', 'finished in 180000 ms'), 'K5 preparation screen', True,
    name='180 000 ms (edge)')
one('s17c_e3', lambda r: edit(r, 'log_s17c_e3.txt', 'finished in 20000 ms', 'finished in 180001 ms'), 'K5 preparation screen', False,
    name='180 001 ms')
one('s17c_e3', lambda r: edit(r, 'log_s17c_e3.txt', 'ShaderPreparation: startup wait finished', 'ShaderPreparationX'),
    'K5 preparation screen', None, name='no preparation line')
one('s17c_e3', lambda r: open(os.path.join(r, 'rec_s17c_e3.mp4.idx'), 'w').write('f\n' * 2999), 'K5 video index', False)
one('s17c_e3', lambda r: put(r, 'runs/s17c_e3/glitch.txt', 'one-frame glitches: 2\n'), 'K5 0 one-frame', False)
one('s17c_e3', lambda r: open(os.path.join(r, 'log_s17c_e3.txt'), 'a').write('ErrorDeviceLost\n'), 'K5 0 death', False)
one('s17c_e3', lambda r: edit_json(r, 's17c_e3', lambda d: d['attempts'][0].update(outcome='timeout')), 'K5 entered', False)
one('s17c_ew', lambda r: open(os.path.join(r, 'log_s17c_ew.txt'), 'a').write('[Vulkan][E] x\n'), 'K5 W 0 [Vulkan][E]', False)
one('s17c_ew', lambda r: edit(r, 'log_s17c_ew.txt', 'DualSrcBlend: supported=1 enabled=1', 'DualSrcBlend: supported=1 enabled=0'),
    'K5 W positive control', False)
one('s17c_ew', lambda r: edit(r, 'log_s17c_ew.txt', 'reason=recipes_current', 'reason=mode'), 'K5 fitness', False)

# ------------------------------------------------------------------------------------------------ K6
one('s17c_ks', lambda r: edit(r, 'log_s17c_ks.txt', 'ShaderReplay: stand stop applied processed=5 records=10\n', ''),
    'K6 stand stop applied', None)
one('s17c_ks', lambda r: edit(r, 'log_s17c_ks.txt', 'ShaderReplay: stand stop applied processed=5 records=10\n', ''),
    'K6 sign of the break', None, name='no stand line -> sign not determined')
one('s17c_ks', lambda r: (edit(r, 'log_s17c_ks.txt', RB % (0, 'stopped') + '\n', ''),
                          edit(r, 'log_s17c_ks.txt', 'ShaderReplay: stand stop', RB % (0, 'stopped') + '\nShaderReplay: stand stop')),
    'K6 sign of the break', False, name='stopped line before the stand line')
one('s17c_ks', lambda r: edit(r, 'log_s17c_ks.txt', 'pipelines_bin=stopped', 'pipelines_bin=written'), 'K6 sign of the break', False,
    name='rebuild written, not stopped')
one('s17c_ks', lambda r: edit(r, 'runs/s17c_ks/state_out.txt', 'cache_files 3 pipelines_bin absent', 'cache_files 3 pipelines_bin 10 aa'),
    'K6 pipelines.bin is not written', False)
one('s17c_ks', lambda r: os.remove(os.path.join(r, 'runs/s17c_ks/state_out.txt')), 'K6 pipelines.bin is not written', None,
    name='no state_out.txt')
one('s17c_kn', lambda r: edit(r, 'log_s17c_kn.txt', 'compat=ok', 'compat=absent'), 'K6 mode line', False)
one('s17c_kn', lambda r: edit(r, 'log_s17c_kn.txt', 'perms_cached=4', 'perms_cached=0'), 'K6 the next start rebuilds the rest', False)
one('s17c_kn', lambda r: edit(r, 'log_s17c_kn.txt', 'pipelines_bin=written', 'pipelines_bin=stopped'), 'K6 the next start rebuilds', False,
    name='not written')
one('s17c_kn', lambda r: edit(r, 'log_s17c_kn.txt', RB % (4, 'written'), RB % (4, 'written') + '\nShaderReplay: rebuild skipped reason=x'),
    'K6 the next start rebuilds', False, name='skip line present')
one('s17c_kn', lambda r: open(os.path.join(r, 'log_s17c_kn.txt'), 'a').write('--- Error ---\n'), 'K6 0 death', False)
one('s17c_kn', lambda r: edit_json(r, 's17c_kn', lambda d: d['attempts'][0].update(hold_exit=1)), 'K6 the process lived', False)
one('s17c_kn', lambda r: edit(r, 'log_s17c_kn.txt', 'GuestOut: Level has started: ' + R.SKY, 'GuestOut: x'), 'K6 entered', False)
one('s17c_kc', lambda r: edit(r, 'log_s17c_kc.txt', 'stand corrupt applied generation=3', 'stand corrupt applied generation=2'),
    'K6 stand corrupt applied', False)
one('s17c_kc', lambda r: edit(r, 'log_s17c_kc.txt', 'ShaderReplay: stand corrupt applied generation=3\n', ''), 'K6 stand corrupt applied',
    None, name='no stand line')
one('s17c_kc', lambda r: edit(r, 'log_s17c_kc.txt', 'generation=2 corrupt=3', 'generation=3 corrupt=0'), 'K6 the previous generation', False)
one('s17c_kc', lambda r: open(os.path.join(r, 'log_s17c_kc.txt'), 'a').write('Unhandled exception: y\n'), 'K6 0 death', False)

# ------------------------------------------------------------------------------------------------ units
D = os.path.join(TMP, 'units')
os.makedirs(D)
f = os.path.join(D, FA)
open(f, 'wb').write(cache_bytes(R.SIG1, [PA0, PA1], with_extra=True))
x = tc_s17c.parse_file(f)
check(len(x['perms']) == 2 and x['perms'][1]['start'] == 4 and x['perms'][0]['spirv_xxh3'] == spirv_xxh(PA0[3]) and x['signature'] == R.SIG1,
      'tc: a file with every optional plan / info part parses (2 permutations, start, XXH3, signature)')
for kind, data in (('checksum', bytearray(cache_bytes(R.SIG1, [PA0]))), ('trailing', cache_bytes(R.SIG1, [PA0], trailing=b'\x00')),
                   ('spirv magic', cache_bytes(R.SIG1, [PA0], bad_magic=True)), ('signature', b'XX' + cache_bytes(R.SIG1, [PA0]))):
    if kind == 'checksum':
        data[-1] ^= 1
    try:
        tc_s17c.parse_bytes(bytes(data))
        check(False, 'tc: %s refused' % kind)
    except tc_s17c.Bad as e:
        check(kind.split()[0] in str(e) or kind == 'signature', 'tc: %s refused (%s)' % (kind, e))
check(tc_s17c.cache_files(D) == [FA] and tc_s17c.cache_files(os.path.join(D, 'none')) == [], 'tc: cache file names of a folder')
c = R.catalogue(os.path.join(BASE, 'state/s17c_c2/replay/replay.3.bin'))
check(c['R_ADDR'] == 0 and c['keep_big'] == 1 and c['src_hashes'] == sorted(SRC_HASHES) and c['generation'] == 3,
      'catalogue: R_ADDR 0, KEEP >= 0x10000 = 1, program hashes, generation')
c = R.catalogue(os.path.join(BASE, 'state/s17c_ca/replay/replay.3.bin'))
check(c['R_ADDR'] == 4, 'catalogue: raw words give R_ADDR 4 (got %d)' % c['R_ADDR'])
bad = bytearray(catalogue_bytes(3, CANON))
bad[-1] ^= 1
open(os.path.join(D, 'bad.bin'), 'wb').write(bytes(bad))
try:
    R.catalogue(os.path.join(D, 'bad.bin'))
    check(False, 'catalogue: spoiled body refused')
except ValueError as e:
    check(str(e) == 'checksum', 'catalogue: spoiled body refused')
mp = os.path.join(D, 'm.tsv')
rows = [(FA, 0, 0, [MAGIC, 1]), (FB, 3, 8, [MAGIC, 2])]
for glued in (False, True):
    for crlf in (False, True):
        open(mp, 'wb').write(manifest_text(rows, glued=glued, crlf=crlf).encode())
        sig, mr, mb = R.read_manifest(mp)
        check(sig == R.SIG1 and len(mr) == 2 and mr[0][0] == FA and mr[1][1] == 3 and mb == 0,
              'manifest: header %s %s - signature and both rows (first row kept)' % ('glued (old)' if glued else 'with newline',
                                                                                     'CRLF' if crlf else 'LF'))
open(mp, 'wb').write((manifest_text(rows) + 'garbage line\n').encode())
check(R.read_manifest(mp)[2] == 1, 'manifest: a malformed line is counted (bad lines)')
x = R.k4x(os.path.join(BASE, 'state/s17c_n0/f19'), os.path.join(BASE, 'state/s17c_r3/f19'),
          os.path.join(BASE, 'state/s17c_r3/replay/rebuild_manifest.tsv'))
check(x['live_perms'] == 3 and x['rebuilt'] == 4 and x['rb_hit'] == 3 and x['rb_dead'] == 1 and x['rb_live_mismatch'] == 0,
      'k4x: live 3, rebuilt 4, hit 3, dead 1, mismatch 0 (order of permutations differs between the folders)')
x = R.k4x(os.path.join(BASE, 'state/s17c_n0/f19'), os.path.join(BASE, 'state/s17c_rs/f19'),
          os.path.join(BASE, 'state/s17c_rs/replay/rebuild_manifest.tsv'), stand=(FB, '0'))
check(x['rb_live_mismatch'] == 1 and x['stand_in_live'] and x['stand_mismatch'], 'k4x: stand permutation found, in live, differs')
x = R.k4x(os.path.join(BASE, 'state/s17c_n0/f19'), os.path.join(BASE, 'state/s17c_rs/f19'),
          os.path.join(BASE, 'state/s17c_rs/replay/rebuild_manifest.tsv'), stand=(FB, None))
check(x.get('stand_in_manifest') is False, 'k4x: a stand line without an index is not found (no exception)')
check(not R.k4x(os.path.join(D, 'nope'), D, mp)['ok'], 'k4x: missing input -> not ok')
sd = os.path.join(D, 'tc')
os.makedirs(os.path.join(sd, 'replay'))
os.makedirs(os.path.join(sd, R.DIR1))
open(os.path.join(sd, 'replay', 'replay.cur'), 'w').write('7\n')
open(os.path.join(sd, 'replay', 'replay.7.bin'), 'wb').write(b'abc')
open(os.path.join(sd, R.DIR1, FA), 'wb').write(b'x')
open(os.path.join(sd, R.DIR1, 'pipelines.bin'), 'wb').write(b'pp')
st = state_s17c.parse('\n'.join(state_s17c.describe(sd)))
check(st['f10'] == dict(present=False) and st['f19']['present'] and st['f19']['cache_files'] == 1 and st['f19']['pipelines_bin'] and
      st['replay']['cur'] == '7' and st['replay']['replay_files']['replay.7.bin'][0] == 3, 'state: describe / parse round trip')
check(R.canon_stand(R.scan(os.path.join(BASE, 'log_s17c_cc.txt')))[0] is True, 'canon_stand: the pair of one hash and canon_mismatch 1')
use(BASE)
rep = dict(R.read_tag('s17c_c2')[0].rep)
check('equal True' in rep.get('signature of the capture folder state/s17c_c2/f10 (reference; seal section 1: = %s)' % R.SIG0, ''),
      'c2 report: signature of the saved capture folder = SIG0')
check(R.Rows().word() == 'MEMBERS_PASS', 'reading: no rows -> MEMBERS_PASS')
rw = R.Rows()
rw.m('a', None)
rw.m('b', False)
check(rw.word() == 'MEMBERS_FAIL', 'reading: NO wins over NOT DETERMINED')
rw = R.Rows()
rw.m('a', None)
rw.r('x', 'y')
check(rw.word() == 'NOT_EVALUABLE', 'reading: NOT DETERMINED -> NOT_EVALUABLE, report rows ignored')

# ------------------------------------------------------------------------------------------------ ASCII and cp1250
for name in ('s17c_read.py', 'tc_s17c.py', 'state_s17c.py', 'r_addr.py', 'go_s17c.sh', 'launch_s17c.sh', 'wait_s17c.sh', 'post_s17c.sh',
             'enter_scene.py', 'guard_s17c.py', 'test_s17c_read.py'):
    p = os.path.join(HERE, name)
    if os.path.exists(p):
        check(all(b < 128 for b in open(p, 'rb').read()), 'ASCII only: %s' % name)
    else:
        check(False, 'ASCII only: %s present' % name)
env = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
env.update(PYTHONIOENCODING='cp1250:strict', S17C_ROOT=BASE, S17C_SEAL=os.path.join(BASE, 'seal.md'), S17C_BIN=os.path.join(BASE, 'bin.exe'))
for args in (['s17c_cc'], ['--table'], ['s17c_r3']):
    p = subprocess.run([sys.executable, os.path.join(HERE, 's17c_read.py')] + args, env=env, capture_output=True)
    check(p.returncode == 0 and b'Traceback' not in p.stderr, 'cp1250 strict output: s17c_read.py %s (rc %d)' % (args[0], p.returncode))
shutil.rmtree(TMP, ignore_errors=True)
print('checks %d' % N[0])
print('ALL OK' if OK[0] else 'FAILED')
sys.exit(0 if OK[0] else 1)
