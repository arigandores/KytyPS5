#!/usr/bin/env python3
# S17a5 (HPP-638, ROADMAP s122 item 561(g)(2)): the stand KYTY_S_REPLAY_TEST=stop keeps the rebuild thread inside the
# rebuild until m_precache_stop (the real close path: preparation loop -> PipelineCache::ReplayCloseStop), at most 60 s.
# Anchors are whole lines; CRLF of the working tree is kept; the script writes bytes.
import sys

PATH = sys.argv[1] if len(sys.argv) > 1 else "C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp"

raw = open(PATH, "rb").read()
crlf = b"\r\n" in raw
text = raw.decode("utf-8").replace("\r\n", "\n")
lines = text.split("\n")


def replace_block(old, new, what):
    global lines
    n = len(old)
    hits = [i for i in range(len(lines) - n + 1) if lines[i:i + n] == old]
    if len(hits) != 1:
        sys.exit("anchor %s: %d hits" % (what, len(hits)))
    i = hits[0]
    lines = lines[:i] + new + lines[i + n:]


# 1. <thread> for std::this_thread::sleep_for (the wait of the stand).
replace_block(
    ["#include <string_view>"],
    ["#include <string_view>", "#include <thread>"],
    "include")

# 2. The stand: after the close event the rebuild thread waits for m_precache_stop.
OLD = [
    "\t\tif (SR::TestStand() == SR::Stand::Stop && !stop_stand_done && processed >= records / 2u) {",
    "\t\t\tstop_stand_done = true;",
    "\t\t\tLOGF(\"ShaderReplay: stand stop applied processed=%u records=%u\\n\", processed, records);",
    "\t\t\tSR::StandRequestClose();",
    "\t\t}",
]
NEW = [
    "\t\tif (SR::TestStand() == SR::Stand::Stop && !stop_stand_done && processed >= records / 2u) {",
    "\t\t\tstop_stand_done = true;",
    "\t\t\tLOGF(\"ShaderReplay: stand stop applied processed=%u records=%u\\n\", processed, records);",
    "\t\t\tSR::StandRequestClose();",
    "\t\t\t// S17a5 (HPP-638, ROADMAP s122 item 561(g)(2)): the preparation loop (window.cpp, WindowPrepareShaders) does not",
    "\t\t\t// wait for this thread - it starts on the main thread after the graphics init and LoadElf, and the rebuild of",
    "\t\t\t// S17c (420 records) ended before it (K6 of S17c not measured). So the stand keeps this thread here, inside the",
    "\t\t\t// rebuild, until the loop reads the close event and PipelineCache::ReplayCloseStop stores m_precache_stop (the",
    "\t\t\t// real close path; ~PipelineCache stores it too); then the loop below is left with processed < records and the",
    "\t\t\t// stopped branch runs. At most StandStopWaitMs: the line \"stand stop timeout\" and the rebuild goes on as before.",
    "\t\t\tconstexpr uint64_t StandStopWaitMs = 60000;",
    "\t\t\tconst auto         wait_begin      = HostMicros();",
    "\t\t\twhile (!m_precache_stop.load() && HostMicros() - wait_begin < StandStopWaitMs * 1000u) {",
    "\t\t\t\tstd::this_thread::sleep_for(std::chrono::milliseconds(5));",
    "\t\t\t}",
    "\t\t\tconst auto waited_ms = (HostMicros() - wait_begin) / 1000u;",
    "\t\t\tif (m_precache_stop.load()) {",
    "\t\t\t\tLOGF(\"ShaderReplay: stand stop seen waited_ms=%\" PRIu64 \" processed=%u records=%u\\n\", waited_ms, processed,",
    "\t\t\t\t     records);",
    "\t\t\t\tbreak;",
    "\t\t\t}",
    "\t\t\tLOGF(\"ShaderReplay: stand stop timeout waited_ms=%\" PRIu64 \" processed=%u records=%u\\n\", waited_ms, processed,",
    "\t\t\t     records);",
    "\t\t}",
]
replace_block(OLD, NEW, "stand")

out = "\n".join(lines)
if crlf:
    out = out.replace("\n", "\r\n")
open(PATH, "wb").write(out.encode("utf-8"))
print("patched", PATH, "crlf" if crlf else "lf")
