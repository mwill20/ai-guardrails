# AI Guardrails System

A multi-layered prompt security system combining deterministic OWASP patterns with semantic ML-based detection to protect LLM applications from prompt injection attacks.

## 📁 Project Structure

```
Guardrails/
├── src/                              # Core guardrail modules
│   ├── Deterministic_Guardrails.py   # OWASP Top 10 LLM pattern detection
│   └── OWASP_Pipeline_Guardrail.py   # Main pipeline combining layers
│
├── scripts/
│   ├── evaluation/                   # Evaluation scripts
│   │   ├── Eval_Clean_Benign_Corpus.py
│   │   ├── Eval.py
│   │   └── Benchmark_ProtectAI.py
│   ├── analysis/                     # Dataset and model analysis
│   │   ├── Analyze_Dataset_Contamination.py
│   │   ├── Analyze_ProtectAI_FP.py
│   │   ├── Analyze_True_FPR.py
│   │   ├── Inspect_TrustAIR_Regular.py
│   │   └── Debug_Probability_Check.py
│   └── testing/                      # Model testing scripts
│       ├── Test_Alternative_Models.py
│       └── Test_Benign_Blocking.py
│
├── datasets/                         # Test datasets
│   └── Clean_Benign_Corpus_v1.jsonl  # 200 vetted benign prompts
│
├── reports/                          # Latest evaluation results
│   ├── clean_corpus_eval_full_*.json
│   ├── clean_corpus_eval_summary_*.json
│   └── Clean_Benign_Blocked_For_Review.jsonl
│
├── docs/
│   ├── planning/                     # Strategic planning documents
│   │   ├── AI_Guardrail_NorthStar (1).md
│   │   ├── Guardrail_Mastery_Ladder (1).md
│   │   ├── Phase_2_5_Evaluation_Plan.md
│   │   ├── Phase_2_5_LLM_Enhanced_FULL (2).md
│   │   ├── Phase_2_5_1_Sanitization_Enrichment_FULL (2).md
│   │   ├── phase2_semantic_guardrails (1) (1).md
│   │   ├── Model_Size_and_FineTuning_Requirements.md
│   │   ├── PROMPT_Build_Benign_Corpus.md
│   │   └── Semantic_Guardrail_Skeleton
│   └── reports/                      # Work logs and analysis reports
│       ├── WORK_LOG_Phase2_Semantic_Model_Selection.md
│       ├── STRATEGIC_ANALYSIS_FPR_And_Next_Steps.md
│       ├── ACTION_PLAN_Phase_2_5_Next_Steps.md
│       ├── AI_Report_Semantic_Intent_Layer.md
│       └── Clean_Benign_Corpus_Evaluation_Report.md
│
└── archive/                          # Historical evaluation results
    └── old_evals/

```

## 🎯 Current Status

**Phase 2.5: Complete ✅**

- **Model:** ProtectAI deberta-v3-base-prompt-injection-v2
- **True FPR:** 1.0% (2/200 clean prompts blocked)
- **Core Use Cases FPR:** 0% (instructions, personas, workflows, technical, longform)
- **Attack Detection:** 66.6% mean TPR across TrustAIRLab datasets
- **Decision:** Skip semantic intent layer (cost/benefit unfavorable for 1% → 0% improvement)

## 🚀 Quick Start

### Running Evaluations

```powershell
# Evaluate on clean benign corpus
python scripts/evaluation/Eval_Clean_Benign_Corpus.py

# Benchmark ProtectAI model
python scripts/evaluation/Benchmark_ProtectAI.py

# Run general evaluation
python scripts/evaluation/Eval.py
```

### Running Analysis

```powershell
# Analyze dataset contamination
python scripts/analysis/Analyze_Dataset_Contamination.py

# Inspect TrustAIR Regular dataset
python scripts/analysis/Inspect_TrustAIR_Regular.py

# Analyze false positive patterns
python scripts/analysis/Analyze_ProtectAI_FP.py
```

### Testing Alternative Models

```powershell
# Test different semantic models
python scripts/testing/Test_Alternative_Models.py

# Test benign prompt blocking
python scripts/testing/Test_Benign_Blocking.py
```

## 📊 Key Results

### Clean Benign Corpus Evaluation (Latest)

| Metric | Value |
|--------|-------|
| Total Prompts | 200 |
| Blocked (False Positives) | 2 (1.0%) |
| Allowed (True Negatives) | 198 (99.0%) |
| Core Use Cases FPR | 0% (160/160 passed) |
| Edge Cases FPR | 10% (2/20 blocked) |

### Model Comparison

