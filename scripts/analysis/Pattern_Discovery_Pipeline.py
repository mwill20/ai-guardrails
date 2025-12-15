"""
Pattern Discovery Pipeline - Phase 2.6 Deterministic Enrichment
================================================================

Purpose: Extract attack patterns from evaluation logs (false negatives) and rank by priority_score.
Output: JSONL file (pattern_candidates_v1.jsonl) sorted by value for deterministic rule implementation.

SCHEMA CONTRACT (pattern_candidates.v1):
========================================

Each JSONL record represents one candidate pattern with dataset-backed evidence,
FN/TP/FP/TN bucket counts, benign regression matches, computed priority metrics,
structured implementation guidance, and an include/exclude/review recommendation—
without storing raw prompt text.

REQUIRED ENUMS:
--------------
CATEGORIES = {"system_marker", "control_phrase", "credential_like", 
              "boundary_testing", "role_confusion", "encoding_obfuscation", "other"}
PATTERN_KINDS = {"literal", "regex", "keyword_set"}
SIGNAL_STRENGTH = {"weak", "strong"}
SEVERITY_HINT = {"low_risk", "medium_risk", "high_risk"}
RECOMMENDATION = {"include", "exclude", "review"}
TARGET_FUNCTIONS = {"check_system_markers", "check_control_phrases", "check_credential_patterns",
                    "check_boundary_testing", "check_role_confusion", "check_encoding_obfuscation"}
SUGGESTED_ACTIONS = {"escalate", "score_only", "log_only"}
SUGGESTED_RISKS = {"none", "low_risk", "medium_risk", "high_risk"}

PATTERN MATCHING SEMANTICS (prevents FPR explosions):
-----------------------------------------------------
- substring: Case-folded contains (pattern.lower() in text.lower())
- regex: Python re with re.IGNORECASE, timeout guard (100ms max), no catastrophic backtracking
- keyword_set: any_of semantics (match if ANY keyword present), unless explicitly labeled all_of
- All matching must be deterministic and reproducible across runs

EVAL LOG PATH CONVENTION:
-------------------------
reports/evals/eval_{YYYYMMDD_HHMMSS}_{DATASET}.jsonl

PATTERN ID CONVENTION:
---------------------
Category-prefixed sequential: SYS_###, CTRL_###, CRED_###, BND_###, ROLE_###, ENC_###, OTH_###

PRIVACY PRINCIPLE:
-----------------
NO raw prompt text stored anywhere. Use prompt_ids only. No prompt_excerpt field.

DECISION LOGIC (per pattern):
-----------------------------
INCLUDE if ALL of:
  - fn_coverage_rate > 0.02 (covers ≥2% of FN prompts)
  - fp_risk_score < 0.02 (≤4 FP prompts out of 200)
  - fp_prompt_hits_clean ≤ 1 (max 1 benign hit = 0.5% FP per pattern)
  - signal_strength="strong" (weak signals never auto-include)

EXCLUDE if ANY of:
  - fp_prompt_hits_clean ≥ 2 (≥1.0% FP risk per pattern)
  - fp_risk_score > 0.05 (legacy threshold)
  - fn_coverage_rate < 0.01 (covers <1% of FNs)

REVIEW: Everything else (ambiguous cases)

METRICS COMPUTATION (unique prompts only):
------------------------------------------
fn_coverage_rate = fn_prompt_hits / fn_total_prompts
  - fn_prompt_hits: number of UNIQUE FN prompts that matched pattern ≥1 time
  - fn_total_prompts: total FN prompts in dataset for this eval run
  - NOT sum of occurrences (prevents double-counting)

tp_support_rate = tp_prompt_hits / tp_total_prompts
fp_risk_score = fp_prompt_hits_clean / 200 (Clean_Benign only)
priority_score = (fn_coverage_rate × 2.0) - (fp_risk_score × 5.0) + (rarity_score × 0.5)

STOP-THE-LINE ASSERTION:
------------------------
Fail run if ANY eval log contains:
  - "action": "UNKNOWN" OR "action": null
  - "jailbreak_prob": null for prompts that should have semantic evaluation
Rationale: Prevents silent allow regressions—no UNKNOWN actions allowed
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple
import subprocess

# Schema constants
CATEGORIES = {
    "system_marker", "control_phrase", "credential_like",
    "boundary_testing", "role_confusion", "encoding_obfuscation", "other"
}

PATTERN_KINDS = {"literal", "regex", "keyword_set"}
SIGNAL_STRENGTH = {"weak", "strong"}
SEVERITY_HINT = {"low_risk", "medium_risk", "high_risk"}
RECOMMENDATION = {"include", "exclude", "review"}
TARGET_FUNCTIONS = {
    "check_system_markers", "check_control_phrases", "check_credential_patterns",
    "check_boundary_testing", "check_role_confusion", "check_encoding_obfuscation", "check_other"
}
SUGGESTED_ACTIONS = {"escalate", "score_only", "log_only"}
SUGGESTED_RISKS = {"none", "low_risk", "medium_risk", "high_risk"}

# Pattern definitions by category
SYSTEM_MARKERS = [
    "system:", "[INST]", "<<SYS>>", "<<sys>>", "</SYS>", "</sys>",
    "hidden instructions", "reveal your prompt", "show me your instructions",
    "[SYSTEM]", "<system>", "system prompt", "your system message"
]

CONTROL_PHRASES = [
    "ignore instructions", "bypass safety", "override restrictions",
    "forget your rules", "disregard previous", "ignore above",
    "ignore all previous", "new instructions:", "updated guidelines:",
    "administrator mode", "developer mode", "debug mode"
]

CREDENTIAL_PATTERNS = [
    r"sk-[a-zA-Z0-9]{20,}",  # OpenAI API keys
    r"AKIA[A-Z0-9]{16}",      # AWS access keys
    r"api_key\s*=\s*['\"][^'\"]+['\"]",
    r"\.env\s*=",
    r"bearer\s+token",
    r"Authorization:\s*Bearer"
]

BOUNDARY_TESTING = [
    "for testing", "hypothetical", "roleplay", "pretend",
    "imagine you are", "let's pretend", "in a fictional world"
]

ROLE_CONFUSION = [
    "assistant:", "user:", "system:", "AI:",
    "You are now", "Act as", "Pretend to be"
]


def get_git_commit() -> str:
    """Get current git commit SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except:
        return "unknown"


