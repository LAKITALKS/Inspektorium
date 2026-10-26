import sys; sys.path.insert(0, sys.argv[1])
from h import *
M = {'008': '3fb05a1a-9599-44e4-b756-15c29c6642b8', '009': '806cb89c-ac5e-45ea-b8aa-49765f0e8af1',
     '010': '30ba8a3f-3be6-4ec1-a250-1dbfd284af87', '011': '662fbdc3-70d3-4911-aee7-25a17538dd49',
     '012': 'b7d8770e-a048-46d3-90c8-109416aa5f8b'}
for att, u in M.items():
    j, task = load(att)
    a = run(j['forensic_record'], task, j.get('final_answer'))
    print(att, task['id'], 'replay==bundle:', same(a, bundle(u)))
    show(a, att)
