# Clinical review log

Each authored item is checked by a clinician before the protocol freeze. Cases judged wrong are fixed or dropped
without looking at any test result. Raw sheets are in `annotation/returned/`.

## Round 1: OB/GYN (Dr. Pradhan, MD), returned 23 Nov 2026

Packet: `annotation/review_packet_obgyn.pdf` (5 cases, all in the dev split). Sheet: `annotation/returned/clinical_review_pradhan_obgyn.xlsx`.

| Case | Error and correction right | Evidence settles it | Follow-on changes right | "Incorrect" feedback really incorrect | Unsupported suggestion inappropriate |
|---|---|---|---|---|---|
| 1 ms-val-514 (eclampsia: lorazepam → magnesium) | Y | Y | Y | Y | Y |
| 2 ms-val-30 (HELLP → cholestasis of pregnancy) | Y | **N** | Y | Y | Y |
| 3 ms-val-185 (Bartholin abscess: sitz baths → I&D) | Y | Y | Y | Y (+) | Y |
| 4 ms-val-333 (mastitis: TMP-SMX → dicloxacillin) | Y | **unclear** | **unclear** | Y | Y |
| 5 ms-val-520 (prolactinoma: levodopa → cabergoline) | Y | Y | **N** | Y | Y |

### Comments and what was done

| Case | Reviewer comment (paraphrased) | Action | Status |
|---|---|---|---|
| 1 | Not "RUQ pain" (not how a patient says it); "upper abdominal pain" | Claim c1 reworded. The MEDEC note itself is source text and is not edited. | done |
| 1 | c2: magnesium "for prevention of recurrent seizures", not "seizure control" | Target text of c2 reworded (check term "magnesium" unchanged) | done |
| 1 | Later event: keep the magnesium part; IV antihypertensives are rarely needed after delivery, so "treat elevated BP as necessary" | Superseding evidence no longer mentions IV antihypertensives; c4 now also changes to "Treat elevated blood pressure as needed." | done |
| 2 | c1: "mildly elevated bile acids" | c1 reworded | done |
| 2 | Add the interval of repeat labs; repeat labs should include bile acids and bilirubin | c3 target now "repeat bile acids and liver tests weekly" | done; **interval to confirm** |
| 2 | Feedback should be professional: "clinical presentation and evidence do not support a diagnosis of HELLP" | Valid feedback reworded | done |
| 2 | Evidence does not settle the question (N) | Proposed: new evidence reports repeat labs with an interval and includes bile acids and bilirubin | **asked reviewer** |
| 3 | Rephrase to "Sitz baths alone is inadequate treatment" | Applied to the correct (valid) feedback, which is the one about sitz baths | done; **which feedback to confirm** |
| 4 | Rephrase feedback 1: "TMP-SMX is the incorrect antibiotic to use for mastitis" | Valid feedback reworded | done |
| 4 | Evidence and follow-on changes unclear; "flow of this case is unclear" | None yet | **asked reviewer** |
| 5 | Visual fields are checked after the history and before labs and MRI | Plan reordered: "Check visual fields" now follows the history (claim ids unchanged) | done |

Effect on the data: 23 examples of these 5 cases changed (15 of the 60 dev-slice examples). Labels: one more D claim
(case 1, superseding: c4). The dataset validator and the pipeline unit tests pass. Dev runs must be repeated for the
changed examples before the freeze (everything else comes from the cache); the test split is untouched.

### Still to review
The remaining 149 cases are outside OB/GYN. They need reviewers for internal medicine, infectious disease, neurology,
pediatrics, emergency medicine and others (`annotation/review_packet_all.pdf`, `annotation/review_packet_v03_new.pdf`).
