"""Track F link F29a (HPP-699, ROADMAP s122 item 638(g)(3)): census of the guest GPU mappings that the default log WRITES,
and of the pairs of distinct mapped ranges that share one 4 MiB tracking region (the layout of row B12).

The mapped set of RenderContext (m_mapped_ranges, a RangeSet: ranges that overlap or touch merge,
src/graphics/host_gpu/rangeSet.h) is fed by MapGpuRange / UnmapGpuRange of src/kernel/memory.cpp. The default log has no
PRINT_NAME header lines, so a block is recognised only by its exact consecutive field lines (one LOGF each):
  MAP_DIRECT   KernelMapDirectMemory: "\t in_addr  = 0x", "\t out_addr = 0x", "\t dmem     = 0x", "\t size     = 0x";
               a map when out_addr != 0 and the first of "\t [Ok]" / "\t [Fail]" in the next 64 lines is "\t [Ok]"
  MAP_FLEX     flexible / pooled map: "\t in_addr  = 0x", "\t out_addr = 0x", "\t size     = <decimal>" (logged after
               every failure return of its function, so a map)
  MAP_COMMIT   KernelMemoryPoolCommit: "\t addr  = 0x", "\t len   = 0x", "\t type  = 0x" (a map; a commit that fails
               after the log is not told apart - an upper bound of the maps)
  UNMAP_DECOM  KernelMemoryPoolDecommit: "\t addr  = 0x", "\t len   = 0x", "\t flags = 0x" (3 lines, no type line)
  MAP_PRT      KernelSetPrtAperture: "\t index = n", "\t addr  = 0x", "\t len   = 0x" (KernelGetPrtAperture prints %p)
  AMBIG_START  "\t start = 0x", "\t len   = 0x": KernelMunmap (an unmap of a virtual range) OR KernelReleaseDirectMemory /
               KernelCheckedReleaseDirectMemory (a release of DIRECT memory offsets, whose GPU alias is unmapped by
               ReleaseDirectMemoryInternal without a line) - counted, NOT applied.
NO line at all: AllocateGuestRuntimeMemory (program and runtime memory), the alias remap of ReleaseDirectMemoryInternal,
ReplaceFixedRangeWithReserved, FreeGuestMemory, the pooled-backing unmaps. Registered buffers (BufferCache::m_buffers)
are not logged. So: a shared region found here is a CANDIDATE of the layout (the hole also needs a registered buffer in
both ranges); none found is NOT a proof that the game never gives the layout.

    python maps_f29a.py <out.txt> <log> [<log> ...]
Per log: blocks by kind, the ranges at the end, every pair of distinct ranges sharing a region the first time it appears
(region, the two ranges, gap, line), and a total line. ASCII code.
"""
import sys

R = 4 << 20


class RangeSet:
    """The arithmetic of src/graphics/host_gpu/rangeSet.h: Add merges ranges that overlap or touch, Subtract splits."""

    def __init__(self):
        self.r = []  # sorted [begin, end)

    def add(self, a, s):
        e = a + s
        out = []
        for b0, e0 in self.r:
            if e0 < a or b0 > e:
                out.append((b0, e0))
            else:
                a, e = min(a, b0), max(e, e0)
        out.append((a, e))
        self.r = sorted(out)

    def sub(self, a, s):
        e = a + s
        out = []
        for b0, e0 in self.r:
            if e0 <= a or b0 >= e:
                out.append((b0, e0))
                continue
            if b0 < a:
                out.append((b0, a))
            if e0 > e:
                out.append((e, e0))
        self.r = sorted(out)


def gpu_range(a, s):
    # IsGpuAddressRange of memory.cpp: vaddr != 0, size != 0, below 1 << 40
    lim = 1 << 40
    return a != 0 and s != 0 and a < lim and s < lim - a


