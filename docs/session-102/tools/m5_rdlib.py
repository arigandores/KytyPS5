"""Session 102, M5: helpers shared by the three qrenderdoc scripts of the M5 bench.

    rd_m5_find.py   - which shader module every draw / dispatch of a capture runs
    rd_m5_bench.py  - the sealed timing bench (pred/01_m5_bench.md s5 as amended by pred/02 s4)
    rd_m5_equal.py  - output equality V-e (pred/01_m5_bench.md s6 as amended by pred/02 s2)

Pure helpers (compare_bytes, the seal checks) import nothing from RenderDoc and are tested
offline by test_m5_102.py.

Runs inside qrenderdoc's embedded Python 3.8 (RenderDoc 1.46): standard library only, no
numpy, no 3.9+ syntax.  Each script inserts C:/kyty/s102 into sys.path before importing this.

RenderDoc API facts this file relies on (checked on the installed 1.46, session 102):
  * PipeState keeps BOTH the graphics and the compute pipeline: GetShader(Pixel) at a dispatch
    returns the PS of whatever graphics pipeline is still bound, so the stage must be chosen by
    the ACTION kind, never by "which stage is non-null".
  * Mesh draws (vkCmdDrawMeshTasksEXT) carry ActionFlags.MeshDispatch and NOT Drawcall.
  * ReplayController.GetShader(ResourceId.Null(), module, entry) returns the reflection (and so
    rawBytes) of a module without SetFrameEvent; SetFrameEvent itself costs 0.2-0.7 s per event
    on a 5.7 GB Sky Garden capture.
  * FetchCounters([EventGPUDuration]) returns one CounterResult per event, CompType.Float and
    CounterUnit.Seconds.
  * There is no public ResourceId constructor from an integer: ids are resolved by str() through
    GetResources().
"""
import hashlib
import json
import os
import sys
import time
import traceback

DEFAULT_CAPTURE_DIR = 'C:/Users/<user>/OneDrive/Desktop/ps5 em/_RenderDoc'


class Log:
    """Line log with a wall clock; flushed on every line so a crash keeps everything."""

    def __init__(self, path):
        self.path = path
        self.t0 = time.time()
        self.handle = open(path, 'w', encoding='utf-8')

    def __call__(self, *parts):
        self.handle.write('[%9.2f] %s\n' % (time.time() - self.t0, ' '.join(str(p) for p in parts)))
        self.handle.flush()

    def close(self):
        try:
            self.handle.close()
        except Exception:
            pass


def hide_ui(log=None):
    """qrenderdoc opens its main window before running --python; hide it (as rd_cs_time.py)."""
    try:
        from PySide2 import QtWidgets
        app = QtWidgets.QApplication.instance()
        if app is None:
            return
        for widget in app.topLevelWidgets():
            widget.hide()
    except Exception as error:  # shiboken prints a harmless path warning here
        if log is not None:
            log('hide_ui:', error)


def sha256_file(path, chunk=16 << 20):
    digest = hashlib.sha256()
    with open(path, 'rb') as stream:
        while True:
            block = stream.read(chunk)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def write_json_atomic(path, data):
    """Write to <path>.tmp and rename, so a reader (or a crash) never sees half a file."""
    temp = path + '.tmp'
    with open(temp, 'w', encoding='utf-8') as stream:
        json.dump(data, stream, indent=1, sort_keys=False)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def compare_bytes(a, b):
    """(equal, first differing byte offset, number of differing bytes) - fast on hundreds of MB.

    The XOR of the two little-endian integers keeps byte i at index i, so the first differing
    offset is the number of leading zero bytes and the differing count is the non-zero bytes.
    A length difference counts every byte past the common length as differing."""
    if a == b:
        return True, None, 0
    n = min(len(a), len(b))
    extra = abs(len(a) - len(b))
    if n == 0:
        return False, 0, extra
    x = (int.from_bytes(a[:n], 'little') ^ int.from_bytes(b[:n], 'little')).to_bytes(n, 'little')
    ndiff = n - x.count(0)
    first = n - len(x.lstrip(bytes(1))) if ndiff else n
    return False, first, ndiff + extra


def seal_hashes():
    """sha256 of both sealed texts (pred/01 and its addendum pred/02), recorded by every tool."""
    import m5_102
    return dict(pred=dict(path=m5_102.PRED, sha256=_sha_or_none(m5_102.PRED), want=m5_102.PRED_SHA),
                addendum=dict(path=m5_102.ADDENDUM, sha256=_sha_or_none(m5_102.ADDENDUM),
                              want=m5_102.ADDENDUM_SHA))


def _sha_or_none(path):
    try:
        return sha256_file(path)
    except OSError:
        return None


def require_seals(log=None):
    """Refuse to run unless both sealed texts are byte-for-byte the sealed ones."""
    seals = seal_hashes()
    for name, row in seals.items():
        if row['sha256'] != row['want']:
            raise SystemExit('SEALED TEXT CHANGED (%s %s: %s != %s): refusing to run'
                             % (name, row['path'], row['sha256'], row['want']))
    if log is not None:
        log('seals verified: pred/01 %s, pred/02 %s' % (seals['pred']['sha256'][:12], seals['addendum']['sha256'][:12]))
    return seals


def env_required(name):
    value = os.environ.get(name, '').strip()
    if not value:
        raise SystemExit('environment variable %s is required' % name)
    return value


REPLAY_OPT_NAMES = ('none', 'conservative', 'balanced', 'fastest')


