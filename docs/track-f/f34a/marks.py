"""F34a: print marker lines of selected logs (plain or .xz), streaming.

usage: marks.py <log> [<log> ...]
Markers: InputScript, Level has started, RenderDoc capture lines, GuestOut (first 400 distinct), FrameTrace count by
present at markers is not available, so we print present numbers when a line carries them.
"""
import lzma, re, sys

rx = re.compile(rb'InputScript|Level has started|RenderDoc|capture|GuestArgs|KytyPS5-20|GuestOut|LevelContextFiber|Exception: code=0xc|Fatal|ErrorDeviceLost|Event: quit|VideoOutRec|KYTY_REC|ShaderPreparation: startup')
for f in sys.argv[1:]:
    print('=====', f, flush=True)
    op = lzma.open if f.endswith('.xz') else open
    seen = {}
    n = 0
    with op(f, 'rb') as h:
        for ln, line in enumerate(h):
            if not rx.search(line):
                continue
            s = line[:260].decode('utf-8', 'replace').rstrip()
            k = re.sub(r'[0-9]+', '#', s)
            c = seen.get(k, 0)
            seen[k] = c + 1
            if c < 3:
                print(ln + 1, s, flush=True)
                n += 1
            if n > 400:
                break
    print('lines', ln + 1, flush=True)
