# IntExR-Scope — Literature Review (v0.1, 2 Oct 2026)

**Scope of this review:** Paper 1 (IntExR-Scope). A short section at the end covers work next to Paper 2 so the novelty review in spring 2027 has a starting point.
**Status:** first pass. Each row in §10 says whether I checked it in this session (`web`) or wrote it from memory (`recall`). Read and check every `recall` row before the **31 Oct novelty review**. Read the `HIGH`-risk papers in full.

---

## 0. One-paragraph summary

Six research threads each cover part of IntExR-Scope. None covers all of it:

1. **Evidence-based revision** (RARR, FRUIT, FAVA, MEDEC, CorBenchX) fixes claims that evidence contradicts. These benchmarks treat the evidence as the oracle, usually fix one error at a time, and do not label the claims that depend on a fix.
2. **Edit propagation** (RippleEdits, MQuAKE, EditPropBench, RevPropBench, LEDGER) labels direct versus downstream changes and protected content. The 2026 papers come very close to the IntExR scope labels. However, they **assume the requested edit is correct**, never ask the model to abstain, and use synthetic or JSON artifacts.
3. **Model editing** (ROME/MEMIT, GRACE, WISE, AlphaEdit) gives us the vocabulary of *locality / specificity / portability*. It edits parameters, though, not the text of a response.
4. **Sycophancy and persuasion** (Sharma et al. 2024; SycEval; PBT; Med-Stress 2026) tests whether models give in to false feedback. It scores the *whole answer* as right or wrong, so it cannot see feedback that is right about one claim and wrong about another.
5. **Belief revision** (AGM; truth-maintenance systems; BeliefBank; Belief-R; ReviseQA) is the right theory: minimal change, dependency-directed retraction, and the difference between revision and update. LLM benchmarks in this thread use toy logic problems.
6. **Abstention** (AbstentionBench, evidence-sufficiency work) covers answer-level "I don't know". It does not cover marking a single claim as unresolved inside a revision.

**The gap IntExR-Scope fills:** no benchmark *jointly* requires the model to (a) treat feedback as a hypothesis to check against evidence rather than an instruction, (b) partition **every** claim of one multi-claim response into direct / propagated / keep / unresolved, and (c) do this in a real, high-stakes domain where claims depend on each other through inference, as in radiology, where the impression follows from the findings.

**Biggest novelty risk:** EditPropBench (Kruthof, 2026, in review at NeurIPS D&B) and RevPropBench (Kikuta, EMNLP 2026 Industry). We must show *empirically* that uncertainty about whether the feedback is valid changes behaviour on scope and propagation. The planned ablation is in §9.

---

## 1. Evidence-based response revision

| Paper | What it does | Relevance / gap |
|---|---|---|
| **Shah, Schuster & Barzilay, AAAI 2020**, *Automatic Fact-guided Sentence Modification* | Rewrites one sentence so it agrees with an updated fact. | The earliest "update text given new evidence" task. Single sentence, no dependents. |
| **Thorne & Vlachos, ACL 2021**, *Evidence-based Factual Error Correction* | Corrects a claim using retrieved evidence. Distant supervision on FEVER. | Claim-level. Assumes the evidence is reliable. No preservation of other claims, because there is only one claim. |
| **Schuster et al., NAACL 2021**, *VitaminC* | Contrastive Wikipedia revisions in which a small change in evidence flips the verdict. Includes a "factual revision" task. | Shows models can be sensitive to small evidence changes. Has an NEI (not enough info) label, the closest thing to *unresolved*. |
| **Logan IV et al., NAACL 2022**, *FRUIT: Faithfully Reflecting Updated Information in Text* | Updates a Wikipedia article given new evidence snippets. | **Closest older task.** Multi-sentence. Measures whether unchanged content is kept (UpdateROUGE). Has no dependency or propagation labels, does not test unreliable evidence, and has no abstention. A candidate non-medical source (§9). |
| **Gao et al., ACL 2023**, *RARR* | Research-and-revise. Retrieves evidence and edits unsupported spans. | Introduced the **attribution vs. preservation** trade-off and measured preservation explicitly. That is our K label. Has no propagation, and treats retrieved evidence as the truth. |
| **Chen et al., 2023**, *PURR* | Trains an editor by denoising synthetic corruptions. | A cheaper RARR. Same gaps. |
| **Zhao et al., ACL 2023**, *Verify-and-Edit* | Edits chain-of-thought reasoning against retrieved facts. | Reasoning-chain editing is a form of propagation. It is not evaluated as such. |
| **Gou et al., ICLR 2024**, *CRITIC* | Self-critique using tools (search, code). | Tool-based verification. No claim-level scope accounting. |
| **Madaan et al., NeurIPS 2023**, *Self-Refine* | Iterative self-feedback. | An "always rewrite" style baseline. Known to over-revise. |
| **Dhuliawala et al., Findings ACL 2024**, *Chain-of-Verification* | Plans verification questions per claim, then revises. | Decomposes and verifies per claim. This is the closest *method* ancestor of our scope-first pipeline (decompose → verify → revise). |
| **Mishra et al., COLM 2024**, *FAVA* | Fine-grained hallucination taxonomy plus an editor. | Edit-based output, so preservation is implicit. Its "unverifiable" type is close to U. |
| **Huang et al., ACL 2023**, *ZeroFEC* | Zero-shot factual error correction by question answering. | Single claim. |
| **Wadhwa et al., Findings EMNLP 2024**, *Learning to Refine with Fine-Grained Natural Language Feedback* | Splits refinement into detect → critique → refine at the claim level. | Shows that claim-level decomposition helps refinement. Assumes the feedback comes from a reliable critic. |

