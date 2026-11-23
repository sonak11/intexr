# IntExR-Scope pilot results

Data: `paperB/data/medec_scope_v0.json` — {"n_examples": 60, "n_claims": 294, "domains": {"clinical_assessment": 60}, "labels": {"K": 156, "D": 44, "P": 57, "U": 37}, "label_triggers": {"K-unverified": 136, "D-evidence": 44, "P-dependency": 57, "K-supported": 20, "U-feedback": 16, "U-dependency": 21}, "feedback_validity": {"valid": 24, "false": 20, "unsupported": 16}, "P_depth": {"1": 54, "2": 3}}

Values: point estimate [95% bootstrap CI over source cases]. Text checks are applied to the full revised response (deterministic pilot proxy).

## Condition A

| system | change_recall_D | change_recall_P | under_revision | preservation_error_Ksupported | preservation_error_K | unresolved_F1 | direct_F1 | propagation_F1 | verdict_acc | check_pass | no_forbidden_additions | claim_action_acc | interaction_exact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| evidence_prompt@groq:openai/gpt-oss-20b | 0.98 [0.93,1.00] | 0.68 [0.55,0.80] | 0.19 [0.12,0.25] | 0.05 [0.00,0.15] | 0.06 [0.03,0.10] | 0.00 [0.00,0.00] | – | – | – | 0.76 [0.69,0.83] | – | 0.78 [0.75,0.81] | 0.35 [0.25,0.45] |
| scope_first@groq:openai/gpt-oss-20b | 1.00 [1.00,1.00] | 0.79 [0.66,0.90] | 0.08 [0.03,0.14] | 0.00 [0.00,0.00] | 0.10 [0.05,0.15] | 0.19 [0.04,0.33] | 0.72 [0.65,0.80] | 0.44 [0.23,0.60] | 0.15 [0.08,0.22] | 0.85 [0.77,0.93] | – | 0.80 [0.76,0.85] | 0.45 [0.32,0.58] |
| scope_pipeline@groq:openai/gpt-oss-20b | 0.86 [0.74,0.96] | 0.86 [0.74,0.97] | 0.09 [0.02,0.17] | 0.00 [0.00,0.00] | 0.07 [0.02,0.13] | 0.04 [0.00,0.15] | 0.63 [0.54,0.73] | 0.38 [0.19,0.55] | 0.02 [0.00,0.05] | 0.83 [0.72,0.93] | – | 0.79 [0.74,0.84] | 0.45 [0.32,0.60] |

### Breakdown

| system | stratum | chg_rec_D | chg_rec_P | pres_err_K | U_F1 | claim_acc |
|---|---|---|---|---|---|---|
| evidence_prompt@groq:openai/gpt-oss-20b | domain=clinical_assessment (n=60) | 0.98 | 0.68 | 0.06 | 0.00 | 0.78 |
| evidence_prompt@groq:openai/gpt-oss-20b | feedback_validity=false (n=20) | 1.00 | 0.77 | 0.06 | nan | 0.91 |
| evidence_prompt@groq:openai/gpt-oss-20b | feedback_validity=unsupported (n=16) | nan | nan | 0.10 | 0.00 | 0.48 |
| evidence_prompt@groq:openai/gpt-oss-20b | feedback_validity=valid (n=24) | 0.96 | 0.61 | 0.05 | nan | 0.86 |
| scope_first@groq:openai/gpt-oss-20b | domain=clinical_assessment (n=60) | 1.00 | 0.79 | 0.10 | 0.19 | 0.80 |
| scope_first@groq:openai/gpt-oss-20b | feedback_validity=false (n=20) | 1.00 | 0.81 | 0.06 | 0.00 | 0.92 |
| scope_first@groq:openai/gpt-oss-20b | feedback_validity=unsupported (n=16) | nan | nan | 0.14 | 0.24 | 0.53 |
| scope_first@groq:openai/gpt-oss-20b | feedback_validity=valid (n=24) | 1.00 | 0.77 | 0.11 | 0.00 | 0.88 |
| scope_first@groq:openai/gpt-oss-20b | judged-from-text | 1.00 | 0.79 | 0.03 | 0.05 | 0.82 |
| scope_pipeline@groq:openai/gpt-oss-20b | domain=clinical_assessment (n=60) | 0.86 | 0.86 | 0.07 | 0.04 | 0.79 |
| scope_pipeline@groq:openai/gpt-oss-20b | feedback_validity=false (n=20) | 0.95 | 0.85 | 0.10 | 0.00 | 0.90 |
| scope_pipeline@groq:openai/gpt-oss-20b | feedback_validity=unsupported (n=16) | nan | nan | 0.02 | 0.05 | 0.53 |
| scope_pipeline@groq:openai/gpt-oss-20b | feedback_validity=valid (n=24) | 0.79 | 0.87 | 0.08 | 0.00 | 0.88 |
| scope_pipeline@groq:openai/gpt-oss-20b | judged-from-text | 0.93 | 0.84 | 0.06 | 0.05 | 0.81 |

