# F21a (HPP-563, ROADMAP s122 item 462(zh)): block sweep of the game logs for B9 - the calls of the stubs of unresolved
# imports - and for the witnesses of F3, B26v, B26g (normal-path requests of the CS that the speculative translation
# skips).  Form of f20a/sweep_f20a.py: 64 MiB blocks (F21A_BLOCK), only whole lines, the unfinished tail is carried;
# '.xz' goes through 'xz -dc'.  One JSON line per log in <out.jsonl>.  Measurement only: reads logs, writes <out.jsonl>.
# Print sites (KytyPS5 3cc79cb2): src/loader/runtimeLinker.cpp:410 LOGF 'Unresolved import stub called [<idx>]: ...
# symbol=<nid>[<lib>][<module>][Func] type= bind= program=<path>' - at most 1024 lines per process (:405-:406, the
# counter is process-wide), :417 '<bad-record>'; :394 'Late-resolved import:' (a stub call that resolves - no stub
# line); :1158 / :1164 'Relocate: unresolved PLT import | non-PLT function patched to stub'; :1216 '=== Stubbed
# function'; src/graphics/host_gpu/renderer/pipeline/computePretranslation.h:116 / :130 'CsPretranslate: hit | miss
# hash=' (every Take() of the normal path on a NEW translation, pipelineCache.cpp:4002 - not with KYTY_CS_PRETRANSLATE=0
# and not with the graphics debug dump); src/graphics/shader/recompiler/frontend/cfg/ShaderCFG.cpp:44 'shader CFG build
# failed'.
# Fields (all counts are lines of the log, 'line' is a 1-based line number, 'us' is microseconds):
#   sha256 (stored file), sha256_text ('.xz': unpacked text), size, lines, ft_n / ft_us (count / sum dt_us of the
#   'FrameTrace: n=' lines)
#   stub_lines   lines with 'Unresolved import stub called [' ; stub_plain: lines 'Unresolved import stub called: '
#   stub_bad     lines with '<bad-record>' (invariant 0); stub_unparsed (invariant 0)
#   stub_max_idx largest [<idx>] (-1 when none); stub_idx_restart: times the index did not grow by 1 (a second process
#                in one log or a lost line; invariant 0)
#   stub[]       one per (symbol, program base name): symbol, nid, lib, module, program, type, bind, n, first_line,
#                first_idx, last_idx, levels {level name or '' : n} (the level = the last non-empty 'Level has started:')
#   late_n / late[] ('Late-resolved import:' lines / distinct names, at most 50)
#   sfn          lines with '=== Stubbed function'
#   rel_plt / rel_nonplt   lines 'Relocate: unresolved PLT import | non-PLT function patched to stub'
#   rel_libs {lib: [plt lines, non-plt lines, distinct symbols]}
#   levels[]     one per non-empty 'Level has started: <name>' (at most 64, levels_over): level, line, ft_before,
#                frames / sum_us (FrameTrace lines after the level line up to the next non-empty level line),
#                stub_before (stub_lines at the level line)
#   lvl_empty    level lines without a name
#   cs_skipped {hash: class}  ('CsPretranslate: skipped hash=' ; class as f14a_f3.py: RESTRACK, BUDGET,
#                OP_<family>_<opcode>, OTHER; RESTRACK with 'GetBufferResource dword 1 is not a valid runtime value'
#                is RESTRACK_GBR1)
#   cs_req {hash: [miss lines, hit lines, first line, first miss reason]}  ('CsPretranslate: miss|hit hash=')
#   cs_summary   text of the last 'CsPretranslate: summary' line; cs_enq ('enqueue skipped' lines); cs_other
#   cfg_in / cfg_out   lines with 'shader CFG build failed' with / without 'CsPretranslate:' in the line;
#                cfg_out_first [line, text[:200]]
#   b9a_n / b9a_first  lines that start with 'FixB9a:' and the text of the first; fatal ('--- Fatal Error ---')
# Identities (selfcheck_f21a.py): stub_lines == sum(stub[].n) + stub_bad + stub_unparsed; stub_lines <= 1024 and
# stub_max_idx + 1 == stub_lines when stub_idx_restart == 0; sum over a stub's levels == n; ft_n >= sum(levels.frames).
# Resumable: paths already in <out.jsonl> are skipped; stops between files after <budget_s> seconds of wall time and
# when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists.  Prints 'SWEEP COMPLETE' when no file is left.
# Usage: python sweep_f21a.py <list.tsv> <out.jsonl> <budget_s>      (list.tsv: path <TAB> size ...)
import hashlib, json, os, re, subprocess, sys, time

