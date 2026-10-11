"""Patch F42c harness: installed binary before the call may be FS13 abab2196 or FS14 013e1974 (item 710(g)(4): FS14d may install FS14
between the tags of the series); after the call = before, returned from the pinned copy of the one found.  LF, ASCII."""
import sys

G = 'C:/kyty/f287/f42c/'
FS13 = 'abab2196e3b66f0449376f736421d5ac5fd3f18f6d6c98b7ef38351c45a44b73'
FS14 = '013e1974ea8abfb41e9951c7939b3890257010f53bad4ff838d6fd70fde3d0cd'


def sub(path, pairs):
    b = open(G + path, 'rb').read().decode('ascii')
    for old, new in pairs:
        if b.count(old) != 1:
            print('ANCHOR FAIL', path, repr(old[:80]), b.count(old))
            sys.exit(1)
        b = b.replace(old, new)
    open(G + path, 'wb').write(b.encode('ascii'))
    print('patched', path)


NL = chr(10)
sub('go_f42c.sh', [
    ('INST=' + FS13 + NL,
     'INST13=' + FS13 + NL + 'INST14=' + FS14 + NL),
    ('PINNED=$F/bin/kyty_emulator_abab2196.exe' + NL,
     'PIN13=$F/bin/kyty_emulator_abab2196.exe' + NL + 'PIN14=$F/bin/kyty_emulator_013e1974.exe' + NL),
    ('[ "$(sha "$PINNED")" = "$INST" ] || { log "pinned FS13 copy $PINNED is not abab2196 - not starting"; exit 1; }' + NL
     + 'WANT=$(sha "$GAME")' + NL
     + '[ "$WANT" = "$INST" ] || { log "installed binary $WANT is not FS13 abab2196 - not starting (question to the lead)"; exit 1; }' + NL,
     'WANT=$(sha "$GAME")' + NL
     + '# installed before the call: FS13 abab2196 or FS14 013e1974 (item 710(g)(4) - FS14d may install FS14 between the tags); after = before' + NL
     + 'case "$WANT" in' + NL
     + '  "$INST13") INST=$INST13; PINNED=$PIN13; INAME=FS13;;' + NL
     + '  "$INST14") INST=$INST14; PINNED=$PIN14; INAME=FS14;;' + NL
     + '  *) log "installed binary $WANT is neither FS13 abab2196 nor FS14 013e1974 - not starting (question to the lead)"; exit 1;;' + NL
     + 'esac' + NL
     + '[ "$(sha "$PINNED")" = "$INST" ] || { log "pinned $INAME copy $PINNED is not ${INST:0:8} - not starting"; exit 1; }' + NL
     + 'log "installed before the call: $INAME ${INST:0:8} (pinned copy $PINNED)"' + NL),
    ('log "installed binary returned from the pinned FS13 copy"', 'log "installed binary returned from the pinned $INAME copy"'),
    ('log "INSTALLED BINARY IS NOT FS13 after the call"', 'log "INSTALLED BINARY IS NOT $INAME (= before) after the call"'),
])

sub('f42c_read.py', [
    ("BIN_INST = '" + FS13 + "'" + NL,
     "BIN_INST = '" + FS13 + "'" + NL + "BIN_INST14 = '" + FS14 + "'" + NL),
    ("        ('installed before = after = FS13 abab2196 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),"
     + NL + "         inst_b == BIN_INST and inst_a == BIN_INST),",
     "        ('installed before = after, FS13 abab2196 or FS14 013e1974 (%s / %s)' % ((inst_b or '-')[:16], (inst_a or '-')[:16]),"
     + NL + "         inst_b in (BIN_INST, BIN_INST14) and inst_a == inst_b),"),
])

sub('test_f42c_read.py', [
    ("FS13 = '" + FS13 + "'" + NL,
     "FS13 = '" + FS13 + "'" + NL + "FS14 = '" + FS14 + "'" + NL),
    ("    t = copy.deepcopy(S)" + NL + "    del t['side']['manifest_cmp']" + NL,
     "    t = copy.deepcopy(S)" + NL
     + "    t['side']['installed_before'] = FS14" + NL
     + "    t['side']['installed_after'] = FS14" + NL
     + "    ok &= check('%s admission installed FS14 before = after - admitted' % tg, read(t)['status'] == 'ADMITTED')" + NL
     + "    for b_, a_ in ((FS13, FS14), (FS14, FS13)):" + NL
     + "        t = copy.deepcopy(S)" + NL
     + "        t['side']['installed_before'] = b_" + NL
     + "        t['side']['installed_after'] = a_" + NL
     + "        ok &= check('%s admission installed %s -> %s' % (tg, b_[:8], a_[:8]), read(t)['status'] == 'NOT_ADMITTED')" + NL
     + "    t = copy.deepcopy(S)" + NL + "    del t['side']['manifest_cmp']" + NL),
])

sub('test_tools_f42c.py', [
    ("FS13 = '" + FS13 + "'" + NL,
     "FS13 = '" + FS13 + "'" + NL + "FS14 = '" + FS14 + "'" + NL),
    ("ok &= check('go: INST literal = FS13 abab2196', 'INST=' + FS13 in src)",
     "ok &= check('go: INST13 / INST14 literals = FS13 abab2196 / FS14 013e1974', 'INST13=' + FS13 in src and 'INST14=' + FS14 in src)"),
    ("'PINNED=$F/bin/kyty_emulator_abab2196.exe' in src)",
     "'PIN13=$F/bin/kyty_emulator_abab2196.exe' in src\n            and 'PIN14=$F/bin/kyty_emulator_013e1974.exe' in src)".replace('\\n', NL)),
    ("ok &= check('on disk: sha256 of the pinned FS13 copy = abab2196', sha('C:/kyty/f287/bin/kyty_emulator_abab2196.exe') == FS13)",
     "ok &= check('on disk: sha256 of the pinned FS13 copy = abab2196', sha('C:/kyty/f287/bin/kyty_emulator_abab2196.exe') == FS13)" + NL
     + "ok &= check('on disk: sha256 of the pinned FS14 copy = 013e1974', sha('C:/kyty/f287/bin/kyty_emulator_013e1974.exe') == FS14)"),
])
print('ALL PATCHED')