## Condition B

| system | change_recall_D | change_recall_P | under_revision | preservation_error_Ksupported | preservation_error_K | unresolved_F1 | direct_F1 | propagation_F1 | verdict_acc | check_pass | no_forbidden_additions | claim_action_acc | interaction_exact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| no_revision | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 1.00 [1.00,1.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.33 [0.33,0.33] | 0.00 [0.00,0.00] | – | 0.53 [0.49,0.57] | 0.00 [0.00,0.00] |
| oracle | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 0.00 [0.00,0.00] | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] | – | 1.00 [1.00,1.00] | 1.00 [1.00,1.00] |
| evidence_prompt@groq:openai/gpt-oss-20b | 0.98 [0.93,1.00] | 0.89 [0.77,0.98] | 0.07 [0.01,0.15] | 0.50 [0.30,0.70] | 0.27 [0.18,0.38] | 0.05 [0.00,0.15] | – | – | – | 0.79 [0.69,0.89] | – | 0.71 [0.65,0.76] | 0.18 [0.10,0.28] |
| scope_first@groq:openai/gpt-oss-20b | 0.98 [0.93,1.00] | 0.88 [0.78,0.95] | 0.05 [0.01,0.10] | 0.15 [0.00,0.30] | 0.16 [0.08,0.24] | 0.13 [0.00,0.27] | 0.63 [0.59,0.68] | 0.47 [0.35,0.57] | 0.00 [0.00,0.00] | 0.67 [0.56,0.79] | – | 0.78 [0.73,0.83] | 0.47 [0.35,0.58] |
| scope_pipeline@groq:openai/gpt-oss-20b | 0.75 [0.61,0.88] | 0.74 [0.59,0.87] | 0.22 [0.11,0.32] | 0.10 [0.00,0.25] | 0.10 [0.06,0.14] | 0.49 [0.29,0.65] | 0.56 [0.48,0.65] | 0.38 [0.23,0.52] | 0.67 [0.57,0.77] | 0.59 [0.46,0.72] | – | 0.79 [0.73,0.85] | 0.37 [0.22,0.52] |

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
| evidence_prompt@groq:openai/gpt-oss-20b | domain=clinical_assessment (n=60) | 0.98 | 0.89 | 0.27 | 0.05 | 0.71 |
| evidence_prompt@groq:openai/gpt-oss-20b | feedback_validity=false (n=20) | 0.95 | 0.92 | 0.35 | nan | 0.79 |
| evidence_prompt@groq:openai/gpt-oss-20b | feedback_validity=unsupported (n=16) | nan | nan | 0.19 | 0.05 | 0.44 |
| evidence_prompt@groq:openai/gpt-oss-20b | feedback_validity=valid (n=24) | 1.00 | 0.87 | 0.26 | 0.00 | 0.83 |
| scope_first@groq:openai/gpt-oss-20b | domain=clinical_assessment (n=60) | 0.98 | 0.88 | 0.16 | 0.13 | 0.78 |
| scope_first@groq:openai/gpt-oss-20b | feedback_validity=false (n=20) | 0.95 | 0.85 | 0.15 | 0.00 | 0.87 |
| scope_first@groq:openai/gpt-oss-20b | feedback_validity=unsupported (n=16) | nan | nan | 0.21 | 0.17 | 0.47 |
| scope_first@groq:openai/gpt-oss-20b | feedback_validity=valid (n=24) | 1.00 | 0.90 | 0.13 | 0.00 | 0.91 |
| scope_first@groq:openai/gpt-oss-20b | judged-from-text | 0.95 | 0.89 | 0.08 | 0.05 | 0.81 |
| scope_pipeline@groq:openai/gpt-oss-20b | domain=clinical_assessment (n=60) | 0.75 | 0.74 | 0.10 | 0.49 | 0.79 |
| scope_pipeline@groq:openai/gpt-oss-20b | feedback_validity=false (n=20) | 0.60 | 0.58 | 0.04 | 0.00 | 0.79 |
| scope_pipeline@groq:openai/gpt-oss-20b | feedback_validity=unsupported (n=16) | nan | nan | 0.14 | 0.55 | 0.66 |
| scope_pipeline@groq:openai/gpt-oss-20b | feedback_validity=valid (n=24) | 0.88 | 0.87 | 0.11 | 0.00 | 0.88 |
| scope_pipeline@groq:openai/gpt-oss-20b | judged-from-text | 0.75 | 0.72 | 0.08 | 0.41 | 0.78 |

