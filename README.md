<div align="center">
  <img src="docs/AI_Guardrail_Logo.png" alt="AI Guardrails Logo" width="400"/>
  
  # AI Guardrails System
  
  **An ongoing learning project** building a production-grade, multi-layered prompt security system combining deterministic OWASP patterns, semantic ML-based detection, and policy enforcement to protect AI/Agentic Systems from prompt injection and jailbreak attacks.
</div>

> **Project Status:** Active development | Phase 2.6 in progress  
> **Focus:** Systematic security engineering methodology with measurement-driven decisions

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

## 🎯 Project Status & Roadmap

### Current Phase: 2.6 - Deterministic Enrichment 🔄

**Objective:** Improve xTRam1 TPR from 25.4% → ≥40% by adding pattern-based detection rules discovered through systematic evaluation log analysis.

**Approach:**
- Extract attack patterns from false negative prompts (evaluation logs)
- Rank patterns by priority score (FN coverage vs FP risk)
- Implement deterministic detection functions with signal strength scoring
- Maintain FPR ≤2.0% (Gate A) while lifting mean TPR to ≥71% (Gate B)

### Completed Phases

#### ✅ Phase 1: Deterministic Guardrails (OWASP-Aligned)
- 5-stage pipeline: ingestion → classification → sanitization → logging → policy
- Pattern-based detection (keywords, regex) for known attack types
- Risk classification: low/medium/high/critical
- **Result:** Fast, explainable baseline defense layer

#### ✅ Phase 2: Semantic Guardrails (ML-Based Detection)
- **Problem:** Initial model (madhurjindal) had 93.6% FPR
- **Solution:** Systematic benchmarking → switched to ProtectAI deberta-v3-base-prompt-injection-v2
- **Achievement:** 92.6pp FPR improvement (93.6% → 1.0%)
- **Current Metrics:**
  - True FPR: **1.0%** (2/200 clean prompts blocked)
  - Mean TPR: **66.6%** across attack datasets
  - Core Use Cases FPR: **0%** (160/160 passed)

#### ✅ Phase 2.5: Clean Corpus Validation
- Built Clean_Benign_Corpus_v1 (200 vetted prompts across 8 categories)
- Discovered TrustAIRLab "benign" dataset contamination
- Validated 1.0% FPR on production-representative prompts
- **Decision:** Deferred semantic intent layer to Phase 3.5 (cost/benefit analysis)

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

### Three-Layer Defense-in-Depth

1. **Deterministic Layer (Phase 1 + 2.6 Enhancement)**
   - OWASP Top 10 LLM patterns (Phase 1 baseline)
   - Evidence-based attack patterns from eval logs (Phase 2.6)
   - Signal strength scoring: weak (boundary testing) vs strong (system markers, control phrases)
   - Fast (<10ms), explainable, zero ML cost

2. **Semantic Layer (Phase 2)**
   - ProtectAI deberta-v3-base-prompt-injection-v2
   - ML-based intent classification for novel attacks
   - Handles obfuscation, paraphrasing, multi-turn attacks

3. **Policy Layer (Planned Phase 3+)**
   - Layer precedence enforcement (safety ratchet: deterministic escalates, never downgrades)
   - No silent allow invariant (explicit ALLOW/SANITIZE/BLOCK required)
   - Context-aware decisions (user roles, sensitivity levels)

### Risk Scoring & Signal Combination

**Deterministic Signals (Phase 2.6):**
- Score 3 (any category) → **high_risk**
- Score 2+2 (two strong signals) → **high_risk**
- Score 2+1 (strong + weak) → **medium_risk**
- Score 1 alone (weak only) → **low_risk** (NO escalation)
- Score 0 (none) → **low_risk**

**Final Risk Levels:**
- **Low Risk:** Allowed, logged
- **Medium Risk:** Allowed with warning, enhanced logging
- **High Risk:** Blocked, detailed logging, security team alert
- **Critical Risk:** Blocked, immediate escalation, forensic capture

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

## 🎯 Planned Enhancements

### Phase 2.6: Deterministic Enrichment (Active)
**Timeline:** 3-5 days | **Status:** Pattern discovery in progress

