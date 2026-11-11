# Knowledge Graphs, Language Models, and Semantic Methods for Atrial Fibrillation Analysis: Systematic Review

Zhaohui Liang, PhD; Niccolo Marini, PhD; Sivaramakrishnan Rajaraman, PhD; Matthew Song; Zhiyun Xue, PhD; Sameer Antani, PhD

All authors: Division of Intramural Research, National Library of Medicine, National Institutes of Health, Bethesda, Maryland, USA. Corresponding author: Sameer Antani.

Reproducibility package for the revised 13-report review, aligned with the concise manuscript dated November 10, 2026. Prepared November 11, 2026. This replaces the older 15-report figure workflow, not the underlying published study data.

Repository: https://github.com/StanleyLiangYork/ECG-AI-for-AF
The earlier figure workflow remains available in Git history at commit `b8f7a314c44a55e2a0010405f35b674189e643d1`. Use the current scripts and CSVs together; do not mix them with historical inputs.

## Abstract

Background: Knowledge graphs and language models are being investigated for atrial fibrillation (AF) analysis, but performance on electrocardiogram (ECG) benchmarks does not establish their usefulness in clinical decisions.

Objective: We aimed to synthesize AF-specific evidence for knowledge-graph, language-model, and related semantic approaches, distinguishing detection in recordings, identification of documented AF, future-event prediction, and clinical benefit.

Methods: We searched PubMed, Web of Science, IEEE Xplore, and the Cochrane Library on August 2, 2026, for English-language publications dated January 1, 2018, through June 30, 2026. Eligible primary studies addressed adults aged ≥18 years and reported separate quantitative AF results. After registration, initial screening, and synthesis, we developed an operational eligibility definition that explicitly included qualifying waveform-token methods. After initial single-reviewer screening, two reviewers independently assessed potentially eligible full texts and extracted study data. QUADAS-3 and PROBAST+AI informed risk-of-bias and applicability assessment; GRADE informed outcome-level certainty assessment. Results were synthesized by clinical target, analysis unit, and validation setting. Heterogeneity and incomplete precision data precluded pooling.

Results: The searches retrieved 535 records; 13 reports were included. Nine addressed AF present in recordings, one documented post-treatment recurrence, one AF discharge-label classification, and two future AF events. In 174 smartwatch recordings, GPT-4o sensitivity was 47.4% (95% CI 38.4%-56.5%; very-low certainty) and specificity was 71.7% (95% CI 59.2%-81.5%; low certainty), compared with 97.4% and 100% for the device algorithm. ECG-FM AF discrimination had moderate certainty in the University Health Network (UHN) evaluation using cardiologist-derived labels (area under the receiver operating characteristic curve (AUROC) 0.996) and low certainty in a separate intensive care unit (ICU) evaluation (AUROC 0.86). These findings concern classification performance, not demonstrated clinical benefit. Neither the added-report restriction nor the documented-adult restriction retained moderate-certainty profiles. Natural language processing (NLP) identified documented recurrence with ECG-report sensitivities of 100% (low certainty) and 92% (very-low certainty) at two sites. Five-year incident-AF AUROC was 0.742 internally and 0.715 in Medical Information Mart for Intensive Care IV (MIMIC-IV) (both low certainty); five-minute warning AUROC was 0.97 (cross-fold SD 0.02; low certainty) in patient-stratified validation. No evaluated system demonstrated improved patient-focused outcomes.

Conclusions: These approaches show task-specific AF analysis capabilities, but clinical benefit remains unestablished. Interpretation must account for outcome timing, evaluation units, and validation settings. Independent patient-level validation and prospective clinical-impact studies are needed; insufficient evidence does not establish ineffectiveness.

Registration: PROSPERO CRD420261408569.

## What is included

- Portable Python plotting scripts and aggregate CSV inputs.
- Seven main figures exported as PNG, SVG, and PDF. Master PNGs default to 600 DPI.
- Optional secondary-results plot from Multimedia Appendix 5 Table S1.
- Aggregate sensitivity scenarios from Multimedia Appendix 6, retained as a table.
- Bibliographic references and validation tests.

No patient-level ECGs, clinical notes, participant identifiers, source PDFs, full-text extractions, reviewer forms, manuscript files, or raw database-search exports are included. CSVs contain only manuscript-level results, reconciled display judgments, selection counts, or diagram labels needed for reproduction. They are **derived aggregate data**, not raw observations.

The current Multimedia Appendices 1–8 contain no embedded figure images. Their appraisal data support main Figures 5–7. The optional Appendix 5 plot is an additional visualization of its table, not an existing submitted figure.

## Installation and use

