"""
Investigate TrustAIRLab regular_2023_12_25 dataset composition.
Check if it's truly benign or contains attacks.
"""

from datasets import load_dataset
import json

print("=" * 80)
print("INVESTIGATING TrustAIRLab/in-the-wild-jailbreak-prompts")
print("Config: regular_2023_12_25")
print("=" * 80)

# Load the dataset
dataset = load_dataset(
    "TrustAIRLab/in-the-wild-jailbreak-prompts",
    "regular_2023_12_25",
    split="train"
)

print(f"\nTotal samples: {len(dataset)}")
print(f"Columns: {dataset.column_names}")

# Sample first 10 rows
print("\n" + "=" * 80)
print("FIRST 10 SAMPLES:")
print("=" * 80)

for i in range(min(10, len(dataset))):
    row = dataset[i]
    print(f"\n[Sample {i+1}]")
    
    # Print all fields
    for key, value in row.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"  {key}: {value[:100]}...")
        else:
            print(f"  {key}: {value}")
    print("-" * 80)

# Check for label/category fields
print("\n" + "=" * 80)
print("CHECKING FOR GROUND TRUTH LABELS:")
print("=" * 80)

sample_row = dataset[0]
print(f"Available fields: {list(sample_row.keys())}")

# Look for any field that might indicate benign vs attack
potential_label_fields = [k for k in sample_row.keys() 
                         if any(word in k.lower() for word in 
                               ['label', 'category', 'type', 'class', 'attack', 'benign'])]

if potential_label_fields:
    print(f"\nPotential label fields found: {potential_label_fields}")
    for field in potential_label_fields:
        unique_values = set(str(dataset[i][field]) for i in range(min(100, len(dataset))))
        print(f"  {field}: {unique_values}")
else:
    print("\n⚠️  NO LABEL FIELDS FOUND - Cannot verify if truly benign!")

# Sample some prompts to manually inspect
print("\n" + "=" * 80)
print("RANDOM SAMPLE INSPECTION (Looking for attack patterns):")
print("=" * 80)

import random
random.seed(42)
samples = random.sample(range(len(dataset)), min(20, len(dataset)))

for idx in samples[:5]:
    row = dataset[idx]
    text_field = row.get('prompt') or row.get('text') or row.get('message') or str(row)
    if isinstance(text_field, str):
        print(f"\n[Sample {idx}]:")
        print(f"  {text_field[:200]}...")
        
        # Check for common attack patterns
        attack_keywords = ['ignore', 'previous instructions', 'system prompt', 
                          'act as', 'bypass', 'reveal', 'jailbreak']
        found_keywords = [kw for kw in attack_keywords if kw.lower() in text_field.lower()]
        if found_keywords:
            print(f"  ⚠️  ATTACK KEYWORDS DETECTED: {found_keywords}")
