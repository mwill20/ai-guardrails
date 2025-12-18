# Quick Reference Guide

## 🚀 Most Common Commands

### Run Latest Clean Corpus Evaluation
```powershell
python scripts/evaluation/Eval_Clean_Benign_Corpus.py
```
**Expected Result:** 1.0% FPR (2/200 blocked)

### Run Full Benchmark on TrustAIRLab Datasets
```powershell
python scripts/evaluation/Eval.py
```
**Expected Result:** 66.6% mean TPR, detailed breakdown by dataset

### Test ProtectAI Model Performance
```powershell
python scripts/evaluation/Benchmark_ProtectAI.py
```
**Compares:** madhurjindal vs ProtectAI models

### Analyze Dataset Quality
```powershell
python scripts/analysis/Inspect_TrustAIR_Regular.py
```
**Shows:** First 20 "benign" samples for manual review

### Test Benign Blocking Patterns
```powershell
python scripts/testing/Test_Benign_Blocking.py
```
**Shows:** Why specific benign prompts get blocked

---

## 📂 Quick File Finder

**"I need to..."**

| Task | File Location |
|------|---------------|
| Modify core guardrail logic | `src/OWASP_Pipeline_Guardrail.py` |
| Update deterministic patterns | `src/Deterministic_Guardrails.py` |
| Add new evaluation | `scripts/evaluation/` (create new file) |
| See latest results | `reports/` (timestamped JSON files) |
| Review project goals | `docs/planning/AI_Guardrail_NorthStar (1).md` |
| Check work history | `docs/reports/WORK_LOG_Phase2_Semantic_Model_Selection.md` |
| Understand decision rationale | `docs/reports/STRATEGIC_ANALYSIS_FPR_And_Next_Steps.md` |
| See clean corpus results | `docs/reports/Clean_Benign_Corpus_Evaluation_Report.md` |
| View test dataset | `datasets/Clean_Benign_Corpus_v1.jsonl` |
| Find archived runs | `archive/old_evals/` |

---

## 🔧 Import Pattern

When creating new scripts:

```python
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import guardrail
from src.OWASP_Pipeline_Guardrail import run_guardrail_pipeline

# Use project-relative paths
project_root = Path(__file__).parent.parent.parent
dataset_path = project_root / "datasets" / "your_dataset.jsonl"
output_path = project_root / "reports" / "your_output.json"
```

---

## 📊 Current Status Quick Facts

| Metric | Value |
|--------|-------|
| **Phase** | 2.5 Complete ✅ |
| **Current Model** | ProtectAI deberta-v3-base-prompt-injection-v2 |
| **True FPR** | 1.0% (2/200 clean prompts) |
| **Core Use Cases FPR** | 0% |
| **Mean TPR** | 66.6% |
| **Production Ready** | YES ✅ |
| **Next Phase** | Phase 3: Adversarial Testing |

---

## 🎯 Decision Quick Reference

**Semantic Intent Layer:** ❌ SKIP  
- **Why:** 1.0% FPR acceptable, cost/benefit unfavorable for 1% → 0%

**Model Swap:** ✅ COMPLETE  
- **From:** madhurjindal (93.6% FPR)
- **To:** ProtectAI v2 (1.0% FPR)
- **Improvement:** 92.6 percentage points

**Next Priority:** Attack Detection (TPR improvement)  
- **Focus Area:** xTRam1 (currently 25.4% TPR)
- **Approach:** Adversarial testing, preprocessing layer

---

## 🔍 Troubleshooting

### Import Errors
```powershell
# Ensure you're running from project root
cd C:\Projects\Guardrails
python scripts/evaluation/Eval_Clean_Benign_Corpus.py
```

### Missing Dependencies
```powershell
pip install -r requirements.txt
```

### "Dataset not found" Errors
- Check: Dataset should be at `datasets/Clean_Benign_Corpus_v1.jsonl`
- Scripts use `Path(__file__).parent.parent.parent` to find project root

### Results Not Saving
- Check: `reports/` directory exists (should be created automatically)
- Permissions: Ensure write access to reports/ directory

---

## 📝 File Naming Conventions

**Evaluation Scripts:** `Eval_[Purpose].py`  
**Analysis Scripts:** `Analyze_[Topic].py`  
**Test Scripts:** `Test_[Feature].py`  
**Reports:** `[type]_eval_[timestamp].json`  
**Docs:** `[TOPIC]_[Context].md`

---

## 🗂️ Directory Structure (Simplified)

```
Guardrails/
├── src/              # Core modules - modify for logic changes
├── scripts/          # Utilities - run these for evaluation/analysis
├── datasets/         # Test data - add new corpora here
├── reports/          # Results - automatically generated
├── docs/             # Documentation - read for context
└── archive/          # History - reference only
```

---

## 💡 Tips

1. **Always run from project root** (`C:\Projects\Guardrails`)
2. **Check README.md first** for comprehensive overview
3. **Review WORK_LOG** for complete history of Phase 2 work
4. **Look at latest reports/** for current metrics
5. **Archive old runs** to keep reports/ clean

---

**Last Updated:** December 13, 2025  
**Project Status:** Production-ready, 1.0% FPR validated
