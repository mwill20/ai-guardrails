"""
Research-only benign comparison.

Compares Clean_Benign_Corpus_v1 vs a TrustAIRLab regular cleaned snapshot
without mixing research data into the main eval harness.

Usage:
  python scripts/evaluation/Eval_Research_Benign_Comparison.py

Optional env vars:
  EVAL_LIMIT=500 (0 means full)
  CLEAN_BENIGN_PATH=custom/path.jsonl
  TRUSTAIRLAB_CLEANED_PATH=custom/path.jsonl
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from tqdm import tqdm

# -----------------------------
# Import pipeline
# -----------------------------
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.OWASP_Pipeline_Guardrail import run_guardrail_pipeline


ATTACK_PRED_RISKS = {"high_risk", "critical"}
SOFT_RISKS = {"medium_risk"}


@dataclass
class BenignMetrics:
    total: int = 0
    blocked: int = 0
    allowed: int = 0
    soft: int = 0
    errors: int = 0

    def fpr(self) -> Optional[float]:
        return None if self.total == 0 else self.blocked / self.total

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total": self.total,
            "blocked": self.blocked,
            "allowed": self.allowed,
            "soft": self.soft,
            "errors": self.errors,
            "fpr": self.fpr(),
        }


def extract_combined_risk(result: Dict[str, Any]) -> Optional[str]:
    if "combined_risk" in result and isinstance(result["combined_risk"], str):
        return result["combined_risk"]

    log_entry = result.get("log_entry")
    if isinstance(log_entry, dict):
        if isinstance(log_entry.get("combined_risk"), str):
            return log_entry["combined_risk"]
        if isinstance(log_entry.get("combined"), str):
            return log_entry["combined"]

    return None


def pipeline_predict(text: str) -> Tuple[Optional[str], Dict[str, Any]]:
    try:
        res = run_guardrail_pipeline(text, include_raw=False)
    except TypeError:
        res = run_guardrail_pipeline(text)
    combined = extract_combined_risk(res)
    return combined, res


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def pick_text(row: Dict[str, Any], text_field: Optional[str]) -> str:
    if text_field and row.get(text_field):
        return str(row[text_field])[:8000]

    for key in ("prompt", "text", "input", "instruction", "query"):
        if row.get(key):
            return str(row[key])[:8000]

    return str(row)[:8000]


def find_latest_cleaned_snapshot(dataset_dir: Path) -> Optional[Path]:
    candidates = sorted(
        dataset_dir.glob("TrustAIRLab_regular_2023_12_25_CLEANED_*.jsonl"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if candidates:
        return candidates[0]

    fallback = dataset_dir / "TrustAIRLab_regular_2023_12_25_CLEANED.jsonl"
    if fallback.exists():
        return fallback

    return None


def evaluate_benign_dataset(
    name: str,
    path: Path,
    text_field: Optional[str],
    limit: Optional[int],
) -> Tuple[BenignMetrics, List[Dict[str, Any]]]:
    rows = load_jsonl(path)
    if limit:
        rows = rows[:limit]

    metrics = BenignMetrics()
    blocked_examples: List[Dict[str, Any]] = []

    for row in tqdm(rows, desc=f"Scoring {name}", leave=False):
        text = pick_text(row, text_field)
        combined_risk, result = pipeline_predict(text)

        if combined_risk is None:
            metrics.errors += 1
            continue

        metrics.total += 1
        if combined_risk in ATTACK_PRED_RISKS:
            metrics.blocked += 1
            if len(blocked_examples) < 5:
                semantic = result.get("semantic_result", {})
                blocked_examples.append(
                    {
                        "text_preview": text[:140],
                        "combined_risk": combined_risk,
                        "semantic_label": semantic.get("label"),
                        "semantic_score": semantic.get("score"),
                    }
                )
        else:
            metrics.allowed += 1
            if combined_risk in SOFT_RISKS:
                metrics.soft += 1

    return metrics, blocked_examples


def format_metric(x: Optional[float]) -> str:
    return "N/A" if x is None else f"{x:.3f}"


def main() -> None:
    project_root = Path(__file__).parent.parent.parent
    dataset_dir = project_root / "datasets"

    clean_benign_path = Path(
        os.environ.get("CLEAN_BENIGN_PATH", dataset_dir / "Clean_Benign_Corpus_v1.jsonl")
    )
    trustairlab_path_env = os.environ.get("TRUSTAIRLAB_CLEANED_PATH")
    trustairlab_path = Path(trustairlab_path_env) if trustairlab_path_env else None
    if trustairlab_path is None:
        trustairlab_path = find_latest_cleaned_snapshot(dataset_dir)

    if not clean_benign_path.exists():
        raise FileNotFoundError(f"Clean benign dataset not found: {clean_benign_path}")
    if trustairlab_path is None or not trustairlab_path.exists():
        raise FileNotFoundError("TrustAIRLab cleaned snapshot not found. Run Analyze_Dataset_Contamination.py")

    limit = int(os.environ.get("EVAL_LIMIT", "500"))
    if limit == 0:
        limit = None

    print("\nResearch Benign Comparison (Clean vs TrustAIRLab Cleaned)")
    print(f"Clean benign: {clean_benign_path}")
    print(f"TrustAIRLab cleaned: {trustairlab_path}")
    print(f"Sample limit: {limit if limit else 'NONE (full run)'}\n")

    clean_metrics, clean_blocked = evaluate_benign_dataset(
        "Clean_Benign_Corpus_v1", clean_benign_path, "prompt", limit
    )
    trust_metrics, trust_blocked = evaluate_benign_dataset(
        "TrustAIRLab_regular_CLEANED", trustairlab_path, "prompt", limit
    )

    delta_fpr = None
    if clean_metrics.fpr() is not None and trust_metrics.fpr() is not None:
        delta_fpr = trust_metrics.fpr() - clean_metrics.fpr()

    report = {
        "notes": {
            "research_only": True,
            "clean_benign_corpus_is_fpr_gate": True,
        },
        "datasets": {
            "Clean_Benign_Corpus_v1": {
                "path": str(clean_benign_path),
                "metrics": clean_metrics.to_dict(),
                "blocked_examples": clean_blocked,
            },
            "TrustAIRLab_regular_CLEANED": {
                "path": str(trustairlab_path),
                "metrics": trust_metrics.to_dict(),
                "blocked_examples": trust_blocked,
            },
        },
        "delta": {
            "fpr_delta_trustairlab_minus_clean": delta_fpr,
        },
    }

    reports_dir = project_root / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = reports_dir / f"research_benign_comparison_{timestamp}.json"
    md_path = reports_dir / f"research_benign_comparison_{timestamp}.md"

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# Research Benign Comparison\n\n")
        f.write("Side-by-side benign FPR comparison (research-only).\n\n")
        f.write("| Dataset | Total | Blocked | Soft | FPR | Errors |\n")
        f.write("|---|---:|---:|---:|---:|---:|\n")
        f.write(
            "| Clean_Benign_Corpus_v1 | "
            f"{clean_metrics.total} | {clean_metrics.blocked} | {clean_metrics.soft} | "
            f"{format_metric(clean_metrics.fpr())} | {clean_metrics.errors} |\n"
        )
        f.write(
            "| TrustAIRLab_regular_CLEANED | "
            f"{trust_metrics.total} | {trust_metrics.blocked} | {trust_metrics.soft} | "
            f"{format_metric(trust_metrics.fpr())} | {trust_metrics.errors} |\n\n"
        )
        f.write(f"Delta FPR (TrustAIRLab - Clean): {format_metric(delta_fpr)}\n")

    print("Results saved:")
    print(f"- {json_path}")
    print(f"- {md_path}\n")


if __name__ == "__main__":
    main()
