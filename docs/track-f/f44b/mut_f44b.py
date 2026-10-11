# F44b (HPP-792, Red Team; ROADMAP s122 item 698(d)(3)): mutants m1-m6 of KYTY_FIX_F29 and of the F29 stand.
# Applied to the files of the F44b worktree (e148f54c) one at a time; anchors are whole lines (stripped of the leading
# indentation only for the match, the indentation of the file is kept); the file is read in binary, CR is removed for
# the search and restored if the file had CRLF; written with write_bytes.
#   python mut_f44b.py apply <wt> <m>    - apply mutant m (m1 m2 m3 m4 m5 m6a m6b); exit 1 if an anchor is not found once
#   python mut_f44b.py check <wt>        - print the git diff stat of the worktree files touched by the mutants
# Revert: git -C <wt> checkout -- src/graphics/host_gpu/renderer/cache/faultManager.cpp tests/F29FaultStand.cpp
import sys

FM = 'src/graphics/host_gpu/renderer/cache/faultManager.cpp'
ST = 'tests/F29FaultStand.cpp'

LAST = 'constexpr auto               last_record = static_cast<uint32_t>(MaxPageFaults - 1);'
COUNT = 'parse.count = clamp ? std::min(parse.raw, last_record) : parse.raw;'
COND = 'if (clamp && parse.raw > last_record) {'
CAP = 'if (total <= FixF29OverflowLines) {'
ST_LAST = 'constexpr uint32_t LastRecord  = 1023;                 // the stand\'s own expectation (not the emulator constant)'
ST_CALL1 = 'const auto            parse = Libs::Graphics::ParseFaultArea('
ST_CALL2 = '(void)Libs::Graphics::ParseFaultArea(area_ptr, false, [&](uint32_t index, uint64_t v) {'
ST_ANCHOR = 'uint64_t Neighbour(uint32_t area, uint32_t i, uint64_t count) {'

# m4: a copy of the function body in the stand (same logic, own static counter and own line), the two calls use the copy.
COPY = [
    'Libs::Graphics::FaultAreaParse ParseFaultAreaCopy(const uint64_t* area, bool clamp,',
    '                                                  const Libs::Graphics::FaultAreaVisitor& visit,',
    '                                                  const Libs::Graphics::FaultAreaPass& pass = {}) {',
    '\tstatic uint64_t                overflow_total = 0;',
    '\tconstexpr uint32_t             last_record    = 1023;',
    '\tLibs::Graphics::FaultAreaParse parse;',
    '\tparse.raw   = static_cast<uint32_t>(area[0]);',
    '\tparse.count = clamp ? std::min(parse.raw, last_record) : parse.raw;',
    '\tif (clamp && parse.raw > last_record) {',
    '\t\tconst uint64_t total = ++overflow_total;',
    '\t\tif (total <= 32) {',
    '\t\t\tLOGF("FixF29: overflow pass=%" PRIu64 " area=%u count=%u read=%u total=%" PRIu64 "\\n", pass.pass, pass.area,',
    '\t\t\t     parse.raw, parse.count, total);',
    '\t\t}',
    '\t}',
    '\tfor (uint32_t index = 1; index <= parse.count; ++index) {',
    '\t\tvisit(index, area[index]);',
    '\t}',
    '\treturn parse;',
    '}',
    '',
]

MUTANTS = {
    'm1': [(FM, LAST, ['constexpr auto               last_record = static_cast<uint32_t>(MaxPageFaults);'])],
    'm2': [(FM, COUNT, ['parse.count = std::min(parse.raw, last_record);'])],
    'm3': [(FM, COUNT, ['parse.count = (clamp && pass.area == 7) ? std::min(parse.raw, last_record) : parse.raw;'])],
    'm4': [(ST, ST_CALL1, ['const auto            parse = ParseFaultAreaCopy(']),
           (ST, ST_CALL2, ['(void)ParseFaultAreaCopy(area_ptr, false, [&](uint32_t index, uint64_t v) {']),
           (ST, ST_ANCHOR, COPY + [ST_ANCHOR])],
    'm5': [(FM, LAST, ['constexpr auto               last_record = static_cast<uint32_t>(MaxPageFaults);']),
           (ST, ST_LAST, ['constexpr uint32_t LastRecord  = 1024;                 // m5: the stand expectation follows the function'])],
    'm6a': [(FM, COND, ['if (parse.raw > last_record) {'])],
    'm6b': [(FM, CAP, ['if (true) {'])],
}


def apply(wt, m):
    files = {}
    for path, anchor, repl in MUTANTS[m]:
        if path not in files:
            raw = open(wt + '/' + path, 'rb').read()
            files[path] = [b'\r\n' in raw, raw.decode('utf-8').replace('\r\n', '\n').split('\n')]
        lines = files[path][1]
        hits = [i for i, l in enumerate(lines) if l.strip() == anchor.strip()]
        if len(hits) != 1:
            print('ANCHOR', m, path, len(hits), anchor)
            return 1
        i = hits[0]
        ind = lines[i][:len(lines[i]) - len(lines[i].lstrip())]
        new = []
        for r in repl:
            if r == anchor:
                new.append(lines[i])
            elif r.startswith('\t') or r == '' or r.startswith('Libs::') or r.startswith('    ') or r == '}':
                new.append(r)
            else:
                new.append(ind + r)
        lines[i:i + 1] = new
        print('applied', m, path, 'line', i + 1, '->', len(new), 'lines')
    for path, (crlf, lines) in files.items():
        text = '\n'.join(lines)
        if crlf:
            text = text.replace('\n', '\r\n')
        open(wt + '/' + path, 'wb').write(text.encode('utf-8'))
    return 0


if __name__ == '__main__':
    if sys.argv[1] == 'apply':
        sys.exit(apply(sys.argv[2], sys.argv[3]))