lst, out, budget = sys.argv[1], sys.argv[2], float(sys.argv[3])
LOCK = os.environ.get('F21A_LOCK', 'C:/kyty/SEALED_RUN.lock')
STOP = os.environ.get('F21A_STOP', 'C:/kyty/f287/STOP')
BLOCK = int(os.environ.get('F21A_BLOCK', str(64 << 20)))
t0 = time.time()
TAB = chr(9)
files = []
for l in open(lst, encoding='utf-8'):
    l = l.rstrip(chr(10))
    if l:
        f = l.split(TAB)
        files.append((f[0], int(f[1])))
done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        if l.startswith('{') and l.rstrip().endswith('}'):
            done.add(json.loads(l)['path'])
left = [x for x in files if x[0] not in done]
print('files', len(files), 'done before', len(done), 'left', len(left), 'left GiB %.2f' % (sum(x[1] for x in left) / 2.0 ** 30))

NL = bytes([10])
CR = bytes([13])
FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
FTLIT = b'FrameTrace: n='
LITS = ((1, b'Unresolved import stub called'), (2, b'Level has started:'), (3, b'CsPretranslate: '),
        (4, b'shader CFG build failed'), (5, b'Relocate: unresolved '), (6, b'Late-resolved import:'),
        (7, b'=== Stubbed function'), (8, b'FixB9a:'), (9, b'--- Fatal Error ---'))
STUB = re.compile(rb'Unresolved import stub called \[(\d+)\]: patch_vaddr=\S+ jmprela_index=\d+ symbol=(.*) type=(\w+) bind=(\w+) program=(.*)')
STUBBAD = re.compile(rb'Unresolved import stub called \[(\d+)\]: record_id=\d+ symbol=<bad-record>')
SYM = re.compile(r'^([^\[]*)\[([^\]]*)\]\[([^\]]*)\]')
REL = re.compile(rb'Relocate: unresolved (PLT import|non-PLT function) patched to stub \[\d+\] \[[0-9a-fA-F]+\] <- [0-9a-fA-F]+, (.*?), ')
LATE = re.compile(rb'Late-resolved import: (\S+)')
CSK = re.compile(rb'CsPretranslate: skipped hash=([0-9a-f]{16}) reason=(.*)')
CRQ = re.compile(rb'CsPretranslate: (miss|hit) hash=([0-9a-f]{16})(?: reason=(\S+))?')
OPC = re.compile(rb'family=(\w+) opcode=(0x\w+)')
USER = re.compile(rb'([Uu]sers.)[^/ ' + bytes([92, 92, 9]) + rb']+')


def dec(b):
    return USER.sub(rb'\1<user>', b).decode('utf-8', 'replace')


def klass(reason):
    if b'budget exceeded' in reason:
        return 'BUDGET'
    if b'resource tracking' in reason:
        return 'RESTRACK_GBR1' if b'GetBufferResource dword 1 is not a valid runtime value' in reason else 'RESTRACK'
    k = OPC.search(reason)
    if k:
        return 'OP_' + (k.group(1) + b'_' + k.group(2)).decode()
    return 'OTHER'


def lib_of(sym):
    m = SYM.match(sym)
    return (m.group(1), m.group(2), m.group(3)) if m else (sym, '?', '?')


