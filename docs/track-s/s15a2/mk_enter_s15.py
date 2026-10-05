"""mk_enter_s15.py - track S, link S15a (HPP-601; ROADMAP "SESSION 122" item 511 (z)(4)-(5)): writes s15/enter_scene_s15.py from
s9/enter_scene_s9.py (seal 07, pinned by sha256) by exact replacements - every anchor must occur exactly once.  The one addition:
the hold of a U arm by the rule of item 511 (z)(4)-(5) (--hold-u MIN_S:FRAMES:CAP_S); S15a2 (HPP-615, item 528 (b)(1)): both
calls of UHold.poll() of the hold in try/except Exception (cause 'error <type name>', u_error).  Refuses when the lock exists.
LF, ASCII.
    python mk_enter_s15.py [<out>]
"""
import hashlib
import os
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
SRC = 'C:/kyty/s288/s9/enter_scene_s9.py'
SRC_SHA = '246b579b8022f6fe636d04abcbdbb095d9ac010c7cb42c27384ee4a62a09d591'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'C:/kyty/s288/s15/enter_scene_s15.py'
NL = chr(10)

HEAD_OLD = '"""enter_scene_s9.py - track S, link S9 (HPP-431;'
HEAD_NEW = ('"""enter_scene_s15.py - track S, link S15a (HPP-601; ROADMAP "SESSION 122" item 511 (z)(4)-(5)): s9/enter_scene_s9.py '
            '(seal 07, sha256 ' + SRC_SHA + ') with ONE addition, the hold of a U arm by the rule of item 511 (z)(4): --hold-u '
            'MIN_S:FRAMES:CAP_S - after "stable" the arm is held while the presented time after the first scene frame (the sum of '
            'dt_us of the FrameTrace rows after it - the rows the scorer counts) is < MIN_S or the video holds < FRAMES frames (the '
            'complete lines of rec_<tag>.mp4.idx, which the emulator flushes per recorded frame), but not longer than CAP_S of '
            'presented time after the first scene frame; item 511 (z)(5): when the entry line of the level has no first scene frame '
            '(no row with draws >= 100 at or after the entry line and before the next start line), the anchor is the entry line '
            '(every FrameTrace row after it).  The first scene frame is found as sc_s.locate finds it.  A wall cap of CAP_S + '
            'U_WALL_EXTRA_S seconds from the start of the hold ends a hold whose game stops presenting (executor\'s variant).  The '
            'attempt records hold_end; <tag>.json records hold_rule.  Without --hold-u nothing differs from enter_scene_s9.py.  S15a2 '
            '(HPP-615, item 528 (b)(1)): an exception of UHold.poll() gives the cause \'error <type name>\', UHold is not polled '
            'again, the hold ends at once and the usual path closes the game.  Made by s15/mk_enter_s15.py."""' + NL + '# The header of the inherited file: enter_scene_s9.py - track S, link S9 (HPP-431;')

