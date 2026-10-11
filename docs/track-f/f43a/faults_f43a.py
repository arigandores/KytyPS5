# F43a (HPP-783, ROADMAP s122 item 694(e)(1)(2)): census of fault-buffer passes in the logs of the course line.
# Population: every emulator log under C:/kyty (txt and .xz, game folder, build and tools excluded) whose line
# '  version: Fork build <owner>/<repo> <hash>' (first 4000 lines) names a course-line build (COURSE below: the installed
# binaries of the CLAUDE.md state line, 9235a7ac .. FS12; hashes as in docs/track-f/f32a/binmap.tsv plus 730ed40 FS12 and
# 4fc501f 9235a7ac). Every line 'Accessed non-GPU cached memory at 0x<addr>' is one entry read by the deferred operation of
# FaultManager::ProcessFaultBuffer (faultManager.cpp:216 at 730ed40a). Passes: method of F41a faults_f41a.py - a gap of
# > GAP log lines starts a new pass; GAP 20 (F41a) and 200 (sensitivity: other threads' lines inside one pass).
# Per log: sha256, build, lines, fault lines (total), max pass size at GAP 20 and 200, passes > 1023 at both, and the
# witness lines of a read past the area (address 0, not a multiple of 16 KiB, or >= 2^40 - a parser entry is always a
# multiple of 16 KiB below 2^40). A log whose TOTAL fault lines are <= 1023 cannot hold a pass > 1023 [c].
# Output: TSV rows to <out.tsv>, summary to stdout, last line ALL OK when every listed log was read to its end.
# Usage: python faults_f43a.py <out.tsv> [--workers N] [--list-only | --from <list.tsv> [--part i/N]]
import hashlib, lzma, os, sys, multiprocessing

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
ROOT = 'C:/kyty'
SKIP_DIRS = {'games', 'build', 'tools', '.git', 'scrub', '_ShaderCache', '_ShaderSeeds', '_RenderDoc', '_Shaders',
             'node_modules', '__pycache__', 'wt', 'wtS'}
COURSE = {
    b'4fc501f': '9235a7ac', b'95eec77': 'dac02fb9', b'9c9d86a': 'FS2', b'4414e23': 'P23', b'd515b90': 'FS3',
    b'3d0e46d': 'FS4', b'0e72bc1': 'FS5', b'4d9e8ab': 'S12', b'3904522': 'FS6', b'd6ee2dc': 'FS7', b'302347b': 'FS8',
    b'0005e11': 'S18', b'11164d7': 'FS9', b'dc5d471': 'FS10', b'ee9632b': 'FS11', b'730ed40': 'FS12',
}
NEEDLE = b'Accessed non-GPU cached memory at 0x'
VER = b'  version: Fork build '
GAPS = (20, 200)
PAGE = 1 << 14
TOP = 1 << 40
TAB = chr(9)
CHUNK = 16 << 20
NL = chr(10)


def gate():
    if os.path.exists(STOP):
        os._exit(4)
    if os.path.exists(LOCK):
        os._exit(3)


def opener(path):
    return lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')


def build_of(path):
    try:
        with opener(path) as f:
            for i, l in enumerate(f):
                if l.startswith(VER):
                    h = l[len(VER):].split()
                    return h[-1][:7] if h else b'?'
                if i >= 4000:
                    return None
    except (OSError, EOFError, lzma.LZMAError):
        return None
    return None


def candidates():
    out = []
    for dp, dns, fns in os.walk(ROOT):
        gate()
        dns[:] = [d for d in dns if d not in SKIP_DIRS and not d.startswith('.')]
        for fn in fns:
            low = fn.lower()
            if not (low.endswith('.txt') or low.endswith('.txt.xz')):
                continue
            if not (low.startswith('log') or '_kyty' in low or 'log_' in low):
                continue
            out.append(os.path.join(dp, fn).replace(os.sep, '/'))
    return sorted(out)


def probe(path):
    gate()
    b = build_of(path)
    return path, b


def scan(arg):
    path, build = arg
    gate()
    h = hashlib.sha256()
    n = 0
    lvl = None
    total = 0
    wit_zero = wit_unal = wit_top = 0
    cur = {g: 0 for g in GAPS}
    last = {g: -10 ** 9 for g in GAPS}
    mx = {g: 0 for g in GAPS}
    over = {g: 0 for g in GAPS}
    npass = {g: 0 for g in GAPS}
    carry = b''
    with opener(path) as f:
        while True:
            gate()
            blk = f.read(CHUNK)
            if blk:
                h.update(blk)
            buf = carry + blk
            if not blk:
                if not buf:
                    break
                carry = b''
            else:
                k = buf.rfind(b'\n')
                if k < 0:
                    carry = buf
                    continue
                carry = buf[k + 1:]
                buf = buf[:k + 1]
            if lvl is None:
                q = buf.find(b'Level has started')
                if q >= 0:
                    lvl = n + buf.count(b'\n', 0, q) + 1
            pos, base, ln = 0, 0, n
            while True:
                q = buf.find(NEEDLE, pos)
                if q < 0:
                    break
                ln += buf.count(b'\n', base, q)
                base = q
                line_no = ln + 1
                s = q + len(NEEDLE)
                try:
                    a = int(buf[s:s + 16], 16)
                except ValueError:
                    a = -1
                total += 1
                if a == 0:
                    wit_zero += 1
                elif a < 0 or a >= TOP:
                    wit_top += 1
                elif a % PAGE:
                    wit_unal += 1
                for g in GAPS:
                    if line_no - last[g] > g:
                        if cur[g] > 1023:
                            over[g] += 1
                        if cur[g]:
                            npass[g] += 1
                        mx[g] = max(mx[g], cur[g])
                        cur[g] = 0
                    cur[g] += 1
                    last[g] = line_no
                pos = s
            n += buf.count(b'\n')
    for g in GAPS:
        if cur[g] > 1023:
            over[g] += 1
        if cur[g]:
            npass[g] += 1
        mx[g] = max(mx[g], cur[g])
    return (path, COURSE.get(build, build.decode('ascii', 'replace')), h.hexdigest(), n, lvl, total, npass[20], mx[20],
            over[20], npass[200], mx[200], over[200], wit_zero, wit_unal, wit_top)


