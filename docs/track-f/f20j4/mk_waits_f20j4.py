#!/usr/bin/env python3
"""F20j4 (HPP-652; ROADMAP s122 item 581(v)(1), (d)): makes waits_f20j4.py from waits_f20j3.py - the F20j3 inventory
plus the loop-cover rule (part E, RC1 of F20k3) and the kind emu_join (item 581(v)(5)). Exact-text replacements, each
must hit exactly once; LF out.

    python mk_waits_f20j4.py <waits_f20j3.py> <waits_f20j4.py>
"""
import sys

src, dst = sys.argv[1], sys.argv[2]
t = open(src, encoding='utf-8').read().replace('\r\n', '\n')

REPL = [
    ('''  D. spin locks - TrackingSpinLock, SpinGuard, ApplyGuard: W:spin (verified).
''', '''  D. spin locks - TrackingSpinLock, SpinGuard, ApplyGuard: W:spin (verified).
  E. F20j4 (HPP-652; ROADMAP s122 item 581(v)(1), RC1 of F20k3) - the loop cover of every F20j3+ W mark (BeginW /
     BeginWReg of a kind from emu_mutex on, outside common/diagB32*): a mark begun inside the body of a loop of its
     function ends every pass - the -w record (>= 10 ms) would be per slice, not per wait (item 574(g)(1)). ok only if
     (a) no loop of the function encloses the mark, or (b) the mark is begun under a test !<mark>.Active() (on its line
     or the 3 lines above) and its Mark object is declared above every enclosing loop (one mark over the whole loop),
     or (c) the (file, kind) is a service loop of the table SERVICE (an idle wait of a service thread: one mark per idle
     period by design). Anything else - LOOP_SLICE, FAILED.
''')
    ,
    ('''#!/usr/bin/env python3
"""F20j3 (HPP-646; ROADMAP s122 item 574(g)(1)): the inventory''',
     '''#!/usr/bin/env python3
# F20j4 (HPP-652; ROADMAP s122 item 581(v)(1), (5)): copy of waits_f20j3.py with part E (loop cover) and emu_join.
"""F20j3 (HPP-646; ROADMAP s122 item 574(g)(1)): the inventory'''),
    ("""    ('common/threads.cpp', 'Thread::Join', None, 'MARK:join', ''),""",
     """    ('common/threads.cpp', 'Thread::Join', None, 'MARK:emu_join', 'F20j4 item 581(v)(5): an emulator thread (PthreadJoin keeps join)'),"""),
    ("""         'gpu_regmem': 'GpuRegmem'}""",
     """         'gpu_regmem': 'GpuRegmem', 'emu_join': 'EmuJoin'}"""),
    ("""summary = {}
for r in rows:""",
     """# ---- E: loop cover (F20j4, item 581(v)(1), RC1 of F20k3)
OLD_KINDS = {'Cond', 'Mutex', 'Sem', 'PSem', 'Evf', 'Eq', 'Sleep', 'GpuIdle', 'GpuRegmem'}
# (file, kind, reason): an idle wait of a service thread - one mark per idle period of its service loop, by design.
SERVICE = [
    ('graphics/host_gpu/renderer/commandRecorder.cpp', 'RecIdle', 'record thread idle - one mark per idle period'),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', 'ASubIdle', 'async submitter idle - one mark per idle period'),
    ('graphics/host_gpu/renderer/commandScheduler.cpp', 'OpsIdle', 'priority operations thread idle - one mark per idle period'),
    ('graphics/presentation/videoOut.cpp', 'VoPace', 'present thread pacing - one mark per frame'),
    ('graphics/presentation/window/window.cpp', 'MainIdle', 'main loop SDL event wait - one mark per wait'),
]
MARK_RX = re.compile(r'\\b(\\w+)\\s*(?:\\.|->)\\s*(BeginWReg|BeginW)\\s*\\(\\s*(?:Common::)?(?:DiagB32::)?Wait::(\\w+)')
LOOP_RX = re.compile(r'^\\s*(?:\\}\\s*)?(?:for|while)\\s*\\(|^\\s*do\\b')


def enclosing_loops(lines, start, i):
    \"\"\"Line indexes of the loop headers whose block encloses line i, inside the function that starts at start.\"\"\"
    depth = 0
    out = []
    for j in range(i - 1, max(start, i - 600) - 1, -1):
        s = strip_comment(lines[j])
        depth += s.count('}') - s.count('{')
        if depth < 0:
            depth = 0
            hdr = j
            if s.strip() == '{' and j > 0:
                hdr = j - 1
            if LOOP_RX.match(strip_comment(lines[hdr])):
                out.append(hdr)
    return out


n_e = 0
for p, lines in TEXT.items():
    if p.startswith('common/diagB32'):
        continue
    for i, l in enumerate(lines):
        m = MARK_RX.search(strip_comment(l))
        if not m or m.group(3) in OLD_KINDS:
            continue
        n_e += 1
        name, kind = m.group(1), m.group(3)
        func, start = enclosing(lines, i)
        loops = enclosing_loops(lines, start, i)
        decl = next((k for k in range(i, max(start, i - 600) - 1, -1)
                     if re.search(r'\\bMark\\s+' + re.escape(name) + r'\\s*;', strip_comment(lines[k]))), None)
        guarded = any(('!' + name + '.Active()') in strip_comment(lines[k]).replace(' ', '') for k in range(max(0, i - 3), i + 1))
        svc = next((r for f, k, r in SERVICE if f == p and k == kind), None)
        where = ','.join('L%d' % (x + 1) for x in sorted(set(loops)))
        if not loops:
            st, ok, det = 'COVER:noloop', True, ''
        elif svc is not None:
            st, ok, det = 'COVER:service', True, svc + ' (loops ' + where + ')'
        elif guarded and decl is not None and decl < min(loops):
            st, ok, det = 'COVER:loop', True, 'Mark %s at L%d above the loops %s, begun under !%s.Active()' % (name, decl + 1, where, name)
        else:
            st, ok, det = 'LOOP_SLICE', False, 'mark %s inside the loops %s: guarded=%s decl=%s' % (
                name, where, guarded, 'L%d' % (decl + 1) if decl is not None else '-')
        if not ok:
            bad += 1
        rows.append(('E', p, i + 1, func, st + ':' + kind, 'ok' if ok else 'FAIL', det, l.strip()[:120]))

summary = {}
for r in rows:"""),
    ("""    key = (r[0], r[4].split(':')[0] + (':' + r[4].split(':')[1] if r[4].startswith(('MARK', 'OLD', 'EXC', 'CALLER', 'TRACKED', 'PRIM')) and ':' in r[4] else ''))""",
     """    key = (r[0], r[4].split(':')[0] + (':' + r[4].split(':')[1] if r[4].startswith(('MARK', 'OLD', 'EXC', 'CALLER', 'TRACKED', 'PRIM', 'COVER')) and ':' in r[4] else ''))"""),
    ("""print('places: A %d, B %d (LockGuard %d), C %d, D %d; primitive mark %s; not ok %d' % (
    sum(1 for r in rows if r[0] == 'A'), sum(1 for r in rows if r[0] == 'B'), n_guard,
    sum(1 for r in rows if r[0] == 'C'), sum(1 for r in rows if r[0] == 'D'), 'ok' if prim_ok else 'FAIL', bad))""",
     """print('places: A %d, B %d (LockGuard %d), C %d, D %d, E %d; primitive mark %s; not ok %d' % (
    sum(1 for r in rows if r[0] == 'A'), sum(1 for r in rows if r[0] == 'B'), n_guard,
    sum(1 for r in rows if r[0] == 'C'), sum(1 for r in rows if r[0] == 'D'), n_e, 'ok' if prim_ok else 'FAIL', bad))"""),
]

for a, b in REPL:
    n = t.count(a)
    if n != 1:
        print('FAIL: %d hits for %r' % (n, a[:80]))
        sys.exit(1)
    t = t.replace(a, b)
open(dst, 'wb').write(t.encode('utf-8'))
print('written', dst)
print('ALL OK')
