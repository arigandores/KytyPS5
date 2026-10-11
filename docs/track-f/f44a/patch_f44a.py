# F44a (HPP-791, ROADMAP s122 item 698(v)(1)-(3), (5), (g)): KYTY_FIX_F29 - ParseFaultArea in faultManager.cpp/.h,
# the deferred operation of FaultManager::ProcessFaultBuffer through it; the stand target f29_fault_stand in CMakeLists.txt.
# Anchors are whole lines; CRLF is stripped before the search and restored after; files are written with write_bytes.
# Usage: python patch_f44a.py <repo root>
import sys

ROOT = sys.argv[1].rstrip('/')
NL = chr(10)


def load(rel):
    b = open(ROOT + '/' + rel, 'rb').read()
    crlf = b'\r\n' in b
    t = b.decode('utf-8').replace(chr(13), '')
    return t, crlf


def save(rel, t, crlf):
    if crlf:
        t = t.replace(NL, chr(13) + NL)
    open(ROOT + '/' + rel, 'wb').write(t.encode('utf-8'))


def replace_lines(t, old_lines, new_lines, name):
    old = NL.join(old_lines) + NL
    n = t.count(old)
    if n != 1:
        raise SystemExit('anchor ' + name + ' count ' + str(n))
    # whole lines: the match must start at a line start
    i = t.find(old)
    if i != 0 and t[i - 1] != NL:
        raise SystemExit('anchor ' + name + ' not at a line start')
    return t.replace(old, NL.join(new_lines) + NL)


# ---------------- faultManager.h ----------------
H = 'src/graphics/host_gpu/renderer/cache/faultManager.h'
t, crlf = load(H)
t = replace_lines(t, [
    '#include <array>',
    '#include <cstdint>',
], [
    '#include <array>',
    '#include <cstdint>',
    '#include <functional>',
], 'h_inc')
t = replace_lines(t, [
    'class BufferCache;',
    '',
], [
    'class BufferCache;',
    '',
    '// Track F, F29 (KYTY_FIX_F29, ROADMAP s122 item 698): one area of the fault download buffer is a counter word',
    '// (faults[0], low 32 bits) and the records faults[1..1023] written by fault_buffer_process.comp. With 1 024 or more',
    '// set bits in one pass the counter is 1 023 + T > 1 023 while only 1 023 records exist; reading faults[1..counter]',
    '// then goes past the area (and past the whole buffer for the last area). ParseFaultArea is the one parse of an area:',
    '// FaultManager::ProcessFaultBuffer and the stand tests/F29FaultStand.cpp call this function, not a copy.',
    '//   raw   - the counter word as read;',
    '//   count - the records visited: clamp ? min(raw, 1 023) : raw (clamp = false is the path before the fix).',
    '// visit(index, value) is called for index = 1 ... count in order. With clamp and raw > 1 023 the function writes the',
    '// line "FixF29: overflow pass= area= count= read= total=" (not more than 32 lines per process; total - the passes',
    '// with an overflow since the start of the process, counted only with clamp). pass carries the fields of that line.',
    'struct FaultAreaParse {',
    '\tuint32_t raw   = 0;',
    '\tuint32_t count = 0;',
    '};',
    'struct FaultAreaPass {',
    '\tuint64_t pass = 0;',
    '\tuint32_t area = 0;',
    '};',
    'using FaultAreaVisitor = std::function<void(uint32_t index, uint64_t value)>;',
    '',
    '// KYTY_FIX_F29 (default 0): the value is read once per process (EnvValueOn: unset/""/0/false/off/no - off).',
    '[[nodiscard]] bool           FixF29Enabled();',
    'FaultAreaParse ParseFaultArea(const uint64_t* area, bool clamp, const FaultAreaVisitor& visit,',
    '                              const FaultAreaPass& pass = {});',
    '',
], 'h_decl')
t = replace_lines(t, [
    '\tuint32_t                                   m_current_area = 0;',
], [
    '\tuint32_t                                   m_current_area = 0;',
    '\tuint64_t                                   m_fix_f29_pass = 0; // KYTY_FIX_F29: passes, grows only at 1',
], 'h_member')
save(H, t, crlf)

