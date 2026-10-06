"""Track S link S18c2 (HPP-654; ROADMAP s122 item 586 (g)-(d)): the reader of the extra tag s18_w2 - W Sky Garden with the S-replay rebuild
under the validation layer (S18a2 b3cee576, input cat_full from the catalogue replay_known, KYTY_SHADER_SEED=0, no KYTY_S_REPLAY, no
KYTY_S_REPLAY_TEST).  The group W2 is built from the members R and W of the S18c reader: this module loads the sealed S18c reader
C:/kyty/s288/s18c/s18c_read.py UNCHANGED (its sha256 is an admission row; the S18c seal docs/track-s/s18c.md section 7 stays whole) and adds
only the tag s18_w2, its paths (root C:/kyty/s288/s18c2) and the group W2.  Seal: docs/track-s/s18c2.md = pred/s18c2_seal.md.
Members of item 586 (g) (named before the data):
  (1) a line 'ShaderReplay: rebuild records=' and no line 'rebuild skipped' and no line 'ShaderSeed: installed' (log, stdout);
  (2) prepared / records >= 0.90; identity prepared + rejected + pending = records; pipelines_bin=written;
  (3) 0 [Vulkan][E]; 0 limit lines of the layer; positive control - [Vulkan][W] > 0 and DualSrcBlend: supported=1 enabled=1 before the
      first GuestOut; VALIDATION_STOP (the process ended before the end of the hold with a [Vulkan][E] line) - NO;
  (4) entered (Level has started: underwater_aerial_garden, outcome ok); the process lived to the end of the hold 310 s; 0 death markers.
Report rows: the preparation screen, frames >= 1 s, the rebuild numbers, the mode line, the translation folder, pipelines.bin after the run.
NO verdict (S18d HPP-645).
usage: python s18c2_read.py s18_w2 [--json <out>]   |   python s18c2_read.py --table
  Paths: S18C2_ROOT (default C:/kyty/s288/s18c2), S18C2_SRC_ROOT (the S18c root, default C:/kyty/s288/s18c), S18C2_SEAL, S18C2_BASE (the
  S18c reader), S18C_BIN (the binary copy, read by the S18c reader).  ASCII output only."""
import hashlib
import importlib.util
import json
import os
import sys

BASE = os.environ.get('S18C2_BASE', 'C:/kyty/s288/s18c/s18c_read.py')
BASE_SHA = '16570bed3667e5a1c9a9e62a92fe2dc03f27453cb4c8d8322edca73d9c026693'   # s18c_read.py of the S18c seal, section 7
ROOT2 = os.environ.get('S18C2_ROOT', 'C:/kyty/s288/s18c2')
SRC_ROOT = os.environ.get('S18C2_SRC_ROOT', 'C:/kyty/s288/s18c')
SEAL2 = os.environ.get('S18C2_SEAL', 'C:/kyty/s288/s18c2/pred/s18c2_seal.md')
TAG = 's18_w2'
HOLD = 310
KNOWN_DIR = 'replay_known'
KNOWN = (('replay.45.bin', 6250527, '12cb378741308d1a82133be521311882881d1bbf04aff649cccc6d8e6607fee1'),
         ('replay.46.bin', 6253395, '332a2f2d6aef0e8b64ccfe366d87df3476117abaf3b6aaf736ffbec2befc7c9a'),
         ('replay.cur', 3, 'a5331f18877e9e1543361e44b4cb0a1f5f0ed5f8297d850bf1fcc68bd7a3ab5f'))   # c644e3ad replay_known_manifest.tsv


def _sha(path):
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''):
            h.update(b)
    return h.hexdigest()


_spec = importlib.util.spec_from_file_location('s18c_read', BASE)
R = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R)
R.ROOT = SRC_ROOT
R.SEAL_PATH = SEAL2
R.SPEC[TAG] = dict(level=R.SKY, form='w', hold=HOLD, state='cat_full', prev=None, env={'KYTY_SHADER_SEED': '0'}, group='W2')
_paths = R.paths
_w_rows = R.w_rows


