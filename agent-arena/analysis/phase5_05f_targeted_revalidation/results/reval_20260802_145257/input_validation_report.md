# Input Validation Report

run: reval_20260802_145257

| rev | model | csv sha256 | rows | validation |
|---|---|---|---|---|
| X | Anthropic Opus 5 | `44b06ba132439bb8…` | 2 (RVAL-001/002) | PASSED |
| Y | GLM GLM 5.2 | `0c68ab39e4f11d66…` | 2 (RVAL-001/002) | PASSED |
| Z | Gemini Gemini 3.5 Flash (Extra Thinking) | `2299ea9f5aa7cd04…` | 2 (RVAL-001/002) | PASSED |

All three inputs verified outside Git, exact 14-column header, RVAL-001/002 once each, all fields valid; hashes match private manifests and known values. Z raw code not executed (AST/literal extraction).