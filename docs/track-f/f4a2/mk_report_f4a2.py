# F4a2: fix references in the report body, append the build-tree diff, write docs/track-f/f4a2.md (LF).
import hashlib
O = 'C:/kyty/f287/f4a2/'
s = open(O + 'f4a2_body.md', 'rb').read().decode('utf-8').replace('\r', '')
fixes = [
    ('(`vulkanWindow.cpp:699`, `features12.uniformBufferStandardLayout =\nsupported`; F4a и рабочие логи — `Vulkan uniformBufferStandardLayout: enabled`)',
     '(`65a09c82:src/graphics/presentation/window/vulkanWindow.cpp:702`, `features12.uniformBufferStandardLayout =\nsupported`; рабочий лог, напр. `C:/kyty/s143/log_v143_01.txt`, — `Vulkan uniformBufferStandardLayout: enabled`)'),
    ('`EXIT_IF`/`EXIT_NOT_IMPLEMENTED` (`:638`, `:651`, `:739`, `:741` и др.) завершают\n  процесс.',
     '`EXIT_IF`/`EXIT_NOT_IMPLEMENTED` после создания (`:620`, `:639`, `:652`, `:654`, `:719`, `:740`, `:742`)\n  завершают процесс.'),
    ('(`retired_sources`, комментарий `:3797`)', '(`retired_sources`, `pipelineCache.cpp:3792`, `:3798`)'),
    ('Время на приведение — 06:41Z…06:43Z.', 'Время на приведение — 06:41:18Z…06:42:39Z (`times.txt`).'),
]
for a, b in fixes:
    assert s.count(a) == 1, a[:50]
    s = s.replace(a, b)
patch = open(O + 'wt_diff_ignorecr.patch', 'rb').read().decode('utf-8')
assert chr(13) not in patch
s += ('\n## Приложение. Разность дерева сборки против `4fc501f4` по `src/` без учёта CR (`git -C C:/kyty/f287/f4a2/wt diff --ignore-cr-at-eol 4fc501f4 -- src`,\n'
      'sha256 `' + hashlib.sha256(patch.encode('utf-8')).hexdigest() + '`)\n\n```diff\n' + patch + '```\n')
open('C:/kyty/KytyPS5/docs/track-f/f4a2.md', 'wb').write(s.encode('utf-8'))
print('report lines', s.count('\n'))
