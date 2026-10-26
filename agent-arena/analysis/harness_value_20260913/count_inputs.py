"""Non-generative, zero-retry token metadata preflight; no completion API."""
import os,datetime
import anthropic
from agent_arena.bounded_harness_mission import *

def main():
 root=rootpath();out=root/REL/'evidence/token_count_preflight.json'
 inputs=read(root/REL/'fresh_holdout_input/inputs.json');byid={x['id']:x for x in inputs};rows={}
 if os.environ.get('ANTHROPIC_BASE_URL','https://api.anthropic.com').rstrip('/')!='https://api.anthropic.com':raise MissionError('not first-party endpoint')
 client=anthropic.Anthropic(max_retries=0,timeout=120)
 for s in schedule(inputs):
  body=expected_payload(byid[s['id']],s['arm'],root)
  result=client.messages.count_tokens(model=MODEL,system=body['system'],messages=body['messages'])
  rows[s['slot_key']]={'input_tokens':result.input_tokens,'payload_sha256':fp(body)}
  print('counted',len(rows),flush=True)
  atomic(out,{'model':MODEL,'operation':'messages.count_tokens','model_generations':0,'http_requests':len(rows),'retries':0,'billable_metadata_cost_usd':0,'by_key':rows,'actual_max_input_tokens':max(x['input_tokens'] for x in rows.values()),'conservative_input_allowance':6000,'slack_required':1000,'counter_is_estimate':True,'pricing_url':'https://platform.claude.com/docs/en/build-with-claude/token-counting','utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 client.close()
if __name__=='__main__':main()