**Takeaway.** This thread defines the *direct update* and *preservation* parts. It does not test propagation, unreliable feedback, or abstention.

## 2. Claim decomposition and claim-level factuality (infrastructure)

- **FActScore** (Min et al., EMNLP 2023): atomic-fact decomposition plus support scoring. **SAFE / LongFact** (Wei et al., NeurIPS 2024), **VeriScore** (Song et al., Findings EMNLP 2024), and **VeriFastScore** (2025) extend it to long-form answers with search.
- **Use for IntExR:** the "decompose into claims" and "align to evidence" steps of the scope-first method come from here. The same papers document the known weaknesses: atomic facts vary in granularity, and decontextualization fails for claims that depend on each other. We must fix granularity in the annotation guide (one clinical finding = one claim).
- **RAGTruth** (Niu et al., ACL 2024) has span-level labels for unsupported or contradicted content in RAG outputs. It is useful as an evidence-alignment sanity check.

## 3. Medical and radiology correction (domain thread)

| Paper | What it does | Gap relative to IntExR |
|---|---|---|
| **Ben Abacha et al., Findings ACL 2025**, *MEDEC* (+ MEDIQA-CORR 2024 shared task) | Detect, locate, and correct one injected error in a clinical note. 3,848 texts. Clinicians perform at about 80%. | One error per note. No dependents, no preservation metric, feedback not modelled. |
| **Rao et al., PSB 2025**, *ReXErr* | LLM-injected, clinically meaningful errors in MIMIC-CXR reports. | Supplies error *types* for CXR (laterality, severity, negation, omission). Useful for perturbations. |
| **Zou et al., 2025**, *CorBenchX* (arXiv 2505.12057) | 26k CXR reports with errors injected by DeepSeek-R1. Detect + correct, with RL fine-tuning. | Scored with BLEU/ROUGE/CheXbert. **Does not measure** whether correct content survives the revision. No propagation. |
| **Pellegrini et al., MIDL 2025**, *RaDialog* | Interactive radiology report generation and correction from clinician instructions. | Closest *interactive* radiology system. Assumes the feedback is correct. Evaluates the whole report. |
| **Jain et al., NeurIPS D&B 2021**, *RadGraph* (+ RadGraph-XL 2024) | Entity/relation graph for CXR reports. Its `suggestive_of` relation links findings to diagnoses (consolidation → pneumonia). | **A key resource:** `suggestive_of` edges give real finding → impression dependencies for P labels. Available on PhysioNet. |
| **Ostmeier et al., Findings EMNLP 2024**, *GREEN*; **Bannur et al., 2024**, *MAIRA-2 / RadFact* | Error-counting and sentence-level entailment metrics for reports. | RadFact's sentence-level logical precision/recall is the right evaluation primitive for "evidence support" and "residual contradiction". |
| **Bannur et al., CVPR 2023**, *BioViL-T* / *MS-CXR-T* | Temporal CXR, comparing against a prior study. | A prior study used as **new evidence**, and temporal "interval change" claims, are a natural source of superseding updates. |
| **Xiao et al., ACL 2026**, *When Correct Beliefs Collapse* (Med-Stress) | Multi-turn clinical pressure makes models abandon correct diagnoses. Proposes the RBED and R-FT defences. | Strong evidence that clinical sycophancy is real. Labelled at the answer level. |
| **Chen et al., npj Digit. Med. 2025**, *When helpfulness backfires* | Models comply with illogical medical requests. | Same caveat: one decision per prompt. |

**Takeaway.** Radiology has (i) a natural dependency structure from findings to impression to recommendation, (ii) public structure annotations (RadGraph), and (iii) documented sycophancy. **No existing CXR correction benchmark measures propagation or preservation.**

## 4. Locality and preservation in model editing

