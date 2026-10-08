"""F29c3 (HPP-713, ROADMAP s122 item 645(v)): the '<commit>:<path>:<line>' references of the section "Издание 3 (стенд)" of
docs/track-f/f29c.md - each found by whole anchors (the line holds the anchor, the next line holds the +1 anchor; the pair
must be unique in the file at that commit), then checked against the report text. Negative control: --shift 1 moves every
line by one and must print FAILED. ASCII, LF.

    python refs_f29c3.py <report.md> [--shift N]
"""
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
ST = 'tests/B12BdaStampStand.cpp'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
REFS = [
    ('726e751e', BC, '!(use_bits && BdaRegionWritePending(index))) {', 'cursor += bytes;'),
    ('726e751e', BC, 'const bool bit_clear = use_bits && !BdaTakeRegionWrite(index);',
     'if (bit_clear && m_bda_region_stamps[index].generation == m_bda_stamp_generation) {'),
    ('0db3b3eb', ST, '!(use_bits && Libs::Graphics::BdaRegionWritePending(index))) {', 'cursor += bytes;'),
    ('0db3b3eb', ST, 'const bool bit_clear = use_bits && !Libs::Graphics::BdaTakeRegionWrite(index);',
     'if (bit_clear && region_stamps[index].generation == stamp_generation) {'),
    ('0db3b3eb', ST, 'const bool     h_bit  = std::strcmp(hook_s, "hook=bitonly") == 0; // F29c3',
     'const bool     h_any  = h_up || h_low || h_bit;'),
    ('0db3b3eb', ST, 'if (s->bit_only) { // F29c3: the bit alone, no page write, no stamp move',
     'Libs::Graphics::BdaNoteRegionWrite(s->address / TRACKER_REGION_SIZE);'),
    ('0db3b3eb', ST, 'if (p == 0 && h_bit && Libs::Graphics::BdaRegionWritePending(hs.address / TRACKER_REGION_SIZE)) {',
     'bit1++;'),
    ('0db3b3eb', ST, 'late_lskips += cache.lskip - l0;', 'late_bit_skips += cache.bit_skipped - b0;'),
    ('0db3b3eb', ST, 'if (hs.fired && h_bit) {', 'hfired++;'),
]


def main(argv):
    report = open(argv[0], encoding='utf-8').read()
    shift = int(argv[argv.index('--shift') + 1]) if '--shift' in argv else 0
    cache = {}
    ok = True
    for c, path, a, b in REFS:
        key = (c, path)
        if key not in cache:
            r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % key], capture_output=True, check=True)
            cache[key] = [x.strip() for x in r.stdout.decode('utf-8').split('\n')]
        lines = cache[key]
        hits = [i for i in range(len(lines) - 1) if a in lines[i] and b in lines[i + 1]]
        if len(hits) != 1:
            ok = False
            print('FAIL anchors %s:%s hits %d: %s' % (c, path, len(hits), a[:60]))
            continue
        n = hits[0] + 1
        ref = '%s:%s:%d' % (c, path, n + shift)
        idx = n + shift - 1
        line_ok = 0 <= idx < len(lines) - 1 and a in lines[idx] and b in lines[idx + 1]
        in_report = ('`%s`' % ref) in report
        print('%s %s anchor %s +1 %s report %s' % ('OK  ' if line_ok and in_report else 'FAIL', ref,
                                                      'yes' if line_ok else 'NO', 'yes' if line_ok else 'NO',
                                                      'yes' if in_report else 'NO'))
        ok &= line_ok and in_report
    print('REFS %d %s' % (len(REFS), 'ALL OK' if ok else 'FAILED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
