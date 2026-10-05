"""mut616.py - S15r2 (HPP-616), Red Team: own hand mutants of the S15a2 edit of enter_scene_s15.py.  Each mutant -> a copy in the
work dir; the author's suite test_enter_scene_s15.py (FX_FAST=1, FX_ENTER_BASE in the work dir) and the probe616.py run on the copy.
    python mut616.py <work dir> <id>
"""
import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

W = pathlib.Path(sys.argv[1])
MID = sys.argv[2]
PART = sys.argv[3] if len(sys.argv) > 3 else 'both'
SRC = 'C:/kyty/s288/s15/enter_scene_s15.py'
SUITE = 'C:/kyty/s288/s15/test_enter_scene_s15.py'
PROBE = str(pathlib.Path(__file__).with_name('probe616.py'))
M = {
    # the except narrowed to the type of the probe P1 (both polls)
    'm1_except_valueerror': [('except Exception as error:   # S15a2, item 528 (b)(1): no further poll',
                              'except ValueError as error:   # S15a2, item 528 (b)(1): no further poll'),
                             ('except Exception as error:   # S15a2, item 528 (b)(1): the poll after',
                              'except ValueError as error:   # S15a2, item 528 (b)(1): the poll after')],
    # after the exception the loop goes on polling (the hold does not end at once)
    'm2_poll_again': [('                            ucause = u_error(error)\n                        if ucause is not None:',
                       '                            u_error(error)\n                            ucause = None\n                        if ucause is not None:')],
    # the poll after the loop: the exception read as "game ended"
    'm3_after_game_ended': [('                        except Exception as error:   # S15a2, item 528 (b)(1): the poll after the loop\n'
                             '                            ucause = u_error(error)',
                             '                        except Exception as error:   # S15a2, item 528 (b)(1): the poll after the loop\n'
                             "                            ucause = 'game ended'")],
}
d = W / (MID + '_' + PART)
shutil.rmtree(d, ignore_errors=True)
d.mkdir(parents=True)
t = open(SRC, 'rb').read().decode('ascii')
for old, new in M[MID]:
    if t.count(old) != 1:
        print('%s ANCHOR COUNT %d - not applied' % (MID, t.count(old)))
        sys.exit(2)
    t = t.replace(old, new)
tgt = d / 'enter_scene_s15.py'
tgt.write_bytes(t.encode('ascii'))
# the suite imports sc_s15.py from its own directory (HERE) - it runs from s15, the target is argv[1]
env = dict(os.environ, PYTHONIOENCODING='utf-8', FX_ENTER_BASE=str(d / 'fx'), FX_FAST='1')
suite = probe = 'not run'
if PART in ('both', 'suite'):
  p = subprocess.run([sys.executable, SUITE, str(tgt)], capture_output=True, text=True, env=env, timeout=300)
# U15 (target = generator output byte for byte) fails on every copy by construction - it does not count as a kill
  fails = [l for l in p.stdout.splitlines() if l.startswith('FAIL') and not l.startswith('FAIL U15 ')]
  suite = 'KILLED by %s' % fails[0][:110] if fails else 'SURVIVED (rc %d, only U15 failed: %s)' % (
      p.returncode, any(l.startswith('FAIL U15 ') for l in p.stdout.splitlines()))
if PART in ('both', 'probe'):
  q = subprocess.run([sys.executable, PROBE, str(d / 'pw'), str(tgt)], capture_output=True, text=True, env=env, timeout=300)
  qf = [l for l in q.stdout.splitlines() if l[:1] == 'Q' and l.endswith('FAIL')]
  probe = 'KILLED by %s' % ','.join(x.split()[0] for x in qf) if qf else 'SURVIVED'
print('%s mutant sha256 %s | author suite: %s | probe616: %s' % (MID, hashlib.sha256(t.encode('ascii')).hexdigest()[:16], suite, probe))
