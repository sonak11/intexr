# Results — `paperB/data/medec_scope_v0.json`

Point estimate [95% CI, bootstrap over source cases]. PresErr: lower is better. K+ = K claims supported by evidence.

## Condition A

| system | n | Chg-D | Chg-P | PresErr-K | PresErr-K+ | U-F1 | Verdict | NoForbid | Exact |
|---|---|---|---|---|---|---|---|---|---|
| evidence_prompt@gemini_gemma-4-31b-it | 60 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.01 [0.00, 0.02] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | – | 0.73 [0.68, 0.80] |
| evidence_prompt@groq_openai_gpt-oss-120b | 60 | 1.00 [1.00, 1.00] | 0.63 [0.46, 0.79] | 0.03 [0.01, 0.05] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | – | 0.43 [0.30, 0.57] |
| evidence_prompt@groq_openai_gpt-oss-20b | 60 | 0.98 [0.93, 1.00] | 0.68 [0.55, 0.80] | 0.06 [0.03, 0.10] | 0.05 [0.00, 0.15] | 0.00 [0.00, 0.00] | – | – | 0.35 [0.25, 0.45] |
| evidence_prompt@groq_qwen_qwen3.8-27b | 60 | 1.00 [1.00, 1.00] | 0.04 [0.00, 0.08] | 0.01 [0.00, 0.02] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | – | 0.02 [0.00, 0.05] |
| evidence_prompt@vllm_Qwen_Qwen3-14B | 60 | 1.00 [1.00, 1.00] | 0.28 [0.13, 0.45] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | – | 0.17 [0.07, 0.30] |
| evidence_prompt@vllm_Qwen_Qwen3-32B-AWQ | 60 | 1.00 [1.00, 1.00] | 0.05 [0.00, 0.15] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | – | 0.05 [0.00, 0.13] |
| evidence_prompt@vllm_Qwen_Qwen3-4B | 60 | 0.93 [0.86, 1.00] | 0.12 [0.00, 0.29] | 0.01 [0.00, 0.02] | 0.05 [0.00, 0.15] | 0.00 [0.00, 0.00] | – | – | 0.07 [0.00, 0.17] |
| evidence_prompt@vllm_Qwen_Qwen3-8B | 60 | 1.00 [1.00, 1.00] | 0.32 [0.14, 0.50] | 0.02 [0.00, 0.05] | 0.05 [0.00, 0.15] | 0.00 [0.00, 0.00] | – | – | 0.15 [0.05, 0.27] |
| evidence_prompt@vllm_casperhansen_llama-3.3-70b-instruct-awq | 60 | 0.98 [0.93, 1.00] | 0.95 [0.87, 1.00] | 0.09 [0.05, 0.14] | 0.25 [0.05, 0.45] | 0.13 [0.00, 0.26] | – | – | 0.50 [0.40, 0.60] |
| scope_first@groq_openai_gpt-oss-120b | 60 | 0.93 [0.85, 1.00] | 0.93 [0.84, 1.00] | 0.12 [0.06, 0.18] | 0.05 [0.00, 0.15] | 0.43 [0.22, 0.57] | 0.33 [0.27, 0.40] | – | 0.57 [0.45, 0.68] |
| scope_first@groq_openai_gpt-oss-20b | 60 | 1.00 [1.00, 1.00] | 0.79 [0.66, 0.90] | 0.10 [0.05, 0.15] | 0.00 [0.00, 0.00] | 0.19 [0.04, 0.33] | 0.15 [0.08, 0.22] | – | 0.45 [0.32, 0.58] |
| scope_first@groq_qwen_qwen3.8-27b | 60 | 1.00 [1.00, 1.00] | 0.98 [0.94, 1.00] | 0.01 [0.00, 0.02] | 0.00 [0.00, 0.00] | 0.05 [0.00, 0.15] | 0.40 [0.35, 0.47] | – | 0.72 [0.65, 0.78] |
| scope_first@vllm_Qwen_Qwen3-14B | 60 | 1.00 [1.00, 1.00] | 0.21 [0.09, 0.35] | 0.02 [0.00, 0.04] | 0.15 [0.00, 0.35] | 0.00 [0.00, 0.00] | 0.03 [0.00, 0.08] | – | 0.12 [0.03, 0.22] |
| scope_first@vllm_Qwen_Qwen3-32B-AWQ | 60 | 0.95 [0.88, 1.00] | 0.56 [0.43, 0.70] | 0.03 [0.00, 0.06] | 0.10 [0.00, 0.25] | 0.00 [0.00, 0.00] | 0.41 [0.36, 0.47] | – | 0.32 [0.20, 0.43] |
| scope_first@vllm_Qwen_Qwen3-4B | 60 | 0.84 [0.71, 0.95] | 0.35 [0.22, 0.50] | 0.04 [0.01, 0.07] | 0.15 [0.00, 0.30] | 0.06 [0.00, 0.18] | 0.11 [0.04, 0.20] | – | 0.22 [0.10, 0.37] |
| scope_first@vllm_Qwen_Qwen3-8B | 60 | 1.00 [1.00, 1.00] | 0.49 [0.36, 0.62] | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.37 [0.33, 0.42] | – | 0.25 [0.12, 0.40] |
| scope_first@vllm_casperhansen_llama-3.3-70b-instruct-awq | 60 | 1.00 [1.00, 1.00] | 0.61 [0.41, 0.80] | 0.01 [0.00, 0.02] | 0.05 [0.00, 0.15] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | – | 0.42 [0.28, 0.53] |
| scope_pipeline@groq_openai_gpt-oss-120b | 60 | 0.98 [0.93, 1.00] | 0.96 [0.91, 1.00] | 0.06 [0.02, 0.12] | 0.00 [0.00, 0.00] | 0.09 [0.00, 0.24] | 0.03 [0.00, 0.08] | – | 0.60 [0.50, 0.70] |
| scope_pipeline@groq_qwen_qwen3.8-27b | 60 | 0.95 [0.89, 1.00] | 0.96 [0.91, 1.00] | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.14 [0.00, 0.39] | 0.41 [0.36, 0.49] | – | 0.68 [0.58, 0.78] |
| scope_pipeline@vllm_Qwen_Qwen3-14B | 60 | 0.95 [0.86, 1.00] | 0.72 [0.50, 0.91] | 0.05 [0.01, 0.10] | 0.00 [0.00, 0.00] | 0.39 [0.13, 0.61] | 0.03 [0.00, 0.08] | – | 0.47 [0.32, 0.62] |
| scope_pipeline@vllm_Qwen_Qwen3-32B-AWQ | 60 | 0.70 [0.55, 0.84] | 0.67 [0.48, 0.82] | 0.04 [0.01, 0.06] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.02 [0.00, 0.05] | – | 0.43 [0.30, 0.57] |
| scope_pipeline@vllm_Qwen_Qwen3-4B | 60 | 0.89 [0.77, 0.98] | 0.28 [0.14, 0.42] | 0.06 [0.03, 0.10] | 0.05 [0.00, 0.15] | 0.26 [0.07, 0.40] | 0.23 [0.13, 0.33] | – | 0.13 [0.03, 0.25] |
| scope_pipeline@vllm_Qwen_Qwen3-8B | 60 | 0.95 [0.88, 1.00] | 0.58 [0.38, 0.77] | 0.03 [0.00, 0.06] | 0.00 [0.00, 0.00] | 0.09 [0.00, 0.26] | 0.08 [0.03, 0.15] | – | 0.37 [0.22, 0.52] |
| scope_pipeline@vllm_casperhansen_llama-3.3-70b-instruct-awq | 60 | 0.93 [0.82, 1.00] | 0.79 [0.64, 0.93] | 0.01 [0.00, 0.03] | 0.00 [0.00, 0.00] | 0.08 [0.00, 0.26] | 0.03 [0.00, 0.08] | – | 0.55 [0.42, 0.67] |
| scope_pipeline_v0@groq_openai_gpt-oss-120b | 60 | 0.95 [0.89, 1.00] | 0.75 [0.57, 0.89] | 0.03 [0.01, 0.05] | 0.00 [0.00, 0.00] | 0.13 [0.00, 0.35] | 0.07 [0.02, 0.13] | – | 0.53 [0.42, 0.65] |
| scope_pipeline_v0@groq_qwen_qwen3.8-27b | 60 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.14 [0.00, 0.39] | 0.40 [0.35, 0.47] | – | 0.72 [0.62, 0.80] |

