# Sealed addendum 07 to pred/01 — session 102, M5: the capture run crashed at start; the ONE technical retry, written before it

**Immutable once written.** `pred/01_m5_bench.md` and `pred/02_m5_addendum.md` are NOT edited.

`m5cap102` (binary `346ba4f6…`, the pred/01 §4 command with `--emu-arg=--rd`) died at start-up, before
the level loaded and before any capture was requested: `--- Fatal Error --- Error: condition
(m_producer != self || m_open_slot != nullptr) is true in commandRecorder.cpp:326` right after
`Window 1 exposed`, exit code 321, no `.rdc` written. The log shows `DmaLayout: mode 1` and 64
injections, `RecordThread: started … record thread on from tick 1`. That assertion is the
single-producer check of the command recorder (a second thread began a record on a ring another
thread owns); nothing in the pred/01 protocol measures anything at that point. **This is a technical
failure (a crash), for which pred/01 §4 allows exactly one further capture attempt.**

**The retry, `m5cap102b`, is the pred/01 §4 command with one addition: `KYTY_RECORD_THREAD=0`.**
Reason: the crash is in the record thread's producer bookkeeping, which the capture does not need —
`RecordThreadWanted()` (`commandRecorder.cpp:1081`) already refuses the record thread for as long as
`RenderDocCapturing()` is true, so the captured frames are recorded directly on the GuestGpu thread
in either case, and the Vulkan command content of the captured frame is the same. It changes the
CPU path of the frames BEFORE the capture only, which M5 does not measure. The cause of the race is
NOT diagnosed here and is recorded as a debt (it did not occur in any of the three runs without
`--rd` this session).

If `m5cap102b` also fails technically, M5 is **not decided this session** and the bench tooling, the
modules and the seals carry over unchanged to session 103.
