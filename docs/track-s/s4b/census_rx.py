#!/usr/bin/env python3
"""S4b (HPP-349, ROADMAP "SESSION 122" item 265 (v)(3)): census of the 13 RX_* expressions of a scorer sc_s.py on real logs.
For each expression: the LOGF reference at 4fc501f4 (RX_PCWOV: 2ce6326e - the S-pcw code is not in 4fc501f4), the form
(the line prefix the scorer dispatches on before applying the expression), the number of lines of that form in each log,
the number of those lines the expression matches (the way the scorer applies it: search / match), and the lines that
carry the form NOT at the start of the line (interleaved writes; the scorer does not read them - printed as data).
    python census_rx.py --scorer <sc_s.py> [--want-sha <sha256 of log 1>] <log> [<log> ...]
Output ASCII only."""
import argparse
import hashlib
import importlib.util
import sys

PC = 'src/graphics/host_gpu/renderer/pipeline/pipelineCache.cpp'
RD = 'src/graphics/host_gpu/renderer/renderDraw.cpp'
WN = 'src/graphics/presentation/window/window.cpp'
# name, reference, form prefix, extra condition on the line (None = none), apply ('search' / 'match')
TABLE = (
    ('RX_SKIP', '4fc501f4:%s:4439' % RD, b'AsyncPipelines: skipped draw', None, 'search'),
    ('RX_HASH', '4fc501f4:%s:6028 (ShaderRegister)' % PC, b'ShaderRegister:', None, 'search'),
    ('RX_HASH', '4fc501f4:%s:3516 (ShaderFirstUse)' % PC, b'ShaderFirstUse:', None, 'search'),
    ('RX_DSAVE', '4fc501f4:%s:4806 (PipelineCacheLog)' % PC, b'Vulkan pipeline cache: saved', None, 'search'),
    ('RX_RSAVE', '4fc501f4:%s:5963' % PC, b'PipelinePrecache: saved', None, 'search'),
    ('RX_QUEUED', '4fc501f4:%s:6425' % PC, b'PipelinePrecache: ', b' recipes -> ', 'search'),
    ('RX_CREATED', '4fc501f4:%s:6431' % PC, b'PipelinePrecache: all pipelines created', None, 'search'),
    ('RX_READY', '4fc501f4:%s:6050 (PipelineCacheLog)' % PC, b'ShaderPreparation: ready', None, 'search'),
    ('RX_WAITED', '4fc501f4:%s:1025' % WN, b'ShaderPreparation: startup wait finished', None, 'search'),
    ('RX_LOADED', '4fc501f4:%s:4647 (PipelineCacheLog)' % PC, b'Vulkan pipeline cache: loaded', None, 'search'),
    ('RX_SHADER', '4fc501f4:%s:3916' % PC, b'AvTrace: shader ', None, 'search'),
    ('RX_VSPS', '4fc501f4:%s:5356, :5394, :6312 (gfx; cs lines 5617/5675/5710/6384 carry no vs=)' % PC,
     b'AvTrace: pipeline gfx', None, 'search'),
    ('RX_PCWOV', '2ce6326e:%s:6252 (S5c; not in 4fc501f4)' % PC, b'AvTrace: pcw overlap ', None, 'search'),
    ('RX_QUEUED_ANY', '4fc501f4:%s:6425' % PC, b'PipelinePrecache: ', b' recipes -> ', 'match'),
)
SIBLINGS = (b'AvTrace: shader-cache', b'AvTrace: shader-spec', b'AvTrace: shader-emit')


def load(path):
    spec = importlib.util.spec_from_file_location('sc_s_census', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def census(S, log):
    rows = [dict(form=0, hit=0, inner=0, first=None) for _ in TABLE]
    sib = dict((p, [0, 0]) for p in SIBLINGS)       # lines of the form, of them matched by RX_SHADER
    h = hashlib.sha256()
    n = 0
    with open(log, 'rb') as f:
        for line in f:
            h.update(line)
            n += 1
            for k, (name, ref, pre, cond, how) in enumerate(TABLE):
                if line.startswith(pre) and (cond is None or cond in line):
                    rx = getattr(S, name)
                    m = rx.match(line) if how == 'match' else rx.search(line)
                    r = rows[k]
                    r['form'] += 1
                    r['hit'] += 1 if m else 0
                    if r['first'] is None:
                        r['first'] = n
                elif pre in line[1:] and (cond is None or cond in line):
                    rows[k]['inner'] += 1
            for p in SIBLINGS:
                if line.startswith(p):
                    sib[p][0] += 1
                    sib[p][1] += 1 if S.RX_SHADER.search(line) else 0
    return h.hexdigest(), n, rows, sib


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--scorer', required=True)
    ap.add_argument('--want-sha', default=None)
    ap.add_argument('logs', nargs='+')
    a = ap.parse_args(argv)
    sc_sha = hashlib.sha256(open(a.scorer, 'rb').read()).hexdigest()
    S = load(a.scorer)
    print('census_rx scorer %s sha256 %s' % (a.scorer, sc_sha))
    print('RX_SHADER pattern: %s' % S.RX_SHADER.pattern.decode('latin1'))
    ok = True
    for i, log in enumerate(a.logs):
        if i == 0 and a.want_sha:
            got = hashlib.sha256(open(log, 'rb').read()).hexdigest()
            print('log %s sha256 %s want %s: %s (checked before the census)' % (log, got, a.want_sha,
                                                                                 'OK' if got == a.want_sha else 'BAD'))
            if got != a.want_sha:
                return 1
        sha, n, rows, sib = census(S, log)
        print('== log %s sha256 %s lines %d' % (log, sha, n))
        for (name, ref, pre, cond, how), r in zip(TABLE, rows):
            print('  %-13s %s form "%s%s" (%s): lines of the form %d, matched %d%s, form not at line start %d%s' % (
                name, ref, pre.decode('latin1'), (' ... %s' % cond.decode('latin1')) if cond else '', how, r['form'],
                r['hit'], ' (first at line %d)' % r['first'] if r['first'] else '', r['inner'],
                '' if r['form'] == r['hit'] else '  <-- MISMATCH'))
            ok &= r['form'] == r['hit']
        for p, (c, m) in sib.items():
            print('  sibling form "%s": lines %d, matched by RX_SHADER %d (the scorer never applies RX_SHADER to them: '
                  'branch "AvTrace: shader " with a space)' % (p.decode('latin1'), c, m))
    print('CENSUS: %s' % ('every form line matched' if ok else 'MISMATCH'))
    return 0


if __name__ == '__main__':
    sys.exit(main())