def main():
    gate()
    out = sys.argv[1]
    workers = int(sys.argv[sys.argv.index('--workers') + 1]) if '--workers' in sys.argv else 4
    if '--from' in sys.argv:
        # list written by --list-only: path, build name, size; --part i/N takes rows i, i+N, ... of the list sorted by size
        rows = [l.rstrip(NL).split(TAB) for l in open(sys.argv[sys.argv.index('--from') + 1], encoding='utf-8') if l.strip()]
        rows.sort(key=lambda r: (-int(r[2]), r[0]))
        if '--part' in sys.argv:
            i, k = (int(x) for x in sys.argv[sys.argv.index('--part') + 1].split('/'))
            rows = rows[i::k]
        name2hash = {v: k for k, v in COURSE.items()}
        cands = [r[0] for r in rows]
        probes = [(r[0], name2hash[r[1]]) for r in rows]
    else:
        cands = candidates()
        with multiprocessing.Pool(workers) as pool:
            probes = pool.map(probe, cands, chunksize=8)
    builds = {}
    for p, b in probes:
        builds[b] = builds.get(b, 0) + 1
    course = [(p, b) for p, b in probes if b in COURSE]
    other = sum(v for k, v in builds.items() if k is not None and k not in COURSE)
    print('candidates', len(cands), 'with_version', sum(v for k, v in builds.items() if k is not None),
          'course', len(course), 'other_builds', other, 'no_version', builds.get(None, 0))
    for k in sorted(COURSE, key=lambda x: COURSE[x]):
        print('  build', COURSE[k], k.decode(), 'logs', sum(1 for _, b in course if b == k))
    if '--list-only' in sys.argv:
        with open(out, 'w', encoding='utf-8', newline=NL) as o:
            for p, b in course:
                o.write(p + TAB + COURSE[b] + TAB + str(os.path.getsize(p)) + NL)
        print('bytes', sum(os.path.getsize(p) for p, _ in course))
        print('ALL OK')
        return
    with multiprocessing.Pool(workers) as pool:
        rows = pool.map(scan, course, chunksize=1)
    rows.sort()
    hdr = ['path', 'build', 'sha256', 'lines', 'level_line', 'fault_lines', 'passes20', 'max20', 'over20', 'passes200',
           'max200', 'over200', 'wit_zero', 'wit_unaligned', 'wit_top']
    with open(out, 'w', encoding='utf-8', newline=NL) as o:
        o.write(TAB.join(hdr) + NL)
        for r in rows:
            o.write(TAB.join(str(x) for x in r) + NL)
    with_f = [r for r in rows if r[5] > 0]
    print('logs_read', len(rows), 'logs_with_fault_lines', len(with_f), 'fault_lines_total', sum(r[5] for r in rows))
    print('max_total_per_log', max((r[5] for r in rows), default=0), 'logs_total_gt_1023', sum(1 for r in rows if r[5] > 1023))
    print('max_pass_gap20', max((r[7] for r in rows), default=0), 'max_pass_gap200', max((r[10] for r in rows), default=0))
    print('passes_gt_1023_gap20', sum(r[8] for r in rows), 'passes_gt_1023_gap200', sum(r[11] for r in rows))
    print('witness_zero', sum(r[12] for r in rows), 'witness_unaligned', sum(r[13] for r in rows),
          'witness_top', sum(r[14] for r in rows))
    for b in sorted(set(r[1] for r in rows)):
        rb = [r for r in rows if r[1] == b]
        print('  build', b, 'logs', len(rb), 'with_faults', sum(1 for r in rb if r[5] > 0), 'max_pass20',
              max(r[7] for r in rb), 'max_pass200', max(r[10] for r in rb), 'max_total', max(r[5] for r in rb))
    top = sorted(rows, key=lambda r: (-r[10], -r[5]))[:10]
    for r in top:
        print('  top', r[0], r[1], 'total', r[5], 'max20', r[7], 'max200', r[10], 'passes20', r[6])
    print('ALL OK' if len(rows) == len(course) and rows else 'FAIL')


if __name__ == '__main__':
    main()
