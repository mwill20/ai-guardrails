"""
Deep dive: Count how many "benign" rows in TrustAIRLab regular
actually contain attack patterns.
"""

from datasets import load_dataset
import re

dataset = load_dataset(
    "TrustAIRLab/in-the-wild-jailbreak-prompts",
    "regular_2023_12_25",
    split="train"
)

print("=" * 80)
print("ANALYZING TrustAIRLab regular_2023_12_25 COMPOSITION")
print("=" * 80)

# Count jailbreak labels
jailbreak_counts = {}
for row in dataset:
    label = row.get('jailbreak', 'unknown')
    jailbreak_counts[label] = jailbreak_counts.get(label, 0) + 1

print(f"\nJailbreak Label Distribution:")
for label, count in sorted(jailbreak_counts.items()):
    pct = (count / len(dataset)) * 100
    print(f"  {label}: {count:,} ({pct:.1f}%)")

# Now check how many "False" labeled rows contain attack patterns
print("\n" + "=" * 80)
print("CHECKING 'BENIGN' ROWS FOR ATTACK PATTERNS:")
print("=" * 80)

attack_patterns = [
    (r'\bignore\s+(all\s+)?previous\s+instructions\b', 'ignore previous instructions'),
    (r'\bact\s+as\s+(a\s+)?(admin|root|system|developer|sudo)\b', 'privilege escalation'),
    (r'\breveal\s+(your\s+)?(system\s+)?prompt\b', 'prompt extraction'),
    (r'\bbypass\s+(security|filter|guardrail|safety)\b', 'bypass attempt'),
    (r'\bjailbreak\b', 'explicit jailbreak'),
    (r'\bDAN\s+mode\b|Do Anything Now', 'DAN jailbreak'),
    (r'<\|im_start\|>|<\|im_end\|>', 'token injection'),
]

benign_rows = [row for row in dataset if row['jailbreak'] == False]
print(f"\nTotal rows labeled jailbreak=False: {len(benign_rows):,}")

pattern_matches = {pattern_name: 0 for _, pattern_name in attack_patterns}
rows_with_patterns = []

for row in benign_rows:
    prompt = row['prompt'].lower()
    matched_patterns = []
    
    for regex, pattern_name in attack_patterns:
        if re.search(regex, prompt, re.IGNORECASE):
            pattern_matches[pattern_name] += 1
            matched_patterns.append(pattern_name)
    
    if matched_patterns:
        rows_with_patterns.append((row['prompt'][:100], matched_patterns))

print("\nAttack Pattern Detections in 'Benign' Rows:")
for pattern_name, count in sorted(pattern_matches.items(), key=lambda x: -x[1]):
    if count > 0:
        pct = (count / len(benign_rows)) * 100
        print(f"  {pattern_name}: {count:,} ({pct:.1f}%)")

print(f"\nTotal 'benign' rows with attack patterns: {len(rows_with_patterns):,} / {len(benign_rows):,}")
contamination_rate = (len(rows_with_patterns) / len(benign_rows)) * 100
print(f"Contamination rate: {contamination_rate:.1f}%")

# Show examples
print("\n" + "=" * 80)
print("EXAMPLES OF 'BENIGN' ROWS WITH ATTACK PATTERNS:")
print("=" * 80)

for i, (text, patterns) in enumerate(rows_with_patterns[:10], 1):
    print(f"\n[Example {i}]")
    print(f"  Text: {text}...")
    print(f"  Detected: {', '.join(patterns)}")
    print(f"  Dataset Label: jailbreak=False (benign)")
    print(f"  Reality: Likely an attack!")

print("\n" + "=" * 80)
print("CONCLUSION:")
print("=" * 80)

if contamination_rate > 10:
    print(f"⚠️  DATASET IS CONTAMINATED!")
    print(f"    {contamination_rate:.1f}% of 'benign' rows contain attack patterns")
    print(f"    This explains your 93.6% FPR - you're blocking actual attacks")
    print(f"    but calling them 'false positives' due to wrong ground truth!")
else:
    print(f"✅ Dataset appears clean (only {contamination_rate:.1f}% contamination)")
