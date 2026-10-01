p = 'C:/kyty/s144/test_go144a.py'
t = open(p, 'rb').read().decode('ascii').replace('\r\n', '\n')
ANCHOR = "print('checks: %d' % N[0])\n"
NEW = r"""ok &= case('g37 next_one.sh (MINOR-4 of audit 143): the API check apichk144.py runs after the tag, the stop file and the lock '
           'and before the call row and the detached call; its NO GO exits rc 4 without a call; the call row says "api GO"',
           nx.find('[ -e C:/kyty/SEALED_RUN.lock ]') < nx.find('python C:/kyty/s144/step2/apichk144.py --tag $T') <
           nx.find('api GO; call: PLWAIT=540 bash C:/kyty/s144/go144a.sh $T" >> $TIMES') <
           nx.find('nohup bash C:/kyty/s144/step2/call_one.sh $T') and nx.count('apichk144.py --tag $T') == 2 and
           nx.count('|| { echo "api check NO GO before $T (row in times.txt)"; exit 4; }') == 2)
for bad in ('v144_08', 'w144_21', 'v143_01', 'w143_01'):
    done = subprocess.run([BASH, str(Path(HERE, 'step2', 'next_one.sh')), bad], capture_output=True, text=True, env=e,
                          timeout=60)
    ok &= case('g38 next_one.sh refuses %s rc 2 (no V of the eight W-only levels, no tag past 20, no tag of 143)' % bad,
               done.returncode == 2 and done.stdout.startswith('usage'))
_spa = importlib.util.spec_from_file_location('apichk_under_test', os.path.join(HERE, 'step2', 'apichk144.py'))
A = importlib.util.module_from_spec(_spa)
_spa.loader.exec_module(A)
ME = 'agent-me'
ISS = dict(id='i1', identifier='HPP-332', status='in_progress', executionRunId='run1')
C1 = dict(id='c1', authorAgentId=ME, createdAt='2026-10-01T06:00:00Z')
C2 = dict(id='c2', authorAgentId='lead', createdAt='2026-10-01T06:01:00Z')
C3 = dict(id='c3', authorUserId='user', createdAt='2026-10-01T06:02:00Z')
rc, row = A.judge('w144_00', ISS, [C1], None, ME)
ok &= case('g39 apichk: in progress, only own comments -> GO rc 0 with the issue, status, run, count and the last comment',
           rc == 0 and row == 'apichk144 w144_00 issue HPP-332 status in_progress executionRunId run1 comments 1 after start '
           'new-foreign 0 last c1 agent-me 2026-10-01T06:00:00Z -> GO')
rc, row = A.judge('w144_00', ISS, [C2, C1], None, ME)
rc2, row2 = A.judge('w144_00', ISS, [C2, C1], 'c2', ME)
rc3, row3 = A.judge('w144_00', ISS, [C1, C2, C3], 'c2', ME)
ok &= case('g40 apichk: an unread comment of another author -> NO GO rc 4 naming the id to pass; after it is read (--after c2) '
           '-> GO; a newer one of a user -> NO GO again (sorted by time, not by the order of the answer)',
           rc == 4 and 'NO GO (1 unread comment(s) of another author since start - read them, then call with --after c2)' in row
           and rc2 == 0 and row2.endswith('-> GO') and rc3 == 4 and '--after c3' in row3)
rc, row = A.judge('w144_00', dict(ISS, status='cancelled'), [], None, ME)
rc2, row2 = A.judge('w144_00', dict(ISS, status='done'), [], None, ME)
rc3, row3 = A.judge('w144_00', dict(ISS, status='blocked'), [], None, ME)
ok &= case('g41 apichk: the issue cancelled or done -> NO GO; blocked alone (a status, not the state of a run) -> GO',
           rc == 4 and 'issue cancelled' in row and rc2 == 4 and 'issue done' in row2 and rc3 == 0)
rc, row = A.judge('w144_00', None, None, None, ME)
rc2, row2 = A.judge('w144_00', ISS, None, None, ME)
rc3, row3 = A.judge('w144_00', ISS, [C1], 'cX', ME)
ok &= case('g42 apichk: no answer (issue or comments) -> NO GO; an --after id not among the comments -> NO GO',
           rc == 4 and rc2 == 4 and 'no answer' in row and rc3 == 4 and 'comment cX not found' in row3)
TM = FX / 'api_times.txt'
calls = []


def fake(url):
    calls.append(url)
    return dict(ISS) if not url.endswith('/comments') else [C1]


old_env = dict(os.environ)
os.environ.update(PAPERCLIP_API_URL='http://h:1/api', PAPERCLIP_API_KEY='k', PAPERCLIP_AGENT_ID=ME)
import contextlib as _cl
import io as _io
_b = _io.StringIO()
with _cl.redirect_stdout(_b):
    rm = A.main(['--tag', 'v144_09', '--issue', 'HPP-332'], fetch=fake, times=str(TM))


def boom(url):
    raise OSError('down')


with _cl.redirect_stdout(_b):
    rm2 = A.main(['--tag', 'v144_09', '--issue', 'HPP-332'], fetch=boom, times=str(TM))
os.environ.clear()
os.environ.update(old_env)
tl = TM.read_text(encoding='ascii').split('\n')
ok &= case('g43 apichk main: two GETs (issue, comments) on the base without /api doubled; one UTC row per call appended to '
           'the times file; a failing GET -> rc 4 and a "no answer" row',
           rm == 0 and calls == ['http://h:1/api/issues/HPP-332', 'http://h:1/api/issues/HPP-332/comments'] and
           re.match(r'^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ apichk144 v144_09 issue HPP-332 status in_progress ', tl[0]) is not None
           and rm2 == 4 and 'no answer' in tl[1] and len([x for x in tl if x]) == 2)
dr = FX / 'api_drv.py'
dr.write_text('import sys, importlib.util\n'
              's = importlib.util.spec_from_file_location("a", %r)\nA = importlib.util.module_from_spec(s)\n'
              's.loader.exec_module(A)\n'
              'def f(u):\n    return {"identifier": "HPP-332", "status": "in_progress"} if not u.endswith("/comments") else '
              '[{"id": "c9", "authorUserId": "u", "createdAt": "x", "body": "\\u0421\\u0442\\u043e\\u043f"}]\n'
              'sys.exit(A.main(["--tag", "w144_00", "--issue", "HPP-332"], fetch=f, times=%r))\n'
              % (os.path.join(HERE, 'step2', 'apichk144.py'), (FX / 'api_t2.txt').as_posix()), encoding='utf-8')
env2 = dict((k, v) for k, v in os.environ.items() if k != 'PYTHONIOENCODING')
env2['PYTHONUTF8'] = '0'
pp = subprocess.run([sys.executable, str(dr)], capture_output=True, env=env2, timeout=60)
try:
    pp.stdout.decode('cp1250', errors='strict')
    encp = pp.returncode == 4 and b'apichk144 w144_00' in pp.stdout and not pp.stderr and \
        all(b < 128 for b in (FX / 'api_t2.txt').read_bytes())
except UnicodeError:
    encp = False
ok &= case('g44 apichk in a child without PYTHONIOENCODING (console cp1250): ASCII line and row, rc 4 on a foreign comment '
           'with a Cyrillic body (the body is never printed)', encp)
ATEXT = Path(HERE, 'step2', 'apichk144.py').read_bytes().decode('utf-8')
ok &= case('g45 apichk144.py is ASCII and LF, starts no process and is in the seal list of sc144',
           all(ord(c) < 128 for c in ATEXT) and '\r' not in ATEXT and 'subprocess' not in ATEXT.split(chr(34) * 3, 2)[2]
           and 'step2/apichk144.py' in S.SEALED_NAMES)
print('checks: %d' % N[0])
"""
assert t.count(ANCHOR) == 1
t = t.replace(ANCHOR, NEW)
open(p, 'wb').write(t.encode('ascii'))
print('ok')
