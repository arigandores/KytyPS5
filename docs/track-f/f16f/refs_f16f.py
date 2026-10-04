"""Track F link F16f (HPP-523): check of the <commit>:<path>:<line> references of the seal docs/track-f/f16f.md (general rule 24(1)): the line
starts with the anchor (after strip) and the next line starts with the +1 text ('' = an empty line).  ASCII output.  Ends with ALL OK."""
import subprocess, sys

REFS = [
    ('39fba40d', 'docs/ROADMAP.md', 22134, '(г) **Константы и правило чтения `KYTY_DIAG_F5`', 'bool`, `Common::EnvValueOn`: нет или пусто'),
    ('39fba40d', 'docs/ROADMAP.md', 22240, '(б) **В1 — набор ветвей B', '(в) **В2 — FMASK:**'),
    ('39fba40d', 'docs/ROADMAP.md', 22242, '(г) **В3 — положительный контроль', '(д) **В4 — имя:**'),
    ('39fba40d', 'docs/ROADMAP.md', 22245, '(ж) **Прочие RC — к F16d как есть:**', '(з) **Звенья:**'),
    ('39fba40d', 'docs/ROADMAP.md', 22309, '(в) **Константы и правило чтения `KYTY_DIAG_F6`', '(г) **Цепочка F16 дополняется'),
    ('39fba40d', 'docs/ROADMAP.md', 22527, '(б) **В-F16d-1 — `cmask_fce_layout` входит в B**', '(в) **В-F16d-2 — справкой'),
    ('39fba40d', 'docs/ROADMAP.md', 22610, '(г) **Правило чтения тождеств при согласованном снимке', '(д) **Звено F16e2'),
    ('39fba40d', 'docs/ROADMAP.md', 22679, '(а) **Приёмка строкой: F16d2 ✓**', '(б) **Пересчёт лида [c]**'),
    ('39fba40d', 'docs/ROADMAP.md', 22689, '482. **Звено F16e2 трека F', '(а) **Приёмка строкой. F16e2 ✓**'),
    ('a24bb060', 'docs/track-f/f16d2.md', 7, '## 1. Форма (а): где копия и печать', ''),
    ('56b04817', 'src/graphics/host_gpu/renderer/diagF5.cpp', 74,
     'bool PublishSet(bool on, DiagSet<CounterEnum>& set, uint32_t frame, uint64_t now_ms) {', 'if (!on) {'),
    ('56b04817', 'src/graphics/host_gpu/renderer/diagF5.cpp', 89,
     'bool ServiceSet(bool on, const char* tag, DiagSet<CounterEnum>& set, const char* const* names) {', 'if (!on) {'),
    ('56b04817', 'src/graphics/guest_gpu/graphicsRun.cpp', 705, 'const bool diag_f56 = DiagF5::On() || DiagF6::On();', ''),
]


def main():
    bad = 0
    for c, path, n, anchor, nxt in REFS:
        t = subprocess.run(['git', '-C', 'C:/kyty/KytyPS5', 'show', '%s:%s' % (c, path)], capture_output=True).stdout.decode('utf-8')
        lines = t.split('\n')
        a = lines[n - 1].strip() if n - 1 < len(lines) else None
        b = lines[n].strip() if n < len(lines) else None
        ok = a is not None and a.startswith(anchor) and (b == '' if nxt == '' else (b or '').startswith(nxt))
        bad += not ok
        print('%s %s:%s:%d' % ('OK  ' if ok else 'FAIL', c, path, n))
    print('refs %d, failed %d' % (len(REFS), bad))
    print('ALL OK' if bad == 0 else 'NOT OK')
    return 0 if bad == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
