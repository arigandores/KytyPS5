"""F20l3 (HPP-655): check of the references <commit>:<path>:<line> of the seal 3 and the report - the anchor is in the line, the +1 text is
in the next line (general rule 24(1)).  usage: python refs_f20l3.py   (ASCII only output; ends with ALL OK)"""
import subprocess
import sys

GIT = 'C:/Program Files/Git/cmd/git.exe'
REPO = 'C:/kyty/KytyPS5'
REFS = [
    ('5da67c7e', 'docs/ROADMAP.md', 23545, '591. **\u0417\u0432\u0435\u043d\u043e F20m2 \u0442\u0440\u0435\u043a\u0430 F (`HPP-649`, \u043b\u0438\u0434): \u0447\u0442\u0435\u043d\u0438\u0435 \u043f\u043e\u0432\u0442\u043e\u0440\u0430 \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u0435\u0439 F20l2', '(\u0430) **\u0427\u0442\u0435\u043d\u0438\u0435 \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u0435\u0439 (\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043b\u0438\u0434\u0430'),
    ('5da67c7e', 'docs/ROADMAP.md', 23548, '(\u0432) **\u041f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043f. 550(\u0434)(7) \u0438 574(\u0431)(7) (\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043b\u0438\u0434\u0430, \u0434\u043e \u0442\u0435\u0433\u043e\u0432).**', '(\u0433) **\u0421\u0435\u0440\u0438\u044f \u043f. 550(\u0435) \u2014 \u043d\u0430\u0437\u043d\u0430\u0447\u0430\u0435\u0442\u0441\u044f (\u043f\u0440\u0438 \u041f\u041a-A \u2713).**'),
    ('5da67c7e', 'docs/ROADMAP.md', 23549, '(\u0433) **\u0421\u0435\u0440\u0438\u044f \u043f. 550(\u0435) \u2014 \u043d\u0430\u0437\u043d\u0430\u0447\u0430\u0435\u0442\u0441\u044f (\u043f\u0440\u0438 \u041f\u041a-A \u2713).**', '(\u0434) **\u04235(1) \u0438 \u0441\u0434\u0432\u0438\u0433 \u0431\u0430\u0437\u044b (\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043b\u0438\u0434\u0430, \u0434\u043e \u0434\u0430\u043d\u043d\u044b\u0445).**'),
    ('5da67c7e', 'docs/ROADMAP.md', 23550, '(\u0434) **\u04235(1) \u0438 \u0441\u0434\u0432\u0438\u0433 \u0431\u0430\u0437\u044b (\u0440\u0435\u0448\u0435\u043d\u0438\u0435 \u043b\u0438\u0434\u0430, \u0434\u043e \u0434\u0430\u043d\u043d\u044b\u0445).**', '(\u0435) **\u041d\u0430\u0431\u043b\u044e\u0434\u0435\u043d\u0438\u0435 `b32_z0b`'),
    ('5da67c7e', 'docs/ROADMAP.md', 23222, '(\u0434) **\u041a\u043e\u043d\u0442\u0440\u043e\u043b\u0438 (F20l, \u0442\u0435\u0433\u0438 \u0434\u043e \u0441\u0435\u0440\u0438\u0438; \u0447\u0442\u0435\u043d\u0438\u0435 \u2014 F20m).**', '(\u0435) **\u0421\u0435\u0440\u0438\u044f \u0438 \u0431\u044e\u0434\u0436\u0435\u0442 (\u043d\u0430\u0437\u043d\u0430\u0447\u0430\u0435\u0442 F20m \u043f\u043e\u0441\u043b\u0435 \u0447\u0442\u0435\u043d\u0438\u044f \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u0435\u0439).**'),
    ('5da67c7e', 'docs/ROADMAP.md', 23223, '(\u0435) **\u0421\u0435\u0440\u0438\u044f \u0438 \u0431\u044e\u0434\u0436\u0435\u0442 (\u043d\u0430\u0437\u043d\u0430\u0447\u0430\u0435\u0442 F20m \u043f\u043e\u0441\u043b\u0435 \u0447\u0442\u0435\u043d\u0438\u044f \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u0435\u0439).**', '(\u0436) **\u0423\u0431\u0438\u0439\u0441\u0442\u0432\u043e \u043c\u0430\u0440\u0448\u0440\u0443\u0442\u0430 \xab\u0430\u0442\u0440\u0438\u0431\u0443\u0446\u0438\u044f \u041132 \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u043e\u043c\xbb.**'),
    ('5da67c7e', 'docs/ROADMAP.md', 23224, '(\u0436) **\u0423\u0431\u0438\u0439\u0441\u0442\u0432\u043e \u043c\u0430\u0440\u0448\u0440\u0443\u0442\u0430 \xab\u0430\u0442\u0440\u0438\u0431\u0443\u0446\u0438\u044f \u041132 \u0438\u043d\u0441\u0442\u0440\u0443\u043c\u0435\u043d\u0442\u043e\u043c\xbb.**', '(\u0437) **\u0417\u0432\u0435\u043d\u044c\u044f (\u0441\u0442\u0430\u0434\u0438\u044f review \u043b\u0438\u0434\u0430 \u0443 \u0437\u0432\u0435\u043d\u0430 \u0438\u0441\u043f\u043e\u043b\u043d\u0438\u0442\u0435\u043b\u044f).**'),
    ('5da67c7e', 'docs/ROADMAP.md', 23264, '(\u0431) **\u041f\u0440\u0430\u0432\u0438\u043b\u043e \u04235(1) (\u0437\u0430\u043c\u0435\u043d\u044f\u0435\u0442 \u043f\u0435\u0440\u0432\u044b\u0439 \u0447\u043b\u0435\u043d \u04235 \u043f. 550(\u0436)', '(\u0432) **\u0412\u043e\u043f\u0440\u043e\u0441 1.**'),
    ('5da67c7e', 'docs/ROADMAP.md', 23428, '(\u0434) **\u041f\u043e\u043f\u0440\u0430\u0432\u043a\u0430 \u043f\u0440\u0430\u0432\u0438\u043b\u0430 \u0447\u0442\u0435\u043d\u0438\u044f \u043f. 550(\u0433)(2)(iv)', '(\u0435) **\u041f\u043e\u0432\u0442\u043e\u0440 \u043a\u043e\u043d\u0442\u0440\u043e\u043b\u0435\u0439 \u2014 F20l2'),
    ('5da67c7e', 'docs/ROADMAP.md', 23538, '590. **\u0417\u0432\u0435\u043d\u043e S18d \u0442\u0440\u0435\u043a\u0430 S (`HPP-645`, \u043b\u0438\u0434): \u0444\u0430\u043a\u0442 \u043f. 588(\u0433)', '(\u0430) **\u0423\u0441\u0442\u0430\u043d\u043e\u0432\u043a\u0430 \u043f\u043e \u0448\u0430\u0433\u0430\u043c \u043f. 588(\u0433)(i)\u2013(vi)**'),
    ('302347b4', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 6424, 'PipelineCacheLog("ShaderSeed: compatibility={}", compatibility);', 'if (const char* value = std::getenv("KYTY_SHADER_SEED")'),
    ('302347b4', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 6450, 'if (recipes_match(cache.Directory() / "pipelines.bin")) return;', 'if (!recipes_match(seed / "pipelines.bin")) {'),
    ('302347b4', 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp', 6506, 'LOGF("PipelinePrecache: no %s yet', 'return;'),
    ('302347b4', 'src/graphics/host_gpu/renderer/pipeline/shaderTranslationCache.cpp', 589, 'if (!variant.empty()) {', 'std::string folder = "variant" + variant;'),
]
ok = True
print('suite refs_f20l3.py refs %d' % len(REFS))
for c, p, ln, a, b in REFS:
    t = subprocess.run([GIT, '-C', REPO, 'show', '%s:%s' % (c, p)], capture_output=True).stdout.decode('utf-8').split('\n')
    good = len(t) > ln and a in t[ln - 1] and b in t[ln]
    ok &= good
    print('%s %s:%s:%d' % ('ok' if good else 'BAD', c, p, ln))
print('refs %d' % len(REFS))
print('ALL OK' if ok else 'FAILED')
sys.exit(0 if ok else 1)