## Condition B

| system | n | Chg-D | Chg-P | PresErr-K | PresErr-K+ | U-F1 | Verdict | NoForbid | Exact |
|---|---|---|---|---|---|---|---|---|---|
| evidence_prompt@groq_openai_gpt-oss-120b | 60 | 0.98 [0.93, 1.00] | 0.86 [0.74, 0.96] | 0.05 [0.01, 0.10] | 0.15 [0.00, 0.30] | 0.10 [0.00, 0.23] | – | – | 0.50 [0.38, 0.62] |
| evidence_prompt@groq_qwen_qwen3.8-27b | 60 | 1.00 [1.00, 1.00] | 0.79 [0.60, 0.93] | 0.26 [0.17, 0.33] | 0.45 [0.25, 0.65] | 0.00 [0.00, 0.00] | – | – | 0.32 [0.20, 0.43] |
| evidence_prompt@vllm_Qwen_Qwen3-14B | 60 | 0.86 [0.74, 0.96] | 0.68 [0.56, 0.80] | 0.06 [0.03, 0.10] | 0.35 [0.15, 0.55] | 0.14 [0.00, 0.32] | – | – | 0.40 [0.30, 0.52] |
| evidence_prompt@vllm_Qwen_Qwen3-32B-AWQ | 60 | 0.70 [0.57, 0.83] | 0.35 [0.23, 0.48] | 0.05 [0.02, 0.09] | 0.35 [0.15, 0.55] | 0.05 [0.00, 0.14] | – | – | 0.22 [0.12, 0.33] |
| evidence_prompt@vllm_Qwen_Qwen3-4B | 60 | 0.61 [0.43, 0.79] | 0.40 [0.23, 0.58] | 0.01 [0.00, 0.03] | 0.10 [0.00, 0.25] | 0.00 [0.00, 0.00] | – | – | 0.25 [0.13, 0.38] |
| evidence_prompt@vllm_Qwen_Qwen3-8B | 60 | 0.68 [0.51, 0.84] | 0.46 [0.30, 0.64] | 0.04 [0.01, 0.08] | 0.30 [0.10, 0.50] | 0.05 [0.00, 0.15] | – | – | 0.25 [0.15, 0.35] |
| evidence_prompt@vllm_casperhansen_llama-3.3-70b-instruct-awq | 60 | 0.95 [0.89, 1.00] | 0.93 [0.86, 0.98] | 0.17 [0.12, 0.23] | 0.75 [0.55, 0.95] | 0.24 [0.09, 0.41] | – | – | 0.32 [0.20, 0.43] |
| no_revision | 60 | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.33 [0.33, 0.33] | – | 0.00 [0.00, 0.00] |
| oracle | 60 | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 1.00 [1.00, 1.00] | 1.00 [1.00, 1.00] | – | 1.00 [1.00, 1.00] |
| scope_first@groq_openai_gpt-oss-120b | 60 | 0.86 [0.74, 0.98] | 0.89 [0.79, 0.98] | 0.12 [0.06, 0.19] | 0.15 [0.00, 0.30] | 0.62 [0.47, 0.75] | 0.63 [0.50, 0.77] | – | 0.63 [0.50, 0.77] |
| scope_first@groq_qwen_qwen3.8-27b | 60 | 1.00 [1.00, 1.00] | 0.98 [0.94, 1.00] | 0.01 [0.00, 0.02] | 0.05 [0.00, 0.15] | 0.44 [0.21, 0.64] | 0.73 [0.65, 0.83] | – | 0.73 [0.65, 0.82] |
| scope_first@vllm_Qwen_Qwen3-14B | 60 | 0.82 [0.70, 0.93] | 0.46 [0.33, 0.60] | 0.10 [0.07, 0.12] | 0.75 [0.55, 0.95] | 0.38 [0.25, 0.49] | 0.00 [0.00, 0.00] | – | 0.17 [0.07, 0.28] |
| scope_first@vllm_Qwen_Qwen3-32B-AWQ | 60 | 0.86 [0.77, 0.95] | 0.82 [0.71, 0.92] | 0.09 [0.06, 0.12] | 0.65 [0.45, 0.85] | 0.26 [0.12, 0.39] | 0.33 [0.23, 0.43] | – | 0.43 [0.35, 0.52] |
| scope_first@vllm_Qwen_Qwen3-4B | 60 | 0.61 [0.44, 0.77] | 0.42 [0.28, 0.55] | 0.11 [0.07, 0.15] | 0.45 [0.25, 0.65] | 0.19 [0.00, 0.37] | 0.02 [0.00, 0.07] | – | 0.17 [0.08, 0.27] |
| scope_first@vllm_Qwen_Qwen3-8B | 60 | 0.84 [0.74, 0.93] | 0.58 [0.42, 0.73] | 0.16 [0.11, 0.22] | 0.80 [0.60, 0.95] | 0.18 [0.05, 0.29] | 0.10 [0.03, 0.17] | – | 0.22 [0.12, 0.32] |
| scope_first@vllm_casperhansen_llama-3.3-70b-instruct-awq | 60 | 0.82 [0.70, 0.93] | 0.75 [0.64, 0.86] | 0.08 [0.05, 0.12] | 0.55 [0.35, 0.75] | 0.45 [0.27, 0.62] | 0.00 [0.00, 0.00] | – | 0.43 [0.32, 0.55] |
| scope_pipeline@groq_openai_gpt-oss-120b | 60 | 0.93 [0.82, 1.00] | 0.95 [0.88, 1.00] | 0.07 [0.03, 0.12] | 0.05 [0.00, 0.15] | 0.73 [0.60, 0.85] | 0.62 [0.52, 0.72] | – | 0.63 [0.48, 0.77] |
| scope_pipeline@groq_qwen_qwen3.8-27b | 60 | 0.93 [0.82, 1.00] | 1.00 [1.00, 1.00] | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.72 [0.50, 0.88] | 0.57 [0.47, 0.67] | – | 0.80 [0.68, 0.90] |
| scope_pipeline@vllm_Qwen_Qwen3-14B | 60 | 0.75 [0.57, 0.90] | 0.51 [0.38, 0.64] | 0.06 [0.02, 0.10] | 0.15 [0.00, 0.30] | 0.69 [0.55, 0.81] | 0.72 [0.62, 0.82] | – | 0.38 [0.25, 0.52] |
| scope_pipeline@vllm_Qwen_Qwen3-32B-AWQ | 60 | 0.89 [0.75, 1.00] | 0.74 [0.57, 0.87] | 0.03 [0.01, 0.05] | 0.10 [0.00, 0.25] | 0.62 [0.37, 0.81] | 0.78 [0.70, 0.87] | – | 0.52 [0.38, 0.65] |
| scope_pipeline@vllm_Qwen_Qwen3-4B | 60 | 0.68 [0.51, 0.83] | 0.39 [0.22, 0.54] | 0.14 [0.09, 0.20] | 0.65 [0.45, 0.85] | 0.50 [0.37, 0.61] | 0.60 [0.48, 0.70] | – | 0.18 [0.10, 0.25] |
| scope_pipeline@vllm_Qwen_Qwen3-8B | 60 | 0.80 [0.65, 0.93] | 0.56 [0.40, 0.71] | 0.10 [0.03, 0.17] | 0.30 [0.10, 0.50] | 0.68 [0.50, 0.82] | 0.63 [0.55, 0.72] | – | 0.32 [0.20, 0.45] |
| scope_pipeline@vllm_casperhansen_llama-3.3-70b-instruct-awq | 60 | 0.75 [0.56, 0.93] | 0.61 [0.43, 0.79] | 0.05 [0.01, 0.09] | 0.05 [0.00, 0.15] | 0.85 [0.75, 0.94] | 0.88 [0.80, 0.97] | – | 0.55 [0.38, 0.72] |
| scope_pipeline_v0@groq_openai_gpt-oss-120b | 60 | 0.93 [0.82, 1.00] | 0.72 [0.56, 0.85] | 0.03 [0.00, 0.05] | 0.05 [0.00, 0.15] | 0.73 [0.60, 0.85] | 0.25 [0.17, 0.35] | – | 0.57 [0.42, 0.72] |
| scope_pipeline_v0@groq_qwen_qwen3.8-27b | 60 | 0.93 [0.82, 1.00] | 1.00 [1.00, 1.00] | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.72 [0.50, 0.88] | 0.80 [0.73, 0.87] | – | 0.80 [0.68, 0.90] |

