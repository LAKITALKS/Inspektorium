"""Create the compact offline review bundle after the final local results commit.

Contains source, frozen inputs/oracle, both raw sections, analysis, controls and QA.
Excludes credentials, retrieved article dumps, bytecode and unrelated user files.
"""
import hashlib,json,re,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
REL=Path('analysis/harness_value_20260913')
BASE=ROOT/REL

def main():
 files=[]
 for directory in (ROOT/'src',BASE):
  for p in sorted(directory.rglob('*')):
   if not p.is_file() or '__pycache__' in p.parts or 'source_retrieval' in p.parts or p.suffix in ('.pyc','.zip'):continue
   files.append(p)
 files += [ROOT/'pyproject.toml',ROOT/'tests/test_bounded_harness_mission.py',ROOT/'tests/test_bounded_harness_continuation.py']
 patterns=[rb'sk-ant-[A-Za-z0-9_-]{30,}',rb'sk-proj-[A-Za-z0-9_-]{30,}',rb'ghp_[A-Za-z0-9]{30,}',rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----']
 inventory={}
 for p in files:
  data=p.read_bytes()
  if any(re.search(pattern,data) for pattern in patterns):raise RuntimeError('Possible credential in '+str(p.relative_to(ROOT)))
  inventory[str(p.relative_to(ROOT))]=hashlib.sha256(data).hexdigest()
 receipt={'final_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=ROOT,text=True).strip(),'tracked_tree_clean':not bool(subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=ROOT,text=True).strip()),'push_performed':False,'files_sha256':inventory,'secret_scan':'No high-confidence credential/private-key patterns in included files. Request headers are explicitly whitelisted; no account addresses, payment details, plaintext organization ID or environment files included.','reproduction':{'command':'PYTHONPATH=src python analysis/harness_value_20260913/reproduce.py','requirements':'Python >=3.11 with the existing project dependencies from pyproject.toml and provider SDK imports available. No network or generation is invoked by reproduce.py.','output':'Reproduces rows.json, rows.csv and summary.json twice from the combined frozen raw section; preserves the original four-response parent.','scope':'The fresh 64-slot analysis is self-contained. Historical raw reconstructions and full project-suite execution refer to the original checkout; their existing results and hashes are included.'}}
 assert receipt['tracked_tree_clean'],'Results must be committed before packaging'
 out=BASE/'agent_arena_harness_value_evidence.zip'
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
  for p in files:z.write(p,p.relative_to(ROOT))
  z.writestr('EVIDENCE_MANIFEST.json',json.dumps(receipt,indent=2)+'\n')
 print(json.dumps({'path':str(out),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'final_commit':receipt['final_commit'],'files':len(files)}))
if __name__=='__main__':main()
