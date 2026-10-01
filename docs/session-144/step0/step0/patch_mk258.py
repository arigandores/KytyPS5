"""Session 144 step 0: ROADMAP item 258 (d) applied to the scorer builder - the stdout precache member of a W is an
executor member [I] (printed apart, not in the admission); the control gate is marked [I]."""
p = 'C:/kyty/s144/step0/mk_sc144.py'
t = open(p, 'rb').read().decode('ascii')
R = [
("""            r['admit'].append(('W form: no "PipelinePrecache: N recipes ->" line in the log and the emulator stdout (item '
                               '254 (e))', pl == 0 and ps == 0, 'log %s, stdout %d' % (pl, ps)))""",
 """            r['admit'].append(('W form: no "PipelinePrecache: N recipes ->" line in the log (item 254 (e))', pl == 0,
                               'log %s' % pl))"""),
("""        o.append('  precache form (item 254 (e)): "PipelinePrecache: N recipes ->" lines log %s, stdout %s; any '
                 '"PipelinePrecache:" line %s' % (pc.get('log'), pc.get('stdout'), pc.get('any')))""",
 """        o.append('  precache form (item 254 (e)): "PipelinePrecache: N recipes ->" lines log %s; executor member [I] (item '
                 '258 (d), not in the verdict): the same line in the emulator stdout %s, any "PipelinePrecache:" line %s' % (
                     pc.get('log'), pc.get('stdout'), pc.get('any')))"""),
("""'STOP RULE CONTROL before %s: %s; letter %s (%s); executor reading (the gate) %s (%s)'""",
 """'STOP RULE CONTROL before %s: %s; letter %s (%s); executor reading [I] (the gate) %s (%s)'"""),
("""        out.append('CONTROL W %s (%s, item 254 (k)(4)): %s; letter (death marker or [Vulkan][E]) %s (%s); executor '
                   'reading (any W row or admission row failing; the gate) %s (%s)' % (""",
 """        out.append('CONTROL W %s (%s, item 254 (k)(4)): %s; letter (death marker or [Vulkan][E]) %s (%s); executor '
                   'reading [I] (any W row or admission row failing; the gate) %s (%s)' % ("""),
("""        out.append('W FORM (item 254 (e)): V with the "PipelinePrecache: N recipes ->" line and no KYTY_PIPELINE_PRECACHE '
                   '%d of %d made; W with KYTY_PIPELINE_PRECACHE=0 and no such line %d of %d made; violated: %s' % (
                       len(vm) - len(vbad), len(vm), len(wm) - len(wbad), len(wm), ','.join(vbad + wbad) or 'none'))""",
 """        wstd = [t for t in wm if (ents[t].get('precache') or {}).get('stdout')]
        out.append('W FORM (item 254 (e)): V with the "PipelinePrecache: N recipes ->" line and no KYTY_PIPELINE_PRECACHE '
                   '%d of %d made; W with KYTY_PIPELINE_PRECACHE=0 and no such line in the log %d of %d made; violated: %s; '
                   'executor member [I] (item 258 (d), not in the verdict; a hit is a question to the lead): W with the line '
                   'in the emulator stdout: %s' % (len(vm) - len(vbad), len(vm), len(wm) - len(wbad), len(wm),
                                                    ','.join(vbad + wbad) or 'none', ','.join(wstd) or 'none'))"""),
]
for a, b in R:
    assert t.count(a) == 1, a[:80]
    t = t.replace(a, b)
open(p, 'wb').write(t.encode('ascii'))

p = 'C:/kyty/s144/step0/partD.py.txt'
t = open(p, 'rb').read().decode('ascii')
R = [
("""        ('W with the precache line in its emulator stdout only', dict(std=[PRE])),
""", ''),
("""e = S.entry_of('w144_09', mk144(BASE / 'D7s',""",
 """e = S.entry_of('w144_09', mk144(BASE / 'D7o', 'w144_09', std=[PRE]), SH4)
ok &= case('D7c the precache line in the emulator stdout of a W only: an executor member [I] (item 258 (d)) - printed, the tag '
           'stays admitted', adm_ok(e) and e['precache']['stdout'] == 1 and any(
               'executor member [I] (item 258 (d), not in the verdict): the same line in the emulator stdout 1,' in x
               for x in S.fmt_entry(e)))
e = S.entry_of('w144_09', mk144(BASE / 'D7s',"""),
("""any(x.startswith('  precache form (item 254 (e)): "PipelinePrecache: N recipes ->" lines log 0, stdout 0') for x in fw)""",
 """any(x.startswith('  precache form (item 254 (e)): "PipelinePrecache: N recipes ->" lines log 0; executor member [I]')
               for x in fw)"""),
("""'W with KYTY_PIPELINE_PRECACHE=0 and no such line 10 of 10 made; violated: none' in o29 and""",
 """'W with KYTY_PIPELINE_PRECACHE=0 and no such line in the log 10 of 10 made; violated: none; executor member [I] (item 258 '
           '(d), not in the verdict; a hit is a question to the lead): W with the line in the emulator stdout: none' in o29 and"""),
("""x.endswith('violated: w144_09') for x in o29f)""", """'violated: w144_09;' in x for x in o29f)"""),
]
for a, b in R:
    assert t.count(a) == 1, a[:80]
    t = t.replace(a, b)
t = t.replace('executor reading (the gate)', 'executor reading [I] (the gate)')
t = t.replace("executor reading (any W row or admission row failing; the gate)",
              "executor reading [I] (any W row or admission row failing; the gate)")
open(p, 'wb').write(t.encode('ascii'))
p = 'C:/kyty/s144/step0/partD2.py.txt'
t = open(p, 'rb').read().decode('ascii')
a = "x.endswith('violated: v144_10,w144_09') for x in o29g)"
assert t.count(a) == 1
t = t.replace(a, "'violated: v144_10,w144_09;' in x for x in o29g)")
t = t.replace('executor reading (the gate)', 'executor reading [I] (the gate)')
open(p, 'wb').write(t.encode('ascii'))
print('ok')
