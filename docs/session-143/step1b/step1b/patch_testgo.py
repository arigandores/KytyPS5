"""Link 1b (HPP-321, item 242 (a), (b), (d)): test_go143a.py - the seal 02, the times.txt row count 12, and the new checks
g31-g36 (cache manifests, winpid, chain pid, DRY plan, the step 2 wrappers).  Each replacement must hit exactly once."""
p = 'C:/kyty/s143/test_go143a.py'
t = open(p, 'rb').read().decode('utf-8')
reps = [
    ("    (root / 'pred' / '01_sc143.md').write_text(", "    (root / 'pred' / '02_sc143.md').write_text("),
    ("and '--pred %s/pred/01_sc143.md' % rp in o", "and '--pred %s/pred/02_sc143.md' % rp in o"),
    ("ok &= case('g9 every plan: one attempt, clock pin, markers 0, the empty gate file, the seal 01_sc143,",
     "ok &= case('g9 every plan: one attempt, clock pin, markers 0, the empty gate file, the seal 02_sc143,"),
    ("all('date -u' in l for l in TEXT.split('\\n') if '>> $TIMES' in l) and TEXT.count('>> $TIMES') == 10)",
     "all('date -u' in l for l in TEXT.split('\\n') if '>> $TIMES' in l) and TEXT.count('>> $TIMES') == 12)"),
    ("ok &= case('g25 the chain reads the seal pred/01_sc143.md and the scorer sc143.py', 'PRED=\"pred/01_sc143.md\"' in TEXT",
     "ok &= case('g25 the chain reads the seal pred/02_sc143.md and the scorer sc143.py', 'PRED=\"pred/02_sc143.md\"' in TEXT"),
]
for a, b in reps:
    n = t.count(a)
    if n != 1:
        raise SystemExit('anchor count %d: %r' % (n, a[:90]))
    t = t.replace(a, b)
NEW = r'''nc = TEXT.find('set -o noclobber')
ok &= case('g31 item 242 (b): the cache manifest before the lock (after the shader cache count, before noclobber) and after '
           'the run (after the enter_scene end row, before the idle-refusal branch), each with a date -u row of times.txt; '
           'the stale list moves an old after-manifest, never the fresh before-manifest',
           TEXT.find('shader cache files before the lock $(cachen)') <
           TEXT.find("CMB=$(python $ROOT/cachemf143.py $OUT/cache_$T.before.json 2>&1 | tail -1 | tr -d '\\r')") <
           TEXT.find('go143a $T cache manifest before the lock: $CMB" >> $TIMES') < nc and
           TEXT.find('enter_scene end rc $RC') <
           TEXT.find("CMA=$(python $ROOT/cachemf143.py $OUT/cache_$T.after.json 2>&1 | tail -1 | tr -d '\\r')") <
           TEXT.find('go143a $T cache manifest after the run: $CMA" >> $TIMES') < TEXT.find('if [ "$RC" = "3" ]') and
           '"runs143/cache_$T.after.json"' in TEXT and 'cache_$T.before.json"' not in TEXT and
           TEXT.count('cachemf143.py $OUT/cache_$T.') == 2)
ok &= case('g32 the lock line carries the Windows pid of the shell (read by the builtin read from /proc/$$/winpid before any '
           'process); the foreign-CPU row gets --chain-pid $WINPID (item 242 (a), (d))',
           TEXT.find('\nWINPID=""\nread -r WINPID < /proc/$$/winpid 2>/dev/null\n') < first_proc and
           'echo "go143a.sh $T pid $$ winpid $WINPID started $(date +%Y-%m-%dT%H:%M:%S)" > $LOCK' in TEXT and
           'fgcpu143.py --since $OUT/fgcpu_$T.a.json --chain-pid $WINPID 2>&1' in fin)
ok &= case('g33 every DRY plan names both manifests and the chain pid of the CPU row',
           all('cache manifest before (cachemf143); lock with winpid' in o and 'cache manifest after (cachemf143)' in o
               and 'fgcpu143 --since --chain-pid' in o for _, o in plans.values()))
r = fixture('g34')
seal(r, ALL)
(r / 'LOCKFILE').write_text('go143a.sh v143_01 pid 7 winpid 123 started x\n')
rc, out = call(r, 'v143_01', DRY='1')
ok &= case('g34 a held lock of the new form is printed whole in the BUSY line', rc == 4 and
           'lock held: go143a.sh v143_01 pid 7 winpid 123 started x' in out)
WR = dict((n, Path(HERE, 'step2', n).read_bytes().decode('utf-8')) for n in ('next_one.sh', 'call_one.sh', 'wait_one.sh'))
nx, cl, wt = WR['next_one.sh'], WR['call_one.sh'], WR['wait_one.sh']
ok &= case('g35 the step 2 wrappers (item 242 (d)): ASCII and LF; next_one checks the tag, the stop file and the lock before '
           'anything else, writes its call row, starts call_one detached (nohup ... & disown) and waits in the foreground '
           'with wait_one; call_one runs exactly the seal call "PLWAIT=540 bash C:/kyty/s143/go143a.sh $T" and writes the rc; '
           'wait_one waits at most 56 x 10 s = 560 s (< 600 s of a tool command)',
           all(all(ord(c) < 128 for c in x) and '\r' not in x for x in WR.values()) and
           nx.find('case "$T" in') < nx.find('[ -e C:/kyty/s143/STOP ]') < nx.find('[ -e C:/kyty/SEALED_RUN.lock ]') <
           nx.find('nohup bash C:/kyty/s143/step2/call_one.sh $T > /dev/null 2>&1 & disown') <
           nx.find('bash C:/kyty/s143/step2/wait_one.sh $T') and
           '\nPLWAIT=540 bash C:/kyty/s143/go143a.sh $T > step2/go_$T.out.txt 2>&1\nRC=$?\n' in cl and
           cl.count('go143a.sh') == 3 and 'for i in $(seq 1 56); do' in wt and 'sleep 10' in wt and
           'mutlib' not in nx + cl + wt and all(line(t).split('call: ')[1].replace(t, '$T') in cl for t in S.SEQ))
e = dict((k, v) for k, v in os.environ.items() if not k.startswith('KYTY_'))
done = subprocess.run([BASH, str(Path(HERE, 'step2', 'next_one.sh')), 'x143'], capture_output=True, text=True, env=e,
                      timeout=60)
ok &= case('g36 next_one.sh refuses an unknown tag rc 2 before the stop file, the lock or any call',
           done.returncode == 2 and done.stdout.startswith('usage'))
'''
anchor = "print('checks: %d' % N[0])\n"
if t.count(anchor) != 1:
    raise SystemExit('final anchor')
t = t.replace(anchor, NEW + anchor)
open(p, 'wb').write(t.encode('utf-8'))
print('patched %d + g31-g36' % len(reps))
