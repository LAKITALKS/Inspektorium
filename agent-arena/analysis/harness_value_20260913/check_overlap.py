"""Read-only historical corpus search inventory; emits only relevant hit locations."""
from pathlib import Path
import hashlib,json,re,subprocess
P=Path(__file__).parent;root=P.resolve().parents[1]
sources=json.loads((P/'candidate_authoring/sources.json').read_text());bank=json.loads((P/'candidate_authoring/candidate_bank.json').read_text())
patterns={s['authoring_id']:[s['doi'].lower(),s['title'].lower().strip('.')] for s in sources}
terms={1:['semaglutide','step 1'],2:['mediterranean','greek population'],3:['dexamethasone','recovery trial'],4:['dapagliflozin','dapa-hf'],5:['dash diet','dash feeding'],6:['nicotinamide','nad+','stem-cell','stem cell'],7:['semaglutide'],8:['vital trial','vitamin d'],9:['tranexamic','crash-2'],10:['pembrolizumab','keynote-024'],11:['attire','albumin'],12:['team-ad','memantine','vitamin e'],13:['sleep disturbance','levenson'],14:['nut consumption','nuts','nurses\' health'],15:['nutrinet','ultraprocessed','ultra-processed'],16:['all our families','screen time','screen-time'],17:['sister study','artificial light','2019.0571'],18:['green space','greenspace'],19:['tmc1','nature25164'],20:['dystrophin','aad5143'],21:['chondroitinase'],22:['cd47','sirpa','sirpα'],23:['channelrhodopsin','rhodopsin'],24:['mcc950','nlrp3']}
for i,ts in terms.items():patterns[f'C{i:02}']+=ts
files=[]
for directory in ('tasks','analysis','research','cases','.agent_arena'):
 if not (root/directory).exists():continue
 for p in (root/directory).rglob('*'):
  if p.is_file() and p.suffix.lower() in ('.json','.jsonl','.yaml','.yml','.md','.txt','.csv','.py') and P.resolve() not in p.resolve().parents:files.append(p)
files+=list(root.glob('Dataset *.json'))+list(root.glob('pilot_dataset*.json'))+list(Path('/tmp/arena-historical-pdf-texts').glob('*.txt'))
rows=[];hits=[]
for p in sorted(set(files)):
 b=p.read_bytes();text=b.decode('utf-8',errors='replace').lower();rows.append({'path':str(p),'sha256':hashlib.sha256(b).hexdigest()})
 for cid,ps in patterns.items():
  found=[t for t in ps if t in text]
  if found:hits.append({'candidate':cid,'path':str(p),'terms':found})
(P/'candidate_authoring/overlap_corpus_inventory.json').write_text(json.dumps({'files':rows,'files_count':len(rows),'hits':hits,'limits':'Literal DOI/title/keyword screening plus author semantic inspection of hits. PDFs extracted with pypdf; no claim about foundation pretraining.'},indent=2)+'\n')
print('files',len(rows),'hits',len(hits))
for cid in patterns:
 h=[x for x in hits if x['candidate']==cid];print(cid,len(h),[(Path(x['path']).name,x['terms']) for x in h if Path(x['path']).suffix in ('.yaml','.txt')][:20])
