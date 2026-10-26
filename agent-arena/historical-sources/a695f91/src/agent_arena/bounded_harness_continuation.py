"""User-authorized prospective continuation of one scientific pilot.

Old authorization, lease and raw freeze are immutable. The new registered scope
permits only the remaining 60 keys and inherits all prior attempt reservations.
No scientific prompt, parser, model runtime, endpoint or production guard changes.
"""
import shutil
from agent_arena import bounded_harness_mission as m
from agent_arena.bounded_harness_mission import *
PLAN_ID=m.PLAN_ID+'-CONTINUATION-001'


def build_specification(definition,repo_root=None):
 root=rootpath(repo_root)
 if set(definition)!={'plan_id','continuation_manifest_sha256'} or definition['plan_id']!=PLAN_ID:
  raise cc.ConditionContractError('continuation identity/schema mismatch')
 path=root/REL/'continuation/manifest.json'
 if sha(path.read_bytes())!=definition['continuation_manifest_sha256']:
  raise cc.ConditionContractError('continuation manifest binding mismatch')
 add=read(path);old=read(root/REL/'execution_plan.json')
 original=m.build_specification(old['definition'],root)
 if add['parent_specification_fingerprint']!=original['specification_fingerprint']:
  raise cc.ConditionContractError('parent scientific specification differs')
 spec={**copy.deepcopy(original),'plan_id':PLAN_ID,'scientific_plan_id':m.PLAN_ID,
       'continuation_manifest_sha256':definition['continuation_manifest_sha256'],
       'parent_specification_fingerprint':original['specification_fingerprint'],
       'expected_calls_total':60,'remaining_keys':add['remaining_keys'],
       'arms':[{'arm_id':ARM_ID,'artifact_namespace':str(REL/'continuation_execution')}]}
 spec.pop('specification_fingerprint',None);spec['specification_fingerprint']=cc._fp(spec)
 return spec


def verify_continuation(root,add):
 base=root/REL;parent=base/'raw_execution';f=read(parent/'raw_freeze.json');old=read(base/'execution_plan.json');ledger=read(parent/'ledger.json')
 if sha((parent/'raw_freeze.json').read_bytes())!=add['parent_raw_freeze_sha256']:raise MissionError('parent freeze changed')
 if sha((base/'execution_plan.json').read_bytes())!=add['parent_authorization_sha256']:raise MissionError('old authorization changed')
 if old['authorization']['status']!=cc.AUTH_CONSUMED or old['authorization']['authorized_budget_calls']!=0 or ledger['state']!='REVOKED' or ledger['executable_remaining_microusd']!=0:raise MissionError('parent is not irrevocably dormant')
 if f['state']!='INCOMPLETE' or fp(f['files'])!=f['files_fingerprint']:raise MissionError('invalid parent freeze')
 for name,digest in f['files'].items():
  if sha((parent/name).read_bytes())!=digest:raise MissionError('parent raw file changed: '+name)
 for name,digest in add['execution_files'].items():
  if sha((root/name).read_bytes())!=digest:raise MissionError('continuation execution file changed: '+name)
 scientific=read(base/'preregistration/freeze_manifest.json')
 for name,digest in scientific['protected_historical_files'].items():
  if sha((root/name).read_bytes())!=digest:raise MissionError('historical protected file changed: '+name)
 # Fresh oracle remains outside runner access; its unchanged hash is adjudication metadata.
 for name,digest in add['scientific_execution_files'].items():
  if sha((root/name).read_bytes())!=digest:raise MissionError('scientific execution content changed: '+name)
 keys=[s['slot_key'] for s in read(base/'preregistration/schedule.json')]
 if ledger['planned_keys']!=keys or ledger['terminal_keys']!=keys[:4] or add['completed_keys']!=keys[:4] or add['remaining_keys']!=keys[4:]:raise MissionError('continuation keys differ from original fixed schedule')
 if len(ledger['attempts'])!=5 or [a['slot_key'] for a in ledger['attempts']]!=keys[:5] or ledger['attempts'][-1]['usage'] is not None:raise MissionError('parent attempt accounting differs')
 if ledger['reserved_microusd']!=5*MAX_ATTEMPT_MICROUSD:raise MissionError('parent exposure mismatch')
 for key,digest in ledger['terminal_record_hashes'].items():
  path=parent/'records'/f'{key.replace(":","-")}.json'
  if sha(path.read_bytes())!=digest:raise MissionError('parent terminal hash differs')
 return ledger


