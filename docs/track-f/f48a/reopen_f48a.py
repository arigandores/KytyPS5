# F48a (HPP-830, ROADMAP p.748(d)): pass over the unique delta logs (agg_f32a.json of the F48a sweep, dup_of == None,
# in_f0 == None) for the reopening / parking witness lines of register rows WITH an outcome that the F0 key list and
# wit_f32a.py do not catch.  One regex per witness; per log: count, first 'line_no:text'; the run form (KYTY_* env and
# '--rd' / '--vulkan-validation' / '--shader-validation' in the first 8 MiB) is printed with the log so the reader can tell
# a stand / instrument / control run from the default form.
# Witnesses (row: register line of the reopening / parking condition):
#   f21_second   Ph21 FIXED (s108:1542): a second '--- Fatal Error ---' in one log (count >= 2 is printed per log)
#   f21_nested   Ph21 N4 F33d (s108:1544): 'nested_fatal'
#   f21_wait     Ph21 (s112): 'FixF21: wait_expired'
#   f24_mode1    Ph24 N2 F40b (s121:1691): 'FixF24: mode=1' (paired with f24_init below: mode=1 without init_owner / init)
#   f24_init     'FixF24: init_owner' or 'FixF24: init'
#   f24_open     'FixF24: open failed'
#   f24_long     'FixF24: pump_update_long'
#   f25_twice    Ph25 (s116:1633): 'FixF25: read failed twice'
#   f29_over     Ph29 (s122:1700): 'FixF29: overflow'
#   f20_unm      Ph20 (s126:1746): 'FixF20Stat:' line with unmatched=<n>, n > 0
#   pause_on     B32 (s106:1523): 'Pause: true' (>= 2 harness tags without KYTY_KEYS -> row by lead item)
#   fliphold     K5 harness (s106:1522): 'FlipHold' line with poll_us >= 500000
#   logstall     B36/B40 (s104:1493 (ii)), Ph27: 'LogAsync: stall'
#   bvhtrip      B1a/B1b (s92): 'BvhLoopCapTrip:'
#   b25          B25 (s102:1467): the assert line of B25 ('Assertion' / 'ASSERT:' with 'command buffer' text is not assumed:
#                the sweep marker b25_assert of ana_f32a.py is the reader; here only 'ASSERT:' is counted as a cross-check)
# Usage: python reopen_f48a.py <sweep_out> <binmap.tsv> <out.json>   (exit 3 lock, 4 STOP; read-only on logs)
import os, re, sys, json, lzma, hashlib, collections

LOCK = os.environ.get('F48A_LOCK', 'C:/kyty/SEALED_RUN.lock')
STOP = os.environ.get('F48A_STOP', 'C:/kyty/f287/STOP')
BLOCK = 8 << 20
NL = b'\n'
W = [
    ('f21_second', re.compile(rb'^--- Fatal Error ---')),
    ('f21_nested', re.compile(rb'nested_fatal')),
    ('f21_wait', re.compile(rb'FixF21: wait_expired')),
    ('f24_mode1', re.compile(rb'FixF24: mode=1')),
    ('f24_init', re.compile(rb'FixF24: init(_owner)?\b')),
    ('f24_open', re.compile(rb'FixF24: open failed')),
    ('f24_long', re.compile(rb'FixF24: pump_update_long')),
    ('f25_twice', re.compile(rb'FixF25: read failed twice')),
    ('f29_over', re.compile(rb'FixF29: overflow')),
    ('f20_unm', re.compile(rb'FixF20Stat:.*\bunmatched=([1-9]\d*)')),
    ('pause_on', re.compile(rb'Pause: true')),
    ('fliphold', re.compile(rb'FlipHold.*\bpoll_us=([5-9]\d{5}|\d{7,})\b')),
    ('logstall', re.compile(rb'LogAsync: stall')),
    ('bvhtrip', re.compile(rb'BvhLoopCapTrip:')),
    ('assert', re.compile(rb'ASSERT:')),
]
PRE = re.compile(rb'FixF2|nested_fatal|Fatal Error|Pause: true|FlipHold|LogAsync: stall|BvhLoopCapTrip|ASSERT:')
ENV = re.compile(rb'\b(KYTY_[A-Z0-9_]+)=([^\s,;\'"]*)')
FORM = re.compile(rb'--rd\b|--vulkan-validation true|--shader-validation true')
RE_BUILD = re.compile(rb'Fork build \S+ ([0-9a-f]{7,40})')


