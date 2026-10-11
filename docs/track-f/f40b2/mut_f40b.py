#!/usr/bin/env python3
# F40b (HPP-771, Red Team): mutants m1, m2, m4, m5, m6 of KYTY_FIX_F24 (ROADMAP s122 item 692(g)(3)).
# Whole-line anchors, each must occur exactly once; CRLF-aware (strips \r, writes back the file's own EOL), LF by
# write_bytes. Usage:
#   python mut_f40b.py check <rev>            - apply every mutant in memory to `git show <rev>:<file>` (repo C:/kyty/KytyPS5)
#   python mut_f40b.py apply <m> <worktree>   - patch the worktree files for mutant <m> (m1|m2|m4|m5|m6)
# m3 (main wait without a bound) is a code-review member by the letter of item 692(g)(3) - no binary.
import subprocess
import sys

JP = 'src/graphics/presentation/window/joyPump.cpp'
WN = 'src/graphics/presentation/window/window.cpp'

M1_DEF = r'''// MUTANT m1 (F40b, ROADMAP s122 item 692(g)(3)): the FS12 open by the add event index, run as a JoyPump task.
void Pump::MutantOpenM1(int index) {
	SDL_LockJoysticks();
	auto* pad = SDL_GameControllerOpen(index);
	if (pad == nullptr) {
		if (m_stand_window.load(std::memory_order_relaxed)) {
			m_stand_open_failed.fetch_add(1, std::memory_order_relaxed);
		}
		if (LineAllowed(m_open_failed_lines)) {
			LOGF("FixF24: open failed index=%d error=\"%s\"\n", index, SDL_GetError());
		}
		SDL_UnlockJoysticks();
		return;
	}
	m_open_pads.fetch_add(1, std::memory_order_relaxed);
	SDL_UnlockJoysticks();
	OpenOne(pad);
}

'''.split('\n')[:-1]

# (file, anchor line, op, lines); op: 'replace' - the anchor line is replaced, 'after' - lines go after it,
# 'before' - lines go before it.
MUTANTS = {
    'm1': [
        (JP, '\tvoid              Close(int instance_id);', 'after',
         ['\tvoid              MutantOpenM1(int index); // MUTANT m1 (F40b)']),
        (JP, 'void Pump::ScanAndOpen() {', 'after',
         ['\tstatic volatile bool mutant_m1 = true; // MUTANT m1 (F40b): no open by instance id after the update',
          '\tif (mutant_m1) {',
          '\t\treturn;',
          '\t}']),
        (JP, 'void Pump::Stop() {', 'before', M1_DEF),
        (JP, 'void NoteAddEvent(int index) {', 'after',
         ['\tP().Post([index] { P().MutantOpenM1(index); }); // MUTANT m1 (F40b): open by the event index, JoyPump task']),
    ],
    'm2': [
        (JP, '\t[[nodiscard]] bool Stopping() const { return m_stop.load(std::memory_order_acquire); }', 'replace',
         ['\t[[nodiscard]] bool Stopping() const { return false; } // MUTANT m2 (F40b): the stop flag is never read']),
    ],
    'm4': [
        (WN, '\t\t\tJoyPump::PostClose(f.id); // Track F, F40a: the close is a JoyPump task (s0.4)', 'replace',
         ['\t\t\tSDL_GameControllerClose(SDL_GameControllerFromInstanceID(f.id)); // MUTANT m4 (F40b): close on the main thread']),
    ],
    'm5': [
        (WN, '\t\tSDL_SetHint(SDL_HINT_AUTO_UPDATE_JOYSTICKS, "0");', 'replace',
         ['\t\t// MUTANT m5 (F40b): SDL_HINT_AUTO_UPDATE_JOYSTICKS is not set']),
    ],
    'm6': [
        (WN, '\t\tif (SDL_InitSubSystem(SDL_INIT_VIDEO) < 0) {', 'replace',
         ['\t\tif (SDL_InitSubSystem(SDL_INIT_VIDEO | SDL_INIT_GAMECONTROLLER) < 0) { // MUTANT m6 (F40b): joystick init on main']),
        (JP, '\tconst bool ok = SDL_InitSubSystem(SDL_INIT_GAMECONTROLLER) == 0;', 'replace',
         ['\tconst bool ok = true; // MUTANT m6 (F40b): the joystick init ran on the main thread']),
    ],
}


def patch_text(text, edits, path):
    crlf = '\r\n' in text
    lines = text.replace('\r\n', '\n').split('\n')
    for (f, anchor, op, new) in edits:
        if f != path:
            continue
        idx = [i for i, l in enumerate(lines) if l == anchor]
        if len(idx) != 1:
            raise SystemExit('ANCHOR %s x%d in %s: %r' % (op, len(idx), path, anchor))
        i = idx[0]
        if op == 'replace':
            lines[i:i + 1] = new
        elif op == 'after':
            lines[i + 1:i + 1] = new
        elif op == 'before':
            lines[i:i] = new
        else:
            raise SystemExit('bad op ' + op)
    out = '\n'.join(lines)
    return out.replace('\n', '\r\n') if crlf else out


def files_of(m):
    return sorted({e[0] for e in MUTANTS[m]})


def main():
    if len(sys.argv) >= 3 and sys.argv[1] == 'check':
        rev = sys.argv[2]
        ok = True
        for m in sorted(MUTANTS):
            for f in files_of(m):
                src = subprocess.run(['git', '-C', 'C:/kyty/KytyPS5', 'show', '%s:%s' % (rev, f)], capture_output=True,
                                     check=True).stdout.decode('utf-8')
                out = patch_text(src, MUTANTS[m], f)
                added = len(out.split('\n')) - len(src.split('\n'))
                mark = out.count('MUTANT %s' % m)
                print('%s %s +%d lines, marks %d' % (m, f, added, mark))
                ok &= mark >= 1
        print('ALL OK' if ok else 'FAIL')
        sys.exit(0 if ok else 1)
    if len(sys.argv) == 4 and sys.argv[1] == 'apply':
        m, wt = sys.argv[2], sys.argv[3]
        for f in files_of(m):
            p = wt + '/' + f
            src = open(p, 'rb').read().decode('utf-8')
            out = patch_text(src, MUTANTS[m], f)
            open(p, 'wb').write(out.encode('utf-8'))
            print('patched', m, f)
        sys.exit(0)
    print(__doc__ if __doc__ else 'usage: check <rev> | apply <m> <worktree>')
    sys.exit(2)


if __name__ == '__main__':
    main()
