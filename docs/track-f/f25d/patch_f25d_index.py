# F25d (HPP-667; ROADMAP s122 item 599(b)(8), RC8 of F25c): the index fix of the window close - the CloseWindow time on
# 4 096 samples x 90 slots x 20 000 records was 110-121 ms (> 100 ms) with the quadratic places of F20j4. Each place gets
# an index that gives the same answer by construction:
#   (1) CloseWindow: the open records matched to the closed ones by a sorted key list (one pass) instead of an erase
#       over the whole list per closed record;
#   (2) PickWaits: membership of a record in the closure by a flag per record instead of std::find over `must`;
#   (3) NearestSnapshot: the inner loop over the samples with their own snapshot only (same order, same ties);
#   (4) RowOf / GidOf: slot + 1 -> the first thread row with it (a position table built once per call).
# Usage: python patch_f25d_index.py <worktree root>
import sys

ROOT = sys.argv[1].rstrip('/\\')
C = 'src/common/diagB32.cpp'
c = open(ROOT + '/' + C, 'rb').read().decode('utf-8').replace('\r\n', '\n')


def sub(text, old, new, count=1):
    n = text.count(old)
    if n != count:
        raise SystemExit('anchor count %d != %d: %r' % (n, count, old[:120]))
    return text.replace(old, new)


# (3) NearestSnapshot
c = sub(c, 'void NearestSnapshot(const uint64_t* t, const uint8_t* kq, const uint64_t* kq_t, size_t n, uint64_t max_ns,\n'
           '                     int32_t* out) {\n'
           '\tfor (size_t i = 0; i < n; i++) {\n'
           '\t\tif (kq[i] != 0) {\n'
           '\t\t\tout[i] = static_cast<int32_t>(i);\n'
           '\t\t\tcontinue;\n'
           '\t\t}\n'
           '\t\tint32_t  best   = -1;\n'
           '\t\tuint64_t best_d = 0;\n'
           '\t\tfor (size_t j = 0; j < n; j++) {\n'
           '\t\t\tif (kq[j] == 0) {\n'
           '\t\t\t\tcontinue;\n'
           '\t\t\t}\n',
        'void NearestSnapshot(const uint64_t* t, const uint8_t* kq, const uint64_t* kq_t, size_t n, uint64_t max_ns,\n'
        '                     int32_t* out) {\n'
        '\t// F25d (item 599(b)(8), RC8 of F25c): the inner loop runs over the samples with a snapshot only, in the same order\n'
        '\t// (the same nearest one and the same tie - the earlier) - n x snapshots instead of n x n.\n'
        '\tstd::vector<size_t> snaps;\n'
        '\tfor (size_t j = 0; j < n; j++) {\n'
        '\t\tif (kq[j] != 0) {\n'
        '\t\t\tsnaps.push_back(j);\n'
        '\t\t}\n'
        '\t}\n'
        '\tfor (size_t i = 0; i < n; i++) {\n'
        '\t\tif (kq[i] != 0) {\n'
        '\t\t\tout[i] = static_cast<int32_t>(i);\n'
        '\t\t\tcontinue;\n'
        '\t\t}\n'
        '\t\tint32_t  best   = -1;\n'
        '\t\tuint64_t best_d = 0;\n'
        '\t\tfor (const size_t j: snaps) {\n')

