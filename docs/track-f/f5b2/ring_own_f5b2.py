# F5b2 (HPP-367, Red Team): own model of ScreenshotGrabber video ring + Presenter::Present attempt loop.
# Independent of f5a2/ring_model_f5a2.py. Transcription of 01ca15d1:screenshot.cpp:324-403 (RecordVideoFrame,
# FinishVideoFrame, FlushPendingVideoSlots, FlushVideoSlot), screenshot.h:76 (3 slots), swapchain.cpp:944-1031 (Present),
# :373-411 (RecoverSwapchain, BeginZeroExtent, TryEndZeroExtent).  Variants: V0 (=0 path, any commit), V1 (d2811535 =1),
# V2 (01ca15d1 =1), V3 (01ca15d1 =0) and mutants of V2.  GPU: done = last_submit - lag after every submit; IsFree(t) = t<=done;
# Wait(t) -> done = max(done, t).  A slot read whose copy submit tick > done after the Wait is a content race (stale bytes).
import itertools, sys

NSLOT = 3


class Ring:
    def __init__(self, gpu):
        self.gpu = gpu
        self.slots = [dict(pending=False, tick=0, present=None, copy_tick=None) for _ in range(NSLOT)]
        self.next = 0
        self.flush_next = 0
        self.presents = 0
        self.video = []  # (present, race)

    def poll(self):
        self.presents += 1
        return True

    def record(self, copy_tick_future):
        s = self.slots[self.next % NSLOT]
        if s['pending']:
            self.flush(True)
        s['present'] = self.presents
        s['copy_tick'] = copy_tick_future
        s['pending'] = True

    def finish(self, tick):
        s = self.slots[self.next % NSLOT]
        if not s['pending']:
            return
        s['tick'] = tick
        self.next += 1
        self.flush(False)

    def flush(self, wait_oldest):
        while True:
            o = self.slots[self.flush_next % NSLOT]
            if not o['pending']:
                return
            if not wait_oldest and not self.gpu.free(o['tick']):
                return
            wait_oldest = False
            o['pending'] = False
            self.gpu.wait(o['tick'])
            race = o['copy_tick'] is None or o['copy_tick'] > self.gpu.done
            self.video.append((o['present'], race))
            self.flush_next += 1


class Gpu:
    def __init__(self, lag):
        self.lag, self.last, self.done = lag, 0, 0

    def submit(self):
        self.last += 1
        self.done = max(self.done, self.last - self.lag)
        return self.last

    def free(self, t):
        return t <= self.done

    def wait(self, t):
        self.done = max(self.done, t)


class World:
    """window: extent_zero flag per call; script: per call a list of attempt outcomes (acq, pres)."""

    def __init__(self, variant, lag):
        self.v = variant
        self.gpu = Gpu(lag)
        self.ring = Ring(self.gpu)
        self.missing = False
        self.extent_zero = False
        self.calls = []  # (present_no, R, F)
        self.fix = variant in ('V1', 'V2', 'Ma', 'Mb', 'Mc')

    def recover(self):
        # Recreate: under fix at zero extent no swapchain (Missing); else a swapchain exists
        self.missing = self.fix and self.extent_zero

    def present(self, outcomes):
        ring, v = self.ring, self.v
        shot = ring.poll()
        pno = ring.presents
        R = F = 0
        new = v in ('V2', 'V3', 'Ma', 'Mb', 'Mc')
        fixm = self.fix and new  # the F5a2 fix_minimize local (V3: 01ca15d1 at =0 -> False)
        recorded = finished = False
        it = iter(outcomes)
        for attempt in range(2):
            if self.fix and self.missing:
                if self.extent_zero:
                    self.calls.append((pno, R, F, 'drop'))
                    return
                self.missing = False  # TryEndZeroExtent -> Create
            acq, pres = next(it, ('ok', 'ok'))
            if acq != 'ok':
                self.recover()
                continue
            supp_rec = fixm and recorded and v != 'Mb'
            tick_future = self.gpu.last + 1
            if shot and not supp_rec:
                ring.record(tick_future)
                R += 1
                recorded = True
            tick = self.gpu.submit()
            assert tick == tick_future
            if pres != 'ok':
                if fixm and recorded and not finished and v != 'Ma':
                    ring.finish(tick)
                    F += 1
                    finished = True
                self.recover()
                continue
            if shot and not (fixm and finished and v != 'Mc'):
                ring.finish(tick)
                F += 1
            self.calls.append((pno, R, F, 'ok'))
            return
        self.calls.append((pno, R, F, 'exhausted'))

    def end(self):
        self.ring.flush(True)  # ~ScreenshotGrabber


