# Next steps + message drafts (2 Oct 2026)

## A. What to do, in order

### Today / this weekend (Oct 2–4)
1. **Send the update to Defei** (draft B1) and the **email to Prof. Metaxas** (draft B2). Everything else depends on two things only they can give: the Paper 1 / Paper B split OK, and clinician reviewers.
2. **Get an API key.** Ask the lab first (B2 asks); otherwise get a personal Anthropic key. Then run the first real results, about 1 hour:
   ```bash
   export ANTHROPIC_API_KEY=...
   python3 scripts/run_pilot.py --data paperB/data/medec_scope_v0.json --systems no_revision oracle dialogue@anthropic:claude-sonnet-5-5 evidence_prompt@anthropic:claude-sonnet-5-5 scope_first@anthropic:claude-sonnet-5-5 --judge anthropic:claude-haiku-4-5-20251001 --conditions A B --out results/medscope_run1
   python3 scripts/run_pilot.py --data pilot/data/pilot_v1.json --systems no_revision oracle dialogue@anthropic:claude-sonnet-5-5 evidence_prompt@anthropic:claude-sonnet-5-5 scope_first@anthropic:claude-sonnet-5-5 --judge anthropic:claude-haiku-4-5-20251001 --conditions A B C D --out results/pilot_run1
   ```
3. **Read 10 MedScope cases yourself** in `results/medec_scope_review.md`, and mark anything that looks clinically off. You'll be asked about them.
4. Click through the **ReXGradient-160K** (Hugging Face) and **CheXpert Plus** (Stanford AIMI) agreements, and start the **PhysioNet/CITI** application in the background.

### Week of Oct 5–9
5. Send the **second-annotator ask** (draft B4) with `annotation/sheet_blank.csv` + `docs/04_annotation_guide.md`.
6. Once Metaxas replies, send the **clinician reviewer request** (draft B3) with the review sheet.
7. Read in full: EditPropBench, RevPropBench, PBT (lit review §12). Update their rows in the matrix.
8. With Claude: write MedScope batch 3, aimed at superseding and depth-2 cases, plus 10 radiology cases.

### Week of Oct 12–16
9. Compute κ (`scripts/annotation_tools.py agree`), list the disagreements, and revise the guide.
10. Run the second and third models (Azure OpenAI / open-weight). Write a one-page results note: is propagation harder than direct fixes? Is there a gap between verified edits (A) and unverified feedback (B)?

### Oct 19–31
11. Draft the novelty memo and meet Metaxas by **Oct 31**.

## B. Drafts. Edit before sending; nothing has been sent.

### B1. Update to Defei (Slack / email)
> Hi Defei, quick update on IntExR since our last check-in:
>
> **Done this week**
> - **Literature review:** 55 papers across evidence-based revision, edit propagation, model editing, sycophancy, belief revision, abstention, and radiology correction, with a coverage matrix. Closest prior work: EditPropBench (May 2026) and RevPropBench (EMNLP 2026 Industry). Both already label direct / cascade / protected edits, but both assume the edit is correct and have no "unresolved" case. So our novelty is the interaction of *unknown feedback validity* with *claim-level scope* (+ unresolved claims), not the D/P/K labels themselves.
> - **Task definition:** inputs/outputs, labels D/P/K/U with precedence rules, metrics, and four conditions. Condition A (verified edit, the EditPropBench setting) vs B (unverified feedback + evidence) directly tests the novelty claim.
> - **Pilot data:** 24 examples (real IU X-ray reports + real COCO captions + synthetic probes). Because MIMIC needs PhysioNet credentialing, I'm using IU X-ray (public) for now and applying for MIMIC in parallel.
> - **External checks:** converted MEDEC, VitaminC, and EditPropBench into our format, including false-feedback variants of EditPropBench.
> - **Harness:** 7 systems, 4 conditions, claim-level metrics with source-case bootstrap CIs. A validation tool found and fixed several converter bugs.
> - **Second paper (proposed):** a clinical dataset paper, *MedScope*. MEDEC notes (CC BY, redistributable) + AI-drafted assessment & plans with an expert-designed error *and* claims that depend on it, decisive evidence, and 7 feedback types. 31 cases / 188 examples so far, all LLM-proposed and **not yet clinically reviewed**. Plan: clinician review + harm ratings, submit before Paper 1 (CHIL 2027?) so Paper 1 can cite it.
>
> **Where I'd value your input**
> 1. Does the Paper 1 / MedScope split look clean enough to avoid an overlap problem?
> 2. Any clinicians you or the group could connect me with for a ~2-hour review?
> 3. Is there a lab API key or compute I can use? No model results exist yet; everything so far is validated with oracle and no-revision baselines.
>
> Repo (private): https://github.com/sonak11/intexr. Happy to walk you through it whenever works.

