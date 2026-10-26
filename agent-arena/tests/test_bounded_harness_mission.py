"""Offline risks in the new mission adapter; no paid test or scientific repair."""
import copy,importlib.util,json
from pathlib import Path
import pytest
from agent_arena import bounded_harness_mission as m,condition_contract as cc,phase7a_real_run as rr
ROOT=Path(__file__).resolve().parents[1]

def payload():return {'final_answer':'solid','evidence_tier':'clinical_human','conclusion_tier':'same as evidence','bridge_supported':True,'confidence':.8,**{k:[] for k in m.LIST_FIELDS}}

def analysis_module():
 spec=importlib.util.spec_from_file_location('bounded_analysis',ROOT/m.REL/'analyze.py');a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a);return a

def test_opaque_roles_balance_and_variant_dependence():
 inputs=m.read(ROOT/m.REL/'fresh_holdout_input/inputs.json');o=m.read(ROOT/m.REL/'fresh_holdout_oracle/oracle.json')
 assert len(inputs)==len({i['id'] for i in inputs})==32
 assert all(set(i)=={'id','claim','packet'} and i['id'].startswith('q-') for i in inputs)
 roots=[r for r in o if r['role']=='primary'];variants=[r for r in o if r['role']=='variant']
 assert len(roots)==24 and len({r['root_id'] for r in variants})==8
 assert {g:sum(r['gold']==g for r in roots) for g in m.LABELS}==dict.fromkeys(m.LABELS,6)
 assert len({i['packet']['source']['doi'] for i in inputs})==24
 byid={r['id']:r for r in o}
 assert all(r['gold']==byid[r['root_id']]['gold'] for r in variants)

def test_requests_real_sdk_wire_and_shared_C(monkeypatch):
 # Existing Anthropic provider is exercised with actual SDK serialization and fake transport.
 rows=m.dry_capture(ROOT)
 assert len(rows)==96
 bykey={(r['arm'],r['id']):r for r in rows}
 for r in rows:
  p=r['generative_payload'];assert set(p)=={'model','max_tokens','temperature','system','messages'}
  assert p['model']==m.MODEL and p['temperature']==0 and p['max_tokens']==4096
  assert len(p['messages'])==1 and p['messages'][0]['role']=='user'
  if r['arm']=='C':
   b=bykey['B',r['id']];assert r['generative_sha256']==b['generative_sha256'] and r['sanitized_wire_sha256']==b['sanitized_wire_sha256']
  if r['arm']=='B':assert p['system'].startswith(m.V2+'\n\n')
  if r['arm']=='A':assert p['system'].startswith(m.A+'\n\n') and not p['system'].startswith(m.V2)
  assert not r['actual_network']

def test_rendering_never_reads_oracle(monkeypatch):
 inp=m.read(ROOT/m.REL/'fresh_holdout_input/inputs.json')[0];original=Path.read_text
 def guarded(path,*a,**kw):
  assert 'oracle' not in str(path) and 'candidate_authoring' not in str(path)
  return original(path,*a,**kw)
 monkeypatch.setattr(Path,'read_text',guarded)
 for a in ('A','B'):m.expected_payload(inp,a,ROOT)
 assert m.task(inp).gold_label is None

@pytest.mark.parametrize('confidence',[None,True,'0.9',1.2,float('nan'),float('inf')])
def test_reasonable_common_confidence_validation(confidence):
 p=payload();p['confidence']=confidence;d=m.interpretation(json.dumps(p));assert not d['confidence_valid'] and not d['common_operational_valid'];assert d['raw_label']=='solid'

def test_schema_and_terminal_not_semantic_retry():
 p=payload();assert m.interpretation(json.dumps(p))['common_operational_valid']
 del p['steps'];assert not m.interpretation(json.dumps(p))['schema_valid']
 assert not m.interpretation('{broken')['common_operational_valid']
 p=payload();p['final_answer']='unrecognized';assert not m.interpretation(json.dumps(p))['common_operational_valid']
 assert not m.interpretation(json.dumps(payload()),'length')['common_operational_valid']

