"""M2a (HPP-838, ROADMAP s122 item 756(v)(1)(ii)): which programs of the game (every AMDGPU ELF of eboot.bin / sce_module,
.text XXH3-64 = program hash) carry the instructions of T234 (DS 0x12/0x13), T306 (MIMG image_sample*_o 0x30-0x37) -
a linear walk with the length rules of docs/track-f/f11a/t1scan_f11a.py decode() (taken from that file by ast, no copy
edits). Candidates only: each is confirmed with the translator's own decoder (KYTY_M_DECODE) by the caller.
Usage: python scan_game.py <out tsv>. Lock and STOP checked."""
import ast
import collections
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_named import elf_programs, GAME  # noqa: E402
import xxhash  # noqa: E402

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/m657/STOP'
SRC = 'C:/kyty/KytyPS5/docs/track-f/f11a/t1scan_f11a.py'


def load_decode():
    tree = ast.parse(open(SRC, encoding='utf-8').read())
    fn = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in ('decode', 'sdst_regs')]
    mod = ast.Module(body=fn, type_ignores=[])
    ns = {}
    exec(compile(mod, SRC, 'exec'), ns)
    return ns['decode']


def main():
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK or STOP')
        return 3
    decode = load_decode()
    files = [GAME + 'eboot.bin']
    mod = GAME + 'sce_module/'
    if os.path.isdir(mod):
        files += [mod + x for x in sorted(os.listdir(mod)) if x.lower().endswith(('.prx', '.sprx', '.elf'))]
    seen = set()
    rows = []
    for fp in files:
        for src, elf, code in elf_programs(fp):
            h = '%016x' % xxhash.xxh3_64_intdigest(code)
            if h in seen:
                continue
            seen.add(h)
            words = [int.from_bytes(code[i:i + 4], 'little') for i in range(0, len(code) - 3, 4)]
            hits = collections.Counter()
            for rec in decode(words):
                w = rec['words'][0] if rec['words'] else 0
                if rec['fam'] == 'DS':
                    op = (w >> 18) & 0xFF
                    if op in (0x12, 0x13):
                        hits['T234'] += 1
                if rec['fam'] == 'MIMG' and rec.get('op') in range(0x30, 0x38):
                    hits['T306_%02x' % rec['op']] += 1
            if hits:
                rows.append((h, src, '0x%x' % elf, ' '.join('%s=%d' % kv for kv in sorted(hits.items()))))
    with open(sys.argv[1], 'w', newline='\n') as f:
        f.write('hash16\tsource\telf\thits\n')
        for r in rows:
            f.write('\t'.join(r) + '\n')
    print('programs', len(seen), 'with hits', len(rows))
    for r in rows:
        print('\t'.join(r))
    return 0


if __name__ == '__main__':
    sys.exit(main())
