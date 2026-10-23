# Second annotator: how to run the agreement study

1. Send `annotation/medscope_annotate.html` to the annotator. Send nothing else: the key file and the data files contain the answers.
2. Suggested message (edit freely):

   > Hi! Could you help with my thesis by labelling 24 short clinical examples (about 1.5 hours, can be split over sessions)?
   > Open the attached file in Chrome or Safari and read the instructions box at the top. Your answers save automatically in that browser.
   > When you're done, press "Download CSV" at the bottom and send me the file. No medical background is needed beyond reading carefully.
   > Please don't look up the source dataset. Thank you!

3. Score the returned file against the gold labels, and against your own labels if you labelled the page too:
   ```bash
   python3 scripts/annotation_tools.py agree annotation/intexr_annotation_XX.csv --gold paperB/data/medec_scope_v0.json --key annotation/medscope_annotate_key.json
   python3 scripts/annotation_tools.py agree annotation/intexr_annotation_XX.csv annotation/intexr_annotation_YOU.csv --key annotation/medscope_annotate_key.json
   ```
   Report Cohen's kappa on the D/P/K/U labels, dependency-set agreement, and verdict kappa. Read the disagreements and the annotator's notes: they show where the guide is unclear.

The page is regenerated with `python3 scripts/make_annotation_html.py`. The fixed seed keeps the same 24 items, so every annotator sees the same items in the same order.
