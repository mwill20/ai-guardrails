# Phase 2.5.1 — Deterministic Sanitization Enrichment (Concise Engineering Spec)

## 1. Purpose
Enhance Phase 1 deterministic sanitization using Phase 2.5 insights and modern jailbreak datasets while keeping sanitization simple, deterministic, and transparent.

## 2. Why Enhancement Is Needed
Phase 1 sanitization is intentionally minimal. Phase 2.5 identifies patterns and tokens that occur frequently in adversarial prompts. Phase 2.5.1 converts these insights into improved deterministic rules.

## 3. Data-Driven Rule Discovery
Analyze:
- High-confidence malicious prompts  
- Dataset samples from Lakera PINT, Mindgard, TrustAIRLab, Giskard  
- Logs where semantic score is high or sensitive patterns matched  

Extract recurring literal patterns → refine deterministic rules.

## 4. Sanitization Rule Categories
### System/Prompt Markers
- "system prompt"
- "hidden instructions"
- "assistant:"
- "system:"

### Credential-Like Tokens
- Keys like `sk-...`
- AWS-style `AKIA...`
- `.env=` style secrets

### Control Phrases
- "override"
- "bypass safety"
- "ignore instructions"

Rules should remain predictable, minimal, and explainable.

## 5. Updated Phase 1 Principles
- Deterministic only  
- No paraphrasing or rewriting  
- Minimal but meaningful token removal  
- Guided by: ASI01, ASI03, ASI05, ASI06  

## 6. Architecture Placement
Improved sanitization still occurs *before* semantic classification:
```
raw → sanitize → semantic_risk → combined_risk
```

## 7. Evaluation
Ensure:
- Fewer malicious literals bypass sanitization  
- Minimal false positives  
- Semantics still functions correctly  

Adjust sanitization patterns as needed.

## 8. Out of Scope
Not included:
- ML-based sanitization  
- Text rewriting  
- Intent interpreters  
- Transformation layers  
- Reasoning guardrails  

## 9. Summary
Phase 2.5.1 introduces a feedback-driven method to evolve deterministic sanitization using real adversarial data. It keeps Phase 1 simple while improving security coverage and aligning with OWASP.
