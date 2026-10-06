"""S17a5 (HPP-638, ROADMAP s122 item 561(g)(2)(1)): order of the lines of the precache/rebuild thread and of the main thread
in the S17c logs (C:/kyty/s288/s17c/log_s17c_<tag>.txt, edition 3, binary S17a4 ed2686da). Prints, per tag, the line
numbers of: end of the PipelineCache constructor (S-pcw), stand stop applied, HostImport preloaded (main thread, graphics
init), FixMinimize (first main thread line after the graphics init), first line of the preparation loop (progress),
Window 1 shown, rebuild summary, close stop requested, startup wait finished; the HostImport preload time, the rebuild
wall_ms, and LOOP_DURING_REBUILD = the preparation loop printed its first line before the rebuild summary. Whole logs
are scanned (1-1.4 M lines each). ASCII only."""
import os
import re
import sys

KEYS = [
    ('pcw', b'S-pcw:'),
    ('stand', b'ShaderReplay: stand stop applied'),
    ('preload', b'HostImport: preloaded'),
    ('fixmin', b'FixMinimize'),
    ('progress', b'ShaderPreparation: progress'),
    ('rebuild', b'ShaderReplay: rebuild records'),
    ('shown', b'Window 1 shown'),
    ('close', b'ShaderReplay: close stop requested'),
    ('wait', b'ShaderPreparation: startup wait finished'),
]
TAGS = sys.argv[1:] or ['ks', 'kn', 'kc', 'r3', 'rs', 'c2', 'n0', 'e3']
for tag in TAGS:
    path = 'C:/kyty/s288/s17c/log_s17c_%s.txt' % tag
    if not os.path.exists(path):
        print(tag, 'no log')
        continue
    found = {}
    extra = {}
    with open(path, 'rb') as f:
        for n, line in enumerate(f, 1):
            for name, key in KEYS:
                if name not in found and line.startswith(key):
                    found[name] = n
                    m = re.search(rb'in (\d+) ms', line) if name == 'preload' else re.search(rb'wall_ms=(\d+)', line)
                    if m and name in ('preload', 'rebuild'):
                        extra[name] = int(m.group(1))
    during = 'progress' in found and 'rebuild' in found and found['progress'] < found['rebuild']
    print('s17c_%s %s preload_ms=%s rebuild_wall_ms=%s LOOP_DURING_REBUILD=%s' % (
        tag, ' '.join('%s=%s' % (k, found.get(k, '-')) for k, _ in KEYS), extra.get('preload', '-'),
        extra.get('rebuild', '-'), 'yes' if during else 'no'))
