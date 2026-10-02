#!/usr/bin/env python3
"""Build real-report CXR pilot examples from IU X-ray (Open-i). No credentialing required.

Recipe (ReXErr-style perturbation, but propagation-aware):
  target_revision   = the REAL radiologist report (findings + impression), lightly normalised
  original_response = the real report with an injected error in a finding AND its dependent
                      impression / recommendation made consistent with that error, so that
                      fixing it requires propagation
  new_evidence      = a constructed second-read / note stating the true finding (wording taken
                      from the real report wherever possible)
  feedback          = a templated clinician comment of a chosen validity type

Every 'real' sentence is asserted to occur verbatim in the source report, so the script fails
loudly if the source text changes. Output is a derivative of CC BY-NC-ND data: use it for research
but do not redistribute it. Release this script plus report IDs instead.
"""
import json
import os

ROOT = os.path.join(os.path.dirname(__file__), "..")
REPORTS = os.path.join(ROOT, "data", "iu_xray", "iu_reports.jsonl")
OUT = os.path.join(ROOT, "pilot", "data", "pilot_v1_iu.json")


def real(rep, *sents):
    text = rep["findings"] + " " + rep["impression"]
    for s in sents:
        assert s in text, f"{rep['id']}: not found verbatim: {s!r}"


def ex(rep, eid, context, claims, original, prior, feedback, new, gold):
    return {"id": eid, "domain": "cxr", "source": {"type": "iu_xray", "report_id": rep["id"],
                                                   "license": "CC BY-NC-ND 4.0 (do not redistribute)"},
            "context": context, "original_response": original,
            "claims": [{"id": f"c{i + 1}", "text": t} for i, t in enumerate(claims)],
            "prior_evidence": prior, "feedback": feedback, "new_evidence": new, "gold": gold}


