"""Session 67, item 1: enter Sky Garden without a human, through the guest's own command line.

    python C:/kyty/s120/enter_scene.py <tag> [flags] [KYTY_X=value ...]

Until session 66 the only way into Sky Garden was the user playing for ~298 s (224 s of them in the
desert). runtimeLinker.cpp handed the guest argc=1 / argv[0]="KytyEmu" although EntryParams holds
argv[3], and the eboot parses about thirty engine options (-lvl, -sequence, -room, -skipIntro,
-perfDisplay, -debugSettings). Session 67 passes them through KYTY_GUEST_ARGS, so this script is
the unattended launch_play.py: it starts the emulator with "-lvl underwater_aerial_garden",
watches the log for the level markers and reports the wall clock of each one.

Acceptance (session 67): the scene is stable in <= 90 s. "Stable" is the definition sky_auto.py
already used - 90 consecutive FrameTrace lines with draws >= 3000, i.e. the garden proper and not
the loading tunnel.

Flags:
    --level <name>        level for the default guest arguments and for the log markers
                          (default underwater_aerial_garden)
    --guest-args "<text>" whole KYTY_GUEST_ARGS value; overrides --level for the command line but
                          not for the markers ("@" / "@<path>" read an args file, see
                          runtimeLinker.cpp)
    --gates "<text>"      gate file text (default: the text of --gates-file)
    --gates-file <path>   default C:/kyty/s120/gates_base.txt, written by gen_gates.py. Session 63
                          rule: a name missing from the gate file KEEPS its state, so the base text
                          pins every gate and knob explicitly instead of being empty.
    --attempts <n>        counted attempts (default 3)
    --timeout <s>         per attempt, from process start to "stable" (default 240)
    --stable-draws <n>    draws per frame that count as being in the scene (default 3000, the
                          Sky Garden figure of sky_auto.py; the desert, -lvl intro_next, settles
                          at about 755 draws and 59.7 FPS, so it needs --stable-draws 500)
    --hold <s>            after success, keep the game running this long (default 0 = close at once)
    --warmup-first        run one extra, uncounted attempt first: the first entry after a fresh
                          build hangs (2 of 2 in session 61, rule of sessions 54/61)
    --rec                 record the video (KYTY_REC); off by default, an entry run does not need
                          360 MB of mp4 and NVENC costs frame time
    --no-install          run the already installed binary instead of C:/kyty/build/install/...
    --no-smi              do not sample the GPU clocks with nvidia-smi
    --no-cpuclk           do not sample the CPU clocks / host load with cpuclk.py
    --emu-arg=<arg>       session 102: one more emulator argument, appended after the fixed ones
                          (repeatable; default none).  Write it with "=" - "--emu-arg=--rd" - or
                          argparse takes a value that starts with "--" for an option of its own.
                          The M5 capture passes --rd (pred/01_m5_bench.md section 4).
    --pred <path>         session 79, item 3.4: the pre-registration this run is covered by. Its
                          sha256, byte count, mtime and ctime are read BEFORE the emulator starts
                          and written into <tag>.json as "prereg". Session 77's audit item C10 -
                          "nothing but a filesystem mtime anchors the ordering" - is discharged by
                          this: the hash is inside an artefact the run itself produces, so editing
                          the pre-registration afterwards is detectable. A missing file is fatal,
                          not a warning: a run that claims a pre-registration must have one.

Artefacts in C:/kyty/s120: log_<tag>.txt, stdout_<tag>.txt, <tag>.json (schema of launch_run.py,
plus an "attempts" list), gpuclk_<tag>.csv, and log_<tag>_a<n>.txt / stdout_<tag>_a<n>.txt for
every attempt that did not reach the scene.

Before the binary is installed and the emulator is started, the idle of the machine is
sampled with nvidia-smi and written to <tag>.json as "pre_run" (guards.py check 0).
Session 67 measured every one of its runs against someone else's game on the GPU, which
cost 19.68 % of gpu_busy_us and 9.48 % of cpu_gpu_us.

KYTY_GPU_TIME is NOT set: PacketsWanted() is false while the GPU time profiler is on, so it would
silently turn the record thread off (see the header of launch_run.py).

This script never presses a key and never touches RenderDoc.
"""
import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import statistics
import subprocess
import sys
import time
from run_safety99 import failure_marker

