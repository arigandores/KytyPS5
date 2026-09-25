"""Session 117, ROADMAP item 11: pre-seal fixes of spn117.py (walker fit, K5 raw sums and lines, cram_write, el_ops,
armed tolerance)."""
from pathlib import Path

p = Path('C:/kyty/s117/spn117.py')
s = p.read_text(encoding='utf-8')


def rep(old, new):
    global s
    assert s.count(old) == 1, old[:80]
    s = s.replace(old, new)


rep("""  armed                   over the kept frames: arm 0 sum spine_n > 0, sum spine_el > 0, sum spine_cmp == 0; arm 1
                          sum spine_cmp > 0
""", """  armed                   over the kept frames: arm 0 sum spine_n > 0, sum spine_el > 0, 100 * sum spine_cmp <= sum
                          spine_el (a mode-2 submission blocked past a flip may still compare - ROADMAP 117 item 11);
                          arm 1 sum spine_cmp > 0
  el_ops                  over the kept frames of arm 1: spine_el / (draws + dispatches) in [EL_OPS_LO_PCT,
                          EL_OPS_HI_PCT] % (the K5 denominator is not the spine's own count taken blind)
""")
rep("""K5 (reproduction), over EVERY frame from the first block's start frame on (both arms, block edges included: each
submission latches its own mode, so a compare can only come from a mode-2 plan):
  FAIL            sum spine_bad > 0 or sum spine_misal > 0
""", """K5 (reproduction), over EVERY FrameTrace-x line with n > START (both arms, block edges, duplicated lines and frames
missing other lines included: each submission latches its own mode, so a compare can only come from a mode-2 plan):
  FAIL            sum spine_bad > 0 or sum spine_misal > 0 or sum cram_write > 0 (const RAM is outside the compare), or
                  any `SpineMismatch:` / `SpineMisalign:` line anywhere in the log
""")
rep("""  PASS  k1_us <= K1_MAX_US;  FAIL otherwise, and then walker_fit = mean over arm-0 kept frames of
        (da_walk_us + spine_ns / 1000) < mean dt_us over the same frames (the walker thread could carry the spine).
""", """  PASS  k1_us <= K1_MAX_US;  FAIL otherwise, and then walker_fit = mean over arm-0 kept frames of
        (da_walk_us + spine_ns / 1000) < mean of (dt_us - spine_ns / 1000) over the same frames: the walker thread
        could carry the spine within the frame the GuestGpu thread would have without it (ROADMAP 117 item 11).
""")
rep("""spine_bad, spine_misal, spine_pad, spine_lost, spine_abort; the first SpineMismatch / SpineMisalign / SpineAbort lines.
""", """spine_bad, spine_misal, spine_pad, spine_lost, spine_abort, cram_write (complete frames, and every x line for K5);
the first SpineMismatch / SpineMisalign / SpineAbort lines.  spine_misal = the real element count of a submission
differs from its plan; spine_lost = compares lost because another plan of the same processor replaced the snapshots
(an instrument limit, caught by the cmp ratio, not a failure) - ROADMAP 117 item 11 (3).
""")
rep("K1_MAX_US = 1200\n", "K1_MAX_US = 1200\nEL_OPS_LO_PCT = 95\nEL_OPS_HI_PCT = 105\n")
rep("""            'spine_lost', 'spine_chk_ns')
REPORT_KEYS""", """            'spine_lost', 'spine_chk_ns', 'cram_write')
REPORT_KEYS""")
rep("ALL_SUMS = ('spine_bad', 'spine_misal', 'spine_pad', 'spine_lost', 'spine_abort', 'spine_cmp', 'spine_el', 'spine_n')",
    "ALL_SUMS = ('spine_bad', 'spine_misal', 'spine_pad', 'spine_lost', 'spine_abort', 'spine_cmp', 'spine_el', 'spine_n',\n"
    "            'cram_write')\nK5_RAW = ('spine_bad', 'spine_misal', 'cram_write')")
rep("DIAG = (b'SpineMismatch:', b'SpineMisalign:', b'SpineAbort:')",
    "DIAG = (b'SpineMismatch:', b'SpineMisalign:', b'SpineAbort:')\nK5_LINES = (b'SpineMismatch:', b'SpineMisalign:')")
