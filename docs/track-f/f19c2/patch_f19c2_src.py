# F19c2 (HPP-559, ROADMAP s122 item 460(v)(1); RC1 of the F19d review): PadOutput::Stop moves m_thread into a local
# std::thread under m_mutex together with m_stop = true; notify_all, then join (detach on the PadOutput thread itself)
# of the local outside the lock; a second or later call finds m_thread empty (not joinable) and returns.
# The KYTY_FIX_B24=0 branches are not touched (PadOutput is not created at 0).
# Anchors are whole lines / whole blocks, each must occur exactly once; CRLF-safe; writes LF back as found.
# Usage: python patch_f19c2_src.py <repo root>
import sys

root = sys.argv[1].rstrip('/')
path = root + '/src/libs/controller.cpp'
raw = open(path, 'rb').read()
crlf = b'\r\n' in raw
s = raw.decode('utf-8').replace('\r\n', '\n')

T = '\t'
N = '\n'

old_comment = T + '// Everything below is guarded by m_mutex; m_thread is touched only by Start and Stop.' + N
new_comment = (T + '// Everything below is guarded by m_mutex. m_thread is set by Start (once, before the object is shared) and' + N +
               T + '// moved out under m_mutex by Stop (F19c2, ROADMAP s122 item 460(v)(1)), so concurrent Stop calls join it once.' + N)

old_stop = (
    'void PadOutput::Stop() {' + N +
    T + '{' + N +
    T + T + 'std::lock_guard lock(m_mutex);' + N +
    T + T + 'm_stop = true;' + N +
    T + '}' + N +
    T + 'm_cv.notify_all();' + N +
    T + 'if (m_thread.joinable()) {' + N +
    T + T + 'if (m_thread.get_id() == std::this_thread::get_id()) {' + N +
    T + T + T + 'm_thread.detach();' + N +
    T + T + '} else {' + N +
    T + T + T + 'm_thread.join();' + N +
    T + T + '}' + N +
    T + '}' + N +
    '}' + N)

new_stop = (
    'void PadOutput::Stop() {' + N +
    T + '// Track F, F19c2 (ROADMAP s122 item 460(v)(1), RC1 of the F19d review): two emergency exits at once call Stop' + N +
    T + '// concurrently. The thread object is moved out under m_mutex with m_stop = true, so exactly one call owns it and' + N +
    T + '// joins it outside the lock; every other call gets an empty (not joinable) thread and returns.' + N +
    T + 'std::thread thread;' + N +
    T + '{' + N +
    T + T + 'std::lock_guard lock(m_mutex);' + N +
    T + T + 'm_stop = true;' + N +
    T + T + 'thread = std::move(m_thread);' + N +
    T + '}' + N +
    T + 'm_cv.notify_all();' + N +
    T + 'if (thread.joinable()) {' + N +
    T + T + 'if (thread.get_id() == std::this_thread::get_id()) {' + N +
    T + T + T + 'thread.detach();' + N +
    T + T + '} else {' + N +
    T + T + T + 'thread.join();' + N +
    T + T + '}' + N +
    T + '}' + N +
    '}' + N)

for old, new in [(old_comment, new_comment), (old_stop, new_stop)]:
    n = s.count(old)
    if n != 1:
        sys.exit('anchor count %d: %r' % (n, old[:80]))
    s = s.replace(old, new)

out = s.replace('\n', '\r\n') if crlf else s
open(path, 'wb').write(out.encode('utf-8'))
print('patched', path, 'crlf' if crlf else 'lf')
