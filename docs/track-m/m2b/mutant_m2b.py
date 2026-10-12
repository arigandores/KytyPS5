"""Track M, M2b (HPP-839, ROADMAP s122 item 756(v)(2)(ii)): mutants of the HLE themes - a rollback of the fix taken at =1
in the worktree C:/kyty/m657/m2/wt (patched): build m_wave1_hle_stand, keep bin/mut_<name>.exe, restore the files byte for
byte (sha256 checked); then the arm of the theme runs at KYTY_M_<theme>=1 through run_stand_m2b.check - the mutant is
caught when the =1 members FAIL.
  <theme>_full : the whole =1 path is rolled back (the knob is still read and printed as 1).
  <theme>_part : one half of the port is rolled back (T265: the counter does not advance - every path gets ID 1;
                 T272: the weapon latch is dropped; T231: the em scale stays, the raster keeps the 128-pixel buffer -
                 f96a14a0 without 58978d15, the glyphs cut into bands).
Usage: python mutant_m2b.py <name>|all   (build and run). Lock and STOP checked before every process."""
import hashlib
import os
import subprocess
import sys

sys.path.insert(0, 'C:/kyty/m657/m2b')
import run_stand_m2b as stand  # noqa: E402

WT = 'C:/kyty/m657/m2/wt/'
HERE = 'C:/kyty/m657/m2b'
BUILD_CMD = 'C:\\kyty\\m657\\m2\\build_m2.cmd'
EXE = 'C:/kyty/m657/m2/build/m_wave1_hle_stand.exe'
MUTANTS = {
    't265_full': ('t265', [
        ('src/libs/libAmpr.cpp',
         '\tconst bool        m265 = MT265On(); // Track M, M2b (T265)\n',
         '\tconst bool        m265 = MT265On() && false; // Track M, M2b (T265)\n')]),
    't265_part': ('t265', [
        ('src/libs/libAmpr.cpp',
         '\t\t\t\t\tinfo.file_id = it->second.file_id = g_m265_next_file_id++;\n',
         '\t\t\t\t\tinfo.file_id = it->second.file_id = g_m265_next_file_id;\n')]),
    't272_full': ('t272', [
        ('src/libs/libPad.cpp',
         '\tif (Controller::MT272On()) {\n',
         '\tif (Controller::MT272On() && false) {\n')]),
    't272_part': ('t272', [
        ('src/libs/controller.cpp',
         '\t\t\treturn previous == M272_TRIGGER_STATE_WEAPON_FIRED || value >= std::min(command.data[1] * 32, 254)\n',
         '\t\t\treturn value >= std::min(command.data[1] * 32, 254)\n')]),
    't231_full': ('t231', [
        ('src/libs/libFont.cpp',
         '\tif (MT231On()) {\n\t\t// Track M, M2b (T231, upstream f96a14a0; KYTY_M_T231): metrics in the em scale',
         '\tif (MT231On() && false) {\n\t\t// Track M, M2b (T231, upstream f96a14a0; KYTY_M_T231): metrics in the em scale'),
        ('src/libs/libFont.cpp',
         '\tif (MT231On() && image_m231 != nullptr) {\n',
         '\tif (MT231On() && image_m231 != nullptr && false) {\n'),
        ('src/libs/libFont.cpp',
         '\t\tconst float scale    = MT231On() ? stbtt_ScaleForMappingEmToPixels(&font->font_info, font->scale_h)\n',
         '\t\tconst float scale    = false ? stbtt_ScaleForMappingEmToPixels(&font->font_info, font->scale_h)\n')]),
    't231_part': ('t231', [
        ('src/libs/libFont.cpp',
         '\t\tconst auto width  = static_cast<uint32_t>(std::clamp(x1 - x0, 0, FONT_GLYPH_MAX_DIM_M231));\n'
         '\t\tconst auto height = static_cast<uint32_t>(std::clamp(y1 - y0, 0, FONT_GLYPH_MAX_DIM_M231));\n',
         '\t\tconst auto width  = static_cast<uint32_t>(std::clamp(x1 - x0, 0, FONT_BITMAP_MAX_DIM));\n'
         '\t\tconst auto height = static_cast<uint32_t>(std::clamp(y1 - y0, 0, FONT_BITMAP_MAX_DIM));\n')]),
}


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def apply(edits):
    saved = {}
    for rel, old, new in edits:
        full = WT + rel
        if full not in saved:
            saved[full] = (open(full, 'rb').read(), sha(full))
    texts = {}
    for rel, old, new in edits:
        full = WT + rel
        t = texts.get(full, saved[full][0].decode('utf-8'))
        crlf = '\r\n' in t
        t = t.replace('\r\n', '\n')
        if t.count(old) != 1:
            raise SystemExit('mutant anchor count %d in %s' % (t.count(old), rel))
        t = t.replace(old, new)
        texts[full] = t.replace('\n', '\r\n') if crlf else t
    for full, t in texts.items():
        open(full, 'wb').write(t.encode('utf-8'))
    return saved


def restore(saved):
    for full, (raw, h) in saved.items():
        open(full, 'wb').write(raw)
        if sha(full) != h:
            raise SystemExit('restore sha mismatch ' + full)


def one(name):
    arm, edits = MUTANTS[name]
    stand.guard()
    saved = apply(edits)
    try:
        log = '%s/mut/build_%s.log' % (HERE, name)
        with open(log, 'wb') as f:
            rc = subprocess.run(['cmd', '/c', BUILD_CMD, 'target', 'm_wave1_hle_stand'], stdout=f,
                                stderr=subprocess.STDOUT).returncode
    finally:
        restore(saved)
    if rc != 0:
        print('%s: BUILD FAILED rc=%d' % (name, rc))
        return False
    exe = '%s/bin/mut_%s.exe' % (HERE, name)
    open(exe, 'wb').write(open(EXE, 'rb').read())
    out_dir = '%s/mut/%s' % (HERE, name)
    os.makedirs(out_dir, exist_ok=True)
    rc1, text = stand.run(exe, arm, 1, out_dir)
    fails = stand.check(arm, 1, rc1, text)
    caught = bool(fails)
    print('%s: %s (exe sha256 %s) %s' % (name, 'CAUGHT' if caught else 'NOT CAUGHT', sha(exe)[:16],
                                        '; '.join(fails)))
    return caught


def main():
    os.makedirs(HERE + '/mut', exist_ok=True)
    names = list(MUTANTS) if sys.argv[1] == 'all' else [sys.argv[1]]
    caught = [one(n) for n in names]
    print('ALL OK' if all(caught) else 'FAIL (mutant not caught)')
    sys.exit(0 if all(caught) else 1)


if __name__ == '__main__':
    main()
