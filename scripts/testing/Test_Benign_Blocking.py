"""
"""Check WHY benign prompts are being blocked.
Test a few truly benign samples through the guardrail.
"""

from pathlib import Path
import sys

# Add parent directory to path for src module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.OWASP_Pipeline_Guardrail import run_guardrail_pipeline
from datasets import load_dataset

dataset = load_dataset(
    "TrustAIRLab/in-the-wild-jailbreak-prompts",
    "regular_2023_12_25",
    split="train"
)

# Test first 10 samples
print("=" * 80)
print("TESTING BENIGN PROMPTS THROUGH GUARDRAIL")
print("=" * 80)

for i in range(10):
    prompt = dataset[i]['prompt']
    
    print(f"\n[Sample {i}]")
    print(f"Prompt: {prompt[:100]}...")
    
    result = run_guardrail_pipeline(prompt, include_raw=False)
    
    print(f"  Deterministic: {result['deterministic_risk']}")
    print(f"  Semantic: {result['semantic_result']['label']} ({result['semantic_result']['score']:.4f})")
    print(f"  Combined: {result['combined_risk']}")
    print(f"  Action: {result['log_entry']['action']}")
    
    if result['log_entry']['action'] == 'blocked':
        print(f"  ⚠️  BLOCKED! Why?")
        print(f"     - Semantic score: {result['semantic_result']['score']:.4f}")
        print(f"     - OWASP: {result['log_entry'].get('owasp_codes', [])}")
