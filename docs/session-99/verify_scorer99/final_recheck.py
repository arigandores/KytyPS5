import sys, json, copy, hashlib, contextlib, io
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, 'C:/kyty/s99')
import bf99 as B
import test99_scorers as T

ROOT = Path(__file__).resolve().parent / 'final_recheck'
ROOT.mkdir(exist_ok=True)
results=[]
def check(name, condition, detail=''):
    results.append(dict(name=name, passed=bool(condition), detail=detail))
    print(name, 'PASS' if condition else 'FAIL', detail)
    assert condition, (name, detail)

def fixture(instrument='a'):
    arms={b:(0,1,1,0)[b%4] for b in range(340)}
    rows={}
    for b, arm in arms.items():
        for i in range(30):
            n=1800+b*30+i
            r=dict.fromkeys(B.REQUIRED,0)
            r.update(arm=arm,blk=b,draws=100,dispatches=10,dt_us=32000,
                     cpu_gpu_us=31500,spin_gpu_us=500,bda_scan=1000,
                     rt_att=100,rt_kpx=200000,gpu_busy_us=12000)
            if arm:
                r.update(bf_n=100,bf_disp=10,bf_push=110,bf_burn_ns=12000000,
                         bf_live_ahead=100 if instrument=='a' else 0,
                         bf_live_mat=10 if instrument=='a' else 110)
            rows[n]=r
    for b in range(1,len(arms)):
        if arms[b-1]!=arms[b]: rows[1800+b*30]['bf_edge']=1
    return rows,arms

def metadata(instrument='a',cal=False):
    m=T.metadata(instrument,cal)
    m['prereg']['sha256']=B.PRED_SHA
    return m

def write(tag,rows,arms,meta,stdout=b'normal\n'):
    texts=meta['schedule'].split(':',1)[1].split('|')
    p=ROOT/('log_'+tag+'.txt')
    with p.open('w',encoding='utf8') as f:
        f.write('BindFloorLatch: mode 1\nBindFloorClear: mode 0\nGpuClockPin: mode 1\n')
        for b, arm in arms.items():
            f.write(f'GateArm: arm={arm} arms=2 block={b} frame={1800+30*b} period=30 abba=1 text={texts[arm]}\n')
            for n in range(1800+30*b,1830+30*b):
                if n not in rows: continue
                txt=' '.join(f'{k}={v}' for k,v in rows[n].items())
                f.write(f'FrameTrace: n={n} {txt}\nFrameTrace-x: n={n} {txt}\n')
    (ROOT/(tag+'.json')).write_text(json.dumps(meta),encoding='utf8')
    (ROOT/('stdout_'+tag+'.txt')).write_bytes(stdout)
    return p

for inst in ('a','c'):
    rows,arms=fixture(inst); meta=metadata(inst)
    path=write('positive_'+inst,rows,arms,meta)
    err,pa=B.protocol(meta,path,inst)
    core=B.controls(rows,pa,inst)
    legacy,keep,area=B.legacy('positive_'+inst,ROOT)
    rev,rv=B.reversibility('positive_'+inst,ROOT)
    (ROOT/('positive_'+inst+'_legacy.txt')).write_text(legacy,encoding='utf8')
    (ROOT/('positive_'+inst+'_rv.txt')).write_text(rev,encoding='utf8')
    check('positive_'+inst,not err and all(core['checks'].values()) and all(keep.values())
          and area=='VALID' and all(rv.values()) and core['B']==19.0,
          {'errors':err,'core':core['checks'],'kept':keep,'area':area,'rv':rv,'pairs':core['endpoint']['pairs']})

rows,arms=fixture(); meta=metadata()
for field in ('bf_mixed','bf_trig_fire','bf_dlskip','bf_live_mat','img_new'):
    bad=copy.deepcopy(rows); del bad[1900][field]
    c=B.controls(bad,arms,'a')
    check('missing_early_'+field,not c['checks']['COUNTERS'] and c['B'] is None)
bad=copy.deepcopy(rows); bad[1900]['bf_live_mat']=1000000
check('early_live_leak',not B.controls(bad,arms,'a')['checks']['DARK_B'])
badmeta=copy.deepcopy(meta); badmeta['arms']=['bindfloor=1 bfmode=3','bindfloor=0 bfmode=3']
path=write('bad_arms',rows,arms,badmeta)
check('contradictory_arms',any('contradict' in e for e in B.protocol(badmeta,path,'a')[0]))
for token in (b'FATAL',b'Fatal error',b'Unhandled exception:',b'GpuMarkerHung',b'GpuCheckpointHang',b'GpuWaitSlow'):
    path=write('stdout_failure',rows,arms,meta,token+b'\n')
    check('stdout_'+token.decode(),any('stdout' in e for e in B.protocol(meta,path,'a')[0]))
shortrows={n:r for n,r in rows.items() if r['blk']<140}; shortarms={b:a for b,a in arms.items() if b<140}
path=write('short_hold',shortrows,shortarms,meta)
check('short_raw_hold',any('duration' in e for e in B.protocol(meta,path,'a')[0]))

# Put a stale VALID CSV next to doubled raw area; its contents must not decide.
path=write('stale_area',rows,arms,meta)
_,extract=B.invoke(B.AS,['area_series.py','stale_area','--root',str(ROOT),'--out',str(ROOT/'area_stale_area.csv')])
bad=copy.deepcopy(rows)
for r in bad.values():
    if r['arm']:r['rt_kpx']*=2
write('stale_area',bad,arms,meta)
out,keep,area=B.legacy('stale_area',ROOT)
(ROOT/'stale_area_legacy.txt').write_text(out,encoding='utf8')
check('fresh_raw_area',area=='INVALID',area)

# All-real component replay of calibration, with no mocked scorer dependency.
calmeta=metadata(cal=True)
write('cal99a',rows,arms,calmeta)
c=B.controls(rows,arms,'a')
data=dict(status='VALID_CALIBRATION_ONLY',tag='cal99a',instrument='a',pred_sha256=B.PRED_SHA,
          binary_sha256=B.BINARY_SHA,dt_a_us=c['dt_a'],dt_u_us=c['dt_u'],bfburn=12000)
for name,key in [('cal99a.json','metadata_sha256'),('log_cal99a.txt','log_sha256'),('stdout_cal99a.txt','stdout_sha256')]:
    data[key]=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
B.calibration_artifact(ROOT,'cal99a').write_text(json.dumps(data),encoding='utf8')
check('calibration_real_replay',not B.calibration_binding(ROOT,'a',meta))
(ROOT/'stdout_cal99a.txt').write_bytes(b'changed\n')
check('calibration_stdout_hash',any('source changed: stdout' in e for e in B.calibration_binding(ROOT,'a',meta)))
write('cal99a',bad,arms,calmeta)
data['log_sha256']=hashlib.sha256((ROOT/'log_cal99a.txt').read_bytes()).hexdigest()
B.calibration_artifact(ROOT,'cal99a').write_text(json.dumps(data),encoding='utf8')
check('calibration_replays_raw_area',any('legacy/area' in e for e in B.calibration_binding(ROOT,'a',meta)))

(ROOT/'assertions.json').write_text(json.dumps(results,indent=2),encoding='utf8')
print('TOTAL',len(results),'PASS')
