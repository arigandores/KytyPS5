"""Session 102, M5 (pred/01_m5_bench.md V-c): which shader module every draw / dispatch runs.

    RD_CAP=<rdc> RD_OUT=<json> "C:/Program Files/RenderDoc/qrenderdoc.exe" --python C:/kyty/s102/rd_m5_find.py

For every draw (Drawcall or MeshDispatch) and every dispatch of the capture it records the
event id, the kind, the PS / VS / MS module of a draw and the CS module of a dispatch; for every
module its stage, SPIR-V byte size and md5(refl.rawBytes) - the md5 m5_plan.py matches against
arm A (V-c).  The raw module bytes are dumped to RD_DUMP_DIR/<md5>.spv (default
<dir of RD_OUT>/modules) so m5_plan.py can scan them and the mechanics test can rebuild them.

Two ways to find the module of an event:
  sd      (default) walk the structured file once: pipeline creation chunks give pipeline ->
          modules, vkCmdBindPipeline per (command buffer, bind point) gives event -> pipeline.
          Seconds for the whole capture.  It is then CROSS-CHECKED by real replay
          (SetFrameEvent + GetPipelineState) on one event of every distinct module and on
          RD_VERIFY_N (default 64) further events spread over the frame; a single mismatch
          discards the sd result and falls back to replay for every event.
  replay  SetFrameEvent + GetPipelineState on every event, as C:/kyty/scripts/rd_find.py does:
          0.2-0.7 s an event on a 5.7 GB capture, i.e. about 1.5 h for 12 800 events.

Env: RD_CAP, RD_OUT (required); RD_MODE=sd|replay; RD_VERIFY_N; RD_DUMP_DIR ('0' = no dump);
     RD_SHA=0 skips the capture sha256 (mechanics only).  Log: <RD_OUT>.log.
"""
import os
import sys
import time
import hashlib
import random

sys.dont_write_bytecode = True
sys.path.insert(0, 'C:/kyty/s102')
import m5_rdlib as lib  # noqa: E402

OUT = lib.env_required('RD_OUT')
log = lib.Log(OUT + '.log')


def sd_mapping(rd, ctrl, actions, log):
    """event id -> {stage: module id string} from the structured file alone."""
    sf = ctrl.GetStructuredFile()
    chunks = sf.chunks
    pipeline_modules = {}
    stage_of_bit = {'VK_SHADER_STAGE_VERTEX_BIT': 'vs', 'VK_SHADER_STAGE_FRAGMENT_BIT': 'ps',
                    'VK_SHADER_STAGE_COMPUTE_BIT': 'cs', 'VK_SHADER_STAGE_MESH_BIT_EXT': 'ms',
                    'VK_SHADER_STAGE_TASK_BIT_EXT': 'ts', 'VK_SHADER_STAGE_GEOMETRY_BIT': 'gs'}
    unknown_stage = set()
    for chunk in chunks:
        if chunk.name == 'vkCreateGraphicsPipelines':
            info = chunk.FindChild('CreateInfo')
            pipeline = str(chunk.FindChild('Pipeline').AsResourceId())
            stages = info.FindChild('pStages')
            mods = {}
            for i in range(stages.NumChildren()):
                stage = stages.GetChild(i)
                bit = stage.FindChild('stage').AsString()
                name = stage_of_bit.get(bit)
                if name is None:
                    unknown_stage.add(bit)
                    continue
                mods[name] = str(stage.FindChild('module').AsResourceId())
            pipeline_modules[pipeline] = mods
        elif chunk.name == 'vkCreateComputePipelines':
            info = chunk.FindChild('CreateInfo')
            pipeline = str(chunk.FindChild('Pipeline').AsResourceId())
            pipeline_modules[pipeline] = {'cs': str(info.FindChild('stage').FindChild('module').AsResourceId())}
    if unknown_stage:
        log('sd: stages ignored:', sorted(unknown_stage))
    log('sd: %d pipelines from creation chunks' % len(pipeline_modules))

    # Every API event belongs to exactly one action; walk them in event order.
    events = []
    for action in actions:
        for event in action.events:
            events.append((event.eventId, event.chunkIndex))
    events.sort()
    bound = {}          # (command buffer, bind point) -> pipeline id string
    mapping = {}
    wanted = {a.eventId: lib.action_kind(rd, a) for a in actions if lib.action_kind(rd, a)}
    null = str(rd.ResourceId.Null())
    for eid, index in events:
        chunk = chunks[index]
        name = chunk.name
        if name == 'vkCmdBindPipeline':
            cmd = str(chunk.FindChild('commandBuffer').AsResourceId())
            point = chunk.FindChild('pipelineBindPoint').AsString()
            bound[(cmd, 'compute' if 'COMPUTE' in point else 'graphics')] = str(
                chunk.FindChild('pipeline').AsResourceId())
        elif name == 'vkBeginCommandBuffer':
            cmd = chunk.FindChild('commandBuffer')
            if cmd is not None:
                key = str(cmd.AsResourceId())
                bound.pop((key, 'compute'), None)
                bound.pop((key, 'graphics'), None)
        if eid in wanted:
            cmd_obj = chunk.FindChild('commandBuffer')
            if cmd_obj is None:
                mapping[eid] = None     # e.g. an "Indirect sub-command" event: resolved by replay
                continue
            cmd = str(cmd_obj.AsResourceId())
            point = 'compute' if wanted[eid] == 'dispatch' else 'graphics'
            pipeline = bound.get((cmd, point))
            mods = pipeline_modules.get(pipeline) if pipeline else None
            if mods is None:
                mapping[eid] = None
                continue
            if wanted[eid] == 'dispatch':
                mapping[eid] = {'cs': mods.get('cs', null)}
            else:
                mapping[eid] = {k: mods.get(k, null) for k in ('ps', 'vs', 'ms', 'ts')}
    return mapping


