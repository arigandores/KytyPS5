# Session 140 step 2 (HPP-268): the session-140 file of this role with the names moved (port140.py) - no change of meaning.
"""idle142 - ONE idle criterion for the chain and the scorer, plus the GPU row of the hold (session 126 step 0,
HPP-83; C:/kyty/s124/idle124.py with the name moved - nothing else changed; ROADMAP s.122 item 25 (zh),
item 40 (e)(5); session 124 was the port of C:/kyty/s123/idle123.py).

The idle part is idle123.py unchanged in meaning (only the name moved):
  * sample_gpu()  - exactly the "pre_run" measurement of enter_scene.py (same query, same PRE_RUN_SAMPLES and
                    PRE_RUN_INTERVAL, "[N/A]" cells stay out of their median, the median rounded to one digit - the
                    value that lands in <tag>.json and that the scorer reads);
  * idle_ok()     - exactly the admission check of map122.py (`pre_run.gpu_util_median <= IDLE_GPU_MAX`, a missing
                    or non-numeric median is NOT idle).
enter_scene.py imports both, so the "pre_run" section in <tag>.json is produced by this code, and with
--require-idle it refuses to start the emulator when idle_ok() is false.  The chain calls this file before the lock
with the same code.  The scorer of the session (step 7) must carry an idle check whose text equals idle_ok() below;
test_idle142.py checks map122.idle_ok against it on every fixture.

New in session 124 (item 40 (e)(5), MINOR-5 of audit 123): the GPU utilisation DURING the hold is written beside the
run as the "hold_gpu" section of <tag>.json - a ROW, NOT A GUARD (nothing refuses or admits on it until a ROADMAP line
says so).  It is read from the run's own nvidia-smi logger (gpuclk_<tag>.csv, one row per 0.5 s) between the two
wall stamps enter_scene.py takes at the start and at the end of the hold (stamp(), the logger's own format):
  * hold_gpu(text, t_from, t_to) - rows with t_from <= timestamp <= t_to; median of utilization.gpu and of
                    power.draw (rounded as the pre_run medians), the row counts, "[N/A]" cells out of their median;
  * hold_gpu_file(path, t_from, t_to) - the same from the file; never raises (a broken row list is a row too).
The emulator itself is the main GPU load of the hold, so this median is not an idle measure; it records whether
something else could have shared the GPU (compare with the run's own history, never with a threshold).

    python C:/kyty/s142/idle142.py [--json <out.json>]
    exit 0 IDLE, 1 BUSY, 2 UNAVAILABLE (no numeric median); one line "idle142: ..." on stdout.
"""
import datetime
import json
import statistics
import subprocess
import sys
import time

PRE_RUN_SAMPLES = 5        # samples of the idle machine, 0.4 s apart: 2 s in total
PRE_RUN_INTERVAL = 0.4
PRE_RUN_QUERY = ('utilization.gpu', 'power.draw', 'memory.used', 'clocks.sm')
IDLE_GPU_MAX = 10          # map122.py IDLE_GPU_MAX; admission is median <= IDLE_GPU_MAX
SMI_TIME_FORMAT = '%Y/%m/%d %H:%M:%S.%f'   # the timestamp column of nvidia-smi --format=csv (gpuclk_<tag>.csv)
UTIL_COLUMN = 3            # timestamp, clocks.sm, clocks.mem, utilization.gpu, power.draw, ... (enter_scene SMI_QUERY)
POWER_COLUMN = 4


def middle(values, digits=1):
    return round(statistics.median(values), digits) if values else None


def sample_gpu(run=subprocess.run, sleep=time.sleep, log=print):
    """The GPU part of enter_scene.py sample_machine(), unchanged in meaning.

    Returns the "pre_run" GPU fields, or {"available": False, "error": ...}; never raises.  `run`/`sleep`/`log` are
    injectable for the offline fixtures.
    """
    # The arguments go as a list.  A composite --query-gpu=a,b,c is mangled when it travels
    # through the shell this harness is driven from, but subprocess hands it over untouched.
    gpu = ['nvidia-smi', '--query-gpu=' + ','.join(PRE_RUN_QUERY),
           '--format=csv,noheader,nounits']
    columns = [[] for _ in PRE_RUN_QUERY]
    try:
        for index in range(PRE_RUN_SAMPLES):
            if index:
                sleep(PRE_RUN_INTERVAL)
            done = run(gpu, capture_output=True, text=True, timeout=30,
                       creationflags=0x08000000)
            if done.returncode != 0:
                raise OSError('nvidia-smi exited %d (%s)'
                              % (done.returncode, (done.stderr or done.stdout).strip()[:200]))
            row = done.stdout.strip().splitlines()[0].split(',')
            for cell, column in zip(row, columns):
                try:
                    column.append(float(cell.strip()))
                except ValueError:
                    pass          # "[N/A]": the field simply stays out of its median
        listing = run(['nvidia-smi', '--query-compute-apps=pid,process_name',
                       '--format=csv'],
                      capture_output=True, text=True, timeout=30,
                      creationflags=0x08000000)
    except (OSError, ValueError, IndexError, subprocess.SubprocessError) as error:
        log('pre_run: nvidia-smi unavailable (%s); the machine watchdog cannot run' % error)
        return dict(available=False, error=str(error))

    # used_gpu_memory is deliberately NOT queried: this driver answers "[N/A]" for every process,
    # so the column carries no information and only makes the line ambiguous to split.
    apps = []
    for line in (listing.stdout or '').splitlines()[1:]:
        line = line.strip()
        if not line or line.lower().startswith(('pid', 'no running processes')):
            continue
        pid, _, name = line.partition(',')
        apps.append(dict(pid=int(pid) if pid.strip().isdigit() else pid.strip(),
                         name=name.strip()))
    return dict(gpu_util_median=middle(columns[0]),
                gpu_power_median=middle(columns[1]),
                gpu_memory_used_mib=int(max(columns[2])) if columns[2] else None,
                gpu_sm_mhz_median=middle(columns[3], 0),
                gpu_util_samples=list(columns[0]),
                gpu_apps=apps)


