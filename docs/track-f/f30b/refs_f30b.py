# F30b (HPP-707, Red Team): every <commit>:<path>:<line> reference of docs/track-f/f30b-review.md - the anchor is the
# whole stripped line, the control +1 is the whole stripped next line; two planted wrong references must be rejected.
# usage: python refs_f30b.py   (run from anywhere inside C:/kyty/KytyPS5)
import subprocess, sys

RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
REFS = [
    ('R1', 'dc5d4712', RD, 3461, '} else if (t_rts != 3 && t_rts_reg) {', 'why = C::RtsXaReg;'),
    ('R2', 'dc5d4712', RD, 3484, 'if (t_rts == 1 && t_rts_pa) {',
     '// The skip (s.3.2): the record\'s outputs, then the stores of the resolution\'s memo hits in its order - the LRU'),
    ('R3', 'dc5d4712', RD, 3536, 'if (t_rts >= 2 && t_rts_pa) {',
     '// The resolution half of the self-check (s.5.1 step 2, s.5.2).'),
    ('R4', 'dc5d4712', RD, 3677, 'if (t_rts == 1 && pb_ok) {',
     '// The skip (s.3.2): the stores the fast path and the capture make on unchanged images, in the capture\'s order.'),
    ('R5', 'dc5d4712', RD, 3706, 'if (t_rts >= 2 && pb_ok) {', 't_rts_pb = true;'),
    ('R6', 'dc5d4712', RD, 3644, 'if (cache.MetaEpoch() != rec->meta) {', 'return C::RtsXbMeta;'),
    ('R7', 'dc5d4712', RD, 3649, 'if (img[i]->backing.state_serial != rec->t[i].state_serial) {', 'return C::RtsXbSer;'),
    ('R8', 'dc5d4712', RD, 1562, 'if (t_rts_race && (bits & kRtsBitsA) == 0) {', 'FS::Add(FS::Counter::RtsRace, 1);'),
    ('R9', 'dc5d4712', RD, 1554, 't_rts_race = stamp_moved;', '}'),
    ('R10', 'dc5d4712', RD, 3538, 'FS::Add(C::RtsPa, 1);', 'FS::Add(C::RtsChk, 1);'),
    ('R11', 'dc5d4712', RD, 3708, 'FS::Add(C::RtsPb, 1);', 'FS::Add(C::RtsChkB, 1);'),
    ('R12', 'dc5d4712', RD, 2194, 'depth.depth_load_clear_enable = depth.depth_clear_enable || meta_clear;',
     'skc3_depth_mat                = meta_clear;'),
    ('R13', 'dc5d4712', RD, 3701, 'state.depth_info.depth_load_clear_enable = false;', '}'),
    ('R14', 'dc5d4712', RD, 3789,
     '// PA and PB (the skip at 1): the record is not refreshed, only re-pinned at BeginRendering ([RC1]).', 'rec->age++;'),
    ('R15', 'dc5d4712', 'src/graphics/host_gpu/renderer/pipeline/descriptors.cpp', 3747,
     'LOGF("FixB42: mode=%d hit=%" PRIu64 " applied=%" PRIu64 " drawn=%" PRIu64 " rearm=%" PRIu64 " hit_all=%" PRIu64',
     None),
    ('R16', 'dc5d4712', 'src/graphics/presentation/videoOut.cpp', 3185, '{"rts_lost", FS::Counter::RtsLost, false},', None),
    ('R17', 'b081117d', 'docs/ROADMAP.md', 18780,
     'же вода на подходе и после шагов по воде (картинка без глитчей в том же кадре сцены [I]); на V харнесса Sky Garden (вход без ввода, Астро не входит в',
     'воду) не виден ⇒ `SCENE_OK` Sky Garden (п. 300) не снимается — форма V сцены не заходит в воду; строка курса меняется скриптом следующего закрытия.'),
]
NEG = [
    ('N1', 'dc5d4712', RD, 3462, '} else if (t_rts != 3 && t_rts_reg) {', None),
    ('N2', 'dc5d4712', RD, 1562, 'if (t_rts_race) {', None),
]

cache = {}


def lines(commit, path):
    key = (commit, path)
    if key not in cache:
        out = subprocess.run(['git', 'show', commit + ':' + path], capture_output=True, check=True).stdout
        cache[key] = out.decode('utf-8').replace('\r\n', '\n').split('\n')
    return cache[key]


def check(ref):
    _, commit, path, n, anchor, nxt = ref
    ls = lines(commit, path)
    if n - 1 >= len(ls) or ls[n - 1].strip() != anchor.strip():
        return False, 'anchor'
    hits = sum(1 for l in ls if l.strip() == anchor.strip())
    if nxt is not None and (n >= len(ls) or ls[n].strip() != nxt.strip()):
        return False, '+1'
    return True, 'anchor x%d' % hits + ('  +1 ok' if nxt is not None else '  +1 n/a (one-line anchor)')


ok = True
for r in REFS:
    good, why = check(r)
    ok &= good
    sys.stdout.write('%-4s %s  %s:%s:%d  %s\n' % (r[0], 'OK  ' if good else 'FAIL', r[1], r[2], r[3], why))
rej = 0
for r in NEG:
    good, _ = check(r)
    rej += 0 if good else 1
sys.stdout.write('NEG rejected %d/%d\n' % (rej, len(NEG)))
ok &= rej == len(NEG)
sys.stdout.write('ALL OK\n' if ok else 'FAILED\n')
sys.exit(0 if ok else 1)
