"""
Investigate false positives from TrustAIRLab regular dataset.
Show actual prompts that were blocked to determine if they're truly benign or mislabeled attacks.
"""

import json
import sys
from pathlib import Path

# Load eval log
project_root = Path(__file__).parent.parent.parent
eval_log = project_root / "reports" / "evals" / "eval_20251215_071846_TrustAIRLab_regular_2023_12_25.jsonl"

if not eval_log.exists():
    print(f"❌ Eval log not found: {eval_log}")
    sys.exit(1)

print("=" * 80)
print("FALSE POSITIVE INVESTIGATION - TrustAIRLab Regular Dataset")
print("=" * 80)
print()

# Load all FPs
fps = []
with open(eval_log, "r", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        if record["ground_truth"] == "benign" and record["action"] == "blocked":
            fps.append(record)

print(f"Total FPs: {len(fps)}")
print()

# Analyze patterns
print("=" * 80)
print("TOP 20 FALSE POSITIVES (Full Prompts)")
print("=" * 80)

for i, fp in enumerate(fps[:20], 1):
    print(f"\n[FP #{i}]")
    print(f"Semantic Score: {fp['jailbreak_prob']:.4f}")
    print(f"Semantic Label: {fp['semantic_label']}")
    print(f"Deterministic: {fp['deterministic_risk']}")
    print(f"OWASP Codes: {fp['owasp_codes']}")
    print(f"Prompt:")
    print(f"  {fp['prompt'][:500]}...")  # First 500 chars
    print("-" * 80)

# Pattern analysis
print("\n" + "=" * 80)
print("PATTERN ANALYSIS IN FPS")
print("=" * 80)

fp_patterns = {
    "Act as": 0,
    "pretend": 0,
    "You are now": 0,
    "roleplay": 0,
    "Pretend to be": 0,
    "ignore": 0,
    "system prompt": 0,
    "reveal": 0,
    "bypass": 0,
    "jailbreak": 0,
}

for fp in fps:
    prompt_lower = fp['prompt'].lower()
    for pattern in fp_patterns.keys():
        if pattern.lower() in prompt_lower:
            fp_patterns[pattern] += 1

print("\nPattern frequencies in FPs:")
for pattern, count in sorted(fp_patterns.items(), key=lambda x: x[1], reverse=True):
    if count > 0:
        pct = (count / len(fps)) * 100
        print(f"  {pattern:20s}: {count:3d} ({pct:5.1f}%)")

# Look for explicit attack indicators
print("\n" + "=" * 80)
print("ATTACK INDICATOR ANALYSIS")
print("=" * 80)

attack_indicators = [
    "ignore previous",
    "disregard",
    "bypass",
    "jailbreak",
    "DAN",
    "developer mode",
    "unrestricted",
    "without restrictions",
    "evil",
    "unethical",
    "illegal",
    "harmful",
]

suspicious_fps = []
for fp in fps:
    prompt_lower = fp['prompt'].lower()
    matched_indicators = [ind for ind in attack_indicators if ind in prompt_lower]
    if matched_indicators:
        suspicious_fps.append({
            "prompt": fp['prompt'][:200],
            "indicators": matched_indicators,
            "score": fp['jailbreak_prob']
        })

print(f"\nFPs with explicit attack indicators: {len(suspicious_fps)}/{len(fps)} ({len(suspicious_fps)/len(fps)*100:.1f}%)")
print("\nTop 10 suspicious FPs (likely mislabeled attacks):")
for i, susp in enumerate(suspicious_fps[:10], 1):
    print(f"\n[Suspicious #{i}]")
    print(f"  Indicators: {susp['indicators']}")
    print(f"  Score: {susp['score']:.4f}")
    print(f"  Prompt: {susp['prompt']}...")
    print()

print("\n" + "=" * 80)
print("CONCLUSION")
print("=" * 80)
if len(suspicious_fps) > len(fps) * 0.05:
    print(f"⚠️  {len(suspicious_fps)/len(fps)*100:.1f}% of FPs contain explicit attack indicators")
    print("    This supports the contamination hypothesis - these are likely mislabeled attacks")
else:
    print(f"✓  Only {len(suspicious_fps)/len(fps)*100:.1f}% of FPs contain attack indicators")
    print("    Most FPs appear to be legitimate benign prompts")