ROOT = pathlib.Path('C:/kyty/s121')
EMU = pathlib.Path.home() / 'OneDrive' / 'Desktop' / 'ps5 em'
BUILD = pathlib.Path('C:/kyty/build')
SMI_QUERY = ('timestamp,clocks.sm,clocks.mem,utilization.gpu,power.draw,temperature.gpu,'
             'clocks_throttle_reasons.active')
STABLE_FRAMES = 90
STABLE_DRAWS = 3000  # Sky Garden; overridden by --stable-draws
FAILURES = (b'GpuHangAbort:', b'ErrorDeviceLost', b'Unhandled exception:')
RE_FRAME = re.compile(rb' n=(\d+)')
RE_DRAWS = re.compile(rb' draws=(\d+)')

PRE_RUN_SAMPLES = 5        # samples of the idle machine, 0.4 s apart: 2 s in total
PRE_RUN_INTERVAL = 0.4
PRE_RUN_QUERY = ('utilization.gpu', 'power.draw', 'memory.used', 'clocks.sm')

# Session 78: the CPU-side parallel of the nvidia-smi logger.  0.5 Hz and pinned to CCD1 by
# cpuclk.py itself, so it cannot share a core with the threads dapin=1 puts on CCD0.
CPU_SAMPLER = 'cpuclk.py'
CPU_INTERVAL = 2.0
HOST_CENSUS_TOP = 20


def rotate_log():
    """_kyty.txt -> _kyty.prev.txt before a launch, exactly as run.sh does.

    The emulator truncates its log itself (spdlog basic_file_sink with truncate=true), but only
    once it reaches Log::Initialize. Reading a file that still holds the previous run would latch
    onto that run's "LevelDocument Loaded" and report a scene entered before the game even started,
    so the file is moved away first and the tail starts from an empty one. Nothing is deleted: the
    previous run stays in _kyty.prev.txt, and every attempt of this script is copied to
    log_<tag>_a<n>.txt before the next one rotates it.
    """
    source = EMU / '_kyty.txt'
    # Session 98: after a GPU execution hang the dead process keeps its handles (so _kyty.txt
    # stays locked) until the driver's TDR resets the GPU, ~60 s here (TdrDelay 60).  trig98a's
    # harness died on exactly that when it launched attempt 2 - so wait up to 180 s, then give up.
    deadline = time.time() + 180.0
    waited = False
    while source.exists():
        try:
            shutil.move(str(source), str(EMU / '_kyty.prev.txt'))
            break
        except PermissionError:
            if time.time() > deadline:
                raise
            if not waited:
                print('note: _kyty.txt is still locked (a hung process awaiting TDR?) - waiting',
                      flush=True)
                waited = True
            time.sleep(2.0)
    if waited:
        print('note: _kyty.txt released', flush=True)


class Tail:
    """Reads a log that was just rotated away, from the beginning; survives a later truncation."""

    def __init__(self, path):
        self.path = path
        self.position = 0
        self.pending = b''

    def lines(self):
        if not self.path.exists():
            return []
        size = self.path.stat().st_size
        if size < self.position:  # the emulator recreated the file
            self.position, self.pending = 0, b''
        with self.path.open('rb') as stream:
            stream.seek(self.position)
            data = self.pending + stream.read()
            self.position = stream.tell()
        rows = data.split(b'\n')
        self.pending = rows.pop()
        return rows


