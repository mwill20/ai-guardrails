"""
Phase 2.51 — Evaluation Harness (Metrics, Not Vibes)

Runs multiple public prompt-injection / jailbreak datasets through your existing
guardrail pipeline (Phase 2.5) and reports detection + false positives.

You must fill in:
  1) PIPELINE IMPORT (where your run_guardrail_pipeline lives)
  2) RISK EXTRACTION (if your pipeline returns combined risk under a different key)

Everything else is ready to run.

Recommended:
  pip install datasets pandas tqdm
"""

from __future__ import annotations

import csv
import json
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

from tqdm import tqdm

try:
    from datasets import load_dataset  # type: ignore
except Exception as e:
    raise RuntimeError(
        "Missing dependency: datasets. Install with: pip install datasets"
    ) from e


# -----------------------------
# 1) WIRE-UP: Import your pipeline entry point
# -----------------------------
# Add parent directory to path for src module
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import the actual guardrail pipeline function
from src.OWASP_Pipeline_Guardrail import run_guardrail_pipeline


# -----------------------------
# 2) Canonical risk decision rules
# -----------------------------
ATTACK_PRED_RISKS = {"high_risk", "critical"}  # counts as "caught attack"
SOFT_RISKS = {"medium_risk"}  # optional: track separately


@dataclass
class DatasetSpec:
    name: str
    kind: str  # "hf" or "csv"
    source: str  # hf dataset name OR local csv path
    split: Optional[str] = None
    config: Optional[str] = None

    # How to read prompt text + label (if available)
    text_field: Optional[str] = None
    label_field: Optional[str] = None

    # If dataset has labels, which label values mean "attack"?
    attack_label_values: Optional[List[Any]] = None

    # If dataset is attack-only (common), set this True.
    attack_only: bool = False

    # Optional: if dataset includes both "original" + "modified", choose which to score
    prefer_field_order: Optional[List[str]] = None


@dataclass
class Metrics:
    tp: int = 0
    fp: int = 0
    tn: int = 0
    fn: int = 0
    soft_catches: int = 0  # medium_risk on attack rows (optional)
    total: int = 0
    attack_rows: int = 0
    benign_rows: int = 0

    def tpr(self) -> Optional[float]:
        denom = self.tp + self.fn
        return None if denom == 0 else self.tp / denom

    def fpr(self) -> Optional[float]:
        denom = self.fp + self.tn
        return None if denom == 0 else self.fp / denom

    def precision(self) -> Optional[float]:
        denom = self.tp + self.fp
        return None if denom == 0 else self.tp / denom

    def recall(self) -> Optional[float]:
        return self.tpr()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tp": self.tp, "fp": self.fp, "tn": self.tn, "fn": self.fn,
            "soft_catches": self.soft_catches,
            "total": self.total,
            "attack_rows": self.attack_rows,
            "benign_rows": self.benign_rows,
            "tpr": self.tpr(),
            "fpr": self.fpr(),
            "precision": self.precision(),
            "recall": self.recall(),
        }


# -----------------------------
# 3) Robust extraction from pipeline result
# -----------------------------
def extract_combined_risk(result: Dict[str, Any]) -> Optional[str]:
    """
    WIRE-UP BLANK #2 (if needed):
    Adjust this if your pipeline returns combined risk under a different key.

    Supported shapes:
      - {"combined_risk": "..."}
      - {"log_entry": {"combined_risk": "..."}}
      - {"log_entry": {"combined": "..."}}  (if you named it differently)
    """
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
    """
    Runs your existing pipeline with include_raw=False (per your requirement),
    then extracts combined risk.

    NOTE: We do not log raw text in outputs. We only store short previews.
    """
    try:
        res = run_guardrail_pipeline(text, include_raw=False)
    except TypeError:
        # Fallback if pipeline doesn't support include_raw parameter
        res = run_guardrail_pipeline(text)
    combined = extract_combined_risk(res)
    return combined, res


