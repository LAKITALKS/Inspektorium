"""Preregistered deterministic endpoint code. Only this post-freeze role joins gold.

Usage: .venv/bin/python analysis/harness_value_20260913/analyze.py
Read immutable raw + ledger, verify hashes, reproduce production interpretation,
validate C research checkpoint, emit rows/paired tables/metrics. No network calls.
"""
from pathlib import Path
import csv,json,math,random,statistics,time
from agent_arena.bounded_harness_mission import *
from agent_arena import phase7a_execution as p7,resume_integrity as ri,phase7a_real_run as rr

def div(a,b):return a/b if b else None
def quantile(xs,q):
 if not xs:return None
 s=sorted(xs);k=(len(s)-1)*q;lo=math.floor(k);hi=math.ceil(k);return s[lo]+(s[hi]-s[lo])*(k-lo)
def wilson(k,n):
 if not n:return None
 z=1.959963984540054;p=k/n;d=1+z*z/n;mid=(p+z*z/(2*n))/d;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
 return [mid-half,mid+half]
def paired(xs,ys,classes=None,bootstrap=True):
 assert len(xs)==len(ys)
 n=len(xs);both=sum(a and b for a,b in zip(xs,ys));b=sum(a and not c for a,c in zip(xs,ys));c=sum(not a and d for a,d in zip(xs,ys));discord=b+c
 p=min(1.0,2*sum(math.comb(discord,k) for k in range(min(b,c)+1))/2**discord) if discord else 1.0
 ax=div(sum(xs),n);ay=div(sum(ys),n)
 delta=ay-ax if n else None
 interval=None;degenerate=False
 if bootstrap and n:
  strata=[[i for i,x in enumerate(classes) if x==g] for g in LABELS] if classes else [list(range(n))]
  rng=random.Random(SEED);draws=[]
  for _ in range(10000):
   indices=[rng.choice(s) for s in strata for _ in s]
   draws.append(sum(int(ys[i])-int(xs[i]) for i in indices)/n)
  interval=[100*quantile(draws,.025),100*quantile(draws,.975)];degenerate=min(draws)==max(draws)
 return {'n':n,'both_correct':both,'X_only_correct':b,'Y_only_correct':c,'both_wrong':n-both-b-c,'X_correct':sum(xs),'Y_correct':sum(ys),'X_accuracy':ax,'Y_accuracy':ay,'delta_pp':100*delta if n else None,'relative_accuracy_change_pct':100*delta/ax if ax else None,'relative_error_reduction_pct':100*delta/(1-ax) if n and ax<1 else None,'mcnemar_exact_two_sided_p':p,'bootstrap_percentile95_pp':interval,'bootstrap_degenerate':degenerate}

def calibration(rows):
 valid=[r for r in rows if r['label_readable'] and r['confidence_valid']]
 if not valid:return {'n':0,'brier':None,'ece5':None,'bins':[]}
 bins=[]
 for b in range(5):
  cells=[r for r in valid if min(int(r['confidence']*5),4)==b]
  bins.append({'bin':b,'n':len(cells),'mean_confidence':statistics.mean(r['confidence'] for r in cells) if cells else None,'accuracy':statistics.mean(r['raw_correct'] for r in cells) if cells else None})
 ece=sum(v['n']/len(valid)*abs(v['mean_confidence']-v['accuracy']) for v in bins if v['n'])
 return {'n':len(valid),'brier':statistics.mean((r['confidence']-int(r['raw_correct']))**2 for r in valid),'ece5':ece,'bins':bins}

