"""F6f lead recount (HPP-378, ROADMAP p.287(v)(5)-(6), p.294(b)). Own code; does not import f6e_read.py.
Reads the five F6e logs (series 2) and stdout files; prints per tag: stub lines by symbol, ASSERT:, user_msg_param,
FixB9a: on, death-like markers, the last AudioPropagation: calls fields, FrameTrace rows, frames >= 1 s and >= 100 ms over
the whole log (a superset of the hold window), SourceCreate per FrameTrace row after 'Level has started' (rough variant)."""
import hashlib, re, sys

ROOT = 'C:/kyty/f287/f6e/'
TAGS = [('f6e_a1', 1), ('f6e_a2', 1), ('f6e_b1', 1), ('f6e_c1', 0), ('f6e_c2', 0)]
RX_STUB = re.compile(rb'Unresolved import stub called \[\d+\]:.*?symbol=(\S+)')
RX_DT = re.compile(rb'^FrameTrace: n=\d+ dt_us=(\d+)')
RX_KV = re.compile(rb'(\w+)=(\d+)')
DEATH = [b'Unhandled exception', b'DEVICE_LOST', b'device lost', b'Fatal error', b'EXCEPTION_ACCESS_VIOLATION']


def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


def scan(tag):
    p = ROOT + 'log_%s.txt' % tag
    r = dict(stubs={}, ap=0, asrt=0, umsg=0, fix=0, death={}, rows=0, k2=0, k3=0, rows_after=0, started=False,
             last=None, first_after=None, maxdt=0)
    with open(p, 'rb') as f:
        for line in f:
            if b'Unresolved import stub called' in line:
                m = RX_STUB.search(line)
                s = m.group(1).decode('latin1') if m else '?'
                r['stubs'][s] = r['stubs'].get(s, 0) + 1
                if b'AudioPropagation' in line:
                    r['ap'] += 1
            if b'ASSERT:' in line:
                r['asrt'] += 1
            if b'user_msg_param' in line:
                r['umsg'] += 1
            if line.startswith(b'FixB9a: on'):
                r['fix'] += 1
            for d in DEATH:
                if d in line:
                    r['death'][d.decode()] = r['death'].get(d.decode(), 0) + 1
            if b'Level has started' in line:
                r['started'] = True
            if line.startswith(b'AudioPropagation: calls'):
                kv = {k.decode(): int(v) for k, v in RX_KV.findall(line)}
                r['last'] = kv
                if r['started'] and r['first_after'] is None:
                    r['first_after'] = (kv, r['rows'])
            m = RX_DT.match(line)
            if m:
                dt = int(m.group(1))
                r['rows'] += 1
                r['maxdt'] = max(r['maxdt'], dt)
                if dt >= 1000000:
                    r['k2'] += 1
                if dt >= 100000:
                    r['k3'] += 1
    so = ROOT + '%s.stdout.txt' % tag
    with open(so, 'rb') as f:
        t = f.read()
    r['so_asrt'] = t.count(b'ASSERT:')
    r['so_stub'] = t.count(b'Unresolved import stub called')
    r['sha'] = sha(p)
    return r


def main():
    ok = True
    for tag, fix in TAGS:
        r = scan(tag)
        last = r['last'] or {}
        print('%s fix=%d log %s' % (tag, fix, r['sha'][:16]))
        print('  stubs log %d (AudioPropagation %d) by symbol %s; stdout stub-like %d' % (
            sum(r['stubs'].values()), r['ap'], sorted(r['stubs'].items(), key=lambda x: -x[1])[:6], r['so_stub']))
        print('  ASSERT: log %d stdout %d; user_msg_param %d; FixB9a: on %d; death-like %s' % (
            r['asrt'], r['so_asrt'], r['umsg'], r['fix'], r['death']))
        print('  FrameTrace rows %d; frames >= 1 s (whole log) %d; >= 100 ms (whole log, incl. entry) %d; max dt %d us' % (
            r['rows'], r['k2'], r['k3'], r['maxdt']))
        if last:
            keys = ['total', 'handles', 'SourceCreate', 'SourceDestroy', 'SourceRender', 'SourceSetAttributes',
                    'SourceGetRays', 'SourceCalculateAudioPaths', 'PortalCreate']
            print('  last AudioPropagation: calls ' + ' '.join('%s=%s' % (k, last.get(k)) for k in keys))
            if r['first_after']:
                kv0, rows0 = r['first_after']
                dr = r['rows'] - rows0
                dc = last.get('SourceCreate', 0) - kv0.get('SourceCreate', 0)
                print('  rough rate after Level has started: dSourceCreate %d / rows %d = %.4f' % (dc, dr, dc / dr if dr else -1))
        else:
            print('  AudioPropagation: calls lines 0')
        # criterion checks
        if fix:
            c = (sum(r['stubs'].values()) == 0 and r['asrt'] == 0 and r['so_asrt'] == 0 and r['umsg'] == 0 and r['fix'] == 1
                 and not r['death'] and r['k2'] == 0)
        else:
            c = r['ap'] >= 1000 and r['fix'] == 0 and r['last'] is None and not r['death']
        print('  lead check %s' % ('ok' if c else 'FAIL'))
        ok &= c
    print('F6F RECOUNT ' + ('ALL OK' if ok else 'FAIL'))
    sys.exit(0 if ok else 1)


main()
