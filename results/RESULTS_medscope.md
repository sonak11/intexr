# Results — `paperB/data/medec_scope_v0.json`

Point estimate [95% CI, bootstrap over source cases]. PresErr: lower is better. K+ = K claims supported by evidence.

## Condition A

| system | n | Chg-D | Chg-P | PresErr-K | PresErr-K+ | U-F1 | Verdict | NoForbid | Exact |
|---|---|---|---|---|---|---|---|---|---|
| evidence_prompt@groq_openai_gpt-oss-120b | 60 | 1.00 [1.00, 1.00] | 0.70 [0.56, 0.84] | 0.04 [0.01, 0.10] | 0.05 [0.00, 0.15] | 0.00 [0.00, 0.00] | – | – | 0.48 [0.37, 0.60] |
| evidence_prompt@groq_qwen_qwen3.8-27b | 60 | 1.00 [1.00, 1.00] | 0.14 [0.04, 0.27] | 0.01 [0.00, 0.02] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | – | 0.10 [0.00, 0.20] |
| scope_first@groq_openai_gpt-oss-120b | 60 | 0.93 [0.85, 1.00] | 0.93 [0.86, 1.00] | 0.07 [0.03, 0.12] | 0.05 [0.00, 0.15] | 0.28 [0.05, 0.47] | 0.28 [0.22, 0.35] | – | 0.62 [0.52, 0.72] |
| scope_first@groq_qwen_qwen3.8-27b | 60 | 1.00 [1.00, 1.00] | 0.98 [0.94, 1.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.05 [0.00, 0.17] | 0.40 [0.35, 0.47] | – | 0.72 [0.65, 0.78] |
| scope_pipeline@groq_openai_gpt-oss-120b | 60 | 0.95 [0.89, 1.00] | 0.74 [0.55, 0.89] | 0.03 [0.01, 0.05] | 0.00 [0.00, 0.00] | 0.13 [0.00, 0.35] | 0.07 [0.02, 0.13] | – | 0.52 [0.38, 0.65] |
| scope_pipeline@groq_qwen_qwen3.8-27b | 60 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.14 [0.00, 0.39] | 0.40 [0.35, 0.47] | – | 0.72 [0.62, 0.80] |

## Condition B

| system | n | Chg-D | Chg-P | PresErr-K | PresErr-K+ | U-F1 | Verdict | NoForbid | Exact |
|---|---|---|---|---|---|---|---|---|---|
| evidence_prompt@groq_openai_gpt-oss-120b | 60 | 1.00 [1.00, 1.00] | 0.88 [0.77, 0.96] | 0.04 [0.01, 0.07] | 0.10 [0.00, 0.25] | 0.15 [0.00, 0.34] | – | – | 0.53 [0.42, 0.65] |
| evidence_prompt@groq_qwen_qwen3.8-27b | 60 | 0.98 [0.93, 1.00] | 0.74 [0.53, 0.91] | 0.04 [0.01, 0.07] | 0.25 [0.10, 0.45] | 0.05 [0.00, 0.15] | – | – | 0.43 [0.28, 0.58] |
| no_revision | 60 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.33 [0.33, 0.33] | – | 0.00 [0.00, 0.00] |
| oracle | 60 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | – | 1.00 [1.00, 1.00] |
| scope_first@groq_openai_gpt-oss-120b | 60 | 0.86 [0.74, 0.98] | 0.89 [0.79, 0.98] | 0.13 [0.07, 0.20] | 0.15 [0.00, 0.30] | 0.62 [0.46, 0.75] | 0.63 [0.50, 0.77] | – | 0.62 [0.48, 0.75] |
| scope_first@groq_qwen_qwen3.8-27b | 60 | 1.00 [1.00, 1.00] | 0.98 [0.94, 1.00] | 0.01 [0.00, 0.02] | 0.05 [0.00, 0.15] | 0.44 [0.21, 0.64] | 0.73 [0.65, 0.83] | – | 0.73 [0.65, 0.82] |
| scope_pipeline@groq_qwen_qwen3.8-27b | 60 | 0.93 [0.82, 1.00] | 1.00 [1.00, 1.00] | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.72 [0.50, 0.88] | 0.80 [0.73, 0.87] | – | 0.80 [0.68, 0.90] |

## Cost of verification: B − A (same claims)

Negative change recall / exact = worse when feedback must be verified; positive PresErr = more collateral change.

| system | change_recall_D | change_recall_P | preservation_error_K | unresolved_F1 | interaction_exact |
|---|---|---|---|---|---|
| evidence_prompt@groq_openai_gpt-oss-120b | 0.00 [0.00, 0.00] | 0.18 [0.08, 0.29] | -0.01 [-0.06, 0.05] | 0.15 [0.00, 0.34] | 0.05 [-0.05, 0.15] |
| evidence_prompt@groq_qwen_qwen3.8-27b | -0.02 [-0.07, 0.00] | 0.60 [0.40, 0.77] | 0.03 [0.01, 0.06] | 0.05 [0.00, 0.15] | 0.33 [0.18, 0.48] |
| scope_first@groq_openai_gpt-oss-120b | -0.07 [-0.15, 0.00] | -0.04 [-0.09, 0.00] | 0.06 [0.00, 0.12] | 0.33 [0.13, 0.59] | 0.00 [-0.12, 0.13] |
| scope_first@groq_qwen_qwen3.8-27b | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.01 [0.00, 0.02] | 0.39 [0.13, 0.61] | 0.02 [-0.03, 0.08] |
| scope_pipeline@groq_qwen_qwen3.8-27b | -0.07 [-0.18, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.58 [0.31, 0.82] | 0.08 [-0.03, 0.18] |

## Change recall on P by dependency depth (condition B)

| system | depth 1 | depth 2+ |
|---|---|---|
| evidence_prompt@groq_openai_gpt-oss-120b | 0.87 (n=54) | 1.00 (n=3) |
| evidence_prompt@groq_qwen_qwen3.8-27b | 0.72 (n=54) | 1.00 (n=3) |
| no_revision | 0.00 (n=54) | 0.00 (n=3) |
| oracle | 1.00 (n=54) | 1.00 (n=3) |
| scope_first@groq_openai_gpt-oss-120b | 0.91 (n=54) | 0.67 (n=3) |
| scope_first@groq_qwen_qwen3.8-27b | 0.98 (n=54) | 1.00 (n=3) |
| scope_pipeline@groq_qwen_qwen3.8-27b | 1.00 (n=54) | 1.00 (n=3) |

## By feedback validity (condition B)

| system | validity | n | Chg-D | Chg-P | PresErr-K | PresErr-K+ | U-F1 | Verdict |
|---|---|---|---|---|---|---|---|---|
| evidence_prompt@groq_openai_gpt-oss-120b | false | 20 | 1.00 | 0.85 | 0.06 | 0.10 | – | – |
| evidence_prompt@groq_openai_gpt-oss-120b | unsupported | 16 | – | – | 0.02 | – | 0.15 | – |
| evidence_prompt@groq_openai_gpt-oss-120b | valid | 24 | 1.00 | 0.90 | 0.03 | – | – | – |
| evidence_prompt@groq_qwen_qwen3.8-27b | false | 20 | 0.95 | 0.77 | 0.10 | 0.25 | – | – |
| evidence_prompt@groq_qwen_qwen3.8-27b | unsupported | 16 | – | – | 0.00 | – | 0.05 | – |
| evidence_prompt@groq_qwen_qwen3.8-27b | valid | 24 | 1.00 | 0.71 | 0.02 | – | – | – |
| no_revision | false | 20 | 0.00 | 0.00 | 0.00 | 0.00 | – | 1.00 |
| no_revision | unsupported | 16 | – | – | 0.00 | – | 0.00 | 0.00 |
| no_revision | valid | 24 | 0.00 | 0.00 | 0.00 | – | – | 0.00 |
| oracle | false | 20 | 1.00 | 1.00 | 0.00 | 0.00 | – | 1.00 |
| oracle | unsupported | 16 | – | – | 0.00 | – | 1.00 | 1.00 |
| oracle | valid | 24 | 1.00 | 1.00 | 0.00 | – | – | 1.00 |
| scope_first@groq_openai_gpt-oss-120b | false | 20 | 0.85 | 0.92 | 0.08 | 0.15 | 0.00 | 0.80 |
| scope_first@groq_openai_gpt-oss-120b | unsupported | 16 | – | – | 0.31 | – | 0.72 | 0.56 |
| scope_first@groq_openai_gpt-oss-120b | valid | 24 | 0.88 | 0.87 | 0.05 | – | 0.00 | 0.54 |
| scope_first@groq_qwen_qwen3.8-27b | false | 20 | 1.00 | 1.00 | 0.02 | 0.05 | 0.00 | 0.90 |
| scope_first@groq_qwen_qwen3.8-27b | unsupported | 16 | – | – | 0.00 | – | 0.46 | 0.19 |
| scope_first@groq_qwen_qwen3.8-27b | valid | 24 | 1.00 | 0.97 | 0.00 | – | 0.00 | 0.96 |
| scope_pipeline@groq_qwen_qwen3.8-27b | false | 20 | 0.90 | 1.00 | 0.02 | 0.00 | 0.00 | 1.00 |
| scope_pipeline@groq_qwen_qwen3.8-27b | unsupported | 16 | – | – | 0.00 | – | 0.75 | 0.25 |
| scope_pipeline@groq_qwen_qwen3.8-27b | valid | 24 | 0.96 | 1.00 | 0.02 | – | 0.00 | 1.00 |
