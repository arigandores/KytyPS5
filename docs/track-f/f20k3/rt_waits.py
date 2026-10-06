# Red Team F20k3: independent inventory of blocking host waits in src/** (not graphics/shader, not launcher),
# compared with the executor's waits_wt.tsv. Prints hits missing from the executor's table.
import os, re, sys, collections

root = sys.argv[1]          # .../src
tsv = sys.argv[2]           # executor's waits_wt.tsv
PATS = [
    ('cv_wait', r'(\.|->)(Wait|WaitFor)\s*\('),
    ('std_wait', r'(\.|->)(wait|wait_for|wait_until)\s*\('),
    ('winwait', r'\b(WaitForSingleObject(Ex)?|WaitForMultipleObjects(Ex)?|MsgWaitForMultipleObjects|SignalObjectAndWait|WaitOnAddress|SleepConditionVariable(CS|SRW))\s*\('),
    ('sleep', r'\b(Sleep|SleepEx|SleepMicro|SleepNano|SleepHighResolution\w*|sleep_for|sleep_until|SDL_Delay|usleep|nanosleep)\s*\('),
    ('acquire', r'(\.|->)(acquire|try_acquire_for|try_acquire_until|arrive_and_wait)\s*\('),
    ('join', r'(\.|->)join\s*\(\s*\)'),
    ('sdl', r'\bSDL_WaitEvent(Timeout)?\s*\('),
    ('rawlock', r'\b(EnterCriticalSection|AcquireSRWLock(Exclusive|Shared))\s*\('),
    ('vkwait', r'\b(waitForFences|vkWaitForFences|waitIdle|vkDeviceWaitIdle|vkQueueWaitIdle|waitSemaphores|vkWaitSemaphores)\s*\('),
    ('future', r'(\.|->)get\s*\(\s*\)\s*;.*future|std::future|std::async'),
    ('spin', r'(_mm_pause|YieldProcessor|this_thread::yield|SwitchToThread)\s*\('),
    ('stdmutex_decl', r'\bstd::(mutex|recursive_mutex|shared_mutex|timed_mutex|recursive_timed_mutex|shared_timed_mutex)\b\s+[A-Za-z_]\w*\s*(;|\{|\[)'),
    ('sem_decl', r'\bstd::(binary_semaphore|counting_semaphore|latch|barrier)\b'),
]
rx = [(k, re.compile(p)) for k, p in PATS]
skip_dirs = ('graphics' + os.sep + 'shader', 'launcher')

hits = []
for dp, dn, fn in os.walk(root):
    rel = os.path.relpath(dp, root)
    if any(rel == s or rel.startswith(s + os.sep) for s in skip_dirs):
        continue
    for f in fn:
        if not f.endswith(('.cpp', '.h', '.inc', '.hpp')):
            continue
        p = os.path.join(dp, f)
        relf = os.path.relpath(p, root).replace(os.sep, '/')
        with open(p, 'rb') as h:
            lines = h.read().decode('utf-8', 'replace').split('\n')
        for i, l in enumerate(lines):
            s = l.strip()
            if s.startswith('//') or s.startswith('*') or s.startswith('/*'):
                continue
            code = re.sub(r'"([^"\\]|\\.)*"', '""', l.split('//')[0])
            for k, r in rx:
                if r.search(code):
                    hits.append((relf, i + 1, k, s[:140]))

ex = collections.defaultdict(set)
exlines = set()
for row in open(tsv, encoding='utf-8'):
    c = row.rstrip('\n').split('\t')
    if c[0] == 'part':
        continue
    try:
        exlines.add((c[1], int(c[2])))
    except ValueError:
        pass

miss = [h for h in hits if (h[0], h[1]) not in exlines]
print('hits', len(hits), 'in_tsv', len(hits) - len(miss), 'missing', len(miss))
byk = collections.Counter(h[2] for h in miss)
print('missing by kind', dict(byk))
for h in miss:
    print('\t'.join(map(str, h)))
