# IntExR-Scope pilot results

Data: `paperB/data/medec_scope_v0.json` — {"n_examples": 60, "n_claims": 294, "domains": {"clinical_assessment": 60}, "labels": {"K": 156, "D": 44, "P": 57, "U": 37}, "label_triggers": {"K-unverified": 136, "D-evidence": 44, "P-dependency": 57, "K-supported": 20, "U-feedback": 16, "U-dependency": 21}, "feedback_validity": {"valid": 24, "false": 20, "unsupported": 16}, "P_depth": {"1": 54, "2": 3}}

Values: point estimate [95% bootstrap CI over source cases]. Text checks are applied to the full revised response (deterministic pilot proxy).

## Condition A

| system | change_recall_D | change_recall_P | under_revision | preservation_error_Ksupported | preservation_error_K | unresolved_F1 | direct_F1 | propagation_F1 | verdict_acc | check_pass | no_forbidden_additions | claim_action_acc | interaction_exact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| evidence_prompt@gemini:gemma-4-31b-it | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.01 [0.00,0.02] | 0.00 [0.00,0.00] | – | – | – | 0.00 [0.00,0.00] | – | 0.87 [0.84,0.90] | 0.73 [0.68,0.80] |
| scope_first@gemini:gemma-4-31b-it | 0.91 [0.80,1.00] | 0.93 [0.84,1.00] | 0.08 [0.00,0.18] | 0.00 [0.00,0.00] | 0.03 [0.00,0.08] | 0.00 [0.00,0.00] | 0.84 [0.75,0.93] | 0.88 [0.77,0.95] | 0.45 [0.37,0.53] | 0.88 [0.77,0.96] | – | 0.83 [0.79,0.87] | 0.58 [0.45,0.72] |
| scope_pipeline@gemini:gemma-4-31b-it | 0.91 [0.82,0.98] | 0.88 [0.78,0.98] | 0.11 [0.02,0.20] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.71 [0.63,0.81] | 0.60 [0.40,0.78] | 0.44 [0.37,0.50] | 0.79 [0.70,0.89] | – | 0.84 [0.79,0.88] | 0.67 [0.58,0.75] |

### Breakdown

| system | stratum | chg_rec_D | chg_rec_P | pres_err_K | U_F1 | claim_acc |
|---|---|---|---|---|---|---|
| evidence_prompt@gemini:gemma-4-31b-it | domain=clinical_assessment (n=60) | 1.00 | 1.00 | 0.01 | 0.00 | 0.87 |
| evidence_prompt@gemini:gemma-4-31b-it | feedback_validity=false (n=20) | 1.00 | 1.00 | 0.00 | nan | 1.00 |
| evidence_prompt@gemini:gemma-4-31b-it | feedback_validity=unsupported (n=16) | nan | nan | 0.02 | 0.00 | 0.52 |
| evidence_prompt@gemini:gemma-4-31b-it | feedback_validity=valid (n=24) | 1.00 | 1.00 | 0.00 | nan | 1.00 |
| scope_first@gemini:gemma-4-31b-it | domain=clinical_assessment (n=60) | 0.91 | 0.93 | 0.03 | 0.00 | 0.83 |
| scope_first@gemini:gemma-4-31b-it | feedback_validity=false (n=20) | 0.90 | 0.92 | 0.04 | 0.00 | 0.94 |
| scope_first@gemini:gemma-4-31b-it | feedback_validity=unsupported (n=16) | nan | nan | 0.00 | 0.00 | 0.53 |
| scope_first@gemini:gemma-4-31b-it | feedback_validity=valid (n=24) | 0.92 | 0.94 | 0.05 | 0.00 | 0.94 |
| scope_first@gemini:gemma-4-31b-it | judged-from-text | 0.91 | 0.91 | 0.03 | 0.00 | 0.83 |
| scope_pipeline@gemini:gemma-4-31b-it | domain=clinical_assessment (n=60) | 0.91 | 0.88 | 0.00 | 0.00 | 0.84 |
| scope_pipeline@gemini:gemma-4-31b-it | feedback_validity=false (n=20) | 0.95 | 0.92 | 0.00 | nan | 0.97 |
| scope_pipeline@gemini:gemma-4-31b-it | feedback_validity=unsupported (n=16) | nan | nan | 0.00 | 0.00 | 0.53 |
| scope_pipeline@gemini:gemma-4-31b-it | feedback_validity=valid (n=24) | 0.88 | 0.84 | 0.00 | nan | 0.93 |
| scope_pipeline@gemini:gemma-4-31b-it | judged-from-text | 0.84 | 0.82 | 0.00 | 0.00 | 0.82 |

## Condition B

