"""mut_f47h.py - F47h (HPP-825): mutants of diagF47Dt.cpp in the F47h worktree (measurement of the review only).

    python mut_f47h.py <m1|m2|m5|base>

Applies one mutation to C:/kyty/f287/f47h/wt/src/graphics/host_gpu/renderer/diagF47Dt.cpp (base: git checkout of the
file). Whole-line anchors, each must occur exactly once; LF kept (the worktree file has no CR).
  m1 - value (i) taken from the cache: ih = hash of the last upload record of the range when it is hashed
  m2 - source (ii) of an inline staging upload re-reads guest memory at the note instead of hashing the staging bytes
  m5 - =0 writes a line: the "F47dt: mode=" line printed before the test of the value
"""
import subprocess
import sys

P = 'C:/kyty/f287/f47h/wt/src/graphics/host_gpu/renderer/diagF47Dt.cpp'
G = 'C:/Program Files/Git/cmd/git.exe'
NL = chr(10)

MUT = {
    'm1': ('\tconst uint64_t ih    = r.ok ? Hash(r.data, size) : 0;',
           '\tuint64_t ih = r.ok ? Hash(r.data, size) : 0; /* F47h m1 */' + NL +
           '\tif (auto m1 = g_uploads.find({address, size}); m1 != g_uploads.end() && '
           'std::strcmp(m1->second.cur.src.st, "hashed") == 0) { ih = m1->second.cur.src.hash; }'),
    'm2': ('\t\t\ts.hash  = Hash(bytes, size);',
           '\t\t\t{ Read rr; ReadGuest(vaddr, size, &rr); s.hash = rr.ok ? Hash(rr.data, size) : 0; } /* F47h m2 */'),
    'm5': ('\t\tconst bool value = Common::EnvValueOn(std::getenv("KYTY_DIAG_F47DT"));',
           '\t\tconst bool value = Common::EnvValueOn(std::getenv("KYTY_DIAG_F47DT"));' + NL +
           '\t\tLOGF("F47dt: mode=%d (F47h m5)\\n", value ? 1 : 0);'),
}


def main():
    name = sys.argv[1]
    subprocess.check_call([G, '-C', 'C:/kyty/f287/f47h/wt', 'checkout', '--', 'src/graphics/host_gpu/renderer/diagF47Dt.cpp'])
    if name == 'base':
        print('base restored')
        return
    text = open(P, 'rb').read().decode('utf-8')
    assert chr(13) not in text
    old, new = MUT[name]
    lines = text.split(NL)
    hits = [i for i, l in enumerate(lines) if l == old]
    assert len(hits) == 1, (name, len(hits))
    lines[hits[0]] = new
    open(P, 'wb').write(NL.join(lines).encode('utf-8'))
    print(name, 'applied at line', hits[0] + 1)


main()