def sample_host():
    """One-shot census of the host: every process, its CPU seconds and working set.

    Taken once, before the install, like the GPU idle sample.  Get-Process is ~0.5 s and is
    never run again during the measurement, so it cannot perturb a block.  The competing
    hypothesis for the between-run variance is the host background set, and until now the
    record held only the processes that had the GPU open.
    """
    script = ('Get-Process | Where-Object {$_.CPU -ne $null} | '
              'Sort-Object CPU -Descending | '
              'Select-Object -First %d Name,Id,CPU,WS | ConvertTo-Json -Compress'
              % HOST_CENSUS_TOP)
    try:
        done = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command',
                               script], capture_output=True, text=True, timeout=60,
                              creationflags=0x08000000)
        top = json.loads(done.stdout) if done.stdout.strip() else []
        if isinstance(top, dict):
            top = [top]
        count = subprocess.run(['powershell', '-NoProfile', '-NonInteractive', '-Command',
                                '(Get-Process).Count'], capture_output=True, text=True,
                               timeout=60, creationflags=0x08000000)
        total = int(count.stdout.strip()) if count.stdout.strip().isdigit() else None
    except Exception as error:                       # noqa: BLE001 - never fail a run for this
        print('pre_run: host census unavailable (%s)' % error, flush=True)
        return dict(available=False, error=str(error))
    rows = [dict(name=row.get('Name'), pid=row.get('Id'),
                 cpu_s=round(row.get('CPU') or 0.0, 1),
                 ws_mib=round((row.get('WS') or 0) / 1048576.0, 1)) for row in top]
    names = sorted({(row['name'] or '').lower() for row in rows})
    print('pre_run: host %s processes, top by CPU: %s'
          % (total, ', '.join('%s %.0fs' % (r['name'], r['cpu_s']) for r in rows[:6])),
          flush=True)
    return dict(available=True, process_count=total, top=rows, top_names=names,
                sampled_at=time.strftime('%Y-%m-%dT%H:%M:%S'))


def sample_machine():
    """The idle of the machine, sampled BEFORE anything of ours touches the GPU.

    Session 67 measured all twelve of its runs while someone else's game was running
    (divinum.exe: 23 % of the GPU and 67 W with our emulator not even started; without it the
    machine idles at 3 % and 30 W).  gpu_busy_us is the distance between the top-of-pipe and the
    bottom-of-pipe timestamp of our OWN command buffers, so every microsecond another client
    preempts us is counted as ours: the clean control run lvl67e came out 19.68 % below lvl67b on
    gpu_busy_us and 9.48 % below on cpu_gpu_us, at 0.01 % different draws per frame.

    The rule "check nvidia-smi before a series of runs" has been in CLAUDE.md since session 30,
    but it was a rule for a human and it was not followed.  This function makes it a machine
    check: what it returns goes into <tag>.json as "pre_run", and guards.py check 0 turns it
    into a PASS/FAIL.

    Returns the "pre_run" section; never raises.  Without nvidia-smi it returns
    {"available": false} and the run continues - a missing watchdog must not cost a run.
    """
    # The arguments go as a list.  A composite --query-gpu=a,b,c is mangled when it travels
    # through the shell this harness is driven from, but subprocess hands it over untouched.
    gpu = ['nvidia-smi', '--query-gpu=' + ','.join(PRE_RUN_QUERY),
           '--format=csv,noheader,nounits']
    columns = [[] for _ in PRE_RUN_QUERY]
    try:
        for index in range(PRE_RUN_SAMPLES):
            if index:
                time.sleep(PRE_RUN_INTERVAL)
            done = subprocess.run(gpu, capture_output=True, text=True, timeout=30,
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
        listing = subprocess.run(['nvidia-smi', '--query-compute-apps=pid,process_name',
                                  '--format=csv'],
                                 capture_output=True, text=True, timeout=30,
                                 creationflags=0x08000000)
    except (OSError, ValueError, IndexError, subprocess.SubprocessError) as error:
        print('pre_run: nvidia-smi unavailable (%s); the machine watchdog cannot run' % error,
              flush=True)
        return dict(available=False, error=str(error))

    # used_gpu_memory is deliberately NOT queried: this driver answers "[N/A]" for every process,
    # so the column carries no information and only makes the line ambiguous to split.
    apps = []
    for line in listing.stdout.splitlines()[1:]:
        line = line.strip()
        if not line or line.lower().startswith(('pid', 'no running processes')):
            continue
        pid, _, name = line.partition(',')
        apps.append(dict(pid=int(pid) if pid.strip().isdigit() else pid.strip(),
                         name=name.strip()))

    def middle(values, digits=1):
        return round(statistics.median(values), digits) if values else None

    section = dict(gpu_util_median=middle(columns[0]),
                   gpu_power_median=middle(columns[1]),
                   gpu_memory_used_mib=int(max(columns[2])) if columns[2] else None,
                   gpu_apps=apps,
                   host=sample_host(),
                   sampled_at=time.strftime('%Y-%m-%dT%H:%M:%S'))
    print('pre_run: GPU %s %% busy, %s W, %s MiB used, SM %s MHz, %d process(es) on the GPU'
          % (section['gpu_util_median'], section['gpu_power_median'],
             section['gpu_memory_used_mib'], middle(columns[3], 0), len(apps)), flush=True)
    if (section['gpu_util_median'] or 0) > 10:
        print('pre_run: WARNING - the GPU is already busy; find out what is using it before '
              'measuring anything (guards.py check 0 will fail this run)', flush=True)
    return section


def sample_prereg(path):
    """Fingerprint the pre-registration BEFORE the emulator starts (session 79, item 3.4).

    Session 78 left eight pre-registrations whose only ordering anchor was mtime == ctime on the
    filesystem, and whose own "WRITTEN <time>" lines were typed from memory and are wrong by up to
    43 minutes (s78 FACTS 6).  Session 77's audit item C10 asked for something stronger.  The run
    itself now carries the hash: <tag>.json is written by this script after the run, from a digest
    taken before it, so a pre-registration edited after the fact no longer matches its own runs.
    """
    file = pathlib.Path(path)
    if not file.exists():
        raise SystemExit('--pred %s does not exist: a run that claims a pre-registration must '
                         'have one' % file)
    data = file.read_bytes()
    stat = file.stat()
    section = dict(path=str(file), bytes=len(data),
                   sha256=hashlib.sha256(data).hexdigest(),
                   mtime=time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(stat.st_mtime)),
                   ctime=time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(stat.st_ctime)),
                   mtime_ctime_delta_s=round(stat.st_mtime - stat.st_ctime, 6),
                   read_at=time.strftime('%Y-%m-%dT%H:%M:%S'))
    print('prereg: %s  %d bytes  sha256 %s  mtime %s  mtime-ctime %+.3f s'
          % (file.name, section['bytes'], section['sha256'][:16], section['mtime'],
             section['mtime_ctime_delta_s']), flush=True)
    return section


