"""Track F link F26c (HPP-692; ROADMAP s122 item 630 (g)(3), (g)(5), (d)): the reader of one tag b25_NN of the B25 series and the table.
No verdict on B25 - the reading is the lead's F26d by item 630 (e).

One pass over the log of the tag (and its stdout) by lines:
  DETECTOR   any line holding one of  b'There are too many objects/batches', b'command_buffer_writer.ppr.cpp', b'pc=0x00000009004a020e'
             (item 630 (g)(5); the strings of F26a sweep_f26a.py SIGS), in the log or the stdout
  entry      the first line holding b'Level has started: intro_next' (the guest line 'GuestOut: Level has started: intro_next')
  sum_dt     sum of dt_us of the lines 'FrameTrace: n=<n> dt_us=<d>' after the entry line up to the next 'Level has started:' line
             (the definition of F26a section 3 / sweep_f26a.py walk), frames = their count, max_dt = their maximum
  death      lines with b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost' (the DEATH
             list of fs10c_read.py) or b'Unhandled host exception' (item 630 (g)(3)), in the log or the stdout
  pre-entry  a row, not a member: max dt_us and the count of frames >= 1 s of the FrameTrace lines before the entry line (item 630
             (d)(2) does not say where the frame >= 1 s is counted; the member reads after the entry - the definitions of F26a
             section 3 - and the row prints the other reading)
  entry_s    the json attempts[0].started_s (wall from the process start to the entry line, enter_scene.py) - 'no entry in 60 s' of item
             630 (d)(2)
Class of the tag (item 630 (d)):
  DETECTOR      a detector line (whatever else) -> stop of the series (d)(1)
  HARNESS       the json is absent, binary_sha256 != FS10 abfded5e, or the form differs (env KYTY_GUEST_ARGS / KYTY_FRAME_TRACE /
                KYTY_GPU_HANG_ABORT_S / KYTY_GPU_CLOCK_PIN / KYTY_GPU_MARKERS, any KYTY_REC / KYTY_GAME_PATCH / KYTY_FIX_* / KYTY_TEST_* key,
                '--vulkan-validation true') -> stop of the series, question to the lead (not a tag of the form 630 (g))
  INTERFERENCE  no entry line, entry_s None or > 60, a death marker, a frame >= 1 s after the entry, or sum_dt < 90 s (the process
                ended before) -> not in N, the series goes on; the 5th stops it (d)(2)
  COUNTED       the entry line, entry_s <= 60, sum_dt >= 90 000 000 us, 0 death markers (so 0 '--- Error ---', 0 'Unhandled host
                exception'), 0 frames >= 1 s after the entry, the binary and the form of 630 (g)
Members of item 620 (g)(1)-(2) (item 620 (d): a new harness of the track F with tags without video carries them), given by post_f26c.sh:
  --disp-after F  the line of dispstate.py after 'lock released'; not 'dispstate ON' -> INTERFERENCE (DISPLAY_OFF) unless DETECTOR
  --tempo-rc N    the exit code of tempo_f26c.py (0 PASS); read only for a COUNTED tag: N != 0 -> TEMPO (stop of the series, question
                  to the lead - item 620 (g)(2)); for other classes a row
usage:
  python f26c_read.py <tag> [--json OUT]                   reads C:/kyty/f287/f26c/{log_<tag>.txt, stdout_<tag>.txt, <tag>.json}
  python f26c_read.py --log LOG [--stdout S] [--run-json J] [--name N] [--json OUT]    (fixtures, positive controls; .xz accepted)
  python f26c_read.py --set-load <tag>.json <run dir>       item 632 (v)(2): the field host_load {before, after, layer} into the json
  python f26c_read.py --table [--dir D]                    the table of D/runs/b25_*/read.json and the series line (exit 1 on a stop)
ASCII only."""
import glob
import json
import lzma
import os
import re
import sys

G = 'C:/kyty/f287/f26c'
TB = 'abfded5ea629ea70b0307540248c79e699485d5d2008ea047bd939729a5ed3fe'
SIGS = (b'There are too many objects/batches', b'command_buffer_writer.ppr.cpp', b'pc=0x00000009004a020e')
E = b'Level has started: intro_next'
LVL = b'Level has started:'
DEATH = (b'Unhandled exception:', b'--- Fatal Error ---', b'--- Error ---', b'GpuHangAbort:', b'ErrorDeviceLost', b'Unhandled host exception')
FT = re.compile(rb'^FrameTrace: n=(\d+) dt_us=(\d+)')
SUM_MIN_US = 90 * 1000 * 1000
FRAME_MAX_US = 1000 * 1000
ENTRY_MAX_S = 60.0
INTERF_STOP = 5
TAGS = 55
INVENTORY = 5
N_RULE = 60
OVER = 0.5
RX_OVER = re.compile(r'^hostload: over05 (\d+) ')
RX_BUSY = re.compile(r"\('<app>', \d+, ([0-9.]+)\)")


