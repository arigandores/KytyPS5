"""Session 102, M5: the sealed timing bench (pred/01_m5_bench.md s5 AS AMENDED by
pred/02_m5_addendum.md s4), in one qrenderdoc.

    RD_CAP=<rdc> RD_PLAN=<plan.json> RD_OUT=<bench.json> \
        "C:/Program Files/RenderDoc/qrenderdoc.exe" --python C:/kyty/s102/rd_m5_bench.py

As implemented here:
  * Refuses to run unless both sealed texts (pred/01, pred/02) match their sha256.
  * Build every module of every arm FIRST (BuildTargetShader with the stage of each replacement:
    PS and CS may be mixed in one arm).  A build error is logged in full and recorded; the bench
    then refuses to time (V-g) unless RD_ALLOW_BUILD_FAIL=1 (mechanics).
  * Every replacement is shown to be IN EFFECT before any timing (the pipeline reflection at the
    module's first event carries the replacement's bytes); otherwise the bench refuses (V-g).
  * Two warm-up fetches with arm B, discarded (kept in the JSON, flagged).
  * Five arms B A V1 V2 V2s.  Round r measures every arm once in the order DESIGN[r mod 10] of
    m5_102.DESIGN: the five cyclic rotations of [B, A, V1, V2, V2s] (rotation k starts at arm k),
    FOLLOWED BY their reverses in the same rotation order (pred/02 s4, "used in that order").
    Every fetch records its round, position, seq_index (= r mod 10) and the whole sequence; the
    list out['round_sequences'] records the sequence of every round.  RD_ARMS restricts the arms
    (mechanics); the design is then filtered to them.
  * R = RD_ROUNDS (default 20, two cycles).  If one FetchCounters takes longer than
    RD_FETCH_LIMIT_S (600 s = 10 min), R drops to the largest value that fits an RD_MAX_HOURS (4 h)
    bench, whole cycles preferred, never below 8 (m5_102.rounds_after_time_rule).
  * A measurement = ReplaceResource for every replacement of the arm, ONE
    FetchCounters([EventGPUDuration]) (seconds -> microseconds), RemoveReplacement for all.
  * RAW per-event durations of every planned event (included AND excluded modules, the scorer
    needs both) are written for every measurement, with the wall time of each call, into RD_OUT
    after EVERY fetch (write-and-rename), so a crash keeps every completed fetch.

Extension (pred/02 s3/s4: INCONCLUSIVE => one extension of 20 more rounds, same design, same
process if possible): with RD_AUTO_EXTEND=1 and RD_EQUAL=<rd_m5_equal.json>, the bench calls the
scorer's own decision (m5_102.decide) after the R rounds and, if it returns INCONCLUSIVE, runs
RD_EXT_ROUNDS (20) more rounds continuing the design (round index R, R+1, ...), flagged
"extension".  Without RD_EQUAL the interim decision cannot be made (V-e decides the valid sets)
and nothing is extended.  RD_RESUME=<bench.json> starts a NEW process that appends extension
rounds to a finished bench (written to RD_OUT, which must differ); it is flagged
"extension_new_process" and repeats the two warm-up fetches.

Env: RD_CAP, RD_PLAN, RD_OUT (required); RD_ROUNDS, RD_MAX_HOURS, RD_FETCH_LIMIT_S, RD_ARMS,
     RD_AUTO_EXTEND, RD_EQUAL, RD_EXT_ROUNDS, RD_RESUME, RD_SHA=0 (skip the capture sha256,
     mechanics only), RD_ALLOW_BUILD_FAIL=1 (mechanics only), RD_FORCE_EXTEND=1 (mechanics
     plans only: run the extension whatever the interim decision, to exercise the path),
     RD_REPLAY_OPT (RenderDoc replay optimisation, default balanced).  Log: <RD_OUT>.log.
"""
import os
import sys
import time
import json
import hashlib

sys.dont_write_bytecode = True
sys.path.insert(0, 'C:/kyty/s102')
import m5_rdlib as lib  # noqa: E402
import m5_102  # noqa: E402

OUT = lib.env_required('RD_OUT')
log = lib.Log(OUT + '.log')


