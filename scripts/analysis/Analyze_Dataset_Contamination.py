"""
Deep dive: Count how many "benign" rows in TrustAIRLab regular
actually contain attack patterns. Also write a removal list and
cleaned benign-only dataset snapshot for reproducibility.
"""

import json
import re
from datetime import datetime
from pathlib import Path

from datasets import load_dataset


def main() -> None:
    dataset = load_dataset(
        "TrustAIRLab/in-the-wild-jailbreak-prompts",
        "regular_2023_12_25",
        split="train",
    )

    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / "reports"
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    removal_path = output_dir / f"trustairlab_regular_contaminated_{timestamp}.jsonl"
    cleaned_path = project_root / "datasets" / f"TrustAIRLab_regular_2023_12_25_CLEANED_{timestamp}.jsonl"

    print("=" * 80)
    print("ANALYZING TrustAIRLab regular_2023_12_25 COMPOSITION")
    print("=" * 80)

    # Count jailbreak labels
    jailbreak_counts = {}
    for row in dataset:
        label = row.get("jailbreak", "unknown")
        jailbreak_counts[label] = jailbreak_counts.get(label, 0) + 1

    print("\nJailbreak Label Distribution:")
    for label, count in sorted(jailbreak_counts.items(), key=lambda x: str(x[0])):
        pct = (count / len(dataset)) * 100
        print(f"  {label}: {count:,} ({pct:.1f}%)")

    # Now check how many "False" labeled rows contain attack patterns
    print("\n" + "=" * 80)
    print("CHECKING 'BENIGN' ROWS FOR ATTACK PATTERNS:")
    print("=" * 80)

    attack_patterns = [
        (r"\bignore\s+(all\s+)?previous\s+instructions\b", "ignore previous instructions"),
        (r"\bact\s+as\s+(a\s+)?(admin|root|system|developer|sudo)\b", "privilege escalation"),
        (r"\breveal\s+(your\s+)?(system\s+)?prompt\b", "prompt extraction"),
        (r"\bbypass\s+(security|filter|guardrail|safety)\b", "bypass attempt"),
        (r"\bjailbreak\b", "explicit jailbreak"),
        (r"\bDAN\s+mode\b|Do Anything Now", "DAN jailbreak"),
        (r"<\|im_start\|>|<\|im_end\|>", "token injection"),
    ]

    pattern_matches = {pattern_name: 0 for _, pattern_name in attack_patterns}
    rows_with_patterns = []
    benign_total = 0
    contaminated_total = 0

    with open(removal_path, "w", encoding="utf-8") as removal_f, open(
        cleaned_path, "w", encoding="utf-8"
    ) as cleaned_f:
        for row in dataset:
            if row.get("jailbreak") is not False:
                continue

            benign_total += 1
            prompt = row["prompt"]
            matched_patterns = []

            for regex, pattern_name in attack_patterns:
                if re.search(regex, prompt, re.IGNORECASE):
                    pattern_matches[pattern_name] += 1
                    matched_patterns.append(pattern_name)

            if matched_patterns:
                contaminated_total += 1
                if len(rows_with_patterns) < 10:
                    rows_with_patterns.append((prompt[:100], matched_patterns))
                removal_f.write(
                    json.dumps(
                        {
                            "prompt": prompt,
                            "patterns": matched_patterns,
                            "label": row.get("jailbreak"),
                        }
                    )
                    + "\n"
                )
            else:
                cleaned_f.write(json.dumps({"prompt": prompt, "label": "benign"}) + "\n")

    print(f"\nTotal rows labeled jailbreak=False: {benign_total:,}")

    print("\nAttack Pattern Detections in 'Benign' Rows:")
    for pattern_name, count in sorted(pattern_matches.items(), key=lambda x: -x[1]):
        if count > 0:
            pct = (count / benign_total) * 100 if benign_total else 0.0
            print(f"  {pattern_name}: {count:,} ({pct:.1f}%)")

    print(f"\nTotal 'benign' rows with attack patterns: {contaminated_total:,} / {benign_total:,}")
    contamination_rate = (contaminated_total / benign_total) * 100 if benign_total else 0.0
    print(f"Contamination rate: {contamination_rate:.1f}%")
    print(f"\nRemoval list: {removal_path}")
    print(f"Cleaned benign snapshot: {cleaned_path}")

    # Show examples
    print("\n" + "=" * 80)
    print("EXAMPLES OF 'BENIGN' ROWS WITH ATTACK PATTERNS:")
    print("=" * 80)

    for i, (text, patterns) in enumerate(rows_with_patterns, 1):
        print(f"\n[Example {i}]")
        print(f"  Text: {text}...")
        print(f"  Detected: {', '.join(patterns)}")
        print("  Dataset Label: jailbreak=False (benign)")
        print("  Reality: Likely an attack!")

    print("\n" + "=" * 80)
    print("CONCLUSION:")
    print("=" * 80)

    if contamination_rate > 2:
        print("!!! DATASET IS CONTAMINATED")
        print(f"    {contamination_rate:.1f}% of 'benign' rows contain attack patterns")
        print("    This inflates FPR because mislabeled attacks look like false positives")
        print("    Recommendation: exclude from benchmark FPR and treat as research-only")
    else:
        print(f"OK. Dataset appears clean (only {contamination_rate:.1f}% contamination)")


if __name__ == "__main__":
    main()
