"""F20l2 (HPP-648): wires runchk_f20l2.py (item 587 (g) debt) into go_f20l2.sh (after procload, before the lock), launch_f20l2.sh (passes
F20L2_RUN_ID from PAPERCLIP_RUN_ID), test_tools_f20l2.py (fixtures) and mk_seal_f20l2.py (seal line).  LF kept as found.  ASCII only."""
import sys

G = 'C:/kyty/f287/f20l2/'


def patch(name, pairs):
    p = G + name
    s = open(p, 'rb').read().decode('ascii')
    crlf = '\r\n' in s
    s = s.replace('\r\n', '\n')
    for old, new in pairs:
        if s.count(old) != 1:
            print('%s: anchor count %d: %r' % (name, s.count(old), old[:70]))
            sys.exit(1)
        s = s.replace(old, new)
    if crlf:
        s = s.replace('\n', '\r\n')
    open(p, 'wb').write(s.encode('ascii'))
    print('patched', name)


patch('go_f20l2.sh', [(
    '[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }\n',
    '[ -e $LOCK ] && { echo "lock appeared: $(head -1 $LOCK)"; mv $OUT $OUT.lock_$(date -u +%H%M%S); exit 3; }\n'
    '# item 587 (g) debt: the run that launched this detached call must still be going (a cancelled run does not stop its detached children)\n'
    'RS=$(python $G/runchk_f20l2.py) || { log "run check (item 587 (g)): $RS - not starting, files untouched"; mv $OUT $OUT.gone_$(date -u +%H%M%S); exit 3; }\n'
    'log "run check (item 587 (g)): $RS"\n')])
patch('launch_f20l2.sh', [(
    'nohup bash -c "bash $G/go_f20l2.sh $T',
    'F20L2_RUN_ID="${PAPERCLIP_RUN_ID:-}" nohup bash -c "bash $G/go_f20l2.sh $T')])
patch('test_tools_f20l2.py', [(
    "Q.urllib.request.urlopen = keep_open\n",
    "Q.urllib.request.urlopen = keep_open\n"
    "# --- runchk_f20l2.py (item 587 (g) debt)\n"
    "_rf = os.path.join(TD, 'runchk.json')\n"
    "for iss, rid, want_rc, want in ((dict(executionRunId='run-a', status='in_progress'), 'run-a', 0, 'RUN ALIVE'),\n"
    "                                (dict(executionRunId=None, status='in_progress'), 'run-a', 1, 'RUN GONE'),\n"
    "                                (dict(executionRunId='run-b', status='in_progress'), 'run-a', 1, 'RUN GONE'),\n"
    "                                (dict(executionRunId='run-a', status='blocked'), 'run-a', 1, 'RUN GONE'),\n"
    "                                (dict(executionRunId='run-a', status='in_progress'), '', 1, 'RUN GONE')):\n"
    "    with open(_rf, 'w', encoding='ascii') as f:\n"
    "        json.dump(iss, f)\n"
    "    p = subprocess.run([sys.executable, os.path.join(HERE, 'runchk_f20l2.py'), '--fake', _rf], capture_output=True, text=True,\n"
    "                       env=dict(os.environ, F20L2_RUN_ID=rid))\n"
    "    check('runchk %s run %r want %r -> %s' % (iss['status'], iss['executionRunId'], rid, want), p.returncode == want_rc and p.stdout.startswith(want))\n"
    "p = subprocess.run([sys.executable, os.path.join(HERE, 'runchk_f20l2.py'), '--fake', os.path.join(TD, 'none.json')], capture_output=True, text=True)\n"
    "check('runchk: unreadable answer -> API ERROR rc 2', p.returncode == 2 and p.stdout.startswith('API ERROR'))\n"
    "_ga = go.index('RS=$(python $G/runchk_f20l2.py)')\n"
    "check('go: run check after procload and before the lock', go.index('procload.py --wait-s') < _ga < go.index('set -o noclobber'))\n"
    "check('launch: passes F20L2_RUN_ID from PAPERCLIP_RUN_ID', 'F20L2_RUN_ID=\"${PAPERCLIP_RUN_ID:-}\" nohup' in\n"
    "      open(os.path.join(HERE, 'launch_f20l2.sh'), encoding='ascii').read())\n"),
    ("'test_guard_f20l2.py', 'port_f20l2.py', 'edit_f20l2.py', 'refs_f20l2.py'):",
     "'test_guard_f20l2.py', 'port_f20l2.py', 'edit_f20l2.py', 'refs_f20l2.py', 'runchk_f20l2.py'):")])
patch('mk_seal_f20l2.py', [("'enter_scene.py', 'procload.py',", "'enter_scene.py', 'runchk_f20l2.py', 'procload.py',")])
