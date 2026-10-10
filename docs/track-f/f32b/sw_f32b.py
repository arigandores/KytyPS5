# F32b (HPP-734, ROADMAP p.672(g)): independent re-sweep of a list of logs.
# Own line loop (whole file, line by line, no segments); signature definition = F0 method (KEY filter, SKIP_PREFIX,
# norm: header strip, PLT/Stubbed/opcode forms, path, hex and numbers -> X, 200 bytes) re-typed from the spec.
# Also witnesses of the parked rows (Ф3/Б26в/Б26г, Ф4а, Ф25, Ф21, Ф24, Ф22) and frames >= 1 s after the level line.
# Usage: python sw_f32b.py <list.txt> <out.json> [workers]
import os, re, sys, json, lzma, collections, multiprocessing

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
KEY = re.compile(
    rb'FrameTrace|Level has started: |GuestArgs:|Event: quit|'
    rb'GpuHangAbort|ErrorDeviceLost|Unhandled exception|--- Fatal Error ---|--- Error ---|Error: condition|EXIT_IF|'
    rb'hold_exit|game ENDED|\[Vulkan\]\[[EW]\]|not implemented|Stubbed function|BvhLoopCapTrip:|PriorityStall:|'
    rb'AsyncPipelines: skipped draw|MainTaskLate:|'
    rb'[Aa]ssert|[Uu]nsupported|[Ww]arning|WARNING|[Ee]rror|ERROR|[Ff]ailed|FAILED|[Ff]atal|[Uu]nknown|not found|'
    rb'[Ii]nvalid|skipped|skipping|[Ee]xception|[Aa]ccess violation|[Aa]bort|ignoring|mismatch|overflow|not supported|'
    rb'too many|[Uu]nresolved|[Tt]imeout|corrupt|device lost|DEVICE_LOST|[Cc]rash|[Dd]eadlock|[Ss]tall|cannot|Cannot|'
    rb'unable|Unable|[Uu]nexpected|[Uu]nhandled|illegal|[Dd]enied|[Mm]issing|out of memory|exceed|truncat')
SKIP = (b'Read ', b'Open:', b'Close:', b'KernelFstat', b'KernelStat', b'path = ', b'CsPretranslate phase',
        b'ShaderRecompiler', b'CsPretranslate structured', b'CsPretranslate predication', b'CsPretranslate: ready',
        b'loop header=')
R_HDR = re.compile(rb'^\[\d+\]\[\d\d:\d\d:\d\d\.\d+\] ')
R_LIB = re.compile(rb'\[([A-Za-z0-9]+)_v\d+\]')
R_HEX = re.compile(rb'0x[0-9a-fA-F]+|\b[0-9a-fA-F]{8,}\b')
R_NUM = re.compile(rb'\d+')
R_OP = re.compile(rb'family=(\w+) opcode=(0x[0-9a-fA-F]+)')
R_PATH = re.compile(rb'(?:[A-Za-z]:[/\\]\S*?(?:games[/\\]PPSA|_SaveData|_ShaderCache)|/app0/|/download0/|/savedata)[^\r]*')
R_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
R_SKH = re.compile(rb'CsPretranslate: skipped hash=([0-9a-f]{16})')
R_REQ = re.compile(rb'CsPretranslate: (miss|hit) hash=([0-9a-f]{16})')
R_FORK = re.compile(rb'Fork build \S+ ([0-9a-f]{7,})')
R_LATE = re.compile(rb'MainTaskLate: .*?us=(\d+)')
FATAL = (b'--- Fatal Error ---', b'--- Error ---', b'Unhandled exception', b'Unhandled host exception', b'GpuHangAbort',
         b'ErrorDeviceLost', b'There are too many objects', b'Access violation', b'access violation')


def norm(s):
    s = R_HDR.sub(b'', s.strip())
    if s.startswith(b'Relocate: unresolved'):
        m = R_LIB.search(s)
        return b'Relocate: unresolved PLT import patched to stub lib=' + (m.group(1) if m else b'?')
    if b'Stubbed function' in s:
        return R_HEX.sub(b'X', s)[:200]
    m = R_OP.search(s)
    if m and b'not implemented' in s:
        return b'OPCODE_NI family=' + m.group(1) + b' opcode=' + m.group(2)
    s = R_PATH.sub(b'<PATH>', s)
    s = R_HEX.sub(b'X', s)
    s = R_NUM.sub(b'X', s)
    return s[:200]