def layer_of(rundir):
    """Item 632 (v)(2), (v)(4): HOST_LOAD - a foreign process above 0.5 CPU s/s in the host load line before or after the tag; CLEAN -
    the lines exist and name none; tags without the lines (b25_01..b25_10): the gate line of procload.txt 'clean (no process above
    0.50' -> CLEAN (the gate of those tags was 0.5); else UNKNOWN."""
    lines = {}
    for k in ('hostload_before', 'hostload_after'):
        p = os.path.join(rundir, k + '.txt')
        if os.path.exists(p):
            lines[k] = open(p, encoding='ascii', errors='replace').read().strip().split('\n')[0]
    if lines:
        over = []
        for k, l in sorted(lines.items()):
            m = RX_OVER.match(l)
            if not m:
                return 'UNKNOWN', lines
            over.append(int(m.group(1)))
        return ('HOST_LOAD' if any(over) else 'CLEAN'), lines
    p = os.path.join(rundir, 'procload.txt')
    if os.path.exists(p):
        g = open(p, encoding='ascii', errors='replace').read().strip().split('\n')
        last = g[-1] if g else ''
        lines['procload'] = last
        if last.startswith('procload: clean (no process above 0.50 '):
            return 'CLEAN', lines
    return 'UNKNOWN', lines


FORM = {'KYTY_GUEST_ARGS': '-lvl intro_next', 'KYTY_FRAME_TRACE': 'lite', 'KYTY_GPU_HANG_ABORT_S': '8', 'KYTY_GPU_CLOCK_PIN': '1',
        'KYTY_GPU_MARKERS': '0'}
FORBID_PREFIX = ('KYTY_REC', 'KYTY_GAME_PATCH', 'KYTY_FIX_', 'KYTY_TEST_')


def opener(p):
    return lzma.open(p, 'rb') if p.endswith('.xz') else open(p, 'rb', buffering=1 << 22)


def scan(path, is_log):
    r = dict(lines=0, sig=[0, 0, 0], sig_first=None, entry_ln=None, entries=0, frames=0, sum_us=0, max_us=0, max_n=None,
             long_frames=0, death={}, death_first=None, next_level_ln=None, error_lines=0, host_exc=0, pre_max_us=0, pre_long=0)
    if not path or not os.path.exists(path):
        r['missing'] = True
        return r
    open_entry = False
    n = 0
    with opener(path) as f:
        for line in f:
            n += 1
            for k, s in enumerate(SIGS):
                if s in line:
                    r['sig'][k] += 1
                    if r['sig_first'] is None:
                        r['sig_first'] = n
            for d in DEATH:
                if d in line:
                    key = d.decode()
                    r['death'][key] = r['death'].get(key, 0) + 1
                    if r['death_first'] is None:
                        r['death_first'] = n
            if b'--- Error ---' in line:
                r['error_lines'] += 1
            if b'Unhandled host exception' in line:
                r['host_exc'] += 1
            if not is_log:
                continue
            if LVL in line:
                if E in line:
                    r['entries'] += 1
                    if r['entry_ln'] is None:
                        r['entry_ln'] = n
                        open_entry = True
                        continue
                if open_entry:
                    open_entry = False
                    r['next_level_ln'] = n
                continue
            if r['entry_ln'] is None and line.startswith(b'FrameTrace: n='):
                m = FT.match(line)
                if m:
                    d = int(m.group(2))
                    r['pre_max_us'] = max(r['pre_max_us'], d)
                    r['pre_long'] += d >= FRAME_MAX_US
                continue
            if open_entry and line.startswith(b'FrameTrace: n='):
                m = FT.match(line)
                if m:
                    d = int(m.group(2))
                    r['frames'] += 1
                    r['sum_us'] += d
                    if d > r['max_us']:
                        r['max_us'] = d
                        r['max_n'] = int(m.group(1))
                    if d >= FRAME_MAX_US:
                        r['long_frames'] += 1
    r['lines'] = n
    return r


