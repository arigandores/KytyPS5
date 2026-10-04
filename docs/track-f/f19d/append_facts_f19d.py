# F19d (HPP-548, Red Team): appends the F19d section of C:/kyty/f287/FACTS.md from the template facts_f19d.md (rule:
# the FACTS section is appended by a python script from a template; LF). Refuses if the section already exists.
import datetime, os, sys
tpl, facts = sys.argv[1], 'C:/kyty/f287/FACTS.md'
if os.path.exists('C:/kyty/SEALED_RUN.lock'):
    print('lock'); sys.exit(3)
head = '## F19d (`HPP-548`'
text = open(tpl, encoding='utf-8').read().replace('\r\n', '\n')
cur = open(facts, 'rb').read().decode('utf-8')
if head in cur:
    print('section exists'); sys.exit(2)
now = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
text = text.replace('{DATE}', now)
if not cur.endswith('\n'):
    text = '\n' + text
with open(facts, 'ab') as f:
    f.write(text.encode('utf-8'))
print('appended', now)
