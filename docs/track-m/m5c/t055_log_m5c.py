"""M5c (HPP-847), T055 6b79b7a00, ROADMAP p.767(zh): does the game call AvPlayerJumpToTime on the observed path.
Code facts used (main f7a5e258, src/libs/avPlayer.cpp): AvPlayerJumpToTime -> Source::Jump -> StartImpl(ms, was_paused, true);
StartImpl ends with StartWorkers(), which creates guest pthreads 'AvPlayerVideoDecoder' (if video), 'AvPlayerAudioDecoder'
(if audio), 'AvPlayerDemuxer' through LibKernel::PthreadCreate, which always logs '\tthread create: <name>, id = ..'
(src/kernel/pthread.cpp). A successful Jump (rc 0) is the only path that emits event WARNING (0x20 = 32) with
JUMP_COMPLETE; the other WARNING source is pump_warnings (LOOPING_BACK, needs SetLooping(1) and demux EOF).
So: successful Jump calls  <=  creates(AvPlayerDemuxer) - starts(Start, PLAY event 3 right after READY or after STOP).
This script (read-only, binary, streamed) prints per log: the ordered sequence of AvPlayer events and AvPlayer thread
creations with line numbers, and the counts.
Usage: python t055_log_m5c.py <log> [<log> ...] > t055_log_m5c.out.txt"""
import os, sys, re, collections
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('LOCK present - exit 3'); sys.exit(3)
EV = re.compile(rb'^\t event_id = (-?\d+)')
TC = re.compile(rb'^\tthread create: (AvPlayer\w*), id = (-?\d+), (-?\d+)')
TB = re.compile(rb'^\tPthread run begin: (AvPlayer\w*), id = (\d+)')
FN = re.compile(rb'^\t ?filename\s*=\s*(.*)$')
NAMES = {1: 'STOP', 2: 'READY', 3: 'PLAY', 4: 'PAUSE', 32: 'WARNING'}
tot = collections.Counter()
for path in sys.argv[1:]:
    print('=' * 100)
    print('LOG', path, 'size', os.path.getsize(path))
    seq = []
    c = collections.Counter()
    n = 0
    with open(path, 'rb') as f:
        for line in f:
            n += 1
            if not line.startswith(b'\t'):
                continue
            m = EV.match(line)
            if m:
                v = int(m.group(1)); c['event_%s' % NAMES.get(v, v)] += 1; seq.append((n, 'event', NAMES.get(v, str(v))))
                continue
            m = TC.match(line)
            if m:
                nm = m.group(1).decode(); c['create_' + nm] += 1; seq.append((n, 'create', nm + ' rc=' + m.group(3).decode()))
                continue
            m = TB.match(line)
            if m:
                nm = m.group(1).decode(); c['run_' + nm] += 1; seq.append((n, 'run', nm + ' id=' + m.group(2).decode()))
                continue
            m = FN.match(line)
            if m and b'video' in m.group(1):
                c['filename'] += 1; seq.append((n, 'filename', m.group(1).decode('latin1')[:80]))
    print('lines', n)
    for ln, k, v in seq:
        print('   %9d %-8s %s' % (ln, k, v))
    for k in sorted(c):
        print('  count %-32s %d' % (k, c[k]))
    tot.update(c)
    starts = c['event_PLAY'] and 1  # PLAY after READY = the Start; later PLAY events follow Resume
    print('  successful_jump_upper_bound = create_AvPlayerDemuxer(%d) - starts_from_Start(%d) = %d' % (
        c['create_AvPlayerDemuxer'], min(c['event_READY'], c['create_AvPlayerDemuxer']),
        c['create_AvPlayerDemuxer'] - min(c['event_READY'], c['create_AvPlayerDemuxer'])))
print('=' * 100)
for k in sorted(tot):
    print('TOTAL %-32s %d' % (k, tot[k]))
print('DONE')
