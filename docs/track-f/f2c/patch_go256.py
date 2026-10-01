# F2c (HPP-310): fill go_f2c.sh by ROADMAP p.256 - (b) binary 5821482a, (v) GLRESTORE=1 and stop of track F on a failed return,
# (e) the HPP-332 lock window in the same command as the lock.  LF in, LF out.
import pathlib
p = pathlib.Path('C:/kyty/f287/f2c/go_f2c.sh')
s = p.read_bytes().decode('ascii')
assert '\r' not in s
R = [
    ('BIN_F2C=""\nBIN_EXPECT=""\nGLRESTORE=""\n',
     'BIN_F2C="/c/kyty/f287/bin/kyty_emulator_5821482a.exe"\n'
     'BIN_EXPECT="5821482a13a38bb9e42719b75fbd7b6e308a08c8e98caab02afb5398aac368dd"\n'
     'GLRESTORE="1"\n'),
    ('#   BINARY: BIN_F2C / BIN_EXPECT - the binary of the lead\'s decision on F2b RC2 (item 237 (g)(3)); empty -> rc 2.\n',
     '#   BINARY: BIN_F2C / BIN_EXPECT - the binary of the lead\'s decision on F2b RC2 (item 237 (g)(3)); empty -> rc 2.\n'
     '#     Item 256 (b): 5821482a (= 4fc501f4 + 22 knob commits + F2a); item 256 (v): GLRESTORE=1.\n'
     '#   FAILED RETURN (item 256 (v)): a shader cache or GLCache return that does not equal the list before writes the stop\n'
     '#     file C:/kyty/f287/STOP (track F stops; the comment in HPP-330 goes before HPP-332 starts).\n'
     '#   LOCK WINDOW (item 256 (e)): right before the lock, in the same command - no lock file, no stop file, and HPP-332\n'
     '#     neither in_progress nor done by the API answer (win332_f2c.py, a times line with the answer); else BUSY rc 4.\n'),
    ('if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi\nset -o noclobber\n',
     'if [ -e $STOPF ]; then busy "stop file $STOPF appeared before the lock"; fi\n'
     'W332=$(python $ROOT/win332_f2c.py 2>&1 | tail -1 | tr -d \'\\r\')\n'
     'W332RC=${PIPESTATUS[0]}\n'
     'tl "lock window p.256(e): $W332"\n'
     'case "$W332" in\n'
     '  *"-> open") ;;\n'
     '  *) busy "lock window p.256(e) closed or unknown: $W332";;\n'
     'esac\n'
     'lockheld\n'
     'set -o noclobber\n'),
    ('        tl "SHADER CACHE RESTORE FAILED: back \'$LIST_BACK\' != before \'$LIST_BEFORE\'"; echo "cache restore failed"; RCX=1\n',
     '        tl "SHADER CACHE RESTORE FAILED: back \'$LIST_BACK\' != before \'$LIST_BEFORE\'"; echo "cache restore failed"; RCX=1; RETFAIL=1\n'),
    ('      tl "SHADER CACHE RESTORE FAILED: move/copy error ($CACHE, $KEEP, $SNAP)"; echo "cache restore failed"; RCX=1\n',
     '      tl "SHADER CACHE RESTORE FAILED: move/copy error ($CACHE, $KEEP, $SNAP)"; echo "cache restore failed"; RCX=1; RETFAIL=1\n'),
    ('        if [ "$GLB" = "$GL_BEFORE" ]; then tl "GLCache returned: $GLB = before"; else tl "GLCACHE RESTORE FAILED: \'$GLB\' != \'$GL_BEFORE\'"; RCX=1; fi\n',
     '        if [ "$GLB" = "$GL_BEFORE" ]; then tl "GLCache returned: $GLB = before"; else tl "GLCACHE RESTORE FAILED: \'$GLB\' != \'$GL_BEFORE\'"; RCX=1; RETFAIL=1; fi\n'),
    ('        tl "GLCACHE RESTORE FAILED: move/copy error"; RCX=1\n',
     '        tl "GLCACHE RESTORE FAILED: move/copy error"; RCX=1; RETFAIL=1\n'),
    ('  FG=$(python $ROOT/fgcpu143.py --since',
     '  if [ "$RETFAIL" = "1" ]; then\n'
     '    echo "p.256(v) F2c cache return failed $(date -u +%Y-%m-%dT%H:%M:%SZ) - track F stopped, comment in HPP-330" > $STOPF\n'
     '    tl "stop file written: cache return failed (p.256(v))"\n'
     '  fi\n'
     '  FG=$(python $ROOT/fgcpu143.py --since'),
    ('INSTALLED=0\nSNAPPED=0\n', 'INSTALLED=0\nRETFAIL=0\nSNAPPED=0\n'),
    ('idle142; procload --wait-s 0; stop file?; lock (lock.log UTC)',
     'idle142; procload --wait-s 0; stop file?; HPP-332 window (win332_f2c, p.256(e)); lock (lock.log UTC)'),
    ('f2c_read.py f2c_b26.py shalist_f2c.py $PRED', 'f2c_read.py f2c_b26.py shalist_f2c.py win332_f2c.py $PRED'),
]
for a, b in R:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
p.write_bytes(s.encode('ascii'))
print('patched', len(R))
