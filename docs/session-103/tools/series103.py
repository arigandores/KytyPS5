"""Session 103 entry series driver (sealed C:/kyty/s103/pred/01_bvh_cap_series.md s2).

    python C:/kyty/s103/series103.py [--skip-warmup] [--start N]

Warm-up ent103_warm (+ ent103_warm2 if it fails), then ent103_01..67 one at a time with
enter_scene.py --attempts 1 --hold 20; technical failures are replaced at the end (<= 3); the
series stops at the second hang. Progress: C:/kyty/s103/series103.log.
"""
import subprocess
import sys
import time

sys.path.insert(0, 'C:/kyty/s103')
import bvh103  # noqa: E402

ROOT = 'C:/kyty/s103'
LOG = ROOT + '/series103.log'


def say(text):
    line = '[%s] %s' % (time.strftime('%H:%M:%S'), text)
    print(line, flush=True)
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')


def run(tag, extra=()):
    cmd = [sys.executable, ROOT + '/enter_scene.py', tag, '--attempts', '1', '--hold', '20',
           '--pred', bvh103.PRED] + list(extra)
    t0 = time.time()
    with open('%s/series_%s.stdout.txt' % (ROOT, tag), 'w', encoding='utf-8') as out:
        rc = subprocess.run(cmd, stdout=out, stderr=subprocess.STDOUT).returncode
    e = bvh103.entry(tag)
    say('%s rc=%d %.0fs class=%s armed=%d trips=%d near=%d slow=%d max_dt=%.2fs %s' % (
        tag, rc, time.time() - t0, e['class'], e['armed'], e['trips'], e['near'], e['slow'],
        e['max_dt_us'] / 1e6, '; '.join(e['markers'])[:200]))
    return e


def main():
    skip_warmup = '--skip-warmup' in sys.argv
    start = int(sys.argv[sys.argv.index('--start') + 1]) if '--start' in sys.argv else 1
    say('series start, seal %s' % bvh103.seal_sha())
    if not skip_warmup:
        w = run('ent103_warm', ['--timeout', '900'])
        if w['class'] != 'ok':
            run('ent103_warm2', ['--timeout', '900'])
    hangs, technical, index, target = 0, 0, start, bvh103.COUNTED
    while index <= target:
        tag = 'ent103_%02d' % index
        e = run(tag)
        if e['class'] == 'hang':
            hangs += 1
            if hangs >= 2:
                say('STOP: second hang (sealed stopping rule)')
                break
        elif e['class'] == 'technical':
            technical += 1
            if technical <= bvh103.MAX_REPLACEMENTS:
                target += 1
                say('technical failure %d, replacement appended (target %d)' % (technical, target))
        index += 1
    entries = [bvh103.entry('ent103_%02d' % i) for i in range(1, index)]
    v = bvh103.verdict(entries)
    say('VERDICT %s items=%s trips_entries=%d worst_dt=%.2fs hangs=%s technical=%s' % (
        v['verdict'], v['items'], len(v['trip_entries']), v['worst_dt_us'] / 1e6, v['hangs'],
        v['technical']))


if __name__ == '__main__':
    main()