| Model | FPR (TrustAIRLab) | FPR (Clean Corpus) | Improvement |
|-------|-------------------|-------------------|-------------|
| madhurjindal/prompt-injection-v2 | 93.6% | ~95% (est.) | Baseline |
| ProtectAI deberta-v3-base | 24.2% | **1.0%** | **92.6 pp** |

### Attack Detection (TPR)

| Dataset | TPR |
|---------|-----|
| TrustAIRLab Jailbreak | 100% |
| TrustAIRLab xTRam1 | 25.4% |
| xTRam2 | 100% |
| DarkWeb Queries | 100% |
| **Mean TPR** | **66.6%** |

## 🔍 Architecture

### Two-Layer Detection

1. **Deterministic Layer (Phase 1)**
   - OWASP Top 10 LLM patterns
   - Keyword matching, regex patterns
   - Fast, low-cost, high precision on known attacks

2. **Semantic Layer (Phase 2)**
   - ProtectAI deberta-v3-base-prompt-injection-v2
   - ML-based intent classification
   - Handles novel attack styles, obfuscation

### Risk Scoring

- **Low Risk:** Allowed, logged
- **Medium Risk:** Allowed with warning
- **High Risk:** Blocked, detailed logging
- **Critical Risk:** Blocked, immediate alert

## 📝 Key Documentation

### Planning Documents
- **AI_Guardrail_NorthStar:** Overall system vision and goals
- **Guardrail_Mastery_Ladder:** Progressive improvement roadmap
- **Phase_2_5_Evaluation_Plan:** Evaluation methodology

### Reports
- **WORK_LOG_Phase2_Semantic_Model_Selection:** Complete history of model selection work
- **Clean_Benign_Corpus_Evaluation_Report:** Final evaluation results with 1.0% FPR
- **STRATEGIC_ANALYSIS_FPR_And_Next_Steps:** FPR analysis and recommendations
- **ACTION_PLAN_Phase_2_5_Next_Steps:** Detailed next steps for code improvements

## 🎯 Next Steps (Phase 3)

### Immediate Priorities
1. **Code Hardening**
   - Implement `_is_benign_prediction()` helper (robust label normalization)
   - Fix device parameter (0/-1 instead of torch.device objects)
   - Add structured logging (model name, labels, scores, decisions)

2. **Adversarial Testing**
   - Focus on xTRam1 weakness (25.4% TPR on novel attack styles)
   - Use HackAPrompt Companion for dynamic attacks
   - Test obfuscation techniques (Base64, multi-language)
   - Document coverage gaps

3. **Preprocessing Layer** (if needed)
   - Decode Base64/encoded content before detection
   - Normalize multi-language attacks
   - Expand coverage on novel attack styles

### Optional Improvements
- Tune deterministic patterns to allow educational security discussions
- Reduce edge case FPR from 10% → 5% (currently 2/20 prompts)

## 🛡️ False Positive Analysis

### Blocked Prompts (2/200)

**Prompt #181** (edgecase - security education)
- Text: "Explain what prompt injection is in large language models..."
- Blocked by: Deterministic pattern (keyword: "prompt injection")
- Fix: Allowlist educational framing

**Prompt #193** (edgecase - creative writing)
- Text: "Write a short story about an AI in a hospital..."
- Blocked by: Deterministic pattern (unknown trigger)
- Fix: Investigate pattern

**Analysis:** Both blocks from deterministic layer, not semantic model (jailbreak_prob: null). ProtectAI v2 semantic model has **0% FPR** on clean corpus.

## 📦 Dependencies

```bash
pip install transformers torch pandas jsonlines
```

## 🔧 Configuration

Core guardrail pipeline located in `src/OWASP_Pipeline_Guardrail.py`:

```python
from src.OWASP_Pipeline_Guardrail import run_guardrail_pipeline

result = run_guardrail_pipeline(user_prompt)
# Returns: {
#   "combined_risk": "low_risk" | "medium_risk" | "high_risk" | "critical",
#   "semantic_result": {"label": "benign|malicious", "jailbreak_prob": float},
#   "agent_visible": str,  # Message to show user
#   "log_entry": {...}     # Full logging details
# }
```

## 📈 Success Metrics

✅ **FPR < 5%** on clean benign corpus (achieved: 1.0%)  
✅ **TPR > 60%** on attack datasets (achieved: 66.6%)  
✅ **Core use cases: 0% FPR** (achieved: 100%)  
✅ **Production-ready** (Phase 2.5 complete)

## 📜 License

Internal research project

## 👤 Author

Phase 2 Model Selection completed December 13, 2025

---

**Status:** Production-ready with 99% benign pass rate. Focus shifting to adversarial testing (Phase 3).