UHOLD_ANCHOR = 'def sample_host():'
UHOLD = r'''SCENE_DRAWS_U = 100      # S15a, item 511 (z)(4): = sc142.SCENE_DRAWS = sc_s.SCENE_DRAWS (the first scene frame of sc_s.locate)
U_WALL_EXTRA_S = 60      # S15a: executor's variant - the wall cap of a U hold is CAP_S + 60 s (a game that stops presenting)
M_START_U = b'GuestOut: Level has started:'


def ft_field(line, name):
    """The integer field ' <name>=<digits>' of a log line (the parse of sc_s.field); None when absent."""
    key = b' ' + name + b'='
    i = line.find(key)
    if i < 0:
        return None
    j = i + len(key)
    k = j
    while k < len(line) and 48 <= line[k] <= 57:
        k += 1
    return int(line[j:k]) if k > j else None


def parse_hold_u(text):
    """--hold-u MIN_S:FRAMES:CAP_S -> (min_us, frames, cap_us); SystemExit on another form or MIN_S > CAP_S."""
    parts = (text or '').split(':')
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        raise SystemExit('--hold-u wants MIN_S:FRAMES:CAP_S, got %r' % text)
    mn, fr, cap = (int(p) for p in parts)
    if mn > cap or cap <= 0:
        raise SystemExit('--hold-u: MIN_S %d > CAP_S %d or CAP_S 0' % (mn, cap))
    return mn * 1000000, fr, cap * 1000000


class UHold:
    """Item 511 (z)(4)-(5), live: the state of a U hold from the log (its own Tail from the beginning) and the video index.

    Rows are the lines beginning "FrameTrace: n=" with an n and a dt_us (the rows of sc_s.scan_s; a torn line is skipped).  eg =
    the number of rows before the FIRST line "GuestOut: Level has started: <level>" (exact name); closed = a later start line of
    any name has been seen (sc_s.locate ends the search of the first scene frame at the next start line); fi = the index of the
    first row with draws >= SCENE_DRAWS_U at or after eg while not closed.  shown = the sum of dt_us of the rows after fi (anchor
    'fi'), or with no fi the sum of dt_us of the rows at or after eg (anchor 'entry', item 511 (z)(5)); no entry line - no anchor.
    done(): 'cap' when shown >= cap_us; 'met' when shown >= min_us and the video holds >= frames frames; None otherwise."""

    def __init__(self, log_path, idx_path, level, rule):
        self.log = Tail(log_path)
        self.idx = Tail(idx_path) if idx_path is not None else None
        self.level = level
        self.min_us, self.frames, self.cap_us = rule
        self.rows = 0
        self.eg = None
        self.closed = False
        self.fi = None
        self.after_entry_us = 0
        self.after_fi_us = 0
        self.video = 0

    def feed(self, line):
        if line.startswith(b'FrameTrace: n='):
            j = line.find(b' ', 14)
            n = int(line[14:j]) if j > 14 else None
            dt = ft_field(line, b'dt_us')
            if n is None or dt is None:
                return
            d = ft_field(line, b'draws')
            i = self.rows
            self.rows += 1
            if self.eg is None:
                return
            self.after_entry_us += dt
            if self.fi is not None:
                self.after_fi_us += dt
            elif not self.closed and (d if d is not None else -1) >= SCENE_DRAWS_U:
                self.fi = i
            return
        if line.startswith(M_START_U):
            name = line[len(M_START_U):].strip().decode('latin1')
            if self.eg is None:
                if name == self.level:
                    self.eg = self.rows
            else:
                self.closed = True

    def anchor(self):
        return 'fi' if self.fi is not None else ('entry' if self.eg is not None else None)

    def shown(self):
        a = self.anchor()
        return self.after_fi_us if a == 'fi' else (self.after_entry_us if a == 'entry' else 0)

    def done(self):
        if self.anchor() is None:
            return None
        if self.shown() >= self.cap_us:
            return 'cap'
        if self.shown() >= self.min_us and self.video >= self.frames:
            return 'met'
        return None

    def poll(self):
        for line in self.log.lines():
            self.feed(line)
        if self.idx is not None:
            self.video += len(self.idx.lines())
        return self.done()

    def report(self, cause):
        return dict(cause=cause, anchor=self.anchor(), shown_us=self.shown(), video_frames=self.video, rows=self.rows,
                    entry_rows=self.eg, first_row=self.fi, closed=self.closed)


def u_error(error):
    """S15a2, item 528 (b)(1): the cause of a U hold whose UHold.poll() raised - 'error <type name>' (printed with its text)."""
    print('U hold: UHold.poll() raised %s: %s - no further poll, the hold ends now (item 528 (b)(1))' % (
        type(error).__name__, str(error).encode('ascii', 'replace').decode('ascii')), flush=True)
    return 'error %s' % type(error).__name__


'''

HOLD_OLD = '''                deadline = hold_t0 + options.hold
                ft = FtCounter(EMU / '_kyty.txt')
                ft.sample()
                while time.monotonic() < deadline and game.poll() is None:
                    time.sleep(FT_SAMPLE_S)
                    ft.sample()
                ft.sample()   # the moment the hold ended (session 123, item 30(v))'''
