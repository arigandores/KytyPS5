# F48a (HPP-830, ROADMAP p.748(d)(2)): delta sweep of logs modified after 2026-10-10 00:00Z by the F32a method.
# docs/track-f/f32a/sweep_f32a.py is imported unchanged (it imports the F0 scanner unchanged: KEY, SKIP_PREFIX, norm(),
# scan_segment(); lock gate = exit 3, STOP = exit 4, .xz opener); this wrapper only sets the output folder (env F32A_OUT
# before import) and the time origin T0 = 2026-10-10 00:00Z (module attribute, read by classify()).
# Usage (same verbs as sweep_f32a.py):
#   python sweep_f48a.py list | run <budget_s> [workers] | agg
import os, sys, calendar
HERE = os.path.dirname(os.path.abspath(__file__))
F32A_DIR = os.environ.get('F48A_F32A_DIR', os.path.join(os.path.dirname(HERE), 'f32a'))
os.environ.setdefault('F32A_OUT', 'C:/kyty/f287/f48a/sw')
if F32A_DIR not in sys.path:
    sys.path.insert(0, F32A_DIR)
import sweep_f32a as S  # noqa: E402  (unchanged method)

T0_F48A = calendar.timegm((2026, 10, 10, 0, 0, 0))
S.T0 = T0_F48A

if __name__ == '__main__':
    c = sys.argv[1] if len(sys.argv) > 1 else ''
    if c == 'list':
        S.cmd_list()
    elif c == 'run':
        S.cmd_run(float(sys.argv[2]) if len(sys.argv) > 2 else 480, int(sys.argv[3]) if len(sys.argv) > 3 else 16)
    elif c == 'agg':
        S.cmd_agg()
    else:
        print('usage: list | run <budget> [workers] | agg')
        sys.exit(2)
