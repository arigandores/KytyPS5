"""reread_vform.py - F2c (HPP-310): the reading of the three F2c tags printed BESIDE the sealed verdict, with only the V-side form
member changed (variant of the executor, NOT the verdict of record).  The sealed f2c_b26.form_of demands >= 1 line
'PipelinePrecache: N recipes -> ' in a V arm; p.254(e) names a positive control only for W (no such line).  In f2c_a/f2c_c the
precache was on but had no usable recipes for 5821482a (variant_fixb26 had no pipelines.bin; the root file: 'stale recipes
(signature mismatch), ignored'), so that line could not appear.  Variant: V form ok when the log has >= 1 'PipelinePrecache:'
line of any kind (the precache code ran); W unchanged (0 'N recipes -> ' lines).  Sealed files are imported sha-checked, not
edited.  ASCII only.  usage: python reread_vform.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f2c_read as R  # noqa: E402

sc = R.load(R.SC142, R.SC142_SHA, 'sc142')
b = R.load(R.B26, R.B26_SHA, 'f2c_b26')
sealed_form = b.form_of


def any_precache(path):
    n = 0
    with open(path, 'rb') as f:
        for line in f:
            if line.startswith(b'PipelinePrecache:'):
                n += 1
    return n


for tag in ('f2c_a', 'f2c_b', 'f2c_c'):
    lp = os.path.join(HERE, 'log_%s.txt' % tag)
    nany = any_precache(lp)
    arm = R.TAGS[tag]['arm']
    rs = R.read_tag(tag, HERE, sc, b)
    b.form_of = (lambda lines, a, nany=nany: (nany >= 1) if a == 'V' else sealed_form(lines, a))
    rv = R.read_tag(tag, HERE, sc, b)
    b.form_of = sealed_form
    print('%s arm %s: PipelinePrecache lines any kind %d, "N recipes ->" %d' % (tag, arm, nany, rs['b26']['precache_lines']))
    print('  sealed (verdict of record): letter %s, p.256 rule %s' % (rs['verdict_letter'], rs['verdict_variant']))
    print('  executor variant (V form = any PipelinePrecache line): letter %s, p.256 rule %s; B26 %s / %s' % (
        rv['verdict_letter'], rv['verdict_variant'], rv['b26']['verdict_letter'], rv['b26']['verdict_variant']))
