"""Session 102, M5: run one of the qrenderdoc tools with the bench-side watchdogs of section 5.

    python C:/kyty/s102/m5_run.py find  --cap <rdc> --out <find.json>
    python C:/kyty/s102/m5_run.py equal --cap <rdc> --plan <plan.json> --out <equal.json>
    python C:/kyty/s102/m5_run.py bench --cap <rdc> --plan <plan.json> --out <bench.json> \
        --env RD_AUTO_EXTEND=1 --env RD_EQUAL=<equal.json>

(equal: arm A is replayed three times per item and V1, V2, V2s are compared with A1 - pred/02 s2;
bench: five arms, R = 20, extension +20 - pred/02 s4.  Both tools refuse unless the two seals match.)

pred/01_m5_bench.md section 5: "nothing else on the GPU (nvidia-smi --query-compute-apps shows no
other process with dedicated memory); clocks and temperature logged every 5 s for the whole
bench".  This wrapper:
  * refuses to start while kyty_emulator.exe or another qrenderdoc.exe is running;
  * records nvidia-smi --query-compute-apps and the GPU idle state before the run (on this
    driver used_gpu_memory reads [N/A] for every process, so the listing is recorded and judged by
    a human, never by this script);
  * logs clocks / temperature / power / utilisation / throttle reasons every 5 s to
    <out>.gpuclk.csv for the whole run;
  * runs qrenderdoc --python <tool> with RD_CAP / RD_PLAN / RD_OUT and any --env pairs, and kills
    it by PID if it outlives --timeout (qrenderdoc can hang on exit; the tools os._exit);
  * writes <out>.run.json: command, environment, sha256 of every tool file, exit code, wall time.
It never launches the game and never builds anything.
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path('C:/kyty/s102')
QRD = 'C:/Program Files/RenderDoc/qrenderdoc.exe'
TOOLS = {'find': ROOT / 'rd_m5_find.py', 'bench': ROOT / 'rd_m5_bench.py', 'equal': ROOT / 'rd_m5_equal.py'}
SMI_QUERY = ('timestamp,clocks.sm,clocks.mem,temperature.gpu,power.draw,utilization.gpu,'
             'clocks_throttle_reasons.active')
NO_WINDOW = 0x08000000


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def running(image):
    done = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq %s' % image, '/FO', 'CSV', '/NH'],
                          capture_output=True, text=True, creationflags=NO_WINDOW)
    return [line for line in done.stdout.splitlines() if image.lower() in line.lower()]


def smi(args):
    try:
        done = subprocess.run(['nvidia-smi'] + args, capture_output=True, text=True, timeout=30,
                              creationflags=NO_WINDOW)
        return done.stdout.strip()
    except (OSError, subprocess.SubprocessError) as error:
        return 'nvidia-smi unavailable: %s' % error


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('tool', choices=sorted(TOOLS))
    parser.add_argument('--cap', required=True)
    parser.add_argument('--plan', default=None)
    parser.add_argument('--out', required=True)
    parser.add_argument('--env', action='append', default=[], help='KEY=VALUE for the tool (RD_*)')
    parser.add_argument('--timeout', type=float, default=6 * 3600.0)
    parser.add_argument('--smi-interval-ms', type=int, default=5000)
    options = parser.parse_args()
    out = Path(options.out)
    run_json = Path(str(out) + '.run.json')
    for path in (out, run_json):
        if path.exists():
            raise SystemExit('refusing to overwrite %s' % path)
    if options.tool != 'find' and not options.plan:
        raise SystemExit('%s needs --plan' % options.tool)
    busy = running('kyty_emulator.exe') + running('qrenderdoc.exe')
    if busy:
        raise SystemExit('refusing to start: %s' % busy)

    env = dict(os.environ)
    env.update(RD_CAP=options.cap, RD_OUT=str(out).replace('\\', '/'))
    if options.plan:
        env['RD_PLAN'] = options.plan
    for pair in options.env:
        key, value = pair.split('=', 1)
        env[key] = value
    record = dict(tool=options.tool, script=str(TOOLS[options.tool]), cap=options.cap, plan=options.plan,
                  out=str(out), env={k: v for k, v in env.items() if k.startswith('RD_')},
                  tool_sha256={p.name: sha(p) for p in list(TOOLS.values()) + [ROOT / 'm5_rdlib.py', ROOT / 'm5_102.py',
                                                                                 ROOT / 'm5_plan.py']},
                  seal_sha256={p.name: sha(p) for p in (ROOT / 'pred/01_m5_bench.md', ROOT / 'pred/02_m5_addendum.md')},
                  pre_compute_apps=smi(['--query-compute-apps=pid,process_name,used_gpu_memory', '--format=csv']),
                  pre_gpu=smi(['--query-gpu=utilization.gpu,power.draw,memory.used,clocks.sm,temperature.gpu',
                               '--format=csv']),
                  started=time.strftime('%Y-%m-%dT%H:%M:%S'))
    print('pre-run GPU:', record['pre_gpu'].replace('\n', ' | '))
    clock_path = Path(str(out) + '.gpuclk.csv')
    handle = clock_path.open('wb')
    logger = subprocess.Popen(['nvidia-smi', '--query-gpu=' + SMI_QUERY, '--format=csv',
                               '-lms', str(options.smi_interval_ms)],
                              stdout=handle, stderr=subprocess.STDOUT, creationflags=NO_WINDOW)
    record['gpuclk'] = str(clock_path)
    t0 = time.time()
    tool = subprocess.Popen([QRD, '--python', str(TOOLS[options.tool])], env=env, creationflags=NO_WINDOW)
    try:
        record['exit_code'] = tool.wait(timeout=options.timeout)
        record['killed'] = False
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(tool.pid)], capture_output=True,
                       creationflags=NO_WINDOW)
        record['exit_code'] = None
        record['killed'] = True
    record['wall_s'] = round(time.time() - t0, 1)
    logger.kill()
    try:
        logger.wait(timeout=10)
    except subprocess.TimeoutExpired:
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(logger.pid)], capture_output=True,
                       creationflags=NO_WINDOW)
    handle.close()
    record['finished'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    record['output_exists'] = out.exists()
    record['output_sha256'] = sha(out) if out.exists() else None
    run_json.write_text(json.dumps(record, indent=1), encoding='utf-8')
    print('%s: exit %s%s, %.0f s -> %s' % (options.tool, record['exit_code'],
                                           ' (KILLED at timeout)' if record['killed'] else '',
                                           record['wall_s'], out))
    return 0 if record['exit_code'] == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