def replay_one(rd, ctrl, eid, kind):
    ctrl.SetFrameEvent(eid, True)
    pipe = ctrl.GetPipelineState()
    if kind == 'dispatch':
        return {'cs': str(pipe.GetShader(rd.ShaderStage.Compute))}
    return {'ps': str(pipe.GetShader(rd.ShaderStage.Pixel)),
            'vs': str(pipe.GetShader(rd.ShaderStage.Vertex)),
            'ms': str(pipe.GetShader(rd.ShaderStage.Mesh)),
            'ts': str(pipe.GetShader(rd.ShaderStage.Task))}


def main():
    import renderdoc as rd
    lib.hide_ui(log)
    cap_path = os.environ.get('RD_CAP', '').strip()
    if not cap_path:
        raise SystemExit('RD_CAP is required (this tool never picks "the newest capture")')
    mode = os.environ.get('RD_MODE', 'sd').strip().lower()
    verify_n = int(os.environ.get('RD_VERIFY_N', '64'))
    dump_dir = (os.environ.get('RD_DUMP_DIR', '').strip()
                or os.path.join(os.path.dirname(OUT), 'modules')).replace('\\', '/')
    if dump_dir == '0':
        dump_dir = None
    header = dict(tool='rd_m5_find', capture=cap_path, capture_bytes=os.path.getsize(cap_path),
                  mode_requested=mode, started=time.strftime('%Y-%m-%dT%H:%M:%S'),
                  replay_optimisation=lib.replay_opt_name(),
                  renderdoc=rd.GetVersionString() if hasattr(rd, 'GetVersionString') else None,
                  complete=False)
    if os.environ.get('RD_SHA', '1') != '0':
        t = time.time()
        header['capture_sha256'] = lib.sha256_file(cap_path)
        log('capture sha256 %s (%.1f s)' % (header['capture_sha256'], time.time() - t))
    else:
        header['capture_sha256'] = None
    t = time.time()
    cap, ctrl = lib.open_capture(rd, cap_path, log)
    header['open_s'] = round(time.time() - t, 2)
    actions = list(lib.walk_actions(ctrl.GetRootActions()))
    work = [(a.eventId, lib.action_kind(rd, a), a) for a in actions if lib.action_kind(rd, a)]
    work.sort(key=lambda row: row[0])
    log('actions %d, draws+dispatches %d' % (len(actions), len(work)))
    sf = ctrl.GetStructuredFile()

    mapping = None
    timing = {}
    if mode == 'sd':
        t = time.time()
        mapping = sd_mapping(rd, ctrl, actions, log)
        timing['sd_s'] = round(time.time() - t, 2)
        unresolved = [eid for eid, kind, _ in work if mapping.get(eid) is None]
        log('sd: %d events mapped, %d unresolved (resolved by replay)' % (len(work) - len(unresolved), len(unresolved)))
        kind_of = dict((e, k) for e, k, _ in work)
        t = time.time()
        for eid in unresolved:
            mapping[eid] = replay_one(rd, ctrl, eid, kind_of[eid])
        timing['unresolved_replay_s'] = round(time.time() - t, 2)
        header['sd_unresolved'] = len(unresolved)
        # Cross-check: one event per distinct (kind, module tuple) plus a spread sample.
        first_of = {}
        for eid, kind, _ in work:
            key = (kind, tuple(sorted(mapping[eid].items())))
            first_of.setdefault(key, eid)
        check = set(first_of.values())
        rng = random.Random(102)
        pool = [eid for eid, _, _ in work if eid not in check]
        check.update(rng.sample(pool, min(verify_n, len(pool))))
        mismatches = []
        t = time.time()
        for eid in sorted(check):
            real = replay_one(rd, ctrl, eid, kind_of[eid])
            if real != mapping[eid]:
                mismatches.append(dict(eid=eid, sd=mapping[eid], replay=real))
        timing['verify_s'] = round(time.time() - t, 2)
        header['sd_verify'] = dict(checked=len(check), distinct_module_sets=len(first_of),
                                   mismatches=len(mismatches), first_mismatches=mismatches[:20])
        log('sd verify: %d events checked (%d distinct module sets), %d mismatches, %.1f s'
            % (len(check), len(first_of), len(mismatches), timing['verify_s']))
        if mismatches:
            log('sd mapping REJECTED - falling back to replay for every event')
            mapping = None
    if mapping is None:
        header['mode_used'] = 'replay'
        mapping = {}
        t = time.time()
        for n, (eid, kind, _) in enumerate(work):
            mapping[eid] = replay_one(rd, ctrl, eid, kind)
            if n % 500 == 0:
                log('replay %d / %d (%.0f s)' % (n, len(work), time.time() - t))
        timing['replay_s'] = round(time.time() - t, 2)
    else:
        header['mode_used'] = 'sd'

    null = str(rd.ResourceId.Null())
    resources = lib.resource_map(ctrl)
    modules = {}
    events = []
    for eid, kind, action in work:
        mods = mapping[eid]
        row = dict(eid=eid, kind=kind, api=sf.chunks[action.events[-1].chunkIndex].name if action.events else None)
        if action.flags & rd.ActionFlags.MeshDispatch:
            row['mesh'] = True
        if action.flags & rd.ActionFlags.Indirect:
            row['indirect'] = True
        for stage, rid in sorted(mods.items()):
            if rid == null:
                continue
            row[stage] = rid
            entry = modules.get(rid)
            if entry is None:
                entry = modules[rid] = dict(stage=stage, n_events=0, first_eids=[])
            entry['n_events'] += 1
            if len(entry['first_eids']) < 8:
                entry['first_eids'].append(eid)
        events.append(row)
    t = time.time()
    if dump_dir:
        os.makedirs(dump_dir, exist_ok=True)
    for rid, entry in modules.items():
        module = resources.get(rid)
        if module is None:
            entry['error'] = 'not in GetResources()'
            continue
        refl_stage, raw = lib.module_reflection(rd, ctrl, module)
        entry['size'] = len(raw)
        entry['md5'] = hashlib.md5(raw).hexdigest()
        entry['refl_stage'] = refl_stage
        if refl_stage != entry['stage']:
            entry['stage_conflict'] = True
        if dump_dir and raw:
            path = os.path.join(dump_dir, entry['md5'] + '.spv').replace('\\', '/')
            if not os.path.exists(path):
                with open(path, 'wb') as stream:
                    stream.write(raw)
            entry['dump'] = path
    timing['modules_s'] = round(time.time() - t, 2)
    header.update(timing=timing, n_events=len(events), n_modules=len(modules), dump_dir=dump_dir,
                  counts=dict(draw=sum(1 for e in events if e['kind'] == 'draw'),
                              dispatch=sum(1 for e in events if e['kind'] == 'dispatch'),
                              mesh=sum(1 for e in events if e.get('mesh'))),
                  finished=time.strftime('%Y-%m-%dT%H:%M:%S'), complete=True)
    header['modules'] = modules
    header['events'] = events
    lib.write_json_atomic(OUT, header)
    log('wrote %s: %d events, %d modules' % (OUT, len(events), len(modules)))
    return 0


lib.run_main(main, log)
