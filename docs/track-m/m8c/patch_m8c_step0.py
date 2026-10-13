"""Track M, M8c (HPP-860), step 0 = RC3 of M8b (ROADMAP s122 item 783(g)): the stand comparator MaxDiff of
tests/MT125Stand.cpp returns +inf for any non-finite output sample (std::max(m, NaN) kept m, so a NaN mix compared as 0).
Only tests/MT125Stand.cpp changes. CRLF-safe; whole-line anchors; writes LF if the file was LF.
Usage: python patch_m8c_step0.py <tree root>   Last line: PATCH OK or FAIL."""
import sys

NL = chr(10)
CR = chr(13)
T = chr(9)
root = sys.argv[1]
path = root + '/tests/MT125Stand.cpp'
raw = open(path, 'rb').read().decode('utf-8')
crlf = (CR + NL) in raw
text = raw.replace(CR + NL, NL)

old = (T + T + 'std::memcpy(&v, out.bytes.data() + i * sizeof(float), sizeof(float));' + NL +
       T + T + 'm = std::max(m, std::fabs(static_cast<double>(v) - ref[i]));' + NL)
new = (T + T + 'std::memcpy(&v, out.bytes.data() + i * sizeof(float), sizeof(float));' + NL +
       T + T + 'if (!std::isfinite(v)) {' + NL +
       T + T + T + '// Track M, M8c (RC3 of M8b, ROADMAP s122 item 783(g)): a non-finite output sample fails the comparison;' + NL +
       T + T + T + '// std::max(m, NaN) keeps m, so without this a NaN mix (NaN GAIN accepted) compared as max_diff 0.' + NL +
       T + T + T + 'return std::numeric_limits<double>::infinity();' + NL +
       T + T + '}' + NL +
       T + T + 'm = std::max(m, std::fabs(static_cast<double>(v) - ref[i]));' + NL)
n = text.count(old)
if n != 1:
    print('anchor count', n)
    print('FAIL')
    sys.exit(1)
if '#include <limits>' not in text and 'numeric_limits' not in text:
    print('no <limits> in use')
    print('FAIL')
    sys.exit(1)
text = text.replace(old, new)
if crlf:
    text = text.replace(NL, CR + NL)
open(path, 'wb').write(text.encode('utf-8'))
print('crlf', crlf, 'patched', path)
print('PATCH OK')
