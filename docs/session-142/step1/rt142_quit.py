# Red Team s142 step 1: what the letter of sc142 (every row, every marker) sees AFTER the first "Event: quit" of an
# enter_scene hold log: rows, their dt, rows >= 1 s / >= 100 ms, the last row, death markers.  Tail of each log only
# (last TAILMB MB, binary); a log whose tail has no Event: quit is reported as such.  s122-s140 logs with a hold.
import glob, json, os, re, hashlib
TAILMB = 48
RX_FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)([^\n]*)')
MK = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost')
out = []
agg = dict(logs=0, noquit=0, withrows=0, rows=0, k2=0, k3=0, mk=0, lastk2=0, malformed=0)
for p in sorted(glob.glob('C:/kyty/s1[2-4][0-9]/*.json')):
    try:
        js = json.load(open(p, encoding='utf-8'))
    except Exception:
        continue
    if not isinstance(js, dict) or 'attempts' not in js:
        continue
    at = js.get('attempts') or []
    if not at or at[-1].get('hold_s') is None:
        continue
    tag = os.path.basename(p)[:-5]
    lp = os.path.join(os.path.dirname(p), 'log_%s.txt' % tag)
    if not os.path.isfile(lp):
        continue
    size = os.path.getsize(lp)
    with open(lp, 'rb') as f:
        f.seek(max(0, size - TAILMB * 1048576))
        buf = f.read()
    agg['logs'] += 1
    q = buf.find(b'Event: quit')
    if q < 0:
        agg['noquit'] += 1
        out.append('%s size %d: no Event: quit in the last %d MB (hold_exit %s)' % (lp, size, TAILMB, at[-1].get('hold_exit')))
        continue
    post = buf[q:]
    rows = [(int(m.group(1)), int(m.group(2))) for m in RX_FT.finditer(post)]
    malformed = post.count(b'FrameTrace: n=') - len(rows)
    mk = [m.decode() for m in MK if m in post]
    k2 = [r for r in rows if r[1] >= 1000000]
    k3 = [r for r in rows if 100000 <= r[1] < 1000000]
    agg['withrows'] += bool(rows)
    agg['rows'] += len(rows)
    agg['k2'] += bool(k2)
    agg['k3'] += bool(k3)
    agg['mk'] += bool(mk)
    agg['malformed'] += malformed
    agg['lastk2'] += bool(rows) and rows[-1][1] >= 1000000
    out.append('%s ga %s: post-quit rows %d max_dt %s K2rows %s K3rows %d last %s markers %s malformed %d' % (
        lp, js.get('guest_args'), len(rows), max((r[1] for r in rows), default=None), k2[:3], len(k3),
        rows[-1] if rows else None, mk or '-', malformed))
print('\n'.join(out))
print('SUMMARY logs %(logs)d no-quit-in-tail %(noquit)d with post-quit rows %(withrows)d post-quit rows %(rows)d '
      'logs with a post-quit row >= 1 s %(k2)d (last row >= 1 s %(lastk2)d) logs with a post-quit row 100 ms..1 s %(k3)d '
      'logs with a post-quit death marker %(mk)d malformed FrameTrace in the post-quit parts %(malformed)d' % agg)
