"""S7: rewrite translator sources whose only difference from git HEAD is CRLF with the exact HEAD blob.
Refuses any file whose content differs beyond line endings. ASCII output only."""
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sighash_s7 import REPO, file_list  # noqa: E402


def main():
    apply = '--apply' in sys.argv
    changed = refused = 0
    for f in file_list():
        rel = os.path.relpath(f, REPO).replace(os.sep, '/')
        r = subprocess.run(['git', '-C', REPO, 'show', 'HEAD:' + rel], capture_output=True)
        if r.returncode != 0:
            continue
        disk = open(f, 'rb').read()
        if disk == r.stdout:
            continue
        if disk.replace(b'\r\n', b'\n') != r.stdout:
            print('REFUSE content differs', rel)
            refused += 1
            continue
        print('eol-only', rel)
        changed += 1
        if apply:
            with open(f, 'wb') as fh:
                fh.write(r.stdout)
    print('eol_only', changed, 'refused', refused, 'applied', 1 if apply else 0)
    sys.exit(1 if refused else 0)


if __name__ == '__main__':
    main()
