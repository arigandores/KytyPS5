# F19d2 (HPP-560, Red Team; ROADMAP s122 item 460(g)): mutants of PadOutput::Stop in the own worktree
# C:/kyty/f287/f19d2/wt (919c1a19). Only the worktree file is changed; restore = git checkout of the file.
#   python mut_f19d2.py m1  - "join of the member outside the lock": no move, m_thread.joinable()/join()/detach() outside
#                             m_mutex (the 9c726d74 body).
#   python mut_f19d2.py m3  - move of m_thread OUTSIDE the lock (after the m_stop block), join of the local.
#   python mut_f19d2.py check - prints which body the file has (new / m1 / m3), exit 1 if none.
# LF in, LF out (write_bytes); the anchor is the whole body block, must occur exactly once.
import sys

PATH = 'C:/kyty/f287/f19d2/wt/src/libs/controller.cpp'
T = chr(9)


def block(lines):
    return ''.join(T + l + chr(10) for l in lines)


NEW = block([
    'std::thread thread;',
    '{',
    T + 'std::lock_guard lock(m_mutex);',
    T + 'm_stop = true;',
    T + 'thread = std::move(m_thread);',
    '}',
    'm_cv.notify_all();',
    'if (thread.joinable()) {',
    T + 'if (thread.get_id() == std::this_thread::get_id()) {',
    T + T + 'thread.detach();',
    T + '} else {',
    T + T + 'thread.join();',
    T + '}',
    '}',
])

M1 = block([
    '{',
    T + 'std::lock_guard lock(m_mutex);',
    T + 'm_stop = true;',
    '}',
    'm_cv.notify_all();',
    'if (m_thread.joinable()) {',
    T + 'if (m_thread.get_id() == std::this_thread::get_id()) {',
    T + T + 'm_thread.detach();',
    T + '} else {',
    T + T + 'm_thread.join();',
    T + '}',
    '}',
])

M3 = block([
    '{',
    T + 'std::lock_guard lock(m_mutex);',
    T + 'm_stop = true;',
    '}',
    'std::thread thread = std::move(m_thread);',
    'm_cv.notify_all();',
    'if (thread.joinable()) {',
    T + 'if (thread.get_id() == std::this_thread::get_id()) {',
    T + T + 'thread.detach();',
    T + '} else {',
    T + T + 'thread.join();',
    T + '}',
    '}',
])


def main():
    mode = sys.argv[1]
    raw = open(PATH, 'rb').read()
    assert b'\r' not in raw, 'CR in file'
    s = raw.decode('utf-8')
    have = [n for n, b in (('new', NEW), ('m1', M1), ('m3', M3)) if s.count(b) == 1]
    if mode == 'check':
        print('body:', have)
        return 0 if len(have) == 1 else 1
    want = {'m1': M1, 'm3': M3}[mode]
    assert s.count(NEW) == 1, 'anchor (new body) count %d' % s.count(NEW)
    s2 = s.replace(NEW, want)
    assert s2.count(want) == 1 and s2.count(NEW) == 0
    open(PATH, 'wb').write(s2.encode('utf-8'))
    print('applied', mode)
    return 0


if __name__ == '__main__':
    sys.exit(main())
