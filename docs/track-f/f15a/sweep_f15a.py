# F15a (HPP-491, ROADMAP s122 item 400(d)(3)): re-sweep of logs after the F0 sweep (F0 - 1574 logs up to s142).
# Roots: C:/kyty/s143..s146, C:/kyty/f287, C:/kyty/p283, C:/kyty/s288. Files: log_*.txt, log_*.txt.xz, _kyty*.txt
# (as F0 loglist_f0.py), fixture/mutant dirs skipped by the F0 regex. Streaming, binary, line by line ('xz -dc' for .xz).
# Per log: build label ('version:' line of the head), lines of 'Event: quit' (first), 'm_files[index] == nullptr',
# '--- Fatal Error ---' (total and after the first 'Event: quit' or 'Event: terminate' - both set need_exit,
# window.cpp:214-224), the 'Error: ...' / 'Not implemented' line after
# each fatal past the quit. Halts between files when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists.
# Usage: python sweep_f15a.py <out.tsv> [--list-only]
import os, re, subprocess, sys, time

out = sys.argv[1]
list_only = '--list-only' in sys.argv
roots = ['C:/kyty/s143', 'C:/kyty/s144', 'C:/kyty/s145', 'C:/kyty/s146', 'C:/kyty/f287', 'C:/kyty/p283', 'C:/kyty/s288']
fx = re.compile(r'/(fx_|work_|mut|test_|fixt)')
files = []
for r in roots:
    for dp, dn, fn in os.walk(r):
        dn[:] = [x for x in dn if x not in ('.git', 'build', 'wt', '_ShaderCache', '_Shaders', 'node_modules', '__pycache__')]
        d = dp.replace(os.sep, '/')
        for f in fn:
            ok = (f.startswith('log_') and (f.endswith('.txt') or f.endswith('.txt.xz'))) or (f.startswith('_kyty') and f.endswith('.txt'))
            if not ok:
                continue
            p = d + '/' + f
            if fx.search(p):
                continue
            files.append((p, os.path.getsize(p)))
files.sort()
print('files', len(files), 'bytes', sum(s for _, s in files))
if list_only:
    for p, s in files:
        print(p, s)
    sys.exit(0)

ver = re.compile(rb'^\s*version:\s*(.+)$')
t0 = time.time()
tot = {'logs': 0, 'quit': 0, 'nullptr': 0, 'nullptr_after_quit': 0, 'fatal': 0, 'fatal_after_quit': 0}
with open(out, 'w', encoding='utf-8', newline='\n') as o:
    o.write('path\tbytes\tlines\tbuild\tquit_line\tnullptr\tnullptr_after_quit\tfatal\tfatal_after_quit\tfatal_after_quit_text\n')
    for p, s in files:
        if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
            o.write('# HALT before %s (lock or STOP)\n' % p)
            print('HALT before', p)
            break
        if p.endswith('.xz'):
            proc = subprocess.Popen(['xz', '-dc', p], stdout=subprocess.PIPE)
            src = proc.stdout
        else:
            proc = None
            src = open(p, 'rb')
        build = ''
        quit_line = 0
        n = nul = nul_q = fat = fat_q = 0
        texts = []
        want_text = False
        for raw in src:
            n += 1
            if n <= 200 and not build:
                m = ver.match(raw.rstrip(b'\r\n'))
                if m:
                    build = m.group(1).decode('utf-8', 'replace').strip()
            if want_text:
                if b'Error' in raw or b'Not implemented' in raw or b'Assertion' in raw:
                    texts.append(raw.strip().decode('utf-8', 'replace')[:160])
                    want_text = False
            if not quit_line and (b'Event: quit' in raw or b'Event: terminate' in raw):
                quit_line = n
            if b'm_files[index] == nullptr' in raw:
                nul += 1
                if quit_line:
                    nul_q += 1
            if b'--- Fatal Error ---' in raw:
                fat += 1
                if quit_line:
                    fat_q += 1
                    want_text = True
        src.close()
        if proc:
            proc.wait()
        tot['logs'] += 1
        tot['quit'] += 1 if quit_line else 0
        tot['nullptr'] += nul
        tot['nullptr_after_quit'] += nul_q
        tot['fatal'] += fat
        tot['fatal_after_quit'] += fat_q
        o.write('%s\t%d\t%d\t%s\t%d\t%d\t%d\t%d\t%d\t%s\n' % (p, s, n, build, quit_line, nul, nul_q, fat, fat_q, ' | '.join(texts)))
        o.flush()
    o.write('# totals %s wall %.1f s\n' % (tot, time.time() - t0))
print('totals', tot, 'wall %.1f s' % (time.time() - t0))