def paths(tag):
    """The S18c paths of a tag; s18_w2 lives under ROOT2, every other tag (s18_c19, its state and read.json) under the S18c root."""
    if tag != TAG:
        return _paths(tag)
    old = R.ROOT
    R.ROOT = ROOT2
    try:
        return _paths(tag)
    finally:
        R.ROOT = old


def files_of(d):
    """{name: (size, sha256)} of the files of a folder ({} when absent)."""
    out = {}
    if os.path.isdir(d):
        for n in sorted(os.listdir(d)):
            fp = os.path.join(d, n)
            if os.path.isfile(fp):
                out[n] = (os.path.getsize(fp), _sha(fp))
    return out


def known_rows(rows):
    """Admission: the S18c reader is the sealed one; replay_known = the manifest c644e3ad and = state/s18_c19/replay (item 569 (d)(3))."""
    bs = _sha(BASE)
    rows.a('S18c reader s18c_read.py = the S18c seal (sha256 %s)' % BASE_SHA[:16], bs == BASE_SHA, bs)
    got = files_of(os.path.join(SRC_ROOT, KNOWN_DIR))
    want = dict((n, (s, h)) for n, s, h in KNOWN)
    rows.a('catalogue %s = manifest c644e3ad (3 files, size, sha256)' % KNOWN_DIR, got == want, 'files %d' % len(got))
    c19 = R.saved_files(R.LAST_CAP)
    rows.a('catalogue %s = state/%s/replay byte for byte' % (KNOWN_DIR, R.LAST_CAP), got == c19 and len(got) > 0,
           'files %d / %d' % (len(got), len(c19)))


def rebuild_line(r):
    """The last 'ShaderReplay: rebuild records=' line (a dict) or None."""
    rb = [d for _, d in r['rebuild'] if 'records' in d]
    return rb[-1] if rb else None


def validation_stop(r, att):
    """VALIDATION_STOP: the process ended before the end of the hold and the log carries a [Vulkan][E] line."""
    return r['vke'] > 0 and not R.lived(att, HOLD)


