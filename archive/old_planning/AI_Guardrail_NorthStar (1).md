# AI Guardrail NorthStar Roadmap

## Overview
This document outlines the complete end‑to‑end security roadmap for building production‑grade guardrails for AI agents. It covers deterministic guardrails, semantic guardrails, datasets, adversarial red-teaming, reasoning guardrails, compliance alignment, and a custom linter for guardrail policy enforcement.

---

## Phase 1 — Deterministic Guardrails (Foundational Pipeline)

### Purpose
Create a simple, explainable, fully deterministic guardrail pipeline that enforces predictable behavior before any semantic models are involved.

### 5-Stage Deterministic Pipeline

1. **Ingestion — `get_raw_input(text)`**  
   Captures untrusted input exactly as the user typed it.  
   Stores it in `raw`.

2. **Classification — `classify_input(text)`**  
   Deterministically labels input as:  
   - `"high_risk"` if it contains both `system:` and `override`  
   - `"medium_risk"` if it contains `system:` but not `override`  
   - `"low_risk"` otherwise  

3. **Sanitization — `sanitize_input(text)`**  
   Removes obvious malicious tokens such as `system:` and `override`.

4. **Safe Logging — `build_log_entry(raw, risk, sanitized)`**  
   Logs metadata only:  
   - risk label  
   - length of raw input  
   - 20‑character preview of sanitized text  
   - action (`allowed` or `blocked`)  
   *Raw input is never logged.*

5. **Final Policy — `final_agent_input(raw, risk, sanitized)`**  
   Decides what the agent sees:  
   - Block (generic message)  
   - Warn + sanitized  
   - Sanitized only  

---

## Phase 2 — Semantic Guardrails (Model-Based Safety Layer)

### Purpose
Augment deterministic guardrails with ML-based classifiers that detect risky patterns beyond simple rules.

### Planned Semantic Classifiers
- `madhurjindal/Jailbreak-Detector-Large`
- `protectai/deberta-v3-small-prompt-injection-v2`
- `xTRam1/safe-guard-classifier`
- `meta-llama/Llama-Prompt-Guard-2-86M`
- `Intel/toxic-prompt-roberta`
- Google ShieldGemma classifiers

### Semantic Risk Labels
- `benign`
- `suspicious`
- `malicious`
- `critical`

Semantic classification runs *after* deterministic classification and influences policy decisions.

---

## Phase 3 — Semantic Datasets + Adversarial Red-Teaming

### Purpose
Evaluate, benchmark, and red‑team guardrails with realistic attack data.

### Static Evaluations Datasets
- Mindgard: Evaded Prompt Injections & Jailbreaks  
- Giskard: `prompt_injections.csv`  
- xTRam1: `safe-guard-prompt-injection`  
- Lakera PINT benchmark  
- TrustAIRLab jailbreak prompts  
- SPML Chatbot Prompt Injection dataset  
- Anthropic red-team dataset  

### Dynamic Red-Team Source  
**HackAPrompt’s Companion — https://companion.injectprompt.com**  
Used to generate:
- tailored prompt injection attempts  
- unique jailbreak variations  
- context-aware attacks against your specific agent design  

### Usage Modes
- Dataset augmentation (“Custom_Attacks” dataset)  
- Feeding evaluation harnesses  
- Regression testing guardrails  
- Human‑in‑the‑loop adversarial learning  

---

## Phase 4 — Learning & Portfolio Development

### Purpose
This is a **learning project**, not production deployment. Focus on mastery, documentation, and reproducible experiments rather than operational concerns.

### Focus Areas

**Measurement Mastery:**
- Building clean ground truth datasets (benign corpus creation)
- Systematic evaluation methodologies (FPR, TPR measurement)
- Manual review processes (TP/FP classification)
- Metric validation (hypothesis testing with data)

**Documentation Excellence:**
- Comprehensive work logs (decision rationale, not just results)
- Reproducible experiments (version-controlled, runnable)
- Technical depth (explain why, not just what)
- Portfolio-ready outputs (showcase problem-solving process)

**Architectural Understanding:**
- Defense in depth (layered security model)
- Model selection impact (biggest lever in ML systems)
- Trade-offs analysis (complexity vs improvement)
- Fail-closed design (conservative security defaults)

**Advanced Topics (Optional):**
- Agent reasoning guardrails (policy agents, tool restrictions)
- Multi-agent orchestration safety
- Adversarial testing frameworks
- Ensemble detection methods

### Learning Advantages