### B2. Email to Prof. Metaxas
> **Subject:** IntExR progress + three decisions (Paper 1 / dataset paper, clinicians, compute)
>
> Dear Prof. Metaxas,
>
> A short progress update and three items where I need your guidance.
>
> **Progress:**
> - I've completed a first literature review (55 papers, with a coverage matrix), a formal task definition for IntExR-Scope, a pilot dataset, and an evaluation harness.
> - Two 2026 benchmarks (EditPropBench, RevPropBench) already label direct, cascaded, and protected edits. However, both assume the requested edit is correct. IntExR-Scope's distinct contribution is the interaction between *unknown feedback validity* and *claim-level scope*, including unresolved claims.
> - The pilot includes a verified-edit vs. unverified-feedback comparison that tests this directly.
>
> **Decisions I'd like your input on:**
> 1. **A separate clinical dataset paper.** I'd like to build *MedScope*: a clinician-reviewed dataset of AI-drafted clinical assessments with expert-designed errors, dependent claims, decisive evidence, and feedback of varying validity, plus clinician harm ratings. It builds on MEDEC (CC BY 4.0). It would be submitted *before* Paper 1 (possibly CHIL 2027), and Paper 1 would cite it and focus on the cross-domain task and the scope-first method. Does this split work for you, or would you prefer to keep everything in Paper 1?
> 2. **Clinical reviewers.** The 188 MedScope examples (31 cases) are LLM-proposed and need clinician review, about 2–3 hours for the first 31 cases. Could you suggest anyone in your network or at the medical school?
> 3. **Compute / API access.** Does the lab have an API account (ideally Anthropic or Azure OpenAI, which PhysioNet permits for MIMIC data) that I could use? The first runs cost under $20.
>
> **Data note:** MIMIC-CXR requires PhysioNet credentialing, which I've started. Meanwhile I'm using the public IU X-ray collection and MEDEC, so work isn't blocked.
>
> I'm on track for the October 31 novelty review. Would a 20-minute meeting next week work to discuss the dataset paper?
>
> Best,
> Sonakshi

### B3. Clinician reviewer request (send after Metaxas OKs / introduces)
> **Subject:** Request: ~2 hours of clinical review for a research dataset on AI clinical-note revision
>
> Dear Dr. [Name],
>
> [Prof. Metaxas suggested I reach out.] I'm a senior at [university] building a research dataset on how AI systems should revise clinical assessments when they receive feedback. The question is when to accept a correction, when to reject it, and how a fix should carry through to dependent parts of the plan.
>
> Each case is a short clinical vignette (from the public MEDEC benchmark) with an AI-drafted assessment and plan that contains one error, a piece of new evidence (a test result or guideline statement), and several versions of feedback. I'd like a clinician to check that:
> - (a) the error is a real error;
> - (b) the follow-on plan items really depend on it;
> - (c) the corrected versions and evidence are clinically sound;
> - (d) each failure is rated for clinical severity (none / minor / moderate / severe).
>
> The first round is 31 cases, about 2–3 hours, done in a review sheet at your own pace. No patient data is involved; all cases are educational vignettes. You'd be acknowledged in the paper, or offered co-authorship for substantial involvement, as you prefer.
>
> Would you be open to this? I'm happy to send two sample cases first so you can judge the effort.
>
> Best regards,
> Sonakshi Sharma

### B4. Second-annotator ask (labmate)
> Hi [Name], could I ask a favor? I need a second annotator for my thesis pilot to measure agreement. It's about 1 hour: 16 short examples, labelling each claim as Direct / Propagated / Keep / Unresolved using a 1-page guide. Please do it independently, without discussing it with me first. Files: the annotation sheet + guide (attached). Happy to return the favor or buy you coffee. Is sometime in the next week possible?

## C. Things only you can do (Claude can't)
- Send the messages above. They are drafts; check names, your university, and the tone.
- Get credentials: API key, PhysioNet/CITI, ReXGradient/CheXpert agreements.
- Confirm the CHIL 2027 deadline (CHIL 2026's was Feb 4, 2026).
- Review a sample of MedScope cases yourself before a clinician sees them.