def w2_rows(rows, tag, r, so, att, extra):
    """s18_w2 (item 586 (g)): the members (1)-(4) and the report rows."""
    spec = R.SPEC[tag]
    known_rows(rows)
    rb = rebuild_line(r)
    rows.m('W2 (1) a line ShaderReplay: rebuild records=', rb is not None, 'rebuild lines %d' % len(r['rebuild']))
    rows.m('W2 (1) no line rebuild skipped', not r['skipped'], r['skipped'][:2])
    rows.m('W2 (1) no line ShaderSeed: installed (log, stdout)', r['seed'] == 0 and so['seed'] == 0, '%d / %d' % (r['seed'], so['seed']))
    rb = rb or {}
    recs, prep, rej, pend = R.num(rb, 'records'), R.num(rb, 'prepared'), R.num(rb, 'rejected'), R.num(rb, 'pending')
    share = None if (prep is None or not recs) else prep / float(recs)
    rows.m('W2 (2) share prepared / records >= 0.90', None if share is None else share >= R.SHARE_MIN,
           'share %s = %s / %s' % (None if share is None else round(share, 4), prep, recs))
    ident = None if None in (recs, prep, rej, pend) else prep + rej + pend == recs
    rows.m('W2 (2) identity prepared + rejected + pending = records', ident, '%s + %s + %s = %s' % (prep, rej, pend, recs))
    rows.m('W2 (2) pipelines_bin=written', rb.get('pipelines_bin') == 'written', rb.get('pipelines_bin'))
    rows.m('W2 (3) 0 [Vulkan][E]', r['vke'] == 0, r['vke'])
    rows.m('W2 (3) 0 limit lines of the layer', r['vk_limit'] == 0, r['vk_limit'])
    dual_before = [x for x in r['dual'] if r['first_guest'] is not None and x[0] < r['first_guest'] and x[1] == 1 and x[2] == 1]
    rows.m('W2 (3) positive control of the layer: [Vulkan][W] > 0 and DualSrcBlend: supported=1 enabled=1 before the first GuestOut',
           r['vkw'] > 0 and len(dual_before) >= 1, 'W %d, dual %s, first GuestOut %s' % (r['vkw'], r['dual'][:2], r['first_guest']))
    vs = validation_stop(r, att)
    rows.m('W2 (3) no VALIDATION_STOP (the process ended before the end of the hold with a [Vulkan][E] line)', not vs,
           'E %d outcome %s hold_s %s' % (r['vke'], att.get('outcome'), att.get('hold_s')))
    rows.m('W2 (4) entered (Level has started: %s, outcome ok)' % spec['level'], R.entered(r, att), 'entry line %s' % r['entry_line'])
    rows.m('W2 (4) the process lived to the end of the hold (%d s)' % spec['hold'], R.lived(att, spec['hold']),
           'outcome %s hold_exit %s hold_s %s' % (att.get('outcome'), att.get('hold_exit'), att.get('hold_s')))
    rows.m('W2 (4) 0 death markers (log, stdout)', R.deaths(r, so) == 0, (r['death'] + so['death'])[:3])
    md = r['mode'][0][1] if r['mode'] else {}
    rows.r('mode line (reference)', md)
    rows.r('translation cache directory = %s (reference)' % R.DIR1, R.directory_ok(r, R.DIR1))
    rows.r('rebuild under the layer: records prepared rejected pending perms_new perms_cached translate_ms wall_ms', ' '.join(
        str(rb.get(k)) for k in ('records', 'prepared', 'rejected', 'pending', 'perms_new', 'perms_cached', 'translate_ms', 'wall_ms')))
    rows.r('frames >= 1 s after the first scene frame / from the entry line (under the layer, reference)', '%d / %d' % (
        r['k2_after'], r['k2_entry']))
    st = R.text(paths(tag)['state_out'])
    f19 = R.state_s17c.parse(st).get('f19', {}) if st is not None else None
    rows.r('%s after the run (state_out.txt)' % R.DIR1, f19)
    extra['rebuild'] = dict((k, rb.get(k)) for k in ('records', 'prepared', 'rejected', 'pending', 'perms_new', 'perms_cached',
                                                     'pipelines_bin', 'wall_ms'))
    extra['prep_ms'] = r['prep']


def w_rows(rows, tag, r, so, att, extra):
    if R.SPEC[tag]['group'] == 'W2':
        return w2_rows(rows, tag, r, so, att, extra)
    return _w_rows(rows, tag, r, so, att, extra)


R.paths = paths
R.w_rows = w_rows


def table():
    R.table()
    print('S18c2 tag %s (seal docs/track-s/s18c2.md, item 586 (g); no verdict - S18d HPP-645)' % TAG)
    d = R.read_json_of(TAG)
    if d is None:
        print('  %-8s W2   NOT READ' % TAG)
        return 0
    print('  %-8s W2   %-28s READING %s' % (TAG, R.SKY, d['reading']))
    for name, ok, det in d['members']:
        print('      %-15s %s | %s' % (R.yn(ok), R.asc(name), R.asc(det)[:200]))
    return 0


def main(argv):
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == '--table':
        return table()
    if argv[0] != TAG:
        print('usage: s18c2_read.py %s [--json <out>] | --table' % TAG)
        return 2
    rows, meta = R.read_tag(TAG)
    print('S18c2 reader over s18c_read.py sha256 %s' % _sha(BASE))
    R.print_rows(TAG, rows, meta)
    if '--json' in argv:
        with open(argv[argv.index('--json') + 1], 'w') as f:
            json.dump(R.to_json(TAG, rows, meta), f, indent=1)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