def idle_ok(meta):
    """map122.py idle_ok, same text: `meta` is a <tag>.json dict (its "pre_run" section is judged)."""
    v = (meta.get('pre_run') or {}).get('gpu_util_median')
    return isinstance(v, (int, float)) and v <= IDLE_GPU_MAX


def verdict(section):
    """IDLE / BUSY / UNAVAILABLE for a "pre_run" section; exit codes 0 / 1 / 2."""
    if idle_ok(dict(pre_run=section)):
        return 'IDLE', 0
    v = (section or {}).get('gpu_util_median')
    if isinstance(v, (int, float)):
        return 'BUSY', 1
    return 'UNAVAILABLE', 2


def stamp(now=None):
    """A wall stamp in the logger's own format, to the millisecond (enter_scene.py: start and end of the hold)."""
    now = datetime.datetime.now() if now is None else now
    return now.strftime(SMI_TIME_FORMAT)[:-3]


def cell_number(cell):
    """'6 %' -> 6.0, '29.93 W' -> 29.93; '[N/A]' or anything else -> None."""
    word = cell.strip().split(' ')[0] if cell.strip() else ''
    try:
        return float(word)
    except ValueError:
        return None


def hold_gpu(text, t_from, t_to):
    """The "hold_gpu" row: the logger rows inside [t_from, t_to] (both ends inclusive), their medians and counts.

    A ROW, NOT A GUARD (item 40 (e)(5)).  `available` is False when a stamp is missing or unreadable, or when no row
    falls inside the window; the medians are then None.
    """
    row = dict(available=False, source='gpuclk csv (nvidia-smi -lms 500)', hold_from=t_from, hold_to=t_to,
               rows=0, util_rows=0, gpu_util_median=None, gpu_power_median=None, gpu_util_max=None, note='a row, not a guard')
    try:
        start = datetime.datetime.strptime(t_from, SMI_TIME_FORMAT)
        end = datetime.datetime.strptime(t_to, SMI_TIME_FORMAT)
    except (TypeError, ValueError):
        row['error'] = 'hold stamps missing or unreadable'
        return row
    util, power = [], []
    for line in (text or '').splitlines():
        cells = line.split(',')
        if len(cells) <= POWER_COLUMN:
            continue
        try:
            when = datetime.datetime.strptime(cells[0].strip(), SMI_TIME_FORMAT)
        except ValueError:
            continue          # the header line, an error line of the logger
        if not start <= when <= end:
            continue
        row['rows'] += 1
        value = cell_number(cells[UTIL_COLUMN])
        if value is not None:
            util.append(value)
        watts = cell_number(cells[POWER_COLUMN])
        if watts is not None:
            power.append(watts)
    row['util_rows'] = len(util)
    row['gpu_util_median'] = middle(util)
    row['gpu_power_median'] = middle(power)
    row['gpu_util_max'] = max(util) if util else None
    row['available'] = bool(util)
    if not util:
        row['error'] = 'no logger row with a numeric utilization.gpu inside the hold'
    return row


def hold_gpu_file(path, t_from, t_to):
    """hold_gpu() of the logger file; never raises (enter_scene.py calls it inside its finally: block)."""
    try:
        with open(path, 'rb') as stream:
            text = stream.read().decode('utf-8', 'replace')
    except (OSError, TypeError) as error:
        row = hold_gpu('', t_from, t_to)
        row['error'] = 'logger file unreadable (%s)' % error
        return row
    return hold_gpu(text, t_from, t_to)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    out = argv[argv.index('--json') + 1] if '--json' in argv else None
    section = sample_gpu(log=lambda s: print(s, flush=True))
    section['sampled_at'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    word, code = verdict(section)
    print('idle142: gpu_util_median=%s (samples %s) threshold <= %d -> %s'
          % (section.get('gpu_util_median'), section.get('gpu_util_samples'), IDLE_GPU_MAX, word), flush=True)
    if out:
        with open(out, 'w', encoding='utf-8', newline='\n') as stream:
            json.dump(dict(pre_run=section, verdict=word), stream, indent=2)
    return code


if __name__ == '__main__':
    sys.exit(main())