# (4) RowOf / GidOf
c = sub(c, 'static ThreadRow* RowOf(Report* r, int32_t slot1) {\n'
           '\tif (slot1 <= 0) {\n'
           '\t\treturn nullptr;\n'
           '\t}\n'
           '\tfor (auto& t: r->threads) {\n'
           '\t\tif (t.slot1 == slot1) {\n'
           '\t\t\treturn &t;\n'
           '\t\t}\n'
           '\t}\n'
           '\treturn nullptr;\n'
           '}\n',
        '// F25d (item 599(b)(8), RC8 of F25c): slot + 1 -> the position of the FIRST thread row with it, built once per call -\n'
        '// the answer of the linear search of F20j4 (RowOf, GidOf) by construction. Rows with slot1 <= 0 are not indexed:\n'
        '// RowOf never returns them, GidOf searches them linearly (none in the sampler\'s reports).\n'
        'class RowIndex {\n'
        'public:\n'
        '\texplicit RowIndex(const Report& r) {\n'
        '\t\tfor (size_t i = 0; i < r.threads.size(); i++) {\n'
        '\t\t\tconst auto s = r.threads[i].slot1;\n'
        '\t\t\tif (s <= 0) {\n'
        '\t\t\t\tm_nonpos = true;\n'
        '\t\t\t\tcontinue;\n'
        '\t\t\t}\n'
        '\t\t\tif (static_cast<size_t>(s) >= m_pos.size()) {\n'
        '\t\t\t\tm_pos.resize(static_cast<size_t>(s) + 1, -1);\n'
        '\t\t\t}\n'
        '\t\t\tif (m_pos[static_cast<size_t>(s)] < 0) {\n'
        '\t\t\t\tm_pos[static_cast<size_t>(s)] = static_cast<int32_t>(i);\n'
        '\t\t\t}\n'
        '\t\t}\n'
        '\t}\n'
        '\t[[nodiscard]] int32_t Pos(int32_t slot1) const {\n'
        '\t\treturn slot1 > 0 && static_cast<size_t>(slot1) < m_pos.size() ? m_pos[static_cast<size_t>(slot1)] : -1;\n'
        '\t}\n'
        '\t[[nodiscard]] bool NonPositive() const { return m_nonpos; }\n'
        '\n'
        'private:\n'
        '\tstd::vector<int32_t> m_pos;\n'
        '\tbool                 m_nonpos = false;\n'
        '};\n'
        '\n'
        'static ThreadRow* RowOf(Report* r, const RowIndex& index, int32_t slot1) {\n'
        '\tconst auto p = index.Pos(slot1);\n'
        '\treturn p >= 0 ? &r->threads[static_cast<size_t>(p)] : nullptr;\n'
        '}\n')
c = sub(c, '\tsize_t     cut  = 0;\n\tconst auto pick = PickWaits(r, &cut);\n\tfor (auto i: pick) {\n'
           '\t\tif (auto* t = RowOf(&r, r.waits[i].waker1); t != nullptr) {\n',
        '\tsize_t         cut  = 0;\n\tconst auto     pick = PickWaits(r, &cut);\n'
        '\tconst RowIndex index(r); // F25d (item 599(b)(8))\n'
        '\tfor (auto i: pick) {\n'
        '\t\tif (auto* t = RowOf(&r, index, r.waits[i].waker1); t != nullptr) {\n')
c = sub(c, '\t\tif (auto* t = RowOf(&r, r.waits[i].peer1); t != nullptr) { // F20j3 (RC2: every waker / peer of the -w records)\n',
        '\t\tif (auto* t = RowOf(&r, index, r.waits[i].peer1); t != nullptr) { // F20j3 (RC2: every waker / peer of the -w records)\n')
c = sub(c, '\t\t\tif (auto* p = RowOf(&r, t.last.peer); p != nullptr && t.must) {\n',
        '\t\t\tif (auto* p = RowOf(&r, index, t.last.peer); p != nullptr && t.must) {\n')
c = sub(c, 'static int32_t GidOf(const Report& r, int32_t slot1) {\n'
           '\tfor (const auto& t: r.threads) {\n'
           '\t\tif (t.slot1 == slot1) {\n'
           '\t\t\treturn t.gid;\n'
           '\t\t}\n'
           '\t}\n'
           '\treturn 0;\n'
           '}\n',
        'static int32_t GidOf(const Report& r, const RowIndex& index, int32_t slot1) {\n'
        '\tif (slot1 > 0) {\n'
        '\t\tconst auto p = index.Pos(slot1);\n'
        '\t\treturn p >= 0 ? r.threads[static_cast<size_t>(p)].gid : 0;\n'
        '\t}\n'
        '\tif (!index.NonPositive()) {\n'
        '\t\treturn 0;\n'
        '\t}\n'
        '\tfor (const auto& t: r.threads) {\n'
        '\t\tif (t.slot1 == slot1) {\n'
        '\t\t\treturn t.gid;\n'
        '\t\t}\n'
        '\t}\n'
        '\treturn 0;\n'
        '}\n')
c = sub(c, '\tfor (auto i: picks) {\n\t\tconst auto& w = r.waits[i];\n',
        '\tconst RowIndex index(r); // F25d (item 599(b)(8))\n'
        '\tfor (auto i: picks) {\n\t\tconst auto& w = r.waits[i];\n')
c = sub(c, '\t\t       n, SlotIndex(w.slot1), GidOf(r, w.slot1), WaitName(w.kind), static_cast<unsigned long long>(w.obj),\n',
        '\t\t       n, SlotIndex(w.slot1), GidOf(r, index, w.slot1), WaitName(w.kind), static_cast<unsigned long long>(w.obj),\n')
c = sub(c, '\t\t       GidOf(r, w.waker1), static_cast<unsigned long long>(w.req_us), w.timed_out, w.open, SlotIndex(w.peer1),\n'
           '\t\t       GidOf(r, w.peer1));\n',
        '\t\t       GidOf(r, index, w.waker1), static_cast<unsigned long long>(w.req_us), w.timed_out, w.open, SlotIndex(w.peer1),\n'
        '\t\t       GidOf(r, index, w.peer1));\n')

