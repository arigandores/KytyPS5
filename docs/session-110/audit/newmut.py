import subprocess, sys, os, time, re
from pathlib import Path
A='C:/kyty/s110/audit110/mut/'
def run(scorer, test, name, old, new, count=1):
    src=Path('C:/kyty/s110/'+scorer).read_text(encoding='utf-8')
    n=src.count(old)
    if n!=count:
        return name, 'ANCHOR x%d'%n
    d=A+name+'/'; os.makedirs(d,exist_ok=True)
    Path(d+scorer).write_text(src.replace(old,new),encoding='utf-8',newline='')
    t=time.time()
    p=subprocess.run([sys.executable,'C:/kyty/s110/'+test,d+scorer],capture_output=True,text=True,encoding='utf-8',errors='replace')
    out=p.stdout
    fails=[l for l in out.splitlines() if (l.rstrip().endswith(' FAIL') or re.search(r' FAIL  failed=', l)) and not l.startswith('CONSTANTS')]
    killed = bool(fails) or 'ALL OK' not in out and ('FIXTURE FAILURES' in out and fails)
    return name, ('KILLED' if fails else 'SURVIVED')+' (%d failing cases, %.0fs) %s'%(len(fails),time.time()-t,[f.split()[0] for f in fails][:4])
STL=[
 ('stl_startup_back', 'stall_after += int(rows > 0)', 'stall_after += int(rows >= 0)'),
 ('stl_D_after_only', 'stall_d += us', 'stall_d += us if rows > 0 else 0'),
 ('stl_M_after_only', 'stall_m = max(stall_m, us)', 'stall_m = max(stall_m, us) if rows > 0 else stall_m'),
 ('stl_nopower_counters', "elif na == 0:", "elif sa == 0:"),
 ('stl_minrows_100', 'MIN_ROWS = 1000', 'MIN_ROWS = 100'),
 ('stl_regex_search', "m = STALL.match(line)", "m = STALL.search(line)"),
 ('stl_armB_nobad', "if arm == 'B' and (tot['cspfree_hit'] <= 0 or tot['cspfree_bad']):", "if arm == 'B' and (tot['cspfree_hit'] <= 0):"),
 ('stl_forbid_norec', "FORBIDDEN_ENV = ('KYTY_GATE_SCHEDULE', 'KYTY_GPU_CHECKPOINTS', 'KYTY_REC')", "FORBIDDEN_ENV = ('KYTY_GATE_SCHEDULE', 'KYTY_GPU_CHECKPOINTS')"),
 ('stl_sync_tol2', "if not 0 <= s - stall_after <= 1:", "if not -1 <= s - stall_after <= 1:"),
 ('stl_ma_min', "ma = max([e.get('m', 0) for e in entries if e['arm'] == 'A'] or [0])", "ma = sum([e.get('m', 0) for e in entries if e['arm'] == 'A'] or [0])"),
 ('stl_order_unsorted', "stamps != sorted(stamps) or ", ""),
 ('stl_dup_tag_arm', "ORDER = 'ABBAABBA'", "ORDER = 'ABABABAB'"),
]
SHP=[
 ('shp_keep_full', 'KEEP_LO, KEEP_HI = 60, 89', 'KEEP_LO, KEEP_HI = 0, 90'),
 ('shp_first_1800', 'PERIOD, START, FIRST_FRAME = 90, 1800, 2100', 'PERIOD, START, FIRST_FRAME = 90, 1800, 1800'),
 ('shp_min_pairs_6', 'MIN_PAIRS = 60', 'MIN_PAIRS = 6'),
 ('shp_ship_99', 'SHIP_US = -100.0', 'SHIP_US = -99.0'),
 ('shp_drop_max', 'DROP_MAX = 0.05', 'DROP_MAX = 0.5'),
 ('shp_cpu_net_raw', "out['cpu_net_us'] = row['cpu_gpu_us'] - row['spin_gpu_us']", "out['cpu_net_us'] = row['cpu_gpu_us']"),
 ('shp_video_frames', 'VIDEO_MIN_FRAMES = 3000', 'VIDEO_MIN_FRAMES = 300'),
 ('shp_walks_tol', 'WALKS_TOL = 0.05', 'WALKS_TOL = 0.5'),
]
if __name__=='__main__':
    which=sys.argv[1]
    lst = STL if which=='stl' else SHP
    scorer,test = ('stl110b.py','test_stl110b.py') if which=='stl' else ('shp110.py','test_shp110.py')
    for name,old,new in lst:
        print(*run(scorer,test,name,old,new), flush=True)
