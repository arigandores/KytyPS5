"""S14j (HPP-533): summary of a SpecDump file (KYTY_TEST_SPECDUMP_* mode of shader_cfg_tests). Streams the dump in binary
mode; prints sha256 of the input, permutation counts by the key stage, distinct hashes and files, signature groups of
the file-sig lines, the aliased spec strings, and the reference line against PipelinePrecache ... sources loaded.

    python summary_s14j.py <specdump.txt> [<specdump_all.txt>]
"""
import collections
import hashlib
import sys


def sha(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(1 << 20), b''):
            h.update(block)
    return h.hexdigest()


def parse(path):
    perms = collections.Counter()
    hashes = collections.defaultdict(set)
    files = collections.defaultdict(set)
    sigs = collections.Counter()
    by_spec = collections.defaultdict(set)
    perm_max = collections.Counter()
    last = None
    with open(path, 'rb') as f:
        for raw in f:
            line = raw.decode('utf-8').rstrip('\n')
            last = line
            if line.startswith('SpecDump: file-sig file='):
                sig = line.split(' sig=', 1)[1]
                sigs[sig.split(':')[1][:8] if ':' in sig else '?'] += 1
            elif line.startswith('SpecDump: file='):
                head, spec = line.split(' spec=', 1)
                fields = dict(kv.split('=', 1) for kv in head[len('SpecDump: '):].split(' '))
                st = fields['stage']
                perms[st] += 1
                hashes[st].add(fields['hash'])
                files[st].add(fields['file'])
                by_spec[(st, spec)].add(fields['file'] + '#' + fields['perm'])
                perm_max[int(fields['perm'])] += 1
    return perms, hashes, files, sigs, by_spec, perm_max, last


path = sys.argv[1]
print('input %s sha256 %s' % (path, sha(path)))
perms, hashes, files, sigs, by_spec, perm_max, last = parse(path)
print('last line: %s' % last)
for st in sorted(perms):
    print('stage %s: perms %d, files %d, distinct hashes %d' % (st, perms[st], len(files[st]), len(hashes[st])))
total = sum(perms.values())
print('perms total %d (VS+PS+CS+MS); VS+PS %d' % (total, perms['VS'] + perms['PS']))
print('distinct (stage, hash) %d' % sum(len(v) for v in hashes.values()))
print('files with >= k permutations: %s' % ', '.join('%d:%d' % (k, perm_max[k]) for k in sorted(perm_max)))
print('signature groups (file-sig lines): %s' % ', '.join('%s %d' % kv for kv in sigs.most_common()))
print('distinct (stage, spec string) %d' % len(by_spec))
multi = sorted(((st, spec), len(w)) for (st, spec), w in by_spec.items() if len(w) > 1)
print('spec strings shared by >= 2 permutations: %d (permutations in them %d)' % (len(multi), sum(n for _, n in multi)))
print('reference: PipelinePrecache "3456 sources loaded" (S10 logs on 699c1e4b, e.g. s10/log_t2_1.txt:2466) counts loads per '
      'recipe - pipelineCache.cpp loaded_sources += vs_loaded + ps_loaded per graphics recipe, + cs_loaded per compute '
      'recipe - with repetition; 1660 graphics + 141 compute recipes give at most 1660 * 2 + 141 = 3461; the dump counts '
      'distinct permutations per file (%d), so equality is not expected' % total)
if len(sys.argv) > 2:
    p2 = sys.argv[2]
    print('letter run %s sha256 %s' % (p2, sha(p2)))
    perms2, _, files2, sigs2, _, _, last2 = parse(p2)
    print('letter run: last line %s' % last2[:160])
    print('letter run: perm lines %d, files with perm lines %d, file-sig lines %d (no totals line: the process stopped)'
          % (sum(perms2.values()), sum(len(v) for v in files2.values()), sum(sigs2.values())))
