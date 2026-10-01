"""Session 145 link 1b rework 1 (HPP-379, ROADMAP s122 item 301): the togit145c copy and privacy scan over the files of the
rework (FACTS.md, times.txt, the runner, the two mutant reports and logs).  ASCII output.
usage: togit145d.py <out.txt>"""
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, 'C:/kyty/s145/step1b')
import togit145c as T  # noqa: E402

T.FILES = ['FACTS.md'] + ['step1b/' + f for f in (
    'times.txt', 'rm1b2.py', 'facts1b10.md', 'togit145d.py', 'mut_only1b_gate2.txt', 'mut_only1b_gate2.log',
    'mut_only1b_sc3.txt', 'mut_only1b_sc3.log')]

if __name__ == '__main__':
    T.main()
