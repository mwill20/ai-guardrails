# Pattern Discovery Report
**Phase 2.6: Deterministic Sanitization Enrichment**

**Date:** December 13, 2025  
**Author:** Project Lead  
**Purpose:** Data-driven pattern discovery for deterministic layer enrichment  
**Goal:** Improve TrustAIRLab_xTRam1 TPR from 25.4% → ≥40% without FPR regression

---

## 🎯 Discovery Methodology

**Data Sources:**
1. ProtectAI v2 high-confidence malicious predictions (jailbreak_prob > 0.9)
2. TrustAIRLab_xTRam1 failures (attacks that bypass current detection)
3. TrustAIRLab_jailbreak patterns (known attack language)
4. TrustAIRLab_DarkWeb patterns (adversarial queries)

**Pattern Selection Criteria:**
- **Frequency:** Appears in ≥5 malicious prompts (avoids one-offs)
- **Feasibility:** Deterministic/regex-friendly (no complex NLP required)
- **FP Risk:** Low benign usage (validate against Clean_Benign_Corpus_v1)
- **Signal Strength:** Clear malicious intent indicator (not just suspicious)

**Signal Classification Reference:**
| Score | Meaning | Interpretation | Example |
|-------|---------|----------------|----------|
| **0** | No signal | Pattern not detected | Clean prompt |
| **1** | Weak presence | Partial match or benign context | "imagine" alone |
| **2** | Clear match | Unambiguous pattern hit | "ignore instructions" |
| **3** | High-confidence malicious | Multiple patterns or strong indicator | "system:" + "override" |

**Quality Gates:**
- **Gate A (FPR):** FPR must remain ≤ 2.0% on Clean_Benign_Corpus_v1
- **Gate B (Coverage):** xTRam1 TPR must improve by ≥15pp (25.4% → ≥40%)

---

## 📊 Dataset Analysis Summary

| Dataset | Total Samples | Malicious Detections (>0.9) | Analyzed | Patterns Extracted |
|---------|---------------|----------------------------|----------|-------------------|
| TrustAIRLab_xTRam1 | TBD | TBD | TBD | TBD |
| TrustAIRLab_jailbreak | TBD | TBD | TBD | TBD |
| TrustAIRLab_xTRam2 | TBD | TBD | TBD | TBD |
| TrustAIRLab_DarkWeb | TBD | TBD | TBD | TBD |
| **Total** | **TBD** | **TBD** | **TBD** | **TBD** |

---

## 🔍 Pattern Discovery Table

### Category 1: System/Prompt Markers (High Priority - Strong Signals)

| Pattern Candidate | Frequency | Dataset(s) | Strong/Weak | FP Risk Notes | Decision | Rationale |
|-------------------|-----------|------------|-------------|---------------|----------|-----------|
| `"system prompt"` | TBD | TBD | Strong (2-3) | Low - rare in benign | ⏳ Pending | Direct system introspection attempt |
| `"hidden instructions"` | TBD | TBD | Strong (2-3) | Low - adversarial framing | ⏳ Pending | Explicit attack language |
| `"reveal your"` + `"prompt"` | TBD | TBD | Strong (3) | Low - meta-prompt attack | ⏳ Pending | Combined pattern increases confidence |
| `"show me your instructions"` | TBD | TBD | Strong (2-3) | Medium - rare benign "help" queries | ⏳ Pending | Validate against benign corpus |
| `"assistant:"` (role marker) | TBD | TBD | Strong (2) | Medium - some chat format examples | ⏳ Pending | Check benign technical discussions |
| `"system:"` (role marker) | TBD | TBD | Strong (3) | Low - direct role injection | ⏳ Pending | Classic injection marker |
| `"[INST]"` (Llama2 marker) | TBD | TBD | Strong (3) | Low - template injection | ⏳ Pending | Model-specific attack pattern |
| `"<<SYS>>"` (system tag) | TBD | TBD | Strong (3) | Low - template injection | ⏳ Pending | Model-specific attack pattern |
| `"<|im_start|>"` (ChatML) | TBD | TBD | Strong (3) | Low - template injection | ⏳ Pending | OpenAI format attack |
| `"###"` + `"Instruction:"` | TBD | TBD | Strong (2) | Medium - some benign docs use ### | ⏳ Pending | Context-dependent (check combinations) |

**Notes:**
- Validate all candidates against Clean_Benign_Corpus_v1 before inclusion
- Consider case-insensitive matching for robustness
- Role markers may need context (e.g., within quotes vs standalone)

---

### Category 2: Credential/Key Extraction Patterns (Medium Priority - Strong Signals)

