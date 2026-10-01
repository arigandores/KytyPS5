# F2a (HPP-307): patch helper. Anchors are WHOLE LINES (a list of full lines that must occur
# exactly once, consecutively); the file is read with CR stripped and written back LF.
import sys


def load(path):
    data = open(path, 'rb').read().decode('utf-8')
    return data.replace('\r\n', '\n').split('\n')


def find_block(lines, anchor):
    hits = []
    n = len(anchor)
    for i in range(len(lines) - n + 1):
        if lines[i:i + n] == anchor:
            hits.append(i)
    return hits


def apply(path, edits):
    """edits: list of (anchor_lines, new_lines, mode); mode in before/after/replace."""
    lines = load(path)
    for anchor, new, mode in edits:
        hits = find_block(lines, anchor)
        if len(hits) != 1:
            print('ANCHOR FAIL', path, mode, repr(anchor[0])[:100], 'hits=%d' % len(hits))
            sys.exit(1)
        i = hits[0]
        n = len(anchor)
        if mode == 'before':
            lines[i:i] = new
        elif mode == 'after':
            lines[i + n:i + n] = new
        elif mode == 'replace':
            lines[i:i + n] = new
        else:
            print('BAD MODE', mode)
            sys.exit(1)
    open(path, 'wb').write('\n'.join(lines).encode('utf-8'))
    print('patched', path, len(edits))