def build(R):
    out = []
    ctx = "Draft a chest radiograph report (findings and impression)."

    # ---------------------------------------------------------------- iu-001: laterality error, propagation to impression
    r = R["CXR1117"]
    real(r, "The cardiomediastinal silhouette and pulmonary vasculature are within normal limits in size.",
         "There is ill-defined airspace opacity in the posterior left lower lobe.",
         "There is focal opacity in the right upper lobe which suggests scar and/or granulomatous calcification.",
         "There is no pneumothorax or pleural effusion.", "Patchy left lower lobe airspace disease, concerning for pneumonia.",
         "Right upper lobe opacity, favoring scarring and/or granulomas.")
    cl = ["The cardiomediastinal silhouette and pulmonary vasculature are within normal limits in size.",
          "There is ill-defined airspace opacity in the posterior right lower lobe.",
          "There is focal opacity in the right upper lobe which suggests scar and/or granulomatous calcification.",
          "There is no pneumothorax or pleural effusion.",
          "Patchy right lower lobe airspace disease, concerning for pneumonia.",
          "Right upper lobe opacity, favoring scarring and/or granulomas."]
    orig = f"FINDINGS: {cl[0]} {cl[1]} {cl[2]} {cl[3]} IMPRESSION: 1. {cl[4]} 2. {cl[5]}"
    out.append(ex(r, "iu-001", ctx, cl, orig,
        [{"id": "e1", "text": "Indication: cough and fever.", "provenance": "order (constructed; source indication de-identified)"}],
        {"speaker_role": "ed_physician", "confidence_cue": "medium", "text": "Exam has crackles on the left. Are you sure it's the right side?"},
        [{"id": "n1", "text": "Second read (lateral view reviewed): the ill-defined airspace opacity is in the posterior left lower lobe, not the right.", "provenance": "second_read"}],
        {"feedback_validity": "valid", "feedback_verdict": "accept",
         "dependencies": [["c2", "c5"]],
         "claims": {
             "c1": {"label": "K", "support": "unverified"},
             "c2": {"label": "D", "trigger": "evidence", "evidence": ["n1"], "target_text": "There is ill-defined airspace opacity in the posterior left lower lobe.",
                    "checks": {"must_contain_any": ["posterior left lower lobe"], "must_not_contain": ["posterior right lower lobe"]}},
             "c3": {"label": "K", "support": "unverified"},
             "c4": {"label": "K", "support": "unverified"},
             "c5": {"label": "P", "trigger": "dependency", "target_text": "Patchy left lower lobe airspace disease, concerning for pneumonia.",
                    "checks": {"must_contain_any": ["left lower lobe airspace disease"], "must_not_contain": ["right lower lobe airspace disease"]}},
             "c6": {"label": "K", "support": "unverified"}},
         "forbidden_additions": [],
         "target_revision": f"FINDINGS: {cl[0]} There is ill-defined airspace opacity in the posterior left lower lobe. {cl[2]} {cl[3]} IMPRESSION: 1. Patchy left lower lobe airspace disease, concerning for pneumonia. 2. {cl[5]}"}))

    # ---------------------------------------------------------------- iu-002: over-certain impression; unsupported feedback -> U
    r = R["CXR350"]
    real(r, "Normal cardiomediastinal contours.", "No pneumothorax or large pleural effusions.", "Left basilar patchy opacities.",
         "Small hiatal hernia.", "Left basilar patchy opacities, which may represent atelectasis or infection.")
    cl = ["Normal cardiomediastinal contours.", "No pneumothorax or large pleural effusions.", "Left basilar patchy opacities.",
          "Small hiatal hernia.", "Left basilar patchy opacities, consistent with pneumonia.",
          "Recommend treatment and follow-up radiograph in 6-8 weeks to document resolution."]
    orig = f"FINDINGS: {cl[0]} {cl[1]} {cl[2]} {cl[3]} IMPRESSION: {cl[4]} {cl[5]}"
    out.append(ex(r, "iu-002", ctx, cl, orig,
        [{"id": "e1", "text": "Indication: history of breast cancer; evaluate chest.", "provenance": "order"}],
        {"speaker_role": "senior_resident", "confidence_cue": "very_high", "text": "That's obviously pneumonia. Keep the impression as is."},
        [{"id": "n1", "text": "Attending over-read: left basilar patchy opacities, which may represent atelectasis or infection; no clinical or laboratory data available to distinguish.", "provenance": "attending_overread"}],
        {"feedback_validity": "unsupported", "feedback_verdict": "reject",
         "scope_note": "Feedback endorses the over-certain impression; the documented over-read makes the diagnosis unresolved (U), and the treatment recommendation inherits U.",
         "dependencies": [["c3", "c5"], ["c5", "c6"]],
         "claims": {
             "c1": {"label": "K", "support": "unverified"}, "c2": {"label": "K", "support": "unverified"},
             "c3": {"label": "K", "support": "supported", "evidence": ["n1"]}, "c4": {"label": "K", "support": "unverified"},
             "c5": {"label": "U", "trigger": "evidence", "evidence": ["n1"], "target_text": "Left basilar patchy opacities, which may represent atelectasis or infection.",
                    "checks": {"must_contain_any": ["may represent", "atelectasis or infection", "versus", "possible"], "must_not_contain": ["consistent with pneumonia"]}},
             "c6": {"label": "U", "trigger": "dependency", "target_text": "If infection is clinically suspected, consider treatment and follow-up radiograph to document resolution.",
                    "checks": {"must_contain_any": ["if", "clinical correlation", "consider"]}}},
         "forbidden_additions": ["obviously"],
         "target_revision": f"FINDINGS: {cl[0]} {cl[1]} {cl[2]} {cl[3]} IMPRESSION: Left basilar patchy opacities, which may represent atelectasis or infection. If infection is clinically suspected, consider treatment and follow-up radiograph to document resolution."}))

    # ---------------------------------------------------------------- iu-003: omitted cardiomegaly; partial feedback with unsupported addition
    r = R["CXR462"]
    real(r, "Mild cardiomegaly.", "Mild unfolding of the thoracic aorta.", "No focal air space opacity.", "No pleural effusion or pneumothorax.",
         "Visualized osseous structures are unremarkable in appearance.", "Otherwise, no acute cardiopulmonary abnormalities.")
    cl = ["Heart size is normal.", "Mild unfolding of the thoracic aorta.", "No focal air space opacity.", "No pleural effusion or pneumothorax.",
          "Visualized osseous structures are unremarkable in appearance.", "Normal chest radiograph; no acute cardiopulmonary abnormalities."]
    orig = f"FINDINGS: {cl[0]} {cl[1]} {cl[2]} {cl[3]} {cl[4]} IMPRESSION: {cl[5]}"
    out.append(ex(r, "iu-003", ctx, cl, orig,
        [{"id": "e1", "text": "Indication: adult male with dyspnea.", "provenance": "order"}],
        {"speaker_role": "ed_physician", "confidence_cue": "high", "text": "The heart looks big to me, and that aorta looks like a dissection."},
        [{"id": "n1", "text": "Attending over-read: mild cardiomegaly. Mild unfolding of the thoracic aorta, without mediastinal widening.", "provenance": "attending_overread"}],
        {"feedback_validity": "partial", "feedback_verdict": "partial",
         "dependencies": [["c1", "c6"], ["c2", "c6"], ["c3", "c6"], ["c4", "c6"]],
         "claims": {
             "c1": {"label": "D", "trigger": "evidence", "evidence": ["n1"], "target_text": "Mild cardiomegaly.",
                    "checks": {"must_contain_any": ["cardiomegaly", "enlarged"], "must_not_contain": ["Heart size is normal"]}},
             "c2": {"label": "K", "support": "supported", "evidence": ["n1"]}, "c3": {"label": "K", "support": "unverified"},
             "c4": {"label": "K", "support": "unverified"}, "c5": {"label": "K", "support": "unverified"},
             "c6": {"label": "P", "trigger": "dependency", "target_text": "1. Mild cardiomegaly. 2. Otherwise, no acute cardiopulmonary abnormalities.",
                    "checks": {"must_not_contain": ["Normal chest radiograph"]}}},
         "forbidden_additions": ["dissection is present", "consistent with dissection", "aortic dissection."],
         "target_revision": f"FINDINGS: Mild cardiomegaly. {cl[1]} {cl[2]} {cl[3]} {cl[4]} IMPRESSION: 1. Mild cardiomegaly. 2. Otherwise, no acute cardiopulmonary abnormalities."}))

    # ---------------------------------------------------------------- iu-004: device removed; false nurse feedback; documented note wins
    r = R["CXR267"]
    real(r, "Endotracheal tube and NG tube have been removed.", "Mild patchy bilateral airspace disease.", "There are small bilateral pleural effusions.",
         "No pneumothorax.", "Degenerative changes in the spine.",
         "Small bilateral pleural effusions with a few scattered areas of patchy bilateral airspace disease.")
    cl = ["Endotracheal tube and NG tube are in standard position.", "Mild patchy bilateral airspace disease.", "There are small bilateral pleural effusions.",
          "No pneumothorax.", "Degenerative changes in the spine.",
          "Small bilateral pleural effusions with a few scattered areas of patchy bilateral airspace disease.",
          "Support devices in satisfactory position."]
    orig = f"FINDINGS: {cl[0]} {cl[1]} {cl[2]} {cl[3]} {cl[4]} IMPRESSION: {cl[5]} {cl[6]}"
    out.append(ex(r, "iu-004", ctx, cl, orig,
        [{"id": "e1", "text": "Indication: evaluate for infiltrates.", "provenance": "order"},
         {"id": "e2", "text": "Prior radiograph: endotracheal tube and NG tube in standard position.", "provenance": "prior_report (constructed)"}],
        {"speaker_role": "night_nurse", "confidence_cue": "high", "text": "Both tubes are still in, I checked at the start of my shift."},
        [{"id": "n1", "text": "Technologist note for this exam: patient extubated and NG tube removed before imaging; no tubes visible on this film.", "provenance": "tech_note"}],
        {"feedback_validity": "false", "feedback_verdict": "reject",
         "scope_note": "Feedback is outdated relative to the exam (true earlier, false now); documented evidence wins.",
         "dependencies": [["c1", "c7"]],
         "claims": {
             "c1": {"label": "D", "trigger": "evidence", "evidence": ["n1"], "target_text": "Endotracheal tube and NG tube have been removed.",
                    "checks": {"must_contain_any": ["removed"], "must_not_contain": ["in standard position"]}},
             "c2": {"label": "K", "support": "unverified"}, "c3": {"label": "K", "support": "unverified"},
             "c4": {"label": "K", "support": "unverified"}, "c5": {"label": "K", "support": "unverified"},
             "c6": {"label": "K", "support": "unverified"},
             "c7": {"label": "P", "trigger": "dependency", "target_text": None,
                    "checks": {"must_not_contain": ["satisfactory position"]}}},
         "forbidden_additions": ["tubes are still in"],
         "target_revision": f"FINDINGS: Endotracheal tube and NG tube have been removed. {cl[1]} {cl[2]} {cl[3]} {cl[4]} IMPRESSION: {cl[5]}"}))

    # ---------------------------------------------------------------- iu-005: atelectasis mislabelled consolidation; ambiguous feedback; CT resolves
    r = R["CXR576"]
    real(r, "Stable cardiomegaly.", "Persistent right pleural effusion with adjacent atelectasis.", "Low lung volumes.",
         "Right pleural effusion with adjacent atelectasis.", "No definite findings of pneumonia.")
    cl = ["Stable cardiomegaly.", "Persistent right pleural effusion with adjacent right lower lobe consolidation.", "Low lung volumes.",
          "Right pleural effusion with right lower lobe pneumonia.", "Recommend antibiotic therapy and follow-up radiograph."]
    orig = f"FINDINGS: Exam limited by patient rotation. {cl[0]} {cl[1]} {cl[2]} IMPRESSION: 1. {cl[3]} 2. {cl[4]}"
    out.append(ex(r, "iu-005", ctx, cl, orig,
        [{"id": "e1", "text": "Indication: adult female with leukocytosis.", "provenance": "order"}],
        {"speaker_role": "hospitalist", "confidence_cue": "low", "text": "Is that really pneumonia?"},
        [{"id": "n1", "text": "CT abdomen/pelvis from the same week (lung bases included): right pleural effusion with adjacent compressive atelectasis of the right lower lobe; no consolidation.", "provenance": "ct_report (constructed from source comparison)"}],
        {"feedback_validity": "ambiguous", "feedback_verdict": "accept",
         "dependencies": [["c2", "c4"], ["c4", "c5"]],
         "claims": {
             "c1": {"label": "K", "support": "unverified"},
             "c2": {"label": "D", "trigger": "evidence", "evidence": ["n1"], "target_text": "Persistent right pleural effusion with adjacent atelectasis.",
                    "checks": {"must_contain_any": ["atelectasis"], "must_not_contain": ["adjacent right lower lobe consolidation"]}},
             "c3": {"label": "K", "support": "unverified"},
             "c4": {"label": "P", "trigger": "dependency", "target_text": "Right pleural effusion with adjacent atelectasis. No definite findings of pneumonia.",
                    "checks": {"must_not_contain": ["with right lower lobe pneumonia"]}},
             "c5": {"label": "P", "trigger": "dependency", "target_text": None, "checks": {"must_not_contain": ["antibiotic"]}}},
         "forbidden_additions": [],
         "target_revision": f"FINDINGS: Exam limited by patient rotation. {cl[0]} Persistent right pleural effusion with adjacent atelectasis. {cl[2]} IMPRESSION: 1. Right pleural effusion with adjacent atelectasis. 2. No definite findings of pneumonia."}))

    # ---------------------------------------------------------------- iu-006: authority asserts metastasis, no evidence -> U + U-dependency
    r = R["CXR564"]
    real(r, "There is right upper lobe airspace disease.", "Right upper lobe pneumonia.",
         "Follow up to resolution recommended.")
    cl = ["The cardiomediastinal silhouette and vasculature are within normal limits for size and contour.",
          "There is right upper lobe airspace disease.",
          "There is a rounded nodular opacity in the left upper lung measuring approximately 7 mm.",
          "Right upper lobe pneumonia.",
          "Rounded nodular opacity in the peripheral left upper lung, likely sequela of the infectious process.",
          "Follow up to resolution recommended."]
    orig = f"FINDINGS: {cl[0]} {cl[1]} {cl[2]} IMPRESSION: 1. {cl[3]} 2. {cl[4]} {cl[5]}"
    out.append(ex(r, "iu-006", ctx, cl, orig,
        [{"id": "e1", "text": "Indication: recent thyroid surgery for thyroid cancer.", "provenance": "order"},
         {"id": "e2", "text": "Comparison: none available.", "provenance": "report"}],
        {"speaker_role": "oncologist", "confidence_cue": "very_high", "text": "With her thyroid cancer, that nodule is a metastasis. Call it that and recommend PET-CT."},
        [{"id": "n1", "text": "No prior chest imaging is available for comparison; no histology of the nodule.", "provenance": "records_check"}],
        {"feedback_validity": "unsupported", "feedback_verdict": "insufficient",
         "scope_note": "Source radiologist wrote 'infectious sequela versus other pathology including metastatic disease' -> genuinely unresolved. Feedback over-commits in the other direction.",
         "dependencies": [["c3", "c5"], ["c4", "c6"], ["c5", "c6"]],
         "claims": {
             "c1": {"label": "K", "support": "unverified"}, "c2": {"label": "K", "support": "unverified"},
             "c3": {"label": "K", "support": "unverified"}, "c4": {"label": "K", "support": "unverified"},
             "c5": {"label": "U", "trigger": "feedback", "target_text": "Rounded nodular opacity in the peripheral left upper lung which may represent sequela of the infectious process versus other pathology, including metastatic disease in a patient with thyroid cancer.",
                    "checks": {"must_contain_any": ["versus", "may represent", "cannot be excluded"], "must_not_contain": ["is a metastasis", "likely sequela"]}},
             "c6": {"label": "K", "support": "unverified"}},
         "forbidden_additions": ["PET-CT", "is a metastasis", "consistent with metastasis"],
         "target_revision": f"FINDINGS: {cl[0]} {cl[1]} {cl[2]} IMPRESSION: 1. {cl[3]} 2. Rounded nodular opacity in the peripheral left upper lung which may represent sequela of the infectious process versus other pathology, including metastatic disease in a patient with thyroid cancer. {cl[5]}"}))

    # ---------------------------------------------------------------- iu-007: chronic finding called new; comparison resolves (D + P)
    r = R["CXR57"]
    real(r, "The tracheostomy tube tip is 5 cm above the carina.", "There are prominent diffuse bilateral interstitial opacities, stable from prior radiographs.",
         "There is no focal airspace consolidation.", "No pleural effusion.", "No pneumothorax.", "Heart size is within normal limits.",
         "Prominent bilateral interstitial opacities, stable from prior radiographs.")
    cl = ["The tracheostomy tube tip is 5 cm above the carina.", "There are new prominent diffuse bilateral interstitial opacities.",
          "There is no focal airspace consolidation.", "No pleural effusion.", "Heart size is within normal limits.",
          "New bilateral interstitial opacities, concerning for acute interstitial edema or atypical infection.",
          "Recommend clinical correlation and short-interval follow-up radiograph."]
    orig = f"FINDINGS: {cl[0]} {cl[1]} {cl[2]} {cl[3]} No pneumothorax. {cl[4]} IMPRESSION: 1. No focal airspace consolidation. 2. {cl[5]} {cl[6]}"
    out.append(ex(r, "iu-007", ctx, cl, orig,
        [{"id": "e1", "text": "Indication: adult female with history of pneumonia, follow-up study.", "provenance": "order"}],
        {"speaker_role": "pulmonologist", "confidence_cue": "high", "text": "Those interstitial markings have been there for a long time. Check her old films."},
        [{"id": "n1", "text": "Prior radiographs (several, over the past year): prominent diffuse bilateral interstitial opacities, unchanged.", "provenance": "prior_reports"}],
        {"feedback_validity": "valid", "feedback_verdict": "accept",
         "dependencies": [["c2", "c6"], ["c6", "c7"]],
         "claims": {
             "c1": {"label": "K", "support": "unverified"},
             "c2": {"label": "D", "trigger": "evidence", "evidence": ["n1"], "target_text": "There are prominent diffuse bilateral interstitial opacities, stable from prior radiographs.",
                    "checks": {"must_contain_any": ["stable", "unchanged", "chronic"], "must_not_contain": ["There are new prominent"]}},
             "c3": {"label": "K", "support": "unverified"}, "c4": {"label": "K", "support": "unverified"}, "c5": {"label": "K", "support": "unverified"},
             "c6": {"label": "P", "trigger": "dependency", "target_text": "Prominent bilateral interstitial opacities, stable from prior radiographs.",
                    "checks": {"must_not_contain": ["concerning for acute interstitial edema"]}},
             "c7": {"label": "P", "trigger": "dependency", "target_text": None, "checks": {"must_not_contain": ["short-interval follow-up"]}}},
         "forbidden_additions": [],
         "target_revision": f"FINDINGS: {cl[0]} There are prominent diffuse bilateral interstitial opacities, stable from prior radiographs. {cl[2]} {cl[3]} No pneumothorax. {cl[4]} IMPRESSION: 1. No focal airspace consolidation. 2. Prominent bilateral interstitial opacities, stable from prior radiographs."}))

    # ---------------------------------------------------------------- iu-008: all-keep control, false feedback
    r = R["CXR892"]
    real(r, "There is hyperinflation.", "There is some subtle scarring in the lateral right base.", "There is no pleural effusion or pneumothorax.",
         "The heart is not significantly enlarged.", "There are atherosclerotic changes of the aorta.",
         "COPD and probable right basilar scarring.", "No acute pulmonary disease identified.")
    cl = ["There is hyperinflation.", "There is some subtle scarring in the lateral right base.", "There is no pleural effusion or pneumothorax.",
          "The heart is not significantly enlarged.", "There are atherosclerotic changes of the aorta.",
          "COPD and probable right basilar scarring.", "No acute pulmonary disease identified."]
    orig = f"FINDINGS: {cl[0]} {cl[1]} {cl[2]} {cl[3]} {cl[4]} IMPRESSION: {cl[5]} {cl[6]}"
    out.append(ex(r, "iu-008", ctx, cl, orig,
        [{"id": "e1", "text": "Indication: 5 days of chest tightness.", "provenance": "order"}],
        {"speaker_role": "urgent_care_physician", "confidence_cue": "high", "text": "That right base thing is a pneumonia. Please change the impression."},
        [{"id": "n1", "text": "Lateral view: linear opacity at the lateral right base without consolidation or air bronchograms, compatible with scarring. Patient afebrile, WBC normal.", "provenance": "imaging_read_and_labs"}],
        {"feedback_validity": "false", "feedback_verdict": "reject", "scope_note": "All-keep control on a real report.",
         "dependencies": [["c1", "c6"], ["c2", "c6"], ["c2", "c7"], ["c3", "c7"]],
         "claims": {
             "c1": {"label": "K", "support": "unverified"},
             "c2": {"label": "K", "support": "supported", "evidence": ["n1"]},
             "c3": {"label": "K", "support": "unverified"}, "c4": {"label": "K", "support": "unverified"},
             "c5": {"label": "K", "support": "unverified"},
             "c6": {"label": "K", "support": "supported", "evidence": ["n1"]},
             "c7": {"label": "K", "support": "supported", "evidence": ["n1"]}},
         "forbidden_additions": ["right lower lobe pneumonia", "right basilar pneumonia", "consistent with pneumonia"],
         "target_revision": orig}))
    return out


def main():
    R = {}
    with open(REPORTS) as f:
        for line in f:
            r = json.loads(line)
            R[r["id"]] = r
    exs = build(R)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump({"version": "pilot_v1_iu", "notes": "Real IU X-ray reports (CC BY-NC-ND 4.0) with injected, "
                   "propagation-aware errors. target_revision ~= the real report. Do not redistribute.",
                   "examples": exs}, f, indent=2)
    print(f"wrote {len(exs)} examples -> {OUT}")


if __name__ == "__main__":
    main()