def start_smi(path):
    try:
        handle = path.open('wb')
        return subprocess.Popen(['nvidia-smi', '--query-gpu=' + SMI_QUERY, '--format=csv',
                                 '-lms', '500'],
                                stdout=handle, stderr=subprocess.STDOUT,
                                creationflags=0x08000000), handle
    except OSError as error:
        print('nvidia-smi not started:', error, flush=True)
        return None, None


def stop_smi(process, handle):
    if process is None:
        return
    try:
        process.kill()
        process.wait(timeout=10)
    except Exception:
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)],
                       capture_output=True, creationflags=0x08000000)
    if handle is not None:
        handle.close()


def start_cpu(path):
    sampler = ROOT / CPU_SAMPLER
    if not sampler.exists():
        print('cpuclk not started: %s is not there' % sampler, flush=True)
        return None, None
    try:
        handle = path.open('wb')
        return subprocess.Popen([sys.executable, str(sampler), str(path),
                                 '--interval', str(CPU_INTERVAL)],
                                stdout=subprocess.DEVNULL, stderr=handle,
                                creationflags=0x08000000), handle
    except OSError as error:
        print('cpuclk not started:', error, flush=True)
        return None, None


def stop_cpu(process, handle):
    """cpuclk writes its CSV itself and line-buffers it, so a hard kill loses nothing."""
    if process is None:
        return
    try:
        process.kill()
        process.wait(timeout=10)
    except Exception:                                 # noqa: BLE001
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)],
                       capture_output=True, creationflags=0x08000000)
    if handle is not None:
        handle.close()