def replay_opt_name():
    """RD_REPLAY_OPT: RenderDoc's replay optimisation level (default 'balanced', RenderDoc's own).
    'none' = ReplayOptimisationLevel.NoOptimisation: every resource is reset to its initial state
    on every replay, which is what an output comparison needs (section 'determinism' of the
    session-102 mechanics README)."""
    name = os.environ.get('RD_REPLAY_OPT', 'balanced').strip().lower() or 'balanced'
    if name not in REPLAY_OPT_NAMES:
        raise SystemExit('RD_REPLAY_OPT must be one of %s' % (REPLAY_OPT_NAMES,))
    return name


def open_capture(rd, path, log):
    rd.InitialiseReplay(rd.GlobalEnvironment(), [])
    cap = rd.OpenCaptureFile()
    result = cap.OpenFile(path, '', None)
    if result != rd.ResultCode.Succeeded:
        raise RuntimeError('OpenFile failed: %s' % result)
    options = rd.ReplayOptions()
    name = replay_opt_name()
    options.optimisation = {'none': rd.ReplayOptimisationLevel.NoOptimisation,
                            'conservative': rd.ReplayOptimisationLevel.Conservative,
                            'balanced': rd.ReplayOptimisationLevel.Balanced,
                            'fastest': rd.ReplayOptimisationLevel.Fastest}[name]
    result, ctrl = cap.OpenCapture(options, None)
    if result != rd.ResultCode.Succeeded:
        raise RuntimeError('OpenCapture failed: %s' % result)
    log('capture opened:', path, 'replay optimisation:', name)
    return cap, ctrl


def walk_actions(actions):
    for action in actions:
        yield action
        for child in walk_actions(action.children):
            yield child


def action_kind(rd, action):
    """'dispatch', 'draw' or None.  Mesh draws count as draws (they carry a PS)."""
    flags = action.flags
    if flags & rd.ActionFlags.Dispatch:
        return 'dispatch'
    if flags & (rd.ActionFlags.Drawcall | rd.ActionFlags.MeshDispatch):
        return 'draw'
    return None


def is_null(rd, rid):
    return rid is None or rid == rd.ResourceId.Null()


def rid_str(rd, rid):
    return None if is_null(rd, rid) else str(rid)


def resource_map(ctrl):
    """str(ResourceId) -> ResourceId for every resource of the capture (shaders included)."""
    return {str(r.resourceId): r.resourceId for r in ctrl.GetResources()}


def module_reflection(rd, ctrl, module):
    """(stage name, rawBytes) of a shader module without moving the replay."""
    entries = ctrl.GetShaderEntryPoints(module)
    if not entries:
        return None, b''
    refl = ctrl.GetShader(rd.ResourceId.Null(), module, entries[0])
    raw = bytes(refl.rawBytes) if refl is not None else b''
    return stage_name(rd, entries[0].stage), raw


def stage_name(rd, stage):
    names = {rd.ShaderStage.Vertex: 'vs', rd.ShaderStage.Pixel: 'ps', rd.ShaderStage.Compute: 'cs',
             rd.ShaderStage.Mesh: 'ms', rd.ShaderStage.Task: 'ts', rd.ShaderStage.Geometry: 'gs',
             rd.ShaderStage.Hull: 'hs', rd.ShaderStage.Domain: 'ds'}
    return names.get(stage, str(stage))


def stage_enum(rd, name):
    table = {'ps': rd.ShaderStage.Pixel, 'pixel': rd.ShaderStage.Pixel, 'fs': rd.ShaderStage.Pixel,
             'cs': rd.ShaderStage.Compute, 'compute': rd.ShaderStage.Compute,
             'vs': rd.ShaderStage.Vertex, 'vertex': rd.ShaderStage.Vertex,
             'ms': rd.ShaderStage.Mesh, 'mesh': rd.ShaderStage.Mesh}
    key = str(name).strip().lower()
    if key not in table:
        raise ValueError('unknown stage %r' % name)
    return table[key]


class Counters:
    """EventGPUDuration fetches, converted to microseconds, keyed by eventId."""

    def __init__(self, rd, ctrl):
        self.rd = rd
        self.ctrl = ctrl
        if rd.GPUCounter.EventGPUDuration not in ctrl.EnumerateCounters():
            raise RuntimeError('EventGPUDuration is not available on this replay')
        self.desc = ctrl.DescribeCounter(rd.GPUCounter.EventGPUDuration)

    def value_us(self, result):
        rd = self.rd
        if self.desc.resultType == rd.CompType.Float:
            value = result.value.d if self.desc.resultByteWidth == 8 else result.value.f
        else:
            value = float(result.value.u64 if self.desc.resultByteWidth == 8 else result.value.u32)
        if self.desc.unit == rd.CounterUnit.Seconds:
            value *= 1e6
        return value

    def fetch(self):
        results = self.ctrl.FetchCounters([self.rd.GPUCounter.EventGPUDuration])
        return {r.eventId: self.value_us(r) for r in results}

    def describe(self):
        rd = self.rd
        return dict(name=self.desc.name, unit=str(self.desc.unit), type=str(self.desc.resultType),
                    width=self.desc.resultByteWidth)


def run_main(main, log):
    """Run main(); log any exception; ALWAYS os._exit (qrenderdoc hangs on a normal exit)."""
    code = 2
    try:
        code = main()
    except SystemExit as stop:
        log('STOP:', stop)
        code = 3
    except Exception:
        log('EXC', traceback.format_exc())
        code = 2
    log('exit code', code)
    log.close()
    os._exit(code if isinstance(code, int) else 0)
