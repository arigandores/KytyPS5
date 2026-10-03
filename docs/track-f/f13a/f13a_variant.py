"""F13a (HPP-479): VARIANT OF THE EXECUTOR (not the seal) of the card end, written after f13_rd and BEFORE the f13_k call.
Why: the sealed rule of f13a_read.py ('first row < 100 after a run of >= 90 rows >= 300') took a one-row dip of draws (k 211, draws 6,
3.60 s) of f13_rd for the card end; the card ended at k 1261 (21.08 s), as in v146_08 (k 1259, 20.98 s).  The seal rows stay as they are
(printed by the letter); this script prints the same rows with
  card end (variant) = the first row with draws < 100 that STARTS a run of >= 600 consecutive rows with draws < 100 (10 s at 60 Hz) and
                       comes after a run of >= 90 consecutive rows with draws >= 300 after entry.
Everything else is f13a_read.py (imported, sha256 printed).  ASCII only.
usage: python f13a_variant.py <rd|k> <log> [<rec.idx>]"""
import hashlib, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import f13a_read as R

BLACK_RUN = 600


def card_end_variant(rows):
    run = 0
    seen = False
    i = 0
    n = len(rows)
    while i < n:
        dr = rows[i][3]
        if dr >= R.CARD_MIN:
            run += 1
            if run >= R.CARD_RUN:
                seen = True
            i += 1
            continue
        run = 0
        if seen and dr < R.BLACK_MAX:
            j = i
            while j < n and rows[j][3] < R.BLACK_MAX:
                j += 1
            if j - i >= BLACK_RUN:
                return rows[i][0]
            i = j
            continue
        i += 1
    return None


def main(argv):
    kind, logp = argv[1], argv[2]
    idxp = argv[3] if len(argv) > 3 else None
    print('variant f13a_variant.py sha256 %s reader f13a_read.py sha256 %s' % (
        hashlib.sha256(open(__file__, 'rb').read()).hexdigest(),
        hashlib.sha256(open(os.path.join(HERE, 'f13a_read.py'), 'rb').read()).hexdigest()))
    R.card_end = card_end_variant
    res = R.analyse(kind, logp, idxp)
    res['card_rule'] = 'VARIANT (first row < 100 starting a run >= %d rows < 100, after >= 90 rows >= 300)' % BLACK_RUN
    R.show(res)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