def kill_game(game):
    """Hard kill: by pid first (never disturb another emulator), image name as the last resort."""
    if game.poll() is not None:
        return
    subprocess.run(['taskkill', '/F', '/T', '/PID', str(game.pid)],
                   capture_output=True, creationflags=0x08000000)
    try:
        game.wait(timeout=20)
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/F', '/IM', 'kyty_emulator.exe'],
                       capture_output=True, creationflags=0x08000000)
        try:
            game.wait(timeout=20)
        except subprocess.TimeoutExpired:
            game.kill()


def close_game(game):
    """WM_CLOSE, so the video, its index and the pipeline cache are finished properly."""
    import ctypes
    user = ctypes.WinDLL('user32')
    callback = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    user.GetWindowThreadProcessId.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_ulong)]
    user.PostMessageW.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_size_t, ctypes.c_ssize_t]

    @callback
    def visit(hwnd, _):
        owner = ctypes.c_ulong()
        user.GetWindowThreadProcessId(hwnd, ctypes.byref(owner))
        if owner.value == game.pid:
            user.PostMessageW(hwnd, 0x10, 0, 0)
        return True

    user.EnumWindows(visit, None)
    try:
        game.wait(timeout=40)
    except subprocess.TimeoutExpired:
        print('still alive 40 s after WM_CLOSE, killing', flush=True)
        kill_game(game)


def attempt(label, tag, options, env, args, index):
    """One launch. Returns a dict describing how it ended."""
    print('--- %s: launching' % label, flush=True)
    rotate_log()
    log_tail = Tail(EMU / '_kyty.txt')
    started = time.monotonic()
    stdout = (EMU / '_run_stdout.txt').open('wb')  # truncated here, so the tail starts at 0 too
    out_tail = Tail(EMU / '_run_stdout.txt')
    game = subprocess.Popen(args, cwd=EMU, env=env, stdout=stdout, stderr=subprocess.STDOUT,
                            creationflags=0x08000000)
    result = dict(label=label, attempt=index, pid=game.pid, level=options.level,
                  guest_args=env.get('KYTY_GUEST_ARGS'), document_s=None, started_s=None,
                  stable_s=None, stable_frame=None, outcome='running', detail=None)
    document = start_marker = stable = None
    run = 0
    frame = 0
    marker_document = ('LevelDocument Loaded: %s' % options.level).encode()
    marker_started = ('GuestOut: Level has started: %s' % options.level).encode()
    def consume():
        """One pass over whatever both logs grew by. Sets result['outcome'] when it is decided."""
        nonlocal document, start_marker, stable, run, frame
        for line in log_tail.lines() + out_tail.lines():
            for bad in FAILURES:
                if bad in line and result['outcome'] == 'running':
                    result.update(outcome=bad.decode().strip(':'),
                                  detail=line[:400].decode('utf8', 'replace'))
                    print('FAIL:', result['detail'], flush=True)
            if result['outcome'] != 'running':
                return
            if b'GpuWaitSlow:' in line:  # session 58: read acopy= here before anything else
                print('note:', line[:400].decode('utf8', 'replace'), flush=True)
            if document is None and marker_document in line:
                document = time.monotonic() - started
                result['document_s'] = round(document, 1)
                print('%.1f s  LevelDocument Loaded: %s' % (document, options.level), flush=True)
            elif start_marker is None and marker_started in line:
                start_marker = time.monotonic() - started
                result['started_s'] = round(start_marker, 1)
                print('%.1f s  Level has started: %s' % (start_marker, options.level), flush=True)
            elif line.startswith(b'FrameTrace:'):
                found = RE_FRAME.search(line)
                if found:
                    frame = int(found[1])
                if document is not None and start_marker is not None:
                    draws = RE_DRAWS.search(line)
                    run = run + 1 if draws and int(draws[1]) >= STABLE_DRAWS else 0
                    if run >= STABLE_FRAMES and stable is None:
                        stable = time.monotonic() - started
                        result.update(stable_s=round(stable, 1), stable_frame=frame, outcome='ok')
                        print('%.1f s  scene stable at frame %d (%d frames with draws >= %d)'
                              % (stable, frame, STABLE_FRAMES, STABLE_DRAWS), flush=True)
                        return

    try:
        while True:
            exited = game.poll() is not None
            consume()
            if result['outcome'] != 'running':
                break
            if exited:
                # Drain once more: the reason the emulator died is in the lines it wrote last.
                time.sleep(1)
                consume()
                if result['outcome'] == 'running':
                    result.update(outcome='exited', detail='exit code %s' % game.returncode)
                break
            if time.monotonic() - started > options.timeout:
                result.update(outcome='timeout',
                              detail='%.0f s, frame %d, document=%s started=%s'
                                     % (options.timeout, frame, result['document_s'],
                                        result['started_s']))
                print('FAIL: timeout after %.0f s (frame %d)' % (options.timeout, frame),
                      flush=True)
                break
            time.sleep(0.5)
    finally:
        if result['outcome'] == 'ok':
            if options.hold > 0:
                print('holding the run for %d s' % options.hold, flush=True)
                hold_t0 = time.monotonic()
                deadline = hold_t0 + options.hold
                while time.monotonic() < deadline and game.poll() is None:
                    time.sleep(1)
                # Session 97: record HOW the hold ended.  bf96b's processes died inside it and
                # the run was written 'ok' with no exit code, which FACTS s96 read as a freeze.
                result['hold_exit'] = game.poll()
                result['hold_s'] = round(time.monotonic() - hold_t0, 1)
                if result['hold_exit'] is not None:
                    print('WARNING: the game ENDED inside the hold after %.1f s, returncode %s '
                          '(0x%08x)' % (result['hold_s'], result['hold_exit'],
                                        result['hold_exit'] & 0xffffffff), flush=True)
            close_game(game)
        else:
            kill_game(game)
        stdout.close()
        time.sleep(2)
    return result