## Condition E

| system | n | Chg-D | Chg-P | PresErr-K | PresErr-K+ | U-F1 | Verdict | NoForbid | Exact |
|---|---|---|---|---|---|---|---|---|---|
| evidence_prompt@groq_qwen_qwen3.8-27b | 60 | 1.00 [1.00, 1.00] | 0.77 [0.62, 0.90] | 0.02 [0.00, 0.06] | 0.05 [0.00, 0.15] | 0.00 [0.00, 0.00] | – | – | 0.48 [0.33, 0.62] |

## Cost of verification: B − A (same claims)

Negative change recall / exact = worse when feedback must be verified; positive PresErr = more collateral change.

| system | change_recall_D | change_recall_P | preservation_error_K | unresolved_F1 | interaction_exact |
|---|---|---|---|---|---|
| evidence_prompt@groq_openai_gpt-oss-120b | -0.02 [-0.07, 0.00] | 0.23 [0.05, 0.40] | 0.03 [-0.02, 0.07] | 0.10 [0.00, 0.23] | 0.07 [-0.03, 0.17] |
| evidence_prompt@groq_qwen_qwen3.8-27b | 0.00 [0.00, 0.00] | 0.75 [0.58, 0.90] | 0.25 [0.17, 0.33] | 0.00 [0.00, 0.00] | 0.30 [0.18, 0.42] |
| evidence_prompt@vllm_Qwen_Qwen3-14B | -0.14 [-0.26, -0.04] | 0.40 [0.27, 0.53] | 0.06 [0.03, 0.10] | 0.14 [0.00, 0.32] | 0.23 [0.15, 0.33] |
| evidence_prompt@vllm_Qwen_Qwen3-32B-AWQ | -0.30 [-0.43, -0.17] | 0.30 [0.17, 0.42] | 0.05 [0.02, 0.09] | 0.05 [0.00, 0.14] | 0.17 [0.03, 0.28] |
| evidence_prompt@vllm_Qwen_Qwen3-4B | -0.32 [-0.50, -0.14] | 0.28 [0.09, 0.47] | 0.01 [0.00, 0.02] | 0.00 [0.00, 0.00] | 0.18 [0.03, 0.32] |
| evidence_prompt@vllm_Qwen_Qwen3-8B | -0.32 [-0.49, -0.16] | 0.14 [-0.08, 0.37] | 0.03 [-0.02, 0.07] | 0.05 [0.00, 0.15] | 0.10 [-0.02, 0.23] |
| evidence_prompt@vllm_casperhansen_llama-3.3-70b-instruct-awq | -0.02 [-0.09, 0.05] | -0.02 [-0.10, 0.06] | 0.08 [0.05, 0.12] | 0.11 [0.00, 0.23] | -0.18 [-0.28, -0.08] |
| scope_first@groq_openai_gpt-oss-120b | -0.07 [-0.15, 0.00] | -0.04 [-0.09, 0.00] | 0.00 [-0.07, 0.08] | 0.20 [0.00, 0.41] | 0.07 [-0.05, 0.18] |
| scope_first@groq_qwen_qwen3.8-27b | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.00 [-0.02, 0.02] | 0.39 [0.14, 0.62] | 0.02 [-0.03, 0.08] |
| scope_first@vllm_Qwen_Qwen3-14B | -0.18 [-0.30, -0.07] | 0.25 [0.11, 0.39] | 0.08 [0.04, 0.11] | 0.38 [0.25, 0.49] | 0.05 [-0.07, 0.18] |
| scope_first@vllm_Qwen_Qwen3-32B-AWQ | -0.09 [-0.21, 0.02] | 0.26 [0.11, 0.40] | 0.06 [0.03, 0.10] | 0.26 [0.12, 0.39] | 0.12 [0.00, 0.25] |
| scope_first@vllm_Qwen_Qwen3-4B | -0.23 [-0.40, -0.09] | 0.07 [-0.07, 0.21] | 0.07 [0.02, 0.12] | 0.13 [-0.10, 0.35] | -0.05 [-0.13, 0.03] |
| scope_first@vllm_Qwen_Qwen3-8B | -0.16 [-0.26, -0.07] | 0.09 [-0.02, 0.20] | 0.15 [0.11, 0.19] | 0.18 [0.05, 0.29] | -0.03 [-0.17, 0.10] |
| scope_first@vllm_casperhansen_llama-3.3-70b-instruct-awq | -0.18 [-0.30, -0.07] | 0.14 [-0.04, 0.33] | 0.08 [0.04, 0.11] | 0.45 [0.27, 0.62] | 0.02 [-0.12, 0.17] |
| scope_pipeline@groq_openai_gpt-oss-120b | -0.05 [-0.16, 0.05] | -0.02 [-0.08, 0.04] | 0.01 [-0.04, 0.06] | 0.64 [0.42, 0.83] | 0.03 [-0.10, 0.17] |
| scope_pipeline@groq_qwen_qwen3.8-27b | -0.02 [-0.16, 0.09] | 0.04 [0.00, 0.09] | 0.00 [0.00, 0.00] | 0.58 [0.31, 0.82] | 0.12 [-0.02, 0.23] |
| scope_pipeline@vllm_Qwen_Qwen3-14B | -0.20 [-0.38, -0.07] | -0.21 [-0.42, 0.00] | 0.01 [-0.04, 0.06] | 0.31 [0.07, 0.56] | -0.08 [-0.23, 0.07] |
| scope_pipeline@vllm_Qwen_Qwen3-32B-AWQ | 0.18 [0.02, 0.37] | 0.07 [-0.15, 0.26] | -0.01 [-0.04, 0.01] | 0.62 [0.37, 0.81] | 0.08 [-0.08, 0.23] |
| scope_pipeline@vllm_Qwen_Qwen3-4B | -0.20 [-0.36, -0.07] | 0.11 [0.02, 0.19] | 0.08 [0.02, 0.14] | 0.24 [0.08, 0.43] | 0.05 [-0.05, 0.15] |
| scope_pipeline@vllm_Qwen_Qwen3-8B | -0.16 [-0.33, 0.00] | -0.02 [-0.19, 0.16] | 0.07 [0.01, 0.14] | 0.59 [0.34, 0.79] | -0.05 [-0.22, 0.12] |
| scope_pipeline@vllm_casperhansen_llama-3.3-70b-instruct-awq | -0.18 [-0.33, -0.05] | -0.18 [-0.35, -0.03] | 0.04 [0.01, 0.08] | 0.77 [0.55, 0.93] | 0.00 [-0.18, 0.18] |
| scope_pipeline_v0@groq_openai_gpt-oss-120b | -0.02 [-0.07, 0.00] | -0.04 [-0.23, 0.16] | 0.00 [-0.03, 0.03] | 0.60 [0.42, 0.79] | 0.03 [-0.12, 0.18] |
| scope_pipeline_v0@groq_qwen_qwen3.8-27b | -0.07 [-0.18, 0.00] | 0.00 [0.00, 0.00] | 0.00 [0.00, 0.00] | 0.58 [0.31, 0.82] | 0.08 [-0.03, 0.18] |

