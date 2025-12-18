# AI Guardrails Project Roadmap
**Master Checklist & Progress Tracker**

**Last Updated:** December 13, 2025  
**Current Phase:** Phase 2.51 (Next Step)  
**Project Type:** Learning & Portfolio Development  
**Production Ready:** Phase 2 complete, FPR validated at 1.0%

---

## 🎯 Project Vision

Build a production-grade, multi-layered prompt security system that:
- **Defends** LLM applications from prompt injection and jailbreak attacks
- **Demonstrates** systematic security engineering methodology
- **Documents** measurement-driven decision-making process
- **Showcases** defense-in-depth architecture understanding

**Learning Focus Areas:**
- ✅ Clean ground truth dataset construction
- ✅ Systematic evaluation methodologies (FPR/TPR measurement)
- ✅ Model selection impact analysis
- ✅ Trade-offs documentation (complexity vs. improvement)
- 🔄 Adversarial testing frameworks
- 📋 Multi-layer security architecture
- 📋 Coverage gap analysis and remediation

---

## 📊 Current Status Overview

| Phase | Status | FPR | TPR | Notes |
|-------|--------|-----|-----|-------|
| **Phase 1** | ✅ Complete | N/A | N/A | Deterministic patterns (OWASP-aligned) |
| **Phase 2** | ✅ Complete | 1.0% | 66.6% | ProtectAI v2 model (validated) |
| **Phase 2.6** | 🎯 **NEXT** | TBD | TBD | Deterministic enrichment (attack patterns) |
| **Phase 2.5** | ⏸️ Deferred → 3.5 | N/A | N/A | Intent layer (explainability/coverage) |
| **Phase 3** | 📋 Planned | TBD | TBD | Adversarial testing & red-teaming |
| **Phase 4** | 📋 Planned | N/A | N/A | Documentation & portfolio polish |
| **Phase 5** | 📋 Optional | N/A | N/A | OWASP AI Top 10 mapping |
| **Phase 5.5** | 📋 Optional | N/A | N/A | Reasoning guardrails (tool governance) |
| **Phase 6** | 📋 Optional | N/A | N/A | Custom linter (meta-guardrail) |

**Legend:** ✅ Complete | 🎯 Active | 🔄 In Progress | ⏸️ Deferred | 📋 Planned | ❌ Skipped

---

## 🏗️ Phase-by-Phase Breakdown

---

### ✅ Phase 1: Deterministic Guardrails (COMPLETE)

**Purpose:** Foundational pipeline with predictable, explainable behavior

**Deliverables:**
- ✅ 5-stage deterministic pipeline (ingestion → classification → sanitization → logging → policy)
- ✅ `Deterministic_Guardrails.py` (pattern-based detection)
- ✅ Risk classification: `low_risk`, `medium_risk`, `high_risk`
- ✅ Keyword-based sanitization (remove "system", "override")
- ✅ Safe logging (no raw input leakage)
- ✅ Final policy gate (block vs allow decisions)

**OWASP Coverage:**
- ASI01: Prompt Injection (basic keyword detection)
- ASI03: Training Data Poisoning (input sanitization)
- ASI05: Supply Chain Vulnerabilities (deterministic validation)
- ASI06: Sensitive Information Disclosure (logging controls)

**Key Design Principles:**
- Zero rewriting or paraphrasing
- Fully deterministic (reproducible)
- Transparent and auditable
- Fail-closed (conservative defaults)

**Status:** Production-ready, forms baseline security layer

---

### ✅ Phase 2: Semantic Guardrails (COMPLETE)

**Purpose:** ML-based detection for patterns beyond simple rules

#### Phase 2.0: Model Selection Crisis
**Problem:** madhurjindal/Jailbreak-Detector-Large → 93.6% FPR (468/500 benign blocked)

**Investigation:**
- ✅ Validated probability extraction (not a bug)
- ✅ Tested alternative models (ProtectAI, Meta Prompt Guard, xTRam)
- ✅ Systematic benchmarking on TrustAIRLab datasets

**Solution:** Model swap to ProtectAI deberta-v3-base-prompt-injection-v2

**Results:**
- FPR: 93.6% → 24.2% (TrustAIRLab Regular)
- TPR: 53.5% → 66.6% (mean across attack datasets)
- Improvement: -69.4 pp FPR, +13.1 pp TPR

#### Phase 2.5: Clean Corpus Validation
**Problem:** TrustAIRLab "benign" dataset contaminated with attacks

**Solution:**
- ✅ Built clean benign corpus (200 prompts, 6 categories)
- ✅ Manual curation (no attack language, realistic use cases)
- ✅ Evaluation script (`Eval_Clean_Benign_Corpus.py`)

**Validated Results:**
- **True FPR: 1.0%** (2/200 blocked, both edge cases)
- Core use cases: 0% FPR (instructions, personas, workflows, technical, longform)
- Edge cases: 10% FPR (security education, creative AI writing)
- **Both blocks from deterministic patterns, not semantic model**

**Key Insight:** ProtectAI v2 semantic model has 0% FPR on clean corpus (jailbreak_prob: null for blocked prompts = deterministic trigger)

**Decision:** Production-ready at 1.0% FPR, model swap highly successful

**Documentation:**
- ✅ `WORK_LOG_Phase2_Semantic_Model_Selection.md` (702 lines)
- ✅ `Clean_Benign_Corpus_Evaluation_Report.md`
- ✅ `STRATEGIC_ANALYSIS_FPR_And_Next_Steps.md`
- ✅ `ACTION_PLAN_Phase_2_5_Next_Steps.md`

**Files:**
- ✅ `src/OWASP_Pipeline_Guardrail.py` (main pipeline)
- ✅ `datasets/Clean_Benign_Corpus_v1.jsonl` (200 prompts)
- ✅ `scripts/evaluation/Eval_Clean_Benign_Corpus.py`
- ✅ `scripts/evaluation/Benchmark_ProtectAI.py`
- ✅ `reports/Clean_Benign_Corpus_Evaluation_Report.md`

**Status:** Complete, 1.0% FPR validated, production-ready

---

### 🎯 Phase 2.6: Deterministic Sanitization Enrichment (NEXT STEP)

**Purpose:** Strengthen deterministic layer using Phase 2 intelligence

**Why This Phase:**
- NOT about FPR (already 1.0%) — about TPR (attack coverage)
- ProtectAI v2 has weak spots: xTRam1 (25.4% TPR on novel attacks), multi-turn attacks
- Deterministic patterns should catch obvious attacks BEFORE semantic model
- Reduces semantic model load and latency
- Maintains explainability (deterministic = auditable)
- Cheap + auditable alternative to adding LLM reasoning overhead

**Data Sources for Pattern Discovery:**
- ✅ ProtectAI v2 high-confidence malicious detections (jailbreak_prob > 0.9)
- 🔄 xTRam1 dataset analysis (find 75% that bypass current detection)
- 🔄 TrustAIRLab attack datasets (jailbreak, DarkWeb queries)
- 🔄 Lakera PINT benchmark patterns
- 🔄 Mindgard jailbreak corpus
- 🔄 Current guardrail logs (critical/malicious tags)

**Pattern Categories to Add:**

#### 1. System/Prompt Markers (High Priority)
```python
# Patterns consistently flagged by ProtectAI v2 as malicious
"system prompt"
"hidden instructions"
"reveal your system prompt"
"show me your instructions"
"assistant:" (role confusion)
"system:" (role injection)
"[INST]" (instruction markers)
"<<SYS>>" (system tags)
```

#### 2. Credential-Like Tokens (Medium Priority)
```python
# Prevent key extraction attempts
"sk-..." (OpenAI API keys)
"AKIA..." (AWS access keys)
".env=" (environment variable patterns)
"api_key=" / "apikey="
"secret_key="
"bearer token"
```

