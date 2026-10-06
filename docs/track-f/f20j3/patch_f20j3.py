"""F20j3 (HPP-646, ROADMAP s122 item 574(g)(1)-(6)): KYTY_DIAG_B32 by U1 of item 550(zh) - marks on the host waits of
the emulator with the waker and the peer, M5 off the sampler thread, ring_hold.

Usage: python patch_f20j3.py <tree root> [--check] [--only=<path prefix>]
Parts (same folder): p1_core.py (diagB32, threads primitives), p2_sites.py (wait sites), p3_mutex.py (TrackedMutex),
p4_tests.py (tests/DiagB32Tests.cpp).
Operations, applied in order to the file texts (CR removed before, restored if the file had CRLF; written with
write_bytes):
  edit(path, old, new)        - a block of WHOLE lines that occurs exactly once (at a line start), replaced;
  edit_n(path, old, new, n)   - the same block occurring exactly n times, every occurrence replaced;
  add_include(path)           - '#include "common/diagB32.h"' after the first #include line (if absent);
  note_before(path, line, arg, n) - before each of exactly n lines whose stripped text is `line`, the line
                                '<indent>Common::DiagB32::NoteSignal(<arg>); // Track F, F20j3' is inserted;
  wrap_mutex(path, name, sel) - the std mutex declaration line(s) of `name` get Common::DiagB32::TrackedMutex<...>.
Any operation that does not find its anchor stops the script before anything is written. Prints ALL OK.
--check: every operation is already applied (nothing written).
"""
import os
import re
import sys

ROOT = sys.argv[1].rstrip('/\\')
CHECK = '--check' in sys.argv[2:]
# --only=<path prefix>: apply (or check) only the operations on files under the prefix (e.g. tests/ - the src files
# keep their timestamps, no full rebuild).
ONLY = next((a.split('=', 1)[1] for a in sys.argv[2:] if a.startswith('--only=')), '')
HERE = os.path.dirname(os.path.abspath(__file__))
OPS = []
INC = '#include "common/diagB32.h"'


def edit(path, old, new):
    OPS.append(('edit', path, old, new, 1))


def edit_n(path, old, new, n):
    OPS.append(('edit', path, old, new, n))


def add_include(path):
    if ('inc', path) not in [(o[0], o[1]) for o in OPS]:
        OPS.append(('inc', path))


def note_before(path, line, arg, n):
    OPS.append(('note', path, line, arg, n))


def wrap_mutex(path, name, sel):
    OPS.append(('wrap', path, name, sel))


def ctad(path, name, n):
    """std::lock_guard<std::X> lock(...name) -> std::lock_guard lock(...name): exactly n lines (the deduced type is the
    same for a std mutex and is the TrackedMutex for a wrapped one)."""
    OPS.append(('ctad', path, name, n))


for part in ('p1_core.py', 'p2_sites.py', 'p3_mutex.py', 'p4_tests.py'):
    exec(open(os.path.join(HERE, part), encoding='utf-8').read())

FILES = {}


def load(path):
    if path not in FILES:
        raw = open(ROOT + '/' + path, 'rb').read().decode('utf-8')
        crlf = '\r\n' in raw
        FILES[path] = [raw.replace('\r\n', '\n'), crlf]
    return FILES[path]


def stop(msg):
    print('STOP ' + msg)
    sys.exit(2)


def count_at_line_start(text, block):
    n = 0
    i = text.find(block)
    while i >= 0:
        if i == 0 or text[i - 1] == '\n':
            n += 1
        i = text.find(block, i + 1)
    return n


DECL = r'^(\s*)((?:static |mutable |alignas\(\d+\) )*)std::(mutex|recursive_mutex|shared_mutex)(\s+)%s(\s*(?:\{\s*\})?\s*;)(.*)$'
DECL_DONE = r'^\s*(?:static |mutable |alignas\(\d+\) )*Common::DiagB32::TrackedMutex<std::(?:mutex|recursive_mutex|shared_mutex)(?:, Common::DiagB32::Wait::\w+)?>\s+%s\s*(?:\{\s*\})?\s*;'
NOTE = 'Common::DiagB32::NoteSignal(%s); // Track F, F20j3'

