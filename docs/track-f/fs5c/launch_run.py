"""Session 67: measured run on the desert that is reachable without a user.

    python C:/kyty/s112/launch_run.py <tag> <phases.json> [flags] [KYTY_X=value ...]

Flags (anything starting with "--"; everything else of the form NAME=VALUE goes to the environment):
    --gputime      turn KYTY_GPU_TIME=1 back on (OFF by default, see the warning below)
    --no-install   do not copy C:/kyty/build/install/kyty_emulator.exe over the emulator folder
    --no-map       do not copy the 29 MB linker map next to the artefacts
    --validation   --vulkan-validation true (same as KYTY_MEASURE_VALIDATION=1)
    --no-rec       do not record the video (KYTY_REC unset)
    --no-smi       do not sample the GPU clocks with nvidia-smi
    --no-watch     do not start tools/watch_emulator.py

KYTY_KEYS drives the game to the playable desert (intro_next); measure_run.py waits
KYTY_MEASURE_OFFSET presents after "LevelDocument Loaded: intro_next" and then walks the phases of
<phases.json>: a list of [name, gate-file text, sample 0/1, length in presents].

=============================================================================================
WARNING - THE NUMBERS OF THIS SCRIPT ARE NOT COMPARABLE WITH THE DESERT RUNS OF SESSIONS 60-65.
=============================================================================================
The launch_run.py of sessions 54-65 set KYTY_GPU_TIME=1 unconditionally. But

    bool CommandBuffer::PacketsWanted() const {                       // context.cpp
        return m_recorder != nullptr && Common::Gates::Enabled(Gate::RecordPackets) &&
               !GpuTimeProfiler::Enabled();
    }

so with KYTY_GPU_TIME set the record thread receives no packets at all: every desert run of
sessions 60-65 was de facto a run with recpack off, while Sky Garden (started through
launch_play.py, which never set KYTY_GPU_TIME) ran with recpack on.  The two scenes were therefore
measured in two different configurations of the renderer.

Session 67 makes this a deliberate choice: KYTY_GPU_TIME is OFF unless --gputime is given, so the
desert runs the same write path as Sky Garden.  Consequences:
  * per-draw CPU, FPS and every rec_* counter of a default s67 desert run must NOT be compared
    against s60-s65 desert numbers - only against other s67 runs;
  * "GpuTime:", "GpuTime-kind:" and "GpuTime-top:" lines are absent unless --gputime is given;
  * with --gputime the run is back in the old configuration (recpack effectively off) and its
    numbers are comparable with s60-s65 again - and only with those.

Other deliberate changes against s64/s65:
  * nvidia-smi samples the SM/memory clocks, utilisation, power, temperature and the throttle
    reasons every 500 ms into gpuclk_<tag>.csv (run_ab.sh did this, launch_run.py never did) - a
    throttled GPU invalidates an A/B, and without the file there is no way to tell afterwards;
  * KYTY_GATE_SCHEDULE (A/B microblocks, session 66 methodology) and KYTY_GUEST_ARGS (the guest's
    own command line) are passed through and written into <tag>.json;
  * before anything of ours touches the GPU the idle of the machine is sampled with
    nvidia-smi (2 s of utilisation/power/memory plus the list of processes on the GPU) into
    the "pre_run" section of <tag>.json; guards.py check 0 fails a run that started on a
    busy GPU.  Session 67 measured all twelve of its runs against someone else's game and
    paid 19.68 % of gpu_busy_us and 9.48 % of cpu_gpu_us for it;
  * KYTY_SRT_NATIVE was dropped from the default environment: no such variable exists in the tree
    any more (it was a no-op in s64/s65 too);
  * _kyty.txt is moved to _kyty.prev.txt before the launch (run.sh always did this, launch_run.py
    never did). The emulator truncates its own log, but only when it reaches Log::Initialize, and
    until then measure_run.py is reading the PREVIOUS run - whose "LevelDocument Loaded:
    intro_next" would set intro=0 and shift the whole measurement window.
"""
import hashlib
import json
import os
import pathlib
import shutil
import statistics
import subprocess
import sys
import time