#### 3. Control Phrases (High Priority)
```python
# Patterns triggering semantic escalation
"ignore previous instructions"
"ignore all instructions"
"disregard safety guidelines"
"bypass safety"
"override your restrictions"
"forget your rules"
"new instructions:"
```

#### 4. Boundary Testing Language (WEAK SIGNALS - Combination Only)
```python
# Common in xTRam1 novel attacks
# ⚠️ NEVER escalate alone (high FPR risk)
# Only escalate when combined with strong indicators (1+2+3)
"for testing purposes"
"in a hypothetical scenario"
"pretend that"
"roleplay as"
"simulate"
"imagine you are not bound by"
```

**Signal Classification:**
- **Strong Signals (1-3):** System markers, credential patterns, control phrases → Can trigger high_risk alone
- **Weak Signals (4):** Boundary testing language → Only escalates risk when combined with strong signals

**Signal Strength Scoring (Explicit Definition):**
| Score | Meaning | Interpretation | Example |
|-------|---------|----------------|----------|
| **0** | No signal | Pattern not detected | Clean prompt |
| **1** | Weak presence | Partial match or benign context | "imagine" alone |
| **2** | Clear match | Unambiguous pattern hit | "ignore instructions" |
| **3** | High-confidence malicious | Multiple patterns or strong indicator | "system:" + "override" |

**Why This Matters:**
- Prevents ambiguous interpretation during implementation
- Makes logs human-readable ("system_marker_strength=3" has precise meaning)
- Enables precise unit test assertions ("expect signal_strength >= 2")
- Supports future pattern tuning decisions

**Quality Gates (Must Pass):**

#### Gate A: FPR Regression Gate
- [ ] Run `Eval_Clean_Benign_Corpus.py` on Clean_Benign_Corpus_v1
- [ ] FPR must remain ≤ 2.0% (current: 1.0%)
- [ ] If fails: rollback patterns, analyze which triggered on benign
- [ ] CI blocker: commit doesn't merge if FPR > 2%

#### Gate B: Coverage Lift Gate
- [ ] xTRam1 TPR must improve by ≥15 percentage points (from 25.4% → ≥40%)
- [ ] Mean TPR must improve by ≥5 percentage points (from 66.6% → ≥71%)
- [ ] If fails: patterns not providing value, reconsider scope
- [ ] Justification: Don't add complexity without measurable coverage improvement

---

**Phase 2.6 Checklist:**

#### Step 1: Data-Driven Pattern Discovery (Week 1) ✅ **COMPLETE**
- [x] Run `Eval.py` on standardized datasets, save detailed logs:
  - [x] TrustAIRLab_jailbreak (attacks, 80.6% TPR)
  - [x] TrustAIRLab_xTRam1 (novel attacks, 25.4% TPR)
  - [x] Lakera_mosscap (obfuscated, 60.4% TPR)
  - [x] Mindgard_evaded (direct attacks, 100% TPR)
  - [x] TrustAIRLab_regular (benign, 24.2% FPR - contaminated dataset)
- [x] Label outcomes per prompt: TP (1,355), FN (645), FP (156), TN (344)
- [x] Extract candidate patterns from FN (missed attacks) and TP (caught attacks) prompts
- [x] **Output structured JSONL**: `reports/phase2_6/pattern_candidates_v1.jsonl`
  - Schema version: `pattern_candidates.v1`
  - One JSON object per pattern (see Pattern Discovery Schema section below)
  - Traceability: prompt IDs only (no raw text), git commit, run metadata
  - Evidence: FN/TP/FP/TN bucket counts per dataset, benign regression check
  - Metrics: fn_coverage_rate, fp_risk_score, priority_score (ranking formula)
  - Decision: recommendation (include/exclude/review), reason, implementation notes
- [ ] Rank patterns by `priority_score`: weighted formula (FN coverage high, FP risk low, rarity high)
- [x] Validate patterns against Clean_Benign_Corpus_v1 (0 FP hits on top patterns)
- [x] Generate comprehensive analysis: `reports/phase2_6/Pattern_Discovery_Report.md`
- [x] **FP Analysis:** Identified double-edged patterns (top FN patterns also top FP triggers)

**⚠️ CRITICAL FINDING:** Pattern discovery revealed that top pattern candidates ("Act as", "pretend", "roleplay") are **double-edged swords** - they appear in both FN (attacks missed) and FP (benign blocked). Adding these to deterministic layer would violate Gate A (FPR >2%). These patterns require **intent classification**, not keyword matching, validating Phase 3.5 intent layer justification.

**DECISION:** Skip remaining Phase 2.6 steps. No viable deterministic patterns found. Proceed to Phase 3 adversarial testing.

#### Step 2: Pattern Categorization & Prioritization ❌ **SKIPPED**
- [ ] Load `pattern_candidates_v1.jsonl` (structured input from Step 1)
- [ ] Parse and validate schema (check `schema_version`, required fields, enum values)
- [ ] Group by `pattern.pattern_type` (system_marker, control_phrase, credential_token, boundary_testing)
- [ ] Calculate detection lift per pattern: `evidence.datasets[].outcome_buckets.false_negative` (xTRam1 focus)
- [ ] Rank by `metrics.priority_score` (pre-computed formula: FN coverage high, FP risk low, rarity high)
- [ ] Filter: `decision.recommendation=include` AND `metrics.fp_risk_score < threshold` patterns proceed to Step 3
- [ ] Document decisions in `Phase_2_6_Pattern_Discovery_Report.md` with traceable `pattern.pattern_id` references

#### Step 3: Deterministic Rule Implementation
- [ ] Create `src/Deterministic_Guardrails_Enhanced.py` (or update existing)
- [ ] Add pattern categories as separate functions:
  - `check_system_markers(text) -> int` (returns signal strength: 0-3, see scoring table)
  - `check_credential_patterns(text) -> int`
  - `check_control_phrases(text) -> int`
  - `check_boundary_testing(text) -> int` (weak signal, 0-1 only)
- [ ] Implement signal combination logic (see Signal Strength Scoring table):
  - Score 3 (any category) → high_risk
  - Score 2+2 (two categories) → high_risk
  - Score 2+1 (strong + weak) → medium_risk
  - Score 1 alone → no escalation
  - Score 0 → no signal
- [ ] Enforce precedence rule: deterministic escalates, never downgrades semantic verdict
- [ ] Enforce invariant: always return explicit action (ALLOW/SANITIZE/BLOCK), never UNKNOWN
- [ ] Maintain explainability (log which patterns triggered + signal strengths)

#### Step 4: Integration & Testing
- [ ] Update `OWASP_Pipeline_Guardrail.py` to use enhanced rules
- [ ] Ensure deterministic layer runs BEFORE semantic model
- [ ] Re-run clean benign corpus evaluation (verify FPR ≤ 1.5%)
- [ ] Run attack datasets (measure TPR improvement, especially xTRam1)

#### Step 5: Evaluation & Documentation
- [ ] Create `Phase_2_6_Evaluation_Report.md`
  - Before/after TPR comparison (by dataset)
  - FPR regression check (clean corpus)
  - Pattern effectiveness analysis (which patterns caught most attacks)
  - Latency impact (deterministic is fast, but measure anyway)
