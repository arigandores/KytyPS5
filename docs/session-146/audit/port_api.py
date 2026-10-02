D = 'C:/kyty/KytyPS5/docs/session-145/audit/'
src = open(D + 'api145.py', 'rb').read().decode('utf-8')
def rep(a, b, n=1):
    global src
    assert src.count(a) == n, (a, src.count(a))
    src = src.replace(a, b)
rep("# api145.py - Session Auditor, s145 step 3 (HPP-353): read-only API pass.", "# api146.py - Session Auditor, s146 step 3 (HPP-389): read-only API pass (a port of the auditor's own api145.py).")
rep("# (1) status / assignee / review stage / monitor of the s145 chain, of the F5 chain of the s144 close and of every other",
    "# (1) status / assignee / review stage / monitor of the s146 chain, of the track chains and of every other")
rep("#     issue HPP-283..HPP-390 that is not done or carries a monitor", "#     issue HPP-283..HPP-400 that is not done or carries a monitor")
rep("# (2) comments of every issue HPP-283..HPP-390 and of HPP-3 created inside the session lock windows of runs145/lock.log",
    "# (2) comments of every issue HPP-283..HPP-400 and of HPP-3 created inside the session lock windows of runs146/lock.log")
rep("# (3) activity of the issues named by ROADMAP item 306: writes of executionPolicy with the number of stages before / after.",
    "# (3) activity of the chain and track issues: writes of executionPolicy with the number of stages before / after (trap 12).")
rep("for ln in open('C:/kyty/s145/runs145/lock.log', encoding='utf-8').read().splitlines():", "for ln in open('C:/kyty/s146/runs146/lock.log', encoding='utf-8').read().splitlines():")
rep("SER = (W[0][1], W[-1][2])", "SER = (W[1][1], W[-1][2])")
rep("CHAIN = {350: 's145 0', 351: 's145 1', 379: 's145 1b', 352: 's145 2', 353: 's145 3', 354: 's145 4', 355: 'F5a', 356: 'F5b', 357: 'F5c', 358: 'F5d',\n         366: 'F5a2', 367: 'F5b2'}",
    "CHAIN = {354: 's145 4', 386: 's146 0', 387: 's146 1', 395: 's146 1b', 388: 's146 2', 389: 's146 3', 390: 's146 4', 391: 'P19', 392: 'P20', 393: 'P21', 394: 'P22',\n"
    "         375: 'F6c', 376: 'F6d', 377: 'F6e', 378: 'F6f', 381: 'FS2a', 382: 'FS2b', 383: 'FS2c', 384: 'FS2d', 364: 'P17', 365: 'P18'}")
rep("for n in [3] + list(range(283, 391)):", "for n in [3] + list(range(283, 401)):")
rep("print('ISSUES read %d (HPP-3, HPP-283..HPP-390)' % len(issues))", "print('ISSUES read %d (HPP-3, HPP-283..HPP-400)' % len(issues))")
rep("    if not lead and not st and n >= 350:", "    if not lead and not st and n >= 386:")
rep("print('ISSUES HPP-350.. of an executor", "print('ISSUES HPP-386.. of an executor")
rep("created inside a session lock window of sc145", "created inside a session lock window of s146 (warm-up and series)")
rep("for n in (352, 377, 353, 380, 364, 381, 382, 383, 315, 318, 319):", "for n in (386, 387, 395, 388, 389, 377, 391, 392, 393, 383, 364, 365, 315):")
assert '145' not in src.replace('api145.py', '').replace("'s145 4'", ''), [l for l in src.split(chr(10)) if '145' in l]
open('C:/kyty/s146/step3/api146.py', 'wb').write(src.encode('utf-8'))
print('written')