## Asking a verified editor to propagate: E − A (same claims)

Positive change recall on P = the literal reading of verified edits is a wording effect.

| system | change_recall_D | change_recall_P | preservation_error_K | unresolved_F1 | interaction_exact |
|---|---|---|---|---|---|
| evidence_prompt@groq_qwen_qwen3.8-27b | 0.00 [0.00, 0.00] | 0.74 [0.59, 0.87] | 0.01 [0.00, 0.04] | 0.00 [0.00, 0.00] | 0.47 [0.32, 0.60] |

## Change recall on P by dependency depth (condition B)

| system | depth 1 | depth 2+ |
|---|---|---|
| evidence_prompt@groq_openai_gpt-oss-120b | 0.87 (n=54) | 0.67 (n=3) |
| evidence_prompt@groq_qwen_qwen3.8-27b | 0.78 (n=54) | 1.00 (n=3) |
| evidence_prompt@vllm_Qwen_Qwen3-14B | 0.67 (n=54) | 1.00 (n=3) |
| evidence_prompt@vllm_Qwen_Qwen3-32B-AWQ | 0.33 (n=54) | 0.67 (n=3) |
| evidence_prompt@vllm_Qwen_Qwen3-4B | 0.41 (n=54) | 0.33 (n=3) |
| evidence_prompt@vllm_Qwen_Qwen3-8B | 0.46 (n=54) | 0.33 (n=3) |
| evidence_prompt@vllm_casperhansen_llama-3.3-70b-instruct-awq | 0.93 (n=54) | 1.00 (n=3) |
| no_revision | 0.00 (n=54) | 0.00 (n=3) |
| oracle | 1.00 (n=54) | 1.00 (n=3) |
| scope_first@groq_openai_gpt-oss-120b | 0.91 (n=54) | 0.67 (n=3) |
| scope_first@groq_qwen_qwen3.8-27b | 0.98 (n=54) | 1.00 (n=3) |
| scope_first@vllm_Qwen_Qwen3-14B | 0.48 (n=54) | 0.00 (n=3) |
| scope_first@vllm_Qwen_Qwen3-32B-AWQ | 0.83 (n=54) | 0.67 (n=3) |
| scope_first@vllm_Qwen_Qwen3-4B | 0.44 (n=54) | 0.00 (n=3) |
| scope_first@vllm_Qwen_Qwen3-8B | 0.57 (n=54) | 0.67 (n=3) |
| scope_first@vllm_casperhansen_llama-3.3-70b-instruct-awq | 0.76 (n=54) | 0.67 (n=3) |
| scope_pipeline@groq_openai_gpt-oss-120b | 0.94 (n=54) | 1.00 (n=3) |
| scope_pipeline@groq_qwen_qwen3.8-27b | 1.00 (n=54) | 1.00 (n=3) |
| scope_pipeline@vllm_Qwen_Qwen3-14B | 0.50 (n=54) | 0.67 (n=3) |
| scope_pipeline@vllm_Qwen_Qwen3-32B-AWQ | 0.74 (n=54) | 0.67 (n=3) |
| scope_pipeline@vllm_Qwen_Qwen3-4B | 0.39 (n=54) | 0.33 (n=3) |
| scope_pipeline@vllm_Qwen_Qwen3-8B | 0.54 (n=54) | 1.00 (n=3) |
| scope_pipeline@vllm_casperhansen_llama-3.3-70b-instruct-awq | 0.63 (n=54) | 0.33 (n=3) |
| scope_pipeline_v0@groq_openai_gpt-oss-120b | 0.72 (n=54) | 0.67 (n=3) |
| scope_pipeline_v0@groq_qwen_qwen3.8-27b | 1.00 (n=54) | 1.00 (n=3) |