def form_problems(j):
    if j is None:
        return ['no json']
    out = []
    if j.get('binary_sha256') != TB:
        out.append('binary %s' % (j.get('binary_sha256') or '-')[:8])
    env = j.get('env') or {}
    for k, v in FORM.items():
        if env.get(k) != v:
            out.append('%s=%s' % (k, env.get(k)))
    for k in env:
        if k.startswith(FORBID_PREFIX):
            out.append('forbidden %s' % k)
    cmd = j.get('cmdline') or []
    for i, a in enumerate(cmd[:-1]):
        if a == '--vulkan-validation' and cmd[i + 1] != 'false':
            out.append('validation')
    return out


def read(name, log, stdout, run_json, require_form=True, disp_after=None, tempo_rc=None, rundir=None):
    lg = scan(log, True)
    so = scan(stdout, False)
    j = None
    if run_json and os.path.exists(run_json):
        j = json.load(open(run_json, encoding='utf-8'))
    att = ((j or {}).get('attempts') or [{}])[0] if j else {}
    entry_s = att.get('started_s')
    det = [a + b for a, b in zip(lg['sig'], so['sig'])]
    death = dict(lg['death'])
    for k, v in so['death'].items():
        death['stdout ' + k] = v
    fp = form_problems(j) if require_form else []
    reasons = []
    if lg.get('missing'):
        reasons.append('no log')
    if lg['entry_ln'] is None:
        reasons.append('no entry line')
    if require_form and (entry_s is None or entry_s > ENTRY_MAX_S):
        reasons.append('entry_s %s > %.0f or none' % (entry_s, ENTRY_MAX_S))
    if death:
        reasons.append('death %s' % ','.join('%s x%d' % (k, v) for k, v in sorted(death.items())))
    if lg['long_frames']:
        reasons.append('%d frames >= 1 s after the entry (max %d us at n %s)' % (lg['long_frames'], lg['max_us'], lg['max_n']))
    if lg['sum_us'] < SUM_MIN_US:
        reasons.append('sum_dt %.1f s < 90 s' % (lg['sum_us'] / 1e6))
    if disp_after is not None and not disp_after.startswith('dispstate ON'):
        reasons.append('DISPLAY_OFF after the tag (%s)' % disp_after[:40])
    if sum(det):
        cls = 'DETECTOR'
    elif fp:
        cls = 'HARNESS'
    elif reasons:
        cls = 'INTERFERENCE'
    elif tempo_rc not in (None, 0):
        cls = 'TEMPO'
        reasons.append('tempo rc %s' % tempo_rc)
    else:
        cls = 'COUNTED'
    return dict(tag=name, cls=cls, detector=det, detector_first_line=lg['sig_first'] or so['sig_first'], entry_line=lg['entry_ln'],
                entries=lg['entries'], entry_s=entry_s, frames=lg['frames'], sum_dt_s=round(lg['sum_us'] / 1e6, 1),
                max_dt_us=lg['max_us'], max_dt_n=lg['max_n'], long_frames=lg['long_frames'], death=death,
                error_lines=lg['error_lines'] + so['error_lines'], host_exc=lg['host_exc'] + so['host_exc'],
                next_level_line=lg['next_level_ln'], log_lines=lg['lines'], reasons=reasons, form=fp,
                pre_entry_max_dt_us=lg['pre_max_us'], pre_entry_long_frames=lg['pre_long'],
                binary=(j or {}).get('binary_sha256'), hold_s=att.get('hold_s'), hold_exit=att.get('hold_exit'),
                outcome=att.get('outcome'), launched=(j or {}).get('launched'), finished=(j or {}).get('finished'),
                log=log, stdout=stdout, json=run_json, disp_after=disp_after, tempo_rc=tempo_rc,
                layer=layer_of(rundir)[0] if rundir else None, load_lines=layer_of(rundir)[1] if rundir else None)


def show(r):
    print('tag %s' % r['tag'])
    print('  CLASS %s' % r['cls'])
    print('  detector strings (too many / writer.ppr.cpp / pc) %d / %d / %d, first line %s' % (tuple(r['detector']) + (r['detector_first_line'],)))
    print('  entry line %s (entries %d), entry_s %s, next level line %s' % (r['entry_line'], r['entries'], r['entry_s'], r['next_level_line']))
    print('  after the entry: frames %d, sum dt %.1f s, max dt %d us (n %s), frames >= 1 s %d' % (r['frames'], r['sum_dt_s'], r['max_dt_us'], r['max_dt_n'], r['long_frames']))
    print('  row (not a member): before the entry max dt %d us, frames >= 1 s %d' % (r['pre_entry_max_dt_us'], r['pre_entry_long_frames']))
    print('  death markers %s; --- Error --- %d; Unhandled host exception %d' % (r['death'] or 0, r['error_lines'], r['host_exc']))
    print('  binary %s; hold_s %s; hold_exit %s; outcome %s; form problems %s' % ((r['binary'] or '-')[:8], r['hold_s'], r['hold_exit'], r['outcome'], r['form'] or 0))
    print('  display after %s; tempo rc %s' % (r['disp_after'], r['tempo_rc']))
    print('  host load layer %s (item 632): %s' % (r.get('layer'), r.get('load_lines')))
    if r['reasons']:
        print('  reasons: %s' % '; '.join(r['reasons']))