def metric(rows):
 n=len(rows);conf={g:{p:0 for p in (*LABELS,'INVALID_OR_MISSING')} for g in LABELS}
 for r in rows:conf[r['gold']][r['final_label'] if r['operational_valid'] else 'INVALID_OR_MISSING']+=1
 released=[r for r in rows if r['diagnostic_accepted']];non_solid=[r for r in rows if r['gold']!='solid'];cv=[r for r in rows if r['confidence_valid'] and r['label_readable']]
 wronghigh=sum(not r['raw_correct'] and r['confidence']>=.9 for r in cv);k=sum(r['operational_correct'] for r in rows)
 return {'assigned':n,'operational_correct':k,'accuracy':div(k,n),'wilson95':wilson(k,n),'label_only_correct':sum(r['raw_correct'] for r in rows),'final_label_only_correct':sum(r['final_label']==r['gold'] for r in rows),'schema_valid':sum(r['schema_valid'] for r in rows),'confidence_valid':sum(r['confidence_valid'] for r in rows),'label_readable':sum(r['label_readable'] for r in rows),'confusion':conf,'class_recall':{g:{'correct':sum(r['operational_correct'] for r in rows if r['gold']==g),'assigned':sum(r['gold']==g for r in rows)} for g in LABELS},'false_solid_endorsements':sum(r['final_label']=='solid' and r['operational_valid'] for r in non_solid),'non_solid_assigned':len(non_solid),'high_confidence_wrong':wronghigh,'high_confidence_wrong_all_assigned_rate':div(wronghigh,n),'high_confidence_wrong_applicable_rate':div(wronghigh,len(cv)),'confidence_applicable':len(cv),'calibration_raw_selected_label':calibration(rows),'diagnostic_acceptance':{'accepted':len(released),'coverage':div(len(released),n),'retained_correct':sum(r['final_label']==r['gold'] for r in released),'retained_wrong':sum(r['final_label']!=r['gold'] for r in released),'conditional_wrong_risk':div(sum(r['final_label']!=r['gold'] for r in released),len(released)),'technical_invalid_accepted_under_common_schema':sum(not r['schema_valid'] for r in released)},'official_release':{'applicable':False,'released':0,'coverage':0,'conditional_wrong_risk':None,'reason':'No classification-to-official-artifact conversion or publication invoked. Research diagnostic acceptance is separately measured.'}}

def control_summary():
 d=read(rootpath()/REL/'evidence/offline_controls.json');fault=[r for r in d['artifacts'] if not r['desired_technically_valid']];clean=[r for r in d['artifacts'] if r['desired_technically_valid']]
 return {'artifact_faults':12,'B_invalid_accepted':sum(r['B_accept'] for r in fault),'C_invalid_accepted':sum(r['C_accept'] for r in fault),'extra_C_catches':sum(r['B_accept'] and not r['C_accept'] for r in fault),'B_false_blocks':sum(not r['B_accept'] for r in clean),'C_false_blocks':sum(not r['C_accept'] for r in clean),'clean_mates':6,'families':{f'F{i}':[{'id':r['fixture_id'],'B_accept':r['B_accept'],'C_accept':r['C_accept']} for r in d['artifacts'] if r['fixture_id'].startswith(f'F{i}-')] for i in range(1,7)},'preexecution':d['shared_pre_execution'],'semantic_probes':[{'fixture_id':r['fixture_id'],'B_accept':r['B_accept'],'C_accept':r['C_accept']} for r in d['semantic_probes']]}