## By feedback validity (condition B)

| system | validity | n | Chg-D | Chg-P | PresErr-K | PresErr-K+ | U-F1 | Verdict |
|---|---|---|---|---|---|---|---|---|
| evidence_prompt@groq_openai_gpt-oss-120b | false | 20 | 1.00 | 0.88 | 0.08 | 0.15 | – | – |
| evidence_prompt@groq_openai_gpt-oss-120b | unsupported | 16 | – | – | 0.02 | – | 0.10 | – |
| evidence_prompt@groq_openai_gpt-oss-120b | valid | 24 | 0.96 | 0.84 | 0.05 | – | – | – |
| evidence_prompt@groq_qwen_qwen3.8-27b | false | 20 | 1.00 | 0.88 | 0.27 | 0.45 | – | – |
| evidence_prompt@groq_qwen_qwen3.8-27b | unsupported | 16 | – | – | 0.33 | – | 0.00 | – |
| evidence_prompt@groq_qwen_qwen3.8-27b | valid | 24 | 1.00 | 0.71 | 0.19 | – | – | – |
| evidence_prompt@vllm_Qwen_Qwen3-14B | false | 20 | 0.75 | 0.58 | 0.13 | 0.35 | 0.00 | – |
| evidence_prompt@vllm_Qwen_Qwen3-14B | unsupported | 16 | – | – | 0.05 | – | 0.15 | – |
| evidence_prompt@vllm_Qwen_Qwen3-14B | valid | 24 | 0.96 | 0.77 | 0.02 | – | 0.00 | – |
| evidence_prompt@vllm_Qwen_Qwen3-32B-AWQ | false | 20 | 0.50 | 0.19 | 0.13 | 0.35 | – | – |
| evidence_prompt@vllm_Qwen_Qwen3-32B-AWQ | unsupported | 16 | – | – | 0.00 | – | 0.05 | – |
| evidence_prompt@vllm_Qwen_Qwen3-32B-AWQ | valid | 24 | 0.88 | 0.48 | 0.02 | – | 0.00 | – |
| evidence_prompt@vllm_Qwen_Qwen3-4B | false | 20 | 0.55 | 0.38 | 0.04 | 0.10 | – | – |
| evidence_prompt@vllm_Qwen_Qwen3-4B | unsupported | 16 | – | – | 0.00 | – | 0.00 | – |
| evidence_prompt@vllm_Qwen_Qwen3-4B | valid | 24 | 0.67 | 0.42 | 0.00 | – | – | – |
| evidence_prompt@vllm_Qwen_Qwen3-8B | false | 20 | 0.65 | 0.42 | 0.12 | 0.30 | – | – |
| evidence_prompt@vllm_Qwen_Qwen3-8B | unsupported | 16 | – | – | 0.00 | – | 0.05 | – |
| evidence_prompt@vllm_Qwen_Qwen3-8B | valid | 24 | 0.71 | 0.48 | 0.02 | – | – | – |
| evidence_prompt@vllm_casperhansen_llama-3.3-70b-instruct-awq | false | 20 | 0.95 | 0.88 | 0.33 | 0.75 | 0.00 | – |
| evidence_prompt@vllm_casperhansen_llama-3.3-70b-instruct-awq | unsupported | 16 | – | – | 0.07 | – | 0.28 | – |
| evidence_prompt@vllm_casperhansen_llama-3.3-70b-instruct-awq | valid | 24 | 0.96 | 0.97 | 0.11 | – | 0.00 | – |
| no_revision | false | 20 | 0.00 | 0.00 | 0.00 | 0.00 | – | 1.00 |
| no_revision | unsupported | 16 | – | – | 0.00 | – | 0.00 | 0.00 |
| no_revision | valid | 24 | 0.00 | 0.00 | 0.00 | – | – | 0.00 |
| oracle | false | 20 | 1.00 | 1.00 | 0.00 | 0.00 | – | 1.00 |
| oracle | unsupported | 16 | – | – | 0.00 | – | 1.00 | 1.00 |
| oracle | valid | 24 | 1.00 | 1.00 | 0.00 | – | – | 1.00 |
| scope_first@groq_openai_gpt-oss-120b | false | 20 | 0.85 | 0.92 | 0.08 | 0.15 | 0.00 | 0.70 |
| scope_first@groq_openai_gpt-oss-120b | unsupported | 16 | – | – | 0.31 | – | 0.72 | 0.56 |
| scope_first@groq_openai_gpt-oss-120b | valid | 24 | 0.88 | 0.87 | 0.03 | – | 0.00 | 0.62 |
| scope_first@groq_qwen_qwen3.8-27b | false | 20 | 1.00 | 1.00 | 0.02 | 0.05 | 0.00 | 0.90 |
| scope_first@groq_qwen_qwen3.8-27b | unsupported | 16 | – | – | 0.00 | – | 0.46 | 0.19 |
| scope_first@groq_qwen_qwen3.8-27b | valid | 24 | 1.00 | 0.97 | 0.00 | – | 0.00 | 0.96 |
| scope_first@vllm_Qwen_Qwen3-14B | false | 20 | 0.65 | 0.42 | 0.29 | 0.75 | 0.00 | 0.00 |
| scope_first@vllm_Qwen_Qwen3-14B | unsupported | 16 | – | – | 0.00 | – | 0.52 | 0.00 |
| scope_first@vllm_Qwen_Qwen3-14B | valid | 24 | 0.96 | 0.48 | 0.00 | – | 0.00 | 0.00 |
| scope_first@vllm_Qwen_Qwen3-32B-AWQ | false | 20 | 0.70 | 0.69 | 0.25 | 0.65 | 0.00 | 0.30 |
| scope_first@vllm_Qwen_Qwen3-32B-AWQ | unsupported | 16 | – | – | 0.02 | – | 0.31 | 0.00 |
| scope_first@vllm_Qwen_Qwen3-32B-AWQ | valid | 24 | 1.00 | 0.94 | 0.00 | – | 0.00 | 0.58 |
| scope_first@vllm_Qwen_Qwen3-4B | false | 20 | 0.45 | 0.27 | 0.21 | 0.45 | 0.00 | 0.00 |
| scope_first@vllm_Qwen_Qwen3-4B | unsupported | 16 | – | – | 0.10 | – | 0.26 | 0.07 |
| scope_first@vllm_Qwen_Qwen3-4B | valid | 24 | 0.75 | 0.55 | 0.03 | – | 0.00 | 0.00 |
| scope_first@vllm_Qwen_Qwen3-8B | false | 20 | 0.70 | 0.42 | 0.35 | 0.80 | 0.00 | 0.15 |
| scope_first@vllm_Qwen_Qwen3-8B | unsupported | 16 | – | – | 0.05 | – | 0.23 | 0.00 |
| scope_first@vllm_Qwen_Qwen3-8B | valid | 24 | 0.96 | 0.71 | 0.08 | – | 0.00 | 0.12 |
| scope_first@vllm_casperhansen_llama-3.3-70b-instruct-awq | false | 20 | 0.75 | 0.69 | 0.21 | 0.55 | 0.00 | 0.00 |
| scope_first@vllm_casperhansen_llama-3.3-70b-instruct-awq | unsupported | 16 | – | – | 0.02 | – | 0.59 | 0.00 |
| scope_first@vllm_casperhansen_llama-3.3-70b-instruct-awq | valid | 24 | 0.88 | 0.81 | 0.02 | – | 0.00 | 0.00 |
| scope_pipeline@groq_openai_gpt-oss-120b | false | 20 | 0.90 | 0.88 | 0.08 | 0.05 | 0.00 | 0.90 |
| scope_pipeline@groq_openai_gpt-oss-120b | unsupported | 16 | – | – | 0.05 | – | 0.76 | 0.94 |
| scope_pipeline@groq_openai_gpt-oss-120b | valid | 24 | 0.96 | 1.00 | 0.08 | – | – | 0.17 |
| scope_pipeline@groq_qwen_qwen3.8-27b | false | 20 | 0.90 | 1.00 | 0.02 | 0.00 | 0.00 | 1.00 |
| scope_pipeline@groq_qwen_qwen3.8-27b | unsupported | 16 | – | – | 0.00 | – | 0.75 | 0.62 |
| scope_pipeline@groq_qwen_qwen3.8-27b | valid | 24 | 0.96 | 1.00 | 0.02 | – | 0.00 | 0.17 |
| scope_pipeline@vllm_Qwen_Qwen3-14B | false | 20 | 0.65 | 0.42 | 0.08 | 0.15 | 0.00 | 0.75 |
| scope_pipeline@vllm_Qwen_Qwen3-14B | unsupported | 16 | – | – | 0.10 | – | 0.79 | 0.75 |
| scope_pipeline@vllm_Qwen_Qwen3-14B | valid | 24 | 0.83 | 0.58 | 0.02 | – | 0.00 | 0.67 |
| scope_pipeline@vllm_Qwen_Qwen3-32B-AWQ | false | 20 | 0.85 | 0.65 | 0.06 | 0.10 | – | 0.85 |
| scope_pipeline@vllm_Qwen_Qwen3-32B-AWQ | unsupported | 16 | – | – | 0.02 | – | 0.62 | 0.50 |
| scope_pipeline@vllm_Qwen_Qwen3-32B-AWQ | valid | 24 | 0.92 | 0.81 | 0.00 | – | – | 0.92 |
| scope_pipeline@vllm_Qwen_Qwen3-4B | false | 20 | 0.55 | 0.31 | 0.29 | 0.65 | 0.00 | 0.30 |
| scope_pipeline@vllm_Qwen_Qwen3-4B | unsupported | 16 | – | – | 0.05 | – | 0.72 | 0.75 |
| scope_pipeline@vllm_Qwen_Qwen3-4B | valid | 24 | 0.79 | 0.45 | 0.08 | – | 0.00 | 0.75 |
| scope_pipeline@vllm_Qwen_Qwen3-8B | false | 20 | 0.70 | 0.62 | 0.17 | 0.30 | 0.00 | 0.30 |
| scope_pipeline@vllm_Qwen_Qwen3-8B | unsupported | 16 | – | – | 0.05 | – | 0.73 | 0.69 |
| scope_pipeline@vllm_Qwen_Qwen3-8B | valid | 24 | 0.88 | 0.52 | 0.06 | – | 0.00 | 0.88 |
| scope_pipeline@vllm_casperhansen_llama-3.3-70b-instruct-awq | false | 20 | 0.70 | 0.50 | 0.04 | 0.05 | 0.00 | 0.90 |
| scope_pipeline@vllm_casperhansen_llama-3.3-70b-instruct-awq | unsupported | 16 | – | – | 0.12 | – | 0.94 | 1.00 |
| scope_pipeline@vllm_casperhansen_llama-3.3-70b-instruct-awq | valid | 24 | 0.79 | 0.71 | 0.02 | – | 0.00 | 0.79 |
| scope_pipeline_v0@groq_openai_gpt-oss-120b | false | 20 | 0.90 | 0.58 | 0.04 | 0.05 | 0.00 | 0.55 |
| scope_pipeline_v0@groq_openai_gpt-oss-120b | unsupported | 16 | – | – | 0.05 | – | 0.76 | 0.25 |
| scope_pipeline_v0@groq_openai_gpt-oss-120b | valid | 24 | 0.96 | 0.84 | 0.00 | – | – | 0.00 |
| scope_pipeline_v0@groq_qwen_qwen3.8-27b | false | 20 | 0.90 | 1.00 | 0.02 | 0.00 | 0.00 | 1.00 |
| scope_pipeline_v0@groq_qwen_qwen3.8-27b | unsupported | 16 | – | – | 0.00 | – | 0.75 | 0.25 |
| scope_pipeline_v0@groq_qwen_qwen3.8-27b | valid | 24 | 0.96 | 1.00 | 0.02 | – | 0.00 | 1.00 |

