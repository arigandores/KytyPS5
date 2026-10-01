"""refs144.py - Red Team s144 step 1 (HPP-331): the map of every <commit>:<path>:<line> reference of review144.md (general
rule 24(1)): the anchor must be a substring of the target line; the same reference +1 must NOT carry it (positive control).
Also: the git copies of the sealed files at 919f43e0 equal the sealed sha256 (so the line numbers of the copies are the
line numbers of the sealed files).  Read only; prints ASCII; the last line ALL OK or NOT OK."""
import hashlib
import subprocess
import sys

REPO = 'C:/kyty/KytyPS5'
PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
SC = 'docs/session-144/step0/sc144.py'
GO = 'docs/session-144/step0/go144a.sh'
ES = 'docs/session-144/step0/enter_scene.py'
RM = 'docs/ROADMAP.md'
REFS = [
    ('4fc501f4', PC, 436, 'Log::WriteToConsoleAndLog(message);'),
    ('4fc501f4', PC, 5848, "return value == nullptr || value[0] != '0';"),
    ('4fc501f4', PC, 6066, 'PipelineCacheLog("ShaderSeed: compatibility={}", compatibility);'),
    ('4fc501f4', PC, 6145, 'InstallShaderSeed();'),
    ('4fc501f4', PC, 6148, 'LOGF("PipelinePrecache: no %s yet'),
    ('4fc501f4', PC, 6199, 'stale recipes (signature mismatch), ignored'),
    ('4fc501f4', PC, 6425, 'LOGF("PipelinePrecache: %u recipes -> %u graphics + %u compute pipelines queued'),
    ('919f43e0', SC, 232, "RX_PRECACHE = re.compile(rb'PipelinePrecache: \\d+ recipes ->')"),
    ('919f43e0', SC, 610, "add('W form: KYTY_PIPELINE_PRECACHE=0 in the env (item 254 (e))', pc == '0', pc)"),
    ('919f43e0', SC, 654, "r['admit'].append(('W form: no \"PipelinePrecache: N recipes ->\" line in the log (item 254 (e))', pl == 0,"),
    ('919f43e0', SC, 657, "r['admit'].append(('V positive control: >= 1 \"PipelinePrecache: N recipes ->\" line in the log (item 254 (e))',"),
    ('919f43e0', SC, 697, 'got = m.group(1)'),
    ('919f43e0', SC, 765, "key = ms[0]['kind'] if ms else ('attempt:%s' % r.get('attempt_outcome'))"),
    ('919f43e0', SC, 914, '    return None'),
    ('919f43e0', SC, 1025, "o.append('  K3 entry window (no warm base): %s' % (d['k3w'] or 'none'))"),
    ('919f43e0', SC, 1115, 'def summary(root, pred_sha, sheet, sheet_tags=None):'),
    ('919f43e0', SC, 1175, "adm = [e for e in made if all(a[1] for a in e['admit'])]"),
    ('919f43e0', SC, 1197, "out.append('FORM B5a (a frame dt >= 1 s after the first scene frame): %d/%d [c] (admitted and entered %d)'"),
    ('919f43e0', SC, 1465, 'if a.check_seal:'),
    ('919f43e0', GO, 225, 'if ! python $ROOT/$SC --check-seal >> $L 2>&1; then'),
    ('919f43e0', GO, 251, 'CMB=$(python $ROOT/cachemf144.py $OUT/cache_$T.before.json 2>&1 | tail -1 | tr -d'),
    ('919f43e0', ES, 420, 'game = subprocess.Popen(args, cwd=EMU, env=env, stdout=stdout, stderr=subprocess.STDOUT,'),
    ('919f43e0', ES, 712, "env={k: v for k, v in env.items() if k.startswith(('KYTY_', 'VK_'))},"),
    ('de2c87af', RM, 13407, 'скорер проверяет её положительным контролем: в логе W нет строки `PipelinePrecache: N recipes ->`, в логе V той же серии она есть;'),
    ('de2c87af', RM, 13414, 'sha логов сверяются со строками `times.txt` их сессий.'),
    ('de2c87af', RM, 13455, 'строка карты печатается с пометкой «повторный вход», формы Б5/Б5а/Б33'),
    ('de2c87af', RM, 13459, 'два подряд W с одним маркером остановки до первой строки `GuestOut` — стоп;'),
    ('de2c87af', RM, 13467, 'цена ошибки формы — стоп после одного тега.'),
    ('de2c87af', RM, 13587, '(д) **Правило печати (новое, для всех треков):** член печати, которого нет в пункте `ROADMAP.md`, называемом печатью, печатается отдельной'),
    ('de2c87af', RM, 13899, '264. **Приёмка шага 0 с. 144 (`HPP-330`, Harness Engineer) лидом: Принято;'),
    ('d4be1c33', RM, 13930, '265. **Звено S4 трека S (`HPP-315`, вопрос `HPP-348`): дефект запечатанного скорера `sc_s.py`'),
]
SEALED = [(SC, 'C:/kyty/s144/sc144.py'), (GO, 'C:/kyty/s144/go144a.sh'), (ES, 'C:/kyty/s144/enter_scene.py')]


def show(commit, path):
    p = subprocess.run(['git', '-C', REPO, 'show', '%s:%s' % (commit, path)], capture_output=True)
    if p.returncode != 0:
        return None
    return p.stdout


def main():
    ok = True
    cache = {}
    for commit, path, line, anchor in REFS:
        key = (commit, path)
        if key not in cache:
            raw = show(commit, path)
            cache[key] = None if raw is None else raw.decode('utf-8', 'replace').replace(chr(13), '').split(chr(10))
        lines = cache[key]
        if lines is None:
            print('NOT OK %s:%s:%d - no such file at the commit' % (commit, path, line))
            ok = False
            continue
        hit = line - 1 < len(lines) and anchor in lines[line - 1]
        ctrl = line < len(lines) and anchor in lines[line]
        good = hit and not ctrl
        ok &= good
        print('%s %s:%s:%d anchor %s; control +1 %s' % ('OK    ' if good else 'NOT OK', commit, path, line,
                                                         'found' if hit else 'MISSING', 'NOT OK (as required)' if not ctrl else 'FOUND (bad)'))
    for path, live in SEALED:
        raw = show('919f43e0', path)
        a = hashlib.sha256(raw).hexdigest() if raw is not None else None
        b = hashlib.sha256(open(live, 'rb').read()).hexdigest()
        same = a == b
        ok &= same
        print('%s git copy 919f43e0:%s sha256 %s = sealed %s sha256 %s' % ('OK    ' if same else 'NOT OK', path, a, live, b))
    print('refs %d, sealed copies %d' % (len(REFS), len(SEALED)))
    print('ALL OK' if ok else 'NOT OK')
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
