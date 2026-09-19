"""Focused independent sealed-rule cases; synthetic artifacts only in this directory."""
import copy
import json
from pathlib import Path
import sys
import tempfile
from unittest.mock import patch
sys.dont_write_bytecode = True
sys.path.insert(0, 'C:/kyty/s99')
import settled99 as S
import test_settled99 as T

HERE = Path(__file__).resolve().parent
tempfile.tempdir = str(HERE)
report = {}
rows, arms = T.fixture(blocks=82)
chosen = S.select(rows, arms)
report['fixed_exact_geometry'] = chosen['pairs'] == [(b, b+1) for b in range(4,80,2)] and chosen['blocks'] == {b:list(range(1861+90*b,1890+90*b)) for b in range(4,80)}
rows2 = copy.deepcopy(rows)
for n in range(1801+30*90,1891+30*90): del rows2[n]
report['whole_internal_block_fails'] = not all(S.analyze(rows2,arms,'a','pilot')['technical'].values())
for key,value in [('arm',1),('blk',7)]:
    r = copy.deepcopy(rows); r[1801][key]=value
    report['early_identity_'+key] = not S.analyze(r,arms,'a','pilot')['technical']['FULL_ROW_IDENTITY']
r = copy.deepcopy(rows); r[1802]['bf_burn_cpu_ns']=1
report['early_cpu_dark_fails'] = not S.analyze(r,arms,'a','pilot')['technical']['CPU_DARK_STRUCTURE']
r = copy.deepcopy(rows); del r[1802]['bf_burn_probe_ns']
report['early_missing_fails'] = not S.analyze(r,arms,'a','pilot')['technical']['FULL_SCHEMA']

with tempfile.TemporaryDirectory(prefix='independent_source_') as temp:
    root=Path(temp)
    (root/'gates_base.txt').write_bytes((S.ROOT/'gates_base.txt').read_bytes())
    m=T.metadata(); m['prereg']['sha256']=S.PRED_SHA
    rows,arms=T.fixture()
    T.write_fixture(root,m,rows,arms)
    with patch.object(S,'ROOT',root):
        pilot=S.evaluate('eng99a1',root)
        report['synthetic_real_pipeline_engineering_lock'] = pilot['status']=='ENGINEERING_COMPLETE' and pilot['decision']['action']=='LOCK' and 'endpoints' not in pilot
        source=root/'source.json'; source.write_text(json.dumps(pilot),encoding='utf8')
        confirm=T.metadata(tag='bf99e',hold=900); confirm['prereg']['sha256']=S.PRED_SHA
        confirm['env'].update(KYTY_SETTLED_SOURCE_TAG='eng99a1',KYTY_SETTLED_SOURCE_SHA256=S.sha(source))
        report['source_real_replay_pass'] = not S.source_check(source,root,confirm,'a','measurement',None,20000)[1]
        corrupted=copy.deepcopy(pilot)
        corrupted['selection']['row_ranges']={'4':[1,29]}
        source.write_text(json.dumps(corrupted),encoding='utf8')
        confirm['env']['KYTY_SETTLED_SOURCE_SHA256']=S.sha(source)
        _,errors=S.source_check(source,root,confirm,'a','measurement',None,20000)
        report['source_changed_selection_rejected']=bool(errors)
        report['source_changed_selection_errors']=errors
        source.write_text(json.dumps(pilot),encoding='utf8')
        confirm['env']['KYTY_SETTLED_SOURCE_SHA256']=S.sha(source)
        with (root/'stdout_eng99a1.txt').open('ab') as f:f.write(b'changed bytes\n')
        report['changed_source_raw_hash_rejected']=bool(S.source_check(source,root,confirm,'a','measurement',None,20000)[1])

report['cpu_not_wall'] = S.analyze(rows,arms,'a','measurement')['endpoints']['B_cpu_ms']==22 and S.analyze(rows,arms,'a','measurement')['endpoints']['B_wall_compatibility_ms']==18
report['negative_round_ties_away'] = S.recommendation(20000,{'dt_delta_us':-1050,'dt_relative':.02},{},1)['next_burn']==18900
report['pilot_never_B']= 'endpoints' not in S.analyze(rows,arms,'a','pilot')
report['combine_keeps_global']=S.combine({'status':'ADMITTED_SETTLED_MEASUREMENT','instrument':'a','endpoints':{'B_cpu_ms':16}}, {'status':'ADMITTED_SETTLED_MEASUREMENT','instrument':'c','endpoints':{'B_cpu_ms':16}})['global_M3'].startswith('GAP unchanged')
print(json.dumps(report,indent=2))
(HERE/'independent_results.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
