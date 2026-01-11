# TrustAIRLab regular (cleaned) - Dataset Card

## Overview
- **Dataset:** TrustAIRLab/in-the-wild-jailbreak-prompts (regular_2023_12_25)
- **Snapshot:** TrustAIRLab_regular_2023_12_25_CLEANED_20260111_091814.jsonl
- **Purpose:** Research-only benign set after removing obvious jailbreak indicators
- **Status:** Not approved for benchmark FPR

## Source
- **Origin:** Hugging Face dataset: TrustAIRLab/in-the-wild-jailbreak-prompts
- **Config:** regular_2023_12_25
- **Fields used:** prompt

## Cleaning Method
- **Script:** scripts/analysis/Analyze_Dataset_Contamination.py
- **Rule set:** Regex/keyword indicators (ignore instructions, DAN, jailbreak, token injection, bypass, etc.)
- **Action:** Remove rows matching attack indicators from the benign-labeled pool
- **Output:**
  - Cleaned benign snapshot (kept)
  - Contamination removal list (kept)

## Artifacts
- **Cleaned dataset:** datasets/TrustAIRLab_regular_2023_12_25_CLEANED_20260111_091814.jsonl
- **Removal list:** reports/trustairlab_regular_contaminated_20260111_091814.jsonl
- **Hashes (SHA256):**
  - 19A4565CFA24398DC1E5E3D99D1F3F57919934EEBDFC520A4DCFC0550BA7140F  datasets/TrustAIRLab_regular_2023_12_25_CLEANED_20260111_091814.jsonl
  - A58E92B3552C2E83F1DAD35DC41026B1C7EC5898A54515E0D5356D698D009F55  reports/trustairlab_regular_contaminated_20260111_091814.jsonl

## Intended Use (Research)
- Compare FPR sensitivity against a larger, wild benign set
- A/B analysis against Clean_Benign_Corpus_v1 to quantify contamination impact
- Hard-negative mining for ambiguous prompts

## Not Approved For
- Official FPR gates or release metrics
- Benchmarks that claim "clean benign" ground truth

## Known Limitations
- Cleaning is pattern-based and conservative; contamination may remain
- The removal list is not a gold-standard label set
- Metrics are useful directionally, not as final truth

## Reproduction
```powershell
python scripts/analysis/Analyze_Dataset_Contamination.py
```

## Notes
- The official benign FPR gate remains `datasets/Clean_Benign_Corpus_v1.jsonl`.
- Research comparisons can be run with `scripts/evaluation/Eval_Research_Benign_Comparison.py`.
