# F24d (HPP-663, Red Team, ROADMAP s122 item 595(zh)): two mutants of the KYTY_FIX_B13=1 branch of
# src/graphics/host_gpu/regionManager.h in the worktree (anchors - whole lines of the =1 block, exactly once; LF kept,
# CR stripped before matching and restored). After the stand build the caller restores the file with git checkout.
#   g1st - the global epoch FIRST: m_cpu_epoch, point 11, m_epoch, point 12, bit, point 13
#   bitlast - the bit AFTER the global epoch: m_epoch, point 11, m_cpu_epoch, point 12, bit, point 13
# Usage: python mut_f24d.py <worktree> <g1st|bitlast>
import sys

path = sys.argv[1].rstrip('/') + '/src/graphics/host_gpu/regionManager.h'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
L = raw.decode('utf-8').replace('\r\n', '\n').split('\n')
T = '\t\t\t\t'
E = T + 'm_epoch.fetch_add(1, std::memory_order_release);'
G = T + 'm_cpu_epoch.fetch_add(1, std::memory_order_release);'
IF = '#if defined(KYTY_TEST_B13_HOOK)'
EN = '#endif'
H11 = T + 'B13Test::Hook(11); // Track F, F24c: after the region epoch, before the bdabits bit'
CM = T + '// Gate "bdabits": the map mirrors this epoch, so it is set here - before the global epoch, never later.'
BIT = T + 'BdaNoteRegionWrite(m_cpu_addr / TRACKER_REGION_SIZE);'
H12 = T + 'B13Test::Hook(12); // Track F, F24c: after the bdabits bit, before the global epoch'
block = [E, IF, H11, EN, CM, BIT, IF, H12, EN, G]
hits = [i for i in range(len(L) - len(block) + 1) if L[i:i + len(block)] == block]
if len(hits) != 1:
    sys.exit('anchor block found %d times' % len(hits))
MUT = T + '// F24d MUTANT %s' % sys.argv[2]
if sys.argv[2] == 'g1st':
    new = [MUT, G, IF, H11, EN, E, IF, H12, EN, BIT]
elif sys.argv[2] == 'bitlast':
    new = [MUT, E, IF, H11, EN, G, IF, H12, EN, BIT]
else:
    sys.exit('unknown mutant')
i = hits[0]
L[i:i + len(block)] = new
txt = '\n'.join(L)
if crlf:
    txt = txt.replace('\n', '\r\n')
open(path, 'wb').write(txt.encode('utf-8'))
print('mutant', sys.argv[2], 'applied at line', i + 1, path)
