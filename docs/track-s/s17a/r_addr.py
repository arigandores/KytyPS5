"""S17a (HPP-611, ROADMAP s122 item 524(z) K3; RC7 of the S16b review): offline scanner R_ADDR of the S-replay catalogue
(format KytyReplay1, src/graphics/host_gpu/renderer/pipeline/shaderReplay.h).

R_ADDR = the number of words of R-SPEC records whose role is an address role (PTR_LO, PTR_HI, V_LO, V_HI, T_LO, T_HI,
T_META6, T_META7, INERT) and whose value is not in the canonical form of that role (shaderReplay.h, Role; the same rule
as ShaderReplay::WordCanonical). R-SRC and R-PIPE carry no address field by construction (key, code, POD); KEEP words are
counted apart (`keep`), not checked.

Every size and offset below is the one of the "ShaderReplayLayout:" line printed by shader_cfg_tests
(TestShaderReplayFormat, ShaderReplay::LayoutLine: sizeof/offsetof of the structs); --layout <file> compares the
constants with that line and fails on any difference (the fixture of RC7). Usage:
  python r_addr.py <replay.<g>.bin> [--layout <file with the ShaderReplayLayout line>]
  python r_addr.py --layout <file>            (layout check only)
"""
import struct
import sys

import xxhash

LAYOUT = {
    'word': 6, 'word.value': 0, 'word.role': 4, 'word.flags': 5,
    'file': 16, 'file.magic': 0, 'file.format': 8, 'file.compat_size': 12,
    'body': 32, 'body.generation': 0, 'body.body_checksum': 8, 'body.sources': 16, 'body.specs': 20, 'body.pipes': 24,
    'src': 72, 'src.src_id': 0, 'src.hash': 8, 'src.stage': 16, 'src.user_data_count': 20, 'src.code_size': 24,
    'src.static_words': 28, 'src.code_words': 32, 'src.back_words': 36, 'src.sha256': 40,
    'spec': 40, 'spec.spec_id': 0, 'spec.src_id': 8, 'spec.live_spec_hash': 16, 'spec.stored_start': 24,
    'spec.user_words': 28, 'spec.reads': 32, 'spec.words': 36,
    'pipe': 32, 'pipe.pipe_id': 0, 'pipe.spec': 8, 'pipe.kind': 24, 'pipe.pod_size': 28,
}
VERSIONS = '1:1:1:1'
MAGIC = b'KytyRpl1'

ROLES = ['KEEP', 'INERT', 'PTR_LO', 'PTR_HI', 'V_LO', 'V_HI', 'T_LO', 'T_HI', 'T_META6', 'T_META7']


def canonical(role, v):
    lo4 = (v & ~0xF) == 0x100
    if role == 0:
        return True
    if role in (1, 4):
        return v == 0 or lo4
    if role == 2:
        return lo4
    if role in (3, 5):
        return (v & 0xFFFF) == 0
    if role == 6:
        return v in (0, 1)
    if role == 7:
        return (v & 0xFF) == 0
    if role == 8:
        return (v & 0xFF000000) == 0
    if role == 9:
        return v == 0
    return False


def parse_layout_line(text):
    for line in text.splitlines():
        at = line.find('ShaderReplayLayout:')
        if at < 0:
            continue
        values = {}
        for item in line[at + len('ShaderReplayLayout:'):].split():
            name, value = item.split('=', 1)
            values[name] = value
        return values
    return None


def check_layout(path):
    text = open(path, 'rb').read().decode('utf-8', 'replace')
    printed = parse_layout_line(text)
    if printed is None:
        print('LAYOUT: no ShaderReplayLayout line in', path)
        return False
    ok = True
    for name, value in LAYOUT.items():
        if printed.get(name) != str(value):
            print('LAYOUT MISMATCH', name, 'scanner', value, 'printed', printed.get(name))
            ok = False
    extra = sorted(set(printed) - set(LAYOUT) - {'versions'})
    if extra:
        print('LAYOUT: printed fields the scanner does not know:', extra)
        ok = False
    if printed.get('versions') != VERSIONS:
        print('LAYOUT: versions', printed.get('versions'), 'scanner', VERSIONS)
        ok = False
    print('LAYOUT', 'OK' if ok else 'FAIL', 'fields', len(LAYOUT))
    return ok


def scan(data):
    """-> dict with counts; raises ValueError on a malformed file."""
    L = LAYOUT
    if data[:8] != MAGIC:
        raise ValueError('magic')
    compat_size = struct.unpack_from('<I', data, L['file.compat_size'])[0]
    pos = L['file'] + compat_size
    generation, checksum, n_src, n_spec, n_pipe = struct.unpack_from('<QQIII', data, pos)
    pos += L['body']
    body = data[pos:]
    if xxhash.xxh3_64_intdigest(body) != checksum:
        raise ValueError('checksum')
    for _ in range(n_src):
        sw, cw, bw = struct.unpack_from('<III', data, pos + L['src.static_words'])
        pos += L['src'] + 4 * (sw + cw + bw)
    out = {'generation': generation, 'sources': n_src, 'specs': n_spec, 'pipes': n_pipe, 'words': 0, 'keep': 0,
           'R_ADDR': 0, 'bad_specs': 0, 'roles': [0] * len(ROLES), 'bad_roles': [0] * len(ROLES), 'unknown_role': 0}
    for _ in range(n_spec):
        (n_words,) = struct.unpack_from('<I', data, pos + L['spec.words'])
        pos += L['spec']
        bad = 0
        for k in range(n_words):
            at = pos + k * L['word']
            value = struct.unpack_from('<I', data, at + L['word.value'])[0]
            role = data[at + L['word.role']]
            out['words'] += 1
            if role >= len(ROLES):
                out['unknown_role'] += 1
                bad += 1
                continue
            out['roles'][role] += 1
            if role == 0:
                out['keep'] += 1
            elif not canonical(role, value):
                out['bad_roles'][role] += 1
                bad += 1
        out['R_ADDR'] += bad
        out['bad_specs'] += 1 if bad else 0
        pos += n_words * L['word']
    for _ in range(n_pipe):
        (pod,) = struct.unpack_from('<I', data, pos + L['pipe.pod_size'])
        pos += L['pipe'] + pod
    if pos != len(data):
        raise ValueError('trailing bytes %d' % (len(data) - pos))
    return out


def main(argv):
    layout = None
    files = []
    i = 0
    while i < len(argv):
        if argv[i] == '--layout':
            layout = argv[i + 1]
            i += 2
        else:
            files.append(argv[i])
            i += 1
    ok = True
    if layout is not None:
        ok = check_layout(layout) and ok
    for path in files:
        data = open(path, 'rb').read()
        r = scan(data)
        print('file', path, 'generation', r['generation'], 'sources', r['sources'], 'specs', r['specs'], 'pipes',
              r['pipes'], 'words', r['words'], 'keep', r['keep'], 'unknown_role', r['unknown_role'])
        print('roles', ' '.join('%s=%d' % (ROLES[k], r['roles'][k]) for k in range(len(ROLES))))
        print('not canonical', ' '.join('%s=%d' % (ROLES[k], r['bad_roles'][k]) for k in range(len(ROLES))))
        print('R_ADDR=%d specs_with_address=%d' % (r['R_ADDR'], r['bad_specs']))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
