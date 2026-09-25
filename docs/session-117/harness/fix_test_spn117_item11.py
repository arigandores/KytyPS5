"""Session 117, ROADMAP item 11: fixtures for the pre-seal fixes of spn117.py."""
from pathlib import Path

p = Path('C:/kyty/s117/test_spn117.py')
s = p.read_text(encoding='utf-8')


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)


rep("""          'spine_cmp': 0, 'spine_bad': 0, 'spine_misal': 0, 'spine_pad': 0, 'spine_lost': 0, 'spine_chk_ns': 0},""",
    """          'spine_cmp': 0, 'spine_bad': 0, 'spine_misal': 0, 'spine_pad': 0, 'spine_lost': 0, 'spine_chk_ns': 0,
          'cram_write': 0},""")
rep("""          'spine_chk_ns': 6000000})""", """          'spine_chk_ns': 6000000, 'cram_write': 0})""")
rep("""         stdout_lines=(), pre=5, order=ABBA, post=0):""",
    """         stdout_lines=(), pre=5, order=ABBA, post=0, strip=()):""")
rep("""        if x:
            xv.update(x(n, b, arm, idx))
""", """        if x:
            xv.update(x(n, b, arm, idx))
        for kind, sn, field in strip:
            if sn == n:
                {'main': mv, 'draw': dv, 'x': xv}[kind].pop(field, None)
""")
# walker rule: need = da_walk + spine against dt - spine (dt 33000, spine 2000 -> frame without the spine 31000)
rep("""case('k1_over_walker_edge', dict(OK, k1='FAIL', consequence='CLOSE_A', walker_fit=False),
     x=lambda n, b, arm, i: {'spine_ns': 2000000}, draw=lambda n, b, arm, i: {'da_walk_us': 31000})
case('k1_over_walker_just_fits', dict(OK, k1='FAIL', consequence='PART2_WALKER', walker_fit=True),
     x=lambda n, b, arm, i: {'spine_ns': 2000000}, draw=lambda n, b, arm, i: {'da_walk_us': 30999})
""", """case('k1_over_walker_edge', dict(OK, k1='FAIL', consequence='CLOSE_A', walker_fit=False),
     x=lambda n, b, arm, i: {'spine_ns': 2000000}, draw=lambda n, b, arm, i: {'da_walk_us': 29000})
case('k1_over_walker_just_fits', dict(OK, k1='FAIL', consequence='PART2_WALKER', walker_fit=True),
     x=lambda n, b, arm, i: {'spine_ns': 2000000}, draw=lambda n, b, arm, i: {'da_walk_us': 28999})
case('k1_over_walker_old_rule', dict(OK, k1='FAIL', consequence='CLOSE_A', walker_fit=False),
     x=lambda n, b, arm, i: {'spine_ns': 2000000}, draw=lambda n, b, arm, i: {'da_walk_us': 30000})
""")
# armed tolerance: 1 % of spine_el on arm-0 kept frames (el 5500 -> 55)
rep("""case('armed_arm0_cmp', dict(verdict='NOT_ADMITTED', failed=['armed']),
     x=lambda n, b, arm, i: {'spine_cmp': 1} if (arm == 0 and i == 50) else {})
""", """case('armed_arm0_cmp', dict(verdict='NOT_ADMITTED', failed=['armed']),
     x=lambda n, b, arm, i: {'spine_cmp': 56} if arm == 0 else {})
case('armed_arm0_cmp_1pct_ok', dict(OK), x=lambda n, b, arm, i: {'spine_cmp': 55} if arm == 0 else {})
""")
# K5 over every x line, the diagnostic lines and cram_write; el_ops; markers; GateArm gap; missing field; pin line
K5 = """case('bad_in_incomplete_frame', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'), blocks=12,
     x=lambda n, b, arm, i: {'spine_bad': 3} if n == START + 1 + PERIOD * 4 + 40 else {},
     drop=(('draw', START + 1 + PERIOD * 4 + 40),))
case('bad_in_dup_frame', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'), blocks=12,
     x=lambda n, b, arm, i: {'spine_bad': 2} if n == START + 1 + PERIOD * 5 + 40 else {},
     dup=(START + 1 + PERIOD * 5 + 40,))
case('mismatch_line_only', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     extra_log=('SpineMismatch: sub=15 el=0 op=0x15 parts=sh, reg=8',))
case('misalign_line_only', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     extra_log=('SpineMisalign: sub=15 planned=7 executed=6',))
case('abort_line_ok', dict(OK, k5='PASS'), extra_log=('SpineAbort: sub=15 packets=10 elements=2',))
case('cram_write_one', dict(verdict='ADMITTED', k5='FAIL', consequence='STOP_STAGE4'),
     x=lambda n, b, arm, i: {'cram_write': 1} if (b == 2 and i == 3) else {})
case('el_ops_lo_edge', dict(OK), x=lambda n, b, arm, i: {'spine_el': 5292} if arm == 1 else {})
case('el_ops_lo', dict(verdict='NOT_ADMITTED', failed=['el_ops']),
     x=lambda n, b, arm, i: {'spine_el': 5291} if arm == 1 else {})
case('el_ops_hi_edge', dict(OK), x=lambda n, b, arm, i: {'spine_el': 5848} if arm == 1 else {})
case('el_ops_hi', dict(verdict='NOT_ADMITTED', failed=['el_ops']),
     x=lambda n, b, arm, i: {'spine_el': 5849} if arm == 1 else {})
for mk, text in (('hang', 'GpuHangAbort: tick=5'), ('slow', 'GpuWaitSlow: tick=5'), ('mhung', 'GpuMarkerHung: cs=1'),
                 ('ckpt', 'GpuCheckpointHang: op=1'), ('lost', 'Vulkan: ErrorDeviceLost'),
                 ('term', '--- std::terminate ---'), ('abort', '--- abort() ---'), ('fatal', '--- Fatal Error ---'),
                 ('unh', 'Unhandled exception: 0xc0000005'), ('err', '--- Error ---'),
                 ('skip', 'AsyncPipelines: skipped draw 0x1')):
    case('marker_' + mk, dict(verdict='NOT_ADMITTED', failed=['no_marker']), extra_log=(text,))
case('arm_block_gap', dict(verdict='NOT_ADMITTED', failed=['arms', 'gate_lines', 'blocks', 'armed', 'el_ops']),
     gate_arm=lambda b, arm: [] if b == 3 else ['GateArm: arm=%d arms=2 block=%d frame=%d period=90 abba=1 text=%s'
                                                % (arm, b, START + PERIOD * b, TEXT[arm])])
case('field_missing', dict(verdict='NOT_ADMITTED', failed=['blocks']),
     strip=(('x', START + 1 + PERIOD * 2 + 50, 'spine_pad'),))
case('pin_malformed', dict(verdict='NOT_ADMITTED', failed=['pinned']), pins=('GpuClockPin: mode X',))
"""
rep("""case('spine_line_absent', """, K5 + """case('spine_line_absent', """)
rep("""        (res['walker_need_us'], 1500.0), (res['dt0_us'], 33000.0),""",
    """        (res['walker_need_us'], 1500.0), (res['dt0_us'], 33000.0), (res['frame_nospine_us'], 32500.0),
        (res['raw_k5']['spine_bad'], 0), (res['k5_lines'], 0),""")
p.write_text(s, encoding='utf-8')
print('test ok')
