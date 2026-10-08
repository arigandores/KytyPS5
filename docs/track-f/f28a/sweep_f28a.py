# F28a (HPP-698, ROADMAP s122 item 638(v)(2)-(3)): sweep of the game logs of list_f28a.tsv (plain files; the xz logs are
# sessions <= 139, before dac02fb9, outside the count - their limiter lines are the register row F0, reference only).
# One regex pass per log over an mmap, the kinds:
#   TC   'Shader translation cache: ' - the variant directory (fixb1b in it <=> KYTY_FIX_B1B in effect, shaderTranslationCache.cpp)
#   CAP  'BvhLoopCap: '               - startup line 'cap=<n> token=<t> default_slot0=<s>' (faultManager.cpp) and the translation
#                                       line 'shader=0x<h> loops=<n> cap=<c> slot=<s>' / 'UNCAPPED' (spirvEmitterProgram.cpp)
#   TRIP 'BvhLoopCapTrip:'            - trip / near readback line (faultManager.cpp; first 64 events of a process)
#   BLT  'bl_trip=[1-9]', BLN 'bl_near=[1-9]' - non-zero FrameTrace counters (every frame)
#   P380 '380bb9d636390bae'           - any other line naming the program (CsPretranslate, dumps, ...)
#   HANG 'GpuHangAbort:', 'ErrorDeviceLost'; CRASH 'Unhandled exception:', '--- Fatal Error ---', '--- Error ---'
#        (death markers of sc146.py, item 128(g) / 218(d)(2))
#   LVL  'Level has started: '        - entry of a scene; QUIT 'Event: quit'
# Every marker is attributed to the entry in effect (the last LVL line before it; 'pre' before the first). Hold of an entry =
# time of the last '[tid][HH:MM:SS.fff]' header before the next LVL line (or before the end) - that before the entry line.
# Output: one JSON line per log in <out.jsonl>; logs already in the output are skipped (resume). Lock and STOP are checked
# before every log (rule 27): found -> the pool stops, exit 5 / 4.
# usage: python sweep_f28a.py <list.tsv> <out.jsonl> <workers>
import json, mmap, os, re, sys
from multiprocessing import Pool

LOCK = 'C:/kyty/SEALED_RUN.lock'
STOP = 'C:/kyty/f287/STOP'
PAT = re.compile(rb'BvhLoopCapTrip:|BvhLoopCap: |GpuHangAbort:|ErrorDeviceLost|Unhandled exception:|--- Fatal Error ---|'
                 rb'--- Error ---|380bb9d636390bae|Level has started: |Shader translation cache: |Event: quit|'
                 rb'bl_trip=[1-9]|bl_near=[1-9]')
HDR = re.compile(rb'(?m)^\[\d+\]\[(\d\d):(\d\d):(\d\d\.\d\d\d)\] ')
KIND = {b'BvhLoopCapTrip:': 'TRIP', b'BvhLoopCap: ': 'CAP', b'GpuHangAbort:': 'HANG', b'ErrorDeviceLost': 'HANG',
        b'Unhandled exception:': 'CRASH', b'--- Fatal Error ---': 'CRASH', b'--- Error ---': 'CRASH',
        b'380bb9d636390bae': 'P380', b'Level has started: ': 'LVL', b'Shader translation cache: ': 'TC',
        b'Event: quit': 'QUIT'}
KEEP_LINES = ('TRIP', 'CAP', 'HANG', 'CRASH', 'P380', 'LVL', 'TC', 'QUIT')


def hdr_before(m, pos):
    w = 1 << 20
    while True:
        lo = max(0, pos - w)
        last = None
        for x in HDR.finditer(m, lo, pos):
            last = x
        if last is not None:
            h, mi, s = last.groups()
            return int(h) * 3600 + int(mi) * 60 + float(s)
        if lo == 0:
            return None
        w <<= 2


def line_at(m, pos):
    a = m.rfind(b'\n', 0, pos) + 1
    b = m.find(b'\n', pos)
    if b < 0:
        b = len(m)
    return m[a:min(b, a + 400)].decode('latin-1').rstrip('\r')