def sequences_for(arm_names, plan):
    """The sealed design (m5_102.DESIGN), filtered to the arms actually benched."""
    if plan.get('sequences'):
        raise SystemExit('a plan may not override the sealed design (pred/02 s4)')
    unknown = [a for a in arm_names if a not in m5_102.ARMS]
    if unknown:
        raise SystemExit('arms %s are not in the sealed design %s' % (unknown, list(m5_102.ARMS)))
    seqs = m5_102.design_for(arm_names)
    for seq in seqs:
        if sorted(seq) != sorted(arm_names):
            raise SystemExit('design sequence %s does not contain every arm %s exactly once' % (seq, arm_names))
    return seqs


def main():
    import renderdoc as rd
    lib.hide_ui(log)
    seals = lib.require_seals(log)
    cap_path = lib.env_required('RD_CAP')
    plan_path = lib.env_required('RD_PLAN')
    plan = json.load(open(plan_path, encoding='utf-8'))
    rounds_req = int(os.environ.get('RD_ROUNDS', str(m5_102.ROUNDS_SEALED)))
    max_hours = float(os.environ.get('RD_MAX_HOURS', '4'))
    fetch_limit = float(os.environ.get('RD_FETCH_LIMIT_S', '600'))
    ext_rounds = int(os.environ.get('RD_EXT_ROUNDS', str(m5_102.EXT_ROUNDS)))
    auto_extend = os.environ.get('RD_AUTO_EXTEND', '0') == '1'
    equal_path = os.environ.get('RD_EQUAL', '').strip() or None
    resume_path = os.environ.get('RD_RESUME', '').strip() or None
    allow_build_fail = os.environ.get('RD_ALLOW_BUILD_FAIL', '0') == '1'
    if os.path.exists(OUT):
        raise SystemExit('RD_OUT %s exists: a bench is never overwritten' % OUT)
    if resume_path and os.path.abspath(resume_path) == os.path.abspath(OUT):
        raise SystemExit('RD_RESUME must differ from RD_OUT')

    arms_all = {arm['name']: arm for arm in plan['arms']}
    arm_filter = [a.strip() for a in os.environ.get('RD_ARMS', '').split(',') if a.strip()]
    arm_names = arm_filter or [a['name'] for a in plan['arms']]
    for name in arm_names:
        if name not in arms_all:
            raise SystemExit('arm %s not in the plan' % name)
    seqs = sequences_for(arm_names, plan)
    events = [int(e) for e in plan['events']]

    if resume_path:
        out = json.load(open(resume_path, encoding='utf-8'))
        if not out.get('complete'):
            raise SystemExit('RD_RESUME %s is not a completed bench' % resume_path)
        out['resumed_from'] = os.path.abspath(resume_path).replace('\\', '/')
        out['extension_new_process'] = True
        out['complete'] = False
        if out['events'] != events or out['arms'] != arm_names:
            raise SystemExit('RD_RESUME bench has other events or arms than the plan')
        if out.get('plan_sha256') != hashlib.sha256(open(plan_path, 'rb').read()).hexdigest():
            raise SystemExit('RD_RESUME bench was made from another plan')
    else:
        out = dict(tool='rd_m5_bench', capture=cap_path, plan=os.path.abspath(plan_path).replace('\\', '/'),
                   plan_sha256=hashlib.sha256(open(plan_path, 'rb').read()).hexdigest(),
                   pred_sha256=plan.get('pred_sha256'), addendum_sha256=plan.get('addendum_sha256'),
                   seals=seals, mechanics=bool(plan.get('mechanics')),
                   arms=arm_names, sequences=[list(s) for s in seqs],
                   design='m5_102.DESIGN: rotations 0..4 of [B, A, V1, V2, V2s] then their reverses 0..4; '
                          'round r uses sequence r mod 10',
                   events=events, rounds_requested=rounds_req, ext_rounds_requested=ext_rounds,
                   max_hours=max_hours, fetch_limit_s=fetch_limit,
                   replay_optimisation=lib.replay_opt_name(),
                   started=time.strftime('%Y-%m-%dT%H:%M:%S'), builds=[], build_errors=[],
                   warmup=[], fetches=[], round_sequences=[], decisions=[], complete=False)
    out['process_started'] = time.strftime('%Y-%m-%dT%H:%M:%S')

    if os.environ.get('RD_SHA', '1') != '0':
        t = time.time()
        sha = lib.sha256_file(cap_path)
        log('capture sha256 %s (%.1f s)' % (sha, time.time() - t))
        if out.get('capture_sha256') and out['capture_sha256'] != sha:
            raise SystemExit('capture sha256 differs from the resumed bench')
        out['capture_sha256'] = sha
        if plan.get('capture_sha256') and plan['capture_sha256'] != sha:
            out['capture_sha256_mismatch_plan'] = plan['capture_sha256']
            log('WARNING: the capture is not the one the plan was made from')
    else:
        out.setdefault('capture_sha256', None)

    t = time.time()
    cap, ctrl = lib.open_capture(rd, cap_path, log)
    out['open_s'] = round(time.time() - t, 2)
    counters = lib.Counters(rd, ctrl)
    out['counter'] = counters.describe()
    resources = lib.resource_map(ctrl)

    # ---- the original modules must be the ones the plan names (md5 of rawBytes) ----
    originals = {}
    for name in arm_names:
        for rep in arms_all[name]['replacements']:
            rid = rep['orig_shader_id']
            if rid in originals:
                continue
            module = resources.get(rid)
            if module is None:
                raise SystemExit('original module %s is not in this capture' % rid)
            _, raw = lib.module_reflection(rd, ctrl, module)
            md5 = hashlib.md5(raw).hexdigest()
            if rep.get('orig_md5') and rep['orig_md5'] != md5:
                raise SystemExit('original module %s md5 %s != plan %s' % (rid, md5, rep['orig_md5']))
            originals[rid] = module

    # ---- build every module of every arm first ----
    built = {}          # (spv md5, stage) -> ResourceId
    arm_reps = {}       # arm -> [(orig ResourceId, new ResourceId)]
    failed = False
    t_build = time.time()
    for name in arm_names:
        pairs = []
        for rep in arms_all[name]['replacements']:
            spv = open(rep['spv_path'], 'rb').read()
            md5 = hashlib.md5(spv).hexdigest()
            if rep.get('md5') and rep['md5'] != md5:
                raise SystemExit('%s: %s md5 %s != plan %s' % (name, rep['spv_path'], md5, rep['md5']))
            key = (md5, rep['stage'])
            if key not in built:
                t = time.time()
                new_id, errors = ctrl.BuildTargetShader('main', rd.ShaderEncoding.SPIRV, spv,
                                                        rd.ShaderCompileFlags(), lib.stage_enum(rd, rep['stage']))
                row = dict(arm=name, item=rep.get('item'), perm=rep.get('perm'), path=rep['spv_path'],
                           md5=md5, stage=rep['stage'], seconds=round(time.time() - t, 3),
                           ok=new_id != rd.ResourceId.Null(), messages=errors or '')
                out['builds'].append(row)
                if new_id == rd.ResourceId.Null():
                    failed = True
                    out['build_errors'].append(row)
                    log('BUILD FAILED %s %s %s:\n%s' % (name, rep.get('item'), rep['spv_path'], errors))
                    continue
                if errors:
                    log('build messages %s %s: %s' % (name, rep['spv_path'], errors))
                built[key] = new_id
            if key in built:
                pairs.append((originals[rep['orig_shader_id']], built[key]))
        arm_reps[name] = pairs
    out['build_s'] = round(time.time() - t_build, 2)
    log('built %d modules in %.1f s, %d failures' % (len(built), out['build_s'], len(out['build_errors'])))
    lib.write_json_atomic(OUT, out)
    if failed and not allow_build_fail:
        raise SystemExit('a module failed to build: the bench does not time (V-g)')

    # ---- the replacement must be IN EFFECT: with an arm applied, the pipeline reflection at a
    # ---- module's first event carries the replacement's bytes (checked on RenderDoc 1.46:
    # ---- GetShader() keeps the original id, GetShaderReflection() reports the replacement) ----
    first_event = {}
    for item in plan['items'].values():
        for module in item.get('modules', []):
            if module.get('events'):
                first_event[module['orig_shader_id']] = (module['events'][0], item['stage'])
    checks = []
    t_check = time.time()
    for name in arm_names:
        reps = arms_all[name]['replacements'] if name != 'B' else []
        if not reps:
            continue
        for orig, new_id in arm_reps.get(name, []):
            ctrl.ReplaceResource(orig, new_id)
        try:
            for r_ in reps:
                where = first_event.get(r_['orig_shader_id'])
                if where is None:
                    continue
                ctrl.SetFrameEvent(where[0], True)
                refl = ctrl.GetPipelineState().GetShaderReflection(lib.stage_enum(rd, where[1]))
                got = hashlib.md5(bytes(refl.rawBytes)).hexdigest() if refl is not None else None
                want = hashlib.md5(open(r_['spv_path'], 'rb').read()).hexdigest()
                checks.append(dict(arm=name, item=r_.get('item'), orig=r_['orig_shader_id'], eid=where[0],
                                   expected=want, got=got, ok=got == want))
        finally:
            for orig, _ in arm_reps.get(name, []):
                ctrl.RemoveReplacement(orig)
    out['replacement_check'] = checks
    out['replacement_check_ok'] = bool(checks) and all(c['ok'] for c in checks)
    out['replacement_check_s'] = round(time.time() - t_check, 1)
    log('replacement check: %d modules, %d not in effect, %.1f s'
        % (len(checks), sum(1 for c in checks if not c['ok']), out['replacement_check_s']))
    lib.write_json_atomic(OUT, out)
    if not out['replacement_check_ok'] and not allow_build_fail:
        raise SystemExit('a replacement is not in effect: the bench does not time (V-g)')

    def measure(name, round_index, position, phase, seq_index=None):
        pairs = arm_reps.get(name, []) if name != 'B' else []
        t0 = time.time()
        for orig, new_id in pairs:
            ctrl.ReplaceResource(orig, new_id)
        t1 = time.time()
        values = counters.fetch()
        t2 = time.time()
        for orig, _ in pairs:
            ctrl.RemoveReplacement(orig)
        t3 = time.time()
        row = dict(phase=phase, round=round_index, pos=position, arm=name, seq_index=seq_index,
                   t_start=round(t0, 3), replace_s=round(t1 - t0, 3), fetch_s=round(t2 - t1, 3),
                   remove_s=round(t3 - t2, 3), n_results=len(values), total_all_us=round(sum(values.values()), 3),
                   d=[values.get(e) for e in events],
                   missing=[e for e in events if e not in values])
        return row

    # ---- warm-up: two fetches with arm B, discarded.  The 4-hour clock starts here. ----
    bench_t0 = out.setdefault('bench_t0', time.time())
    for i in range(2):
        row = measure('B', -1, i, 'warmup' if not resume_path else 'warmup_resume')
        out['warmup'].append(row)
        lib.write_json_atomic(OUT, out)
        log('warm-up %d: fetch %.2f s, total %.1f us' % (i, row['fetch_s'], row['total_all_us']))

    # one "fetch" (the 10-minute trigger) is the FetchCounters call; the budget counts the whole
    # measurement (replace + fetch + remove)
    fetch_only = [w['fetch_s'] for w in out['warmup']]
    fetch_times = [w['fetch_s'] + w['replace_s'] + w['remove_s'] for w in out['warmup']]

    def run_rounds(first, count, flag):
        """Rounds first .. first+count-1; returns the number completed."""
        target = first + count
        triggered = any(f > fetch_limit for f in fetch_only)
        r = first
        while r < target:
            seq_index = r % len(seqs)
            seq = seqs[seq_index]
            out['round_sequences'].append(dict(round=r, phase=flag, seq_index=seq_index, sequence=list(seq)))
            for position, name in enumerate(seq):
                row = measure(name, r, position, flag, seq_index)
                out['fetches'].append(row)
                fetch_only.append(row['fetch_s'])
                fetch_times.append(row['fetch_s'] + row['replace_s'] + row['remove_s'])
                lib.write_json_atomic(OUT, out)
                log('round %d seq %d %-3s pos %d: replace %.2f fetch %.2f remove %.2f s, planned events %d missing %d'
                    % (r, seq_index, name, position, row['replace_s'], row['fetch_s'], row['remove_s'],
                       len(events), len(row['missing'])))
                if row['fetch_s'] > fetch_limit and not triggered:
                    triggered = True
                    log('a fetch took %.0f s > %.0f s: the 4-hour rule is armed' % (row['fetch_s'], fetch_limit))
            r += 1
            if triggered and flag == 'main':
                per_round = len(seqs[0]) * (sum(fetch_times) / len(fetch_times))
                elapsed = time.time() - bench_t0
                fit_more = int(max(0.0, max_hours * 3600.0 - elapsed) // per_round)
                new_total = m5_102.rounds_after_time_rule(count, r - first, (r - first) + fit_more)
                new_target = first + new_total
                if new_target != target:
                    out['decisions'].append(dict(kind='rounds_drop', after_round=r - 1, rounds_before=target - first,
                                                 rounds_after=new_total, per_round_s=round(per_round, 1),
                                                 elapsed_s=round(elapsed, 1),
                                                 rule='m5_102.rounds_after_time_rule (whole cycles preferred, floor 8)'))
                    log('4-hour rule: R %d -> %d (per round %.0f s, elapsed %.0f s)'
                        % (target - first, new_total, per_round, elapsed))
                    target = new_target
                    lib.write_json_atomic(OUT, out)
        return r - first

    if resume_path:
        start = max([f['round'] for f in out['fetches']] + [-1]) + 1
        done = run_rounds(start, ext_rounds, 'extension')
        out['rounds_extension'] = out.get('rounds_extension', 0) + done
    else:
        done_main = run_rounds(0, rounds_req, 'main')
        out['rounds_main'] = done_main
        out['rounds_extension'] = 0
        if auto_extend:
            if not equal_path:
                out['decisions'].append(dict(kind='extension_not_evaluated', reason='RD_AUTO_EXTEND without RD_EQUAL'))
                log('RD_AUTO_EXTEND=1 but no RD_EQUAL: the interim decision cannot be made')
            else:
                equal = json.load(open(equal_path, encoding='utf-8'))
                if equal.get('plan_sha256') != out['plan_sha256']:
                    raise SystemExit('RD_EQUAL was made from another plan: no interim decision')
                interim = m5_102.decide(plan, out, equal, final=False,
                                        mechanics=bool(plan.get('mechanics')))
                stats = interim.get('statistics', {})
                out['decisions'].append(dict(kind='interim', equal=os.path.abspath(equal_path).replace('\\', '/'),
                                             verdict=interim.get('verdict'), status=interim.get('status'),
                                             statistical=interim.get('statistical_classification'),
                                             extend=interim.get('extend'),
                                             points={k: stats.get(k, {}).get('point') for k in m5_102.DECIDING_STATS},
                                             ci_minus1={k: stats.get(k, {}).get('ci_minus1') for k in m5_102.DECIDING_STATS}))
                log('interim decision: %s / %s (extend %s)'
                    % (interim.get('status'), interim.get('verdict'), interim.get('extend')))
                force = os.environ.get('RD_FORCE_EXTEND', '0') == '1' and plan.get('mechanics')
                if force:
                    out['decisions'].append(dict(kind='extension_forced', reason='RD_FORCE_EXTEND on a mechanics plan'))
                if interim.get('extend') or force:
                    done = run_rounds(done_main, ext_rounds, 'extension')
                    out['rounds_extension'] = done
    out['finished'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    out['bench_s'] = round(time.time() - bench_t0, 1)
    out['complete'] = True
    lib.write_json_atomic(OUT, out)
    for new_id in built.values():
        ctrl.FreeTargetResource(new_id)
    log('bench complete: %d main rounds, %d extension rounds, %.0f s' % (out['rounds_main'], out['rounds_extension'], out['bench_s']))
    return 0


lib.run_main(main, log)