- **Methods:** KnowledgeEditor (De Cao et al., EMNLP 2021); MEND and SERAC (Mitchell et al., ICLR/ICML 2022); ROME (Meng et al., NeurIPS 2022) and MEMIT (ICLR 2023); GRACE (Hartvigsen et al., NeurIPS 2023); WISE (Wang et al., NeurIPS 2024); AlphaEdit (Fang et al., ICLR 2025, null-space constrained).
- **Evaluation vocabulary:** *efficacy*, *generalization* (paraphrase), *specificity/locality* (neighbourhood prompts unchanged), *portability* (Yao et al., EMNLP 2023 survey), *fluency*. CounterFact and zsRE are the standard datasets, and KnowEdit (Zhang et al., 2024) unifies them.
- **Side effects:** Gupta et al. (Findings ACL 2024) show that edits at scale cause gradual, then catastrophic, forgetting. Li et al. (ICLR 2024, *Unveiling the Pitfalls*) show that edits can conflict and distort knowledge.
- **Long-form:** **LEME** (Rosati et al., NAACL 2024) evaluates edited models on long-form generation. It finds *factual drift*, and its long-form scores barely correlate with short-form locality scores. **DocMEdit** (Zeng et al., Findings ACL 2025) makes edits at document level (38k items) and finds low accuracy with large side effects.
- **Medical:** MedLaSA / MedCF (Xu et al., 2024) edit medical facts with a locality test set.
- **Use for IntExR:** we borrow the *locality = preservation* framing and the metric names. Paper 1 is about **non-parametric text revision**, so locality is measured on the claims of the response, not on neighbouring prompts. Paper 2 reconnects to the parametric thread (GRACE, WISE, AlphaEdit as lifelong-editing baselines).

## 5. Propagation of corrections across dependent claims ← most important thread

| Paper | Setting | D | P | Pres. | Unres. | Unrel. FB |
|---|---|---|---|---|---|---|
| **Onoe et al., ACL 2023**, *Can LMs learn new entities from descriptions?* | Inject an entity description, test inferences | ✓ | ✓ | ◐ | ✗ | ✗ |
| **Zhong et al., EMNLP 2023**, *MQuAKE* (+ *MQuAKE-Remastered*, ICLR 2025) | Multi-hop questions after an edit | ✓ | ✓ | ✗ | ✗ | ✗ |
| **Cohen et al., TACL 2024**, *RippleEdits* | Six criteria, including logical generalization, compositionality, and **relation specificity / preservation** | ✓ | ✓ | ✓ | ✗ | ✗ |
| **Li et al., Findings EMNLP 2023**, *DepEdit* (specificity & implication awareness) | Dependency-aware evaluation of fact editing | ✓ | ✓ | ✓ | ✗ | ✗ |
| **Padmanabhan et al., NeurIPS 2023**, *Propagating knowledge updates via distillation* | Distil an entity definition into weights | ✓ | ✓ | ◐ | ✗ | ✗ |
| **Liu et al., 2025**, *PropMEND* (arXiv 2506.08920) | Hypernetwork meta-trained for propagation; Controlled RippleEdit | ✓ | ✓ | ◐ | ✗ | ✗ |
| **ChainEdit, 2025** (arXiv 2507.08427) | Propagating ripple effects with logical rules | ✓ | ✓ | ◐ | ✗ | ✗ |
| **Kruthof, 2026**, ***EditPropBench*** (arXiv 2605.02083; in review at NeurIPS D&B) | Synthetic ML manuscripts with fact graphs. Labels **direct targets, required downstream updates, protected text**. Metrics: ERA, LES, collateral damage rate | ✓ | ✓ | ✓ | ✗ | ✗ |
| **Kikuta, EMNLP 2026 Industry**, ***RevPropBench*** (*What Else Needs Fixing?*, arXiv 2609.03254) | JSON artifacts from conversations in 9 domains. Labels **direct vs. cascade**. Metrics: miss, over-edit, wrong value. Ambiguous cases explicitly excluded | ✓ | ✓ | ✓ | ✗ | ✗ |
| **LEDGER, Findings ACL 2026** (arXiv 2606.28379) | Agentic document editing with a dependency graph. Consistency 76% vs. 56% for the baseline | ✓ | ✓ | ◐ | ✗ | ✗ |

**Findings to cite in our motivation:**
- On EditPropBench's hard implicit stratum, the best system (Claude Opus 4.6) misses about 30% of required downstream updates (ERA 0.705, range 0.148–0.705). Plan-then-edit *underperformed* direct editing (0.555 vs. 0.705). This is a warning for our scope-first pipeline: an explicit planning step can hurt propagation recall. We must ablate it.
- RevPropBench: completion runs from 68% to 93%. Choosing the best of three samples helps by 2–10 points. "OR"-merging edits causes over-editing and "AND"-merging drops correct edits. The **precision/recall trade-off between over- and under-revision** is real and should be a headline plot for us.
- LEME: short-form locality does not predict long-form drift. Supports measuring preservation on the actual response.