HOLD_NEW = '''                deadline = hold_t0 + options.hold
                ft = FtCounter(EMU / '_kyty.txt')
                ft.sample()
                uh = None
                ucause = None
                if options.hold_u:
                    # S15a, item 511 (z)(4)-(5): the U hold - the rule, a wall cap of CAP_S + U_WALL_EXTRA_S
                    rule = parse_hold_u(options.hold_u)
                    uh = UHold(EMU / '_kyty.txt', (ROOT / ('rec_%s.mp4.idx' % tag)) if options.rec else None,
                               options.level, rule)
                    deadline = hold_t0 + rule[2] / 1000000.0 + U_WALL_EXTRA_S
                    print('U hold (item 511 (z)(4)): presented >= %d s after the first scene frame (or the entry line) and '
                          'video >= %d frames, cap %d s presented; wall cap %d s' % (
                              rule[0] // 1000000, rule[1], rule[2] // 1000000, rule[2] // 1000000 + U_WALL_EXTRA_S), flush=True)
                while time.monotonic() < deadline and game.poll() is None:
                    time.sleep(FT_SAMPLE_S)
                    ft.sample()
                    if uh is not None:
                        try:
                            ucause = uh.poll()
                        except Exception as error:   # S15a2, item 528 (b)(1): no further poll, the hold ends now
                            ucause = u_error(error)
                        if ucause is not None:
                            break
                if uh is not None:
                    if ucause is None:
                        try:
                            ucause = uh.poll() or ('game ended' if game.poll() is not None else 'wall cap')
                        except Exception as error:   # S15a2, item 528 (b)(1): the poll after the loop
                            ucause = u_error(error)
                    result['hold_end'] = uh.report(ucause)
                    print('U hold end: %s' % json.dumps(result['hold_end'], sort_keys=True), flush=True)
                ft.sample()   # the moment the hold ended (session 123, item 30(v))'''

ARG_OLD = "    parser.add_argument('--hold', type=int, default=0)\n"
ARG_NEW = ("    parser.add_argument('--hold', type=int, default=0)\n"
           "    parser.add_argument('--hold-u', default=None,\n"
           "                        help='S15a, item 511 (z)(4): MIN_S:FRAMES:CAP_S - the U hold (needs --hold > 0)')\n")
PARSE_OLD = "    if options.root:\n        globals()['ROOT'] = pathlib.Path(options.root)\n"
PARSE_NEW = ("    if options.root:\n        globals()['ROOT'] = pathlib.Path(options.root)\n"
             "    hold_rule = None\n"
             "    if options.hold_u:\n"
             "        mn, fr, cap = parse_hold_u(options.hold_u)\n"
             "        if options.hold <= 0:\n"
             "            raise SystemExit('--hold-u needs --hold > 0')\n"
             "        hold_rule = dict(min_shown_s=mn // 1000000, video_frames=fr, cap_s=cap // 1000000,\n"
             "                         wall_extra_s=U_WALL_EXTRA_S, scene_draws=SCENE_DRAWS_U)\n")
JSON_OLD = "            guest_args=guest_args, hold_s=options.hold,\n"
JSON_NEW = "            guest_args=guest_args, hold_s=options.hold, hold_rule=hold_rule,\n"
ROOT_OLD = "ROOT = pathlib.Path('C:/kyty/s288/s4')\n"
ROOT_NEW = "ROOT = pathlib.Path('C:/kyty/s288/s15')\n"


def main():
    if os.path.exists(LOCK):
        print('LOCKED - nothing written')
        return 5
    raw = open(SRC, 'rb').read()
    got = hashlib.sha256(raw).hexdigest()
    if got != SRC_SHA:
        print('STOP: %s sha256 %s != %s' % (SRC, got, SRC_SHA))
        return 1
    t = raw.decode('ascii').replace(chr(13) + NL, NL)
    for old, new in ((HEAD_OLD, HEAD_NEW), (UHOLD_ANCHOR, UHOLD + UHOLD_ANCHOR), (HOLD_OLD, HOLD_NEW), (ARG_OLD, ARG_NEW),
                     (PARSE_OLD, PARSE_NEW), (JSON_OLD, JSON_NEW), (ROOT_OLD, ROOT_NEW)):
        if t.count(old) != 1:
            print('STOP: anchor found %d times: %r' % (t.count(old), old[:80]))
            return 1
        t = t.replace(old, new)
    t.encode('ascii')
    with open(OUT, 'wb') as f:
        f.write(t.encode('ascii'))
    print('WROTE %s sha256 %s lines %d (from %s %s)' % (OUT, hashlib.sha256(t.encode('ascii')).hexdigest(), t.count(NL), SRC,
                                                        SRC_SHA[:16]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
