# External component-check sets (IntExR format)

Small samples converted by `scripts/convert_external.py` from public datasets. Each file keeps its source license.

| File | Source | License | Attribution |
|---|---|---|---|
| `medec_intexr.json` | MEDEC-MS validation+test | CC BY 4.0 | Ben Abacha et al., *MEDEC: A Benchmark for Medical Error Detection and Correction in Clinical Notes*, Findings of ACL 2025. https://github.com/abachaa/MEDEC |
| `vitaminc_intexr.json` | VitaminC dev (real revisions) | CC BY-SA 3.0 (this derivative is also CC BY-SA 3.0) | Schuster, Fisch & Barzilay, *Get Your Vitamin C!*, NAACL 2021. https://huggingface.co/datasets/tals/vitaminc |
| `editpropbench_intexr.json` | EditPropBench v1.0 cascade-v1-creative | CC BY 4.0 | Kruthof, *EditPropBench*, arXiv:2605.02083. https://huggingface.co/datasets/EditCoherenceBench/EditCoherenceBench |

Changes made: reformatted into the IntExR schema; added feedback-validity variants (valid/false) and constructed evidence items; EditPropBench protected units subsampled to ≤40 claims per item. Feedback text and "experiment log" evidence are ours.