def sweep(row):
    path, size, mtime, root, js = row
    if os.path.exists(LOCK):
        return {'halt': 'LOCK'}
    if os.path.exists(STOP):
        return {'halt': 'STOP'}
    res = {'path': path, 'size': size, 'mtime': mtime, 'json': js}
    if size == 0:
        res['empty'] = True
        return res
    with open(path, 'rb') as f:
        m = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        ev = []
        for x in PAT.finditer(m):
            s = x.group(0)
            k = KIND.get(s) or ('BLT' if s.startswith(b'bl_trip') else 'BLN')
            ev.append((x.start(), k))
        lines = {}
        entries = []
        for pos, k in ev:
            if k in KEEP_LINES:
                ln = line_at(m, pos)
                if k == 'P380' and ('BvhLoopCap: ' in ln):
                    continue  # the same line was taken as CAP
                lines.setdefault(k, []).append((pos, ln))
            if k == 'LVL':
                entries.append(pos)
        t_end = hdr_before(m, len(m))
        ent = []
        for i, pos in enumerate(entries):
            nxt = entries[i + 1] if i + 1 < len(entries) else len(m)
            t0 = hdr_before(m, pos)
            t1 = hdr_before(m, nxt)
            hold = None
            if t0 is not None and t1 is not None:
                hold = t1 - t0
                if hold < 0:
                    hold += 86400
            ent.append({'pos': pos, 'line': line_at(m, pos), 'hold_s': hold})
        m.close()
    # attribution
    def entry_of(pos):
        j = -1
        for i, e in enumerate(ent):
            if e['pos'] <= pos:
                j = i
            else:
                break
        return j
    counts = {}
    for pos, k in ev:
        j = entry_of(pos)
        counts.setdefault(k, {})
        counts[k][str(j)] = counts[k].get(str(j), 0) + 1
    res['entries'] = ent
    res['counts'] = counts
    res['lines'] = {k: [(entry_of(p), l) for p, l in v[:80]] for k, v in lines.items()}
    res['lines_total'] = {k: len(v) for k, v in lines.items()}
    res['t_end'] = t_end
    if js and js != '-' and ';' not in js and os.path.isfile(js) and js.endswith('.json'):
        try:
            d = json.load(open(js, encoding='utf-8'))
            res['binary_sha256'] = d.get('binary_sha256') or d.get('exe_sha256') or d.get('binary')
            env = d.get('env')
            env = env if isinstance(env, str) else json.dumps(env)
            res['env_cap'] = re.findall(r"KYTY_BVH_LOOP_CAP[A-Z_]*'?\"?\s*[:=]\s*'?\"?([^'\",}]*)", env or '')
            res['env_b1b'] = re.findall(r"KYTY_FIX_B1B'?\"?\s*[:=]\s*'?\"?([^'\",}]*)", env or '')
            res['env_hang'] = re.findall(r"KYTY_GPU_HANG_ABORT_S'?\"?\s*[:=]\s*'?\"?([^'\",}]*)", env or '')
            res['guest_args'] = d.get('guest_args')
            res['hold_s_json'] = d.get('hold_s')
            res['started'] = d.get('started')
        except Exception as e:  # noqa
            res['json_error'] = repr(e)[:200]
    return res


def main():
    lst, out, workers = sys.argv[1], sys.argv[2], int(sys.argv[3])
    rows = []
    for line in open(lst, encoding='utf-8'):
        p, s, mt, r, js = line.rstrip('\n').split('\t')
        if p.endswith('.xz'):
            continue
        rows.append((p, int(s), int(mt), r, js))
    done = set()
    if os.path.exists(out):
        for line in open(out, encoding='utf-8'):
            done.add(json.loads(line)['path'])
    todo = [r for r in rows if r[0] not in done]
    print('plain logs', len(rows), 'done', len(done), 'todo', len(todo), flush=True)
    halted = None
    with Pool(workers) as pool, open(out, 'a', encoding='utf-8', newline='\n') as f:
        for res in pool.imap_unordered(sweep, todo):
            if 'halt' in res:
                halted = res['halt']
                pool.terminate()
                break
            f.write(json.dumps(res) + '\n')
            f.flush()
    if halted:
        print('HALT', halted)
        sys.exit(5 if halted == 'LOCK' else 4)
    print('ALL DONE')


if __name__ == '__main__':
    main()
