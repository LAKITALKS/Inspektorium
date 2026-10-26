"""Assemble the authorized two-section raw view; run unchanged frozen analysis.

No generation or network operation. Usage from checkout or extracted evidence bundle:
  PYTHONPATH=src python analysis/harness_value_20260913/reproduce.py
The original parent raw_execution directory and old authorization are never written.
"""
import hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REL=Path('analysis/harness_value_20260913')
BASE=ROOT/REL

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 combined=BASE/'continuation_execution';freeze=read(combined/'raw_freeze.json');add=read(BASE/'continuation/manifest.json')
 assert freeze['state']=='COMPLETE' and freeze['terminal_slots']==64
 assert sha(BASE/'raw_execution/raw_freeze.json')==add['parent_raw_freeze_sha256']
 assert sha(BASE/'execution_plan.json')==add['parent_authorization_sha256']
 assert sha(BASE/'continuation/manifest.json')==freeze['binding']['continuation_manifest_sha256']
 for name,digest in freeze['files'].items():assert sha(combined/name)==digest,name
 ledger=read(combined/'ledger.json');assert ledger['state']=='REVOKED' and ledger['executable_remaining_microusd']==0
 pre=read(BASE/'preregistration/freeze_manifest.json');analysis_sha=pre['all_preparation_files'][str(REL/'analyze.py')]
 assert sha(BASE/'analyze.py')==analysis_sha
 receipts=[]
 with tempfile.TemporaryDirectory(prefix='arena-combined-scoring-') as work:
  root=Path(work);base=root/REL;base.mkdir(parents=True)
  shutil.copytree(ROOT/'src',root/'src',ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for directory in ('preregistration','fresh_holdout_input','fresh_holdout_oracle'):
   shutil.copytree(BASE/directory,base/directory)
  for name in ('common_dictionary.txt','analyze.py'):shutil.copyfile(BASE/name,base/name)
  shutil.copytree(combined,base/'raw_execution')
  (base/'evidence').mkdir();shutil.copyfile(BASE/'evidence/offline_controls.json',base/'evidence/offline_controls.json')
  timing=BASE/'evidence/postrun_control_timing.json'
  if timing.exists():shutil.copyfile(timing,base/'evidence/postrun_control_timing.json')
  env=os.environ.copy();env['PYTHONPATH']=str(root/'src')
  for index in (1,2):
   result=subprocess.run([sys.executable,str(base/'analyze.py')],cwd=root,env=env,text=True,capture_output=True)
   if result.returncode:raise RuntimeError(result.stdout+'\n'+result.stderr)
   receipts.append({'run':index,'exit_code':result.returncode,'files':{n:sha(base/'derived_analysis'/n) for n in ('rows.json','rows.csv','summary.json')}})
  assert receipts[0]['files']==receipts[1]['files']
  shutil.copytree(base/'derived_analysis',BASE/'derived_analysis',dirs_exist_ok=True)
  if not timing.exists():shutil.copyfile(base/'evidence/postrun_control_timing.json',timing)
 receipt={'unchanged_preregistered_analysis_sha256':analysis_sha,'continuation_raw_freeze_sha256':sha(combined/'raw_freeze.json'),'parent_raw_freeze_sha256':add['parent_raw_freeze_sha256'],'analysis_runs':receipts,'identical':True,'assembly':'4 original records copied byte-for-byte plus 60 continuation records; cumulative ledger, original endpoints.','checkpoint_note':'Checkpoint storage identity contains temporary scoring path; score tables are path-independent and byte-reproduced.'}
 (BASE/'evidence/analysis_reproduction.json').write_text(json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({'identical':True,'files':receipts[0]['files']}))
if __name__=='__main__':main()