| system | change_recall_D | change_recall_P | under_revision | preservation_error_Ksupported | preservation_error_K | unresolved_F1 | direct_F1 | propagation_F1 | verdict_acc | check_pass | no_forbidden_additions | claim_action_acc | interaction_exact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_revision | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 1.00 [1.00,1.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.33 [0.33,0.33] | 0.00 [0.00,0.00] | – | 0.53 [0.49,0.57] | 0.00 [0.00,0.00] |
| oracle | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | – | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] |
| evidence_prompt@gemini:gemma-4-31b-it | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | 0.00 [0.00,0.00] | 0.15 [0.00,0.30] | 0.02 [0.00,0.04] | 0.05 [0.00,0.15] | – | – | – | 0.00 [0.00,0.00] | – | 0.87 [0.84,0.90] | 0.68 [0.62,0.75] |
| scope_first@gemini:gemma-4-31b-it | 0.86 [0.77,0.95] | 0.86 [0.75,0.95] | 0.14 [0.05,0.24] | 0.10 [0.00,0.25] | 0.03 [0.01,0.06] | 0.58 [0.33,0.79] | 0.78 [0.70,0.85] | 0.79 [0.69,0.89] | 0.88 [0.78,0.96] | 0.82 [0.73,0.91] | – | 0.86 [0.81,0.92] | 0.67 [0.53,0.78] |
| scope_pipeline@gemini:gemma-4-31b-it | 0.86 [0.75,0.96] | 0.88 [0.77,0.97] | 0.11 [0.04,0.19] | 0.00 [0.00,0.00] | 0.02 [0.00,0.05] | 0.47 [0.17,0.70] | 0.66 [0.58,0.75] | 0.54 [0.40,0.67] | 0.83 [0.73,0.93] | 0.66 [0.53,0.79] | – | 0.86 [0.82,0.91] | 0.65 [0.53,0.77] |

### Breakdown

| system | stratum | chg_rec_D | chg_rec_P | pres_err_K | U_F1 | claim_acc |
|---|---|---|---|---|---|---|
| no_revision | domain=clinical_assessment (n=60) | 0.00 | 0.00 | 0.00 | 0.00 | 0.53 |
| no_revision | feedback_validity=false (n=20) | 0.00 | 0.00 | 0.00 | nan | 0.53 |
| no_revision | feedback_validity=unsupported (n=16) | nan | nan | 0.00 | 0.00 | 0.53 |
| no_revision | feedback_validity=valid (n=24) | 0.00 | 0.00 | 0.00 | nan | 0.53 |
| oracle | domain=clinical_assessment (n=60) | 1.00 | 1.00 | 0.00 | 1.00 | 1.00 |
| oracle | feedback_validity=false (n=20) | 1.00 | 1.00 | 0.00 | nan | 1.00 |
| oracle | feedback_validity=unsupported (n=16) | nan | nan | 0.00 | 1.00 | 1.00 |
| oracle | feedback_validity=valid (n=24) | 1.00 | 1.00 | 0.00 | nan | 1.00 |
| evidence_prompt@gemini:gemma-4-31b-it | domain=clinical_assessment (n=60) | 1.00 | 1.00 | 0.02 | 0.05 | 0.87 |
| evidence_prompt@gemini:gemma-4-31b-it | feedback_validity=false (n=20) | 1.00 | 1.00 | 0.06 | 0.00 | 0.97 |
| evidence_prompt@gemini:gemma-4-31b-it | feedback_validity=unsupported (n=16) | nan | nan | 0.00 | 0.05 | 0.54 |
| evidence_prompt@gemini:gemma-4-31b-it | feedback_validity=valid (n=24) | 1.00 | 1.00 | 0.00 | nan | 1.00 |
| scope_first@gemini:gemma-4-31b-it | domain=clinical_assessment (n=60) | 0.86 | 0.86 | 0.03 | 0.58 | 0.86 |
| scope_first@gemini:gemma-4-31b-it | feedback_validity=false (n=20) | 0.85 | 0.81 | 0.06 | 0.00 | 0.89 |
| scope_first@gemini:gemma-4-31b-it | feedback_validity=unsupported (n=16) | nan | nan | 0.00 | 0.60 | 0.73 |
| scope_first@gemini:gemma-4-31b-it | feedback_validity=valid (n=24) | 0.88 | 0.90 | 0.03 | 0.00 | 0.93 |
| scope_first@gemini:gemma-4-31b-it | judged-from-text | 0.86 | 0.84 | 0.02 | 0.24 | 0.83 |
| scope_pipeline@gemini:gemma-4-31b-it | domain=clinical_assessment (n=60) | 0.86 | 0.88 | 0.02 | 0.47 | 0.86 |
| scope_pipeline@gemini:gemma-4-31b-it | feedback_validity=false (n=20) | 0.80 | 0.88 | 0.02 | nan | 0.92 |
| scope_pipeline@gemini:gemma-4-31b-it | feedback_validity=unsupported (n=16) | nan | nan | 0.00 | 0.49 | 0.68 |
| scope_pipeline@gemini:gemma-4-31b-it | feedback_validity=valid (n=24) | 0.92 | 0.87 | 0.03 | 0.00 | 0.93 |
| scope_pipeline@gemini:gemma-4-31b-it | judged-from-text | 0.73 | 0.75 | 0.02 | 0.31 | 0.80 |