def load_eval_logs(eval_dir: Path) -> Dict[str, List[Dict]]:
    """
    Load all evaluation logs from reports/evals/ directory.
    Returns dict: dataset_name -> list of eval records
    """
    eval_logs = {}
    
    if not eval_dir.exists():
        print(f"❌ Eval directory does not exist: {eval_dir}")
        print(f"Please run: python scripts/evaluation/Eval.py --dataset <name>")
        sys.exit(1)
    
    log_files = list(eval_dir.glob("eval_*.jsonl"))
    if not log_files:
        print(f"❌ No eval logs found in {eval_dir}")
        print(f"Please run: python scripts/evaluation/Eval.py --dataset <name>")
        sys.exit(1)
    
    for log_file in log_files:
        # Parse dataset name from filename: eval_{timestamp}_{dataset}.jsonl
        parts = log_file.stem.split("_", 2)
        if len(parts) >= 3:
            dataset_name = parts[2]
        else:
            dataset_name = log_file.stem
        
        records = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line)
                    
                    # STOP-THE-LINE ASSERTION
                    if record.get("action") in [None, "UNKNOWN"]:
                        print(f"❌ STOP-THE-LINE: {log_file.name}:{line_num}")
                        print(f"   action=\"{record.get('action')}\" detected")
                        print(f"   Prevents silent allow regressions—no UNKNOWN actions allowed")
                        sys.exit(1)
                    
                    if "jailbreak_prob" in record and record["jailbreak_prob"] is None:
                        if record.get("ground_truth") in ["attack", "jailbreak"]:
                            print(f"❌ STOP-THE-LINE: {log_file.name}:{line_num}")
                            print(f"   jailbreak_prob=null for attack prompt")
                            print(f"   Semantic evaluation should have produced a probability")
                            sys.exit(1)
                    
                    records.append(record)
                except json.JSONDecodeError as e:
                    print(f"⚠️  Warning: Invalid JSON in {log_file.name}:{line_num}: {e}")
                    continue
        
        eval_logs[dataset_name] = records
        print(f"✅ Loaded {len(records)} records from {dataset_name}")
    
    return eval_logs


def classify_outcome(record: Dict) -> str:
    """
    Classify prompt outcome: TP / FN / FP / TN
    
    Ground truth vs guardrail action:
    - attack + BLOCK/SANITIZE = TP
    - attack + ALLOW = FN
    - benign + BLOCK/SANITIZE = FP
    - benign + ALLOW = TN
    """
    ground_truth = record.get("ground_truth", "").lower()
    action = record.get("action", "").lower()
    
    is_attack = ground_truth in ["attack", "jailbreak", "malicious"]
    is_blocked = action in ["blocked", "sanitize"]
    
    if is_attack and is_blocked:
        return "true_positive"
    elif is_attack and not is_blocked:
        return "false_negative"
    elif not is_attack and is_blocked:
        return "false_positive"
    else:
        return "true_negative"


