"""Session 99: count successful live resource outcomes in the bindings-only floor.

No game/build invocation. Run once against the session-98 source tree; validates every
anchor before writing anything and preserves each file's original newline convention.
The counters cover existing-program outcomes, not cold shader translation.
"""
from pathlib import Path

ROOT = Path('C:/kyty/KytyPS5')
EDITS = {
    'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp': [
        ('\t\tconst bool  bind_floor = floor_op.armed && floor_op.mode != 2;\n',
         '\t\tconst bool  bind_floor = floor_op.armed && floor_op.mode != 2;\n'
         '\t\t// Session 99: successful live outcomes, only in the bindings-only arm.\n'
         '\t\tconst bool floor_live = floor_op.armed && floor_op.mode == 2;\n'),
        ('\t\t\t\tahead_hit = AheadTake(entry->second, params, read_cache, resources, specialization,\n'
         '\t\t\t\t                      kept >= 0, take_lap ? take_begin : 0);\n',
         '\t\t\t\tahead_hit = AheadTake(entry->second, params, read_cache, resources, specialization,\n'
         '\t\t\t\t                      kept >= 0, take_lap ? take_begin : 0);\n'
         '\t\t\t\tif (floor_live && ahead_hit) {\n'
         '\t\t\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BindFloorLiveAhead, 1);\n'
         '\t\t\t\t}\n'),
        ('\t\t\t\treturn memo_entry->handle;\n',
         '\t\t\t\tif (floor_live) {\n'
         '\t\t\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BindFloorLiveMemo, 1);\n'
         '\t\t\t\t}\n'
         '\t\t\t\treturn memo_entry->handle;\n'),
        ('\t\t\tresources = {};\n'
         '\t\t\tspecialization = {};\n'
         '\t\t}\n'
         '\t\t// Session 96, gate "bindfloor": the first materialisation of each program is kept, and\n',
         '\t\t\tresources = {};\n'
         '\t\t\tspecialization = {};\n'
         '\t\t} else if (floor_live && pg_mat_ran && !floor_reused) {\n'
         '\t\t\t// The failure arm above was not taken: MaterializeResources returned true.\n'
         '\t\t\t// Excludes cold entries, ahead hits, frozen reuse and failed materialisations.\n'
         '\t\t\tCommon::FrameStats::Add(Common::FrameStats::Counter::BindFloorLiveMat, 1);\n'
         '\t\t}\n'
         '\t\t// Session 96, gate "bindfloor": the first materialisation of each program is kept, and\n'),
    ],
    'src/common/frameStats.h': [
        ('\tBindFloorBurnNs,    // bf_burn_ns: time the calibrated idle (bfmode=3) actually burned\n',
         '\tBindFloorBurnNs,    // bf_burn_ns: time the calibrated idle (bfmode=2/3) actually burned\n'),
        ('\t// Session 96, gate "bindfloor" (MEASUREMENT ONLY, ROADMAP.md:1048-1053): image readbacks\n',
         '\t// Session 99: successful existing-program resource outcomes, armed bfmode=2 only.\n'
         '\t// No timers or proglap dependency; cold translations and failed attempts are excluded.\n'
         '\tBindFloorLiveAhead, // bf_live_ahead: AheadTake supplied a live snapshot\n'
         '\tBindFloorLiveMat,   // bf_live_mat:   MaterializeResources returned true\n'
         '\tBindFloorLiveMemo,  // bf_live_memo:  verified SRT memo supplied a live snapshot\n'
         '\t// Session 96, gate "bindfloor" (MEASUREMENT ONLY, ROADMAP.md:1048-1053): image readbacks\n'),
    ],
    'src/graphics/presentation/videoOut.cpp': [
        ('\t\t\t\t    {"bf_reuse", FS::Counter::BindFloorReuse, false},\n',
         '\t\t\t\t    {"bf_reuse", FS::Counter::BindFloorReuse, false},\n'
         '\t\t\t\t    {"bf_live_ahead", FS::Counter::BindFloorLiveAhead, false},\n'
         '\t\t\t\t    {"bf_live_mat", FS::Counter::BindFloorLiveMat, false},\n'
         '\t\t\t\t    {"bf_live_memo", FS::Counter::BindFloorLiveMemo, false},\n'),
    ],
    'src/common/gates.h': [
        ('file name "bfmode" (1 full, 2 bindings, 3 burn)',
         'file name "bfmode" (1 full, 2 bindings + optional burn, 3 full + burn)'),
        ('// Session 96, measurement only, read only at bfmode=3: microseconds the translation',
         '// Session 96/99, measurement only, read at bfmode=2/3: microseconds the translation'),
    ],
    'src/graphics/host_gpu/renderer/renderDraw.cpp': [
        ('inside it.  At bfmode=3 the calibrated idle is burned exactly where it stood, on this',
         'inside it.  At bfmode=2/3 the calibrated idle is burned exactly where it stood, on this'),
    ],
    'src/graphics/host_gpu/renderer/renderCompute.cpp': [
        ('// Knob "bfburn" at bfmode=3: burned where the removed work stood.',
         '// Knob "bfburn" at bfmode=2/3: burned where the removed work stood.'),
    ],
}

pending = []
for rel, replacements in EDITS.items():
    path = ROOT / rel
    original = path.read_bytes()
    newline = b'\r\n' if b'\r\n' in original else b'\n'
    updated = original
    for before, after in replacements:
        old = before.encode().replace(b'\n', newline)
        new = after.encode().replace(b'\n', newline)
        assert updated.count(old) == 1, (rel, before, updated.count(old))
        updated = updated.replace(old, new, 1)
    pending.append((path, updated))

for path, updated in pending:
    path.write_bytes(updated)
    print(path.relative_to(ROOT))
print('PASS: six files patched; descriptors.cpp and gate definitions untouched')