- [ ] Update `WORK_LOG` with Phase 2.6 findings
**Success Criteria:**
- ✅ **Gate A (FPR):** FPR remains ≤ 2.0% on Clean_Benign_Corpus_v1 (CI blocker)
- ✅ **Gate B (Coverage):** xTRam1 TPR improves from 25.4% → ≥40% (+15pp minimum)
- ✅ Mean TPR improves from 66.6% → ≥71% (+5pp minimum)
- ✅ All rules are deterministic (no ML, no rewriting)
- ✅ Each rule has documented rationale + test case
- ✅ Pattern strength classification documented (strong vs weak signals)
- ✅ **Layer precedence enforced:** Deterministic escalates only, never downgrades semantic
- ✅ **No silent allow invariant:** Every prompt receives explicit action (ALLOW/SANITIZE/BLOCK)
- ✅ Signal scoring table used consistently (0=none, 1=weak, 2=clear, 3=malicious)
- ✅ **Pattern discovery schema v1 enforced:** All patterns traceable via `pattern.pattern_id` to JSONL evidence
- ✅ **No vibes-based patterns:** Every pattern has `evidence.datasets[].outcome_buckets`, `metrics.fp_risk_score`, `decision.reason`
- ✅ **Schema validation:** JSONL passes `schema_version=pattern_candidates.v1` contract, all required fields present, enums valid