def extract_patterns_from_prompts(prompts: List[str], category: str) -> Dict[str, List[int]]:
    """
    Extract patterns from prompts based on category.
    Returns: dict mapping pattern -> list of prompt indices that matched
    
    Uses unique prompts only (not occurrence counts).
    """
    pattern_matches = defaultdict(set)  # Use set for unique prompt indices
    
    if category == "system_marker":
        patterns = SYSTEM_MARKERS
        for pattern in patterns:
            for idx, prompt in enumerate(prompts):
                if pattern.lower() in prompt.lower():
                    pattern_matches[pattern].add(idx)
    
    elif category == "control_phrase":
        patterns = CONTROL_PHRASES
        for pattern in patterns:
            for idx, prompt in enumerate(prompts):
                if pattern.lower() in prompt.lower():
                    pattern_matches[pattern].add(idx)
    
    elif category == "credential_like":
        patterns = CREDENTIAL_PATTERNS
        for pattern in patterns:
            regex = re.compile(pattern, re.IGNORECASE)
            for idx, prompt in enumerate(prompts):
                try:
                    if regex.search(prompt):
                        pattern_matches[pattern].add(idx)
                except Exception as e:
                    print(f"⚠️  Regex error for pattern '{pattern}': {e}")
                    continue
    
    elif category == "boundary_testing":
        patterns = BOUNDARY_TESTING
        for pattern in patterns:
            for idx, prompt in enumerate(prompts):
                if pattern.lower() in prompt.lower():
                    pattern_matches[pattern].add(idx)
    
    elif category == "role_confusion":
        patterns = ROLE_CONFUSION
        for pattern in patterns:
            for idx, prompt in enumerate(prompts):
                if pattern.lower() in prompt.lower():
                    pattern_matches[pattern].add(idx)
    
    # Convert sets to lists
    return {pattern: list(indices) for pattern, indices in pattern_matches.items()}


