"""
Phase 2.6 Gate A Validation - Test FPR on Clean_Benign_Corpus_v1

GATE A: FPR ≤ 2.0% on Clean_Benign_Corpus_v1
Baseline: 1.0% FPR before OWASP pattern addition
Target: ≤ 2.0% FPR after OWASP pattern addition
"""

import json
import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from OWASP_Pipeline_Guardrail import run_guardrail_pipeline

print("=" * 80)
print("PHASE 2.6 GATE A VALIDATION")
print("=" * 80)
print("Gate A: FPR ≤ 2.0% on Clean_Benign_Corpus_v1")
print("Baseline: 1.0% FPR (2/200 prompts)")
print("=" * 80)
print()

# Load clean benign corpus
dataset_path = project_root / "datasets" / "Clean_Benign_Corpus_v1.jsonl"

if not dataset_path.exists():
    print(f"❌ Dataset not found: {dataset_path}")
    sys.exit(1)

prompts = []
with open(dataset_path, "r", encoding="utf-8") as f:
    for line in f:
        record = json.loads(line)
        prompts.append(record["prompt"])

print(f"Loaded {len(prompts)} benign prompts from Clean_Benign_Corpus_v1")
print()

# Run evaluation
print("Running evaluation...")
false_positives = []
true_negatives = []

for i, prompt in enumerate(prompts):
    result = run_guardrail_pipeline(prompt)
    
    if result["log_entry"]["action"] == "blocked":
        false_positives.append({
            "prompt_id": i,
            "prompt": prompt,
            "deterministic_risk": result["deterministic_risk"],
            "deterministic_pattern_hits": result["deterministic_pattern_hits"],
            "semantic_label": result["semantic_result"]["label"],
            "semantic_score": result["semantic_result"]["score"],
            "combined_risk": result["combined_risk"],
        })
    else:
        true_negatives.append(i)

# Calculate FPR
total_benign = len(prompts)
fp_count = len(false_positives)
tn_count = len(true_negatives)
fpr = (fp_count / total_benign) * 100

print()
print("=" * 80)
print("RESULTS")
print("=" * 80)
print(f"Total benign prompts: {total_benign}")
print(f"True Negatives (TN):  {tn_count} ({tn_count/total_benign*100:.1f}%)")
print(f"False Positives (FP): {fp_count} ({fpr:.1f}%)")
print()

if fpr <= 2.0:
    print(f"✅ GATE A PASSED: FPR = {fpr:.1f}% ≤ 2.0%")
else:
    print(f"❌ GATE A FAILED: FPR = {fpr:.1f}% > 2.0%")

print()

# Show FP details
if fp_count > 0:
    print("=" * 80)
    print("FALSE POSITIVE DETAILS")
    print("=" * 80)
    
    for i, fp in enumerate(false_positives, 1):
        print(f"\n[FP #{i}]")
        print(f"Prompt: {fp['prompt'][:100]}...")
        print(f"Deterministic Risk: {fp['deterministic_risk']}")
        print(f"Deterministic Patterns: {fp['deterministic_pattern_hits']}")
        print(f"Semantic Label: {fp['semantic_label']}")
        print(f"Semantic Score: {fp['semantic_score']:.4f}")
        print(f"Combined Risk: {fp['combined_risk']}")
        print("-" * 80)
else:
    print("✅ Zero false positives on clean benign corpus!")
    print("   OWASP patterns have perfect precision on vetted benign prompts")

print()
print("=" * 80)
print("COMPARISON TO BASELINE")
print("=" * 80)
print(f"Baseline FPR:  1.0% (2/200 prompts)")
print(f"Current FPR:   {fpr:.1f}% ({fp_count}/{total_benign} prompts)")

if fp_count <= 2:
    print(f"✅ FPR maintained or improved!")
elif fp_count <= 4:
    print(f"⚠️  FPR increased but still within Gate A threshold (≤2.0%)")
else:
    print(f"❌ FPR increased beyond acceptable threshold")
