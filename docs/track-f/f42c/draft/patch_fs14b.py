import sys
P = 'C:/kyty/f287/f42c/test_tools_f42c.py'
NL = chr(10)
b = open(P, 'rb').read().decode('ascii')
old = "ok &= check('go: installed before the call must be FS13', '[ \"$WANT\" = \"$INST\" ] ||' in src)"
new = ("ok &= check('go: installed before the call must be FS13 or FS14 (case on WANT, other -> exit 1)',"
       + NL + "            'case \"$WANT\" in' in src and '\"$INST13\") INST=$INST13; PINNED=$PIN13; INAME=FS13;;' in src"
       + NL + "            and '\"$INST14\") INST=$INST14; PINNED=$PIN14; INAME=FS14;;' in src"
       + NL + "            and 'nor FS14 013e1974 - not starting (question to the lead)\"; exit 1;;' in src"
       + NL + "            and src.index('case \"$WANT\" in') < src.index('[ \"$(sha \"$PINNED\")\" = \"$INST\" ] ||') < src.index('mkdir -p $OUT'))")
if b.count(old) != 1:
    print('ANCHOR FAIL', b.count(old)); sys.exit(1)
b = b.replace(old, new)
b = b.replace("ok &= check('go: installed_after must be FS13',", "ok &= check('go: installed_after must be = before (INST)',")
open(P, 'wb').write(b.encode('ascii'))
print('patched')
