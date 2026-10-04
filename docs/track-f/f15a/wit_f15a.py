# F15a (HPP-491, ROADMAP s122 item 400(d)(1)): witness log of B4 - the lines before 'm_files[index] == nullptr'.
# Streams the log (plain or .xz through 'xz -dc'), keeps a ring of the last RING lines, prints the ring at the first
# fatal, the line numbers of 'Event: quit', 'done!', the fatal, and the thread ids (PRINT_NAME headers '[tid][time] lib::func()')
# seen after 'Event: quit' with their last function.
import collections, re, subprocess, sys

path = sys.argv[1]
RING = int(sys.argv[2]) if len(sys.argv) > 2 else 120
if path.endswith('.xz'):
    proc = subprocess.Popen(['xz', '-dc', path], stdout=subprocess.PIPE)
    src = proc.stdout
else:
    proc = None
    src = open(path, 'rb')

hdr = re.compile(rb'^\[(\w+)\]\[(\d\d:\d\d:\d\d\.\d+)\]\s+(\S+)')
ring = collections.deque(maxlen=RING)
quit_line = None
fatal_line = None
nullptr_line = None
after_quit = collections.OrderedDict()
n = 0
printed = False
for raw in src:
    n += 1
    line = raw.rstrip(b'\r\n')
    ring.append((n, line))
    if quit_line is None and b'Event: quit' in line:
        quit_line = n
        print('EVENT_QUIT line', n, line[:200].decode('utf-8', 'replace'))
    if b'done!' == line.strip():
        print('DONE line', n)
    m = hdr.match(line)
    if m and quit_line is not None:
        tid = m.group(1).decode()
        after_quit[tid] = (n, m.group(2).decode(), m.group(3).decode('utf-8', 'replace'))
    if b'--- Fatal Error ---' in line and fatal_line is None:
        fatal_line = n
        print('FATAL line', n)
    if b'm_files[index] == nullptr' in line and nullptr_line is None:
        nullptr_line = n
        print('NULLPTR line', n, line[:200].decode('utf-8', 'replace'))
        if not printed:
            printed = True
            print('--- ring of the last', len(ring), 'lines before and with the fatal')
            for k, l in ring:
                print('%9d  %s' % (k, l[:220].decode('utf-8', 'replace')))
print('TOTAL lines', n)
print('--- thread headers after Event: quit (tid: last line, time, function)')
for tid, (k, t, f) in after_quit.items():
    print(tid, k, t, f)
if proc:
    proc.wait()
