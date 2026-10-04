# F20a (HPP-551): the translation dump in the sample logs - the number of IR lines (a line whose first non-blank
# character is '%') before and after the first scene frame of Sky Garden, and the frames after it whose interval holds
# at least one IR line (count, the largest dt_us, the list of [idx, dt_us] when short).  Line-by-line reading.
# Usage: python irscan_f20a.py <out.txt> <tag=path> ...
import lzma, multiprocessing, re, sys

FT = re.compile(rb'FrameTrace: n=(\d+) dt_us=(\d+)')
DRAWS = re.compile(rb' draws=(\d+)')


def scan(a):
    tag, path = a.split('=', 1)
    f = lzma.open(path, 'rb') if path.endswith('.xz') else open(path, 'rb')
    in_sg = False
    first_n = None
    idx = 0
    before = after = cur = 0
    fr = []
    for line in f:
        if line.startswith(b'FrameTrace: n='):
            m = FT.match(line)
            if m and in_sg:
                if first_n is None:
                    d = DRAWS.search(line)
                    if d and int(d.group(1)) >= 100:
                        first_n = int(m.group(1))
                else:
                    idx += 1
                    if cur:
                        fr.append((idx, int(m.group(2)), cur))
            cur = 0
        elif b'Level has started:' in line:
            name = line.split(b'Level has started:', 1)[1].strip()
            if name:
                in_sg = name == b'underwater_aerial_garden'
        elif line.lstrip()[:1] == b'%':
            if first_n is None:
                before += 1
            else:
                after += 1
                cur += 1
    f.close()
    return '%s: first_n %s; IR lines before the first scene frame %d, after %d; frames with IR lines in the interval %d, max dt_us %d; [idx, dt_us, IR lines]: %s' % (
        tag, first_n, before, after, len(fr), max([x[1] for x in fr] or [0]), [list(x) for x in fr[:14]])


if __name__ == '__main__':
    with multiprocessing.Pool(12) as pool:
        res = pool.map(scan, sys.argv[2:])
    with open(sys.argv[1], 'w', encoding='utf-8', newline='\n') as o:
        for r in res:
            o.write(r + '\n')
            print(r)
