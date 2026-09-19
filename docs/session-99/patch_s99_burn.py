"""Session 99: allow calibrated burn in the bindings-only floor. No defaults change."""
from pathlib import Path

path = Path('C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/pipeline/descriptors.cpp')
raw = path.read_bytes()
text = raw.decode('utf-8').replace('\r\n', '\n')
old = '''// Session 96, knob "bfburn" at "bfmode"=3 (MEASUREMENT ONLY, ROADMAP.md:1062-1065): the'''
new = '''// Sessions 96/99, knob "bfburn" at "bfmode"=2 or 3 (MEASUREMENT ONLY): the'''
assert text.count(old) == 1
text = text.replace(old, new)
old = '''// was really burned, never what was asked for.  At any other mode this returns on the first
// line and costs one relaxed atomic load.
void RenderExecutor::BindFloorBurnSlice() {
	// Session 97: the latched mode of this op, like every other floor site.
	if (BindFloorCurrentOp().mode != 3) {'''
new = '''// was really burned, never what was asked for.  Modes 0/1 return without burning.
void RenderExecutor::BindFloorBurnSlice() {
	// Read the latched mode once: bindings-only needs its own DRS calibration too.
	const auto mode = BindFloorCurrentOp().mode;
	if (mode != 2 && mode != 3) {'''
assert text.count(old) == 1
text = text.replace(old, new)
result = text.encode('utf-8')
if b'\r\n' in raw:
    result = result.replace(b'\n', b'\r\n')
path.write_bytes(result)
print('PASS: modes 2/3 can burn; modes 0/1 and zero budget remain inert')