1. **Pattern Discovery Pipeline**
   - ✅ Schema v1 contract locked (JSONL output with full traceability)
   - ✅ Pattern matching semantics defined (substring/regex/keyword_set)
   - 🔄 Extract patterns from FN prompts (5 categories: system_marker, control_phrase, credential_like, boundary_testing, role_confusion)
   - 🔄 Compute priority_score = (fn_coverage_rate × 2.0) - (fp_risk_score × 5.0) + (rarity_score × 0.5)
   - 🔄 Validate against Clean_Benign_Corpus_v1 (max 1 FP per pattern)

2. **Implementation**
   - Create `Deterministic_Guardrails_Enhanced.py` with 5 detection functions
   - Implement signal combination logic per scoring table
   - Enforce layer precedence (safety ratchet) and no silent allow invariant
   - Unit tests for pattern matching, signal scoring, and layer interaction

3. **Quality Gates**
   - **Gate A:** FPR ≤2.0% on Clean_Benign_Corpus_v1
   - **Gate B1:** xTRam1 TPR ≥40% (baseline 25.4%, +15pp lift)
   - **Gate B2:** Mean TPR ≥71% (baseline 66.6%, +5pp lift)

### Phase 3: Adversarial Testing & Red-Teaming (Planned)
**Focus:** Stress-test both layers against novel attack vectors

1. **Coverage Gap Analysis**
   - Document remaining FNs after Phase 2.6
   - Categorize bypass techniques (obfuscation, encoding, multi-turn)
   - Use HackAPrompt Companion for dynamic attack generation

2. **Obfuscation Defenses**
   - Base64/hex decoding preprocessing
   - Multi-language normalization
   - Character substitution detection (l33t speak, homoglyphs)

3. **Code Hardening**
   - Robust label normalization (`_is_benign_prediction()` helper)
   - Structured logging (JSON format with model/pattern IDs)
   - Timeout guards for regex (prevent catastrophic backtracking)

### Phase 3.5: Semantic Intent Layer (Deferred)
**Rationale:** Cost/benefit analysis showed unfavorable ROI for 1.0% → 0% FPR improvement

- LLM-based intent classification for edge cases
- Explainability enhancements ("why was this blocked?")
- Conditional activation (only for ambiguous prompts)

### Phase 4+: Production Hardening (Future)
- OWASP AI Top 10 mapping and compliance documentation
- Reasoning guardrails (tool use governance for agentic systems)
- Custom linter (meta-guardrail for policy enforcement)
- Performance optimization (caching, batching, async processing)

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

### Phase 2.5 Achievements ✅
- **FPR < 5%** on clean benign corpus → **achieved: 1.0%**
- **TPR > 60%** on attack datasets → **achieved: 66.6%**
- **Core use cases: 0% FPR** → **achieved: 100%** (160/160 passed)
- **Production-ready baseline** → semantic + deterministic layers validated

### Phase 2.6 Targets 🎯
- **Gate A:** FPR ≤2.0% (maintain low false positive rate)
- **Gate B1:** xTRam1 TPR ≥40.0% (currently 25.4%, need +15pp lift)
- **Gate B2:** Mean TPR ≥71.0% (currently 66.6%, need +5pp lift)
- **Latency:** Deterministic layer <10ms (non-blocking)

## 🤝 Contributing

This is a learning/portfolio project demonstrating systematic security engineering methodology. Key principles:

- **Measurement-driven decisions** (FPR/TPR gates, not vibes)
- **Reproducible artifacts** (eval logs, pattern discovery JSONL)
- **Defense-in-depth** (multiple layers with clear precedence rules)
- **No silent failures** (explicit ALLOW/SANITIZE/BLOCK required)

## 📜 License

MIT License - Internal research project for learning and portfolio development

## 👤 Author

**Michael Williams**  
- Phase 1: Deterministic baseline (OWASP patterns)
- Phase 2: Semantic layer + model selection (Dec 13, 2025)
- Phase 2.5: Clean corpus validation (Dec 13, 2025)
- Phase 2.6: Deterministic enrichment (Dec 14-15, 2025) - **In Progress**

---

**Project Timeline:**  
- Started: November 2025
- Phase 2.5 Complete: December 13, 2025
- Phase 2.6 Active: December 14, 2025
- Next Milestone: Gate A/B validation (Phase 2.6 complete)

**GitHub:** [mwill20/ai-guardrails](https://github.com/mwill20/ai-guardrails)
