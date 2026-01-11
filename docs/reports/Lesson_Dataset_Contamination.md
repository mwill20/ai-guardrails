# Lesson: Dataset Contamination Breaks Security Metrics

## Summary
When benign datasets contain hidden attacks, FPR explodes and security decisions become inverted. A contaminated benign set makes real attacks look like false positives, which can cause you to weaken defenses instead of improving them.

## What Happened Here
- TrustAIRLab regular is labeled benign but contains jailbreak-style prompts.
- Contaminated benign data inflated FPR and made the semantic model look worse than it was.
- A clean benign corpus (Clean_Benign_Corpus_v1) restored a reliable FPR baseline.

## The Core Lesson
Treat data quality as part of the security boundary. If your benign set is noisy, your metrics are untrustworthy and tuning decisions become harmful.

## Walkthrough (Recommended Practice)
1. **Detect contamination**
   - Run a contamination scan and create a removal list.
   - Script: `scripts/analysis/Analyze_Dataset_Contamination.py`

2. **Quarantine and version**
   - Keep a timestamped cleaned snapshot and the removal list.
   - Store hashes and provenance (see dataset card).

3. **Separate benchmarks from research**
   - Official FPR gate: `datasets/Clean_Benign_Corpus_v1.jsonl`
   - Research-only benign set: cleaned TrustAIRLab snapshot

4. **Compare side-by-side (research)**
   - Use the research comparison script to quantify contamination impact.
   - Script: `scripts/evaluation/Eval_Research_Benign_Comparison.py`

5. **Make decisions using clean ground truth**
   - Tune thresholds and patterns against the clean corpus only.
   - Use TrustAIRLab cleaned data for directional insights, not go/no-go gates.

## What We Changed in This Repo
- Cleaned TrustAIRLab snapshot is versioned and documented.
- Main eval harness uses Clean_Benign_Corpus_v1 for FPR.
- Added a research-only comparison script for side-by-side benign FPR.

## How to Capitalize on This
- Document data quality as part of your security methodology.
- Show how contamination shifts metrics (before/after comparison).
- Treat dataset QA as a reusable guardrail for new corpora.

## References
- Dataset card: `docs/reports/TrustAIRLab_regular_2023_12_25_CLEANED_Dataset_Card.md`
- Removal list: `reports/trustairlab_regular_contaminated_20260111_091814.jsonl`
- Clean snapshot: `datasets/TrustAIRLab_regular_2023_12_25_CLEANED_20260111_091814.jsonl`
