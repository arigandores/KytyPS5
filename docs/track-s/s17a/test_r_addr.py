"""S17a (HPP-611): fixtures of the R_ADDR scanner (r_addr.py). Synthetic generation files built from r_addr.LAYOUT:
a canonical catalogue -> R_ADDR 0; the same with one raw address word per address role -> R_ADDR = that count (the form
of the stand KYTY_S_REPLAY_TEST=addr); a spoiled body -> checksum error; trailing bytes -> error; a layout line with one
changed offset -> layout check FAIL; the printed line of the build (argument) -> layout check OK. Ends with ALL OK.
Usage: python test_r_addr.py [<file with the ShaderReplayLayout line of shader_cfg_tests>]"""
import os
import struct
import sys
import tempfile

import xxhash

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import r_addr  # noqa: E402

L = r_addr.LAYOUT
ok = True


def check(cond, text):
    global ok
    print(('ok   ' if cond else 'FAIL ') + text)
    ok = ok and cond


def build(spec_words, compat=b'compat', pipe_pod=b'', trailing=b''):
    body = b''
    # one source: 2 static words, 3 code words, 0 back
    src = bytearray(L['src'])
    struct.pack_into('<Q', src, L['src.src_id'], 11)
    struct.pack_into('<I', src, L['src.static_words'], 2)
    struct.pack_into('<I', src, L['src.code_words'], 3)
    struct.pack_into('<I', src, L['src.back_words'], 0)
    body += bytes(src) + struct.pack('<5I', 1, 2, 3, 4, 5)
    spec = bytearray(L['spec'])
    struct.pack_into('<Q', spec, L['spec.spec_id'], 22)
    struct.pack_into('<I', spec, L['spec.words'], len(spec_words))
    body += bytes(spec)
    for value, role in spec_words:
        w = bytearray(L['word'])
        struct.pack_into('<I', w, L['word.value'], value)
        w[L['word.role']] = role
        body += bytes(w)
    pipe = bytearray(L['pipe'])
    struct.pack_into('<I', pipe, L['pipe.pod_size'], len(pipe_pod))
    body += bytes(pipe) + pipe_pod
    head = bytearray(L['file'])
    head[0:8] = r_addr.MAGIC
    struct.pack_into('<I', head, L['file.format'], 1)
    struct.pack_into('<I', head, L['file.compat_size'], len(compat))
    bh = bytearray(L['body'])
    struct.pack_into('<QQIII', bh, 0, 7, xxhash.xxh3_64_intdigest(body + trailing), 1, 1, 1)
    return bytes(head) + compat + bytes(bh) + body + trailing


CANON = [(0x100, 2), (0x00000000, 3), (7, 0), (0x10A, 4), (0x00200000, 5), (1, 6), (0x09000000, 7),
         (0x00ABCDEF, 8), (0, 9), (0x103, 1), (0, 1)]
RAW = [(0x12345678, 2), (0x00000002, 3), (7, 0), (0x80001000, 4), (0x00200003, 5), (0x40000, 6), (0x09000012, 7),
       (0x5A000000, 8), (0x1234, 9), (0xDEADBEEF, 1), (0, 1)]

r = r_addr.scan(build(CANON, pipe_pod=b'\x00' * 9))
check(r['R_ADDR'] == 0 and r['bad_specs'] == 0 and r['keep'] == 1 and r['words'] == 11, 'canonical catalogue R_ADDR 0')
r = r_addr.scan(build(RAW))
check(r['R_ADDR'] == 9 and r['bad_specs'] == 1, 'raw address words R_ADDR 9 (got %d)' % r['R_ADDR'])
spoiled = bytearray(build(CANON))
spoiled[-1] ^= 0xFF
try:
    r_addr.scan(bytes(spoiled))
    check(False, 'spoiled body rejected')
except ValueError as e:
    check(str(e) == 'checksum', 'spoiled body rejected (%s)' % e)
try:
    r_addr.scan(build(CANON, trailing=b'\x00\x00'))
    check(False, 'trailing bytes rejected')
except ValueError as e:
    check(str(e).startswith('trailing'), 'trailing bytes rejected (%s)' % e)
check(r_addr.canonical(2, 0x100) and not r_addr.canonical(2, 0) and r_addr.canonical(6, 1) and not r_addr.canonical(6, 2)
      and not r_addr.canonical(10, 0), 'canonical() = ShaderReplay::WordCanonical fixtures')

line = 'ShaderReplayLayout: ' + ' '.join('%s=%d' % kv for kv in r_addr.LAYOUT.items()) + ' versions=' + r_addr.VERSIONS
with tempfile.TemporaryDirectory() as d:
    good = os.path.join(d, 'good.txt')
    bad = os.path.join(d, 'bad.txt')
    open(good, 'w').write('noise\n' + line + '\n')
    open(bad, 'w').write(line.replace('spec.words=36', 'spec.words=32') + '\n')
    check(r_addr.check_layout(good), 'layout check of a matching line')
    check(not r_addr.check_layout(bad), 'layout check catches a moved offset')
if len(sys.argv) > 1:
    check(r_addr.check_layout(sys.argv[1]), 'layout of the build = scanner constants (%s)' % sys.argv[1])
else:
    print('note: no build layout file given; the fixture against the printed line is not run')
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
