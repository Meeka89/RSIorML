# Annotated bibliography

Reading list organized by the six background areas in the proposal. Entries are
starting points, **not verified citations** — before any of these appears in the
manuscript, pull the actual paper, confirm authors/venue/year, and fill in the
annotation. Move an entry to "Read" only once its annotation is written.

Citation keys used here are what `source` fields in the dataset should reference.

## Status

| | |
|---|---|
| To read | everything below |
| Read + annotated | none yet |

---

## 1. Distillation and model compression

- **`hinton2015distilling`** — Hinton, Vinyals, Dean. *Distilling the Knowledge in a
  Neural Network.* arXiv:1503.02531. The origin of temperature-softened logit
  transfer; grounds the `distillation` topic items.
- **`wang2023selfinstruct`** — Wang et al. *Self-Instruct.* Bootstrapping instruction
  data from a model's own generations — relevant to where distillation shades into
  imitation.

## 2. Model extraction

- **`tramer2016stealing`** — Tramèr et al. *Stealing Machine Learning Models via
  Prediction APIs.* USENIX Security 2016. The canonical extraction-via-API threat
  model; directly underwrites `amb-extract-001`.
- **`carlini2024stealing`** — Carlini et al. *Stealing Part of a Production Language
  Model.* Extraction against deployed LLM APIs; establishes that the ambiguous items
  describe a real capability, not a hypothetical.

## 3. Recursive self-improvement and AI R&D acceleration

- **`bostrom2014superintelligence`** — Bostrom. *Superintelligence.* Source of the
  standard RSI framing; cite for terminology, not for empirical claims.
- **METR RE-Bench** — evaluations of AI agents on ML research engineering tasks.
  Useful for the "is this near-term?" framing in `leg-rsi-001`.
- **Frontier-lab policy documents** on AI R&D capability thresholds. Cite the current
  published versions; check for revisions before submission.

## 4. AI safety benchmarks

- **`mazeika2024harmbench`** — Mazeika et al. *HarmBench.* Standardized red-teaming
  evaluation. Contrast: broad harm coverage, not the AI-improvement gray area.
- **`zou2023universal`** — Zou et al. *Universal and Transferable Adversarial Attacks
  on Aligned Language Models.* Jailbreak robustness; a different axis than ours.

## 5. Over-refusal and under-refusal

- **`rottger2024xstest`** — Röttger et al. *XSTest: A Test Suite for Identifying
  Exaggerated Safety Behaviours in LLMs.* NAACL 2024. **Closest prior work.** Same
  safe/unsafe-contrast design; different domain, and single-turn only. The gap this
  project fills is stated relative to this paper — read it first.
- **`cui2024orbench`** — Cui et al. *OR-Bench: An Over-Refusal Benchmark for Large
  Language Models.* Scale over over-refusal; again single-turn.

## 6. Instruction tuning and alignment behavior

- **`qi2024finetuning`** — Qi et al. *Fine-tuning Aligned Language Models Compromises
  Safety, Even When Users Do Not Intend To!* ICLR 2024. Empirical basis for treating
  safety-removal fine-tuning as a live risk rather than a hypothetical.
- **`lermen2023lora`** — Lermen et al. *LoRA Fine-tuning Efficiently Undoes Safety
  Training.* Grounds `uns-safetyremoval-002`.
- **`bai2022constitutional`** — Bai et al. *Constitutional AI.* Background on how
  refusal behavior is trained in the first place.

---

## Positioning note (draft)

XSTest and OR-Bench both test whether models over-refuse safe prompts that *resemble*
unsafe ones — but within single turns, and in general harm domains. HarmBench and the
jailbreak literature test robustness to adversarial pressure. Neither line asks
whether a model tracks intent *across* turns in a domain where the same vocabulary
serves education and misuse. That intersection — AI-improvement topics, multi-turn,
with `clarify` and `redirect` as first-class correct answers rather than failures — is
the claimed contribution. **Verify this gap holds by searching the 2025-2026
literature before committing to it in the paper.**