def scenarios():
    S = {}
    S['normal'] = [('n', None)] * 20
    # minimize episode, OUT_OF_DATE on present: call 8 present fails, window zero for calls 8..14, restore at 15
    S['episode_present'] = [('n', None)] * 7 + [('z', [('ok', 'fail')])] + [('z', None)] * 6 + [('n', None)] * 10
    S['episode_acquire'] = [('n', None)] * 7 + [('z', [('fail', 'ok')])] + [('z', None)] * 6 + [('n', None)] * 10
    S['two_episodes'] = ([('n', None)] * 5 + [('z', [('ok', 'fail')])] + [('z', None)] * 3) * 2 + [('n', None)] * 8
    S['resize_recovery'] = [('n', None)] * 6 + [('n', [('ok', 'fail'), ('ok', 'ok')])] + [('n', None)] * 10
    S['retry_exhausted'] = [('n', None)] * 6 + [('n', [('ok', 'fail'), ('ok', 'fail')])] + [('n', None)] * 10
    S['exh_acq_then_pres'] = [('n', None)] * 6 + [('n', [('fail', 'ok'), ('ok', 'fail')])] + [('n', None)] * 10
    S['exh_pres_then_acq'] = [('n', None)] * 6 + [('n', [('ok', 'fail'), ('fail', 'ok')])] + [('n', None)] * 10
    S['episode_restore_same_call'] = [('n', None)] * 7 + [('z1', [('ok', 'fail'), ('ok', 'ok')])] + [('n', None)] * 10
    S['back_to_back_fail'] = [('n', None)] * 4 + [('n', [('ok', 'fail'), ('ok', 'ok')])] * 3 + [('n', None)] * 8
    return S


def run(variant, lag, scen):
    w = World(variant, lag)
    for win, outs in scen:
        if win == 'z':
            w.extent_zero = True
        elif win == 'n':
            w.extent_zero = False
        elif win == 'z1':  # zero only for the recreate of attempt 0 of this call, then non-zero (immediate restore)
            w.extent_zero = True
        o = list(outs) if outs else [('ok', 'ok')]
        if win == 'z1':
            # attempt 0 -> recover at zero extent; attempt 1 sees a non-zero extent again
            orig_recover = w.recover

            def rec_once(orig=orig_recover):
                orig()
                w.extent_zero = False
                w.recover = orig
            w.recover = rec_once
        w.present(o)
    w.end()
    return w


def check(w):
    errs = []
    pres = [p for p, _ in w.ring.video]
    for a, b in zip(pres, pres[1:]):
        if b <= a:
            errs.append('order %d->%d' % (a, b))
    if len(set(pres)) != len(pres):
        errs.append('dup')
    if any(r for _, r in w.ring.video):
        errs.append('race %s' % [p for p, r in w.ring.video if r])
    # the destructor waits only for the oldest pending slot (screenshot.cpp:213 FlushPendingVideoSlots(true)); slots
    # recorded after the last written one may stay unwritten at exit - the code does so too (tail, not a defect)
    last = max(pres) if pres else 0
    recorded_calls = [c[0] for c in w.calls if c[1] > 0 and c[0] <= last]
    for p in recorded_calls:
        if pres.count(p) != 1:
            errs.append('call %d in video %d times' % (p, pres.count(p)))
    for p, R, F, how in w.calls:
        if R > 1 or F != R:
            errs.append('call %d R=%d F=%d %s' % (p, R, F, how))
    return errs


def main():
    S = scenarios()
    out = []
    summary = {}
    for variant in ('V0', 'V3', 'V1', 'V2', 'Ma', 'Mb', 'Mc'):
        nfail = 0
        for name, scen in S.items():
            for lag in range(4):
                if variant in ('V0', 'V3') and name.startswith(('episode', 'two_episodes')):
                    continue  # =0 at zero extent: real recreate at extent 0 -> validation stop (B37); ring not modelled
                w = run(variant, lag, scen)
                e = check(w)
                if e:
                    nfail += 1
                out.append('%s %-26s lag=%d %s video=%s' % (variant, name, lag, 'FAIL ' + ';'.join(e[:4]) if e else 'PASS',
                                                         ','.join(str(p) + ('!' if r else '') for p, r in w.ring.video)))
        summary[variant] = nfail
    # V0 == V3 trace identity (=0 byte for byte at the model level)
    same = all(run('V0', lag, sc).ring.video == run('V3', lag, sc).ring.video and run('V0', lag, sc).calls == run('V3', lag, sc).calls
               for sc in S.values() for lag in range(4))
    print('\n'.join(out))
    print('SUMMARY fails per variant:', summary)
    print('V0==V3 traces:', same)
    ok = summary['V2'] == 0 and summary['V1'] > 0 and summary['Ma'] > 0 and summary['Mb'] > 0 and summary['Mc'] > 0 and same
    print('mutants of V2: Ma (no Finish after a failed present) = %d, Mb (Record repeated on attempt 1) = %d, '
          'Mc (success Finish not suppressed) = %d failing cases; each > 0 required' % (summary['Ma'], summary['Mb'], summary['Mc']))
    print('ALL OK' if ok else 'NOT OK')
    sys.exit(0 if ok else 1)


main()
