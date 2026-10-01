"""Link 1b of s145 (HPP-379): the details of the rows 295 (b)(1)-(2) are strings like every admission detail (add() of admit);
the two mutant anchors move with them.  ASCII only."""
import hashlib
import sys
for path, pairs in (('C:/kyty/s145/sc145.py', (
        ("    return [(W295[0], r['limit'] == 0, r['limit']), (W295[1], r['vk2'] >= 1, r['vk2']),",
         "    return [(W295[0], r['limit'] == 0, str(r['limit'])), (W295[1], r['vk2'] >= 1, str(r['vk2'])),"),)),
                    ('C:/kyty/s145/mut_sc145.py', (
        ("\"    return [(W295[0], r['limit'] == 0, r['limit'])\", \"    return [(W295[0], True, r['limit'])\"",
         "\"    return [(W295[0], r['limit'] == 0, str(r['limit']))\", \"    return [(W295[0], True, str(r['limit']))\""),
        ("\"(W295[1], r['vk2'] >= 1, r['vk2'])\", \"(W295[1], r['vk2'] >= 0, r['vk2'])\"",
         "\"(W295[1], r['vk2'] >= 1, str(r['vk2']))\", \"(W295[1], r['vk2'] >= 0, str(r['vk2']))\"")))):
    src = open(path, 'rb').read().decode('utf-8')
    for old, new in pairs:
        if src.count(old) != 1:
            print('ANCHOR COUNT %d in %s: %r' % (src.count(old), path, old))
            sys.exit(1)
        src = src.replace(old, new)
    open(path, 'wb').write(src.encode('ascii'))
    print('%s sha256 %s' % (path, hashlib.sha256(src.encode('ascii')).hexdigest()))
