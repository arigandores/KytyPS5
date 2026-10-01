# Track F, F5a (HPP-355), step 2: both Missing() checks also test the knob - the =0 path is the old one by construction.
import sys

P = 'C:/kyty/KytyPS5/src/graphics/presentation/window/swapchain.cpp'
raw = open(P, 'rb').read()
crlf = b'\r\n' in raw
t = raw.decode('utf-8').replace('\r\n', '\n')

pairs = [
    ('\t\tif (swapchain.Missing()) [[unlikely]] { // F5 (B37): KYTY_FIX_MINIMIZE=1 and a zero extent only\n\t\t\tBeginZeroExtent();\n',
     '\t\tif (FixMinimizeEnabled() && swapchain.Missing()) [[unlikely]] { // F5 (B37): KYTY_FIX_MINIMIZE=1, zero extent\n\t\t\tBeginZeroExtent();\n'),
    ('\t\tif (swapchain.Missing()) [[unlikely]] { // F5 (B37): KYTY_FIX_MINIMIZE=1 and a zero extent only\n\t\t\tif (!m_impl->TryEndZeroExtent()) {\n',
     '\t\tif (FixMinimizeEnabled() && swapchain.Missing()) [[unlikely]] { // F5 (B37): KYTY_FIX_MINIMIZE=1, zero extent\n\t\t\tif (!m_impl->TryEndZeroExtent()) {\n'),
]
for old, new in pairs:
    if t.count(old) != 1:
        print('ANCHOR FAIL', t.count(old), old[:60])
        sys.exit(1)
    t = t.replace(old, new)
if crlf:
    t = t.replace('\n', '\r\n')
open(P, 'wb').write(t.encode('utf-8'))
print('PATCH2 OK')