def scan(path):
    if os.path.exists(STOP):
        return {'path': path, 'err': 'STOP'}
    op = lzma.open if path.endswith('.xz') else open
    sigs = collections.Counter()
    ex = {}
    w = collections.Counter()
    skipped = set()
    req = set()
    fork = None
    lvl_seen = False
    quit_line = None
    fatal_after_quit = 0
    fatal_lines = []
    nlines = 0
    big = []
    try:
        with op(path, 'rb') as fh:
            for line in fh:
                nlines += 1
                if (nlines & 0xFFFFF) == 0 and os.path.exists(LOCK):
                    return {'path': path, 'err': 'LOCK'}
                if fork is None and b'Fork build' in line:
                    m = R_FORK.search(line)
                    if m:
                        fork = m.group(1)[:7].decode()
                if b'CsPretranslate: ' in line:
                    m = R_SKH.search(line)
                    if m:
                        skipped.add(m.group(1))
                    m = R_REQ.search(line)
                    if m:
                        req.add(m.group(2)); w['req_lines'] += 1
                if b'Recvfrom' in line or b'\t len   = ' in line or b'\t addrlen = ' in line:
                    w['sock_block'] += 1
                if b'\t protocol = ' in line:
                    w['sock_create'] += 1
                if b'Read 0 bytes' in line:
                    w['read0'] += 1
                if b'direct read failed' in line:
                    w['direct_read_failed'] += 1
                if b'Controller' in line and b'removed' in line:
                    w['ctrl_removed'] += 1
                if b'06479' in line and b'VUID' in line:
                    w['vuid06479'] += 1
                if b'shader CFG build failed' in line and b'CsPretranslate' not in line:
                    w['cfg_fail_normal'] += 1
                if b'Level has started: ' in line and not line.rstrip().endswith(b'started:'):
                    lvl_seen = True
                if line.startswith(b'Event: quit') and quit_line is None:
                    quit_line = nlines
                for f in FATAL:
                    if f in line:
                        if len(fatal_lines) < 20:
                            fatal_lines.append((nlines, line[:200].decode('latin1')))
                        if quit_line is not None:
                            fatal_after_quit += 1
                        break
                if line.startswith(b'MainTaskLate:'):
                    m = R_LATE.search(line)
                    if m and int(m.group(1)) >= 1000000:
                        w['late_ge1s'] += 1
                if not KEY.search(line):
                    continue
                t = line.lstrip()
                if t.startswith(b'FrameTrace'):
                    m = R_FT.match(t)
                    if m and lvl_seen and int(m.group(2)) >= 1000000 and len(big) < 50:
                        big.append((int(m.group(1)), int(m.group(2))))
                    continue
                if t.startswith(SKIP):
                    continue
                if t.startswith(b'entry_block=') and b'failure=None' in t:
                    continue
                if b'Level has started: ' in t or b'GuestArgs:' in t:
                    continue
                s = norm(t)
                sigs[s] += 1
                if s not in ex:
                    ex[s] = nlines
    except Exception as e:
        return {'path': path, 'err': repr(e)}
    return {'path': path, 'lines': nlines, 'fork': fork,
            'sigs': {k.decode('latin1'): v for k, v in sigs.items()},
            'ex': {k.decode('latin1'): v for k, v in ex.items()},
            'w': dict(w), 'skipped_n': len(skipped), 'req_skipped': sorted(x.decode() for x in (req & skipped)),
            'req_n': len(req), 'quit_line': quit_line, 'fatal_after_quit': fatal_after_quit,
            'fatal_lines': fatal_lines, 'big': big}


if __name__ == '__main__':
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('LOCK/STOP'); sys.exit(3)
    paths = [l.strip() for l in open(sys.argv[1], encoding='utf-8') if l.strip()]
    nw = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    with multiprocessing.Pool(nw) as pool:
        res = pool.map(scan, paths, chunksize=1)
    json.dump(res, open(sys.argv[2], 'w', encoding='utf-8'))
    errs = [r for r in res if 'err' in r]
    print('files', len(res), 'errors', len(errs), [e['err'] for e in errs][:5])