def table(g=G):
    rows = []
    for p in sorted(glob.glob(g + '/runs/b25_*/read.json')):
        if os.path.basename(os.path.dirname(p)).count('.'):
            continue
        rows.append(json.load(open(p, encoding='ascii')))
    print('| tag | binary | hold s | frames | sum dt s | max dt us | detector | class | layer | reasons |')
    print('|---|---|---|---|---|---|---|---|---|---|')
    for r in rows:
        print('| %s | %s | %s | %d | %.1f | %d | %d/%d/%d | %s | %s | %s |' % (r['tag'], (r['binary'] or '-')[:8], r['hold_s'], r['frames'], r['sum_dt_s'],
              r['max_dt_us'], r['detector'][0], r['detector'][1], r['detector'][2], r['cls'], r.get('layer') or '-', '; '.join(r['reasons']) or '-'))
    c = {k: sum(1 for r in rows if r['cls'] == k) for k in ('COUNTED', 'INTERFERENCE', 'DETECTOR', 'HARNESS', 'TEMPO')}
    stop = 'DETECTOR_STOP' if c['DETECTOR'] else 'HARNESS_STOP' if c['HARNESS'] else 'TEMPO_STOP' if c['TEMPO'] else 'INTERFERENCE_STOP' if c['INTERFERENCE'] >= INTERF_STOP \
        else 'COMPLETE' if c['COUNTED'] + INVENTORY >= N_RULE else 'GOING'
    print('SERIES tags %d counted %d interference %d detector %d harness %d tempo %d; N = %d inventory + %d = %d of %d; state %s'
          % (len(rows), c['COUNTED'], c['INTERFERENCE'], c['DETECTOR'], c['HARNESS'], c['TEMPO'], INVENTORY, c['COUNTED'], INVENTORY + c['COUNTED'], N_RULE, stop))
    lay = {k: sum(1 for r in rows if r['cls'] == 'COUNTED' and r.get('layer') == k) for k in ('CLEAN', 'HOST_LOAD', 'UNKNOWN')}
    print('LAYERS of the counted tags (item 632 (g)): CLEAN %d HOST_LOAD %d UNKNOWN %d' % (lay['CLEAN'], lay['HOST_LOAD'], lay['UNKNOWN']))
    return stop


def set_load(jpath, rundir):
    j = json.load(open(jpath, encoding='utf-8'))
    lay, lines = layer_of(rundir)
    j['host_load'] = dict(layer=lay, before=lines.get('hostload_before'), after=lines.get('hostload_after'), item='ROADMAP s122 item 632 (v)(2)')
    with open(jpath, 'w', encoding='utf-8') as f:
        json.dump(j, f, indent=2)
    print('host_load field written: layer %s' % lay)
    return 0


def main(argv):
    opt = lambda k, d=None: argv[argv.index(k) + 1] if k in argv else d  # noqa: E731
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == '--set-load':
        return set_load(argv[1], argv[2])
    if argv[0] == '--table':
        stop = table(opt('--dir', G))
        return 0 if stop in ('GOING', 'COMPLETE') else 1
    if argv[0] == '--log':
        r = read(opt('--name', 'log'), opt('--log'), opt('--stdout'), opt('--run-json'), require_form=bool(opt('--run-json')))
    else:
        t = argv[0]
        da = open(opt('--disp-after'), encoding='ascii', errors='replace').read().strip() if opt('--disp-after') else None
        tr = int(opt('--tempo-rc')) if opt('--tempo-rc') is not None else None
        r = read(t, '%s/log_%s.txt' % (G, t), '%s/stdout_%s.txt' % (G, t), '%s/%s.json' % (G, t), disp_after=da, tempo_rc=tr,
                 rundir='%s/runs/%s' % (G, t))
    show(r)
    if opt('--json'):
        with open(opt('--json'), 'w', encoding='ascii') as f:
            json.dump(r, f, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
