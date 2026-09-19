"""Focused independent mutations against actual scorer; no game/build/source mutation."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import shutil
import sys
import tempfile
from unittest.mock import patch

sys.path.insert(0, 'C:/kyty/s99')
import settled99_gc as S
import test_settled99_gc as T

OUT = Path(__file__).parent
frozen = OUT / 'frozen'
frozen.mkdir(exist_ok=True)
hashes = {}
for p in (S.PRED, Path(S.__file__), Path(T.__file__), Path('C:/kyty/s99/settled99.py')):
    data = p.read_bytes()
    hashes[str(p)] = {'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()}
    (frozen / p.name).write_bytes(data)
(OUT / 'frozen_hashes.json').write_text(json.dumps(hashes, indent=2)+'\n')
# Reconstruct the exact originally reviewed scorer by reversing only root's fix;
# hash asserts byte-for-byte identity before executing that retained failed version.
original_scorer = Path(S.__file__).read_bytes().replace(
    b"('igc', rb'^BindFloorGcAudit: mode\\s*(\\d+)\\b')",
    b"('igc', rb'^BindFloorGcAudit: mode (\\d+)')")
assert hashlib.sha256(original_scorer).hexdigest() == '6d242596de76023c1dbdcab9a58bfbe5ed690ce340734e972b6115aa60c2f804'
old_path = frozen/'settled99_gc_original_failed.py'
old_path.write_bytes(original_scorer)
spec = importlib.util.spec_from_file_location('independent_original_gc_scorer', old_path)
previous_scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(previous_scorer)

results = []
def note(name, assertion, detail=None):
    assert assertion, name
    results.append(dict(name=name, expected_observed=True, detail=detail))

rows, arms = T.fixture()
base = S.analyze(rows, arms, 'a', 'pilot')
note('baseline technical/strict', all(base['technical'].values()) and all(base['strict'].values()))
for key in ('bf_igc_bad', 'bf_igc_critical', 'bf_igc_evict'):
    altered = copy.deepcopy(rows)
    altered[1813][key] = 1
    assert 1813 not in base['selection']['rows']
    got = S.analyze(altered, arms, 'a', 'pilot')
    note(key+' before selected window, zero births', not got['technical'][key.upper()+'_ZERO'])
for key in S.IGC:
    altered = copy.deepcopy(rows)
    del altered[1813][key]
    note('missing '+key+' early', not S.analyze(altered, arms, 'a', 'pilot')['technical']['FULL_SCHEMA'])
    altered = copy.deepcopy(rows)
    altered[1813][key] = -1
    note('negative '+key+' early', not S.analyze(altered, arms, 'a', 'pilot')['technical']['IGC_NONNEGATIVE'])
altered = copy.deepcopy(rows)
for row in altered.values():
    row['bf_igc_checks'] = 0
note('no checks rejects', not S.analyze(altered, arms, 'a', 'pilot')['technical']['IGC_CHECKS_POSITIVE'])
altered = copy.deepcopy(rows)
block = next(b for b in base['selection']['blocks'] if arms[b])
for n in base['selection']['blocks'][block]:
    altered[n]['bf_igc_hold'] = 0
note('one retained armed block without hold rejects', not S.analyze(altered, arms, 'a', 'pilot')['technical']['IGC_HOLD_EACH_ARMED_BLOCK'])

for tag in ('eng99a1', 'eng99a2', 'eng99a3', 'eng99a3_entry1', 'eng99a3_entry2'):
    try:
        S.identity(tag)
    except ValueError:
        note('old tag rejected '+tag, True)
    else:
        note('old tag rejected '+tag, False)
for inst, ordinal in [('a',4), ('c',1)]:
    note('fresh reset '+inst, S.source_check(None, S.ROOT, {}, inst, 'pilot', ordinal, 17800)[1] == [])
    note('fresh reset old-source rejected '+inst, bool(S.source_check(Path('eng99a3_result.json'), S.ROOT, {}, inst, 'pilot', ordinal, 17800)[1]))

with tempfile.TemporaryDirectory(prefix='independent_gc99_') as tmp:
    root = Path(tmp)
    meta = T.metadata()
    meta['prereg']['sha256'] = S.PRED_SHA
    altered = copy.deepcopy(rows)
    for row in altered.values():
        if not row['arm']:
            row['img_new'] = 40
    log, stdout = T.write_fixture(root, meta, altered, arms)
    result = S.evaluate('eng99a4', root, mechanics=True)
    note('high birth technical and strict pass', all(result['technical'].values()) and all(result['strict'].values()))
    note('old image proxy FAILs stay visible', result['reported_image_birth_proxies'] == {'R6': False, "R6'": False}
         and 'FAIL' in result['reported_full_reversibility'])
    note('buffer R7 still deciding', 'R7' in result['technical'] and "R7'" in result['technical'])
    note('high birth mechanics LOCK no admitted result', result['decision']['action'] == 'LOCK' and result['status'] == 'NOT_MEASUREMENT')
    (OUT/'high_birth_mechanics.json').write_text(json.dumps(result, indent=2)+'\n')

    original = log.read_bytes()
    source = Path('C:/kyty/KytyPS5/src/graphics/host_gpu/renderer/cache/textureCache.cpp').read_text()
    fmt = re.search(r'LOGF\("(BindFloorGcAudit: [^"\n]+)"', source)[1]
    actual = fmt.replace('%u', '1').replace('\\n', '\n').encode()
    note('C++ emits no-space marker', actual == b'BindFloorGcAudit: mode1\n', repr(actual))
    log.write_bytes(re.sub(rb'BindFloorGcAudit: mode\s*1\n', lambda _: actual, original))
    got = previous_scorer.protocol(meta, log, stdout, 'a', 'pilot')
    note('ORIGINAL DEFECT valid actual marker rejected', got['errors'] == ['log mode/pin evidence missing/wrong'], got['errors'])
    (OUT/'actual_marker_protocol_failure.json').write_text(json.dumps(got, indent=2)+'\n')
    got = S.protocol(meta, log, stdout, 'a', 'pilot')
    note('FIX actual C++ marker accepted', got['errors'] == [], got['errors'])
    (OUT/'actual_marker_protocol_fixed.json').write_text(json.dumps(got, indent=2)+'\n')
    log.write_bytes(original)
    for mutate in ('missing_env', 'wrong_env', 'lifetime_env_zero'):
        m = copy.deepcopy(meta)
        if mutate == 'missing_env': m['env'].pop('KYTY_BIND_FLOOR_GC_AUDIT')
        if mutate == 'wrong_env': m['env']['KYTY_BIND_FLOOR_GC_AUDIT'] = '0'
        if mutate == 'lifetime_env_zero': m['env']['KYTY_IMAGE_LIFETIME_TRACE'] = '0'
        got = S.protocol(m, log, stdout, 'a', 'pilot')
        note(mutate+' rejected', bool(got['errors']))

    for key in ('bf_igc_bad', 'bf_igc_critical', 'bf_igc_evict', 'buf_new'):
        changed = copy.deepcopy(rows)
        if key == 'buf_new':
            for row in changed.values():
                if not row['arm']: row['buf_new'] = 40
        else:
            changed[1813][key] = 1
        T.write_fixture(root, meta, changed, arms)
        got = S.evaluate('eng99a4', root, mechanics=True)
        note('full pipeline rejects '+key+' with zero image births', got['decision']['action'] == 'INVESTIGATE')
        if key == 'buf_new':
            note('R7/R7prime violations remain decisive', not got['technical']['R7'] and not got['technical']["R7'"])

(OUT/'independent_results.json').write_text(json.dumps(dict(verdict='PASS after root runtime-marker fix; original defect retained', cases=results), indent=2)+'\n')
print(f'{len(results)} expected outcomes confirmed; original integration defect reproduced and fixed version passes.')
