# F5a2 (HPP-366, ROADMAP s122 item 280(g)): model test of the ScreenshotGrabber video ring (KYTY_REC) driven by the
# Presenter::Present attempt loop, without a Vulkan device.  The ring is a line-by-line transcription of
# screenshot.cpp RecordVideoFrame :324-368, FinishVideoFrame :374-382, FlushPendingVideoSlots :386-399, FlushVideoSlot
# :401-403 (pending=false, Wait(tick)) and ~ScreenshotGrabber :213; the loop - swapchain.cpp Present :947-1027 after F5a2.
# Variants: "old" - KYTY_FIX_MINIMIZE=0 (Record each attempt, Finish on success only; no zero-extent path);
# "f5a" - d2811535 at =1 (zero-extent drop path, Record/Finish as old); "f5a2" - this fix at =1.
# Check (item 280(g)): video order strictly by present (strictly increasing, no repeats), every recorded present in
# the video exactly once, per call Record <= 1 and Finish == Record.  Expected: f5a2 passes every scenario; f5a fails
# the zero-extent episode (positive control of F5b RC1); old fails retry-exhausted and recovery-with-retry scenarios
# (register row F12, =0 path open - information only).  Last line "ALL OK" when the expectations hold.
import sys

RING = 3


class Sim:
    def __init__(self, variant, lag, ood_on):
        self.v = variant
        self.fix = variant in ("f5a", "f5a2")
        self.new = variant == "f5a2"
        self.lag = lag          # GPU completes submits up to tick - lag after each submit
        self.ood_on = ood_on    # where a stale swapchain reports OUT_OF_DATE: "present" (w144_09) or "acquire"
        # scheduler
        self.tick = 0
        self.done = 0
        # ring
        self.slots = [dict(pending=False, tick=0, present=0) for _ in range(RING)]
        self.rec_next = 0
        self.flush_next = 0
        self.presents = 0
        self.video = []
        # swapchain / window
        self.missing = False
        self.stale = False
        self.minimized = False
        self.extra_ood = 0
        self.recorded_presents = []
        self.call_violations = []
        self.dropped = 0
        self.exhausted = 0

    # --- scheduler
    def submit(self):
        self.tick += 1
        self.done = max(self.done, self.tick - self.lag)
        return self.tick

    def is_free(self, t):
        return t <= self.done

    def wait(self, t):
        self.done = max(self.done, t)

    # --- ring (screenshot.cpp)
    def poll(self):
        self.presents += 1
        return True  # m_rec_frame = KYTY_REC set

    def record(self):
        slot = self.slots[self.rec_next % RING]
        if slot["pending"]:
            self.flush_pending(True)
        slot["present"] = self.presents
        slot["pending"] = True
        self.recorded_presents.append(self.presents)

    def finish(self, tick):
        slot = self.slots[self.rec_next % RING]
        if not slot["pending"]:
            return
        slot["tick"] = tick
        self.rec_next += 1
        self.flush_pending(False)

    def flush_pending(self, wait_oldest):
        while True:
            oldest = self.slots[self.flush_next % RING]
            if not oldest["pending"]:
                return
            if not wait_oldest and not self.is_free(oldest["tick"]):
                return
            wait_oldest = False
            oldest["pending"] = False
            self.wait(oldest["tick"])
            self.video.append(oldest["present"])
            self.flush_next += 1

    def destroy_grabber(self):
        self.flush_pending(True)

    # --- swapchain
    def acquire_ok(self):
        return not (self.stale and self.ood_on == "acquire")

    def present_ok(self):
        if self.extra_ood > 0:
            self.extra_ood -= 1
            return False
        return not self.stale

    def recover(self):
        self.done = self.tick  # Destroy waits for the queue to idle
        if self.fix and self.minimized:
            self.missing = True
        else:
            self.missing = False
            self.stale = False

    # --- Presenter::Present
    def present_call(self):
        screenshot = self.poll()
        recorded = finished = False
        n_rec = n_fin = 0
        for attempt in range(2):
            if self.fix and self.missing:
                if self.minimized:  # TryEndZeroExtent false: drop
                    self.dropped += 1
                    return n_rec, n_fin
                self.missing = False
                self.stale = False
            if not self.acquire_ok():
                self.recover()
                continue
            if screenshot and not (self.new and recorded):
                self.record()
                recorded = True
                n_rec += 1
            t = self.submit()
            if not self.present_ok():
                if self.new and recorded and not finished:
                    self.finish(t)
                    finished = True
                    n_fin += 1
                self.recover()
                continue
            if screenshot and not (self.new and finished):
                self.finish(t)
                n_fin += 1
            return n_rec, n_fin
        self.exhausted += 1
        return n_rec, n_fin

    def run(self, calls, events):
        for i in range(1, calls + 1):
            for e in events.get(i, ()):
                if e == "minimize":
                    self.minimized = True
                    self.stale = True
                elif e == "restore":
                    self.minimized = False
                elif e == "resize":
                    self.stale = True
                elif e == "exhaust":
                    self.extra_ood = 2
                elif e == "ood_once":
                    self.extra_ood = 1
            n_rec, n_fin = self.present_call()
            if not (n_rec <= 1 and n_fin == n_rec):
                self.call_violations.append((self.presents, n_rec, n_fin))
        self.destroy_grabber()
        return self

    def verdict(self):
        # ~ScreenshotGrabber flushes with wait only the oldest slot (screenshot.cpp:213, :392-395): the slots still
        # running on the GPU at that moment stay unwritten - the tail of the recording, in the real code too.  So
        # "once": no repeats, and every recorded present is either in the video or a pending tail slot newer than the
        # last written frame; a recorded present missing from both was overwritten (lost) - a failure.
        v = self.video
        inc = all(b > a for a, b in zip(v, v[1:]))
        tail = sorted(s["present"] for s in self.slots if s["pending"])
        last = v[-1] if v else 0
        rec = sorted(set(self.recorded_presents))
        once = (len(v) == len(set(v)) and all(p > last for p in tail) and
                sorted(v + tail) == rec and len(tail) <= RING)
        ok = inc and once and not self.call_violations
        return ok, inc, once