ROOT = pathlib.Path('C:/kyty/s112')
EMU = pathlib.Path('C:/kyty/KytyPS5/ps5 em')
BUILD = pathlib.Path('C:/kyty/build')
SMI_QUERY = ('timestamp,clocks.sm,clocks.mem,utilization.gpu,power.draw,temperature.gpu,'
             'clocks_throttle_reasons.active')

PRE_RUN_SAMPLES = 5        # samples of the idle machine, 0.4 s apart: 2 s in total
PRE_RUN_INTERVAL = 0.4
PRE_RUN_QUERY = ('utilization.gpu', 'power.draw', 'memory.used', 'clocks.sm')


def parse_schedule(raw):
    """KYTY_GATE_SCHEDULE="<N>[+<start>]:<arm>|<arm>[|...]" exactly as gates.cpp reads it.

    Returns (period, start, [arm text, ...]); period 0 means "the emulator will ignore this".
    """
    if not raw:
        return 0, 0, []
    head, _, tail = raw.partition(':')
    if not tail:
        return 0, 0, []
    start = 0
    if '+' in head:
        head, _, start_text = head.partition('+')
        start = int(start_text) if start_text.isdigit() else 0
    if not head.isdigit():
        return 0, 0, []
    period = int(head)
    # gates.cpp stops after SCHEDULE_ARMS_MAX arms and keeps those, and rejects the whole schedule
    # if any arm it took is empty or >= SCHEDULE_TEXT_MAX bytes.
    arms = tail.split('|')[:8]
    if period == 0 or period > 100000 or any(len(arm) == 0 or len(arm) >= 512 for arm in arms):
        return 0, 0, []
    return period, start, arms


