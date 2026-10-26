# Input Validation Report — final_reval_20260802_190208

| check | P (Opus 5) | Q (GLM 5.2) |
|---|---|---|
| canonical CSV exists | yes | yes |
| private manifest exists | yes | yes |
| manifest structural validation | PASSED | PASSED |
| manifest exact-copy verification | PASSED | PASSED (extracted==external==canonical) |
| frozen prep commit/tag | matched | matched |
| acceptance criteria version | 5.05h/1.0 | 5.05h/1.0 |
| frozen bundle sha256 recorded | matched | matched |
| canonical sha == manifest | yes (`4b6f5037…`) | yes (`db1ca2e1…`, key `canonical_private_csv_sha256`) |
| canonical size == manifest | yes | yes |
| exact 14-col schema | yes | yes |
| exactly one FXR-731 row | yes | yes |
| all substantive fields completed | yes | yes |
| labels/categoricals permitted; primary≠secondary; conf∈[0,1] | yes | yes |
| ingestion method | (byte-copy from external) | pasted_output; raw+extracted validated; **no pasted code executed** |

Both responses were **preserved before comparison**; **neither revalidator was excluded**.