def seed_ledger(path,binding,slots,parent):
 ledger=BudgetLedger(path,binding,slots,create=True)
 for key in ('attempts','terminal_keys','terminal_record_hashes','reserved_microusd'):
  ledger.data[key]=copy.deepcopy(parent[key])
 ledger.data['executable_remaining_microusd']=MAX_TOTAL_MICROUSD-parent['reserved_microusd']
 ledger.data['parent_ledger_sha256']=sha(canon(parent).encode())
 ledger.data['carried_unknown_billing_attempt_ids']=['attempt-005']
 atomic(path,ledger.data)
 return ledger


def _run_mission(root):
 root=rootpath(root)
 try:return _execute_mission(root)
 except BaseException as exc:
  base=root/REL;path=base/'continuation/execution_plan.json'
  if path.is_file():
   plan=read(path)
   if plan.get('authorization',{}).get('status')==cc.AUTH_REAL:
    plan['authorization'].update(status=cc.AUTH_CONSUMED,authorized_budget_calls=0,authorization_source='failed_continuation_preflight_revocation')
    plan['progress']={'status':cc.PROGRESS_PARTIAL_INCOMPLETE,'completed_calls':0};atomic(path,plan)
    atomic(base/'evidence/continuation_prelease_abort.json',{'exception_type':type(exc).__name__,'reason':str(exc),'executable_budget_calls':0})
  raise

