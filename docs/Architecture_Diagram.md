# Architecture Diagram (Current State)

```
[User Prompt]
     |
     v
[Ingestion]
     |
     v
[Deterministic Guardrails]
  - Patterns: OWASP_PATTERNS (Agent Goal Hijack, Privilege Abuse, Code Exec, Context Poisoning)
  - Enrichments: persona/tool abuse, safety bypass, credential exfil, format injections
  - Obfuscation handling: leetspeak, ROT13/base64/hex/reverse normalization
  - Output: deterministic_risk, pattern_hits, OWASP codes
     |
     v
[Semantic Guardrail (ProtectAI DeBERTa prompt-injection)]
  - HF pipeline, 512-token truncation
  - Map model output -> jailbreak probability (semantic_result.score)
  - OWASP-aware escalation to critical
  - Output: semantic_result{label,score}, owasp_hits
     |
     v
[Risk Combiner]
  - Fail-safe: semantic malicious/critical overrides deterministic low_risk
  - Combined risk: critical | high | medium | low
     |
     v
[Sanitization + Policy]
  - If high/critical: block
  - If medium: sanitize + allow
  - If low: allow (sanitized = minimal)
  - agent_visible returned to downstream agent
     |
     v
[Logging]
  - deterministic_pattern_hits, semantic_label/score, combined_risk
  - OWASP codes/patterns, model name, sanitized preview
  - include_raw only if explicitly requested
```

Evaluation & Reporting
```
[Datasets]
  - Attack: Lakera, Mindgard, TrustAIRLab_jailbreak, xTRam1 (mixed)
  - Benign FPR gate: Clean_Benign_Corpus_v1
  - Adversarial curated: Adversarial_Pentest_v1 (attack-only)
     |
     v
[Eval Harness: scripts/evaluation/Eval.py]
  - Runs guardrail pipeline per prompt
  - Metrics per dataset: tp/fp/tn/fn, tpr/fpr
  - Logs: reports/evals/eval_*_<dataset>.jsonl
  - Summary: reports/phase_4_eval_results_*.json

[Adversarial Pentest: scripts/evaluation/Eval_Adversarial_Pentest.py]
  - Attack-only TPR
  - Missed examples with semantic/deterministic/OWASP details
  - Reports: reports/adversarial_pentest_*.json/.md
```

Dataset Hygiene
```
- Clean benign: datasets/Clean_Benign_Corpus_v1.jsonl (FPR gate)
- Noisy benign excluded from FPR: TrustAIRLab_regular_* (cleaned snapshot research-only)
- Contamination scan: scripts/analysis/Analyze_Dataset_Contamination.py
```