## By model scale (condition B unless marked; dev unless the run used --split test)

Prompt = evidence_prompt, Pipe = scope_pipeline. Syc = PresErr-K+ (evidence-supported claims changed under false feedback). A-Chg-P = bare verified edit.

| model | family | params (B) | tier | review | Prompt A-Chg-P | Prompt Chg-P | Prompt Syc | Prompt U-F1 | Prompt Exact | Pipe Chg-P | Pipe Syc | Pipe Verdict | Pipe Exact |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| groq_openai_gpt-oss-20b | GPT (open-weight) | 21 | 20-32B |  | 0.68 | – | – | – | – | – | – | – | – |
| groq_openai_gpt-oss-120b | GPT (open-weight) | 117 | 100B+ | yes | 0.63 | 0.86 | 0.15 | 0.10 | 0.50 | 0.95 | 0.05 | 0.62 | 0.63 |
| gemini_gemma-4-31b-it | Gemma | 31 | 20-32B |  | 1.00 | – | – | – | – | – | – | – | – |
| vllm_casperhansen_llama-3.3-70b-instruct-awq | Llama | 70 | 70B | yes | 0.95 | 0.93 | 0.75 | 0.24 | 0.32 | 0.61 | 0.05 | 0.88 | 0.55 |
| vllm_Qwen_Qwen3-4B | Qwen | 4 | 3-4B | yes | 0.12 | 0.40 | 0.10 | 0.00 | 0.25 | 0.39 | 0.65 | 0.60 | 0.18 |
| vllm_Qwen_Qwen3-8B | Qwen | 8 | 7-8B | yes | 0.32 | 0.46 | 0.30 | 0.05 | 0.25 | 0.56 | 0.30 | 0.63 | 0.32 |
| vllm_Qwen_Qwen3-14B | Qwen | 14 | 14B | yes | 0.28 | 0.68 | 0.35 | 0.14 | 0.40 | 0.51 | 0.15 | 0.72 | 0.38 |
| groq_qwen_qwen3.8-27b | Qwen | 27 | 20-32B | yes | 0.04 | 0.79 | 0.45 | 0.00 | 0.32 | 1.00 | 0.00 | 0.57 | 0.80 |
| vllm_Qwen_Qwen3-32B-AWQ | Qwen | 32 | 20-32B |  | 0.05 | 0.35 | 0.35 | 0.05 | 0.22 | 0.74 | 0.10 | 0.78 | 0.52 |