SCEN = {
    "normal": (40, {}),
    "minimize_episode": (40, {11: ["minimize"], 21: ["restore"]}),
    "two_episodes": (60, {11: ["minimize"], 15: ["restore"], 31: ["minimize"], 40: ["restore"]}),
    "restore_next_call": (30, {11: ["minimize"], 12: ["restore"]}),
    "resize_recovery": (40, {11: ["resize"]}),
    "retry_exhausted": (40, {11: ["exhaust"]}),
    "ood_once_then_ok": (40, {11: ["ood_once"]}),
}
# Zero-extent scenarios do not exist on the =0 path (Recreate builds a 0x0 swapchain - B37 itself, not modelled).
ZERO = {"minimize_episode", "two_episodes", "restore_next_call"}

ok_all = True
rows = []
for variant in ("f5a2", "f5a", "old"):
    for name, (calls, events) in SCEN.items():
        if variant == "old" and name in ZERO:
            continue
        for ood_on in ("present", "acquire"):
            for lag in (0, 1, 2, 3):
                s = Sim(variant, lag, ood_on).run(calls, events)
                ok, inc, once = s.verdict()
                rows.append((variant, name, ood_on, lag, ok, inc, once, s))
                tail = s.video[8:22]
                print("%-5s %-18s ood_on=%-7s lag=%d %s inc=%d once=%d viol=%d drop=%d exh=%d video[8:22]=%s" % (
                    variant, name, ood_on, lag, "PASS" if ok else "FAIL", inc, once, len(s.call_violations),
                    s.dropped, s.exhausted, tail))

# Expectations.
f5a2_fail = [r for r in rows if r[0] == "f5a2" and not r[4]]
f5a_ep_fail = [r for r in rows if r[0] == "f5a" and r[1] == "minimize_episode" and r[2] == "present" and not r[4]]
old_f12 = [r for r in rows if r[0] == "old" and r[1] in ("retry_exhausted", "resize_recovery") and not r[4]]
old_normal_ok = all(r[4] for r in rows if r[0] == "old" and r[1] == "normal")
f5a_normal_ok = all(r[4] for r in rows if r[0] == "f5a" and r[1] == "normal")
print()
print("f5a2 failing cases: %d (expected 0)" % len(f5a2_fail))
print("f5a minimize_episode (ood on present) failing lags: %d of 4 (expected > 0: positive control of F5b RC1)" % len(f5a_ep_fail))
print("old retry_exhausted/resize_recovery failing cases: %d (information: register row F12, =0 open)" % len(old_f12))
print("old normal all pass: %s; f5a normal all pass: %s" % (old_normal_ok, f5a_normal_ok))
ok_all = not f5a2_fail and len(f5a_ep_fail) > 0 and old_normal_ok and f5a_normal_ok
# F5b RC1 trace: after the episode every third frame is late - show the f5a order at lag 0.
s = Sim("f5a", 0, "present").run(40, {11: ["minimize"], 21: ["restore"]})
print("f5a lag=0 video:", s.video)
s = Sim("f5a2", 0, "present").run(40, {11: ["minimize"], 21: ["restore"]})
print("f5a2 lag=0 video:", s.video)
if ok_all:
    print("ALL OK")
    sys.exit(0)
print("EXPECTATION FAILED")
sys.exit(1)
