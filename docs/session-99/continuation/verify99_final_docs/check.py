from pathlib import Path
import json, hashlib, subprocess, re
root=Path('C:/kyty/KytyPS5'); s=Path('C:/kyty/s99'); arc=root/'docs/session-99'; out=s/'verify99_final_docs'
def js(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*args): return subprocess.check_output(['git','-C',str(root),*args]).decode('utf-8')
report={}; errors=[]
old=json.loads(git('show','HEAD:docs/session-99/canonical-sha256.json')); new=js(arc/'canonical-sha256.json')
report['canonical_counts']=[len(old),len(new)]
report['old_entries_unchanged']=all(new.get(k)==v for k,v in old.items())
for k,v in new.items():
 p=arc/k
 if not p.is_file() or p.stat().st_size!=v['bytes'] or sha(p)!=v['sha256']: errors.append('canonical:'+k)
small=js(arc/'continuation/small-sha256.json')['artifacts']; raw=js(arc/'continuation/raw-sha256.json')['artifacts']
report['small_count']=len(small); report['raw_count']=len(raw); report['raw_bytes']=sum(v['bytes'] for v in raw.values())
for k,v in small.items():
 p=arc/'continuation'/k
 if p.stat().st_size!=v['bytes'] or sha(p)!=v['sha256']: errors.append('small:'+k)
report['archive_actual_count']=len([p for p in (arc/'continuation').rglob('*') if p.is_file()])
report['archive_max_file']=max((p.stat().st_size,str(p.relative_to(arc))) for p in (arc/'continuation').rglob('*') if p.is_file())
for k,v in raw.items():
 p=Path(v['location'])
 if not p.is_file() or p.stat().st_size!=v['bytes']: errors.append('raw_size:'+k)
report['raw_sha_scope']='All raw paths/sizes checked; no duplicate 3.2GB rehash, freshly hashed by archive task.'
report['facts_equal']=(s/'FACTS.md').read_bytes()==(root/'docs/local-session-99.md').read_bytes()==(arc/'continuation/FACTS.md').read_bytes()
game=Path('C:/Users/<user>/OneDrive/Desktop/ps5 em')
report['agents_claude_equal']=(game/'AGENTS.md').read_bytes()==(game/'CLAUDE.md').read_bytes()
ag=(game/'AGENTS.md').read_text(encoding='utf-8-sig'); ho=(game/'HANDOFF.md').read_text(encoding='utf-8-sig')
report['latest_session_numbers']=re.findall(r'^Дата:.*?\*\*Сессия\s*(\d+)',ag,re.M)[:5]
report['handoff_final_block_equals_agents']=ag[ag.index('Дата:'):ag.index('Дата:',ag.index('Дата:')+1)].strip()==ho[ho.rindex('Дата:'):].strip()
report['seals']={p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in (s/'pred').glob('*.md')}
for tag in ['bf99g','bf99h','bf99e','eng99a4','eng99c1','eng99c2','aa99plain']:
 d=js(s/'settled_runs'/f'{tag}_score.json')
 report[tag]={k:v for k,v in d.items() if k not in ['selection','technical','strict','reported_original','raw_sha256','source_artifact','aa_artifact','pred04_source_replay'] and not isinstance(v,(dict,list))}
 report[tag]['dict_keys']={k:list(v) for k,v in d.items() if isinstance(v,dict)}
 report[tag]['controls']={k:{'pass':sum(x is True for x in d[k].values()),'total':len(d[k]),'failed':{n:x for n,x in d[k].items() if x is not True}} for k in ['technical','strict'] if k in d}
 for k in ['metrics','endpoint','decision','reported_image_birth_proxies','selection','reported_original','reported_whole_window']:
  if k in d: report[tag][k]=d[k]
 if tag in ['bf99g','bf99h']: report[tag]['parent_recount']=js(s/'settled_runs'/f'{tag}_parent_recount.json')
report['combined']=js(s/'settled_runs/combined99_score.json')
report['video']={n:{'frames':(d:=js(s/n/'report.json'))['frames'],'events':len(d['events'])} for n in ['video99_full','video99_base_full']}
report['cpp_numstat']=git('diff','--numstat','--','src')
report['staged']=git('diff','--cached','--name-only')
report['installed']={'bytes':(game/'kyty_emulator.exe').stat().st_size,'sha256':sha(game/'kyty_emulator.exe')}
report['encoding_suspect_lines']=[(i,t) for i,t in enumerate((s/'FACTS.md').read_text(encoding='utf-8-sig').splitlines(),1) if 'user independently' in t or i==1]
for key in ['old_entries_unchanged','facts_equal','agents_claude_equal','handoff_final_block_equals_agents']:
 if not report[key]: errors.append(key)
report['errors']=errors
(out/'checks.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in report.items() if k not in ['bf99g','bf99h','bf99e','eng99a4','eng99c1','eng99c2','aa99plain']},indent=2,ensure_ascii=True))
for tag in ['bf99g','bf99h','bf99e','eng99a4','eng99c1','eng99c2','aa99plain']:
 print(tag,json.dumps({k:v for k,v in report[tag].items() if k not in ['selection','reported_original','dict_keys','reported_whole_window']},ensure_ascii=True))
