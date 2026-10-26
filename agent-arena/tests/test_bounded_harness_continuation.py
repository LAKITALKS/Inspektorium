"""Only direct continuation risks: immutable parent, inherited caps, guarded 60 keys."""
import copy,json,shutil
from pathlib import Path
import pytest
from agent_arena import bounded_harness_mission as m,bounded_harness_continuation as c
from agent_arena import condition_contract as cc,phase7a_real_run as rr
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/m.REL

def test_parent_and_scientific_binding_unchanged():
 add=m.read(BASE/'continuation/manifest.json')
 # Current development must fail the consumed execution snapshot's source gate.
 # Verify immutable scientific/parent bytes separately, without rebinding that
 # historical manifest to today's implementation or authorizing another run.
 with pytest.raises(m.MissionError,match='continuation execution file changed'):
  c.verify_continuation(ROOT,add)
 assert m.sha((BASE/'raw_execution/raw_freeze.json').read_bytes())==add['parent_raw_freeze_sha256']
 assert m.sha((BASE/'execution_plan.json').read_bytes())==add['parent_authorization_sha256']
 for name,digest in add['scientific_execution_files'].items():
  assert m.sha((ROOT/name).read_bytes())==digest
 parent=m.read(BASE/'raw_execution/ledger.json')
 assert parent['state']=='REVOKED' and parent['executable_remaining_microusd']==0
 assert len(parent['terminal_keys'])==4 and len(add['remaining_keys'])==60
 assert not set(parent['terminal_keys'])&set(add['remaining_keys'])
 assert m.sha((BASE/'fresh_holdout_oracle/oracle.json').read_bytes())==add['fresh_oracle_sha256']

def test_parent_raw_tampering_rejected(tmp_path):
 b=tmp_path/m.REL;b.mkdir(parents=True)
 shutil.copytree(BASE/'raw_execution',b/'raw_execution')
 shutil.copy(BASE/'execution_plan.json',b/'execution_plan.json')
 add=m.read(BASE/'continuation/manifest.json')
 p=b/'raw_execution/attempts/attempt-001-response.bin';p.write_bytes(p.read_bytes()+b' ')
 with pytest.raises(m.MissionError,match='parent raw file changed'):c.verify_continuation(tmp_path,add)

def test_old_reservations_terminal_keys_and_unknown_limit_survive(tmp_path):
 old=m.read(BASE/'raw_execution/ledger.json');slots=m.read(BASE/'preregistration/schedule.json')
 ledger=c.seed_ledger(tmp_path/'ledger.json',{'test':'continuation'},slots,old)
 key=slots[4]['slot_key']
 assert ledger.data['attempts'][:5]==old['attempts'] and ledger.data['reserved_microusd']==132400
 with pytest.raises(m.MissionError,match='terminal'):ledger.reserve(slots[0]['slot_key'],'x','y')
 with pytest.raises(m.MissionError,match='schedule'):ledger.reserve(slots[5]['slot_key'],'x','y')
 assert ledger.reserve(key,'x','y')=='attempt-006'
 assert ledger.reserve(key,'x','y')=='attempt-007'
 with pytest.raises(m.MissionError,match='attempt cap'):ledger.reserve(key,'x','y')
 ledger.terminal(key,'z');ledger.revoke('TEST')
 with pytest.raises(m.MissionError,match='non-executable'):ledger.reserve(slots[5]['slot_key'],'x','y')
 assert old==m.read(BASE/'raw_execution/ledger.json')

def test_sixty_fake_completions_reuse_four_without_oracle(tmp_path,monkeypatch):
 import httpx,socket
 b=tmp_path/m.REL;b.mkdir(parents=True)
 for directory in ('raw_execution','continuation','fresh_holdout_input','preregistration'):
  shutil.copytree(BASE/directory,b/directory)
 (b/'common_dictionary.txt').write_bytes((BASE/'common_dictionary.txt').read_bytes())
 (b/'evidence').mkdir();shutil.copy(BASE/'evidence/token_count_preflight.json',b/'evidence/token_count_preflight.json')
 doc={'specification':{'specification_fingerprint':'f'*64,'runtime':{'expiry_utc':'2999-01-01T00:00:00+00:00'}},'authorization':{'status':cc.AUTH_REAL}}
 m.atomic(b/'continuation/execution_plan.json',doc)
 source={'valid':True,'commit':'a'*40,**{k:'b'*64 for k in ('repository_identity','tree','tracked_source_fingerprint','tracked_config_fingerprint','python_environment_fingerprint','source_state_fingerprint')}}
 monkeypatch.setattr(cc,'resolve_registered_plan',lambda *a:copy.deepcopy(doc));monkeypatch.setattr(cc,'production_authorization_errors',lambda *a:[])
 monkeypatch.setattr(c,'verify_continuation',lambda *a:None)
 monkeypatch.setattr(c.pi,'inspect_source_state',lambda *a:copy.deepcopy(source));monkeypatch.setattr(c.pi,'execute_full_replication_qa',lambda *a:{'synthetic':True});monkeypatch.setattr(c.pi,'validate_full_replication_qa_record',lambda *a:(c.pi.QA_PASSED,[]));monkeypatch.setattr(c.pi,'compare_source_binding',lambda *a:[])
 monkeypatch.setattr(rr,'check_provider_availability',lambda:{'available':True});monkeypatch.setattr(rr,'check_exact_model_availability',lambda *a:{'available':True});monkeypatch.setattr(c.subprocess,'check_output',lambda *a,**k:'a'*40)
 monkeypatch.setenv('ANTHROPIC_API_KEY','offline-placeholder');monkeypatch.setenv('ANTHROPIC_BASE_URL','https://api.anthropic.com')
 monkeypatch.setattr(socket.socket,'connect',lambda *a,**k:(_ for _ in ()).throw(AssertionError('No network')))
 observed=[]
 class FakeWire(httpx.BaseTransport):
  def __init__(self,**kw):pass
  def handle_request(self,request):
   body=json.loads(request.content);inp=json.loads(body['messages'][0]['content']);observed.append(inp['id'])
   payload={'final_answer':'solid','confidence':.8,'evidence_tier':'clinical_human','conclusion_tier':'same as evidence','bridge_supported':True,**{k:[] for k in m.LIST_FIELDS}}
   return httpx.Response(200,json={'id':'msg_synthetic','type':'message','role':'assistant','model':m.MODEL,'content':[{'type':'text','text':json.dumps(payload)}],'stop_reason':'end_turn','stop_sequence':None,'usage':{'input_tokens':1,'output_tokens':1}},request=request)
 monkeypatch.setattr(httpx,'HTTPTransport',FakeWire)
 result=c._run_mission(tmp_path);ledger=m.read(b/'continuation_execution/ledger.json');freeze=m.read(b/'continuation_execution/raw_freeze.json')
 assert result['complete'] and len(observed)==60 and len(ledger['attempts'])==65
 assert ledger['reserved_microusd']==65*m.MAX_ATTEMPT_MICROUSD and ledger['executable_remaining_microusd']==0
 assert freeze['reused_slots']==4 and freeze['new_provider_invocations']==60 and freeze['shared_C_slots']==32
 assert ledger['attempts'][4]['usage'] is None
 assert not (b/'fresh_holdout_oracle').exists()
 for name in ('raw_freeze.json','ledger.json','lease.json'):
  assert (b/'raw_execution'/name).read_bytes()==(BASE/'raw_execution'/name).read_bytes()
 with pytest.raises(m.MissionError,match='lease'):c._run_mission(tmp_path)
