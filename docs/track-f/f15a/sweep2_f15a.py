# F15a (HPP-491, ROADMAP s122 item 400(d)(3)): re-sweep of logs after the F0 sweep - block search version of
# sweep_f15a.py (the same file list rule and the same markers; line-by-line Python did not fit the 600 s tool limit
# on 127 GB). Files are read in 64 MiB blocks with a 4 KiB overlap; a marker never spans a line, so the counts are
# those of a line scan. Per log: build label (first 'version:' line in the first 64 KiB), byte offset of the first
# 'Event: quit' or 'Event: terminate' (both set need_exit, window.cpp:214-224), counts of 'm_files[index] == nullptr'
# and '--- Fatal Error ---' in total and after that offset, the first 'Error'/'Not implemented' line within 2 KiB
# after each fatal past the quit.
# Resumable: paths already in <out.tsv> are skipped; stops between files after <budget_s> seconds of wall time and
# when C:/kyty/SEALED_RUN.lock or C:/kyty/f287/STOP exists. Prints 'SWEEP COMPLETE' when no file is left.
# Usage: python sweep2_f15a.py <out.tsv> <budget_s>
import os, re, sys, time

out = sys.argv[1]
budget = float(sys.argv[2])
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

done = set()
if os.path.exists(out):
    for l in open(out, encoding='utf-8'):
        if l.startswith('C:/'):
            done.add(l.split('\t', 1)[0])
else:
    with open(out, 'w', encoding='utf-8', newline='\n') as o:
        o.write('path\tbytes\tbuild\tquit_off\tnullptr\tnullptr_after_quit\tfatal\tfatal_after_quit\tfatal_after_quit_text\n')

left = [(p, s) for p, s in files if p not in done]
print('files', len(files), 'done before', len(done), 'left', len(left))

QUIT = (b'Event: quit', b'Event: terminate')
NUL = b'm_files[index] == nullptr'
FAT = b'--- Fatal Error ---'
VER = re.compile(rb'(?m)^\s*version:\s*([^\r\n]+)')
BLOCK = 64 << 20
OVER = 4096


def positions(buf, pat, limit):
    res = []
    i = buf.find(pat)
    while i != -1 and i < limit:
        res.append(i)
        i = buf.find(pat, i + 1)
    return res


def text_after(buf, i):
    seg = buf[i:i + 2048]
    for ln in seg.split(b'\n')[1:]:
        if b'Error' in ln or b'Not implemented' in ln or b'Assertion' in ln:
            return ln.strip().decode('utf-8', 'replace')[:160]
    return ''


t0 = time.time()
n_done = 0
with open(out, 'a', encoding='utf-8', newline='\n') as o:
    for p, s in left:
        if time.time() - t0 > budget:
            print('BUDGET stop, left', len(left) - n_done)
            break
        if os.path.exists('C:/kyty/SEALED_RUN.lock') or os.path.exists('C:/kyty/f287/STOP'):
            print('HALT before', p)
            break
        if p.endswith('.xz'):
            import subprocess
            proc = subprocess.Popen(['xz', '-dc', p], stdout=subprocess.PIPE)
            src = proc.stdout
        else:
            proc = None
            src = open(p, 'rb')
        build = ''
        quit_off = -1
        nul = nul_q = fat = fat_q = 0
        texts = []
        base = 0          # file offset of buf[0]
        buf = b''
        first = True
        while True:
            data = src.read(BLOCK)
            eof = not data
            buf += data
            if first:
                m = VER.search(buf[:65536])
                if m:
                    build = m.group(1).decode('utf-8', 'replace').strip()
                first = False
            limit = len(buf) if eof else max(0, len(buf) - OVER)
            if quit_off < 0:
                q = [x for pat in QUIT for x in positions(buf, pat, limit)]
                if q:
                    quit_off = base + min(q)
            for i in positions(buf, NUL, limit):
                nul += 1
                if 0 <= quit_off <= base + i:
                    nul_q += 1
            for i in positions(buf, FAT, limit):
                fat += 1
                if 0 <= quit_off <= base + i:
                    fat_q += 1
                    texts.append(text_after(buf, i))
            if eof:
                break
            base += limit
            buf = buf[limit:]
        src.close()
        if proc:
            proc.wait()
        o.write('%s\t%d\t%s\t%d\t%d\t%d\t%d\t%d\t%s\n' % (p, s, build, quit_off, nul, nul_q, fat, fat_q, ' | '.join(texts)))
        o.flush()
        n_done += 1
    else:
        print('SWEEP COMPLETE')
print('this call files', n_done, 'wall %.1f s' % (time.time() - t0))
