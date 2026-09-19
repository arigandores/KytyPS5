import collections,csv,json,pathlib
root=pathlib.Path('C:/kyty/s99'); out=root/'verify99_visual_raw'
summary=json.loads((out/'raw_summary.json').read_text())
base=json.loads((root/'video99_base_full/report.json').read_text())
summary['vis99base']['detector']={'frames':base['frames'],'events_count':len(base['events']),'events':base['events']}
(out/'raw_summary.json').write_text(json.dumps(summary,indent=2))
events=summary['bf99e']['detector']['events']
reportlines=[n for n,line in enumerate((root/'video99_full/report.json').read_text().splitlines(),1) if '"frame":' in line]
with (out/'bf99e_event_map.csv').open('w',newline='') as f:
    writer=csv.writer(f); writer.writerow(['event','report_line','video_frame','present','host_s','idx_line','trace_line','arm','block','diff_prev','diff_next','area'])
    for i,(e,rl) in enumerate(zip(events,reportlines),1):
        t=e['trace']; writer.writerow([i,rl,e['frame'],*e['present'],e['idx_line'],t['line'],t['arm'],t['blk'],e['diff_prev'],e['diff_next'],e['area']])
groups=collections.defaultdict(list)
for i,e in enumerate(events): groups[(e['trace']['blk'],e['trace']['arm'])].append((i,e))
table=['| Block / arm | Events | Host time, s | Present IDs | Raw references |','|---|---:|---|---|---|']
for (blk,arm),group in groups.items():
    i,a=group[0]; j,b=group[-1]
    table.append(f"| {blk} / {arm} | {len(group)} | {a['present'][1]:.3f}–{b['present'][1]:.3f} | {a['present'][0]}–{b['present'][0]} | video99_full/report.json:{reportlines[i]}; log_bf99e.txt:{a['trace']['line']}; bf99e_event_map.csv:{i+2} |")
