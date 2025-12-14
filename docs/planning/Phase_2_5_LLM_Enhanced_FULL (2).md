# Phase 2.5 — LLM-Enhanced Semantic Guardrails (Concise Engineering Spec)

## 1. Purpose
Phase 2.5 upgrades the semantic layer from a placeholder to a real ML-based classifier using `madhurjindal/Jailbreak-Detector-Large`. It enhances detection of jailbreaks, prompt injection attempts, privilege abuse, code execution intent, and memory manipulation. This phase does not change pipeline architecture—only the internal logic of `semantic_classify_input`.

## 2. ML Integration
- Use Hugging Face model: `madhurjindal/Jailbreak-Detector-Large`
- Wrapper: `run_jailbreak_detector(text) -> (raw_label, raw_score)`
- Consumed via: `semantic_classify_input(text)`

## 3. Semantic Risk Mapping
| Condition | Output |
|----------|--------|
| BENIGN | benign |
| JAILBREAK & score < 0.60 | suspicious |
| JAILBREAK & 0.60–0.85 | malicious |
| JAILBREAK & ≥ 0.85 & no sensitive patterns | malicious |
| JAILBREAK & ≥ 0.85 & sensitive patterns | critical |

## 4. Sensitive Pattern Engine (OWASP-Aligned)
### ASI01 — Goal Hijack
- "ignore previous instructions"
- "override"
- "bypass safety"
- "reveal system prompt"

### ASI03 — Privilege Abuse
- "act as admin"
- "authenticate as"
- "run as root"

### ASI05 — Code Execution
- "run shell"
- "execute code"
- "eval"

### ASI06 — Memory Poisoning
- "remember this"
- "store this rule"
- "update your default"

Patterns serve as escalation triggers when paired with high ML confidence.

## 5. Combined Risk Behavior
Pipeline rules remain unchanged:
- critical/malicious → block  
- suspicious → sanitize  
- benign → allow  

## 6. Logging Requirements
Logs must include:
- deterministic_risk  
- semantic_label  
- semantic_score  
- combined_risk  
- sanitized_preview  
- **patterns_matched**  
- action  

## 7. Evaluation Requirements
- Manual high-risk prompts  
- Small slices of adversarial datasets (Lakera, Mindgard, TrustAIRLab, Giskard)  
- Tune thresholds and patterns based on misclassifications  

## 8. Out of Scope
- Reasoning guardrails  
- Tool governance  
- Identity/IAM  
- Memory isolation  
- Supply chain protections  
- Multi-agent security  

## 9. Summary
Phase 2.5 introduces the first true ML-powered semantic guardrail layer, aligned with OWASP high-impact risks, providing intent detection and severity scoring while maintaining deterministic transparency.
