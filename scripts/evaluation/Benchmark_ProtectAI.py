"""
Full benchmark: Compare ProtectAI vs current model on 100 TrustAIR regular samples.
"""

from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
import torch
from datasets import load_dataset
from tqdm import tqdm

# Load dataset
dataset = load_dataset(
    "TrustAIRLab/in-the-wild-jailbreak-prompts",
    "regular_2023_12_25",
    split="train"
)

test_samples = dataset[:100]

print("=" * 80)
print("BENCHMARKING: ProtectAI vs Current Model")
print("Testing on 100 TrustAIR regular samples")
print("=" * 80)

# Load both models
models = {
    "Current (madhurjindal)": "madhurjindal/Jailbreak-Detector-Large",
    "ProtectAI v2": "protectai/deberta-v3-base-prompt-injection-v2",
}

results = {}

for model_name, model_id in models.items():
    print(f"\nLoading {model_name}...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_id, use_fast=False)
    model = AutoModelForSequenceClassification.from_pretrained(model_id)
    classifier = pipeline(
        task="text-classification",
        model=model,
        tokenizer=tokenizer,
        truncation=True,
        max_length=512,
        device=torch.device("cuda" if torch.cuda.is_available() else "cpu"),
    )
    
    blocked_count = 0
    attack_scores = []
    
    print(f"Testing {model_name}...")
    for prompt in tqdm(test_samples['prompt']):
        outputs = classifier(prompt[:512], top_k=2)
        
        # Get attack probability
        attack_score = None
        for pred in outputs:
            label_lower = pred['label'].lower()
            if any(word in label_lower for word in ['jailbreak', 'injection', 'attack']):
                attack_score = pred['score']
                break
            elif any(word in label_lower for word in ['benign', 'safe', 'legit']):
                attack_score = 1 - pred['score']
                break
        
        if attack_score is None:
            attack_score = outputs[0]['score']
        
        attack_scores.append(attack_score)
        
        # Using 0.75 threshold (same as current guardrail)
        if attack_score > 0.75:
            blocked_count += 1
    
    results[model_name] = {
        'blocked': blocked_count,
        'fpr': (blocked_count / 100) * 100,
        'scores': attack_scores
    }

print("\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

for model_name, data in results.items():
    print(f"\n{model_name}:")
    print(f"  Blocked: {data['blocked']}/100")
    print(f"  FPR: {data['fpr']:.1f}%")
    print(f"  Mean attack score: {sum(data['scores'])/len(data['scores']):.4f}")
    print(f"  Median attack score: {sorted(data['scores'])[50]:.4f}")
    
    # Score distribution
    score_ranges = {
        "0.00-0.25 (benign)": 0,
        "0.25-0.50 (likely benign)": 0,
        "0.50-0.75 (suspicious)": 0,
        "0.75-1.00 (blocked)": 0
    }
    
    for score in data['scores']:
        if score <= 0.25:
            score_ranges["0.00-0.25 (benign)"] += 1
        elif score <= 0.50:
            score_ranges["0.25-0.50 (likely benign)"] += 1
        elif score <= 0.75:
            score_ranges["0.50-0.75 (suspicious)"] += 1
        else:
            score_ranges["0.75-1.00 (blocked)"] += 1
    
    print(f"  Score distribution:")
    for range_name, count in score_ranges.items():
        print(f"    {range_name}: {count}")

print("\n" + "=" * 80)
print("COMPARISON")
print("=" * 80)

current_fpr = results["Current (madhurjindal)"]['fpr']
protectai_fpr = results["ProtectAI v2"]['fpr']
improvement = current_fpr - protectai_fpr

print(f"\nCurrent Model FPR: {current_fpr:.1f}%")
print(f"ProtectAI v2 FPR: {protectai_fpr:.1f}%")
print(f"Improvement: {improvement:.1f} percentage points")

if protectai_fpr < 10:
    print(f"\n✅ ProtectAI v2 solves the FPR problem! ({protectai_fpr:.1f}% < 10% target)")
else:
    print(f"\n⚠️  ProtectAI v2 still has high FPR ({protectai_fpr:.1f}%)")
