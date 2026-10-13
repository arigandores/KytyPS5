# M5a HLE1: one streaming pass over M3 logs, counting the journal lines our HLE code prints on the paths of
# themes T125 (AudioOut2), T055/T298/T059 (AvPlayer), T023 (agc command buffer), T031 (guest printf).
# Read-only, binary mode, 64 MiB chunks cut at the last newline. Usage: python scan_m5a.py <log> [<log> ...]
import os, re, sys, collections, hashlib
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('SEALED_RUN.lock present - exit'); sys.exit(3)

LINE = re.compile(
    rb'^(?:\t (?:port_type     = |audio_handle  = |port          = |port = 0x|data_format   = |queue_depth = |event_id = |filename|uri_type|'
    rb'auto_start|debug_level|num_output_video|demux_video|event_replacement\.event_callback|avformat|avcodec|'
    rb'av_read|unsupported codec|decoder not found|command buffer)'
    rb'|AudioStat:|AudioOut:|AvTrace|AvPlayer video|GuestOut: |GuestFmt: |PS5 NID fallback|Level has started|'
    rb'\[\d+\]\[[^\]\n]*\] (?:AudioOut2|AvPlayer|LibcInternal|libc)::)[^\n]*$', re.M)
SIGS = (b'There are too many objects/batches', b'command_buffer_writer.ppr.cpp', b'pc=0x00000009004a020e',
        b'suspiciously large', b'exhausted and has no grow', b'grow callback failed', b'did not provide enough',
        b'AllocateDW failed', b'%.*')

def scan(path):
    c = collections.Counter()
    port_type = collections.Counter()
    pair = collections.Counter()          # (port_type, audio_handle>0)
    port_handles = []
    last_pt = None
    events = []
    keep = collections.defaultdict(list)  # kind -> lines (capped)
    guest = collections.Counter()
    sig = collections.Counter()
    astat = {}
    size = os.path.getsize(path)
    f = open(path, 'rb')
    base = 0
    tail = b''
    CH = 64 << 20
    while True:
        blk = f.read(CH)
        if not blk:
            buf = tail; tail = b''
            if not buf: break
        else:
            buf = tail + blk
            k = buf.rfind(b'\n')
            if k < 0:
                tail = buf; continue
            tail = buf[k + 1:]; buf = buf[:k + 1]
        for s in SIGS:
            n = buf.count(s)
            if n: sig[s.decode()] += n
        for m in LINE.finditer(buf):
            ln = m.group(0)
            off = base + m.start()
            if ln.startswith(b'\t port_type'):
                v = int(ln.split(b'=')[1]); port_type[v] += 1; last_pt = v; c['port_type'] += 1
            elif ln.startswith(b'\t audio_handle'):
                v = int(ln.split(b'=')[1]); pair[(last_pt, v > 0)] += 1; last_pt = None; c['audio_handle'] += 1
            elif ln.startswith(b'\t port          = '):
                port_handles.append(int(ln.split(b'=')[1], 16)); c['port_create'] += 1
            elif ln.startswith(b'\t port = 0x'):
                c['port_destroy'] += 1
            elif ln.startswith(b'\t event_id'):
                events.append((off, int(ln.split(b'=')[1]))); c['event_id'] += 1
            elif ln.startswith(b'GuestOut: '):
                c['GuestOut'] += 1; guest[ln[10:].strip()[:200]] += 1
            elif ln.startswith(b'AudioStat:'):
                c['AudioStat'] += 1
                d = dict(x.split(b'=', 1) for x in ln[10:].split() if b'=' in x)
                p = int(d.get(b'port', b'-1')); astat[p] = (int(d.get(b'pushes', b'0')), int(d.get(b'q_fail', b'0')), int(d.get(b'dev', b'0')))
            else:
                key = ln[:28].decode('utf-8', 'replace')
                if ln.startswith(b'['):
                    key = 'PRINT_NAME ' + ln.split(b'] ', 1)[1][:40].decode('utf-8', 'replace')
                elif ln.startswith(b'\t'):
                    key = ln.strip()[:24].decode('utf-8', 'replace')
                elif b':' in ln[:20]:
                    key = ln.split(b':')[0].decode('utf-8', 'replace')
                c[key] += 1
                if len(keep[key]) < 12:
                    keep[key].append('@%d %s' % (off, ln[:240].decode('utf-8', 'replace')))
        base += len(buf)
    return dict(size=size, c=c, port_type=port_type, pair=pair, port_handles=port_handles, events=events,
                keep=keep, guest=guest, sig=sig, astat=astat)

EV = {1: 'STOP', 2: 'READY', 3: 'PLAY', 4: 'PAUSE', 0x20: 'WARNING'}
for p in sys.argv[1:]:
    r = scan(p)
    print('=' * 100)
    print('LOG %s size=%d' % (p, r['size']))
    print('counts:', dict(sorted(r['c'].items())))
    print('sig counts:', dict(r['sig']))
    print('AudioOut2PortCreate port_type:', dict(r['port_type']), ' (port_type, audio_handle>0):', dict(r['pair']))
    ph = r['port_handles']
    if ph:
        print('port handles logged: n=%d min=%d max=%d first=%s last=%s' % (len(ph), min(ph), max(ph), ph[:20], ph[-5:]))
    print('AudioStat last per port (pushes, q_fail, dev):', r['astat'])
    print('AvPlayer events (%d):' % len(r['events']), ','.join(EV.get(v, str(v)) for _, v in r['events']))
    if r['events']:
        print('  event offsets:', [o for o, _ in r['events']])
    for k, v in sorted(r['keep'].items()):
        print('-- %s (%d)' % (k, r['c'][k]))
        for x in v: print('   ', x)
    print('GuestOut unique=%d total=%d; top 25:' % (len(r['guest']), sum(r['guest'].values())))
    for t, n in r['guest'].most_common(25):
        print('   %6d  %s' % (n, t.decode('utf-8', 'replace')))
    gl = [t for t in r['guest'] if b'%' in t]
    print('GuestOut lines containing %% (unformatted remnants): %d %s' % (len(gl), [x[:80] for x in gl[:10]]))
    sys.stdout.flush()
print('DONE')
