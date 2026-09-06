# Manuscript outline

**Target:** *The First Derivative* — check the current author guidelines for length,
format, and citation style before drafting, and record them here.

## 1. Introduction
Distillation, compression, and fine-tuning are core ML curriculum topics that sit
adjacent to real misuse. State the research question. Claim: the contribution is a
benchmark for the AI-improvement gray area with multi-turn context tracking.

## 2. Background and related work
Six areas from `papers/bibliography.md`. The positioning argument runs through XSTest
and OR-Bench (over-refusal, single-turn, general domains) and HarmBench (broad harm
coverage) to the gap: no benchmark asks whether models track intent across turns in a
domain where the same vocabulary serves both education and misuse.

## 3. Benchmark design
Four categories, four expected-response types. Why `clarify` and `redirect` are
correct answers rather than failures. The control-conversation design and why it is
necessary. Reproduce the decision procedure from `rubric/labeling-rubric.md`.

## 4. Dataset construction
Item counts by category and topic. Paraphrase groups. Two-annotator procedure, Cohen's
kappa, and how disagreements were resolved. Report any rubric amendments — the
amendment history is a finding, not an embarrassment.

## 5. Method
Models and exact revisions. Serving setup, decoding parameters, system-prompt
condition. Response classification and judge validation (kappa against human labels).
Metric definitions with their denominators stated explicitly.

## 6. Results
Per-model table of the six metrics. Single-turn vs. multi-turn gap. Shift-detection
rate at `shift_turn`, and sticky-refusal on controls. Confusion matrix over expected
vs. actual response types. Per-category and per-topic breakdowns.

## 7. Discussion
Where models fail: over-refusal on legitimate research, or failure to notice the
shift? Does refusal behavior transfer across turns or reset? Is `clarify` behavior
present at all, or do models binary-split into answer/refuse?

## 8. Limitations
Small dataset. English only. Prompts authored by one person, so author bias in what
"ambiguous" means. Judge reliability. Open-weight models only — no claim about
frontier systems. Point-in-time model snapshots.

## 9. Ethics
Reproduce and expand `README.md`'s statement. Address the release decision for the
`unsafe` split.

## 10. Conclusion and future work
