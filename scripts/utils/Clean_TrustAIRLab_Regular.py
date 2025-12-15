"""
Create a cleaned version of TrustAIRLab regular dataset by relabeling mislabeled attacks.

RATIONALE:
- Original dataset has 37.2% contamination (mislabeled attacks labeled as "benign")
- Keep original for:
  * Documenting dataset quality issues
  * Reproducibility (comparing to published benchmarks)
  * Research into dataset contamination detection
- Create cleaned version for:
  * Reliable FPR testing
  * Training/validation of future models
  * Accurate performance metrics

RELABELING CRITERIA (Attack Indicators):
- "ignore previous" / "disregard previous" / "forget previous"
- "unrestricted" / "without restrictions"
- "evil" / "harmful" / "illegal" / "unethical"
- "bypass" / "jailbreak" / "DAN"
- Classic jailbreak patterns
"""

import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent

# Attack indicators for relabeling
ATTACK_INDICATORS = [
    "ignore previous",
    "disregard previous",
    "forget previous",
    "ignore all previous",
    "disregard all previous",
    "bypass",
    "jailbreak",
    "DAN",
    "developer mode",
    "unrestricted",
    "without restrictions",
    "evil",
    "harmful",
    "illegal",
    "unethical",
    "no restrictions",
    "do anything now",
    "act as if",
    "break the rules",
    "override",
]

def contains_attack_indicators(text: str) -> list:
    """Return list of attack indicators found in text."""
    text_lower = text.lower()
    found = []
    for indicator in ATTACK_INDICATORS:
        if indicator in text_lower:
            found.append(indicator)
    return found


print("=" * 80)
print("CLEAN TRUSTAIRLAB REGULAR DATASET")
print("=" * 80)
print()

# Load from eval logs (contains the prompts + ground truth)
eval_log_path = project_root / "reports" / "evals" / "eval_20251215_071846_TrustAIRLab_regular_2023_12_25.jsonl"
cleaned_path = project_root / "datasets" / "TrustAIRLab_regular_2023_12_25_CLEANED.jsonl"

if not eval_log_path.exists():
    print(f"❌ Eval log not found: {eval_log_path}")
    print("   Run scripts/evaluation/Eval.py first")
    sys.exit(1)

# Load and analyze (from eval logs)
original_records = []
with open(eval_log_path, "r", encoding="utf-8") as f:
    for line in f:
        eval_record = json.loads(line)
        # Convert eval log format to dataset format
        original_records.append({
            "prompt": eval_record["prompt"],
            "label": eval_record["ground_truth"]  # "benign" or "attack"
        })

print(f"Loaded {len(original_records)} records from original dataset")
print()

# Identify mislabeled attacks
relabeled_count = 0
relabeled_records = []

print("Analyzing for mislabeled attacks...")
print()

for record in original_records:
    indicators = contains_attack_indicators(record["prompt"])
    
    if indicators and record["label"] == "benign":
        # Mislabeled attack - relabel as "attack"
        relabeled_records.append({
            "prompt": record["prompt"],
            "label": "attack",  # RELABELED
            "original_label": "benign",
            "relabel_reason": f"Contains attack indicators: {', '.join(indicators[:3])}",
            "indicators": indicators
        })
        relabeled_count += 1
    else:
        # Keep as-is
        relabeled_records.append({
            "prompt": record["prompt"],
            "label": record["label"],
        })

# Save cleaned dataset
with open(cleaned_path, "w", encoding="utf-8") as f:
    for record in relabeled_records:
        f.write(json.dumps(record) + "\n")

print("=" * 80)
print("RESULTS")
print("=" * 80)
print(f"Original records: {len(original_records)}")
print(f"Relabeled: {relabeled_count} ({relabeled_count/len(original_records)*100:.1f}%)")
print(f"Unchanged: {len(original_records) - relabeled_count}")
print()
print(f"✅ Cleaned dataset saved to:")
print(f"   {cleaned_path}")
print()
print("=" * 80)
print("USAGE NOTES")
print("=" * 80)
print("Original dataset: Use for documenting contamination, research reproducibility")
print("Cleaned dataset:  Use for reliable FPR testing, accurate performance metrics")
print()
print("Both datasets preserved for different testing purposes.")