# (2) PickWaits
c = sub(c, '\tstd::vector<size_t> must;\n'
           '\tfor (int step = 0; step < 3; step++) {\n'
           '\t\tconst auto before = set.size();\n'
           '\t\tfor (size_t i = 0; i < r.waits.size(); i++) {\n'
           '\t\t\tif (std::find(set.begin(), set.end(), r.waits[i].slot1) != set.end() &&\n'
           '\t\t\t    std::find(must.begin(), must.end(), i) == must.end()) {\n'
           '\t\t\t\tmust.push_back(i);\n',
        '\tstd::vector<size_t> must;\n'
        '\t// F25d (item 599(b)(8), RC8 of F25c): a record\'s membership in `must` - a flag per record, not std::find over must.\n'
        '\tstd::vector<char> in_must(r.waits.size(), 0);\n'
        '\tfor (int step = 0; step < 3; step++) {\n'
        '\t\tconst auto before = set.size();\n'
        '\t\tfor (size_t i = 0; i < r.waits.size(); i++) {\n'
        '\t\t\tif (in_must[i] == 0 && std::find(set.begin(), set.end(), r.waits[i].slot1) != set.end()) {\n'
        '\t\t\t\tin_must[i] = 1;\n'
        '\t\t\t\tmust.push_back(i);\n')
c = sub(c, '\tstd::vector<size_t> rest;\n'
           '\tfor (size_t i = 0; i < r.waits.size(); i++) {\n'
           '\t\tif (std::find(must.begin(), must.end(), i) == must.end()) {\n',
        '\tstd::vector<size_t> rest;\n'
        '\tfor (size_t i = 0; i < r.waits.size(); i++) {\n'
        '\t\tif (in_must[i] == 0) {\n')

# (1) CloseWindow: open records vs closed ones
c = sub(c, '\tfor (const auto& w: m_recent) {\n'
           '\t\tif (w.end_ns > start && w.start_ns < flip_ns) {\n'
           '\t\t\t// The same wait seen open in the last sample and closed (in the ring) before the flip: keep the closed record.\n'
           '\t\t\tr.waits.erase(std::remove_if(r.waits.begin(), r.waits.end(),\n'
           '\t\t\t                             [&](const Core::WaitRec& o) {\n'
           '\t\t\t\t                             return o.open != 0 && o.slot1 == w.slot1 && o.start_ns == w.start_ns;\n'
           '\t\t\t                             }),\n'
           '\t\t\t              r.waits.end());\n'
           '\t\t\tr.waits.push_back(w);\n'
           '\t\t}\n'
           '\t}\n',
        '\t// The same wait seen open in the last sample and closed (in the ring) before the flip: keep the closed record.\n'
        '\t// F25d (item 599(b)(8), RC8 of F25c): one pass - an open record is dropped iff a closed record of the window has its\n'
        '\t// slot and start (sorted keys, binary search); the kept open records stay first in their order, the closed ones follow\n'
        '\t// in the m_recent order - the list of the per-record erase of F20j4 (r.waits holds only open records here).\n'
        '\t{\n'
        '\t\tstd::vector<std::pair<int32_t, uint64_t>> keys;\n'
        '\t\tfor (const auto& w: m_recent) {\n'
        '\t\t\tif (w.end_ns > start && w.start_ns < flip_ns) {\n'
        '\t\t\t\tkeys.emplace_back(w.slot1, w.start_ns);\n'
        '\t\t\t}\n'
        '\t\t}\n'
        '\t\tstd::sort(keys.begin(), keys.end());\n'
        '\t\tr.waits.erase(std::remove_if(r.waits.begin(), r.waits.end(),\n'
        '\t\t                             [&](const Core::WaitRec& o) {\n'
        '\t\t\t                             return o.open != 0 &&\n'
        '\t\t\t                                    std::binary_search(keys.begin(), keys.end(), std::make_pair(o.slot1, o.start_ns));\n'
        '\t\t                             }),\n'
        '\t\t              r.waits.end());\n'
        '\t\tfor (const auto& w: m_recent) {\n'
        '\t\t\tif (w.end_ns > start && w.start_ns < flip_ns) {\n'
        '\t\t\t\tr.waits.push_back(w);\n'
        '\t\t\t}\n'
        '\t\t}\n'
        '\t}\n')
open(ROOT + '/' + C, 'wb').write(c.encode('utf-8'))
print('INDEX PATCH OK')