text='''# Independent raw visual verification — vis99base versus bf99e

## Result and scope

PASS for the requested raw control checks: one surviving >=900s hold, continuous video index, no positive bindfloor anywhere in the control log, and all decoded video frames examined by the authorized memory-bounded three-frame detector. Normal control: **17,802 frames / 0 detector events**. Existing floor video: **18,037 frames / 185 detector events**, including **11 events labelled base arm 0**. This is a detector result, not a proof of rendering correctness or absence of persistent defects. No game, build, CPU scoring, B, or source changes were performed.

## Claims with raw evidence

- **900s hold actually covered:** vis99base.json:327 records exactly one attempt (PID63948); :338 outcome=ok; :340 hold_exit=null; :341 actual hold_s=900.3 (requested :349=900). Independently, rec_vis99base.mp4.idx:398 maps stable present398 to host16.748s; :17802 ends at present17802, host917.981s. Post-stable index span=901.233s. Log closes normally at log_vis99base.txt:2673384 (Window1 closed), :2673385 (Event: quit). No GpuHangAbort, terminate, abort or VK_ERROR_DEVICE_LOST marker found by the explicit scan.
- **Complete continuous index:** rec_vis99base.mp4.idx:1 = `0 1 0.000`; :17802 = `17801 17802 917.981`. All17,802 rows have video_frame=i and present=i+1; zero gaps, duplicates, backward timestamps or equal timestamps. Detector independently decoded exactly17,802 frames, exit0; detector_stdout.txt:1 records `frames=17802 one-frame glitches=0`; detector_stderr.txt is empty. video99_base_full/report.json:3 frames17802, :4 events[].
- **Physical floor never enabled:** complete scan of all2,673,386 control-log lines finds178 bindfloor assignments, all0; positive occurrences0. First log_vis99base.txt:455581 (GateArm block0/present1800), last :2657645 (block177/present17730) both bindfloor=0. Across17,793 FrameTrace-x rows, all sampled activity fields bf_n, bf_disp, bf_reuse, bf_burn_ns, bf_burn_cpu_n, bf_skip, bf_gc_hold, bf_edge, bf_bgc_hold, bf_clr_skip have zero nonzero rows (first :18047). Metadata environment/schedule vis99base.json:53 and :64 agrees: both label arms bindfloor0/drawahead1/bfmode2/bfburn17800. The arm1 label in this control is not a physical floor arm.
- **Trace continuity and its limit:** FrameTrace and FrameTrace-x each cover every n=2..17794 (17,793 rows), no internal gap. The recording includes8 final presents17795..17802 without a FrameTrace row. Do not claim a one-to-one traced mapping for those final8. Both recordings show this shutdown tail; no detector event in either falls in that unmapped tail.
- **Comparable wall duration:** bf99e index has18,037 continuous rows, last host917.681s; stable present396 at16.399s gives901.282s post-stable. Both metadata actual holds900.3s. Difference in overall indexed coverage is0.300s, control longer.
- **Identity:** hashes.json stores size and full SHA256 for sealed protocol, both metadata and indexed videos, control log, and original floor detector report. Protocol SHA256=fb376ee63ce8fb19c7151e37c34ddc340fbecafc6aa648a27a9c160e7bc20af0,8583 bytes; matches vis99base.json:320 seal. Both metadata binary SHA256 fields identify34206e3fe4fb7c887af2901ce6332d63d0ebd715ef95d3a4ff5547654b58355f. Installed executable was not rehashed in this bounded visual task.

## Floor-video event mapping

The mapping below is from original detector events to their .idx present and exact FrameTrace n. These are reported arm labels; they are not proof that each image's content was generated wholly under that arm. All185 events map to a traced present:174 arm1,11 arm0. Event count is a count of qualifying three-frame centers, not185 independent incidents. Adjacent alternating frames can generate many events.

'''+ '\n'.join(table)+'''

Earliest event: frame8879/present8880/450.531s, arm1/block78, previous/next mean differences4.281381/4.281836 and neighbour difference0.007254. Latest: frame13966/present13967/707.199s, arm0/block135, differences9.273279/9.480002, neighbours2.761156. The10 arm0 events in block107 occupy frames11430..11439 at579.564..579.998s; one further arm0 event occurs707.199s. Full185-event numerical map is bf99e_event_map.csv.

## Limits

- The detector uses threshold4 and requires both neighbour differences>4 plus outer-neighbour similarity<35% of the smaller difference (C:/kyty/s32/vidglitch_stream.py:26). It detects transient/alternating anomalies of that form. It cannot rule out persistent corruption, frozen content, regional glitches under threshold, or correct idle animation qualifying as a transient. Fixed early/middle/late image inspection is performed separately by the parent and is not duplicated or inferred here.
- The normal control's zero events versus floor video's185 supports a difference in this detector's transient signature; it does not by itself establish P1 for large persistent effects. It does not separate normal renderer from recorder, establish a binary regression, or prove visual recovery after disabling floor. The185-event original result is preserved as-is.
- Use .idx host timestamps for actual hold and events. The MP4 is tagged60/1fps and its17,802 frames have296.7s playback duration; detector timeline.second likewise divides frame index by60. Those playback seconds are not the917.981s observed host interval.
- No effect estimate, CPU budget, freeze estimate or B was produced. bf99e's prior failed measurement remains failed.

Reproduction: verify_raw.py scans logs line-by-line and indexes without retaining decoded images; finalize.py adds the finished detector report and mapping. Authorized detector command: `python C:/kyty/s32/vidglitch_stream.py C:/kyty/s99/rec_vis99base.mp4 C:/kyty/s99/video99_base_full 4`; stdout/stderr preserved separately. Detector process exited0. All writes confined to verify99_visual_raw and video99_base_full.
'''
(out/'VERIFY.md').write_text(text,encoding='utf-8')
print(text)