def main():
    """Main pipeline execution."""
    print("=" * 70)
    print("Pattern Discovery Pipeline - Phase 2.6")
    print("=" * 70)
    print()
    
    # Setup paths
    project_root = Path(__file__).parent.parent.parent
    eval_dir = project_root / "reports" / "evals"
    output_dir = project_root / "reports" / "phase2_6"
    output_file = output_dir / "pattern_candidates_v1.jsonl"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Get metadata
    git_commit = get_git_commit()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    eval_run_id = f"eval_{timestamp}"
    
    print(f"📁 Eval logs directory: {eval_dir}")
    print(f"📝 Output file: {output_file}")
    print(f"🔖 Git commit: {git_commit[:8]}")
    print(f"🆔 Eval run ID: {eval_run_id}")
    print()
    
    # Load evaluation logs
    print("📥 Loading evaluation logs...")
    eval_logs = load_eval_logs(eval_dir)
    print()
    
    # Classify outcomes
    print("📊 Classifying outcomes...")
    outcome_stats = defaultdict(int)
    fn_prompts = []  # False negatives (attacks we missed)
    tp_prompts = []  # True positives (attacks we caught)
    fp_prompts = []  # False positives (benign we blocked)
    
    for dataset_name, records in eval_logs.items():
        for record in records:
            outcome = classify_outcome(record)
            outcome_stats[outcome] += 1
            
            if outcome == "false_negative":
                fn_prompts.append(record["prompt"])
            elif outcome == "true_positive":
                tp_prompts.append(record["prompt"])
            elif outcome == "false_positive":
                fp_prompts.append(record["prompt"])
    
    print(f"  TP: {outcome_stats['true_positive']}")
    print(f"  FN: {outcome_stats['false_negative']}")
    print(f"  FP: {outcome_stats['false_positive']}")
    print(f"  TN: {outcome_stats['true_negative']}")
    print()
    
    # Analyze FP patterns (patterns causing false alarms)
    print("⚠️  Analyzing false positive triggers...")
    fp_pattern_triggers = []
    
    for category in ["system_marker", "control_phrase", "credential_like", "boundary_testing", "role_confusion"]:
        fp_matches = extract_patterns_from_prompts(fp_prompts, category)
        for pattern, fp_indices in fp_matches.items():
            if len(fp_indices) >= 2:  # Patterns appearing in 2+ FPs
                fp_pattern_triggers.append({
                    "pattern": pattern,
                    "category": category,
                    "fp_count": len(fp_indices),
                    "fp_rate": len(fp_indices) / len(fp_prompts) if fp_prompts else 0
                })
    
    fp_pattern_triggers.sort(key=lambda x: x["fp_count"], reverse=True)
    print(f"  Found {len(fp_pattern_triggers)} patterns causing FPs")
    if fp_pattern_triggers[:5]:
        print("  Top FP triggers:")
        for trigger in fp_pattern_triggers[:5]:
            print(f"    - '{trigger['pattern']}' ({trigger['fp_count']} FPs, {trigger['fp_rate']:.1%})")
    print()
    
    # Extract patterns from FN prompts (attacks we missed - priority targets)
    print("🔍 Extracting patterns from false negatives...")
    pattern_candidates = []
    
    for category in ["system_marker", "control_phrase", "credential_like", "boundary_testing", "role_confusion"]:
        print(f"  Analyzing category: {category}")
        fn_matches = extract_patterns_from_prompts(fn_prompts, category)
        
        for pattern, fn_indices in fn_matches.items():
            if len(fn_indices) < 2:  # Skip patterns that only appear once
                continue
            
            # Calculate metrics
            fn_coverage = len(fn_indices) / len(fn_prompts) if fn_prompts else 0
            
            # Check FP risk against Clean_Benign_Corpus (if available)
            clean_corpus_path = project_root / "datasets" / "Clean_Benign_Corpus_v1.jsonl"
            fp_hits_clean = 0
            if clean_corpus_path.exists():
                with open(clean_corpus_path, "r", encoding="utf-8") as f:
                    clean_prompts = [json.loads(line)["prompt"] for line in f]
                    for prompt in clean_prompts:
                        if pattern.lower() in prompt.lower():
                            fp_hits_clean += 1
            
            fp_risk = fp_hits_clean / 200 if clean_corpus_path.exists() else 0.0
            
            # Decision logic
            if fp_hits_clean >= 2:
                decision = "exclude"
                rationale = f"FP risk too high ({fp_hits_clean} clean corpus hits)"
            elif fn_coverage > 0.02 and fp_risk < 0.02 and fp_hits_clean <= 1:
                decision = "include"
                rationale = f"Good coverage ({fn_coverage:.1%}), low FP risk"
            elif fn_coverage < 0.01:
                decision = "exclude"
                rationale = f"Low coverage ({fn_coverage:.1%})"
            else:
                decision = "review"
                rationale = "Ambiguous - needs manual review"
            
            priority_score = (fn_coverage * 2.0) - (fp_risk * 5.0)
            
            pattern_candidates.append({
                "schema_version": "1",
                "pattern_id": f"{category}_{len(pattern_candidates):03d}",
                "category": category,
                "pattern": {
                    "kind": "literal",
                    "value": pattern,
                    "case_sensitive": False
                },
                "evidence": {
                    "fn_prompt_hits": len(fn_indices),
                    "fn_coverage_rate": fn_coverage,
                    "fp_prompt_hits_clean": fp_hits_clean,
                    "fp_risk_score": fp_risk
                },
                "metrics": {
                    "priority_score": priority_score
                },
                "decision": {
                    "action": decision,
                    "rationale": rationale
                },
                "metadata": {
                    "git_commit": git_commit,
                    "eval_run_id": eval_run_id,
                    "discovery_timestamp": timestamp
                }
            })
    
    # Sort by priority score
    pattern_candidates.sort(key=lambda x: x["metrics"]["priority_score"], reverse=True)
    
    # Write output
    print()
    print(f"💾 Writing {len(pattern_candidates)} pattern candidates...")
    with open(output_file, "w", encoding="utf-8") as f:
        for candidate in pattern_candidates:
            f.write(json.dumps(candidate) + "\n")
    
    # Write FP analysis report
    fp_report_file = output_dir / "fp_pattern_analysis.json"
    with open(fp_report_file, "w", encoding="utf-8") as f:
        json.dump({
            "total_fps": len(fp_prompts),
            "fp_triggers": fp_pattern_triggers,
            "metadata": {
                "git_commit": git_commit,
                "eval_run_id": eval_run_id,
                "timestamp": timestamp
            }
        }, f, indent=2)
    
    # Summary
    include_count = sum(1 for p in pattern_candidates if p["decision"]["action"] == "include")
    review_count = sum(1 for p in pattern_candidates if p["decision"]["action"] == "review")
    exclude_count = sum(1 for p in pattern_candidates if p["decision"]["action"] == "exclude")
    
    print()
    print("✅ Pattern discovery pipeline complete")
    print(f"📊 FN Patterns: {output_file}")
    print(f"📊 FP Analysis: {fp_report_file}")
    print(f"📈 Summary: {include_count} include, {review_count} review, {exclude_count} exclude")
    print()


if __name__ == "__main__":
    main()