Python 3.10 or newer is recommended. From this repository folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python scripts/generate_figures.py
```

On Windows activate with `.venv\\Scripts\\activate`.

```bash
# Include the optional Appendix 5 plot:
python scripts/generate_figures.py --appendix

# Smaller master exports or a custom destination:
python scripts/generate_figures.py --dpi 300 --output figures_300dpi

# Regenerate just the appraisal plots:
python scripts/plot_appraisals.py --dpi 600
```

The scripts use paths relative to this repository, work offline after dependency installation, and never read the original research folders. Re-running overwrites generated figures, not input CSVs. No pooled estimates or new appraisal judgments are calculated.

## Figure and data map

| Output | Inputs | Interpretation |
|---|---|---|
| Figure 1 clinical framework | framework.csv | Content-equivalent vector schematic; icons and artwork are not pixel-identical to the manuscript bitmap |
| Figure 2 PRISMA | prisma.csv | Database flow; 535 identified, 174 assessed, 13 included |
| Figure 3 AF accuracy | performance.csv | Separate ECG-image and recurrence-report panels |
| Figure 4 discrimination | performance.csv | Separate five-year, five-minute, and discharge-label endpoints |
| Figure 5 QUADAS-3 | quadas.csv | 11 accuracy records from 10 reports |
| Figure 6 PROBAST+AI | probast.csv | 10 stage/site records from 3 reports |
| Figure 7 GRADE | grade.csv | 35 metric/setting profiles; 6 moderate, 14 low, 15 very low |
| Optional Appendix 5 plot | performance.csv | Secondary monitor-report and note results |
| Appendix 6 sensitivity table | sensitivity_scenarios.csv | Separate scenarios, not cumulative or independent studies |

Figures 1–4 are programmatic redraws with matching content/estimates, not byte-identical copies of previous artwork. Figures 5–7 reuse the reconciled plotting design. Figures are not automatically inserted into Word documents.

## Scientific interpretation

- Sensitivity and specificity are separate. Values are proportions, not percentages, in performance.csv.
- Wilson 95% intervals are recalculated only where numerator and denominator are supplied. Published report-level intervals are retained without assuming independent patients.
- Five-minute warning error bars are cross-fold SDs, **not** confidence intervals.
- Missing intervals remain missing. Comparators are grey in the discrimination plot.
- No meta-analysis, cross-study ranking, patient-level reanalysis, or model training is performed.
- GRADE numeric deductions and display status are separate fields. Grey “–” means inconsistency not assessable; grey “?” means publication bias undetermined. Neither implies evidence of absence.
- MIMIC-IV ECG-FM profiles concern machine-generated labels. Primary ratings and separate restrictions must not be combined as independent replications.
- The PRISMA caption must retain the explanation that two initially excluded database records were later retrieved (172 + 2 = 174), and that one separately citation-identified report was assessed and excluded for population eligibility. That separate report is recorded in prisma.csv but is not included in the database-flow box counts.
- Research limitations, age-confirmation provenance, postregistration eligibility, and GRADE adaptation remain as described in the manuscript and appendices. Plot reproduction does not independently validate them.

## Image files for submission

The generated figures are committed in `figures/` for direct viewing and download: Figures 1–7 and the optional Appendix 5 secondary-results plot, each as PNG, SVG, and PDF. Smaller PNG copies are in `figures/JMIR_upload_ready/`. These are outputs of the supplied scripts, not raw study data.

Master PNGs are rendered at 600 DPI by default, with vector SVG/PDF alternatives. `figures/JMIR_upload_ready/` contains opaque RGB PNG copies within 1200 × 1200 pixels and 5 MB. DPI metadata alone does not create detail. JMIR's currently published upload guidance specifies these pixel/file limits, not a universal 600-DPI requirement:
https://support.jmir.org/hc/en-us/articles/115002199367

Review the upload preview before submitting, especially dense Figure 7. Captions belong in the manuscript/submission fields, not inside image files.

## Data provenance and updates

See [data dictionary](DATA_DICTIONARY.md). Performance estimates trace to manuscript references in data/references.csv and source locators in performance.csv. Appraisal display CSVs were exported from the reconciled current figure data; full appraisal rationales remain in Multimedia Appendices 6–8, not in this repository. Sensitivity counts are transcribed from Appendix 6 and are not recalculated from individual participants.

The README abstract is a snapshot of the current manuscript. Update it explicitly when the manuscript changes. Any scientific data change should be reviewed against the source, followed by the tests and regeneration. Do not replace unavailable information with zeros.

## Citation and permissions

Please cite the systematic review using the title and authors above. No publication DOI has been assigned in this package. The repository retains its existing MIT license (see LICENSE). This license does not change rights in the published source papers or their underlying datasets; neither is redistributed here.