def _execute_mission(root):
 """Only called by the public registered dispatcher, with no injected dependencies."""
 import datetime, httpx, anthropic
 from agent_arena import phase7a_real_run as rr
 root=rootpath(root);base=root/REL;out=base/'continuation_execution'
 document=cc.resolve_registered_plan(PLAN_ID,root)
 errors=cc.production_authorization_errors(document,root)
 if errors:raise MissionError('; '.join(errors))
 freeze=read(base/'continuation/manifest.json')
 if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(document['specification']['runtime']['expiry_utc']):raise MissionError('mission authorization expired')
 if (out/'lease.json').exists():raise MissionError('one-shot lease exists; no resume supported')
 verify_continuation(root,freeze)
 source_before=pi.inspect_source_state(root)
 if not source_before.get('valid'):raise MissionError('source gate: '+str(source_before.get('errors')))
 qa=pi.execute_full_replication_qa(root,source_before)
 status,errors=pi.validate_full_replication_qa_record(qa,source_before)
 atomic(base/'evidence/continuation_preflight_qa.json',{'qa':qa,'validation_status':status,'validation_errors':errors})
 if status!=pi.QA_PASSED or errors:raise MissionError('canonical QA: '+str(errors))
 source_after=pi.inspect_source_state(root)
 errors=pi.compare_source_binding(source_before,source_after)
 if errors:raise MissionError('environment/source gate: '+str(errors))
 if cc.resolve_registered_plan(PLAN_ID,root)!=document:raise MissionError('authorization/spec changed after QA')
 verify_continuation(root,freeze)
 if not rr.check_provider_availability()['available']:raise MissionError('credentials unavailable')
 metadata=rr.check_exact_model_availability(MODEL)
 if not metadata['available']:raise MissionError('exact snapshot unavailable')
 # Environment cannot redirect requests to a reseller or proxy endpoint.
 if os.environ.get('ANTHROPIC_BASE_URL','https://api.anthropic.com').rstrip('/')!='https://api.anthropic.com':raise MissionError('nonstandard API account route')
 inputs=read(base/'fresh_holdout_input/inputs.json');byid={i['id']:i for i in inputs};slots=read(base/'preregistration/schedule.json')
 if len(byid)!=32 or slots!=schedule(inputs):raise MissionError('32x2 fixed schedule mismatch')
 all_slots=slots;slots=[s for s in all_slots if s['slot_key'] in freeze['remaining_keys']]
 if [s['slot_key'] for s in slots]!=freeze['remaining_keys']:raise MissionError('remaining schedule mismatch')
 token_counts=read(base/'evidence/token_count_preflight.json')
 if token_counts['actual_max_input_tokens']+1000>6000 or token_counts['model']!=MODEL:raise MissionError('input-token bound fails')
 for s in slots:
  if token_counts['by_key'][s['slot_key']]['payload_sha256']!=fp(expected_payload(byid[s['id']],s['arm'],root)):raise MissionError('counted payload mismatch')
 binding={'plan_id':PLAN_ID,'specification_fingerprint':document['specification']['specification_fingerprint'],'preregistration_commit':source_after['commit'],'freeze_manifest_sha256':sha((base/'preregistration/freeze_manifest.json').read_bytes()),'source':source_after,'parent_raw_freeze_sha256':freeze['parent_raw_freeze_sha256'],'continuation_manifest_sha256':sha((base/'continuation/manifest.json').read_bytes()),'scientific_plan_id':m.PLAN_ID,'parent_source':read(base/'raw_execution/raw_freeze.json')['binding']['source']}
 out.mkdir(parents=True,exist_ok=True)
 lease={**binding,'ownership_pid':os.getpid(),'state':'ONE_SHOT_CONSUMED','resume':'PROHIBITED'}
 fd=os.open(out/'lease.json',os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
 with os.fdopen(fd,'w') as f:f.write(canon(lease));f.flush();os.fsync(f.fileno())
 ledger=seed_ledger(out/'ledger.json',binding,all_slots,read(base/'raw_execution/ledger.json'))
 for directory in ('attempts','records'):
  shutil.copytree(base/'raw_execution'/directory,out/directory)
 (out/'parent').mkdir()
 for name in ('raw_freeze.json','ledger.json','lease.json','preflight.json'):
  shutil.copyfile(base/'raw_execution'/name,out/'parent'/name)
 atomic(out/'preflight.json',{'binding':binding,'qa':qa,'qa_status':status,'model_metadata':metadata,'provider_constructed':False})
 OriginalClient=httpx.Client;current={};raw_records=[];abort=None
 class ObservedTransport(httpx.BaseTransport):
  def __init__(self):self.inner=httpx.HTTPTransport(retries=0)
  def close(self):self.inner.close()
  def handle_request(self,request):
   body=json.loads(request.content)
   if str(request.url)!='https://api.anthropic.com/v1/messages' or request.method!='POST' or body!=current['payload']:raise MissionError('wire request differs from frozen payload/endpoint')
   wire={'method':request.method,'url':str(request.url),'headers':{k:v for k,v in request.headers.items() if k in ('content-type','anthropic-version')},'body_utf8':request.content.decode()}
   aid=ledger.reserve(current['slot']['slot_key'],fp(body),fp(wire));current['attempt_ids'].append(aid)
   atomic(out/'attempts'/f'{aid}-request.json',wire)
   t=time.monotonic_ns()
   try:
    response=self.inner.handle_request(request);data=response.read()
   except Exception as exc:
    ledger.observe(aid,state='UNKNOWN_BILLING_TRANSPORT_ERROR',exception_type=type(exc).__name__,provider_duration_ns=time.monotonic_ns()-t)
    raise
   duration=time.monotonic_ns()-t
   # Store server bytes before the production adapter parses them.
   rp=out/'attempts'/f'{aid}-response.bin';rp.write_bytes(data)
   with rp.open('rb') as f:os.fsync(f.fileno())
   try:v=json.loads(data)
   except (ValueError,UnicodeError):v={}
   usage=v.get('usage') if isinstance(v,dict) else None
   cost=None
   if isinstance(usage,dict):
    ti=usage.get('input_tokens',0);to=usage.get('output_tokens',0);cr=usage.get('cache_read_input_tokens',0);cw=usage.get('cache_creation_input_tokens',0)
    # No caching requested. Report any unexpected use and fail after preserving bytes.
    cost=ti+5*to
    if ti+cr+cw>6000 or to>4096 or cr or cw:current['integrity_error']='unexpected token/cache accounting'
   if response.status_code==200 and v.get('model')!=MODEL:current['integrity_error']='returned model mismatch'
   ledger.observe(aid,state='HTTP_RESPONSE_RECORDED',http_status=response.status_code,response_sha256=sha(data),provider_message_id=v.get('id'),resolved_model=v.get('model'),usage=usage,confirmed_token_cost_microusd=cost,provider_duration_ns=duration,request_id=response.headers.get('request-id'))
   if response.status_code not in (408,409,429) and response.status_code<500 and response.status_code!=200:response.headers['x-should-retry']='false'
   return response
 class ObservedClient(OriginalClient):
  def __init__(self,**kw):super().__init__(transport=ObservedTransport(),**kw)
 try:
  with patch.object(httpx,'Client',ObservedClient):
   for s in slots:
    verify_continuation(root,freeze)
    if subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()!=binding['preregistration_commit']:raise MissionError('commit changed during execution')
    if cc.resolve_registered_plan(PLAN_ID,root)!=document:raise MissionError('authorization changed during execution')
    if datetime.datetime.now(datetime.timezone.utc)>=datetime.datetime.fromisoformat(document['specification']['runtime']['expiry_utc']):raise MissionError('expired during execution')
    inp=byid[s['id']];current.clear();current.update(slot=s,payload=expected_payload(inp,s['arm'],root),attempt_ids=[a['attempt_id'] for a in ledger.data['attempts'] if a['slot_key']==s['slot_key']])
    provider=AnthropicProvider(MODEL,temperature=0.0,max_tokens=4096)
    t=time.monotonic_ns();resp=provider.generate(task(inp),system(s['arm'],root));elapsed=time.monotonic_ns()-t
    row={**s,'input_sha256':fp(inp),'request_sha256':fp(current['payload']),'raw_text':resp.text,'raw_sha256':sha(resp.text.encode()),'finish_reason':resp.finish_reason,'error_type':resp.error_type if resp.error else None,'provider_duration_ns':elapsed,'attempt_ids':current['attempt_ids'],'usage':resp.usage,'shared_C':s['arm']=='B','terminal':not bool(resp.error),'resolved_model':MODEL if not current.get('integrity_error') else None}
    path=out/'records'/f'{s["slot_key"].replace(":","-")}.json';atomic(path,row);raw_records.append(row)
    if current.get('integrity_error'):raise MissionError(current['integrity_error'])
    if resp.error:raise MissionError('provider failed; no manual restart: '+str(resp.error_type))
    row['processing']=interpretation(resp.text,resp.finish_reason)
    atomic(path,row)
    ledger.terminal(s['slot_key'],sha(path.read_bytes()))
    # No labels/gold interpreted or printed during execution.
    print('terminal',len(ledger.data['terminal_keys']),'of 64; HTTP attempts',len(ledger.data['attempts']),flush=True)
 except BaseException as exc:
  abort=type(exc).__name__+': '+str(exc)
 finally:
  complete=len(ledger.data['terminal_keys'])==64 and abort is None
  ledger.revoke('COMPLETE' if complete else 'INCOMPLETE: '+str(abort))
  # Tracked consumed state uses the existing authorization state machine.
  plan=read(base/'continuation/execution_plan.json');plan['authorization']={'status':cc.AUTH_CONSUMED,'specification_fingerprint':document['specification']['specification_fingerprint'],'authorization_source':'one_shot_execution_consumed','authorized_budget_calls':0}
  plan['progress']={'status':cc.PROGRESS_COMPLETE if complete else cc.PROGRESS_PARTIAL_INCOMPLETE,'completed_calls':len(ledger.data['terminal_keys'])-4};atomic(base/'continuation/execution_plan.json',plan)
  files={str(p.relative_to(out)):sha(p.read_bytes()) for p in sorted(out.rglob('*')) if p.is_file() and p.name!='raw_freeze.json'}
  atomic(out/'raw_freeze.json',{'state':'COMPLETE' if complete else 'INCOMPLETE','abort':abort,'planned_slots':64,'terminal_slots':len(ledger.data['terminal_keys']),'missing_slots':64-len(ledger.data['terminal_keys']),'new_provider_invocations':len(raw_records),'reused_slots':4,'shared_C_slots':sum(k.startswith('B:') for k in ledger.data['terminal_keys']),'files':files,'files_fingerprint':fp(files),'binding':binding})
 return {'complete':complete,'abort':abort,'terminal':len(ledger.data['terminal_keys'])}