def test_budget_unknown_attempt_reservations_and_terminal_idempotence(tmp_path):
 slots=[{'slot_key':'A:one'},{'slot_key':'B:one'}];l=m.BudgetLedger(tmp_path/'ledger.json',{'spec':'frozen'},slots,create=True)
 for n in range(3):l.reserve('A:one','payload','wire')
 with pytest.raises(m.MissionError):l.reserve('A:one','payload','wire')
 assert l.data['reserved_microusd']==3*m.MAX_ATTEMPT_MICROUSD
 l.terminal('A:one','rawhash')
 with pytest.raises(m.MissionError):l.reserve('A:one','payload','wire')
 with pytest.raises(m.MissionError):l.terminal('A:one','changed')
 l.reserve('B:one','payload','wire');l.revoke('interruption')
 assert l.data['executable_remaining_microusd']==0 and l.data['reserved_microusd']==4*m.MAX_ATTEMPT_MICROUSD
 with pytest.raises(m.MissionError):l.reserve('B:one','payload','wire')
 with pytest.raises(m.MissionError):m.BudgetLedger(l.path,{'spec':'other'},slots)

def test_budget_cannot_overrun_or_change_schedule(tmp_path):
 l=m.BudgetLedger(tmp_path/'ledger.json',{},[{'slot_key':'A:one'},{'slot_key':'B:one'}],create=True)
 with pytest.raises(m.MissionError):l.reserve('B:one','p','w')
 l.data['reserved_microusd']=8000000;m.atomic(l.path,l.data)
 with pytest.raises(m.MissionError):l.reserve('A:one','p','w')

def test_invalid_authorization_precedes_provider(monkeypatch):
 monkeypatch.setattr(cc,'resolve_registered_plan',lambda *a:{})
 monkeypatch.setattr(cc,'production_authorization_errors',lambda *a:['consumed or wrong scope'])
 def forbidden(*a,**kw):raise AssertionError('provider boundary reached')
 monkeypatch.setattr(m,'AnthropicProvider',forbidden)
 with pytest.raises(m.MissionError,match='consumed'):m._run_mission(ROOT)
 with pytest.raises(rr.ConditionAuthorizationError):rr.run_registered_condition(m.PLAN_ID,m.ARM_ID,'sonnet',repo_root=ROOT)

def test_fixed_faults_and_clean_mates():
 d=m.read(ROOT/m.REL/'evidence/offline_controls.json')
 assert len(d['artifacts'])==18 and len(d['shared_pre_execution'])==6 and len(d['semantic_probes'])==2
 assert all(r['C_accept']==r['desired_technically_valid'] for r in d['artifacts'])
 assert all(r['accepted']==r['desired_technically_valid'] for r in d['shared_pre_execution'])
 assert all(not r['fake_provider_constructions'] for r in d['shared_pre_execution'] if not r['desired_technically_valid'])
 assert all(r['C_accept'] and r['checkpoint_valid'] and r['B_accept'] for r in d['semantic_probes'])

def test_hand_calculated_pairing_sign_and_denominators():
 a=analysis_module();r=a.paired([True,True,False,False],[True,False,True,True],bootstrap=False)
 assert (r['both_correct'],r['X_only_correct'],r['Y_only_correct'],r['both_wrong'])==(1,1,2,0)
 assert r['delta_pp']==25 and r['relative_accuracy_change_pct']==50 and r['relative_error_reduction_pct']==50 and r['mcnemar_exact_two_sided_p']==1
 r=a.paired([False]*24,[True]+[False]*23,bootstrap=False);assert r['n']==24 and r['delta_pp']==pytest.approx(100/24) and r['relative_accuracy_change_pct'] is None
 assert a.paired([],[],bootstrap=False)['delta_pp'] is None
 assert a.paired([True]*24,[True]*24,['solid']*6+['overclaim']*6+['correlation_vs_causation']*6+['mechanism_vs_evidence']*6)['bootstrap_degenerate']

