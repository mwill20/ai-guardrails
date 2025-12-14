# Model Size & Fine-Tuning Requirements for `madhurjindal/Jailbreak-Detector-Large`

## 1. Model Size Overview

### Base Model
- **Architecture:** `microsoft/mdeberta-v3-base`
- **Parameter Count:** ~280 million (0.28B)
- **Reported Size:** ~0.3B parameters

### Memory Footprint (Inference)

**FP32 calculation:**

- Parameters: **280,000,000**
- FP32 = **4 bytes per parameter**

```
280,000,000 × 4 = 1,120,000,000 bytes
```

Convert to GiB:

```
1,120,000,000 / 1,073,741,824 ≈ 1.04 GiB
```

**Inference memory footprint:**  
≈ **1.0–1.1 GiB**

Plus small overhead for:
- tokenizer  
- pipeline buffers  
- activations  

Total: **1.2–1.5 GiB** (very manageable).

---

## 2. Do We Need to Post-Train This Model?

**Short answer:**  
No — not for Phase 2.5.

The model is:
- Already fine-tuned specifically for **jailbreak detection**
- Reported to achieve **~98% accuracy** on its domain
- Suitable for immediate use in the semantic guardrail pipeline

Phase 2.5 only requires:
- Integrating a real model  
- Mapping model output to semantic risk levels  
- Logging + evaluation  

**Fine-tuning is optional**, not required.

---

## 3. Fine-Tuning Requirements (If Needed Later)

Below are *planning calculations* for future phases.

---

## 3.1 Full Fine-Tuning Memory Requirements

When doing full fine-tuning using AdamW:

### Components in VRAM
| Component | Memory |
|----------|--------|
| FP16 forward weights | 0.52 GiB |
| FP32 master weights | 1.04 GiB |
| Gradients (FP16) | 0.52 GiB |
| AdamW states (m+v, FP32) | 2.08 GiB |

### Total Optimizer + Weights

```
0.52 + 1.04 + 0.52 + 2.08 = 4.16 GiB
```

### Add Activations
Activation memory depends on:
- sequence length (default 512)
- batch size (8–16)
- number of layers (DeBERTa-base depth)

Typical range: **2–6 GiB**

### Total VRAM for Full Fine-Tune
```
4.16 GiB + 3–6 GiB = ~8–12 GiB
```

**Recommended GPU for full training:**  
- 16GB (T4, V100, A10G, RTX 4090)  
- 24GB gives more flexibility  

---

## 3.2 LoRA / PEFT Fine-Tuning Requirements

Using LoRA:
- Base weights frozen
- Only small adapter matrices trained

VRAM costs:

| Component | Estimated |
|----------|-----------|
| FP16 weights | ~0.52 GiB |
| LoRA weights + optimizer | ~0.2–0.5 GiB |
| Activations | 2–4 GiB |

### Total VRAM for LoRA Fine-Tune
```
~3–6 GiB
```

**Meaning:**  
- Fits on an **8GB GPU**  
- Easy to run on **Colab T4** with adjusted batch size  

---

## 4. Dataset Size Considerations (For Future Post-Training)

Typical domain adaptation training needs:
- 10k–100k labeled prompts (benign vs jailbreak)
- ~200 tokens per prompt

```
100,000 × 200 = 20 million tokens
```

Storage requirement: **negligible**  
Curation requirement: **high** (the expensive part).

---

## 5. Summary Table

| Task | VRAM Needed | Notes |
|------|-------------|-------|
| **Inference only** | **1.2–1.5 GB** | Easy on CPU or GPU |
| **LoRA fine-tune** | **3–6 GB** | Fits on Colab |
| **Full fine-tune** | **8–12 GB** | Needs 16GB GPU for comfort |

---

## 6. Recommendation for This Project Phase

For **Phase 2.5**, use the model **as-is**:

- No fine-tuning required  
- Focus on integration, evaluation, logging, and risk mapping  
- Fine-tuning can occur in Phase 3 or 4 if evaluation reveals gaps  

This aligns with your NorthStar and keeps development efficient and realistic.
