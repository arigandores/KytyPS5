"""Track M, M2b (HPP-839, ROADMAP s122 item 756(v)(2)): pairs of package paths with the same 31-bit FNV-1a ID.

ComputeFileId of libAmpr.cpp (FS15): FNV-1a 32 over the bytes of the guest path (prefix + path, as the APR resolve
concatenates them), masked with 0x7fffffff. Walks the package directory read-only (files and directories), hashes
"<prefix><relative path with '/'>" for each prefix and prints every pair (all members of a bucket of size >= 2).

Usage: pairs_t265.py <package dir> <out.tsv>
Output TSV: prefix, id, kind_a, size_a, path_a, kind_b, size_b, path_b (path without the prefix); last line ALL OK / FAIL.
"""
import os
import sys
from collections import defaultdict

PREFIXES = ['/app0/', 'app0/']


def fnv31(data):
    h = 2166136261
    for b in data:
        h ^= b
        h = (h * 16777619) & 0xffffffff
    return h & 0x7fffffff


def main():
    root, out = sys.argv[1], sys.argv[2]
    entries = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root).replace('\\', '/')
        for name in dirnames:
            rel = name if rel_dir == '.' else rel_dir + '/' + name
            entries.append(('d', 0, rel))
        for name in filenames:
            rel = name if rel_dir == '.' else rel_dir + '/' + name
            entries.append(('f', os.path.getsize(os.path.join(dirpath, name)), rel))
    lines = []
    total_pairs = 0
    file_pairs = 0
    for prefix in PREFIXES:
        buckets = defaultdict(list)
        for kind, size, rel in entries:
            buckets[fnv31((prefix + rel).encode('utf-8'))].append((kind, size, rel))
        for h, items in sorted(buckets.items()):
            if len(items) < 2:
                continue
            items.sort(key=lambda x: x[2])
            for i in range(len(items)):
                for j in range(i + 1, len(items)):
                    a, b = items[i], items[j]
                    total_pairs += 1
                    if a[0] == 'f' and b[0] == 'f':
                        file_pairs += 1
                    lines.append('%s\t%08x\t%s\t%d\t%s\t%s\t%d\t%s' % (prefix, h, a[0], a[1], a[2], b[0], b[1], b[2]))
    with open(out, 'w', encoding='utf-8', newline='\n') as f:
        f.write('# entries=%d pairs=%d file_pairs=%d\n' % (len(entries), total_pairs, file_pairs))
        for l in lines:
            f.write(l + '\n')
        ok = any(l.startswith('/app0/\t') for l in lines)
        f.write('ALL OK\n' if ok else 'FAIL (no /app0/ pair)\n')
    print('entries=%d pairs=%d file_pairs=%d' % (len(entries), total_pairs, file_pairs))
    for l in lines:
        print(l)


if __name__ == '__main__':
    main()