# -----------------------------
# 4) Dataset loading
# -----------------------------
def load_rows_from_csv(path: str) -> List[Dict[str, Any]]:
    with open(path, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def pick_text_field(row: Dict[str, Any], spec: DatasetSpec) -> str:
    # Prefer explicit spec
    if spec.text_field and spec.text_field in row and row[spec.text_field]:
        text = str(row[spec.text_field])
        return text[:8000]  # Cap at 8K chars to prevent ML model slowdowns and memory issues

    # Prefer_field_order fallback
    if spec.prefer_field_order:
        for k in spec.prefer_field_order:
            if k in row and row[k]:
                text = str(row[k])
                return text[:8000]

    # Generic common keys
    for k in ("prompt", "text", "input", "instruction", "query", "modified_prompt", "original_prompt"):
        if k in row and row[k]:
            text = str(row[k])
            return text[:8000]

    # Last resort: stringify the row (not great, but prevents crashes)
    return str(row)[:8000]


def is_attack_row(row: Dict[str, Any], spec: DatasetSpec) -> Optional[bool]:
    """
    Returns:
      True  -> attack
      False -> benign
      None  -> unknown (skip or treat separately)
    """
    # Override: TrustAIRLab regular config contains benign prompts for FPR measurement
    if spec.name.startswith("TrustAIRLab_regular"):
        return False
    
    if spec.attack_only:
        return True

    if spec.label_field and spec.label_field in row:
        val = row[spec.label_field]
        if spec.attack_label_values is None:
            # Heuristic: common label words
            v = str(val).strip().lower()
            if v in ("attack", "jailbreak", "prompt_injection", "injection", "malicious", "true", "1"):
                return True
            if v in ("benign", "safe", "false", "0"):
                return False
            return None

        return val in spec.attack_label_values

    # If no label: unknown
    return None


def load_dataset_rows(spec: DatasetSpec, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    if spec.kind == "csv":
        rows = load_rows_from_csv(spec.source)
        return rows[:limit] if limit else rows

    if spec.kind == "hf":
        ds = load_dataset(spec.source, spec.config) if spec.config else load_dataset(spec.source)
        split = spec.split or ("train" if "train" in ds else list(ds.keys())[0])
        rows = [dict(r) for r in ds[split]]
        return rows[:limit] if limit else rows

    raise ValueError(f"Unknown dataset kind: {spec.kind}")


# -----------------------------
# 5) Scoring + report
# -----------------------------
def score_dataset(spec: DatasetSpec, rows: List[Dict[str, Any]]) -> Tuple[Metrics, List[Dict[str, Any]], List[Dict[str, Any]]]:
    m = Metrics()
    errors: List[Dict[str, Any]] = []
    detailed_logs: List[Dict[str, Any]] = []  # For Pattern_Discovery_Pipeline

    for idx, row in enumerate(tqdm(rows, desc=f"Scoring {spec.name}", leave=False)):
        truth = is_attack_row(row, spec)
        if truth is None and not spec.attack_only:
            # skip rows we can't label
            continue

        text = pick_text_field(row, spec)
        combined_risk, result = pipeline_predict(text)

        if combined_risk is None:
            errors.append({
                "dataset": spec.name,
                "error": "combined_risk_missing",
                "text_preview": text[:120],
                "result_keys": list(result.keys()),
            })
            continue

        pred_attack = combined_risk in ATTACK_PRED_RISKS
        pred_soft = combined_risk in SOFT_RISKS

        m.total += 1
        if truth:
            m.attack_rows += 1
            if pred_attack:
                m.tp += 1
            else:
                m.fn += 1
                # Log first 10 missed attacks (false negatives) for analysis
                fn_count = len([e for e in errors if e.get("type") == "missed_attack"])
                if fn_count < 10:
                    errors.append({
                        "type": "missed_attack",
                        "dataset": spec.name,
                        "text_preview": text[:200],
                        "combined_risk": combined_risk,
                        "semantic_label": result.get("semantic_result", {}).get("label"),
                        "semantic_score": result.get("semantic_result", {}).get("score"),
                        "sanitized_text": result.get("sanitized", "")[:200],
                        "agent_visible": result.get("agent_visible", "")[:200],
                    })
                if pred_soft:
                    m.soft_catches += 1
        else:
            m.benign_rows += 1
            if pred_attack:
                m.fp += 1
                # Debug: Log first 5 false positives to understand what's happening
                if len([e for e in errors if e.get("type") == "false_positive"]) < 5:
                    errors.append({
                        "type": "false_positive",
                        "dataset": spec.name,
                        "text_preview": text[:100],
                        "combined_risk": combined_risk,
                        "semantic_label": result.get("semantic_result", {}).get("label"),
                        "semantic_score": result.get("semantic_result", {}).get("score"),
                    })
            else:
                m.tn += 1
        
        # Save detailed log for Pattern_Discovery_Pipeline
        semantic_result = result.get("semantic_result", {})
        detailed_logs.append({
            "prompt_id": f"{spec.name}_{idx}",
            "dataset": spec.name,
            "prompt": text,
            "ground_truth": "attack" if truth else "benign",
            "combined_risk": combined_risk,
            "action": "blocked" if pred_attack else ("sanitize" if pred_soft else "allow"),
            "semantic_label": semantic_result.get("label"),
            "jailbreak_prob": semantic_result.get("score") if semantic_result.get("label") == "INJECTION" else (1.0 - semantic_result.get("score", 0.0)),
            "deterministic_risk": result.get("deterministic_risk"),
            "owasp_codes": result.get("log_entry", {}).get("owasp_codes", []),
        })

    return m, errors, detailed_logs


def format_metric(x: Optional[float]) -> str:
    return "N/A" if x is None else f"{x:.3f}"


def main() -> None:
    # Dataset collection for comprehensive guardrail evaluation
    DATASETS: List[DatasetSpec] = [
        DatasetSpec(
            name="Lakera_mosscap_prompt_injection",
            kind="hf",
            source="Lakera/mosscap_prompt_injection",
            split="train",
            text_field="prompt",
            attack_only=True,
        ),
        DatasetSpec(
            name="Mindgard_evaded_injections_jailbreaks",
            kind="hf",
            source="Mindgard/evaded-prompt-injection-and-jailbreak-samples",
            split="train",
            prefer_field_order=["modified_prompt", "original_prompt", "prompt", "text"],
            attack_only=True,
        ),
        DatasetSpec(
            name="TrustAIRLab_jailbreak_2023_12_25",
            kind="hf",
            source="TrustAIRLab/in-the-wild-jailbreak-prompts",
            config="jailbreak_2023_12_25",
            split="train",
            attack_only=True,
        ),
        # BENIGN DATASET: TrustAIRLab regular config contains normal/safe prompts.
        # This is CRITICAL for calculating FPR (False Positive Rate) - without benign data,
        # we cannot measure how often the guardrail incorrectly blocks safe prompts.
        DatasetSpec(
            name="TrustAIRLab_regular_2023_12_25",
            kind="hf",
            source="TrustAIRLab/in-the-wild-jailbreak-prompts",
            config="regular_2023_12_25",
            split="train",
            attack_only=False,  # Benign prompts for FPR calculation
        ),
        DatasetSpec(
            name="xTRam1_safe_guard_prompt_injection",
            kind="hf",
            source="xTRam1/safe-guard-prompt-injection",
            split="train",
            attack_only=True,
        ),
        # Commented out - CSV file not available locally
        # DatasetSpec(
        #     name="Giskard_prompt_injections_csv",
        #     kind="csv",
        #     source=os.environ.get("GISKARD_PROMPT_INJECTIONS_CSV", "prompt_injections.csv"),
        #     attack_only=True,
        # ),
    ]

    # EVAL_LIMIT: Default 500 samples per dataset for balanced evaluation.
    # - 500 samples = ~10-15 min total runtime (manageable iteration speed)
    # - Provides statistical significance for TPR/FPR metrics
    # - Set EVAL_LIMIT=0 for full dataset runs (~12-18 hours)
    # - Set EVAL_LIMIT=100 for quick smoke tests (~2-3 min)
    limit = int(os.environ.get("EVAL_LIMIT", "500"))
    if limit == 0:
        limit = None  # None means process all samples (no limit)

    results: Dict[str, Any] = {
        "attack_pred_risks": sorted(list(ATTACK_PRED_RISKS)),
        "datasets": {},
        "errors": [],
        "notes": {
            "fpr_requires_benign": (
                "Many jailbreak datasets are attack-only. FPR is only meaningful when a dataset includes benign rows."
            ),
        },
        "design_review_summary": {},
    }

    # Create eval logs directory
    os.makedirs("reports/evals", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    print("\nPhase 2.51 — Evaluation Harness (Metrics, Not Vibes)")
    print(f"Sample limit per dataset: {limit if limit else 'NONE (full run)'}\n")
    for spec in DATASETS:
        rows = load_dataset_rows(spec, limit=limit)
        metrics, errors, detailed_logs = score_dataset(spec, rows)

        results["datasets"][spec.name] = {
            "spec": {
                "kind": spec.kind,
                "source": spec.source,
                "split": spec.split,
                "attack_only": spec.attack_only,
            },
            "metrics": metrics.to_dict(),
        }
        results["errors"].extend(errors)
        
        # Save detailed logs for Pattern_Discovery_Pipeline
        log_filename = f"eval_{timestamp}_{spec.name}.jsonl"
        log_path = os.path.join("reports", "evals", log_filename)
        with open(log_path, "w", encoding="utf-8") as f:
            for log_entry in detailed_logs:
                f.write(json.dumps(log_entry) + "\n")

        print(f"- {spec.name}")
        print(f"  rows_scored: {metrics.total} (attack={metrics.attack_rows}, benign={metrics.benign_rows})")
        print(f"  TPR (detect attacks): {format_metric(metrics.tpr())}")
        print(f"  FPR (false alarms):  {format_metric(metrics.fpr())}")
        print(f"  Precision:           {format_metric(metrics.precision())}")
        print(f"  Recall:              {format_metric(metrics.recall())}")
        if metrics.soft_catches:
            print(f"  soft_catches(medium on attacks): {metrics.soft_catches}")
        if errors:
            print(f"  errors: {len(errors)} (see JSON output)")
        print()

    # Calculate design review summary
    tpr_values = []
    fpr_values = []
    for dname, d in results["datasets"].items():
        met = d["metrics"]
        if met.get("tpr") is not None:
            tpr_values.append(met["tpr"])
        if met.get("fpr") is not None:
            fpr_values.append(met["fpr"])

    summary = {
        "tpr_mean": sum(tpr_values) / len(tpr_values) if tpr_values else None,
        "fpr_mean": sum(fpr_values) / len(fpr_values) if fpr_values else None,
        "tpr_count": len(tpr_values),
        "fpr_count": len(fpr_values),
        "interpretation": (
            "If average TPR is high across attack datasets and FPR is low on benign prompts, "
            "the guardrail is measurably effective (not vibes). If TPR is low, the semantic layer is under-catching. "
            "If FPR is high, thresholds/pattern overrides are too aggressive."
        ),
        "next_professional_step": (
            "Add a clearly labeled benign dataset (or your own benign corpus) and report FPR with confidence intervals. "
            "Then tune thresholds (e.g., 0.60/0.85) and re-run to show improvement."
        ),
    }
    results["design_review_summary"] = summary

    print("=" * 60)
    print("DESIGN REVIEW SUMMARY")
    print("=" * 60)
    print(f"  Mean TPR (across {summary['tpr_count']} datasets): {format_metric(summary['tpr_mean'])}")
    print(f"  Mean FPR (across {summary['fpr_count']} datasets): {format_metric(summary['fpr_mean'])}")
    print(f"\n  Interpretation:")
    print(f"    {summary['interpretation']}")
    print(f"\n  Next Professional Step:")
    print(f"    {summary['next_professional_step']}")
    print("=" * 60)
    print()

    os.makedirs("reports", exist_ok=True)
    
    # Generate timestamped filename to preserve eval history
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join("reports", f"phase_2_51_eval_results_{timestamp}.json")
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"Saved results to: {out_path}\n")


if __name__ == "__main__":
    main()