def sweep(path, size):
    rec = {'path': path, 'size': size, 'xz': path.endswith('.xz'), 'lines': 0, 'ft_n': 0, 'ft_us': 0,
           'stub_lines': 0, 'stub_plain': 0, 'stub_bad': 0, 'stub_unparsed': 0, 'stub_max_idx': -1, 'stub_idx_restart': 0,
           'stub': [], 'late_n': 0, 'late': [], 'sfn': 0, 'rel_plt': 0, 'rel_nonplt': 0, 'rel_libs': {},
           'levels': [], 'levels_over': 0, 'lvl_empty': 0, 'cs_skipped': {}, 'cs_req': {}, 'cs_summary': '', 'cs_enq': 0,
           'cs_other': 0, 'cfg_in': 0, 'cfg_out': 0, 'cfg_out_first': None, 'b9a_n': 0, 'b9a_first': '', 'fatal': 0}
    stub = {}
    relsym = {}
    h = hashlib.sha256()
    h2 = hashlib.sha256()
    proc = None
    if rec['xz']:
        with open(path, 'rb') as fh:
            while True:
                b = fh.read(BLOCK)
                if not b:
                    break
                h.update(b)
        proc = subprocess.Popen(['xz', '-dc', path], stdout=subprocess.PIPE)
        f = proc.stdout
    else:
        f = open(path, 'rb')
    carry = b''
    cur = None
    curname = ''
    while True:
        b = f.read(BLOCK)
        if not b and not carry:
            break
        if proc is None:
            h.update(b)
        else:
            h2.update(b)
        buf = carry + b
        if b:
            cut = buf.rfind(NL)
            if cut == -1:
                carry = buf
                continue
            carry = buf[cut + 1:]
            buf = buf[:cut + 1]
        else:
            carry = b''
            if not buf.endswith(NL):
                buf += NL
        base_line = rec['lines']
        ev = []
        i = buf.find(FTLIT)
        while i != -1:
            if i == 0 or buf[i - 1:i] == NL:
                m = FT.match(buf, i)
                if m:
                    ev.append((i, 0, int(m.group(2))))
            i = buf.find(FTLIT, i + 1)
        for kind, lit in LITS:
            i = buf.find(lit)
            while i != -1:
                ls = buf.rfind(NL, 0, i) + 1
                le = buf.find(NL, i)
                ev.append((ls, kind, le))
                i = buf.find(lit, le)
        ev.sort()
        lc_pos, lc_n = 0, 0
        for e in ev:
            pos, kind = e[0], e[1]
            if kind == 0:
                rec['ft_n'] += 1
                rec['ft_us'] += e[2]
                if cur is not None:
                    cur['frames'] += 1
                    cur['sum_us'] += e[2]
                continue
            lc_n += buf.count(NL, lc_pos, pos)
            lc_pos = pos
            line = base_line + lc_n + 1
            t = buf[pos:e[2]].rstrip(CR)
            if kind == 1:
                if b'Unresolved import stub called [' not in t:
                    rec['stub_plain'] += 1
                    continue
                rec['stub_lines'] += 1
                m = STUB.search(t)
                if not m:
                    mb = STUBBAD.search(t)
                    if mb:
                        rec['stub_bad'] += 1
                        idx = int(mb.group(1))
                    else:
                        rec['stub_unparsed'] += 1
                        continue
                else:
                    idx = int(m.group(1))
                if idx != rec['stub_max_idx'] + 1:
                    rec['stub_idx_restart'] += 1
                rec['stub_max_idx'] = max(rec['stub_max_idx'], idx)
                if not m:
                    continue
                sym = dec(m.group(2))
                prog = dec(m.group(5)).replace(chr(92), '/').rsplit('/', 1)[-1]
                key = (sym, prog)
                s = stub.get(key)
                if s is None:
                    nid, lib, mod = lib_of(sym)
                    s = stub[key] = {'symbol': sym, 'nid': nid, 'lib': lib, 'module': mod, 'program': prog,
                                     'type': m.group(3).decode(), 'bind': m.group(4).decode(), 'n': 0, 'first_line': line,
                                     'first_idx': idx, 'last_idx': idx, 'levels': {}}
                s['n'] += 1
                s['last_idx'] = idx
                s['levels'][curname] = s['levels'].get(curname, 0) + 1
            elif kind == 2:
                name = dec(t.split(b'Level has started:', 1)[1].strip())[:80]
                if not name:
                    rec['lvl_empty'] += 1
                    continue
                curname = name
                cur = {'level': name, 'line': line, 'ft_before': rec['ft_n'], 'frames': 0, 'sum_us': 0,
                       'stub_before': rec['stub_lines']}
                if len(rec['levels']) < 64:
                    rec['levels'].append(cur)
                else:
                    rec['levels_over'] += 1
            elif kind == 3:
                m = CSK.search(t)
                if m:
                    rec['cs_skipped'][m.group(1).decode()] = klass(m.group(2))
                    continue
                m = CRQ.search(t)
                if m:
                    r = rec['cs_req'].setdefault(m.group(2).decode(), [0, 0, line, ''])
                    if m.group(1) == b'miss':
                        r[0] += 1
                        if not r[3]:
                            r[3] = (m.group(3) or b'').decode()
                    else:
                        r[1] += 1
                    continue
                if b'CsPretranslate: summary' in t:
                    rec['cs_summary'] = dec(t.split(b'CsPretranslate: ', 1)[1])[:300]
                elif b'CsPretranslate: enqueue skipped' in t:
                    rec['cs_enq'] += 1
                else:
                    rec['cs_other'] += 1
            elif kind == 4:
                if b'CsPretranslate:' in t:
                    rec['cfg_in'] += 1
                else:
                    rec['cfg_out'] += 1
                    if rec['cfg_out_first'] is None:
                        rec['cfg_out_first'] = [line, dec(t)[:200]]
            elif kind == 5:
                m = REL.search(t)
                if not m:
                    continue
                plt = m.group(1) == b'PLT import'
                rec['rel_plt' if plt else 'rel_nonplt'] += 1
                sym = dec(m.group(2))
                lib = lib_of(sym)[1]
                r = rec['rel_libs'].setdefault(lib, [0, 0, 0])
                r[0 if plt else 1] += 1
                relsym.setdefault(lib, set()).add(sym)
            elif kind == 6:
                rec['late_n'] += 1
                m = LATE.search(t)
                if m and len(rec['late']) < 50:
                    nm = dec(m.group(1))
                    if nm not in rec['late']:
                        rec['late'].append(nm)
            elif kind == 7:
                rec['sfn'] += 1
            elif kind == 8:
                if t.startswith(b'FixB9a:'):
                    rec['b9a_n'] += 1
                    if not rec['b9a_first']:
                        rec['b9a_first'] = dec(t)[:120]
            elif kind == 9:
                rec['fatal'] += 1
        rec['lines'] += buf.count(NL)
        if not b:
            break
    if proc is None:
        f.close()
    else:
        proc.wait()
        rec['xz_rc'] = proc.returncode
        rec['sha256_text'] = h2.hexdigest()
    rec['sha256'] = h.hexdigest()
    for lib, s in relsym.items():
        rec['rel_libs'][lib][2] = len(s)
    rec['stub'] = sorted(stub.values(), key=lambda s: s['first_line'])
    return rec


n = 0
for p, s in left:
    if os.path.exists(LOCK) or os.path.exists(STOP):
        print('STOPPED: lock or STOP present')
        sys.exit(3)
    if time.time() - t0 > budget:
        break
    if not os.path.exists(p):
        rec = {'path': p, 'size': s, 'missing': True}
    else:
        rec = sweep(p, s)
    with open(out, 'ab') as fo:
        fo.write((json.dumps(rec, ensure_ascii=True, sort_keys=True) + chr(10)).encode('ascii'))
    n += 1
print('swept now', n, 'wall %.1f s' % (time.time() - t0))
if n == len(left):
    print('SWEEP COMPLETE')