| Pattern Candidate | Frequency | Dataset(s) | Strong/Weak | FP Risk Notes | Decision | Rationale |
|-------------------|-----------|------------|-------------|---------------|----------|-----------|
| `"sk-"` (OpenAI API key prefix) | TBD | TBD | Strong (3) | Low - rare in benign | ⏳ Pending | Direct key extraction attempt |
| `"AKIA"` (AWS access key prefix) | TBD | TBD | Strong (3) | Low - rare in benign | ⏳ Pending | Cloud credential extraction |
| `".env="` | TBD | TBD | Strong (2-3) | Medium - some dev tutorials | ⏳ Pending | Environment variable exposure |
| `"api_key="` / `"apikey="` | TBD | TBD | Strong (2) | Medium - common in docs | ⏳ Pending | Check for question vs injection context |
| `"secret_key"` | TBD | TBD | Strong (2) | Medium - common in docs | ⏳ Pending | Check for question vs extraction |
| `"bearer token"` | TBD | TBD | Strong (2) | Low - auth header reference | ⏳ Pending | Authorization extraction attempt |
| `"Authorization: Bearer"` | TBD | TBD | Strong (2-3) | Low - HTTP header injection | ⏳ Pending | Direct auth bypass attempt |
| `"password"` + `"="` | TBD | TBD | Strong (2) | High - very common benign usage | ⏳ Pending | Likely exclude - too common |

**Notes:**
- Credential patterns should be context-aware (requesting info vs providing it)
- Consider regex patterns for prefix matching (e.g., `sk-[A-Za-z0-9]+`)
- High FP risk patterns may need combination logic (weak signal alone)

---

### Category 3: Control Phrases (High Priority - Strong Signals)

| Pattern Candidate | Frequency | Dataset(s) | Strong/Weak | FP Risk Notes | Decision | Rationale |
|-------------------|-----------|------------|-------------|---------------|----------|-----------|
| `"ignore previous instructions"` | TBD | TBD | Strong (3) | Low - classic injection | ⏳ Pending | Canonical prompt injection phrase |
| `"ignore all instructions"` | TBD | TBD | Strong (3) | Low - classic injection | ⏳ Pending | Canonical prompt injection phrase |
| `"disregard"` + `"guidelines"` | TBD | TBD | Strong (2-3) | Low - adversarial intent | ⏳ Pending | Safety bypass language |
| `"bypass safety"` | TBD | TBD | Strong (3) | Low - explicit attack | ⏳ Pending | Direct safety system attack |
| `"override"` + `"restrictions"` | TBD | TBD | Strong (3) | Low - control bypass | ⏳ Pending | Classic jailbreak language |
| `"forget your rules"` | TBD | TBD | Strong (3) | Low - direct attack | ⏳ Pending | Rule reset attempt |
| `"new instructions:"` | TBD | TBD | Strong (2-3) | Medium - some benign use | ⏳ Pending | Instruction replacement attack |
| `"stop being"` + AI identity | TBD | TBD | Strong (2) | Low - identity override | ⏳ Pending | Jailbreak framing |
| `"you are now"` + role change | TBD | TBD | Strong (2) | Medium - some benign roleplay | ⏳ Pending | Check against creative writing corpus |
| `"from now on"` + behavior change | TBD | TBD | Strong (2) | Medium - some benign requests | ⏳ Pending | Context-dependent override |

**Notes:**
- Control phrases are highest-value patterns (direct attack intent)
- Many are already in deterministic layer - validate current coverage
- Consider phrase variations (e.g., "forget all rules", "ignore your rules")

---

### Category 4: Boundary Testing Language (Low Priority - WEAK SIGNALS ONLY)

| Pattern Candidate | Frequency | Dataset(s) | Strong/Weak | FP Risk Notes | Decision | Rationale |
|-------------------|-----------|------------|-------------|---------------|----------|-----------|
| `"for testing purposes"` | TBD | TBD | Weak (1) | **HIGH** - very common benign | ⏳ Pending | Only escalate with strong signals |
| `"in a hypothetical scenario"` | TBD | TBD | Weak (1) | **HIGH** - common in discussions | ⏳ Pending | Only escalate with strong signals |
| `"pretend that"` | TBD | TBD | Weak (1) | **HIGH** - creative writing, roleplay | ⏳ Pending | Only escalate with strong signals |
| `"roleplay as"` | TBD | TBD | Weak (1) | **HIGH** - legitimate creative use | ⏳ Pending | Only escalate with strong signals |
| `"simulate"` | TBD | TBD | Weak (1) | **HIGH** - technical discussions | ⏳ Pending | Only escalate with strong signals |
| `"imagine you are"` | TBD | TBD | Weak (1) | **HIGH** - creative writing | ⏳ Pending | Only escalate with strong signals |
| `"let's say"` | TBD | TBD | Weak (0-1) | **VERY HIGH** - everyday language | ❌ Exclude | Too common, no signal value |
| `"what if"` | TBD | TBD | Weak (0-1) | **VERY HIGH** - everyday language | ❌ Exclude | Too common, no signal value |