# ---------------- faultManager.cpp ----------------
C = 'src/graphics/host_gpu/renderer/cache/faultManager.cpp'
t, crlf = load(C)
t = replace_lines(t, [
    '#include "common/assert.h"',
    '#include "common/logging/log.h"',
], [
    '#include "common/assert.h"',
    '#include "common/envFlag.h"',
    '#include "common/logging/log.h"',
], 'c_inc1')
t = replace_lines(t, [
    '#include <algorithm>',
    '#include <bit>',
    '#include <cinttypes>',
    '#include <cstring>',
    '#include <limits>',
], [
    '#include <algorithm>',
    '#include <atomic>',
    '#include <bit>',
    '#include <cinttypes>',
    '#include <cstdlib>',
    '#include <cstring>',
    '#include <limits>',
], 'c_inc2')
t = replace_lines(t, [
    '} // namespace',
    '',
    'FaultManager::FaultManager(GraphicContext& graphics, CommandScheduler& scheduler,',
], [
    '// KYTY_FIX_F29: at most this many "FixF29: overflow" lines per process.',
    'constexpr uint64_t FixF29OverflowLines = 32;',
    '',
    '} // namespace',
    '',
    'bool FixF29Enabled() {',
    '\tstatic const bool enabled = Common::EnvValueOn(std::getenv("KYTY_FIX_F29"));',
    '\treturn enabled;',
    '}',
    '',
    'FaultAreaParse ParseFaultArea(const uint64_t* area, bool clamp, const FaultAreaVisitor& visit,',
    '                              const FaultAreaPass& pass) {',
    '\tstatic std::atomic<uint64_t> overflow_total {0};',
    '\tconstexpr auto               last_record = static_cast<uint32_t>(MaxPageFaults - 1);',
    '\tFaultAreaParse               parse;',
    '\tparse.raw   = static_cast<uint32_t>(area[0]);',
    '\tparse.count = clamp ? std::min(parse.raw, last_record) : parse.raw;',
    '\tif (clamp && parse.raw > last_record) {',
    '\t\tconst uint64_t total = overflow_total.fetch_add(1, std::memory_order_relaxed) + 1;',
    '\t\tif (total <= FixF29OverflowLines) {',
    '\t\t\tLOGF("FixF29: overflow pass=%" PRIu64 " area=%u count=%u read=%u total=%" PRIu64 "\\n", pass.pass,',
    '\t\t\t     pass.area, parse.raw, parse.count, total);',
    '\t\t}',
    '\t}',
    '\tfor (uint32_t index = 1; index <= parse.count; ++index) {',
    '\t\tvisit(index, area[index]);',
    '\t}',
    '\treturn parse;',
    '}',
    '',
    'FaultManager::FaultManager(GraphicContext& graphics, CommandScheduler& scheduler,',
], 'c_func')
t = replace_lines(t, [
    '\t     LoopCap::BvhLoopCapSignatureToken().c_str(), LoopCap::BvhLoopCapSlot(0x380bb9d636390baeull));',
], [
    '\t     LoopCap::BvhLoopCapSignatureToken().c_str(), LoopCap::BvhLoopCapSlot(0x380bb9d636390baeull));',
    '\tLOGF("FixF29: mode=%d\\n", FixF29Enabled() ? 1 : 0);',
], 'c_mode')
t = replace_lines(t, [
    '\tconst auto area = m_current_area;',
    '\tm_scheduler.DeferOperation([this, mapped, offset, area, trips, trip_offset] {',
], [
    '\tconst auto     area     = m_current_area;',
    '\tconst uint64_t fix_pass = FixF29Enabled() ? ++m_fix_f29_pass : 0;',
    '\tm_scheduler.DeferOperation([this, mapped, offset, area, trips, trip_offset, fix_pass] {',
], 'c_defer')
t = replace_lines(t, [
    '\t\tconst auto* faults = std::bit_cast<const uint64_t*>(mapped);',
    '\t\tconst auto  count  = static_cast<uint32_t>(faults[0]);',
    '\t\tfor (uint32_t index = 1; index <= count; ++index) {',
    '\t\t\tfault_ranges.Add(faults[index], BufferCache::CACHING_PAGESIZE);',
    '\t\t\tLOGF("Accessed non-GPU cached memory at 0x%016" PRIx64 "\\n", faults[index]);',
    '\t\t}',
], [
    '\t\tconst auto* faults = std::bit_cast<const uint64_t*>(mapped);',
    '\t\t(void)ParseFaultArea(',
    '\t\t    faults, FixF29Enabled(),',
    '\t\t    [&fault_ranges](uint32_t /*index*/, uint64_t value) {',
    '\t\t\t    fault_ranges.Add(value, BufferCache::CACHING_PAGESIZE);',
    '\t\t\t    LOGF("Accessed non-GPU cached memory at 0x%016" PRIx64 "\\n", value);',
    '\t\t    },',
    '\t\t    {fix_pass, area});',
], 'c_loop')
save(C, t, crlf)

# ---------------- CMakeLists.txt ----------------
M = 'CMakeLists.txt'
t, crlf = load(M)
t = replace_lines(t, [
    'add_kyty_full_emulator_test(audio_propagation_tests',
    '\t"${KYTY_TESTS_DIR}/AudioPropagationTests.cpp")',
    '',
], [
    'add_kyty_full_emulator_test(audio_propagation_tests',
    '\t"${KYTY_TESTS_DIR}/AudioPropagationTests.cpp")',
    '',
    '# Track F, F29 fault area parse stand (F44a HPP-791; ROADMAP s122 item 698(d)(1)): the real parser',
    '# FAULT_BUFFER_PROCESS_SPV on the GPU (stage G) and ParseFaultArea of faultManager.cpp on the CPU (stage P); run by',
    '# docs/track-f/f44a/run_stand_f44a.py, not by ctest.',
    'add_kyty_full_emulator_test(f29_fault_stand',
    '\t"${KYTY_TESTS_DIR}/F29FaultStand.cpp")',
    '',
], 'm_target')
save(M, t, crlf)
print('PATCH OK')
