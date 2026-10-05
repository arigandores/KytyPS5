"""patch_mk_s15a2.py - track S, link S15a2 (HPP-615; ROADMAP "SESSION 122" item 528 (b)(1)): patches s15/mk_enter_s15.py so the
generated s15/enter_scene_s15.py wraps both calls of UHold.poll() of the hold in try/except Exception - an exception gives the cause
'error <type name>', UHold is not polled again, the hold ends at once and the usual path follows (hold_end, ft_*, hold_exit,
close_game).  Exact replacements, every anchor exactly once; refuses when the lock exists; LF, ASCII.
    python patch_mk_s15a2.py
"""
import hashlib
import os
import sys

LOCK = 'C:/kyty/SEALED_RUN.lock'
MK = 'C:/kyty/s288/s15/mk_enter_s15.py'
MK_SHA = '72f0ea1ad9562f194964a1a20144c7847ee109dc46625c927d06104cfec9ed73'
NL = chr(10)

R = [
    # 1. the header of the generated file names the change of S15a2
    ("'attempt records hold_end; <tag>.json records hold_rule.  Without --hold-u nothing differs from enter_scene_s9.py.  Made '\n"
     "            'by s15/mk_enter_s15.py.\"\"\"'",
     "'attempt records hold_end; <tag>.json records hold_rule.  Without --hold-u nothing differs from enter_scene_s9.py.  S15a2 '\n"
     "            '(HPP-615, item 528 (b)(1)): an exception of UHold.poll() gives the cause \\'error <type name>\\', UHold is not polled '\n"
     "            'again, the hold ends at once and the usual path closes the game.  Made by s15/mk_enter_s15.py.\"\"\"'"),
    # 2. the helper that names the cause, placed after UHold
    ("    def report(self, cause):\n"
     "        return dict(cause=cause, anchor=self.anchor(), shown_us=self.shown(), video_frames=self.video, rows=self.rows,\n"
     "                    entry_rows=self.eg, first_row=self.fi, closed=self.closed)\n\n\n'''",
     "    def report(self, cause):\n"
     "        return dict(cause=cause, anchor=self.anchor(), shown_us=self.shown(), video_frames=self.video, rows=self.rows,\n"
     "                    entry_rows=self.eg, first_row=self.fi, closed=self.closed)\n\n\n"
     "def u_error(error):\n"
     "    \"\"\"S15a2, item 528 (b)(1): the cause of a U hold whose UHold.poll() raised - 'error <type name>' (printed with its text).\"\"\"\n"
     "    print('U hold: UHold.poll() raised %s: %s - no further poll, the hold ends now (item 528 (b)(1))' % (\n"
     "        type(error).__name__, str(error).encode('ascii', 'replace').decode('ascii')), flush=True)\n"
     "    return 'error %s' % type(error).__name__\n\n\n'''"),
    # 3. the poll inside the hold loop
    ("                    if uh is not None:\n"
     "                        ucause = uh.poll()\n"
     "                        if ucause is not None:\n"
     "                            break\n",
     "                    if uh is not None:\n"
     "                        try:\n"
     "                            ucause = uh.poll()\n"
     "                        except Exception as error:   # S15a2, item 528 (b)(1): no further poll, the hold ends now\n"
     "                            ucause = u_error(error)\n"
     "                        if ucause is not None:\n"
     "                            break\n"),
    # 4. the poll after the loop
    ("                    if ucause is None:\n"
     "                        ucause = uh.poll() or ('game ended' if game.poll() is not None else 'wall cap')\n",
     "                    if ucause is None:\n"
     "                        try:\n"
     "                            ucause = uh.poll() or ('game ended' if game.poll() is not None else 'wall cap')\n"
     "                        except Exception as error:   # S15a2, item 528 (b)(1): the poll after the loop\n"
     "                            ucause = u_error(error)\n"),
    # 5. the docstring of the generator
    ("the hold of a U arm by the rule of item 511 (z)(4)-(5) (--hold-u MIN_S:FRAMES:CAP_S).  Refuses when the lock exists.  LF, ASCII.\n",
     "the hold of a U arm by the rule of item 511 (z)(4)-(5) (--hold-u MIN_S:FRAMES:CAP_S); S15a2 (HPP-615, item 528 (b)(1)): both\n"
     "calls of UHold.poll() of the hold in try/except Exception (cause 'error <type name>', u_error).  Refuses when the lock exists.\n"
     "LF, ASCII.\n"),
]


def main():
    if os.path.exists(LOCK):
        print('LOCKED - nothing written')
        return 5
    raw = open(MK, 'rb').read()
    got = hashlib.sha256(raw).hexdigest()
    if got != MK_SHA:
        print('STOP: %s sha256 %s != %s' % (MK, got, MK_SHA))
        return 1
    t = raw.decode('ascii')
    if chr(13) in t:
        print('STOP: CR in %s' % MK)
        return 1
    for k, (old, new) in enumerate(R, 1):
        if t.count(old) != 1:
            print('STOP: anchor %d occurs %d times' % (k, t.count(old)))
            return 1
        t = t.replace(old, new)
    t.encode('ascii')
    if os.path.exists(LOCK):
        print('LOCKED before the write - nothing written')
        return 5
    with open(MK, 'w', encoding='ascii', newline=NL) as f:
        f.write(t)
    print('PATCHED %s sha256 %s (was %s), %d replacements' % (MK, hashlib.sha256(t.encode('ascii')).hexdigest(), MK_SHA, len(R)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
