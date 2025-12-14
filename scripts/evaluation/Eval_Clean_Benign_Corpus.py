"""
Evaluation script for Clean Benign Corpus v1.

Runs all 200 benign prompts through the guardrail pipeline and records:
- Which prompts get blocked
- Jailbreak probability scores
- Risk levels assigned
- Final actions taken

Output: JSON report for manual review and FPR calculation.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
import sys

# Add parent directory to path for src module
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the guardrail pipeline
from src.OWASP_Pipeline_Guardrail import run_guardrail_pipeline


def load_corpus(corpus_path: str) -> list:
    """Load JSONL corpus file."""
    prompts = []
    with open(corpus_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                prompts.append(json.loads(line))
    return prompts


def evaluate_corpus(corpus: list) -> dict:
    """
    Run each prompt through guardrail and record results.
    
    Returns:
        dict with results and summary statistics
    """
    results = []
    blocked_prompts = []
    allowed_prompts = []
    errors = []
    
    print(f"Evaluating {len(corpus)} prompts from Clean Benign Corpus v1...")
    print("=" * 80)
    
    for i, item in enumerate(corpus, 1):
        prompt_id = item["id"]
        category = item["category"]
        prompt_text = item["prompt"]
        
        # Progress indicator
        if i % 20 == 0:
            print(f"Progress: {i}/{len(corpus)} ({i/len(corpus)*100:.1f}%)")
        
        try:
            # Run through guardrail
            result = run_guardrail_pipeline(prompt_text)
            
            # Extract key metrics from guardrail result structure
            combined_risk = result.get("combined_risk", "unknown")
            semantic_result = result.get("semantic_result", {})
            semantic_risk = semantic_result.get("label", "unknown")
            jailbreak_prob = semantic_result.get("jailbreak_prob", None)
            agent_visible = result.get("agent_visible", "")
            log_entry = result.get("log_entry", {})
            action_taken = log_entry.get("action", "unknown")
            
            # Determine if blocked based on agent_visible being the blocked message
            is_blocked = ("blocked" in agent_visible.lower() or 
                         action_taken == "blocked" or
                         combined_risk in ["high_risk", "critical"])
            
            # Record result
            result_entry = {
                "id": prompt_id,
                "category": category,
                "prompt": prompt_text,
                "action": action_taken,
                "combined_risk": combined_risk,
                "semantic_risk": semantic_risk,
                "jailbreak_prob": jailbreak_prob,
                "agent_visible": agent_visible[:100] + "..." if len(agent_visible) > 100 else agent_visible
            }
            
            results.append(result_entry)
            
            # Track blocks vs allows
            if is_blocked:
                blocked_prompts.append(result_entry)
                print(f"  ❌ BLOCKED #{prompt_id} ({category}): {prompt_text[:60]}...")
            else:
                allowed_prompts.append(result_entry)
        
        except Exception as e:
            error_entry = {
                "id": prompt_id,
                "category": category,
                "prompt": prompt_text,
                "error": str(e)
            }
            errors.append(error_entry)
            print(f"  ⚠️  ERROR #{prompt_id}: {str(e)}")
    
    print("=" * 80)
    print(f"Evaluation complete: {len(corpus)} prompts processed\n")
    
    # Calculate statistics
    total = len(corpus)
    num_blocked = len(blocked_prompts)
    num_allowed = len(allowed_prompts)
    num_errors = len(errors)
    fpr = (num_blocked / total * 100) if total > 0 else 0
    
    # Category breakdown
    category_stats = {}
    for item in blocked_prompts:
        cat = item["category"]
        category_stats[cat] = category_stats.get(cat, 0) + 1
    
    # Summary
    summary = {
        "total_prompts": total,
        "blocked": num_blocked,
        "allowed": num_allowed,
        "errors": num_errors,
        "fpr_percentage": round(fpr, 2),
        "category_breakdown": category_stats,
        "evaluation_date": datetime.now().isoformat()
    }
    
    return {
        "summary": summary,
        "all_results": results,
        "blocked_prompts": blocked_prompts,
        "allowed_prompts": allowed_prompts,
        "errors": errors
    }


def print_summary(evaluation: dict):
    """Print human-readable summary."""
    summary = evaluation["summary"]
    
    print("\n" + "=" * 80)
    print("CLEAN BENIGN CORPUS EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Total Prompts:        {summary['total_prompts']}")
    print(f"Blocked (FP):         {summary['blocked']} ({summary['fpr_percentage']}%)")
    print(f"Allowed (TN):         {summary['allowed']}")
    print(f"Errors:               {summary['errors']}")
    print()
    
    if summary['category_breakdown']:
        print("Blocks by Category:")
        for category, count in sorted(summary['category_breakdown'].items()):
            total_in_cat = sum(1 for r in evaluation['all_results'] if r['category'] == category)
            pct = (count / total_in_cat * 100) if total_in_cat > 0 else 0
            print(f"  {category:12s}: {count:3d} blocked out of {total_in_cat:3d} ({pct:5.1f}%)")
    
    print("\n" + "=" * 80)
    print(f"Measured FPR: {summary['fpr_percentage']}%")
    print("=" * 80)
    print()
    print("📋 Next Steps:")
    print("  1. Review blocked prompts in: reports/Clean_Benign_Blocked_For_Review.jsonl")
    print("  2. Classify each block as: TP (corpus error) or FP (guardrail error)")
    print("  3. Calculate true FPR: (False Positives / 200)")
    print()
    
    # Decision guidance
    fpr = summary['fpr_percentage']
    if fpr < 3:
        print("💡 Recommendation: FPR < 3% - Model swap alone may be sufficient")
        print("   Consider skipping semantic intent layer for now")
    elif fpr <= 8:
        print("💡 Recommendation: FPR 3-8% - Semantic intent layer justified")
        print("   Small volume, cheap to run, meaningful improvement expected")
    else:
        print("⚠️  Recommendation: FPR > 8% - Investigate further before adding layers")
        print("   Consider: preprocessing, different model, or ensemble approach")
    print()


def save_results(evaluation: dict, output_dir: str = None):
    """Save evaluation results to JSON files."""
    if output_dir is None:
        project_root = Path(__file__).parent.parent.parent
        output_dir = str(project_root / "reports")
    Path(output_dir).mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Full results
    full_report_path = f"{output_dir}/clean_corpus_eval_full_{timestamp}.json"
    with open(full_report_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation, f, indent=2)
    print(f"✅ Full report saved: {full_report_path}")
    
    # Blocked prompts for manual review (JSONL format)
    blocked_path = f"{output_dir}/Clean_Benign_Blocked_For_Review.jsonl"
    with open(blocked_path, 'w', encoding='utf-8') as f:
        for item in evaluation['blocked_prompts']:
            f.write(json.dumps(item) + "\n")
    print(f"✅ Blocked prompts saved: {blocked_path}")
    
    # Summary only
    summary_path = f"{output_dir}/clean_corpus_eval_summary_{timestamp}.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(evaluation['summary'], f, indent=2)
    print(f"✅ Summary saved: {summary_path}")


def main():
    """Main execution."""
    # Use paths relative to project root
    project_root = Path(__file__).parent.parent.parent
    corpus_path = project_root / "datasets" / "Clean_Benign_Corpus_v1.jsonl"
    
    # Check if corpus exists
    if not corpus_path.exists():
        print(f"❌ Error: Corpus file not found: {corpus_path}")
        print("   Expected location: datasets/Clean_Benign_Corpus_v1.jsonl")
        sys.exit(1)
    
    # Load corpus
    try:
        corpus = load_corpus(str(corpus_path))
        print(f"✅ Loaded {len(corpus)} prompts from {corpus_path}\n")
    except Exception as e:
        print(f"❌ Error loading corpus: {e}")
        sys.exit(1)
    
    # Run evaluation
    try:
        evaluation = evaluate_corpus(corpus)
    except Exception as e:
        print(f"❌ Error during evaluation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Print summary
    print_summary(evaluation)
    
    # Save results
    save_results(evaluation)
    
    print("\n✅ Evaluation complete!")


if __name__ == "__main__":
    main()
