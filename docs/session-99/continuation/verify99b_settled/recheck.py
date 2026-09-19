"""Only the two initial findings; actual synthetic pipeline, no mock replay."""
import copy,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.dont_write_bytecode=True
sys.path.insert(0,'C:/kyty/s99')
import settled99 as S
import test_settled99 as T
HERE=Path(__file__).resolve().parent
tempfile.tempdir=str(HERE)
checks={}
with tempfile.TemporaryDirectory(prefix='recheck_') as temp:
    root=Path(temp)
    (root/'gates_base.txt').write_bytes((S.ROOT/'gates_base.txt').read_bytes())
    m=T.metadata();m['prereg']['sha256']=S.PRED_SHA
    rows,arms=T.fixture();T.write_fixture(root,m,rows,arms)
    with patch.object(S,'ROOT',root):
        pilot=S.evaluate('eng99a1',root)
        checks['baseline_pilot_LOCK']=pilot['status']=='ENGINEERING_COMPLETE' and pilot['decision']['action']=='LOCK'
        fields=pilot['reported_old_area_controls']
        checks['old_three_area_controls_preserved']=len(fields)==3
        checks['old_WORK_FAIL_preserved']=any('[FAIL]' in line and 'work within' in line for line in fields)
        checks['old_area_INVALID_preserved']=pilot['reported_old_area_verdict']=='INVALID'
        checks['pilot_no_endpoint']='endpoints' not in pilot
        source=root/'source.json';source.write_text(json.dumps(pilot),encoding='utf8')
        confirm=T.metadata(tag='bf99e',hold=900);confirm['prereg']['sha256']=S.PRED_SHA
        confirm['env'].update(KYTY_SETTLED_SOURCE_TAG='eng99a1',KYTY_SETTLED_SOURCE_SHA256=S.sha(source))
        checks['untampered_source_roundtrip_pass']=not S.source_check(source,root,confirm,'a','measurement',None,20000)[1]
        wrong=copy.deepcopy(pilot);wrong['selection']['row_ranges']={'4':[1,29]}
        source.write_text(json.dumps(wrong),encoding='utf8');confirm['env']['KYTY_SETTLED_SOURCE_SHA256']=S.sha(source)
        errors=S.source_check(source,root,confirm,'a','measurement',None,20000)[1]
        checks['original_mutation_now_rejected']='source selection does not reproduce from raw under this sealed rule' in errors
with (HERE/'relevant_tests_final.txt').open('w',encoding='utf8') as out:
    suite=unittest.defaultTestLoader.loadTestsFromNames([
        'test_settled99.ControlFlowTests.test_frozen_source_requires_launch_pin_exact_budget_and_raw_replay',
        'test_settled99.ControlFlowTests.test_full_pilot_pipeline_with_real_old_helpers_is_mechanics_only'])
    result=unittest.TextTestRunner(stream=out,verbosity=2).run(suite)
checks['relevant_author_tests_pass']=result.wasSuccessful() and result.testsRun==2
(HERE/'recheck_results.json').write_text(json.dumps(checks,indent=2)+'\n',encoding='utf8')
print(json.dumps(checks,indent=2))
sys.exit(0 if all(checks.values()) else 1)
