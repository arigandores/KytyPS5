import json,hashlib
from pathlib import Path
R=Path('C:/kyty/s99'); O=R/'verify99_c_raw'
def read(p): return json.loads(p.read_text())
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def line(p,token): return next(i for i,s in enumerate(p.read_text().splitlines(),1) if token in s)
c=read(O/'bf99h_admitted.json'); replay=read(O/'replay_bf99h.json')
a=read(R/'verify99_confirm_raw/bf99g_independent.json'); ar=read(R/'verify99_confirm_raw/replay_bf99g.json')
for obj in (a,c):
    assert all(sha(R/name)==digest for name,digest in obj['raw_sha256'].items())
for obj in (replay,ar):
    assert obj['status']=='ADMITTED_SETTLED_MEASUREMENT' and not obj['errors'] and all(obj['technical'].values()) and all(obj['strict'].values())
assert abs(c['endpoints']['B_cpu_ms']-replay['endpoints']['B_cpu_ms'])<1e-12
assert abs(c['endpoints']['B_wall_ms']-replay['endpoints']['B_wall_compatibility_ms'])<1e-12
assert not c['errors'] and all(c['strict'].values()) and all(c['zero_invariants'].values())
av,cv=a['endpoints']['B_cpu_ms'],c['endpoints']['B_cpu_ms']
combined={'status':'DIAGNOSTIC_ONLY','diagnostic':'HIGH' if min(av,cv)>=15.5 else 'LOW' if max(av,cv)<=11 else 'GAP','B_cpu_ms':[av,cv],'B_wall_compatibility_ms':[a['endpoints']['B_wall_ms'],c['endpoints']['B_wall_ms']],'addend_ms':0,'global_M3':'GAP unchanged; G/R1 alive and unlicensed','source_a':'verify99_confirm_raw/bf99g_independent.json (previous independent raw verification, raw hashes rechecked now)','source_c':'verify99_c_raw/bf99h_admitted.json (fresh independent raw parser)','replay_technical_count':len(replay['technical']),'replay_technical_passed':sum(replay['technical'].values()),'replay_strict_count':len(replay['strict']),'raw_unchanged':True,'current_frozen_scorer_sha256':sha(R/'settled99_norec.py')}
with (O/'combined_independent.json').open('x') as f: json.dump(combined,f,indent=2);f.write('\n')
p1=read(O/'eng99c1_raw.json'); p2=read(O/'eng99c2_raw.json')
reference=lambda filename,key:f'{filename}:{line(R/filename,key)}'
report=f'''# Independent VERIFY of bf99h(c) and combined diagnostic

PASS: bf99h is ADMITTED_SETTLED_MEASUREMENT under sealed pred05. This reviewer was not the implementation author and calculated c directly from raw logs with a separate parser, `verify99_c_raw/recount_c.py`. Endpoint calculation was enabled only after independent admission bands and fresh shared technical/provenance replay passed. No game/build was launched; no seal/source/raw/old score was edited.

| Claim | Evidence relative to C:/kyty/s99 | Fresh result |
|---|---|---|
| Immutable rule and scorer | pred/05_observer_separation.md:32; settled99_norec.py:25 | SHA256 pred05 fb376ee63ce8fb19c7151e37c34ddc340fbecafc6aa648a27a9c160e7bc20af0; scorer8216acd9797f7b2eeb61f2654a7827daed3f103ac0a07ec3b80a570ae6626399 |
| Whole raw continuity and identity | {reference('verify99_c_raw/bf99h_admitted.json','stream_counts')}; bf99h.json:344 | 18245 main/draw/x rows EACH, n2..18246; 183 original GateArm blocks; no duplicate/missing/out-of-order row or arm error; hold900.3s, raw917.191640s (after-stable900.358733s in replay); no forbidden fatal marker |
| Fixed population, no reuse or repair | log_bf99h.txt:493701 and :2608188; {reference('verify99_c_raw/bf99h_admitted.json','selected_block_range')} | Original blocks4..179, idx60..88 only, n>=2100; 88 distinct pairs (44AB/44BA),2552 rows/arm. Initial quartet0..3 and incomplete terminal quartet180..183 wholly excluded; no internal exclusions |
| Work/C5 | {reference('verify99_c_raw/bf99h_admitted.json','draws_U_A')} | draws5034.733542319749→5040.027429467084, work+0.1051473152022364%; abs<0.5% and C5<=2% PASS |
| Raw area and matching | {reference('verify99_c_raw/bf99h_admitted.json','area_U_A')} | rt_kpx/rt_att2008.078350426786→2008.049273703920; split−0.0014479874682061% (<1%);88/88 pairs within original0.5% pair band; matching100%>=90% |
| C9 timing | {reference('verify99_c_raw/bf99h_admitted.json','dt_U_A_us')} | dt_U49913.056818181816/dt_A50171.295454545456us; abs difference0.5173769206408756%<=3% |
| Falls and edges | {reference('verify99_c_raw/bf99h_admitted.json','completed_falls')} |45 completed falls>=30;91 total bf_edge, all idx0; pair minimum>=30 passes |
| CPU burn full log | log_bf99h.txt:456411; {reference('verify99_c_raw/bf99h_admitted.json','bf_burn_cpu_ns')} | CPU88954177609ns,42584690 successful samples,bad0; wall83621069464ns; query indicator14808653003ns. Every required field present; no negative audited counter |
| Direct GC full log | log_bf99h.txt:16545; {reference('verify99_c_raw/bf99h_admitted.json','bf_igc_checks')} |146241 checks/65820 holds; bad/critical/evict0; every retained armed block held>=226 calls |
| Integrity/buffer recovery | {reference('verify99_c_raw/bf99h_admitted.json','zero_invariants')}; {reference('verify99_c_raw/bf99h_admitted.json','recovery')} | mixed/defer_force/trig_*/dlskip/clr_skip/skip_drop/gm_ops all0; buffer two-/three-row recovery medians1/3<=50; xover,xover_acb,defer92 each remain reported |
| Frozen source chain and A/A | bf99h.json:63; eng99c2.json:63; {reference('verify99_c_raw/replay_bf99h.json','source_artifact')} | source c2 artifact f8df75ffde566f43e7120462877fa30a81fe7803b1669ae5e26bf21f4069d6a4; immediate c1 source5e97bac7a607e77977b3e5db7d80da08d42ba8536ee5a78b2a51e82afa9c5886; AA3c8c8ed44a93ad1d9295016e0e5cdc7602f142d6be443ad6863e292b1068a55e. Fresh frozen scorer recursively replays c1/c2 and AA from raw and checks prelaunch SHA fields, not labels alone |
| Shared controls and no recorder | {reference('verify99_c_raw/replay_bf99h.json','technical')} |44/44 technical,6/6 strict,errors[]; KYTY_REC absent, no Recording:/ImageLife runtime trace, same binary34206e3f…355f and fixed10200us burn. Earlier progress message's43 count was a manual counting error: len44,sum44; executor technical dict equals fresh dict, key diff empty |
| Endpoint from independently selected raw | {reference('verify99_c_raw/bf99h_admitted.json','endpoints')} | B_c_cpu={cv:.15f}ms; B_c_wall={c['endpoints']['B_wall_ms']:.15f}ms. Median of88 armed-block means of (cpu_gpu_us−spin_gpu_us−bf_burn_cpu_ns/1000)/1000; matches fresh scorer exactly. No2.2535 addend and no observer residual subtraction |

Armed retained mean CPU burn10.816662789577ms versus wall10.173132940047ms, difference+0.643529849530ms; CPU query cost indicator1.799092679467ms. The wall endpoint is compatibility readout only.

The source engineering chain was also personally parsed: eng99c1 has20pairs/11falls,work+0.414748550334%,area−0.010062405672%,matching20/20; dt_U49824.99137931035−dt_A57473.418965517245=−7648.4275862069us. The frozen update is17800+round100(−7648.4276)=10200. Its C9 diagnostic15.3505848661% FAIL remains a pilot TUNE, never a measurement. eng99c2 has22pairs/12falls,work+0.208306169518%,area−0.003582563600%,matching22/22; dt_U49527.65987460815/dt_A49317.35579937304us, relative0.424619446523%<=1% => LOCK10200. Neither pilot receives B. The AA is freshly replayed; its earlier independent raw result remains verify99_confirm_raw/aa99plain_independent.json.

Historical observations are retained: image R6 two-row median45 PASS; R6′ three-row median54 FAIL (>50). R6′ is reported-only by pred04, not relabelled PASS. Historical whole-window criterion3 is still INVALID, work−1.292%, with original C1/C4/C6/C8/C8″ failures printed in replay; none supplants the prespecified settled population.

Combined rule pred02 §6 (carried by pred05 §5): both independent confirmations admitted, B_a_cpu={av:.15f}ms from prior independent raw verification, B_c_cpu={cv:.15f}ms computed here. Their raw hashes were freshly rechecked unchanged. min={min(av,cv):.15f}>=15.5, therefore HIGH DIAGNOSTIC with addend0. The independent calculation is `verify99_c_raw/combined_independent.json:1`. This completes the two-instrument bindings-only CPU diagnostic; global M3 remains GAP and G/R1 alive/unlicensed. c is a different live resource-acquisition implementation, not subtraction of dead workers.

Not proved: global architectural impossibility or60 FPS ceiling, correctness/pixel recovery, binary regression attribution, recording as sole cause of historical work failure, universal cache identity correctness, or cross-queue untorn execution. This reviewer did not read or evaluate VISUAL/FACTS/author causal reports.45 mode2 falls are not the historical857-edge mode3 power. A positive floor number cannot be sold as a shipped correctness-preserving optimisation.

Raw pins: log_bf99h.txt {c['raw_sha256']['log_bf99h.txt']}; stdout_bf99h.txt {c['raw_sha256']['stdout_bf99h.txt']}; bf99h.json {c['raw_sha256']['bf99h.json']}. All review analysis subprocesses completed; no owned game/GPU process exists.
'''
with (O/'VERIFY.md').open('x',encoding='utf-8') as f:f.write(report)
print(json.dumps(combined,indent=2))