rep("""    seen = {'main': {}, 'draw': {}, 'x': {}}
    dups = set()
""", """    seen = {'main': {}, 'draw': {}, 'x': {}}
    dups = set()
    raw_k5 = {k: 0 for k in K5_RAW}
    k5_lines = 0
""")
rep("""            if line.startswith(DIAG) and len(diag) < 20:
                diag.append(line[:200].decode('utf-8', 'replace').strip())
""", """            if line.startswith(DIAG) and len(diag) < 20:
                diag.append(line[:200].decode('utf-8', 'replace').strip())
            if line.startswith(K5_LINES):
                k5_lines += 1
""")
rep("""                got = dict(FIELD.findall(line, m.end()))
                rec = {k: int(got[k.encode()]) for k in names if k.encode() in got}
""", """                got = dict(FIELD.findall(line, m.end()))
                rec = {k: int(got[k.encode()]) for k in names if k.encode() in got}
                if kind == 'x' and n > START:
                    for k in K5_RAW:
                        raw_k5[k] += int(got.get(k.encode(), 0))
""")
rep("""        armed=(ksum(0, 'spine_n') > 0 and ksum(0, 'spine_el') > 0 and ksum(0, 'spine_cmp') == 0
               and ksum(1, 'spine_cmp') > 0),
""", """        armed=(ksum(0, 'spine_n') > 0 and ksum(0, 'spine_el') > 0 and 100 * ksum(0, 'spine_cmp') <= ksum(0, 'spine_el')
               and ksum(1, 'spine_cmp') > 0),
        el_ops=(ops1 > 0 and 100 * ksum(1, 'spine_el') >= EL_OPS_LO_PCT * ops1
                and 100 * ksum(1, 'spine_el') <= EL_OPS_HI_PCT * ops1),
""")
rep("""    checks = dict(
        binary=""", """    ops1 = ksum(1, 'draws') + ksum(1, 'dispatches')
    checks = dict(
        binary=""")
rep("""    if sums_all['spine_bad'] > 0 or sums_all['spine_misal'] > 0:
        k5 = 'FAIL'""", """    if raw_k5['spine_bad'] > 0 or raw_k5['spine_misal'] > 0 or raw_k5['cram_write'] > 0 or k5_lines > 0:
        k5 = 'FAIL'""")
rep("""    walker_need = mean([v['da_walk_us'] + v['spine_us'] for v in values[0]])
    dt0 = mean([v['dt_us'] for v in values[0]])
    walker_fit = walker_need is not None and dt0 is not None and walker_need < dt0
""", """    walker_need = mean([v['da_walk_us'] + v['spine_us'] for v in values[0]])
    dt0 = mean([v['dt_us'] for v in values[0]])
    frame_nospine = mean([v['dt_us'] - v['spine_us'] for v in values[0]])
    walker_fit = walker_need is not None and frame_nospine is not None and walker_need < frame_nospine
""")
rep("""               cmp_ratio=cmp_ratio, walker_need_us=walker_need, dt0_us=dt0, walker_fit=walker_fit,""",
    """               cmp_ratio=cmp_ratio, walker_need_us=walker_need, dt0_us=dt0, frame_nospine_us=frame_nospine,
               walker_fit=walker_fit, raw_k5=raw_k5, k5_lines=k5_lines,""")
rep("""    out.append('K5 %s: sums over %d frames %s; cmp_ratio (arm 1 kept) %s (bar %d %%)'
               % (res['k5'], res['all_frames'], ', '.join('%s=%d' % kv for kv in res['sums_all'].items()),
                  fmt(res['cmp_ratio'], 4), CMP_MIN_PCT))
""", """    out.append('K5 %s: every x line after %d: %s, SpineMismatch/Misalign lines %d; complete frames (%d): %s; '
               'cmp_ratio (arm 1 kept) %s (bar %d %%)'
               % (res['k5'], START, ', '.join('%s=%d' % kv for kv in res['raw_k5'].items()), res['k5_lines'],
                  res['all_frames'], ', '.join('%s=%d' % kv for kv in res['sums_all'].items()),
                  fmt(res['cmp_ratio'], 4), CMP_MIN_PCT))
""")
rep("""    out.append('K1 %s: spine %s us a frame (arm 0 kept; bar %d); walker need %s us vs dt %s us -> walker_fit %s'
               % (res['k1'], fmt(res['k1_us']), K1_MAX_US, fmt(res['walker_need_us']), fmt(res['dt0_us']),
                  res['walker_fit']))
""", """    out.append('K1 %s: spine %s us a frame (arm 0 kept; bar %d); walker need %s us vs the frame without the spine %s us '
               '(dt %s) -> walker_fit %s'
               % (res['k1'], fmt(res['k1_us']), K1_MAX_US, fmt(res['walker_need_us']), fmt(res['frame_nospine_us']),
                  fmt(res['dt0_us']), res['walker_fit']))
""")
p.write_text(s, encoding='utf-8')
print('scorer ok')