def gate():
    if os.path.exists(STOP):
        os._exit(4)
    if os.path.exists(LOCK):
        os._exit(3)


def opener(p):
    return lzma.open(p, 'rb') if p.endswith('.xz') else open(p, 'rb')


def scan_bytes(chunks):
    # chunks: iterable of bytes blocks; returns (per-witness [count, first], head_env, head_form, build, lines)
    res = {k: [0, None] for k, _ in W}
    head = b''
    rest = b''
    ln = 0
    for b in chunks:
        gate()
        if len(head) < (8 << 20):
            head += b[:(8 << 20) - len(head)]
        b = rest + b
        cut = b.rfind(NL)
        if cut < 0:
            rest = b
            continue
        body, rest = b[:cut + 1], b[cut + 1:]
        if PRE.search(body):
            for i, line in enumerate(body.split(NL)[:-1]):
                if not PRE.search(line):
                    continue
                for k, rx in W:
                    if rx.search(line):
                        res[k][0] += 1
                        if res[k][1] is None:
                            res[k][1] = '%d:%s' % (ln + i + 1, line[:200].decode('utf-8', 'replace'))
        ln += body.count(NL)
    if rest:
        for k, rx in W:
            if rx.search(rest):
                res[k][0] += 1
                if res[k][1] is None:
                    res[k][1] = '%d:%s' % (ln + 1, rest[:200].decode('utf-8', 'replace'))
        ln += 1
    env = sorted(set('%s=%s' % (a.decode(), v.decode('utf-8', 'replace')) for a, v in ENV.findall(head)))
    form = sorted(set(x.decode() for x in FORM.findall(head)))
    m = RE_BUILD.search(head)
    return res, env, form, (m.group(1).decode()[:7] if m else '?'), ln


def blocks(p):
    with opener(p) as fh:
        while True:
            b = fh.read(BLOCK)
            if not b:
                return
            yield b


def main():
    gate()
    out_dir, binmap, out = sys.argv[1], sys.argv[2], sys.argv[3]
    course = {}
    for l in open(binmap, encoding='utf-8'):
        x = l.rstrip('\n').split('\t')
        if x[0] not in ('9235a7ac', 'dac02fb9'):
            course[x[3]] = x[0]
    recs = [r for r in json.load(open(out_dir + '/agg_f32a.json', encoding='utf-8')) if not r['dup_of'] and not r['in_f0']]
    rows = []
    for r in recs:
        res, env, form, b, ln = scan_bytes(blocks(r['path']))
        build = r['build'] if r['build'] != '?' else b
        rows.append({'path': r['path'], 'build': build, 'course': course.get(build[:7]), 'levels': r['levels'], 'lines': ln,
                     'lines_agg': r['lines'], 'env': env, 'form': form, 'w': res})
    json.dump(rows, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    ok = True
    bad_lines = [x['path'] for x in rows if x['lines'] != x['lines_agg']]
    print('logs', len(rows), 'course', sum(1 for x in rows if x['course']), 'line count = sweep:', len(rows) - len(bad_lines), 'of', len(rows))
    if bad_lines:
        ok = False
        print('LINE COUNT MISMATCH', bad_lines[:5])
    for k, _ in W:
        hit = [x for x in rows if x['w'][k][0] > 0]
        hc = [x for x in hit if x['course']]
        print('%-11s logs %3d (course %3d) lines %6d' % (k, len(hit), len(hc), sum(x['w'][k][0] for x in hit)))
        for x in hit[:40]:
            print('    %s %s %s n=%d | form %s | env %s | %s' % (x['path'], x['build'], x['course'] or 'OTHER', x['w'][k][0], ','.join(x['form']) or '-',
                  ' '.join(e for e in x['env'] if not e.startswith('KYTY_FRAME_TRACE'))[:300], x['w'][k][1]))
    print('ALL OK' if ok else 'FAILED')
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
