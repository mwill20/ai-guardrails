"""
Download TrustAIRLab and other datasets from HuggingFace to local disk.
This allows Pattern_Discovery_Pipeline.py to process them.
"""

from datasets import load_dataset
import jsonlines
from pathlib import Path
from tqdm import tqdm

# Create datasets directory
datasets_dir = Path("datasets")
datasets_dir.mkdir(exist_ok=True)

print("=" * 80)
print("DOWNLOADING TRUSTAIRLAB DATASETS FROM HUGGINGFACE")
print("=" * 80)

# Dataset configurations (matching Eval.py exactly)
DATASETS = [
    {
        "name": "TrustAIRLab_jailbreak",
        "source": "TrustAIRLab/in-the-wild-jailbreak-prompts",
        "config": "jailbreak_2023_12_25",
        "split": "train",
        "text_field": "prompt",
    },
    {
        "name": "TrustAIRLab_xTRam1",
        "source": "xTRam1/safe-guard-prompt-injection",
        "config": None,
        "split": "train",
        "text_field": "prompt",
    },
    {
        "name": "Lakera_mosscap",
        "source": "Lakera/mosscap_prompt_injection",
        "config": None,
        "split": "train",
        "text_field": "prompt",
    },
    {
        "name": "Mindgard_evaded",
        "source": "Mindgard/evaded-prompt-injection-and-jailbreak-samples",
        "config": None,
        "split": "train",
        "text_field": "modified_prompt",  # Try modified_prompt first
    },
]

for ds_config in DATASETS:
    name = ds_config["name"]
    source = ds_config["source"]
    config = ds_config["config"]
    split = ds_config["split"]
    text_field = ds_config["text_field"]
    
    print(f"\n{name}:")
    print(f"  Source: {source}")
    if config:
        print(f"  Config: {config}")
    
    try:
        # Load from HuggingFace
        print("  Loading from HuggingFace...")
        if config:
            dataset = load_dataset(source, config, split=split)
        else:
            dataset = load_dataset(source, split=split)
        
        print(f"  Loaded {len(dataset)} samples")
        
        # Save to JSONL
        output_file = datasets_dir / f"{name}.jsonl"
        print(f"  Saving to: {output_file}")
        
        with jsonlines.open(output_file, mode='w') as writer:
            for idx, row in enumerate(tqdm(dataset, desc=f"  Writing {name}")):
                # Find text field (try common names)
                text = None
                for field in [text_field, 'prompt', 'text', 'message', 'content']:
                    if field in row:
                        text = row[field]
                        break
                
                if text is None:
                    print(f"    Warning: Could not find text field in row {idx}")
                    continue
                
                # Write row with ID and text
                writer.write({
                    "id": f"{name}_{idx}",
                    "prompt": text,
                    "dataset": name,
                    "original_index": idx
                })
        
        print(f"  ✅ Saved {len(dataset)} prompts to {output_file}")
        
    except Exception as e:
        print(f"  ❌ Error loading {name}: {e}")
        print(f"     You may need to check dataset config names on HuggingFace")

print("\n" + "=" * 80)
print("DOWNLOAD COMPLETE")
print("=" * 80)
print(f"\nDatasets saved to: {datasets_dir.absolute()}")
print("\nNext step: Run Pattern_Discovery_Pipeline.py with eval logs")