**⚠️ CRITICAL RULES FOR WEAK SIGNALS:**
- **NEVER trigger high_risk alone** (FPR disaster)
- **Only escalate when combined with Category 1, 2, or 3 patterns**
- **Must validate against Clean_Benign_Corpus_v1 with 0% FP tolerance**
- **If in doubt, exclude** - weak signals are optional, not required

---

## 🧪 False Positive Risk Analysis

### Validation Process:
1. **Pattern candidate identified** from attack datasets
2. **Grep search** across Clean_Benign_Corpus_v1 (200 prompts)
3. **Manual review** of any matches (context analysis)
4. **FP calculation:** (benign_matches / 200) × 100%
5. **Decision threshold:** 
   - Strong signals: ≤1% FP acceptable (2 prompts)
   - Weak signals: 0% FP required (0 prompts)

### High-Risk Patterns (Pre-Analysis):
| Pattern | Expected Benign Usage | Mitigation Strategy |
|---------|----------------------|---------------------|
| `"password"` | Very high (security docs) | Require context (extraction vs question) |
| `"for testing"` | High (legitimate testing) | Weak signal only, never alone |
| `"imagine"` | High (creative writing) | Weak signal only, never alone |
| `"roleplay"` | High (creative AI use) | Weak signal only, never alone |
| `"system"` | Medium (technical docs) | Require full phrase "system prompt" or "system:" |

---

## 📈 Expected Coverage Improvement

### Baseline (Current State):
- **TrustAIRLab_xTRam1 TPR:** 25.4% (18/71 detected)
- **Bypassed attacks:** 53 prompts (74.6%)
- **Mean TPR:** 66.6%

### Target (Post-Phase 2.6):
- **TrustAIRLab_xTRam1 TPR:** ≥40% (+15pp minimum)
- **Mean TPR:** ≥71% (+5pp minimum)
- **FPR (Clean Corpus):** ≤2.0% (currently 1.0%)

### Pattern Impact Estimation:
| Pattern Category | Estimated xTRam1 Coverage | FP Risk | Implementation Priority |
|------------------|---------------------------|---------|------------------------|
| System/Prompt Markers | +10-15pp (catch meta-attacks) | Low | **High** (implement first) |
| Control Phrases | +5-10pp (catch instruction overrides) | Low | **High** (implement first) |
| Credential Patterns | +2-5pp (catch extraction attempts) | Medium | Medium (validate thoroughly) |
| Boundary Testing (weak) | +0-2pp (only with strong signals) | High | Low (cautious implementation) |

**Note:** Conservative estimates assume deterministic patterns catch ~30-40% of xTRam1 novel attacks.

---

## 🚦 Decision Summary

### Patterns to Include (Strong Signals):
*To be filled after analysis*

**Count:** TBD  
**Rationale:** TBD

---

### Patterns to Include (Weak Signals - Combination Only):
*To be filled after analysis*

**Count:** TBD  
**Rationale:** TBD

---

### Patterns to Exclude:
*To be filled after analysis*

**Count:** TBD  
**Rationale:** TBD

---

## 🔄 Next Steps

1. **Run Eval.py** on all TrustAIRLab datasets, save detailed logs with prompts + predictions
2. **Extract patterns** from high-confidence malicious predictions (jailbreak_prob > 0.9)
3. **Frequency analysis** across attack datasets (sort by occurrence count)
4. **FP validation** against Clean_Benign_Corpus_v1 (grep + manual review)
5. **Populate this template** with actual data, frequencies, and decisions
6. **Implementation** in Deterministic_Guardrails_Enhanced.py (only validated patterns)
7. **Gate A check** (FPR ≤2% on clean corpus)
8. **Gate B check** (xTRam1 TPR ≥40%, mean TPR ≥71%)

---

## 📝 Analysis Notes

*Use this section to capture insights during pattern discovery:*

### Surprising Findings:
- TBD

### Pattern Families (Related Patterns):
- TBD

### xTRam1-Specific Attack Styles:
- TBD

### Potential Blind Spots (No Patterns):
- TBD

---

**Template Version:** 1.0  
**Last Updated:** December 13, 2025  
**Status:** Ready for analysis (Step 1 of Phase 2.6)
