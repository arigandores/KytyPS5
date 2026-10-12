"""mut_f47h2.py - track F, F47h2 (HPP-829, ROADMAP s122 item 742(d), 743(g)): own mutants m1, m2, m2p, m5, m6, m7 of
diagF47Dt.cpp (stand) and m8 of the reader dt_f47g2.py (selftest).  Whole-line anchors, exactly one hit, LF kept.
m1, m2, m5 - copies of mut_f47h.py (F47h) with the key of F47g2 (image key); m2p, m6, m7 - own wording of the same
mutations as mut_f47g2.py (F47g2), written independently.

    python mut_f47h2.py src <worktree root> <m1|m2|m2p|m5|m6|m7>     mutate diagF47Dt.cpp (caller restores: git checkout)
    python mut_f47h2.py reader <dt_f47g2.py> <out.py> m8             write a mutated copy of the reader

m1   value (i) is the hash of the record of the image (the cache) when it is hashed, not of the guest bytes now
m2   the inline note hashes guest memory at the note instead of the staging bytes (RC4, arm S)
m2p  the resolution of a pooled source hashes guest memory instead of the staging copy (RC4, arm A2)
m5   =0 writes a line ("F47dt: mode=")
m6   q is taken from the present thread (PresentNow) instead of the flips queued by the parse (RC1, arm Q)
m7   the record of value (ii) is the one of the image uploaded last into the range (RC2, arm T)
m8   reader: (i) != (ii) with cpu=1 / maybe=1 is read as ne (defect) instead of und (F3, fixture G9)
"""
import sys

NL = chr(10)
F = '/src/graphics/host_gpu/renderer/diagF47Dt.cpp'
SRC = {
    'm1': ('\tconst uint64_t ih    = r.ok ? Hash(r.data, size) : 0;',
           '\tuint64_t ih = r.ok ? Hash(r.data, size) : 0; /* F47h2 m1 */' + NL +
           '\tif (auto m1 = g_uploads.find(key); m1 != g_uploads.end() && '
           'std::strcmp(m1->second.cur.src.st, "hashed") == 0) { ih = m1->second.cur.src.hash; }'),
    'm2': ('\t\t\ts.hash  = Hash(bytes, size);',
           '\t\t\t{ Read rr; ReadGuest(vaddr, size, &rr); s.hash = rr.ok ? Hash(rr.data, size) : 0; } /* F47h2 m2 */'),
    'm2p': ('\t\ts.hash  = Hash(s.bytes, size);',
            '\t\t{ Read rr; ReadGuest(address, size, &rr); s.hash = rr.ok ? Hash(rr.data, size) : 0; } /* F47h2 m2p */'),
    'm5': ('\t\tconst bool value = Common::EnvValueOn(std::getenv("KYTY_DIAG_F47DT"));',
           '\t\tconst bool value = Common::EnvValueOn(std::getenv("KYTY_DIAG_F47DT"));' + NL +
           '\t\tLOGF("F47dt: mode=%d (F47h2 m5)' + chr(92) + 'n", value ? 1 : 0);'),
    'm6': ('\treturn g_flips.load(std::memory_order_relaxed) + 1u;',
           '\treturn PresentNow(); /* F47h2 m6 */'),
    'm7': ('\tauto       it    = g_uploads.find(key);',
           '\tauto       it    = last != g_range_last.end() ? g_uploads.find(last->second) : g_uploads.end(); '
           '/* F47h2 m7 */'),
}
READER = {
    'm8': ("        if t.get('cpu') == '1' or t.get('maybe') == '1':",
           "        if False:  # F47h2 m8"),
}


def sub(lines, old, new, name):
    hits = [i for i, l in enumerate(lines) if l == old]
    if len(hits) != 1:
        print('ANCHOR %s: %d hits' % (name, len(hits)))
        sys.exit(1)
    lines[hits[0]] = new
    return hits[0] + 1


def main():
    if sys.argv[1] == 'src':
        root, name = sys.argv[2].rstrip('/' + chr(92)), sys.argv[3]
        path = root + F
        lines = open(path, 'rb').read().decode('utf-8').split(NL)
        at = sub(lines, SRC[name][0], SRC[name][1], name)
        open(path, 'wb').write(NL.join(lines).encode('utf-8'))
        print('MUTATED %s line %d' % (name, at))
    elif sys.argv[1] == 'reader':
        src, out, name = sys.argv[2], sys.argv[3], sys.argv[4]
        lines = open(src, 'rb').read().decode('utf-8').split(NL)
        at = sub(lines, READER[name][0], READER[name][1], name)
        open(out, 'wb').write(NL.join(lines).encode('utf-8'))
        print('MUTATED %s line %d -> %s' % (name, at, out))
    else:
        sys.exit(2)


main()