def copy_artifacts(tag, suffix=''):
    for source, target in ((EMU / '_kyty.txt', ROOT / ('log_%s%s.txt' % (tag, suffix))),
                           (EMU / '_run_stdout.txt', ROOT / ('stdout_%s%s.txt' % (tag, suffix)))):
        if source.exists():
            shutil.copy2(source, target)
            print('copied', target, flush=True)


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('tag')
    parser.add_argument('--level', default='underwater_aerial_garden')
    parser.add_argument('--guest-args', default=None)
    parser.add_argument('--gates', default=None)
    parser.add_argument('--gates-file', default=str(ROOT / 'gates_base.txt'))
    parser.add_argument('--attempts', type=int, default=3)
    parser.add_argument('--timeout', type=float, default=240)
    parser.add_argument('--stable-draws', type=int, default=STABLE_DRAWS)
    parser.add_argument('--hold', type=int, default=0)
    parser.add_argument('--warmup-first', action='store_true')
    parser.add_argument('--rec', action='store_true')
    parser.add_argument('--no-install', action='store_true')
    parser.add_argument('--no-smi', action='store_true')
    parser.add_argument('--no-cpuclk', action='store_true')
    parser.add_argument('--pred', default=None,
                        help='pre-registration file; its sha256 goes into <tag>.json')
    parser.add_argument('--emu-arg', action='append', default=[],
                        help='extra emulator argument, repeatable; write --emu-arg=--rd')
    parser.add_argument('extra', nargs='*', help='KYTY_X=value pairs for the environment')
    options = parser.parse_args()
    globals()['STABLE_DRAWS'] = options.stable_draws
    tag = options.tag

    gates = options.gates
    if gates is None:
        path = pathlib.Path(options.gates_file)
        if path.exists():
            gates = ' '.join(path.read_text(encoding='utf8').split())
        else:
            raise SystemExit('no gate text: %s is missing, run gen_gates.py or pass --gates'
                             % path)
    (ROOT / 'gates.req').write_text(gates)
    (ROOT / 'sample.req').write_text('0')

    guest_args = options.guest_args if options.guest_args is not None else '-lvl ' + options.level
    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env.update(KYTY_FRAME_TRACE='lite', KYTY_GPU_HANG_ABORT_S='8',
               KYTY_GATE_FILE=str(ROOT / 'gates.req'),
               KYTY_SAMPLE_GATE=str(ROOT / 'sample.req'),
               KYTY_QUEUE_TRACE='1',
               KYTY_GUEST_ARGS=guest_args)
    if options.rec:
        env['KYTY_REC'] = str(ROOT / ('rec_%s.mp4' % tag))
    if os.environ.get('KYTY_GATE_SCHEDULE'):
        env['KYTY_GATE_SCHEDULE'] = os.environ['KYTY_GATE_SCHEDULE']
    for pair in options.extra:
        key, value = pair.split('=', 1)
        env[key] = value

    # Session 72 fix: this note was written unconditionally, so a run that passed
    # KYTY_GPU_TIME=1 (gpt71a) still claimed the record thread was live. Read env, not notes -
    # and now notes agrees with env.
    gpu_time = env.get('KYTY_GPU_TIME', '0') not in ('0', '', None)
    notes = ['KYTY_GPU_TIME=%s: the record thread is OFF (PacketsWanted false), so cpu/draw, '
             'dt_us and gpu_busy_us of this run compare with nothing' % env['KYTY_GPU_TIME']
             if gpu_time else
             'KYTY_GPU_TIME unset: the record thread stays live (PacketsWanted)',
             'guest command line: %s' % guest_args,
             'stable = %d consecutive FrameTrace lines with draws >= %d'
             % (STABLE_FRAMES, STABLE_DRAWS)]
    # Session 67 correction: the idle of the machine is sampled BEFORE the binary is installed
    # and before the nvidia-smi logger starts, so guards.py check 0 can refuse a run that shared
    # the GPU with something else - that mistake cost session 67 19.68 % of gpu_busy_us.
    prereg = sample_prereg(options.pred) if options.pred else None
    pre_run = sample_machine()

    if not options.no_install:
        source = BUILD / 'install/kyty_emulator.exe'
        if not source.exists():
            raise SystemExit('no built emulator at %s (use --no-install)' % source)
        shutil.copy2(source, EMU / 'kyty_emulator.exe')
        mapping = BUILD / 'kyty_emulator_clang_lld_link.map'
        if mapping.exists():
            shutil.copy2(mapping, ROOT / ('%s.map' % tag))
        notes.append('installed %s' % source)
    else:
        notes.append('ran the already installed binary (--no-install)')

    args = [str(EMU / 'kyty_emulator.exe'), '--screen-width', '1280', '--screen-height', '720',
            '--user-name', 'Player', '--user-id', '1000', '--present-mode', 'Fifo',
            '--vblank-frequency', '60', '--console-language', '1',
            '--vulkan-validation', 'false', '--shader-validation', 'false',
            '--shader-optimization-type', 'Size', '--shader-log-direction', 'File',
            '--shader-log-folder', '_Shaders', '--command-buffer-dump', 'false',
            '--command-buffer-dump-folder', '_Buffers', '--printf-direction', 'File',
            '--printf-output-file', '_kyty.txt', '--spirv-debug-printf', 'false',
            '--game', str(EMU / 'games/PPSA21564-app')]
    # Session 102: extra emulator arguments (the M5 capture's --rd), after the fixed ones;
    # main.cpp ParseArgs is order-independent.  They land in <tag>.json through cmdline.
    args += options.emu_arg
    if options.emu_arg:
        notes.append('extra emulator arguments: %s' % ' '.join(options.emu_arg))

    smi, smi_handle = (None, None)
    if not options.no_smi:
        smi, smi_handle = start_smi(ROOT / ('gpuclk_%s.csv' % tag))
    cpu, cpu_handle = (None, None)
    if not options.no_cpuclk:
        cpu, cpu_handle = start_cpu(ROOT / ('cpuclk_%s.csv' % tag))

    attempts = []
    success = None
    # Session 80: the real launch instant.  `started` below is stamped in the finally: block and
    # is therefore the run's END - it was read as a start by FACTS s79 section 7.
    launched = time.strftime('%Y-%m-%dT%H:%M:%S')
    try:
        plan = ([('warmup', 0)] if options.warmup_first else []) + \
               [('attempt %d' % (n + 1), n + 1) for n in range(options.attempts)]
        for label, index in plan:
            run_env = dict(env)
            # Session 57/58: a corrupt driver pipeline cache is the first suspect when the entry
            # dies with ErrorDeviceLost, so retry without it.
            if any(a['outcome'] == 'ErrorDeviceLost' for a in attempts):
                run_env['KYTY_PIPELINE_CACHE'] = '0'
            result = attempt(label, tag, options, run_env, args, index)
            result['pipeline_cache_off'] = run_env.get('KYTY_PIPELINE_CACHE') == '0'
            attempts.append(result)
            if label == 'warmup':
                copy_artifacts(tag, '_warmup')
                print('warmup finished (%s), not counted' % result['outcome'], flush=True)
                # Session 99: a failed warmup is a result, not permission for another process.
                if (result['outcome'] != 'ok' or result.get('hold_exit') is not None
                        or (result.get('hold_s') or 0) < options.hold):
                    print('STOP: warmup failed; counted process will not launch', flush=True)
                    break
                warmup_paths = [ROOT / ('%s_%s_warmup.txt' % (stream, tag))
                                for stream in ('log', 'stdout')]
                if not all(path.is_file() for path in warmup_paths):
                    print('STOP: warmup output absent; counted process will not launch', flush=True)
                    break
                warmup_failed = False
                for warmup_path in warmup_paths:
                    with warmup_path.open('rb') as warmup_stream:
                        if any(failure_marker(line) for line in warmup_stream):
                            warmup_failed = True
                            break
                if warmup_failed:
                    print('STOP: warmup failure marker; counted process will not launch', flush=True)
                    break
                continue
            if result['outcome'] == 'ok':
                success = result
                break
            copy_artifacts(tag, '_a%d' % index)
    finally:
        stop_smi(smi, smi_handle)
        stop_cpu(cpu, cpu_handle)
        copy_artifacts(tag)
        try:
            sys.path.insert(0, str(ROOT))
            from launch_run import parse_schedule
            period, start, arms = parse_schedule(env.get('KYTY_GATE_SCHEDULE'))
        except Exception:
            period, start, arms = 0, 0, []
        (ROOT / ('%s.json' % tag)).write_text(json.dumps(dict(
            tag=tag,
            binary_sha256=hashlib.sha256((EMU / 'kyty_emulator.exe').read_bytes()).hexdigest(),
            # `started` is stamped HERE, in the finally: block, so it is the run's END.
            # Kept unchanged so every json in the record keeps meaning the same thing; use
            # `launched` for the start and `finished` for the end.  (Session 80.)
            started=time.strftime('%Y-%m-%dT%H:%M:%S'),
            launched=launched,
            finished=time.strftime('%Y-%m-%dT%H:%M:%S'),
            cmdline=args,
            env={k: v for k, v in env.items() if k.startswith(('KYTY_', 'VK_'))},
            schedule=env.get('KYTY_GATE_SCHEDULE') or '',
            arms=arms,
            phases=[],
            notes='; '.join(notes),
            pre_run=pre_run,
            prereg=prereg,
            attempts=attempts, gates=gates, schedule_period=period, schedule_start=start,
            guest_args=guest_args, hold_s=options.hold,
            cpuclk_requested=not options.no_cpuclk,
            gpuclk=None if smi is None else str(ROOT / ('gpuclk_%s.csv' % tag)),
            cpuclk=None if cpu is None else str(ROOT / ('cpuclk_%s.csv' % tag))), indent=2))

    print()
    for row in attempts:
        print('%-10s %-16s document=%s s started=%s s stable=%s s %s'
              % (row['label'], row['outcome'], row['document_s'], row['started_s'],
                 row['stable_s'], row['detail'] or ''), flush=True)
    if success is None:
        print('VERDICT: no attempt reached %s' % options.level, flush=True)
        raise SystemExit(1)
    print('VERDICT: %s in %.1f s - %s (acceptance <= 90 s)'
          % (options.level, success['stable_s'],
             'PASS' if success['stable_s'] <= 90 else 'FAIL'), flush=True)


if __name__ == '__main__':
    main()