def main():
 root=rootpath();base=root/REL;rawdir=base/'raw_execution';out=base/'derived_analysis';out.mkdir(exist_ok=True)
 freeze=read(rawdir/'raw_freeze.json');assert fp(freeze['files'])==freeze['files_fingerprint']
 for name,digest in freeze['files'].items():assert sha((rawdir/name).read_bytes())==digest,name
 ledger=read(rawdir/'ledger.json');assert ledger['state']=='REVOKED' and ledger['executable_remaining_microusd']==0
 assert sha((base/'preregistration/freeze_manifest.json').read_bytes())==freeze['binding']['freeze_manifest_sha256']
 pre=read(base/'preregistration/freeze_manifest.json');oracle_path=base/'fresh_holdout_oracle/oracle.json'
 assert sha(oracle_path.read_bytes())==pre['oracle_sha256']
 inputs=read(base/'fresh_holdout_input/inputs.json');oracle=read(oracle_path);byinp={i['id']:i for i in inputs};bygold={i['id']:i for i in oracle}
 assert len(inputs)==32 and len(byinp)==32 and sum(r['role']=='primary' for r in oracle)==24
 raw=[read(p) for p in sorted((rawdir/'records').glob('*.json'))];bykey={r['slot_key']:r for r in raw};assert len(bykey)==len(raw)
 for r in raw:
  assert r['request_sha256']==fp(expected_payload(byinp[r['id']],r['arm'],root))
  assert r['raw_sha256']==sha(r['raw_text'].encode())
  assert r['input_sha256']==fp(byinp[r['id']])
 braw=[r for r in raw if r['arm']=='B']
 t=time.monotonic_ns();records,units,contract=bind_research_records(braw,oracle,inputs,freeze['binding']['source'],arm_id='B',root=root,checkpoint_root=out/'C_checkpoint')
 rp,mp=out/'C_checkpoint/records.jsonl',out/'C_checkpoint/manifest.json';rp.parent.mkdir(exist_ok=True)
 rr._write_jsonl_atomic(rp,records);atomic(mp,ri.build_checkpoint_manifest(contract,records))
 checked=ri.validate_resume_checkpoint(rp,mp,contract,units);assert checked['valid'],checked['errors']
 cbyid={r['unit_id']:r for r in records};control_ns=time.monotonic_ns()-t
 timing=base/'evidence/postrun_control_timing.json'
 if not timing.exists():atomic(timing,{'binding_and_checkpoint_validation_ns':control_ns,'n_records':len(records),'one_time_post_freeze_measurement':True})
 rows=[]
 for g in sorted(oracle,key=lambda x:x['id']):
  for arm in ('A','B','C'):
   k=('B' if arm=='C' else arm)+':'+g['id'];r=bykey.get(k)
   d=interpretation(r['raw_text'],r['finish_reason']) if r else {'raw_label':None,'label_readable':False,'confidence':None,'confidence_state':'MISSING','confidence_valid':False,'schema_valid':False,'common_operational_valid':False,'final_label':None,'production_parse':{}}
   label=d['final_label'] if arm=='C' else d['raw_label'];valid=bool(r and r['terminal'] and d['common_operational_valid'])
   diagnostic=bool(p7.is_calibration_valid(cbyid[g['id']])) if arm=='C' and g['id'] in cbyid else valid
   payload=expected_payload(byinp[g['id']],'B' if arm=='C' else arm,root)
   attempts=[a for a in ledger['attempts'] if a['slot_key']==k]
   processing=r.get('processing',{}) if r else {}
   if processing:
    for key in ('raw_label','confidence','schema_valid','final_label','confidence_state'):assert processing[key]==d[key]
   rows.append({'id':g['id'],'root_id':g['root_id'],'role':g['role'],'arm':arm,'gold':g['gold'],'raw_label':d['raw_label'],'final_label':label,'label_readable':d['label_readable'],'confidence':d['confidence'],'confidence_valid':d['confidence_valid'],'confidence_state':d['confidence_state'],'schema_valid':d['schema_valid'],'operational_valid':valid,'raw_correct':d['raw_label']==g['gold'],'operational_correct':valid and label==g['gold'],'diagnostic_accepted':diagnostic,'official_release':False,'release_reason':'Research diagnostic eligible' if diagnostic else 'Missing or invalid research diagnostic; no official release path invoked','raw_sha256':r['raw_sha256'] if r else None,'request_sha256':fp(payload),'input_sha256':fp(byinp[g['id']]),'source_packet_sha256':g['source_packet_sha256'],'shared_raw_origin':k if arm=='C' else None,'terminal':bool(r and r['terminal']),'attempt_ids':[a['attempt_id'] for a in attempts],'http_attempts':len(attempts),'provider_duration_ns':r['provider_duration_ns'] if r else None,'parser_duration_ns':processing.get('B_parser_ns'),'incremental_interpretation_ns':processing.get('C_incremental_interpretation_ns') if arm=='C' else 0,'confirmed_token_cost_microusd':sum(a['confirmed_token_cost_microusd'] or 0 for a in attempts),'maximum_reserved_microusd':sum(a['reserved_microusd'] for a in attempts),'usage':[a['usage'] for a in attempts],'model':MODEL,'error_type':r.get('error_type') if r else 'MISSING'})
 primary={a:[r for r in rows if r['arm']==a and r['role']=='primary'] for a in ('A','B','C')}
 classes=[r['gold'] for r in primary['A']];pairs={}
 for x,y in (('A','B'),('A','C'),('B','C')):
  pairs[x+'->'+y]=paired([r['operational_correct'] for r in primary[x]],[r['operational_correct'] for r in primary[y]],classes)
  pairs[x+'->'+y]['confirmatory']=x=='A' and y=='B' and freeze['state']=='COMPLETE'
  pairs[x+'->'+y]['label_discordant_roots']=sum(a['raw_label']!=b['raw_label'] for a,b in zip(primary[x],primary[y]))
  pairs[x+'->'+y]['validity_discordant_roots']=sum(a['operational_valid']!=b['operational_valid'] for a,b in zip(primary[x],primary[y]))
  common=[(a,b) for a,b in zip(primary[x],primary[y]) if a['label_readable'] and b['label_readable'] and a['confidence_valid'] and b['confidence_valid']]
  sx=statistics.mean((a['confidence']-int(a['raw_correct']))**2 for a,b in common) if common else None
  sy=statistics.mean((b['confidence']-int(b['raw_correct']))**2 for a,b in common) if common else None
  cx=calibration([a for a,b in common]);cy=calibration([b for a,b in common])
  pairs[x+'->'+y]['paired_ece5_exploratory']={'n':len(common),'X':cx['ece5'],'Y':cy['ece5'],'improvement_X_minus_Y':cx['ece5']-cy['ece5'] if common else None,'relative_reduction':(cx['ece5']-cy['ece5'])/cx['ece5'] if cx['ece5'] else None}
  pairs[x+'->'+y]['paired_brier']={'n':len(common),'X':sx,'Y':sy,'improvement_X_minus_Y':sx-sy if common else None,'relative_reduction':(sx-sy)/sx if sx else None}
  pairs[x+'->'+y]['raw_label_only']=paired([r['raw_correct'] for r in primary[x]],[r['raw_correct'] for r in primary[y]],classes,bootstrap=False)
  pairs[x+'->'+y]['worsening_ids']=[a['id'] for a,b in zip(primary[x],primary[y]) if a['operational_correct'] and not b['operational_correct']]
 robustness={}
 for arm in ('A','B','C'):
  ar={r['id']:r for r in rows if r['arm']==arm};vp=[]
  for g in oracle:
   if g['role']!='variant':continue
   a,b=ar[g['root_id']],ar[g['id']];vp.append({'root_id':g['root_id'],'variant_id':g['id'],'root_label':a['final_label'],'variant_label':b['final_label'],'jointly_correct':a['operational_correct'] and b['operational_correct'],'label_consistent':a['final_label'] is not None and a['final_label']==b['final_label'],'transition':str(bool(a['operational_correct']))+'->'+str(bool(b['operational_correct']))})
  robustness[arm]={'n':8,'jointly_correct':sum(r['jointly_correct'] for r in vp),'label_consistent':sum(r['label_consistent'] for r in vp),'pairs':vp}
 costs={}
 for a in ('A','B'):
  rs=[r for r in rows if r['arm']==a];dur=[r['provider_duration_ns']/1e6 for r in rs if r['provider_duration_ns'] is not None];par=[r['parser_duration_ns']/1e6 for r in rs if r['parser_duration_ns'] is not None]
  costs[a]={'logical_assigned':32,'terminal':sum(r['terminal'] for r in rs),'http_attempts':sum(r['http_attempts'] for r in rs),'estimated_token_cost_usd':sum(r['confirmed_token_cost_microusd'] for r in rs)/1e6,'maximum_reserved_usd':sum(r['maximum_reserved_microusd'] for r in rs)/1e6,'input_tokens':sum((u or {}).get('input_tokens',0) for r in rs for u in r['usage']),'output_tokens':sum((u or {}).get('output_tokens',0) for r in rs for u in r['usage']),'provider_latency_ms':{'n':len(dur),'p50':quantile(dur,.5),'p95':quantile(dur,.95)},'parser_latency_ms':{'n':len(par),'p50':quantile(par,.5),'p95':quantile(par,.95)}}
 local=[r['incremental_interpretation_ns']/1e6 for r in rows if r['arm']=='C' and r['incremental_interpretation_ns'] is not None]
 costs['C']={'generation_cost':'Shared with B; zero additional calls','incremental_interpretation_ms':{'n':len(local),'p50':quantile(local,.5),'p95':quantile(local,.95)},'checkpoint_control_timing':read(timing)}
 metrics={a:metric(rs) for a,rs in primary.items()};cs=control_summary();c=metrics['C'];a=metrics['A']
 screen={'complete':freeze['state']=='COMPLETE','C_at_least_18':c['operational_correct']>=18,'C_each_class_at_least_3':all(v['correct']>=3 for v in c['class_recall'].values()),'C_at_most_one_extra_error_vs_A':a['operational_correct']-c['operational_correct']<=1,'C_false_endorsements_at_most_1':c['false_solid_endorsements']<=1,'C_at_most_one_extra_endorsement_vs_A':c['false_solid_endorsements']-a['false_solid_endorsements']<=1,'artifact_mandatory_controls':cs['C_invalid_accepted']==0 and cs['C_false_blocks']==0,'preexecution_controls':all(r['accepted']==r['desired_technically_valid'] for r in cs['preexecution']),'cost_cap':ledger['reserved_microusd']<=8000000,'revoked_budget_zero':ledger['executable_remaining_microusd']==0}
 result={'schema':'harness-value-analysis/1','status':freeze['state'],'primary_contrast':'B-A operational accuracy, 24 all-assigned roots','primary_efficacy_verdict_enabled':freeze['state']=='COMPLETE','counts':{k:freeze[k] for k in ('planned_slots','terminal_slots','missing_slots','new_provider_invocations','shared_C_slots','reused_slots')},'metrics':metrics,'paired':pairs,'robustness':robustness,'controls':cs,'cost_latency':costs,'research_screen':screen,'recommendation_pending_coordinator':'GO TO PHASE 8' if all(screen.values()) else 'ONE SMALL ADDITIONAL EXPERIMENT REQUIRED','raw_freeze_fingerprint':freeze['files_fingerprint'],'limitations':['24 author-constructed roots, not representative biomedical sampling.','Variants are dependent; N=1 leaves run-to-run uncertainty unmeasured.','Exact p-value and stratified bootstrap are small-pilot summaries, not general effectiveness or equivalence proof.','ECE bins are [0,.2),[.2,.4),[.4,.6),[.6,.8),[.8,1], exploratory.','Confidence is selected-label correctness, not multiclass probabilities.','No independent B-to-C generative effect or standalone provider runtime.','Official release is not applicable to diagnostic-only replication artifacts.']}
 atomic(out/'rows.json',rows);atomic(out/'summary.json',result)
 with (out/'rows.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows({k:canon(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows)
 print(json.dumps({'status':result['status'],'primary':pairs['A->B'],'C_correct':c['operational_correct'],'screen':screen},indent=2))
if __name__=='__main__':main()
