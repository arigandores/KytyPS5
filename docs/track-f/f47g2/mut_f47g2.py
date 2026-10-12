"""mut_f47g2.py - track F, F47g2 (HPP-828, ROADMAP s122 item 742(v)(4)): own mutants of diagF47Dt.cpp for the stand
(the binary members of RC1, RC2, RC4).  Whole-line anchors, exactly one hit, LF kept.

    python mut_f47g2.py <worktree root> <m2|m2p|m6|m7>

m2   the inline note hashes guest memory at the note instead of the staging bytes (RC4, arm S)
m2p  the resolution of a pooled source hashes guest memory instead of the staging copy (RC4, arm A2)
m6   q is taken from the present thread (GpuTimeProfiler::Frame / the stand override) (RC1, arm Q)
m7   the record of value (ii) is looked up by the range (the image uploaded last into it) (RC2, arm T)
The caller restores the file with git checkout."""
import sys

F = '/src/graphics/host_gpu/renderer/diagF47Dt.cpp'
M = {
    'm2': ('\t\t\ts.hash  = Hash(bytes, size);',
           '\t\t\t{ Read rg; ReadGuest(vaddr, size, &rg); s.hash = rg.ok ? Hash(rg.data, size) : 0; } // MUTANT m2'),
    'm2p': ('\t\ts.hash  = Hash(s.bytes, size);',
            '\t\t{ Read rg; ReadGuest(address, size, &rg); s.hash = rg.ok ? Hash(rg.data, size) : 0; } // MUTANT m2p'),
    'm6': ('\treturn g_flips.load(std::memory_order_relaxed) + 1u;',
           '\treturn PresentNow(); // MUTANT m6'),
    'm7': ('\tauto       it    = g_uploads.find(key);',
           '\tauto       it    = last != g_range_last.end() ? g_uploads.find(last->second) : g_uploads.end(); // MUTANT m7'),
}

root, name = sys.argv[1].rstrip('/\\'), sys.argv[2]
path = root + F
text = open(path, 'rb').read().decode('utf-8')
lines = text.split('\n')
old, new = M[name]
hits = [i for i, l in enumerate(lines) if l == old]
if len(hits) != 1:
    print('ANCHOR %s: %d hits' % (name, len(hits)))
    sys.exit(1)
lines[hits[0]] = new
open(path, 'wb').write('\n'.join(lines).encode('utf-8'))
print('MUTATED %s line %d' % (name, hits[0] + 1))
