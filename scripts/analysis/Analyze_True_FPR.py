"""
Re-analyze the actual eval results to see what's being blocked.
Check if the 93.6% FPR is due to:
1. Dataset contamination (6% confirmed)
2. Overly aggressive blocking of legitimate prompts
3. Wrong ground truth assumption
"""

import json
from datasets import load_dataset

# Load the most recent eval results
eval_file = "reports/phase_2_51_eval_results_20251212_082243.json"

print("=" * 80)
print("ANALYZING ACTUAL EVAL RESULTS")
print("=" * 80)

with open(eval_file, 'r') as f:
    results = json.load(f)

# Find TrustAIRLab regular results
trustair_regular = None
for dataset_name, data in results['datasets'].items():
    if 'regular' in dataset_name.lower():
        trustair_regular = data
        print(f"\nFound: {dataset_name}")
        print(f"  Total: {data['metrics']['total']}")
        print(f"  FP: {data['metrics']['fp']}")
        print(f"  TN: {data['metrics']['tn']}")
        print(f"  FPR: {data['metrics']['fpr']:.1%}")
        break

if not trustair_regular:
    print("⚠️  TrustAIRLab regular results not found!")
    exit(1)

# Load the actual dataset
dataset = load_dataset(
    "TrustAIRLab/in-the-wild-jailbreak-prompts",
    "regular_2023_12_25",
    split="train"
)

# Check first 500 samples (what eval actually tested)
print("\n" + "=" * 80)
print("ANALYZING FIRST 500 SAMPLES (EVAL SUBSET):")
print("=" * 80)

eval_subset = dataset[:500]

# Count attack patterns in this subset
import re

attack_patterns = [
    (r'\bignore\s+(all\s+)?previous\s+instructions\b', 'ignore previous instructions'),
    (r'\bact\s+as\s+(a\s+)?(admin|root|system|developer|sudo|DAN)\b', 'privilege/role'),
    (r'\breveal\s+(your\s+)?(system\s+)?prompt\b', 'prompt extraction'),
    (r'\bbypass\s', 'bypass'),
    (r'\bjailbreak\b', 'jailbreak'),
]

contaminated = 0
examples_blocked = []
examples_allowed = []

for i, prompt in enumerate(eval_subset['prompt']):
    has_attack_pattern = False
    matched = []
    
    for regex, name in attack_patterns:
        if re.search(regex, prompt.lower()):
            has_attack_pattern = True
            matched.append(name)
            contaminated += 1
            break
    
    if i < 20:  # Save first 20 for inspection
        if has_attack_pattern:
            examples_blocked.append((i, prompt[:150], matched))
        else:
            examples_allowed.append((i, prompt[:150]))

print(f"\nFirst 500 samples contamination: {contaminated} / 500 ({contaminated/5:.1f}%)")
print(f"\nExpected blocks due to contamination: ~{contaminated}")
print(f"Actual blocks (FP): {trustair_regular['metrics']['fp']}")
print(f"Difference: {trustair_regular['metrics']['fp'] - contaminated}")

# Show examples
print("\n" + "=" * 80)
print("EXAMPLES OF CONTAMINATED 'BENIGN' SAMPLES:")
print("=" * 80)
for idx, text, patterns in examples_blocked[:5]:
    print(f"\n[Sample {idx}] - CONTAINS ATTACK PATTERNS")
    print(f"  {text}...")
    print(f"  Patterns: {patterns}")

print("\n" + "=" * 80)
print("EXAMPLES OF TRULY BENIGN SAMPLES:")
print("=" * 80)
for idx, text in examples_allowed[:5]:
    print(f"\n[Sample {idx}]")
    print(f"  {text}...")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)

adjusted_fp = trustair_regular['metrics']['fp'] - contaminated
adjusted_fpr = adjusted_fp / 500
actual_fpr = trustair_regular['metrics']['fpr']

print(f"\nReported FPR: {actual_fpr:.1%}")
print(f"Contamination-adjusted FPR: {adjusted_fpr:.1%}")
print(f"Reduction: {(actual_fpr - adjusted_fpr) * 100:.1f} percentage points")

if adjusted_fpr > 0.50:
    print(f"\n⚠️  Even after contamination adjustment, FPR is still {adjusted_fpr:.1%}")
    print("    This suggests the guardrail IS overly aggressive on legitimate prompts")
else:
    print(f"\n✅ Contamination explains most of the FPR!")
    print(f"    True FPR is only {adjusted_fpr:.1%} on actually benign prompts")