def sample_machine():
    """The idle of the machine, sampled BEFORE anything of ours touches the GPU.

    Session 67 measured all twelve of its runs while someone else's game was running
    (<app>: 23 % of the GPU and 67 W with our emulator not even started; without it the
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
                   sampled_at=time.strftime('%Y-%m-%dT%H:%M:%S'))
    print('pre_run: GPU %s %% busy, %s W, %s MiB used, SM %s MHz, %d process(es) on the GPU'
          % (section['gpu_util_median'], section['gpu_power_median'],
             section['gpu_memory_used_mib'], middle(columns[3], 0), len(apps)), flush=True)
    if (section['gpu_util_median'] or 0) > 10:
        print('pre_run: WARNING - the GPU is already busy; find out what is using it before '
              'measuring anything (guards.py check 0 will fail this run)', flush=True)
    return section


def start_smi(path):
    """nvidia-smi sampling the clocks every 500 ms; None if nvidia-smi is not on PATH."""
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
    """Kill the sampler by pid (never by image name: another nvidia-smi may be someone else's)."""
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


def main():
    argv = sys.argv[1:]
    flags = {arg for arg in argv if arg.startswith('--')}
    rest = [arg for arg in argv if not arg.startswith('--')]
    unknown = flags - {'--gputime', '--no-install', '--no-map', '--validation', '--no-rec',
                       '--no-smi', '--no-watch'}
    if unknown:
        raise SystemExit('unknown flags: %s' % ' '.join(sorted(unknown)))
    if len(rest) < 2:
        raise SystemExit(__doc__.splitlines()[2].strip())
    tag, phases_path = rest[0], pathlib.Path(rest[1])

    env = {k: v for k, v in os.environ.items() if not k.startswith('KYTY_')}
    env.update(KYTY_FRAME_TRACE='lite', KYTY_AV_TRACE='1',
               KYTY_ASYNC_COPY_GPU_WAIT='0', KYTY_DYNAMIC_STATE_CACHE='1',
               KYTY_PIPELINE_FAST_HASH='1', KYTY_DESCRIPTOR_REUSE='1',
               KYTY_KEYS='@2170:j,@2460:j',
               KYTY_GATE_FILE=str(ROOT / 'gates.req'),
               KYTY_QUEUE_TRACE='1', KYTY_GPU_HANG_ABORT_S='8',
               KYTY_SAMPLE_GATE=str(ROOT / 'sample.req'))
    if '--no-rec' not in flags:
        env['KYTY_REC'] = str(ROOT / ('rec_%s.mp4' % tag))
    if '--gputime' in flags:
        env['KYTY_GPU_TIME'] = '1'
    # The schedule and the guest command line come from this shell unless a KEY=VALUE overrides
    # them below; both are plain environment variables of the emulator.
    for name in ('KYTY_GATE_SCHEDULE', 'KYTY_GUEST_ARGS'):
        if os.environ.get(name):
            env[name] = os.environ[name]
    for pair in rest[2:]:
        key, value = pair.split('=', 1)
        env[key] = value

    offset = env.pop('KYTY_MEASURE_OFFSET', '7100')
    phase_len = env.pop('KYTY_MEASURE_PHASE', '300')
    max_s = env.pop('KYTY_MEASURE_MAX_S', '900')
    build = pathlib.Path(env.pop('KYTY_MEASURE_BUILD', str(BUILD)))
    validation = env.pop('KYTY_MEASURE_VALIDATION', '0') == '1' or '--validation' in flags
    for key in [key for key, value in env.items() if key.startswith('KYTY_') and value == 'unset']:
        del env[key]

    phases = json.loads(phases_path.read_text())
    (ROOT / 'sample.req').write_text('0')
    (ROOT / 'gates.req').write_text(phases[0][1])

    notes = []
    if '--gputime' in flags:
        notes.append('KYTY_GPU_TIME=1: PacketsWanted() is false, the record thread gets no '
                     'packets (recpack effectively off) - comparable with s60-s65, not with the '
                     's67 default')
    else:
        notes.append('KYTY_GPU_TIME unset (s67 default): recpack is live, unlike every desert run '
                     'of s60-s65 - do not compare per-draw CPU or FPS with those')
    if validation:
        notes.append('Vulkan validation on: timings are meaningless, correctness only')

    # Session 67 correction: the idle of the machine is sampled BEFORE the binary is installed
    # and before the nvidia-smi logger starts, so guards.py check 0 can refuse a run that shared
    # the GPU with something else - that mistake cost session 67 19.68 % of gpu_busy_us.
    pre_run = sample_machine()

    if '--no-install' not in flags:
        source = build / 'install/kyty_emulator.exe'
        if not source.exists():
            raise SystemExit('no built emulator at %s (use --no-install to run the installed one)'
                             % source)
        shutil.copy2(source, EMU / 'kyty_emulator.exe')
        notes.append('installed %s' % source)
    else:
        notes.append('ran the already installed binary (--no-install)')
    if '--no-map' not in flags:
        mapping = build / 'kyty_emulator_clang_lld_link.map'
        if mapping.exists():
            shutil.copy2(mapping, ROOT / ('%s.map' % tag))
        else:
            notes.append('no linker map at %s: samples_phase.py/direct_sites.py will not resolve '
                         'addresses' % mapping)

    args = [str(EMU / 'kyty_emulator.exe'), '--screen-width', '1280', '--screen-height', '720',
            '--user-name', 'Player', '--user-id', '1000', '--present-mode', 'Fifo',
            '--vblank-frequency', '60', '--console-language', '1',
            '--vulkan-validation', 'true' if validation else 'false',
            '--shader-validation', 'false', '--shader-optimization-type', 'Size',
            '--shader-log-direction', 'File', '--shader-log-folder', '_Shaders',
            '--command-buffer-dump', 'false', '--command-buffer-dump-folder', '_Buffers',
            '--printf-direction', 'File', '--printf-output-file', '_kyty.txt',
            '--spirv-debug-printf', 'false', '--game', str(EMU / 'games/PPSA21564-app')]

    period, start, arms = parse_schedule(env.get('KYTY_GATE_SCHEDULE'))
    if env.get('KYTY_GATE_SCHEDULE') and period == 0:
        notes.append('KYTY_GATE_SCHEDULE=%r does not parse: the emulator will ignore it'
                     % env['KYTY_GATE_SCHEDULE'])

    smi, smi_handle = (None, None)
    if '--no-smi' not in flags:
        smi, smi_handle = start_smi(ROOT / ('gpuclk_%s.csv' % tag))

    # Nothing is deleted: the previous run stays in _kyty.prev.txt (and in log_<previous tag>.txt).
    if (EMU / '_kyty.txt').exists():
        shutil.move(str(EMU / '_kyty.txt'), str(EMU / '_kyty.prev.txt'))

    try:
        with (EMU / '_run_stdout.txt').open('wb') as output:
            game = subprocess.Popen(args, cwd=EMU, env=env, stdout=output,
                                    stderr=subprocess.STDOUT, creationflags=0x08000000)
            meta = dict(
                tag=tag,
                binary_sha256=hashlib.sha256((EMU / 'kyty_emulator.exe').read_bytes()).hexdigest(),
                started=time.strftime('%Y-%m-%dT%H:%M:%S'),
                cmdline=args,
                env={k: v for k, v in env.items() if k.startswith(('KYTY_', 'VK_'))},
                schedule=env.get('KYTY_GATE_SCHEDULE') or '',
                arms=arms,
                phases=phases,
                notes='; '.join(notes),
                # the idle of the machine before the launch; guards.py check 0 reads it
                pre_run=pre_run,
                # extras beyond the schema, used by the other scripts of this folder
                pid=game.pid, phases_file=str(phases_path), schedule_period=period,
                schedule_start=start, guest_args=env.get('KYTY_GUEST_ARGS'),
                gpuclk=None if smi is None else str(ROOT / ('gpuclk_%s.csv' % tag)))
            (ROOT / ('%s.json' % tag)).write_text(json.dumps(meta, indent=2))

            if '--no-watch' not in flags:
                watcher_output = (ROOT / ('watch_%s.log' % tag)).open('wb')
                subprocess.Popen([sys.executable, 'C:/kyty/KytyPS5/tools/watch_emulator.py',
                                  str(game.pid), str(EMU / '_kyty.txt'),
                                  str(ROOT / ('hang_%s' % tag)),
                                  '--dump-tool', 'C:/kyty/s49/windows_hang_dump.exe',
                                  '--min-frame', '3000'],
                                 stdout=watcher_output, stderr=subprocess.STDOUT,
                                 creationflags=0x08000000)
            measure_output = (ROOT / ('measure_%s.log' % tag)).open('wb')
            measure = subprocess.Popen([sys.executable, str(ROOT / 'measure_run.py'),
                                        str(game.pid), tag, str(phases_path),
                                        'offset=' + offset, 'phase=' + phase_len,
                                        'max=' + max_s],
                                       stdout=measure_output, stderr=subprocess.STDOUT,
                                       creationflags=0x08000000)
            print('Game PID', game.pid, flush=True)
            print('Exit', game.wait(), flush=True)
            try:
                measure.wait(timeout=30)
            except subprocess.TimeoutExpired:
                measure.kill()
    finally:
        stop_smi(smi, smi_handle)

    # measure_run.py copies these too; repeat here so an aborted driver still leaves artefacts.
    time.sleep(2)
    for source, target in ((EMU / '_kyty.txt', ROOT / ('log_%s.txt' % tag)),
                           (EMU / '_run_stdout.txt', ROOT / ('stdout_%s.txt' % tag))):
        if source.exists():
            shutil.copy2(source, target)
            print('copied', target, flush=True)


if __name__ == '__main__':
    main()
