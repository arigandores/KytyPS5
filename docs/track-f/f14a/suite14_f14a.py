"""F14a (HPP-487): failures of the full shader_cfg_tests run (suite/suite.log) by test name, against the historical list of 14
of HANDOFF section 4 (docs/agent/HANDOFF.md:7716-7721; since session 24 the reference is 0 failures, HANDOFF:7714)."""
import re
import sys

LOG = 'C:/kyty/f287/f14a/suite/suite.log'
HIST = ['CfgLoopHeaderDsAppendConsumeStructured', 'CfgLoopHeaderDsReadStructured', 'CfgLoopHeaderDsRead2B64Structured',
        'CfgLoopEarlyBreakNoSelection', 'CfgNestedLoopLocalExitNoSelection', 'CfgConditionalLatchNoSelection',
        'CfgDirectConditionalLatchNoSelection', 'CfgLoopEarlyContinuesNoSelection', 'CfgLoopGatewaySelection',
        'CfgConditionalLoopHeaderSelection', 'CfgMultipleLoopLatches', 'CfgNestedEarlyExitLoopForwarders',
        'PixelImageSampleLodSelection', 'SrtWalkerRealSBufferTranslation']
tests = []
fails = {}
cur = None
for line in open(LOG, 'rb').read().decode('latin1').replace('\r', '').split('\n'):
    m = re.match(r'^\[test\] (\S+)$', line)
    if m:
        cur = m.group(1)
        tests.append(cur)
    elif line.startswith('ShaderCfgTests: failed: '):
        fails.setdefault(cur, []).append(line[len('ShaderCfgTests: failed: '):])
print('tests run:', len(tests), 'distinct:', len(set(tests)))
print('failing tests:', len(fails))
for t, msgs in fails.items():
    print('  ', t, '|', ' | '.join(msgs))
present = [h for h in HIST if any(t.endswith(h) for t in tests)]
failing_hist = [h for h in HIST if any(t.endswith(h) for t in fails)]
print('historical 14: run now %d of 14; failing now %d: %s' % (len(present), len(failing_hist), ','.join(failing_hist)))
print('missing from the run:', ','.join(h for h in HIST if h not in present) or '-')
ok = len(tests) == 127 and list(fails) == ['TestNewShaderRecompilerPixelImageSampleLodSelection'] and len(present) == 14
print('ALL OK' if ok else 'FAIL')
sys.exit(0 if ok else 1)
