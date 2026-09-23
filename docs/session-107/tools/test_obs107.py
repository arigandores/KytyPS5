"""Session 107: fixtures for obs107.py - every decision term carries a planted effect and every verdict branch is
walked in NON-draft mode (the seal check is pointed at a throwaway file).  Rule from ROADMAP, decision after 106.
    python C:/kyty/s106_stage/test_obs107.py <obs107.py path>
"""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

SRC = Path(sys.argv[1])
BASE = Path('C:/kyty/s106_stage/fx_obs')
NL = chr(10)


def make(name, would, look=100, h2_ns=150000, wall_ns=250000, cpu_ns=180000, bad=0, drop_key=None,
         verify_line=False, gates='plkstat=1 cspmemo=3', fatal=False):
    d = BASE / name
    d.mkdir(parents=True, exist_ok=True)
    lines = ['GpuClockPin: mode 1', 'RecordThread: started gpu', 'RecordThread: started present']
    if verify_line:
        lines.append('CspMemoVerify: MISMATCH hash=0x1 memo_id=1 id=2')
    if fatal:
        lines.append('AsyncPipelines: skipped draw')
    for n in range(1790, 1800 + 3100):
        x = {'pl_cont_n': 300, 'pl_cont_wall_ns': wall_ns, 'pl_cont_cpu_ns': cpu_ns, 'pl_cont_h0_ns': 20000,
             'pl_cont_h1_ns': 30000, 'pl_cont_h2_ns': h2_ns, 'pl_cont_h3_ns': wall_ns - 50000 - h2_ns,
             'pl_cont_h0_n': 20, 'pl_cont_h1_n': 30, 'pl_cont_h2_n': 200, 'pl_cont_h3_n': 50,
             'pl_wq_hold_ns': 400000, 'pl_wq_hold_n': 1070, 'pl_wp_hold_ns': 300000, 'pl_wp_hold_n': 100,
             'cspm_look': look, 'cspm_would': would, 'cspm_skip': 0, 'cspm_bad': bad if n == 2500 else 0,
             'cspm_store': look, 'cspm_clear': 0, 'cspf_have': 90, 'cspf_new': 0, 'pl_prog_n': 5000,
             'pl_prog_wait_us': 100, 'pl_pipe_wait_us': 120, 'pl_cs_wait_us': 150}
        if drop_key:
            x.pop(drop_key)
        lines.append('FrameTrace: n=%d dt_us=31000 cpu_gpu_us=30000 draws=5000' % n)
        lines.append('FrameTrace-draw: n=%d spin_gpu_us=30' % n)
        lines.append('FrameTrace-x: n=%d ' % n + ' '.join('%s=%d' % kv for kv in x.items()))
    (d / 'log_obs107.txt').write_text(NL.join(lines) + NL, encoding='utf-8')
    meta = {'binary_sha256': 'x', 'gates': 'dawalk=1 ' + gates, 'attempts': [{'outcome': 'ok', 'hold_exit': None}]}
    (d / 'obs107.json').write_text(json.dumps(meta), encoding='utf-8')
    return d


spec = importlib.util.spec_from_file_location('obs107', SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
seal = BASE / 'seal.md'
BASE.mkdir(parents=True, exist_ok=True)
seal.write_text('fixture seal', encoding='utf-8')
mod.PRED = str(seal)
mod.PRED_SHA = hashlib.sha256(seal.read_bytes()).hexdigest()
mod.PRED_BYTES = seal.stat().st_size

cases = [
    ('go', dict(would=90), 'GO'),
    ('nogo_rate', dict(would=30), 'NO-GO'),
    ('nogo_tag2', dict(would=90, h2_ns=50000), 'NO-GO'),
    ('verify_bad', dict(would=90, bad=1), 'VERIFY FAIL'),
    ('verify_line', dict(would=90, verify_line=True), 'VERIFY FAIL'),
    ('verify_nohit', dict(would=0), 'VERIFY FAIL'),
    ('missing_field', dict(would=90, drop_key='pl_cont_h2_ns'), 'INVALID'),
    ('gate_text', dict(would=90, gates='plkstat=1 cspmemo=1'), 'INVALID'),
    ('fatal', dict(would=90, fatal=True), 'INVALID'),
]
ok = True
for name, kw, want in cases:
    root = make(name, **kw)
    out = mod.evaluate(root, 'obs107', False)
    got = out['verdict']
    r = out['readouts']
    passed = got.startswith(want)
    ok &= passed
    print('%-14s want %-12s got %-60s %s  spin=%s tag2=%s rate=%s' % (name, want, got[:60], 'OK' if passed else 'FAIL',
                                                                   r['spin_share'], r['tag2_us'], r['would_rate']))
print('ALL OK' if ok else 'FIXTURE FAILURES')
sys.exit(0 if ok else 1)
