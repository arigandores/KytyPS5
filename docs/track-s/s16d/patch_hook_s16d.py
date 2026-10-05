"""S16d (HPP-608): put the probe P-S16 into a tree's shader_cfg_tests - copies S16dProbe.inc to tests/ and inserts the
include and the KYTY_S16D_JOBS entry into tests/shaderCfgTests.cpp (whole-line anchors, LF, CR stripped and restored).

    python patch_hook_s16d.py <tree> [--f19]     # --f19: the tree has the F19 code (KYTY_S16D_HAVE_F19 for arm B)
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
NL = chr(10)


def main():
    tree = sys.argv[1]
    f19 = '--f19' in sys.argv[2:]
    shutil.copyfile(os.path.join(HERE, 'S16dProbe.inc'), os.path.join(tree, 'tests', 'S16dProbe.inc'))
    path = os.path.join(tree, 'tests', 'shaderCfgTests.cpp')
    raw = open(path, 'rb').read()
    crlf = b'\r\n' in raw
    text = raw.decode('utf-8').replace('\r', '')
    lines = text.split(NL)
    anchor = ['int main() {', '  using namespace Libs::Graphics;', '', '  EnsureConfigInitialized();']
    hits = [i for i in range(len(lines) - 3) if lines[i:i + 4] == anchor]
    if len(hits) != 1:
        raise SystemExit('anchor hits %d' % len(hits))
    i = hits[0]
    if any('S16dProbe.inc' in x for x in lines):
        raise SystemExit('already patched')
    head = ['// Track S, S16d (HPP-608, ROADMAP s122 item 516(v)): probe P-S16 of S-replay (tests/S16dProbe.inc).']
    if f19:
        head.append('#define KYTY_S16D_HAVE_F19 1')
    head += ['#include "S16dProbe.inc"', '']
    entry = ['  if (const char *s16d_jobs = std::getenv("KYTY_S16D_JOBS"); s16d_jobs != nullptr) {',
             '    // Track S, S16d (HPP-608): probe P-S16, read-only over the S13b catalogue (S16dProbe.inc).',
             '    const char *s16d_out = std::getenv("KYTY_S16D_OUT");',
             '    return s16d_out == nullptr ? 1 : S16dProbe::Main(s16d_jobs, s16d_out);',
             '  }']
    out = lines[:i] + head + lines[i:i + 4] + entry + lines[i + 4:]
    data = NL.join(out)
    if crlf:
        data = data.replace(NL, chr(13) + NL)
    open(path, 'wb').write(data.encode('utf-8'))
    print('patched %s at line %d (f19=%d, crlf=%d)' % (path, i + 1, f19, crlf))


if __name__ == '__main__':
    main()
