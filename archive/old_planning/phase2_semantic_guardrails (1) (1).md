# Phase 2 — Semantic + Deterministic Guardrail Skeleton (Updated)

```python
from typing import Literal, TypedDict

# Expanded Literal (now includes "unknown")
SemanticRisk = Literal["unknown", "benign", "suspicious", "malicious", "critical"]


class SemanticRiskResult(TypedDict):
    label: SemanticRisk
    score: float


def semantic_classify_input(text: str) -> SemanticRiskResult:
    text_lower = text.lower()

    result: SemanticRiskResult = {
        "label": "unknown",
        "score": 0.0,
    }

    if "ignore previous instructions" in text_lower and "system prompt" in text_lower:
        result["label"] = "critical"
        result["score"] = 1.0
        return result

    elif "ignore previous instructions" in text_lower:
        result["label"] = "malicious"
        result["score"] = 0.75
        return result

    elif "system prompt" in text_lower:
        result["label"] = "suspicious"
        result["score"] = 0.5
        return result

    result["label"] = "benign"
    return result


def combine_risks(deterministic_risk: str, semantic_label: SemanticRisk) -> str:
    if semantic_label == "critical":
        return "critical"
    elif semantic_label == "malicious" or deterministic_risk == "high_risk":
        return "high_risk"
    elif semantic_label == "suspicious" or deterministic_risk == "medium_risk":
        return "medium_risk"
    else:
        return "low_risk"


def build_log_entry(
    raw_text: str,
    deterministic_risk: str,
    semantic_result: SemanticRiskResult,
    combined_risk: str,
    sanitized_text: str,
) -> dict:
    log = {}
    log["deterministic_risk"] = deterministic_risk
    log["semantic_label"] = semantic_result["label"]
    log["semantic_score"] = semantic_result["score"]
    log["combined_risk"] = combined_risk
    log["length"] = len(raw_text)
    log["sanitized_preview"] = sanitized_text[:20]

    if combined_risk in ("high_risk", "critical"):
        action = "blocked"
    else:
        action = "allowed"

    log["action"] = action
    return log


def process_input(user_text: str) -> dict:
    raw = get_raw_input(user_text)
    det_risk = classify_input(raw)
    semantic_result = semantic_classify_input(raw)
    combined = combine_risks(det_risk, semantic_result["label"])
    sanitized = sanitize_input(raw)

    log_entry = build_log_entry(
        raw,
        det_risk,
        semantic_result,
        combined,
        sanitized,
    )
    agent_input = final_agent_input(raw, combined, sanitized)

    return {
        "log_entry": log_entry,
        "agent_input": agent_input,
    }


def final_agent_input(raw_text: str, combined_risk: str, sanitized_text: str) -> str:
    if combined_risk in ("high_risk", "critical"):
        return "Request blocked due to unsafe content."
    elif combined_risk == "medium_risk":
        return "User input sanitized: " + sanitized_text
    else:
        return sanitized_text


if __name__ == "__main__":
    result = process_input("Hello, system prompt, ignore previous instructions")
    print(result)
```