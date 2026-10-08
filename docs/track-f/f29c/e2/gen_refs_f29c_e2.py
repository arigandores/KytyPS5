"""F29c edition 2 (HPP-702): the '<commit>:<path>:<line>' references of the section "издание 2" of f29c.md, found by whole
anchors in 726e751e (the line holds the anchor, the next line holds the +1 anchor; the pair must be unique). Appends to a
copy of refs_f29c.tsv, so that refs_f29c.py checks the whole report with one table. Copy of gen_refs_f29c.py. ASCII.

    python gen_refs_f29c_e2.py <old.tsv> <out.tsv>
"""
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
C = '726e751e'
BC = 'src/graphics/host_gpu/renderer/cache/bufferCache.cpp'
BH = 'src/graphics/host_gpu/renderer/cache/bufferCache.h'
FS = 'src/common/frameStats.h'
VO = 'src/graphics/presentation/videoOut.cpp'
ST = 'tests/B12BdaStampStand.cpp'
REFS = [
    ('bc_rewalk', BC, 'if (b12_pass && m_bda_region_stamps[index].walked_pass == m_bda_pass) {',
     'm_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);'),
    ('bc_late', BC, 'if (b12_pass && m_bda_region_stamps[index].skipped_pass == m_bda_pass) {',
     'const auto& late = m_bda_region_stamps[index];'),
    ('bc_late_cond', BC,
     'if (late.generation == m_bda_stamp_generation && late.stamp == m_memory_tracker.RegionWriteStamp(index) &&',
     '!(use_bits && BdaRegionWritePending(index))) {'),
    ('bc_late_collect', BC, 'm_memory_tracker.CollectCpuModifiedRanges(cursor, bytes, m_bda_dirty_ranges);',
     'm_b12_lskip++;'),
    ('bc_take', BC, 'const bool bit_clear = use_bits && !BdaTakeRegionWrite(index);',
     'if (bit_clear && m_bda_region_stamps[index].generation == m_bda_stamp_generation) {'),
    ('bc_mark_bit', BC, 'm_bda_region_stamps[index].skipped_pass = m_bda_pass;', '}'),
    ('bc_mark_seen', BC, 'seen.skipped_pass = m_bda_pass;', '}'),
    ('bc_witness', BC, 'seen = {stamp, m_bda_stamp_generation};', 'if (b12_pass) {'),
    ('bc_walked', BC, 'seen.walked_pass = m_bda_pass;', '}'),
    ('bc_stat', BC, 'LOGF("FixB12Stat: passes=%llu rewalk=%llu rwd=%llu lskip=%llu',
     'static_cast<unsigned long long>(m_b12_rewalk), static_cast<unsigned long long>(m_b12_rwd),'),
    ('bh_skipped', BH, 'uint64_t                   skipped_pass = 0;', '};'),
    ('fs_lskip', FS, 'BdaB12Lskip,             // bda_b12_lskip', '// Session 113 (item 18)'),
    ('vo_lskip', VO, '{"bda_b12_lskip", FS::Counter::BdaB12Lskip, false},', '{"prio_unsub", FS::Counter::PrioUnsub, false},'),
    ('st_late', ST, 'if (b12_pass && region_stamps[index].skipped_pass == bda_pass) {',
     'const auto& late = region_stamps[index];'),
    ('st_mark_bit', ST, 'region_stamps[index].skipped_pass = bda_pass;', '}'),
    ('st_mark_seen', ST, 'seen.skipped_pass = bda_pass;', '}'),
    ('st_hlost1', ST, 'hlost1 += Covered(in_pass, hs.address, page) ? 0 : 1;', 'hlost += h_lost ? 1 : 0;'),
]


def main(argv):
    rows = open(argv[0], encoding='utf-8').read().rstrip('\n').split('\n')
    cache = {}
    ok = True
    for name, path, a, b in REFS:
        if path not in cache:
            r = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (C, path)], capture_output=True, check=True)
            cache[path] = [x.strip() for x in r.stdout.decode('utf-8').split('\n')]
        lines = cache[path]
        hits = [i for i in range(len(lines) - 1) if a in lines[i] and (lines[i + 1] == '' if b == '' else b in lines[i + 1])]
        if len(hits) != 1:
            ok = False
            print('FAIL %s hits %d' % (name, len(hits)))
            continue
        rows.append('\t'.join([C, path, str(hits[0] + 1), a, b]))
        print('%s %s:%s:%d' % (name, C, path, hits[0] + 1))
    open(argv[1], 'w', encoding='utf-8', newline='\n').write('\n'.join(rows) + '\n')
    print('ROWS %d %s' % (len(rows), 'OK' if ok else 'FAILED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