**Out of Scope:**
- ❌ ML-based rewriting or paraphrasing
- ❌ LLM intent classification (that's Phase 2.5)
- ❌ Dynamic policies or reasoning guardrails (that's Phase 5.5)
- ❌ Multi-turn state tracking (that's Phase 3)

**Estimated Duration:** 3-5 days (includes pattern discovery, implementation, evaluation)

**Files to Create:**
- `scripts/analysis/Pattern_Discovery_Pipeline.py` (structured pattern extraction with schema v1)
- `docs/reports/phase2_6/pattern_candidates_v1.jsonl` (structured output, one pattern per line)
- `docs/reports/Phase_2_6_Pattern_Discovery_Report.md` (populated from JSONL)
- `docs/reports/Phase_2_6_Evaluation_Report.md`

---

### **Pattern Discovery Schema v1 (JSONL) — Hybrid Production Grade**

**File:** `docs/reports/phase2_6/pattern_candidates_v1.jsonl`  
**Format:** One JSON object per line (JSONL)  
**Sort:** Descending by `metrics.priority_score`, then descending by `evidence.datasets[].outcome_buckets.false_negative`, then ascending by `evidence.benign_regression.match_count_total`  
**Contract:** "Each record represents one candidate pattern with dataset-backed evidence, FN/TP/FP/TN bucket counts, benign regression matches, computed priority metrics, structured implementation guidance, and an include/exclude/review recommendation—without storing raw prompt text."

#### **Complete Schema Example:**
```jsonl
{
  "schema_version": "pattern_candidates.v1",
  "pattern_id": "SYS_001",
  "category": "system_marker",

  "pattern": {
    "value": "<<sys>>",
    "normalized_value": "<<sys>>",
    "pattern_kind": "literal",
    "regex": null,
    "case_sensitive": false,
    "token_boundary": false,
    "signal_strength": "strong",
    "severity_hint": "high_risk"
  },

  "evidence": {
    "datasets": [
      {
        "dataset_name": "TrustAIRLab_xTRam1",
        "split": "test",
        "eval_log_path": "reports/evals/eval_20251213_073707_TrustAIRLab_xTRam1.jsonl",
        "sample_count_total": 500,
        "match_count_total": 37,
        "outcome_buckets": {
          "true_positive": 0,
          "false_negative": 37,
          "false_positive": 0,
          "true_negative": 0
        },
        "example_prompt_ids": [12, 88, 104, 233, 411]
      }
    ],
    "benign_regression": {
      "dataset_name": "Clean_Benign_Corpus_v1",
      "eval_log_path": "reports/evals/eval_20251213_073707_Clean_Benign_Corpus_v1.jsonl",
      "sample_count_total": 200,
      "match_count_total": 0,
      "example_prompt_ids": []
    }
  },

  "run": {
    "eval_run_id": "eval_20251213_073707",
    "timestamp_utc": "2025-12-13T07:37:07Z",
    "git_commit": "abcdef1234567890",
    "script": "scripts/analysis/Pattern_Discovery_Pipeline.py",
    "model": {
      "name": "protectai/deberta-v3-base-prompt-injection-v2",
      "version": "pinned-or-hash-if-known"
    },
    "guardrail": {
      "entrypoint": "src/OWASP_Pipeline_Guardrail.py::run_guardrail",
      "policy_version": "phase2.6-pre"
    }
  },

  "metrics": {
    "fn_coverage_rate": 0.074,
    "tp_support_rate": 0.0,
    "fp_risk_score": 0.0,
    "rarity_score": 0.88,
    "priority_score": 0.93
  },

  "decision": {
    "recommendation": "include",
    "requires_review": false,
    "reason": "Appears in xTRam1 false negatives; zero matches in Clean_Benign_Corpus_v1."
  },

  "implementation": {
    "target_function": "check_system_markers",
    "suggested_action": "escalate",
    "suggested_risk": "high_risk",
    "notes": "Strong signal; count as 2 points in signal scoring."
  },

  "created_at": "2025-12-13T08:12:14Z"
}
```

#### **Schema Field Definitions (Canonical):**

**Top-Level (Required):**
- `schema_version` (string): Always `"pattern_candidates.v1"`
- `pattern_id` (string): Stable ID with category prefix: `SYS_###`, `CTRL_###`, `CRED_###`, `BND_###`, `ROLE_###`, `ENC_###`, `OTH_###`
- `category` (string enum): Pattern category for grouping/filtering

**pattern (object):**
- `value` (string): Literal string or human-readable representation
- `normalized_value` (string): Lowercased/trimmed version (matching basis)
- `pattern_kind` (enum): `"literal" | "regex" | "keyword_set"`
- `regex` (string|null): Regex if used; else null
- `case_sensitive` (bool): Whether pattern match is case-sensitive
- `token_boundary` (bool): Whether word boundaries required
- `signal_strength` (enum): `"weak" | "strong"`
- `severity_hint` (enum): `"low_risk" | "medium_risk" | "high_risk"`

**evidence (object):**
- `datasets` (array of objects): Evidence per dataset (supports multi-dataset patterns)
  - `dataset_name` (string): Exact identifier used in reports (e.g., `TrustAIRLab_xTRam1`)
  - `split` (string): `"train" | "test" | "eval" | "unknown"`
  - `eval_log_path` (string): Path to eval log file following convention: `reports/evals/eval_{YYYYMMDD_HHMMSS}_{DATASET}.jsonl`
  - `sample_count_total` (int): Total prompts in dataset
  - `match_count_total` (int): Prompts matching pattern
  - `outcome_buckets` (object of int): Counts by pipeline outcome: `true_positive`, `false_negative`, `false_positive`, `true_negative`
  - `example_prompt_ids` (array[int]): Sample prompt IDs (no raw text)
- `benign_regression` (object): Regression check against clean corpus
  - `dataset_name` (string): `"Clean_Benign_Corpus_v1"`
  - `eval_log_path` (string): Path to clean corpus eval log
  - `sample_count_total` (int): 200
  - `match_count_total` (int): Matches in clean corpus (FP risk indicator)
  - `example_prompt_ids` (array[int]): IDs of false positives

**run (object):**
- `eval_run_id` (string): Unique identifier for evaluation run (format: `eval_{YYYYMMDD_HHMMSS}`)
- `timestamp_utc` (string): ISO8601 UTC timestamp when pattern was discovered
- `git_commit` (string): Git commit SHA when generated (or "unknown")
- `script` (string): Script path that produced the file
- `model.name` (string): Model used by guardrail (e.g., ProtectAI v2)
- `model.version` (string): Pin/tag/hash if available
- `guardrail.entrypoint` (string): Function called to evaluate prompts
- `guardrail.policy_version` (string): e.g., "phase2.6-pre", "phase2.6-post"

**metrics (object):**
- `fn_coverage_rate` (float 0-1): `match_count_in_FN / total_FN_in_dataset` (xTRam1 lift indicator)
- `tp_support_rate` (float 0-1): `match_count_in_TP / total_TP_in_dataset` (validation metric)
- `fp_risk_score` (float 0-1): Derived from benign corpus matches (0.0 = best, no FP risk)
- `rarity_score` (float 0-1): Preference for specific patterns (not generic words)
- `priority_score` (float 0-1): Final ranking score (weighted: FN coverage high, FP risk low, rarity high)

**decision (object):**
- `recommendation` (enum): `"include" | "exclude" | "review"`
- `requires_review` (bool): True if risk is ambiguous (e.g., weak signal, medium FP risk)
- `reason` (string): One-line justification for decision

**implementation (object):**
- `target_function` (string enum): Which deterministic function should implement this pattern
- `suggested_action` (string enum): Recommended behavior when pattern matches
- `suggested_risk` (string enum): Risk level to assign when pattern triggers
- `notes` (string): Implementation guidance (e.g., "count as 2 points in signal scoring")

**created_at (string):**
- ISO8601 UTC timestamp when record was created

#### **Required Enums (Code Constants):**
```python
CATEGORIES = {
  "system_marker", "control_phrase", "credential_like",
  "boundary_testing", "role_confusion", "encoding_obfuscation", "other"
}

PATTERN_KINDS = {"literal", "regex", "keyword_set"}

SIGNAL_STRENGTH = {"weak", "strong"}

SEVERITY_HINT = {"low_risk", "medium_risk", "high_risk"}

RECOMMENDATION = {"include", "exclude", "review"}

OUTCOME_BUCKETS = {"true_positive", "false_negative", "false_positive", "true_negative"}

TARGET_FUNCTIONS = {
  "check_system_markers", "check_control_phrases", "check_credential_patterns",
  "check_boundary_testing", "check_role_confusion", "check_encoding_obfuscation", "check_other"
}

SUGGESTED_ACTIONS = {"escalate", "score_only", "log_only"}

SUGGESTED_RISKS = {"none", "low_risk", "medium_risk", "high_risk"}
```

#### **Eval Log Path Convention (Required):**
All `eval_log_path` values must follow:
```
reports/evals/eval_{YYYYMMDD_HHMMSS}_{DATASET}.jsonl
```
Example: `reports/evals/eval_20251213_073707_TrustAIRLab_xTRam1.jsonl`

#### **Pattern ID Convention (Required):**
Category-prefixed, sequential per category:
- `SYS_###` (system_marker)
- `CTRL_###` (control_phrase)
- `CRED_###` (credential_like)
- `BND_###` (boundary_testing)
- `ROLE_###` (role_confusion)
- `ENC_###` (encoding_obfuscation)
- `OTH_###` (other)

---

**Status:** Ready to start immediately

---

### 📋 Phase 3: Adversarial Testing & Attack-Side Hardening

**Purpose:** Systematically find and fix coverage gaps through red-teaming

**Why Initially Deferred:**
- 1.0% FPR acceptable for production (99% benign pass rate)
- Cost/benefit unfavorable for 1% → 0% improvement
- Engineering overkill for 2 edge case prompts

**Revised Purpose (Post-Phase 3 Decision):**
- **NOT for FPR reduction** (already solved)
- **FOR explainability** (SOC analyst understanding)
- **FOR coverage gaps** (attacks avoiding injection language)
- **FOR multi-step narratives** (reasoning over attack chains)

**New Justification Criteria:**
After Phase 3 adversarial testing, intent layer warranted if:
- ✅ Coverage gaps discovered (attacks with no keywords)
- ✅ Multi-turn attacks show state-tracking need
- ✅ Obfuscation attacks bypass deterministic + semantic layers
- ✅ Need explainability for security operations team
- ✅ Need reasoning over multi-step attack narratives

**Architecture (If Built):**
```python
# LLM-based intent classification for ambiguous cases
def classify_intent(prompt: str, semantic_result: dict, deterministic_result: dict, 
                   conversation_history: list = None) -> dict:
    """
    Uses GPT-4 or Claude to reason about:
    - Actual user intent (benign task vs attack attempt)
    - Multi-step attack narratives
    - Obfuscation detection
    - Explainability for SOC analysts
    
    **Triggering Rules (TIGHT CONTRACT - Keep Cost/Latency Bounded):**
    Only called when ONE of:
    1. Semantic confidence is ambiguous (0.4 ≤ jailbreak_prob ≤ 0.7)
    2. Layer conflict: deterministic=low_risk BUT semantic=malicious (or vice versa)
    3. Multi-turn risk score increases across conversation
    4. Coverage gap: attack style from ATTACK_TAXONOMY.md that bypasses layers 1+2
    
    **NOT a primary detector** - surgical use only for:
    - Explainability (SOC analyst summaries)
    - Ambiguity resolution (conflicting signals)
    - Multi-turn reasoning (state-dependent attacks)
    """
    # LLM reasoning prompt with few-shot examples
    # Returns: {
    #   "intent_label": "benign" | "suspicious" | "malicious",
    #   "confidence": float,
    #   "explanation": str,  # Natural language rationale for SOC
    #   "evidence": [...]    # Which signals triggered this conclusion
    # }
```

**Phase 3.5 Checklist (If Pursued):**

#### Prerequisites (Must Complete First)
- [ ] Phase 2.6 complete (deterministic enrichment)
- [ ] Phase 3 complete (adversarial testing)
- [ ] Coverage gap analysis shows need (not just nice-to-have)
- [ ] Attack taxonomy completed (maps which layer should catch what)
- [ ] **Accepted Risk category defined:** Won't-fix attacks documented in Coverage_Matrix.md
- [ ] **Layer precedence verified:** Intent layer cannot downgrade deterministic/semantic verdicts
- [ ] **No silent allow verified:** System invariant holds across all layers

#### Step 1: Intent Layer Design
- [ ] Define when intent layer triggers (confidence thresholds, signal combinations)
- [ ] Design LLM prompt for intent classification (few-shot examples, reasoning chain)
- [ ] Choose LLM (GPT-4, Claude 3.5 Sonnet, or similar reasoning model)
- [ ] Define output schema (intent label + explanation + confidence)

#### Step 2: Implementation
- [ ] Create `src/Intent_Classifier.py`
- [ ] Integrate with `OWASP_Pipeline_Guardrail.py` (after semantic layer)
- [ ] Add explainability logging (natural language rationale)
- [ ] Implement caching (avoid redundant LLM calls for similar prompts)

#### Step 3: Evaluation
- [ ] Test on Phase 3 coverage gaps (attacks that bypassed deterministic + semantic)
- [ ] Measure latency impact (LLM adds ~500ms-2s per call)
- [ ] Calculate cost per prompt (LLM API costs)
- [ ] Evaluate explainability quality (human review of reasoning)

#### Step 4: Decision
- [ ] Cost/benefit analysis (coverage improvement vs. latency/cost)
- [ ] Portfolio value analysis (demonstrates advanced reasoning guardrails)
- [ ] Documentation of decision (why built or why not)

**Success Criteria (If Built):**
- ✅ Catches attacks that bypass deterministic + semantic layers
- ✅ Provides actionable explainability for SOC team
- ✅ Latency acceptable (<2s per ambiguous prompt)
- ✅ Cost justified by coverage improvement

**Decision Point:** Revisit after Phase 3 adversarial testing

**Status:** Deferred, decision pending Phase 3 results

---

### 📋 Phase 3: Adversarial Testing & Attack-Side Hardening

**Purpose:** Systematically find and fix coverage gaps through red-teaming

**Why This Phase:**
- Current weakness: xTRam1 (25.4% TPR on novel attack styles)
- Need to document what ProtectAI v2 catches vs. doesn't catch
- Single-shot classifiers fail on multi-turn, obfuscated, and encoded attacks
- Real security = knowing your blind spots, not just having defenses

**Attack Vectors to Test:**

#### 1. Obfuscation Techniques
- Base64 encoding ("aWdub3JlIHByZXZpb3VzIGluc3RydWN0aW9ucw==")
- Unicode normalization (homoglyphs, zero-width characters)
- ROT13/Caesar cipher variants
- Leetspeak ("1gn0r3 pr3v10us 1nstruct10ns")
- Mixed-language attacks (English keywords in non-English text)

#### 2. Multi-Turn Attacks
- Progressive instruction buildup (spread attack across conversation)
- Context manipulation (establish trust, then inject)
- Slow-burn jailbreaks (gradual boundary erosion)
- State-dependent attacks (only malicious after specific history)

#### 3. Novel Attack Styles (xTRam1 Coverage)
- Attacks avoiding injection keywords entirely
- Indirect instruction attempts ("help me understand how to...")
- Hypothetical framing ("in a fictional world where...")
- Socratic jailbreaks (leading questions)

#### 4. Encoding Tricks
- HTML entity encoding (`&lt;system&gt;`)
- URL encoding (`%69%67%6E%6F%72%65`)
- Unicode escape sequences (`\u0069\u0067\u006E\u006F\u0072\u0065`)
- Markdown/code block hiding

#### 5. Cross-Language Attacks
- English instructions in Chinese/Arabic/Russian text
- Translation attacks (ask for translation of malicious text)
- Code-switching mid-attack

**Phase 3 Checklist:**

#### Step 1: Baseline Coverage Documentation (Week 1)
- [ ] Create `docs/reports/Coverage_Matrix.md`
- [ ] Document ProtectAI v2 strengths (what it catches reliably)
- [ ] Document known weaknesses (xTRam1 25.4% TPR, etc.)
- [ ] List untested attack vectors (multi-turn, obfuscation, encoding)

#### Step 2: Static Adversarial Datasets
- [ ] Load and benchmark on:
  - [ ] Lakera PINT benchmark
  - [ ] Mindgard jailbreak corpus
  - [ ] Giskard prompt_injections.csv
  - [ ] SPML Chatbot Prompt Injection dataset
  - [ ] Anthropic red-team dataset (if available)
- [ ] Create `scripts/evaluation/Eval_Adversarial_Datasets.py`
- [ ] Document TPR by attack category in `Coverage_Matrix.md`

#### Step 3: Dynamic Red-Teaming (HackAPrompt Companion)
- [ ] Use https://companion.injectprompt.com for:
  - [ ] Tailored attacks against guardrail design
  - [ ] Context-aware jailbreak generation
  - [ ] Novel attack style exploration
- [ ] Create `datasets/HackAPrompt_Custom_Attacks.jsonl` (50-100 prompts)
- [ ] Evaluate and document which attacks succeed

#### Step 4: Multi-Turn Attack Testing
- [ ] Design conversation-based attack test suite
- [ ] Test progressive instruction buildup
- [ ] Test context manipulation attacks
- [ ] Document: Does guardrail maintain state? Should it?
- [ ] Decision: Add multi-turn tracking or remain stateless?

#### Step 5: Pre-Semantic Normalization Layer (If Needed)
If obfuscation/encoding attacks succeed:
- [ ] Create `src/Input_Normalizer.py`:
  - [ ] Decode Base64 (detect and decode)
  - [ ] Normalize Unicode (homoglyph mapping)
  - [ ] Strip invisible characters (zero-width, control chars)
  - [ ] HTML entity decoding
- [ ] Insert normalization BEFORE deterministic + semantic layers
- [ ] Re-evaluate attack datasets (measure TPR improvement)

#### Step 6: Coverage Gap Remediation
For each discovered attack type that bypasses guardrails:
- [ ] Classify as: deterministic pattern, semantic model, or requires intent layer
- [ ] Implement fix in appropriate layer
- [ ] Re-test to verify coverage improvement
- [ ] Document residual risk (if no fix available)

**Attack Classification Categories:**
1. **Fixable (Deterministic):** Add pattern to Phase 2.6 enrichment
2. **Fixable (Semantic):** Model limitation, may need normalization layer or different model
3. **Fixable (Intent Layer):** Requires Phase 3.5 reasoning (ambiguity, multi-turn, obfuscation)
4. **Accepted Risk (Documented):** Attacks requiring full natural language reasoning across long conversational histories with no deterministic or semantic signals. These represent fundamental limitations of stateless, single-turn guardrails and are explicitly documented as out-of-scope.

**Accepted Risk Criteria (Won't Fix):**
- Attack requires multi-turn state tracking beyond Phase 3.5 scope
- No detectable patterns (deterministic, semantic, or intent-based)
- Attack success rate < 5% in adversarial testing
- Cost/complexity of fix exceeds portfolio value
- Explicitly documented in Coverage_Matrix.md with justification

**Purpose:** Bounds Phase 3.5 mandate to solvable problems, prevents scope creep into "solve all of NLP"

#### Step 7: Documentation & Portfolio
- [ ] Create `docs/reports/Phase_3_Adversarial_Testing_Report.md`:
  - Coverage matrix (attack type × detection layer × TPR)
  - Blind spots analysis (documented limitations)
  - Remediation decisions (what was fixed, what wasn't, why)
  - Residual risk assessment (known attacks that bypass system)
- [ ] Update `Coverage_Matrix.md` with final state
- [ ] Create visual: defense-in-depth layer effectiveness diagram
- [ ] **Create `docs/reports/ATTACK_TAXONOMY.md`:**
  - Map: Attack Style → Example → Which Layer Should Catch → Why
  - Identifies exactly what Phase 3.5 Intent Layer should handle
  - Prevents "let's add LLM because cool" — forces justification

**Success Criteria:**
- ✅ xTRam1 TPR improves to >50% (from 25.4%)
- ✅ Mean TPR across all datasets >80%
- ✅ All attack categories tested (obfuscation, multi-turn, encoding, novel styles)
- ✅ Coverage matrix fully documented (what's caught, what's not, why)
- ✅ Blind spots explicitly documented (no "security by obscurity")
- ✅ FPR regression check (still ≤ 2% on clean corpus)
- ✅ **Accepted Risk category defined** (won't-fix attacks documented with justification)

**Decision Point:** After Phase 3, decide if intent layer (Phase 3.5) is needed for coverage gaps

**Estimated Duration:** 1-2 weeks (includes dataset collection, testing, remediation)

**Files to Create:**
- `scripts/evaluation/Eval_Adversarial_Datasets.py`
- `scripts/testing/Test_Obfuscation_Attacks.py`
- `scripts/testing/Test_MultiTurn_Attacks.py`
- `src/Input_Normalizer.py` (if needed)
- `datasets/HackAPrompt_Custom_Attacks.jsonl`
- `docs/reports/Coverage_Matrix.md`
- `docs/reports/ATTACK_TAXONOMY.md` (attack→layer mapping)
- `docs/reports/Phase_3_Adversarial_Testing_Report.md`

**Status:** Next after Phase 2.6

---

### ⏸️ Phase 3.5: Intent/Reasoning Layer (Deferred Until After Phase 3)

**Original Purpose (Phase 2.5):** LLM-based ambiguous case resolution for FPR reduction

**Why Initially Deferred:**
- 1.0% FPR acceptable for production (99% benign pass rate)
- Cost/benefit unfavorable for 1% → 0% improvement
- Engineering overkill for 2 edge case prompts

**Revised Purpose (Post-Phase 3 Decision):**
- **NOT for FPR reduction** (already solved)
- **FOR explainability** (SOC analyst understanding)
- **FOR coverage gaps** (attacks avoiding injection language)
- **FOR multi-step narratives** (reasoning over attack chains)

**New Justification Criteria:**
After Phase 3 adversarial testing, intent layer warranted if:
- ✅ Coverage gaps discovered (attacks with no keywords)
- ✅ Multi-turn attacks show state-tracking need
- ✅ Obfuscation attacks bypass deterministic + semantic layers
- ✅ Need explainability for security operations team
- ✅ Need reasoning over multi-step attack narratives

**Architecture (If Built):**
```python
# LLM-based intent classification for ambiguous cases
def classify_intent(prompt: str, semantic_result: dict, deterministic_result: dict, 
                   conversation_history: list = None) -> dict:
    """
    Uses GPT-4 or Claude to reason about:
    - Actual user intent (benign task vs attack attempt)
    - Multi-step attack narratives
    - Obfuscation detection
    - Explainability for SOC analysts
    
    **Triggering Rules (TIGHT CONTRACT - Keep Cost/Latency Bounded):**
    Only called when ONE of:
    1. Semantic confidence is ambiguous (0.4 ≤ jailbreak_prob ≤ 0.7)
    2. Layer conflict: deterministic=low_risk BUT semantic=malicious (or vice versa)
    3. Multi-turn risk score increases across conversation
    4. Coverage gap: attack style from ATTACK_TAXONOMY.md that bypasses layers 1+2
    
    **NOT a primary detector** - surgical use only for:
    - Explainability (SOC analyst summaries)
    - Ambiguity resolution (conflicting signals)
    - Multi-turn reasoning (state-dependent attacks)
    """
    # LLM reasoning prompt with few-shot examples
    # Returns: {
    #   "intent_label": "benign" | "suspicious" | "malicious",
    #   "confidence": float,
    #   "explanation": str,  # Natural language rationale for SOC
    #   "evidence": [...]    # Which signals triggered this conclusion
    # }
```

**Phase 3.5 Checklist (If Pursued):**

#### Prerequisites (Must Complete First)
- [ ] Phase 2.6 complete (deterministic enrichment)
- [ ] Phase 3 complete (adversarial testing)
- [ ] Coverage gap analysis shows need (not just nice-to-have)
- [ ] Attack taxonomy completed (maps which layer should catch what)
- [ ] **Accepted Risk category defined:** Won't-fix attacks documented in Coverage_Matrix.md
- [ ] **Layer precedence verified:** Intent layer cannot downgrade deterministic/semantic verdicts
- [ ] **No silent allow verified:** System invariant holds across all layers

#### Step 1: Intent Layer Design
- [ ] Define when intent layer triggers (confidence thresholds, signal combinations)
- [ ] Design LLM prompt for intent classification (few-shot examples, reasoning chain)
- [ ] Choose LLM (GPT-4, Claude 3.5 Sonnet, or similar reasoning model)
- [ ] Define output schema (intent label + explanation + confidence)

#### Step 2: Implementation
- [ ] Create `src/Intent_Classifier.py`
- [ ] Integrate with `OWASP_Pipeline_Guardrail.py` (after semantic layer)
- [ ] Add explainability logging (natural language rationale)
- [ ] Implement caching (avoid redundant LLM calls for similar prompts)

#### Step 3: Evaluation
- [ ] Test on Phase 3 coverage gaps (attacks that bypassed deterministic + semantic)
- [ ] Measure latency impact (LLM adds ~500ms-2s per call)
- [ ] Calculate cost per prompt (LLM API costs)
- [ ] Evaluate explainability quality (human review of reasoning)

#### Step 4: Decision
- [ ] Cost/benefit analysis (coverage improvement vs. latency/cost)
- [ ] Portfolio value analysis (demonstrates advanced reasoning guardrails)
- [ ] Documentation of decision (why built or why not)

**Success Criteria (If Built):**
- ✅ Catches attacks that bypass deterministic + semantic layers
- ✅ Provides actionable explainability for SOC team
- ✅ Latency acceptable (<2s per ambiguous prompt)
- ✅ Cost justified by coverage improvement

**Decision Point:** Revisit after Phase 3 adversarial testing

**Status:** Deferred, decision pending Phase 3 results

---

### 📋 Phase 4: Learning & Portfolio Development

**Purpose:** Polish documentation and showcase systematic security engineering methodology

**Why This Phase:**
- Transform work logs into portfolio-ready case studies
- Demonstrate measurement-driven decision making
- Show understanding of defense-in-depth architecture
- Create reference material others wish existed

**Phase 4 Checklist:**

#### Step 1: Documentation Audit
- [ ] Review all work logs for completeness
- [ ] Ensure every decision has documented rationale
- [ ] Add "why not X?" sections (show alternatives considered)
- [ ] Create decision tree diagrams (visual representation of choices)

#### Step 2: Portfolio Case Studies
- [ ] **Case Study 1:** Model Selection Crisis
  - Problem: 93.6% FPR with madhurjindal model
  - Investigation: Probability extraction validation, model benchmarking
  - Solution: ProtectAI v2 swap → 1.0% FPR
  - Lesson: Model selection is biggest lever in ML systems
- [ ] **Case Study 2:** Ground Truth Dataset Construction
  - Problem: TrustAIRLab "benign" dataset contaminated
  - Solution: Build clean 200-prompt corpus, manual curation
  - Validation: 1.0% FPR measurement (vs. 24.2% on noisy dataset)
  - Lesson: Can't measure what you can't trust
- [ ] **Case Study 3:** Cost/Benefit Decision Making
  - Problem: 1.0% FPR - is semantic intent layer justified?
  - Analysis: 1% → 0% improvement vs. latency/cost/complexity
  - Decision: Skip for FPR, defer for coverage gaps
  - Lesson: Engineering discipline = knowing when not to build

#### Step 3: Visual Documentation
- [ ] Architecture diagram (defense-in-depth layers)
- [ ] Coverage matrix heatmap (attack type × layer × effectiveness)
- [ ] Decision tree (model selection, layer addition, pattern enrichment)
- [ ] Before/after metrics visualization (FPR, TPR improvement)

#### Step 4: Reproducibility Documentation
- [ ] Ensure all evaluation scripts are runnable
- [ ] Document exact model versions and parameters
- [ ] Create `REPRODUCTION_GUIDE.md` with step-by-step instructions
- [ ] Verify clean git history (meaningful commits, no secrets)

#### Step 5: Learning Reflections
- [ ] Document what you'd do differently (with hindsight)
- [ ] Explain biggest surprises (unexpected findings)
- [ ] Describe skill gaps filled (before/after comparison)
- [ ] List open questions (future research directions)

**Deliverables:**
- [ ] `PORTFOLIO_CASE_STUDIES.md` (3 case studies)
- [ ] `ARCHITECTURE_OVERVIEW.md` (visual + narrative)
- [ ] `REPRODUCTION_GUIDE.md` (step-by-step)
- [ ] `LESSONS_LEARNED.md` (reflections)
- [ ] Presentation slides (optional, for portfolio)

**Success Criteria:**
- ✅ Documentation tells coherent story (problem → investigation → solution → validation)
- ✅ Decisions have clear rationale (not just "it seemed right")
- ✅ Experiments are reproducible (someone else can run and verify)
- ✅ Portfolio-ready (can show to employers/collaborators)

**Estimated Duration:** 3-5 days (polish existing work, not new research)

**Status:** After Phase 3 complete

---

### 📋 Phase 5: OWASP AI Top 10 Mapping (Optional Learning Module)

**Purpose:** Understand recognized security frameworks (educational, not compliance)

**Why This Phase:**
- Learn structured threat modeling methodology
- Understand how guardrails map to standard frameworks
- Create reference documentation (portfolio piece)
- Build security framework literacy

**OWASP AI Top 10 (2023):**
1. **LLM01: Prompt Injection** — Malicious inputs manipulating LLM behavior
2. **LLM02: Insecure Output Handling** — Downstream system vulnerabilities
3. **LLM03: Training Data Poisoning** — Manipulated training data
4. **LLM04: Model Denial of Service** — Resource exhaustion attacks
5. **LLM05: Supply Chain Vulnerabilities** — Third-party model/data risks
6. **LLM06: Sensitive Information Disclosure** — Unintended data leakage
7. **LLM07: Insecure Plugin Design** — Plugin/extension vulnerabilities
8. **LLM08: Excessive Agency** — Uncontrolled LLM actions
9. **LLM09: Overreliance** — Over-trusting LLM outputs
10. **LLM10: Model Theft** — Unauthorized model extraction

**Phase 5 Checklist:**

#### Step 1: Guardrail Coverage Mapping
- [ ] For each OWASP category, document:
  - Which guardrail layers address it (deterministic, semantic, intent)
  - How effective coverage is (full, partial, none)
  - Residual risks (what's not covered)
  - Justification for gaps (out of scope vs. need remediation)

#### Step 2: Threat Modeling
- [ ] Create threat model for each category:
  - Attack vectors applicable to your system
  - Mitigation strategies implemented
  - Detection capabilities
  - Response procedures (block, log, alert)

#### Step 3: Documentation
- [ ] Create `docs/reports/OWASP_AI_Top_10_Mapping.md`
- [ ] Visual coverage matrix (threat × layer × status)
- [ ] Gap analysis (what's not covered and why)

**Deliverables:**
- [ ] `OWASP_AI_Top_10_Mapping.md`
- [ ] Threat model documentation
- [ ] Coverage matrix visual

**Success Criteria:**
- ✅ All 10 categories analyzed
- ✅ Coverage gaps explicitly documented
- ✅ Demonstrates understanding of security frameworks

**Estimated Duration:** 2-3 days

**Status:** Optional, after Phase 4

---

### 📋 Phase 5.5: Reasoning Guardrails (Optional Advanced Topic)

**Purpose:** Policy-based control for agent actions and tool usage

**Why This Phase:**
- Beyond input filtering → control what agent can DO
- Tool-use governance (which tools allowed in which contexts)
- Multi-agent orchestration safety
- Dynamic policy enforcement

**Scope:**
- Tool-access restrictions (e.g., "no file deletion without confirmation")
- Data scope limitations (e.g., "only access public data")
- Action chaining policies (e.g., "no automated financial transactions")
- Context-dependent permissions (e.g., "elevated privileges require MFA")

**Phase 5.5 Checklist:**

#### Step 1: Policy Definition Framework
- [ ] Define policy schema (YAML/JSON for tool permissions)
- [ ] Create policy engine (`src/Policy_Agent.py`)
- [ ] Implement policy evaluation (before tool execution)

#### Step 2: Tool Registration
- [ ] Inventory all agent tools/actions
- [ ] Classify by risk level (low, medium, high, critical)
- [ ] Define default policies (conservative defaults)

#### Step 3: Policy Enforcement
- [ ] Integrate with agent execution loop
- [ ] Add policy check before tool invocation
- [ ] Log policy decisions (allowed/denied + reason)

#### Step 4: Dynamic Policies
- [ ] Context-aware policies (user role, data sensitivity, time of day)
- [ ] State-dependent policies (require confirmation for chained actions)
- [ ] Breakglass procedures (emergency override + audit logging)

**Deliverables:**
- [ ] `src/Policy_Agent.py`
- [ ] `policies/tool_access_policies.yaml`
- [ ] `docs/reports/Reasoning_Guardrails_Design.md`

**Success Criteria:**
- ✅ All agent tools governed by policies
- ✅ Policy violations logged and blocked
- ✅ Demonstrates understanding of action-level security

**Estimated Duration:** 1 week

**Status:** Optional, advanced topic

---

### 📋 Phase 6: Custom Guardrail Linter (Optional Meta-Guardrail)

**Purpose:** Static analysis tool to prevent insecure guardrail code

**Why This Phase:**
- Prevent guardrail bypasses at development time
- Enforce architectural patterns (pipeline ordering)
- Catch dangerous patterns (eval, subprocess, raw logging)
- Meta-guardrail: security for security code

**Enforced Rules:**
- ✅ Pipeline ordering (ingestion → classification → sanitization → logging → policy)
- ✅ No raw input leakage (raw never in logs, never to agent)
- ✅ No guardrail bypass (all agent-facing code through `final_agent_input`)
- ✅ Dangerous pattern detection (`eval`, unsafe `subprocess`, string concat for commands)
- ✅ Policy validation (new tools must be registered with policy agent)

**Phase 6 Checklist:**

#### Step 1: Linter Design
- [ ] Choose AST analysis library (Python: `ast`, `libcst`, or `pylint` plugin)
- [ ] Define rule set (security checks + architectural patterns)
- [ ] Create `tools/guardrail_linter.py`

#### Step 2: Rule Implementation
- [ ] Pipeline ordering check
- [ ] Raw leakage detection
- [ ] Dangerous pattern scanning
- [ ] Policy coverage check

#### Step 3: Integration
- [ ] Pre-commit hook (run before git commit)
- [ ] CI/CD integration (GitHub Actions)
- [ ] IDE integration (optional, for real-time warnings)

#### Step 4: Documentation
- [ ] Rule documentation (what's checked, why, how to fix)
- [ ] False positive handling (how to suppress legitimate warnings)
- [ ] Contribution guide (how to add new rules)

**Deliverables:**
- [ ] `tools/guardrail_linter.py`
- [ ] `.pre-commit-config.yaml`
- [ ] `.github/workflows/lint.yml`
- [ ] `docs/LINTER_RULES.md`

**Success Criteria:**
- ✅ Catches all defined security anti-patterns
- ✅ Integrates seamlessly with development workflow
- ✅ Low false positive rate (<5%)

**Estimated Duration:** 3-5 days

**Status:** Optional, advanced topic

---

## 🎓 Learning Mastery Ladder

**Training Architecture** (from `Guardrail_Mastery_Ladder.md`):

Each stage requires **3 clean reps** to advance:

### 1️⃣ Pyramid Training (3× Full Runs)
Progressive rebuild: imports → types → signatures → logic → sanitization → wiring → test harness

### 2️⃣ Progressive Prompts (3×)
Incremental guided construction ("add function X", "implement rule Y")

### 3️⃣ Fill-in-the-Missing Parts (3×)
Complete partially written code (pattern recognition, structural understanding)

### 4️⃣ Broken Code Repair (3×)
Debug intentionally broken guardrail code (error detection, debugging instinct)

### 5️⃣ Blind Rewrite Challenges (3×)
Rewrite from memory, no hints (recall, structure, fluency)

### 6️⃣ Timed Rep Sets (3×)
Rebuild under time limits: 10 min → 7 min → 5 min (speed, clarity, confidence)

### 7️⃣ Generalization Phase (3×)
Apply architecture to new guardrail systems (PII leakage, tool-use, data exfiltration)  
**Goal:** Transferable skill, not memorization

---

## 📈 Success Metrics

### Technical Metrics
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| **FPR (Clean Corpus)** | ≤ 2.0% | 1.0% | ✅ Excellent |
| **TPR (Mean)** | ≥ 80% | 66.6% | 🔄 Improving (Phase 2.6, 3) |
| **TPR (TrustAIRLab_xTRam1)** | ≥ 50% | 25.4% | ❌ Weak (Phase 2.6, 3 focus) |
| **TPR (TrustAIRLab_jailbreak)** | ≥ 95% | 100% | ✅ Excellent |
| **TPR (TrustAIRLab_DarkWeb)** | ≥ 95% | 100% | ✅ Excellent |
| **Latency (p95)** | <100ms | TBD | 📋 Measure in Phase 3 |

### Portfolio Metrics
- ✅ Clean ground truth dataset built (200 prompts, manually curated)
- ✅ Systematic evaluation methodology documented (FPR/TPR measurement)
- ✅ Model selection crisis resolved (93.6% → 1.0% FPR)
- ✅ Cost/benefit analysis documented (intent layer decision)
- 🔄 Coverage matrix documented (attack type × layer × TPR)
- 📋 Adversarial testing completed (blind spots identified)
- 📋 Reproducible experiments (all evaluations runnable)

### Learning Metrics
- ✅ Measurement rigor (hypothesis testing with data)
- ✅ Defense-in-depth understanding (layered security model)
- ✅ Model selection impact (biggest lever in ML systems)
- ✅ Trade-offs documentation (complexity vs. improvement)
- 🔄 Adversarial testing frameworks (red-teaming methodology)
- 📋 Security framework literacy (OWASP AI Top 10)
- 📋 Reasoning guardrails (policy-based action control)

---

## 🚀 Next Steps Summary

### Immediate (This Week)
1. **Phase 2.6: Deterministic Enrichment** 🎯
   - Analyze TrustAIRLab_xTRam1 failures (find 75% bypass patterns)
   - Extract recurring patterns from ProtectAI v2 malicious detections
   - Implement enhanced deterministic rules (strong vs weak signal classification)
   - Pass Gate A (FPR ≤2%) and Gate B (xTRam1 +15pp, mean +5pp TPR)

### Short-Term (Next 2 Weeks)
2. **Phase 3: Adversarial Testing**
   - Benchmark on adversarial datasets (Lakera, Mindgard, Giskard)
   - Dynamic red-teaming with HackAPrompt Companion
   - Test obfuscation, multi-turn, encoding attacks
   - Document coverage matrix (what's caught, what's not)

3. **Phase 3.5 Decision: Intent/Reasoning Layer**
   - Review Phase 3 coverage gaps and ATTACK_TAXONOMY.md
   - Decide if intent layer warranted (explainability/coverage vs. complexity/cost)
   - Check triggering contract: ambiguity, conflicts, multi-turn, coverage gaps
   - If yes: implement surgical LLM reasoning layer (NOT primary detector)
   - If no: document why and what residual risks remain

### Medium-Term (Next Month)
4. **Phase 4: Portfolio Polish**
   - Create case studies (model selection crisis, ground truth construction, cost/benefit analysis)
   - Visual documentation (architecture diagrams, coverage matrix)
   - Ensure reproducibility (all scripts runnable, dependencies documented)
   - Learning reflections (what you'd do differently)

### Optional (As Time Allows)
5. **Phase 5: OWASP AI Mapping** (2-3 days)
6. **Phase 5.5: Reasoning Guardrails** (1 week)
7. **Phase 6: Custom Linter** (3-5 days)

---

## 📝 Key Decisions Log

| Date | Decision | Rationale | Outcome |
|------|----------|-----------|---------|
| 2025-12-12 | Model swap: madhurjindal → ProtectAI v2 | 93.6% FPR crisis, ProtectAI v2 best balance | FPR: 93.6% → 24.2% |
| 2025-12-13 | Build clean benign corpus (200 prompts) | TrustAIRLab "benign" contaminated with attacks | True FPR: 1.0% (validated) |
| 2025-12-13 | Skip semantic intent layer for FPR | 1% → 0% improvement not worth complexity | Focus on TPR instead |
| 2025-12-13 | Defer intent layer for coverage gaps | Revisit after Phase 3 adversarial testing | Decision pending Phase 3 |
| 2025-12-13 | Next: Phase 2.6 (deterministic enrichment) | Address TrustAIRLab_xTRam1 weakness (25.4% TPR) | Starting immediately |
| 2025-12-13 | Accepted Risk category for Phase 3 | Bounds Phase 3.5 scope to solvable problems | Won't fix: long multi-turn, no signals, <5% success |
| 2025-12-14 | Pattern discovery schema v1 (JSONL) | Prevent vibes-based pattern selection, enforce traceability, CI-ready | Full schema: run metadata, outcome_buckets (TP/FN/FP/TN), benign_regression, metrics (priority_score), decision (include/exclude/review) |

---025-12-13 | No silent allow invariant | All prompts get explicit action (ALLOW/SANITIZE/BLOCK) | Fail-closed by default |
| 2025-12-13 | Signal scoring table (0-3 explicit) | Prevents ambiguous interpretation, enables precise tests | Scoring: 0=none, 1=weak, 2=clear, 3=malicious |
| 2025-12-13 | Accepted Risk category for Phase 3 | Bounds Phase 3.5 scope to solvable problems | Won't fix: long multi-turn, no signals, <5% success |

---

## 🎯 Current Focus

**Phase 2.6: Deterministic Sanitization Enrichment**

**Goal:** Improve attack detection (TPR) by enriching deterministic patterns with Phase 2 intelligence

**Why Now:** TrustAIRLab_xTRam1 weakness (25.4% TPR), deterministic patterns should catch more attacks pre-semantic

**Timeline:** 3-5 days (pattern discovery → implementation → evaluation)

**Success:** TrustAIRLab_xTRam1 ≥40% TPR (+15pp), mean ≥71% TPR (+5pp), FPR ≤2% (Gate A+B)

---

## 📚 Key Documents Reference

| Document | Purpose | Location |
|----------|---------|----------|
| **PROJECT_ROADMAP.md** (this file) | Master checklist & progress tracker | Root |
| **README.md** | Project overview, quick start | Root |
| **QUICK_REFERENCE.md** | Common commands, file finder | Root |
| **AI_Guardrail_NorthStar (1).md** | Original vision document | `docs/planning/` |
| **WORK_LOG_Phase2_Semantic_Model_Selection.md** | Phase 2 detailed history | `docs/reports/` |
| **Clean_Benign_Corpus_Evaluation_Report.md** | 1.0% FPR validation report | `docs/reports/` |
| **STRATEGIC_ANALYSIS_FPR_And_Next_Steps.md** | FPR crisis analysis | `docs/reports/` |
| **ACTION_PLAN_Phase_2_5_Next_Steps.md** | Phase 2.5 code improvements | `docs/reports/` |
| **Phase_2_5_1_Sanitization_Enrichment_FULL (2).md** | Phase 2.6 specification (fka 2.51) | `docs/planning/` |

---

**Last Updated:** December 13, 2025  
**Next Review:** After Phase 2.6 completion (Gate A + Gate B pass)  
**Maintained By:** Project lead (you)  
**Status:** Living document, update after each phase milestone

---

## 🔧 Professional Fixes Applied

**Sanity Checks Completed:**
- ✅ Phase numbering: 2.51→2.6, 2.5→3.5 (chronological, no parent/child confusion)
- ✅ Measurement provenance: Standardized dataset names (TrustAIRLab_xTRam1, Clean_Benign_Corpus_v1)
- ✅ FPR regression prevention: Weak signals (boundary testing) only escalate when combined
- ✅ CI Gates: Gate A (FPR≤2%), Gate B (coverage lift +15pp xTRam1, +5pp mean)
- ✅ Intent layer contract: Tight triggering rules (ambiguity, conflicts, multi-turn only)
**Production-Grade Refinements:**
- ✅ **Signal scoring table:** Explicit 0-3 definitions (none/weak/clear/malicious)
- ✅ **Layer precedence rule:** Deterministic escalates only, never downgrades semantic (safety ratchet)
- ✅ **No silent allow invariant:** All prompts get explicit action, UNKNOWN = error (fail-closed)
- ✅ **Accepted Risk category:** Bounds Phase 3.5 scope (won't fix: long multi-turn, no signals, <5%)
- ✅ **Pattern discovery schema v1:** Full JSONL spec (run metadata, outcome_buckets, benign_regression, metrics, decision, notes)
- ✅ **Structured pattern pipeline:** Label (TP/FN/FP/TN) → Extract → Rank by priority_score → Validate → Emit JSONL → CI/reports
- ✅ **Traceability contract:** No raw prompt text in JSONL (prompt IDs + hashes only), git commit tracking, reproducible metrics