**What you DON'T need to worry about:**
- ❌ Production latency / SLA requirements
- ❌ Cost at scale (millions of requests)
- ❌ Incremental rollout / A-B testing
- ❌ Legal compliance (SOC2, GDPR)
- ❌ User support / appeal processes

**What you CAN focus on:**
- ✅ Experiment freely (try, measure, iterate)
- ✅ Use expensive models (learning cost is worth it)
- ✅ Perfect your methodology (do it right, not fast)
- ✅ Document everything (build reference others wish existed)
- ✅ Understand deeply (why things work, not just that they work)

---

## Phase 5 — OWASP AI Top 10 Mapping (Optional Learning Module)

### Purpose
Understand how guardrails map to recognized security frameworks (learning exercise, not compliance requirement).

### Activities
- Map implemented guardrails to OWASP AI Top 10 threat categories  
- Document which threats are mitigated vs not covered
- Understand security framework thinking (structured threat modeling)
- Produce mapping documentation (portfolio piece)

**Note:** This is educational, not for production compliance. Focus on understanding security frameworks, not meeting audit requirements.

---

## Phase 6 — Custom Guardrail Linter (Static Protection Layer)

### Purpose
Prevent insecure code or policies from ever making it into the runtime pipeline.

### Enforced Rules

#### Pipeline Ordering
- ingestion → classification → sanitization → logging → policy  

#### No Raw Leakage
- raw input may not appear in logs  
- raw input may not reach the agent  

#### No Guardrail Bypass
- All agent‑facing code must go through `final_agent_input`  

#### Dangerous Pattern Detection
- Block or warn on:  
  - `eval`  
  - unsafe `subprocess` usage  
  - insecure string concatenation for commands  
  - missing sanitization or missing policy checks  

#### Policy & Config Validation
- New tools/actions must be registered with the policy agent  
- Sensitive tools require explicit guardrail approval  

### Execution Points
- As a pre‑commit hook  
- As a GitHub Actions CI step  
- As a static analysis tool over agent configs  

This linter creates a “meta‑guardrail” around everything else.

---

## Combined Guardrail Architecture

```
              [ Phase 6 — Custom Linter (Optional) ]
                  (static analysis for learning)

                     ┌─────────────────┐
                     │  Deterministic  │
                     │    Guardrails   │
                     └───────┬─────────┘
                             ▼
                    Ingestion Layer
                             ▼
                  Deterministic Classifier
                             ▼
                    Sanitization Layer
                             ▼
                        Safe Logging
                             ▼
                      Final Policy Gate
                             ▼
                     ┌─────────────────┐
                     │   Agent Brain   │
                     └─────────────────┘
                             ▲
                             │
         [ Phase 2 ] Semantic Classifiers (ProtectAI v2 jailbreak detector)
         [ Phase 2.6 ] Intent Layer (LLM-based ambiguous case resolution)
         [ Phase 3 ] Adversarial Testing (systematic red-teaming)
         [ Phase 4 ] Learning & Documentation (measurement mastery)
         [ Phase 5 ] OWASP AI mapping (optional educational module)
```

---

## Purpose of This Roadmap

This "AI Guardrail NorthStar" document serves as:

**Learning & Reference:**
- Blueprint for systematic guardrail development
- Guide for understanding defense-in-depth security
- Reference for model selection and evaluation methodology
- Living document tracking project evolution

**Portfolio Development:**
- Demonstrates systematic problem-solving approach
- Shows measurement-driven decision making
- Documents technical depth and critical thinking
- Showcases reproducible experiment design

**Scope Note:**
This is a **learning project**, not production deployment. Focus is on:
- ✅ Understanding why security measures work
- ✅ Building clean measurement methodologies
- ✅ Documenting comprehensive decision rationale
- ✅ Creating reproducible, well-tested implementations

Not focused on:
- ❌ Production scalability or SLA requirements
- ❌ Legal compliance (SOC2, GDPR, etc.)
- ❌ Operational concerns (monitoring, incident response)

**Current Status:**
- ✅ Phase 1 (Deterministic Guardrails): Complete
- ✅ Phase 2 (Semantic Guardrails): Model swap complete, measurement in progress
- ⏳ Phase 2.5: Code hardening and FPR validation
- 📋 Phase 2.6: Intent layer (pending FPR measurement)
- 📋 Phase 3: Adversarial testing
- 📋 Phase 4-6: Advanced topics (optional)

You can attach this file to your project for continuity and reference.

