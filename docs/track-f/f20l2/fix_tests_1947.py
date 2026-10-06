"""F20l2 (HPP-648): four fixtures added to test_b32_read.py after sens_b32.py missed 4 edits of 111 (2026-10-06 19:47Z):
ring_hold (cumulative) apart from ring_hold_w; GuestGpu step with S >= 50 % (not Sw); the theta admission row itself; the loader mode
of the reference reread.  The reader b32_read.py is not touched.  ASCII only."""
import sys

P = 'C:/kyty/f287/f20l2/test_b32_read.py'
src = open(P, 'rb').read().decode('utf-8')
crlf = '\r\n' in src
src = src.replace('\r\n', '\n')


def rep(old, new):
    global src
    n = src.count(old)
    if n != 1:
        print('anchor count %d: %r' % (n, old[:80]))
        sys.exit(1)
    src = src.replace(old, new)


rep("flip=2, threads=None, waits=None, xw=None, x=True, hdr=True, cum=None, ring_hold=0):",
    "flip=2, threads=None, waits=None, xw=None, x=True, hdr=True, cum=None, ring_hold=0, ring_hold_c=None):")
rep("(cum or {}).get('rep_drop', 0), ring_hold, ring_hold))",
    "(cum or {}).get('rep_drop', 0), ring_hold if ring_hold_c is None else ring_hold_c, ring_hold))")
rep("res = read('ring', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, ring_hold=3, threads=GUEST_R)),",
    "res = read('ring', build({T0: dict(dt=200000, diag=diag_block(FIRST + T0, 200000, ring_hold=3, ring_hold_c=7, threads=GUEST_R)),")
rep("check('ring_hold_w sum 3, frames 1, -x lines with the field 2',",
    "check('ring_hold_w sum 3 (cumulative ring_hold 7 not summed), frames 1, -x lines with the field 2',")
rep("""check('stand pc: no waker, no peer -> EMU_WAIT:gpu_wait, GuestGpu not in the chain',""",
    """THR_PC4 = [thr(0, 'Present', 'Present', S=S), thr(1, 'Gpu', 'Gpu', S=S), thr(2, 'DrawThread', 'guest', W={'gpu_wait': S})]
_res4 = read('stand_pc4', build({T0 + 1: dict(dt=230000, diag=diag_block(FIRST + T0 + 1, 230000, instr=0, threads=THR_PC4,
                                                                        waits=[dict(slot=2, kind='gpu_wait', waker=-1, peer=1)]))},
                                test_fire_idx=T0 + 1, stand_mode='gpusleep'))
_st4 = _res4['stand'][0]
check('stand pc: GuestGpu S 40 of 40 (not Sw) in the chain -> member yes', _st4['gpu_in_chain'] and _st4['gpu_sw_or_s50'], _st4)
check('stand pc: no waker, no peer -> EMU_WAIT:gpu_wait, GuestGpu not in the chain',""")
rep("""check('admission pd without the loader FAIL', not r['admitted'])""",
    """check('admission pd without the loader FAIL', not r['admitted'])
r = adm_dir('pd_loadhalf', 'b32_pd', R.FORM['b32_pd'], log_on, binary=B2, load=dict(LD, mode='half'))
check('admission pd with the loader mode half (not all) FAIL', not r['admitted'] and
      [a[1] for a in r['admission'] if a[0].startswith('loader ran')] == [False], [a for a in r['admission'] if not a[1]])""")
rep("""check('admission: no theta_load line in the seal FAIL, the log is not read', not r['admitted'] and r['log'] is None)""",
    """check('admission: no theta_load line in the seal FAIL, the log is not read', not r['admitted'] and r['log'] is None)
check('admission: the theta_load row itself FAIL when the seal has no line', [a[1] for a in r['admission'] if a[0].startswith('theta_load from the seal')] == [False],
      [a for a in r['admission'] if not a[1]])""")
if crlf:
    src = src.replace('\n', '\r\n')
open(P, 'wb').write(src.encode('utf-8'))
print('patched', P)