bad = 0
for op in OPS:
    kind, path = op[0], op[1]
    if not path.startswith(ONLY):
        continue
    entry = load(path)
    text = entry[0]
    if kind == 'edit':
        old, new, n = op[2], op[3], op[4]
        if not old.endswith('\n') or not new.endswith('\n'):
            stop('block without final newline in %s' % path)
        if CHECK:
            if count_at_line_start(text, new) != n:
                bad += 1
                print('NOT APPLIED %s: %s' % (path, old.splitlines()[0][:90]))
            continue
        if text.count(old) != n or count_at_line_start(text, old) != n:
            stop('%s: block found %d times (%d at a line start), want %d: %s' % (
                path, text.count(old), count_at_line_start(text, old), n, old.splitlines()[0][:90]))
        entry[0] = text.replace(old, new)
    elif kind == 'inc':
        if any(ln.startswith(INC) for ln in text.split('\n')):
            continue
        if CHECK:
            bad += 1
            print('NOT APPLIED %s: include' % path)
            continue
        lines = text.split('\n')
        first = next((i for i, l in enumerate(lines) if l.startswith('#include ')), None)
        if first is None:
            stop('%s: no #include line' % path)
        lines.insert(first + 1, INC + ' // Track F, F20j3 (KYTY_DIAG_B32, ROADMAP s122 item 574(g))')
        entry[0] = '\n'.join(lines)
    elif kind == 'note':
        line, arg, n = op[2], op[3], op[4]
        lines = text.split('\n')
        idx = [i for i, l in enumerate(lines) if l.strip() == line]
        note = NOTE % arg
        done = [i for i in idx if i > 0 and lines[i - 1].strip() == note]
        if CHECK:  # later edits may add notified lines of their own (with the note): all must carry it
            if len(idx) < n or len(done) != len(idx):
                bad += 1
                print('NOT APPLIED %s: note before %s (%d of %d)' % (path, line, len(done), n))
            continue
        if len(idx) != n:
            stop('%s: line "%s" found %d times, want %d' % (path, line, len(idx), n))
        if done:
            stop('%s: note before %s already present' % (path, line))
        for i in reversed(idx):
            indent = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
            lines.insert(i, indent + note)
        entry[0] = '\n'.join(lines)
    elif kind == 'wrap':
        name, sel = op[2], op[3]
        lines = text.split('\n')
        rx = re.compile(DECL % re.escape(name))
        rd = re.compile(DECL_DONE % re.escape(name))
        idx = [i for i, l in enumerate(lines) if rx.match(l)]
        idx_done = [i for i, l in enumerate(lines) if rd.match(l)]
        if sel is None:
            pick = [(0, None)]
            want = 1
        elif isinstance(sel, int):
            pick = [(k, None) for k in range(sel)]
            want = sel
        else:
            pick = sel
            want = None
        if CHECK:
            if len(idx_done) != len(pick):
                bad += 1
                print('NOT APPLIED %s: wrap %s (%d of %d)' % (path, name, len(idx_done), len(pick)))
            continue
        if want is not None and len(idx) != want:
            stop('%s: declaration of %s found %d times, want %d' % (path, name, len(idx), want))
        if want is None and len(idx) <= max(k for k, _ in pick):
            stop('%s: declaration of %s found %d times' % (path, name, len(idx)))
        for k, wkind in pick:
            i = idx[k]
            m = rx.match(lines[i])
            targ = 'std::' + m.group(3) + (', Common::DiagB32::Wait::' + wkind if wkind else '')
            tail = m.group(6)
            if '//' not in tail:
                tail = tail + ' // Track F, F20j3 (KYTY_DIAG_B32 W:%s, ROADMAP s122 item 574(g)(1))' % (
                    'ult' if wkind == 'Ult' else 'emu_mutex')
            lines[i] = m.group(1) + m.group(2) + 'Common::DiagB32::TrackedMutex<' + targ + '>' + m.group(4) + name + \
                m.group(5) + tail
        entry[0] = '\n'.join(lines)
    elif kind == 'ctad':
        name, n = op[2], op[3]
        rx = re.compile(r'(std::(?:lock_guard|unique_lock|scoped_lock|shared_lock))<std::\w+>(\s+\w+\s*[({][^;]*?(?<![\w])' +
                        re.escape(name) + r'\s*[)},])')
        lines = text.split('\n')
        idx = [i for i, l in enumerate(lines) if rx.search(l)]
        if CHECK:
            if idx:
                bad += 1
                print('NOT APPLIED %s: ctad %s (%d left)' % (path, name, len(idx)))
            continue
        if len(idx) != n:
            stop('%s: explicit lock of %s found %d times, want %d' % (path, name, len(idx), n))
        for i in idx:
            lines[i] = rx.sub(r'\1\2', lines[i])
        entry[0] = '\n'.join(lines)
    else:
        stop('unknown op ' + kind)

if CHECK:
    print('operations %d not applied %d' % (len(OPS), bad))
    print('ALL OK' if bad == 0 else 'FAILED')
    sys.exit(0 if bad == 0 else 1)

for path, (text, crlf) in FILES.items():
    out = text.replace('\n', '\r\n') if crlf else text
    open(ROOT + '/' + path, 'wb').write(out.encode('utf-8'))
    print('patched %s (%s)' % (path, 'CRLF' if crlf else 'LF'))
print('operations %d files %d' % (len(OPS), len(FILES)))
print('ALL OK')
