p = 'C:/kyty/s146/step0/partf146.py.txt'
t = open(p, 'rb').read().decode('ascii')


def rep(old, new):
    global t
    assert t.count(old) == 1, old[:80]
    t = t.replace(old, new)


rep("""          ('two lines, the second one 1/1', ['DualSrcBlend: supported=0 enabled=0', DUAL11] + wl6(SKY, dual=False), True))""",
    """          ('two lines, the second one 1/1', ['DualSrcBlend: supported=0 enabled=0', DUAL11] + wl6(SKY, dual=False), True),
          ('supported=1 enabled=10 (two digits)', ['DualSrcBlend: supported=1 enabled=10'] + wl6(SKY, dual=False), False))""")
rep("""root = mk146(BASE / 'F11', 'v146_05', extra=[STUB, STUB, ASR, UMP], std=[STUB, ASR])""",
    """root = mk146(BASE / 'F11', 'v146_05', extra=[STUB, STUB, ASR, UMP], std=[STUB, ASR, UMP, UMP])""")
rep("""e11['asserts'] == dict(log=1, stdout=1, ump_log=1, ump_stdout=0) and""",
    """e11['asserts'] == dict(log=1, stdout=1, ump_log=1, ump_stdout=2) and""")
rep(""""user_msg_param" lines log 1, stdout 0 - != '""", """"user_msg_param" lines log 1, stdout 2 - != '""")
rep("""e12c = S.entry_of('v146_05', mk146(BASE / 'F12c', 'v146_05'), SH6)""",
    """e12c = S.entry_of('v146_05', mk146(BASE / 'F12c', 'v146_05'), SH6)
e12d = S.entry_of('v146_05', mk146(BASE / 'F12d', 'v146_05', tiles='TILES rec_v146_05.mp4 sha256 %s: frames 5; tile events T4 0, '
                                   'T12 0; events \\n' % ('ab' * 32)), SH6)""")
rep("""           e12b['tiles'] is None and e12c['tiles'] is None and adm_ok(e12) and adm_ok(e12b) and""",
    """           e12b['tiles'] is None and e12c['tiles'] is None and adm_ok(e12) and adm_ok(e12b) and
           e12d['tiles'] is not None and e12d['tiles']['t4'] == 0 and e12d['tiles']['events'] == '' and""")
rep("""(R19c / 'score_i146_v.txt').write_text('FS VERDICT i146_v: PASS\\nWARMUP VERDICT i146_v: FAIL (x)\\n')""",
    """(R19c / 'score_i146_v.txt').write_text('WARMUP VERDICT i146_v: FAIL (x)\\nFS VERDICT i146_v: PASS\\n')""")
open(p, 'wb').write(t.encode('ascii'))
print('ok')
