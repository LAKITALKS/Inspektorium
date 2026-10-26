# Research material of the audit runtime

This folder holds research material of the Inspektorium audit runtime that is
not part of either installed package. The wheels and the runtime source
distribution do not include it.

| Folder | Content |
| --- | --- |
| [`datasets/`](datasets/README.md) | Early case-pack inputs, moved here in 0.2.0 |
| [`legacy-launchers/`](legacy-launchers/README.md) | Historical `run_*.py` launchers, moved here in 0.2.0; most call model providers |
| [`agent_arena_library_expansion_150/`](agent_arena_library_expansion_150/README.md) | Earlier library-expansion research workspace, unchanged |

## Moved files

For Inspektorium 0.2.0 the loose files at the top of `agent-arena/` were moved
here with `git mv`. Their contents are unchanged; each SHA-256 below equals the
public hash recorded for the old path in the
[2026-10-26 import index](../../publication/2026-10-26/import-index.json).
Old paths link to publication commit
`94eb4fc8b26c22da6a2cebdd01e5a7799750104d`.

| Old path (at `94eb4fc`) | New path | SHA-256 |
| --- | --- | --- |
| [`Dataset 2.pdf`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/Dataset%202.pdf) | [`datasets/dataset-2.pdf`](datasets/dataset-2.pdf) | `7c270802c79c398551a4932d03bfaae2cdcf80686f37e0fc29eed0e1f1c6062c` |
| [`Dataset 3.pdf`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/Dataset%203.pdf) | [`datasets/dataset-3.pdf`](datasets/dataset-3.pdf) | `4b39374e3cb55bec25ebbf737a1b1986e62ad0e750d515ff945c5e19391828bc` |
| [`Dataset 4.pdf`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/Dataset%204.pdf) | [`datasets/dataset-4.pdf`](datasets/dataset-4.pdf) | `68491d80d5177be1595cc5163c4b11df9e1433659bf40c4cf2060b642b4645e6` |
| [`Dataset 5.json`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/Dataset%205.json) | [`datasets/dataset-5.json`](datasets/dataset-5.json) | `69be56b163b216bef6f2163b63aac8c30b2961b28c31f17551736981568d0d0f` |
| [`Dataset 6.pdf`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/Dataset%206.pdf) | [`datasets/dataset-6.pdf`](datasets/dataset-6.pdf) | `38b12e136c955c4a3da34803a0c619e14955a2ceead899a70990065ffe33c687` |
| [`pilot_dataset_6_cases (1).json`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/pilot_dataset_6_cases%20%281%29.json) | [`datasets/pilot-dataset-6-cases.json`](datasets/pilot-dataset-6-cases.json) | `62a93af923f42a4217fc6818a9f83bd2eacc23069f2ae8075c8fcf8564bc2bde` |
| [`run_calibration_rerun.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_calibration_rerun.py) | [`legacy-launchers/run_calibration_rerun.py`](legacy-launchers/run_calibration_rerun.py) | `22a0e7a86401ca8f31759300ade81477ec498ab9cc085f5c8ec20980fe8468f3` |
| [`run_full_27.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_full_27.py) | [`legacy-launchers/run_full_27.py`](legacy-launchers/run_full_27.py) | `4324bc44f159d38f6b49aa601daa03a054705cfdbc3cac3448fa67ae125239da` |
| [`run_llm_validation_sprint.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_llm_validation_sprint.py) | [`legacy-launchers/run_llm_validation_sprint.py`](legacy-launchers/run_llm_validation_sprint.py) | `a332ecccce550a5f0dbbe58d178cb1387208568ae0ec1e7a04ca805647bd1309` |
| [`run_llm_validation_sprint2.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_llm_validation_sprint2.py) | [`legacy-launchers/run_llm_validation_sprint2.py`](legacy-launchers/run_llm_validation_sprint2.py) | `6c97f32e9e80651b78ce5377a75debd9c4cb543a5af2a34d625c6cee683e3748` |
| [`run_llm_validation_sprint3.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_llm_validation_sprint3.py) | [`legacy-launchers/run_llm_validation_sprint3.py`](legacy-launchers/run_llm_validation_sprint3.py) | `5b89f65eca037455d68ac94063af1c1e0f89a4376b28a030b55e3d2ac3fbeedb` |
| [`run_mechanism_calibration.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_mechanism_calibration.py) | [`legacy-launchers/run_mechanism_calibration.py`](legacy-launchers/run_mechanism_calibration.py) | `f6d212e7b8d13a93f370d7a815c84eccb48c7db108f2818e371294630486a29c` |
| [`run_mechanism_calibration2.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_mechanism_calibration2.py) | [`legacy-launchers/run_mechanism_calibration2.py`](legacy-launchers/run_mechanism_calibration2.py) | `098debc0a7cd84bc57bc6de0157817c7375e2f062aba053051f1198fa4ffff41` |
| [`run_mechanism_retest.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_mechanism_retest.py) | [`legacy-launchers/run_mechanism_retest.py`](legacy-launchers/run_mechanism_retest.py) | `cea46c17541ea6fc5ec9f8af023c306e84f8757fbccb6987dba84ee8d7abcfcc` |
| [`run_mini_validation.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_mini_validation.py) | [`legacy-launchers/run_mini_validation.py`](legacy-launchers/run_mini_validation.py) | `21c7d6505b0b1ee6474caa1aaaa77cea5bc82c72ba9d54d89f7cfaccaa1a30f0` |
| [`run_overclaim_retest.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_overclaim_retest.py) | [`legacy-launchers/run_overclaim_retest.py`](legacy-launchers/run_overclaim_retest.py) | `b195a62142be47f71f1beabe1e16c30aa9693c44cacf043496643a71a46f266f` |
| [`run_praxis.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_praxis.py) | [`legacy-launchers/run_praxis.py`](legacy-launchers/run_praxis.py) | `11de2481c7cc2966af8c1ec9df044b6eb421f1b58267b8a9f53fa5f7b6a909f5` |
| [`run_public_001.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_public_001.py) | [`legacy-launchers/run_public_001.py`](legacy-launchers/run_public_001.py) | `d1a75b19089ff6878133f43ea34ce1ac90514b3d7f78a3962a128506cbba6620` |
| [`run_study_forensics_pilot.py`](https://github.com/LAKITALKS/Inspektorium/blob/94eb4fc8b26c22da6a2cebdd01e5a7799750104d/agent-arena/run_study_forensics_pilot.py) | [`legacy-launchers/run_study_forensics_pilot.py`](legacy-launchers/run_study_forensics_pilot.py) | `2b96feb8200c144e4171983bb390211c1b6378d43896f2f256a378d1a2b1f6e8` |

Historical records keep the old paths and are not rewritten: the import index
and the other 2026-10-26 publication records, historical inventories under
`analysis/` (for example `analysis/harness_value_20260913/evidence/historical_pdf_inventory.json`),
task notes and run records that name "Dataset 2" to "Dataset 6", and the usage
notes inside the launchers. Read those paths against commit `94eb4fc`.