def shared_pairs(rs):
    pairs = []
    r = rs.r
    for i in range(1, len(r)):
        pb, pe = r[i - 1]
        b, e = r[i]
        if (pe - 1) // R == b // R:
            pairs.append((b // R, (pb, pe), (b, e)))
    return pairs


def val(line, prefix):
    return line[len(prefix):].strip().decode('ascii', 'replace')


def census(path, out):
    with open(path, 'rb') as f:
        L = f.read().split(b'\n')
    kinds = dict.fromkeys(('MAP_DIRECT', 'MAP_DIRECT_FAIL', 'MAP_FLEX', 'MAP_COMMIT', 'UNMAP_DECOM', 'MAP_PRT',
                           'AMBIG_START', 'GPU_NOACCESS_FLEX'), 0)
    rs = RangeSet()
    seen = set()
    first = []
    n = len(L)
    for i in range(n - 3):
        l0 = L[i]
        if not l0.startswith(b'\t '):
            continue
        act = None
        if l0.startswith(b'\t in_addr  = 0x') and L[i + 1].startswith(b'\t out_addr = 0x'):
            a = int(val(L[i + 1], b'\t out_addr = '), 16)
            if L[i + 2].startswith(b'\t dmem     = 0x') and L[i + 3].startswith(b'\t size     = 0x'):
                s = int(val(L[i + 3], b'\t size     = '), 16)
                ok = None
                for k in range(i + 4, min(n, i + 68)):
                    if L[k].startswith(b'\t [Ok]'):
                        ok = True
                        break
                    if L[k].startswith(b'\t [Fail]'):
                        ok = False
                        break
                if ok and a != 0:
                    kinds['MAP_DIRECT'] += 1
                    act = ('map', a, s)
                else:
                    kinds['MAP_DIRECT_FAIL'] += 1
            elif L[i + 2].startswith(b'\t size     = ') and val(L[i + 2], b'\t size     = ').isdigit():
                s = int(val(L[i + 2], b'\t size     = '))
                kinds['MAP_FLEX'] += 1
                if any(L[k].startswith(b'\t gpu_mode = NoAccess') for k in range(i + 3, min(n, i + 8))):
                    kinds['GPU_NOACCESS_FLEX'] += 1
                act = ('map', a, s)
        elif l0.startswith(b'\t addr  = 0x') and L[i + 1].startswith(b'\t len   = 0x') and not (
                i > 0 and L[i - 1].startswith(b'\t index = ')):
            a = int(val(l0, b'\t addr  = '), 16)
            s = int(val(L[i + 1], b'\t len   = '), 16)
            if L[i + 2].startswith(b'\t type  = 0x'):
                kinds['MAP_COMMIT'] += 1
                act = ('map', a, s)
            elif L[i + 2].startswith(b'\t flags = 0x') and not L[i + 3].startswith(b'\t '):
                kinds['UNMAP_DECOM'] += 1
                act = ('unmap', a, s)
        elif l0.startswith(b'\t index = ') and L[i + 1].startswith(b'\t addr  = 0x') and L[i + 2].startswith(
                b'\t len   = 0x'):
            kinds['MAP_PRT'] += 1
            act = ('map', int(val(L[i + 1], b'\t addr  = '), 16), int(val(L[i + 2], b'\t len   = '), 16))
        elif l0.startswith(b'\t start = 0x') and L[i + 1].startswith(b'\t len   = 0x'):
            kinds['AMBIG_START'] += 1
        if act is None or not gpu_range(act[1], act[2]):
            continue
        if act[0] == 'map':
            rs.add(act[1], act[2])
        else:
            rs.sub(act[1], act[2])
        for p in shared_pairs(rs):
            if p not in seen:
                seen.add(p)
                first.append((i + 1, p))
    out.append('LOG %s lines %d' % (path, n))
    out.append('  blocks ' + ' '.join('%s=%d' % kv for kv in kinds.items()))
    out.append('  ranges at end %d: %s' % (len(rs.r), ' '.join('[0x%x,0x%x)' % x for x in rs.r)))
    for ln, (reg, p1, p2) in first:
        out.append('  SHARED region 0x%x (base 0x%x) line %d: [0x%x,0x%x) and [0x%x,0x%x) gap 0x%x' %
                   (reg, reg * R, ln, p1[0], p1[1], p2[0], p2[1], p2[0] - p1[1]))
    out.append('  shared pairs (distinct, ever) %d; at end %d' % (len(first), len(shared_pairs(rs))))
    return len(first), len(shared_pairs(rs)), kinds


def main(argv):
    out = []
    logs = argv[1:]
    tot = tot_end = with_pair = 0
    agg = {}
    for p in logs:
        a, b, kinds = census(p, out)
        tot += a
        tot_end += b
        with_pair += 1 if a else 0
        for k, v in kinds.items():
            agg[k] = agg.get(k, 0) + v
        sys.stdout.write(out[-1] + '\n')
        sys.stdout.flush()
    out.append('BLOCKS ' + ' '.join('%s=%d' % kv for kv in agg.items()))
    out.append('TOTAL logs %d, logs with a shared pair %d, distinct pairs %d, pairs at end %d' %
               (len(logs), with_pair, tot, tot_end))
    open(argv[0], 'w', encoding='ascii', newline='\n').write('\n'.join(out) + '\n')
    print(out[-2])
    print(out[-1])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
