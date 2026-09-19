"""Session 99 continuation: optional CPU readout beside the unchanged wall burn.

Only the three explicitly assigned C++ files are edited. Preserve their line endings.
"""
from pathlib import Path
import hashlib

ROOT = Path('C:/kyty/KytyPS5')

def replace_once(path, before, after):
    original = path.read_bytes()
    newline = b'\r\n' if b'\r\n' in original else b'\n'
    old = before.encode().replace(b'\n', newline)
    new = after.encode().replace(b'\n', newline)
    if original.count(old) != 1:
        raise RuntimeError(f'{path}: expected one anchor, found {original.count(old)}')
    result = original.replace(old, new, 1)
    path.write_bytes(result)
    print(f'{path}: {hashlib.sha256(original).hexdigest()} -> {hashlib.sha256(result).hexdigest()}')

replace_once(ROOT / 'src/common/frameStats.h',
'''\tBindFloorBurnNs,    // bf_burn_ns: time the calibrated idle (bfmode=2/3) actually burned
''',
'''\tBindFloorBurnNs,    // bf_burn_ns: time the calibrated idle (bfmode=2/3) actually burned
\t// Session 99: optional KYTY_BIND_FLOOR_CPU=1 readout, same clock as cpu_gpu_us.
\tBindFloorBurnCpuNs, // bf_burn_cpu_ns: sum of successful GuestGpu CPU deltas around burn
\tBindFloorBurnCpuN,  // bf_burn_cpu_n: successful strictly positive CPU sample pairs
\tBindFloorBurnCpuBad,// bf_burn_cpu_bad: zero/backwards readings or zero CPU delta
\tBindFloorBurnProbeNs, // bf_burn_probe_ns: wall bounds around both CPU queries, all pairs
''')

replace_once(ROOT / 'src/graphics/presentation/videoOut.cpp',
'''\t\t\t\t    {"bf_burn_ns", FS::Counter::BindFloorBurnNs, false},
''',
'''\t\t\t\t    {"bf_burn_ns", FS::Counter::BindFloorBurnNs, false},
\t\t\t\t    {"bf_burn_cpu_ns", FS::Counter::BindFloorBurnCpuNs, false},
\t\t\t\t    {"bf_burn_cpu_n", FS::Counter::BindFloorBurnCpuN, false},
\t\t\t\t    {"bf_burn_cpu_bad", FS::Counter::BindFloorBurnCpuBad, false},
\t\t\t\t    {"bf_burn_probe_ns", FS::Counter::BindFloorBurnProbeNs, false},
''')

replace_once(ROOT / 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp',
'''\tconst uint64_t begin = Common::FrameStats::NowNs();
\tuint64_t       now   = begin;
\twhile (now - begin < slice) {
\t\tnow = Common::FrameStats::NowNs();
\t}
\tfloor.burned_ns += now - begin;
\tCommon::FrameStats::Add(Common::FrameStats::Counter::BindFloorBurnNs, now - begin);
''',
'''\t// Session 99, measurement only: a parallel CPU readout, NEVER the budget clock.
\t// Initialised once at the first actual burn; modes 0/1 and zero budgets never reach it.
\tstatic const bool cpu_probe = [] {
\t\tconst char* value = std::getenv("KYTY_BIND_FLOOR_CPU");
\t\tconst bool on = value != nullptr && value[0] == '1' && value[1] == '\\0';
\t\tLOGF("BindFloorCpu: mode %u\\n", on ? 1u : 0u);
\t\treturn on;
\t}();
\tuint64_t cpu_begin = 0;
\tuint64_t probe_ns  = 0;
\tif (cpu_probe) {
\t\tconst uint64_t probe_begin = Common::FrameStats::NowNs();
\t\tcpu_begin = Common::FrameStats::ThreadCpuNs(Common::FrameStats::ThreadRole::Gpu);
\t\tprobe_ns = Common::FrameStats::NowNs() - probe_begin;
\t}
\tconst uint64_t begin = Common::FrameStats::NowNs();
\tuint64_t       now   = begin;
\twhile (now - begin < slice) {
\t\tnow = Common::FrameStats::NowNs();
\t}
\tif (cpu_probe) {
\t\tconst uint64_t probe_begin = Common::FrameStats::NowNs();
\t\tconst uint64_t cpu_end =
\t\t    Common::FrameStats::ThreadCpuNs(Common::FrameStats::ThreadRole::Gpu);
\t\tprobe_ns += Common::FrameStats::NowNs() - probe_begin;
\t\t// Zero samples (including a zero delta) fail visibly. Do not substitute wall time.
\t\tif (cpu_begin != 0 && cpu_end > cpu_begin) {
\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BindFloorBurnCpuNs,
\t\t\t                        cpu_end - cpu_begin);
\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BindFloorBurnCpuN, 1);
\t\t} else {
\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BindFloorBurnCpuBad, 1);
\t\t}
\t\t// Both query costs are bounded, including the tails outside the CPU sample span.
\t\t// Probe/counter overhead is intentionally not deducted from cpu_gpu_us.
\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BindFloorBurnProbeNs, probe_ns);
\t}
\tfloor.burned_ns += now - begin;
\tCommon::FrameStats::Add(Common::FrameStats::Counter::BindFloorBurnNs, now - begin);
''')