**Takeaway / differentiation.** EditPropBench and RevPropBench already established "direct + propagated + protected" as a benchmark design. **IntExR-Scope must not claim the D/P/K partition itself as the novelty.** What remains new:
- (i) **Feedback validity is unknown.** The edit is a claim to verify, so the correct D set is defined by evidence, not by the request. This produces cases neither paper can express: *correct feedback with no evidence → U*; *wrong feedback on a claim the evidence overturns anyway → D*; *partial feedback → D on some claims, K on others*.
- (ii) **An unresolved label, and unresolved status that propagates** through dependencies.
- (iii) **Real clinical text** with inferential, not arithmetic, dependencies. RevPropBench's six patterns are arithmetic, substitution, add/remove, threshold, temporal, and status-flip. Ours are clinical inference, recommendation, and temporal scope.
- (iv) **Temporal scope:** superseding evidence that should change forward-looking claims but *not* descriptions of an earlier state (pilot example `cxr-004`).

## 6. Minimal text revision and over-editing

- **Text-editing models and data:** IteraTeR (Du et al., ACL 2022) gives a taxonomy of revision intents. PEER (Schick et al., 2022), CoEdIT (Raheja et al., Findings EMNLP 2023) and EditEval (Dwivedi-Yu et al., 2022/2024) cover instruction-based editing. ARIES (D'Arcy et al., ACL 2024) contains scientific paper edits made in response to reviewer feedback. It is a real feedback-driven revision corpus.
- **Over-correction:** minimal-edit GEC work (2025–26) documents LLM over-correction and mitigates it with prompts, batching, and edit-level voting. *When Models Edit Too Much* (2026) finds over-editing is the *default* behaviour of code LLMs, and an explicit "preserve" clause cuts excess edit distance by about 33%.
- **Use for IntExR:**
  - The preservation error and over-revision metrics need a semantic definition: a K claim is "changed" if its meaning changes, not if its wording changes. Report both string-level and semantic-level numbers.
  - A "preservation clause" prompt is a cheap, strong baseline we must include, so the scope-first method is not compared against a weak baseline.

## 7. Feedback verification, sycophancy, persuasion, knowledge conflict

- **Sycophancy:**
  - Sharma et al. (ICLR 2024) document sycophancy across RLHF models.
  - Wei et al. (2023) reduce it with simple synthetic data.
  - FlipFlop (Laban et al., 2023) shows that "Are you sure?" flips answers.
  - Wang et al. (Findings EMNLP 2023) find ChatGPT cannot defend true beliefs in debate.
  - SycEval (Fanous et al., 2025) covers medical and maths questions: 58% sycophantic behaviour, 14.7% *regressive*.
  - MedPRESS (2026, arXiv 2608.02520) and *Why LLMs Give In* (2026, arXiv 2608.01017) study conversational factors behind medical sycophancy.
- **Accept vs. resist:** **Stengel-Eskin, Hase & Bansal, NAACL 2025**, *Persuasion-Balanced Training (PBT)*. Training only to resist persuasion hurts acceptance of good persuasion, and the reverse. **This is the closest conceptual match to our "verify feedback" axis.** PBT works per answer, not per claim.
- **Self-correction limits:** Huang et al. (ICLR 2024) show LLMs cannot self-correct reasoning without external feedback. Kamoi et al. (TACL 2024) survey when self-correction works and conclude that reliable external feedback is the key ingredient. **Motivates giving explicit evidence.**
- **Knowledge conflict / unreliable evidence:**
  - Xie et al. (ICLR 2024, *Adaptive Chameleon or Stubborn Sloth*): models are highly receptive to coherent external evidence even when it conflicts with what they know.
  - Xu et al. (EMNLP 2024): survey of knowledge conflicts.
  - **ClashEval** (Wu et al., NeurIPS 2024 D&B): models adopt wrong retrieved content, including drug dosages, more than 60% of the time.
  - Xu et al. (ACL 2024, *The Earth is Flat because...*): persuasive misinformation.
  - *Faithfulness vs. Safety under counterfactual medical evidence* (2026, arXiv 2601.11886).
- **Multi-turn feedback:** MINT (Wang et al., ICLR 2024) evaluates multi-turn interaction with tools and natural-language feedback. *LLMs Get Lost in Multi-Turn Conversation* (Laban et al., 2025) finds a large drop in multi-turn performance.
- **Takeaway.** All of these score *one decision per interaction*: flip or don't flip. None scores the *partition* of a multi-claim response when feedback is partly right. That is our axis.

## 8. Belief revision and contradiction propagation

- **Classical theory (cite in the task definition):**
  - **AGM** (Alchourrón, Gärdenfors & Makinson, 1985): rationality postulates for revision, with *minimal change* as the core.
  - **Katsuno & Mendelzon (1991):** *revision* (the world is the same, our information was wrong) versus *update* (the world changed). This is exactly our `cxr-004` distinction between correction and supersession.
  - **Truth-maintenance systems:** Doyle (1979, JTMS) and de Kleer (1986, ATMS) store a justification for each belief and retract dependent beliefs when a support is removed. This is *dependency-directed* propagation and an exact formal ancestor of our P label.
- **LLM belief work:**
  - BeliefBank (Kassner et al., EMNLP 2021): memory plus a constraint solver for consistency.
  - ConCoRD (Mitchell et al., EMNLP 2022).
  - Hase et al. (EACL 2023): measure and update beliefs with belief graphs, and test whether updates spread to related beliefs.
  - Hase et al. (2024), *Fundamental Problems With Model Editing: How Should Rational Belief Revision Work in LLMs?*: a position paper that recommends evaluating editing against a normative belief-revision standard. **Cite as philosophical motivation.**
- **Benchmarks:**
  - **Belief-R** (Wilie et al., EMNLP 2024): premises that should defeat an earlier conclusion. The BREU metric balances *update* against *maintain*, roughly our D/P vs. K balance.
  - **ReviseQA** (Helwe, AlRashed & Orabona, ICML 2025 workshop): multi-turn logic with added and removed facts.
  - **DeltaLogic** (2026): minimal premise edits.
  - All three use synthetic logic. None uses natural-language responses with evidence of varying reliability.

## 9. Benchmarks for updating long-form responses, and our positioning

| Benchmark | Unit | Domain | Evidence given? | Feedback can be wrong? | Partial scope labels? | Abstain? |
|---|---|---|---|---|---|---|
| FRUIT 2022 | article | Wikipedia | ✓ | ✗ | ✗ | ✗ |
| RARR 2023 | passage | open QA | retrieved | n/a | ✗ (spans) | ✗ |
| LEME 2024 | long-form gen | Wikidata entities | n/a (param.) | ✗ | ◐ | ✗ |
| DocMEdit 2025 | document | Wikipedia | ✓ | ✗ | ◐ | ✗ |
| MEDEC 2025 | note | clinical | ✗ | n/a | ✗ (1 error) | ✗ |
| CorBenchX 2025 | report | CXR | image | n/a | ✗ | ✗ |
| EditPropBench 2026 | manuscript | synthetic ML papers | fact graph | ✗ | ✓ D/P/protected | ✗ |
| RevPropBench 2026 | JSON artifact | 9 practical domains | conversation | ✗ | ✓ direct/cascade | ✗ (excluded) |
| PBT / SycEval / Med-Stress | answer | QA / medical | ◐ | ✓ | ✗ | ✗ |
| **IntExR-Scope (ours)** | **multi-claim response** | **CXR + non-medical** | **✓ prior + new** | **✓ (6 validity types)** | **✓ D/P/K/U + deps** | **✓** |

**The ablation that answers the novelty question.** Run the same examples under three conditions:

- **(A) verified-edit:** the gold-correct edit is given as an instruction. This is the EditPropBench/RevPropBench condition.
- **(B) unverified feedback + evidence:** the IntExR condition.
- **(C) evidence only, no feedback.**

If propagation recall or preservation is significantly worse in (B) than in (A) on the *same* claims, the joint setting is not a simple union of existing benchmarks. That result is the core argument of the paper. The pilot should already estimate this effect.

**Non-medical source decision.** COCO captions (current plan) are real and multi-annotator. Five captions per image give a natural new-evidence split and natural *conflict* (for example, "open lid" vs. "on the lid"), which suits U. However, dependencies are shallow: inferences from objects to activity or setting, usually depth 1. Alternatives if the pilot shows COCO is too easy for P:

- FRUIT/Wikipedia updates, with real temporal supersession.
- ARIES, real revisions made in response to reviewer feedback.

Decide after the pilot (see plan, wk 5).

## 10. Coverage matrix (requested)

✓ = central to the evaluation, ◐ = partly or implicitly covered, ✗ = not covered. "Unreliable FB" means the paper evaluates feedback or evidence that may be false, partial, ambiguous, or outdated. "Checked" says whether I looked at the source in this session (`web`) or wrote the row from memory (`recall`). A machine-readable copy is in [`literature_matrix.csv`](literature_matrix.csv).

| # | Paper (venue) | Thread | Evaluates | Direct | Propagated | Preservation | Unresolved | Unreliable FB | Checked | Risk to novelty |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | EditPropBench (Kruthof, arXiv 2026) | propagation | edit-ripple adherence in synthetic manuscripts | ✓ | ✓ | ✓ | ✗ | ✗ | web | **HIGH** |
| 2 | RevPropBench / What Else Needs Fixing? (Kikuta, EMNLP-Ind 2026) | propagation | direct vs. cascade edits in JSON artifacts | ✓ | ✓ | ✓ | ✗ | ✗ | web | **HIGH** |
| 3 | LEDGER (Findings ACL 2026) | propagation | dependency-graph agentic doc editing | ✓ | ✓ | ◐ | ✗ | ✗ | web | MED |
| 4 | RippleEdits (Cohen et al., TACL 2024) | propagation | ripple effects of KE | ✓ | ✓ | ✓ | ✗ | ✗ | web | MED |
| 5 | MQuAKE (Zhong et al., EMNLP 2023) | propagation | multi-hop after edit | ✓ | ✓ | ✗ | ✗ | ✗ | recall | LOW |
| 6 | DepEdit (Li et al., Findings EMNLP 2023) | propagation | specificity + implication | ✓ | ✓ | ✓ | ✗ | ✗ | recall | LOW |
| 7 | Onoe et al. (ACL 2023) | propagation | entity-knowledge inferences | ✓ | ✓ | ◐ | ✗ | ✗ | recall | LOW |
| 8 | PropMEND (Liu et al., 2025) | propagation | hypernetwork propagation | ✓ | ✓ | ◐ | ✗ | ✗ | web | LOW |
| 9 | ChainEdit (2025) | propagation | logic-rule ripple propagation | ✓ | ✓ | ◐ | ✗ | ✗ | web | LOW |
| 10 | LEME (Rosati et al., NAACL 2024) | model editing | long-form drift after edits | ✓ | ◐ | ✓ | ✗ | ✗ | web | MED |
| 11 | DocMEdit (Zeng et al., Findings ACL 2025) | model editing | document-level edits | ✓ | ◐ | ◐ | ✗ | ✗ | web | MED |
| 12 | ROME / MEMIT (Meng et al., 2022/23) | model editing | efficacy, paraphrase, neighborhood | ✓ | ✗ | ✓ | ✗ | ✗ | recall | LOW |
| 13 | GRACE / WISE / AlphaEdit (2023–25) | lifelong editing | sequential edits, locality, retention | ✓ | ✗ | ✓ | ✗ | ✗ | recall | LOW (P2: MED) |
| 14 | Gupta et al. (Findings ACL 2024) | model editing | forgetting at scale | ✗ | ✗ | ✓ | ✗ | ✗ | recall | LOW |
| 15 | MedLaSA/MedCF (Xu et al., 2024) | medical KE | medical edits + locality | ✓ | ✗ | ✓ | ✗ | ✗ | recall | LOW |
| 16 | FRUIT (Logan IV et al., NAACL 2022) | evidence revision | article update from new evidence | ✓ | ◐ | ✓ | ✗ | ✗ | recall | MED |
| 17 | RARR (Gao et al., ACL 2023) | evidence revision | attribution + preservation | ✓ | ✗ | ✓ | ✗ | ✗ | recall | MED |
| 18 | PURR (Chen et al., 2023) | evidence revision | denoising editor | ✓ | ✗ | ✓ | ✗ | ✗ | recall | LOW |
| 19 | VitaminC (Schuster et al., NAACL 2021) | evidence revision | contrastive evidence, revision | ✓ | ✗ | ◐ | ◐ | ✗ | recall | LOW |
| 20 | Thorne & Vlachos (ACL 2021) | claim correction | evidence-based FEC | ✓ | ✗ | ◐ | ✗ | ✗ | recall | LOW |
| 21 | Shah et al. (AAAI 2020) | claim correction | fact-guided sentence modification | ✓ | ✗ | ◐ | ✗ | ✗ | recall | LOW |
| 22 | ZeroFEC (Huang et al., ACL 2023) | claim correction | zero-shot FEC | ✓ | ✗ | ◐ | ✗ | ✗ | recall | LOW |
| 23 | FAVA (Mishra et al., COLM 2024) | claim correction | fine-grained hallucination edit | ✓ | ✗ | ✓ | ◐ | ✗ | recall | LOW |
| 24 | Chain-of-Verification (Dhuliawala et al., 2024) | claim correction | per-claim verify then revise | ✓ | ✗ | ◐ | ✗ | ✗ | recall | LOW (method ancestor) |
| 25 | CRITIC (Gou et al., ICLR 2024) | evidence revision | tool-based critique | ✓ | ✗ | ✗ | ✗ | ◐ | recall | LOW |
| 26 | Self-Refine (Madaan et al., NeurIPS 2023) | revision | iterative self-feedback | ◐ | ✗ | ✗ | ✗ | ✗ | recall | LOW (baseline) |
| 27 | Wadhwa et al. (Findings EMNLP 2024) | claim correction | detect–critique–refine | ✓ | ✗ | ◐ | ✗ | ✗ | recall | LOW |
| 28 | MEDEC (Ben Abacha et al., Findings ACL 2025) | medical correction | single-error clinical note correction | ✓ | ✗ | ◐ | ✗ | ✗ | web | MED |
| 29 | CorBenchX (Zou et al., 2025) | medical correction | CXR report error detect/correct | ✓ | ✗ | ✗ | ✗ | ✗ | web | MED |
| 30 | ReXErr (Rao et al., PSB 2025) | medical correction | CXR error injection | ✓ | ✗ | ✗ | ✗ | ✗ | web | LOW |
| 31 | RaDialog (Pellegrini et al., MIDL 2025) | medical interactive | report correction from instructions | ✓ | ✗ | ✗ | ✗ | ✗ | recall | MED |
| 32 | IteraTeR / CoEdIT / EditEval | minimal revision | instruction editing | ◐ | ✗ | ✓ | ✗ | ✗ | recall | LOW |
| 33 | ARIES (D'Arcy et al., ACL 2024) | minimal revision | edits in response to reviews | ✓ | ◐ | ◐ | ✗ | ◐ | recall | LOW |
| 34 | Minimal-edit GEC over-correction (2025–26) | minimal revision | over-correction | ◐ | ✗ | ✓ | ✗ | ✗ | web | LOW |
| 35 | Sharma et al. (ICLR 2024) sycophancy | feedback verification | capitulation to user | ✗ | ✗ | ◐ | ✗ | ✓ | recall | LOW |
| 36 | FlipFlop (Laban et al., 2023) | feedback verification | answer flips under challenge | ✗ | ✗ | ◐ | ✗ | ✓ | recall | LOW |
| 37 | SycEval (Fanous et al., 2025) | feedback verification | progressive vs. regressive sycophancy (med) | ◐ | ✗ | ◐ | ✗ | ✓ | web | MED |
| 38 | PBT (Stengel-Eskin et al., NAACL 2025) | feedback verification | accept good / resist bad persuasion | ✓ | ✗ | ✓ | ✗ | ✓ | web | MED |
| 39 | Med-Stress (Xiao et al., ACL 2026) | feedback verification | clinical belief stability | ✗ | ✗ | ✓ | ✗ | ✓ | web | MED |
| 40 | MedPRESS (2026) | feedback verification | multi-turn patient pressure | ✗ | ✗ | ✓ | ✗ | ✓ | web | LOW |
| 41 | ClashEval (Wu et al., NeurIPS D&B 2024) | knowledge conflict | adoption of wrong retrieved evidence | ✓ | ✗ | ◐ | ✗ | ✓ | recall | MED |
| 42 | Xie et al. (ICLR 2024) knowledge conflicts | knowledge conflict | receptiveness to conflicting evidence | ◐ | ✗ | ✗ | ✗ | ✓ | recall | LOW |
| 43 | Huang et al. (ICLR 2024) / Kamoi et al. (TACL 2024) | self-correction | limits of self-correction | ◐ | ✗ | ◐ | ✗ | ◐ | recall | LOW |
| 44 | MINT (Wang et al., ICLR 2024) | multi-turn feedback | tool + NL feedback | ◐ | ✗ | ✗ | ✗ | ◐ | recall | LOW |
| 45 | BeliefBank (Kassner et al., EMNLP 2021) | belief revision | consistency via constraints | ✓ | ✓ | ◐ | ✗ | ◐ | recall | LOW |
| 46 | Hase et al. (EACL 2023) belief graphs | belief revision | update + spread to related beliefs | ✓ | ✓ | ✓ | ✗ | ✗ | recall | LOW |
| 47 | Belief-R (Wilie et al., EMNLP 2024) | belief revision | update vs. maintain under new premises | ✓ | ◐ | ✓ | ✗ | ✗ | web | MED |
| 48 | ReviseQA (Helwe et al., ICML-WS 2025) | belief revision | multi-turn logical revision | ✓ | ✓ | ◐ | ✗ | ✗ | web | LOW |
| 49 | AGM 1985; Katsuno–Mendelzon 1991; TMS (Doyle 1979, de Kleer 1986) | theory | minimal change; revision vs. update; dependency retraction | ✓ | ✓ | ✓ | ◐ | ✗ | recall | — (foundation) |
| 50 | AbstentionBench (Kirichenko et al., 2025); Wen et al. survey (TACL 2025) | abstention | when to abstain | ✗ | ✗ | ✗ | ✓ | ◐ | web | LOW |
| 51 | Evidence-Sufficiency benchmark (2026) | abstention | 5-level evidence sufficiency in RAG | ✗ | ✗ | ✗ | ✓ | ◐ | web | LOW |
| 52 | Woodpecker (Yin et al., 2023) / LURE (Zhou et al., ICLR 2024) / Volcano (Lee et al., NAACL 2024) | VLM revision (COCO) | post-hoc hallucination correction | ✓ | ✗ | ◐ | ✗ | ✗ | recall | LOW |
| 53 | CHAIR (Rohrbach et al., 2018) / POPE (Li et al., 2023) / FaithScore (Jing et al., 2024) | VLM eval (COCO) | object / atomic-fact hallucination | ✗ | ✗ | ✗ | ✗ | ✗ | recall | — (metric) |
| 54 | FActScore / SAFE / VeriScore | claim decomposition | atomic-fact support | ✗ | ✗ | ✗ | ◐ | ✗ | recall | — (infrastructure) |
| 55 | RadGraph (Jain et al., 2021) / RadFact (Bannur et al., 2024) / GREEN (2024) | CXR infrastructure | entities/relations; entailment metrics | ✗ | ◐ | ✗ | ✗ | ✗ | web | — (infrastructure) |

**No row has ✓ in all five columns, and no row has ✓ in both Propagated and Unreliable FB.** Unresolved ✓ occurs only in abstention work, which has no revision.

## 11. Next to Paper 2 (start a list now; review in May 2027)

- **Memory from feedback:** MemPrompt (Madaan et al., EMNLP 2022); TeachMe (Mishra et al., Findings EMNLP 2022); SERAC/GRACE/WISE as memory-based editors; MemoryBank, MemGPT.
- **Contamination / poisoning:** AgentPoison (Chen et al., NeurIPS 2024); PoisonedRAG (Zou et al., USENIX Security 2025); memory-injection attacks (2025).
- **Continual editing:** WISE, AlphaEdit, and *Model editing at scale* (Gupta et al. 2024) as lifelong baselines; MQuAKE-T for temporal supersession.
- **Rollback:** versioned memory and retraction, which ties back to TMS/ATMS. No LLM benchmark for rollback is known yet. Check this in the Paper 2 novelty review.

## 12. Reading order before the 31 Oct novelty review

1. EditPropBench (full). Copy its metric suite (ERA, LES, CDR) where compatible, so reviewers can compare.
2. RevPropBench (full). Note the over-edit / miss / wrong-value decomposition.
3. PBT (Stengel-Eskin et al.) and SycEval: how they define "positive" vs. "negative" persuasion.
4. RARR §preservation, and FRUIT's evaluation.
5. Belief-R / BREU, and Hase et al. 2024 *Fundamental Problems*, for the theory section.
6. MEDEC, CorBenchX, RaDialog, RadGraph `suggestive_of`: the domain grounding.
7. LEDGER: a candidate strong method baseline ("strong current correction baseline" in the thesis plan).

### Sources checked in this session
- [EditPropBench, arXiv 2605.02083](https://arxiv.org/abs/2605.02083v2) · [EditCoherenceBench dataset card](https://huggingface.co/datasets/EditCoherenceBench/EditCoherenceBench)
- [What Else Needs Fixing? / RevPropBench, arXiv 2609.03254](https://arxiv.org/abs/2609.03254)
- [LEDGER, Findings ACL 2026](https://aclanthology.org/2026.findings-acl.515/)
- [PropMEND, arXiv 2506.08920](https://arxiv.org/abs/2506.08920) · [ChainEdit, arXiv 2507.08427](https://arxiv.org/pdf/2507.08427)
- [LEME, NAACL 2024](https://aclanthology.org/2024.naacl-long.208/) · [DocMEdit, Findings ACL 2025](https://aclanthology.org/2025.findings-acl.1012/)
- [CorBenchX, arXiv 2505.12057](https://arxiv.org/abs/2505.12057) · [MEDEC, Findings ACL 2025](https://aclanthology.org/2025.findings-acl.1159/)
- [When Correct Beliefs Collapse, ACL 2026](https://aclanthology.org/2026.acl-long.395/) · [MedPRESS](https://arxiv.org/html/2608.02520)
- [PBT, NAACL 2025](https://aclanthology.org/2025.naacl-long.412/)
- [ReviseQA](https://openreview.net/pdf?id=Z4KBiAYXlI) · [Belief-R, EMNLP 2024](https://aclanthology.org/2024.emnlp-main.586.pdf)
- [RadGraph](https://physionet.org/content/radgraph/1.0.0/) · [PhysioNet: MIMIC data with LLMs and online services](https://physionet.org/news/post/llm-responsible-use/)
- [Evidence Sufficiency Benchmark (2026)](https://www.sciencedirect.com/org/science/article/pii/S1546221826007526)