def test_selected_label_brier_and_bins():
 a=analysis_module();rows=[{'label_readable':True,'confidence_valid':True,'confidence':.9,'raw_correct':True},{'label_readable':True,'confidence_valid':True,'confidence':.9,'raw_correct':False}]
 c=a.calibration(rows);assert c['brier']==pytest.approx(.41) and c['ece5']==pytest.approx(.4) and c['n']==2
 rows.append({'label_readable':True,'confidence_valid':False,'confidence':None,'raw_correct':True});assert a.calibration(rows)==c
 assert a.calibration([])['brier'] is None

def test_historical_authorizations_stay_consumed():
 for p in ('AA-P5B-HAIKU-FULL-REPLICATION-001','AA-P5B-SONNET-FULL-REPLICATION-001'):
  d=cc.resolve_registered_plan(p,ROOT);assert d['authorization']['status']==cc.AUTH_CONSUMED and d['authorization']['authorized_budget_calls']==0

@pytest.mark.parametrize('mode',['clean','transport_retry','permanent_error','preflight_failure'])
def test_complete_executor_with_fake_wire_and_no_oracle(tmp_path,monkeypatch,mode):
 import httpx,socket
 root=tmp_path;base=root/m.REL;base.mkdir(parents=True)
 inputs=m.read(ROOT/m.REL/'fresh_holdout_input/inputs.json');m.atomic(base/'fresh_holdout_input/inputs.json',inputs)
 (base/'common_dictionary.txt').write_text((ROOT/m.REL/'common_dictionary.txt').read_text())
 slots=m.schedule(inputs);m.atomic(base/'preregistration/schedule.json',slots)
 byid={i['id']:i for i in inputs};counts={s['slot_key']:{'payload_sha256':m.fp(m.expected_payload(byid[s['id']],s['arm'],root)),'input_tokens':100} for s in slots}
 m.atomic(base/'evidence/token_count_preflight.json',{'model':m.MODEL,'actual_max_input_tokens':100,'by_key':counts})
 oracle_bytes=(ROOT/m.REL/'fresh_holdout_oracle/oracle.json').read_bytes()
 m.atomic(base/'preregistration/freeze_manifest.json',{'execution_files':{},'protected_historical_files':{},'oracle_sha256':m.sha(oracle_bytes)})
 doc={'specification':{'specification_fingerprint':'f'*64,'runtime':{'expiry_utc':'2999-01-01T00:00:00+00:00'}},'authorization':{'status':cc.AUTH_REAL}}
 m.atomic(base/'execution_plan.json',doc)
 source={'valid':True,'commit':'a'*40,**{k:'b'*64 for k in ('repository_identity','tree','tracked_source_fingerprint','tracked_config_fingerprint','python_environment_fingerprint','source_state_fingerprint')}}
 monkeypatch.setattr(cc,'resolve_registered_plan',lambda *a:copy.deepcopy(doc))
 monkeypatch.setattr(cc,'production_authorization_errors',lambda *a:[])
 monkeypatch.setattr(m.pi,'inspect_source_state',lambda *a:copy.deepcopy(source))
 monkeypatch.setattr(m.pi,'execute_full_replication_qa',lambda *a:{'synthetic':True})
 monkeypatch.setattr(m.pi,'validate_full_replication_qa_record',lambda *a:(m.pi.QA_PASSED,[]))
 monkeypatch.setattr(m.pi,'compare_source_binding',lambda *a:[])
 monkeypatch.setattr(rr,'check_provider_availability',lambda:{'available':True})
 monkeypatch.setattr(rr,'check_exact_model_availability',lambda *a:{'available':True})
 monkeypatch.setattr(m.subprocess,'check_output',lambda *a,**k:'a'*40)
 monkeypatch.setenv('ANTHROPIC_API_KEY','offline-placeholder');monkeypatch.setenv('ANTHROPIC_BASE_URL','https://api.anthropic.com')
 monkeypatch.setattr(socket.socket,'connect',lambda *a,**k:(_ for _ in ()).throw(AssertionError('Network forbidden')))
 state={'calls':0}
 class FakeWire(httpx.BaseTransport):
  def __init__(self,**kw):pass
  def handle_request(self,request):
   state['calls']+=1
   if mode=='transport_retry' and state['calls']==1:raise httpx.ReadTimeout('synthetic timeout',request=request)
   if mode=='permanent_error':return httpx.Response(403,json={'type':'error','error':{'type':'permission_error','message':'synthetic'}},request=request)
   return httpx.Response(200,json={'id':f'msg_offline_{state["calls"]}','type':'message','role':'assistant','model':m.MODEL,'content':[{'type':'text','text':json.dumps(payload())}],'stop_reason':'end_turn','stop_sequence':None,'usage':{'input_tokens':1,'output_tokens':1}},request=request)
 monkeypatch.setattr(httpx,'HTTPTransport',FakeWire)
 if mode=='preflight_failure':
  monkeypatch.setattr(m.pi,'validate_full_replication_qa_record',lambda *a:(m.pi.QA_FAILED,['synthetic failed gate']))
  monkeypatch.setattr(m,'AnthropicProvider',lambda *a,**k:(_ for _ in ()).throw(AssertionError('Provider must not be constructed')))
  with pytest.raises(m.MissionError,match='canonical QA'):m._run_mission(root)
  assert state['calls']==0 and not (base/'raw_execution/lease.json').exists()
  assert m.read(base/'execution_plan.json')['authorization']['authorized_budget_calls']==0
  assert m.read(base/'execution_plan.json')['authorization']['status']==cc.AUTH_CONSUMED
  assert m.read(base/'evidence/prelease_abort.json')['provider_boundary_reached'] is False
  assert m.read(base/'evidence/registered_preflight_qa.json')['validation_status']==m.pi.QA_FAILED
  return
 result=m._run_mission(root);ledger=m.read(base/'raw_execution/ledger.json')
 assert ledger['state']=='REVOKED' and ledger['executable_remaining_microusd']==0
 if mode=='permanent_error':assert not result['complete'] and state['calls']==1 and result['terminal']==0
 else:assert result['complete'] and result['terminal']==64 and state['calls']==64+(mode=='transport_retry')
 if mode=='transport_retry':assert ledger['attempts'][0]['state']=='UNKNOWN_BILLING_TRANSPORT_ERROR' and ledger['reserved_microusd']==65*m.MAX_ATTEMPT_MICROUSD
 assert not (base/'fresh_holdout_oracle').exists()
 with pytest.raises(m.MissionError,match='lease'):m._run_mission(root)

 # Verify the complete deterministic scoring join only AFTER raw freeze. No real
 # model predictions are involved in this hand-controlled synthetic run.
 if mode=='clean':
  import shutil
  shutil.copytree(ROOT/'src',root/'src')
  (base/'fresh_holdout_oracle').mkdir();(base/'fresh_holdout_oracle/oracle.json').write_bytes(oracle_bytes)
  shutil.copy(ROOT/m.REL/'evidence/offline_controls.json',base/'evidence/offline_controls.json')
  a=analysis_module();monkeypatch.setattr(a,'rootpath',lambda:root)
  a.main();summary=base/'derived_analysis/summary.json';before=m.sha(summary.read_bytes());a.main();assert m.sha(summary.read_bytes())==before
  v=m.read(summary);assert v['metrics']['A']['assigned']==24 and v['metrics']['A']['operational_correct']==6
  assert v['paired']['B->C']['delta_pp']==0 and v['robustness']['A']['n']==8
