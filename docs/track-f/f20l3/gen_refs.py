import os
S = os.environ['PAPERCLIP_RUN_SCRATCH_DIR']
R = [('5da67c7e', 'docs/ROADMAP.md', 23545, '591. **Звено F20m2 трека F (`HPP-649`, лид): чтение повтора контролей F20l2', '(а) **Чтение контролей (решение лида'),
     ('5da67c7e', 'docs/ROADMAP.md', 23548, '(в) **Поправка п. 550(д)(7) и 574(б)(7) (решение лида, до тегов).**', '(г) **Серия п. 550(е) — назначается (при ПК-A ✓).**'),
     ('5da67c7e', 'docs/ROADMAP.md', 23549, '(г) **Серия п. 550(е) — назначается (при ПК-A ✓).**', '(д) **У5(1) и сдвиг базы (решение лида, до данных).**'),
     ('5da67c7e', 'docs/ROADMAP.md', 23550, '(д) **У5(1) и сдвиг базы (решение лида, до данных).**', '(е) **Наблюдение `b32_z0b`'),
     ('5da67c7e', 'docs/ROADMAP.md', 23222, '(д) **Контроли (F20l, теги до серии; чтение — F20m).**', '(е) **Серия и бюджет (назначает F20m после чтения контролей).**'),
     ('5da67c7e', 'docs/ROADMAP.md', 23223, '(е) **Серия и бюджет (назначает F20m после чтения контролей).**', '(ж) **Убийство маршрута «атрибуция Б32 инструментом».**'),
     ('5da67c7e', 'docs/ROADMAP.md', 23224, '(ж) **Убийство маршрута «атрибуция Б32 инструментом».**', '(з) **Звенья (стадия review лида у звена исполнителя).**'),
     ('5da67c7e', 'docs/ROADMAP.md', 23264, '(б) **Правило У5(1) (заменяет первый член У5 п. 550(ж)', '(в) **Вопрос 1.**'),
     ('5da67c7e', 'docs/ROADMAP.md', 23428, '(д) **Поправка правила чтения п. 550(г)(2)(iv)', '(е) **Повтор контролей — F20l2'),
     ('5da67c7e', 'docs/ROADMAP.md', 23538, '590. **Звено S18d трека S (`HPP-645`, лид): факт п. 588(г)', '(а) **Установка по шагам п. 588(г)(i)–(vi)**'),
     ('302347b4', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 6424, 'PipelineCacheLog("ShaderSeed: compatibility={}", compatibility);',
      'if (const char* value = std::getenv("KYTY_SHADER_SEED")'),
     ('302347b4', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 6450, 'if (recipes_match(cache.Directory() / "pipelines.bin")) return;',
      'if (!recipes_match(seed / "pipelines.bin")) {'),
     ('302347b4', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 6506, 'LOGF("PipelinePrecache: no %s yet', 'return;'),
     ('302347b4', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 589, 'if (!variant.empty()) {',
      'std::string folder = "variant" + variant;'),
     ]
NL = chr(92) + 'n'
body = ('"""F20l3 (HPP-655): check of the references <commit>:<path>:<line> of the seal 3 and the report - the anchor is in the line, the +1 text is\n'
        'in the next line (general rule 24(1)).  usage: python refs_f20l3.py   (ASCII only output; ends with ALL OK)"""\n'
        'import subprocess\nimport sys\n\nGIT = \'C:/Program Files/Git/cmd/git.exe\'\nREPO = \'C:/kyty/KytyPS5\'\nREFS = [\n' +
        ''.join('    (%s, %s, %d, %s, %s),\n' % (ascii(c), ascii(p), l, ascii(a), ascii(b)) for c, p, l, a, b in R) +
        ']\nok = True\nprint(\'suite refs_f20l3.py refs %d\' % len(REFS))\nfor c, p, ln, a, b in REFS:\n'
        '    t = subprocess.run([GIT, \'-C\', REPO, \'show\', \'%s:%s\' % (c, p)], capture_output=True).stdout.decode(\'utf-8\').split(\'' + NL + '\')\n'
        '    good = len(t) > ln and a in t[ln - 1] and b in t[ln]\n    ok &= good\n'
        '    print(\'%s %s:%s:%d\' % (\'ok\' if good else \'BAD\', c, p, ln))\n'
        'print(\'refs %d\' % len(REFS))\nprint(\'ALL OK\' if ok else \'FAILED\')\nsys.exit(0 if ok else 1)\n')
open(S + '/refs_f20l3.py', 'wb').write(body.encode('ascii'))
print('ok')
