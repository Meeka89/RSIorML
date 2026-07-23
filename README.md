# Context-Aware Safety Benchmark for AI-Improvement Prompts

A benchmark evaluating whether open-weight LLMs can use conversational context to distinguish legitimate AI research questions from requests that may facilitate model extraction, unsafe distillation, or recursive self-improvement.

**Author:** Michael Kelley
**Advisor:** Dr. Joe Faith, Harding University, Department of Computer Science
**Target venue:** *The First Derivative* (undergraduate research journal for CS & AI)
**Timeline:** August 2026 – March 2027

## Motivation

Questions about distillation, model compression, fine-tuning, and alignment are core to legitimate ML education and research. But the same topics border on misuse: unauthorized model imitation, safety-removal fine-tuning, and AI-assisted AI development. Existing safety benchmarks focus on broad harmful-content refusal, jailbreaks, or over-refusal (e.g., XSTest, OR-Bench). Few examine the gray area between AI research and AI-improvement misuse — and fewer still test whether models can track a conversation's *shift* from legitimate to suspect intent across turns.

**Research question:** Can open-weight LLMs use conversational context to distinguish legitimate AI research from requests that may lead to model extraction, unsafe distillation, or recursive self-improvement?

## Benchmark design

Prompts fall into four categories:

1. **Clearly legitimate** — standard AI research/education questions
2. **Clearly unsafe** — explicit AI-improvement misuse requests
3. **Ambiguous single-turn** — context-dependent prompts with unclear intent
4. **Multi-turn context-shift** — conversations that begin legitimately and drift toward unauthorized imitation or detection-avoidance

Each item is labeled with an expected response type: normal helpful response, clarifying response, safe redirection, or refusal.

## Evaluation metrics

- False refusal rate on legitimate research prompts
- False compliance rate on suspicious AI-improvement prompts
- Clarification rate on ambiguous prompts
- Safe-redirect rate on risky prompts
- Consistency across paraphrases
- Single-turn vs. multi-turn performance gap

## Repository structure

```
├── README.md
├── papers/              # Annotated bibliography and reading notes
├── data/
│   ├── prompts/         # Labeled single-turn prompts by category
│   └── conversations/   # Multi-turn context-shift dialogues
├── rubric/              # Labeling rubric and annotation guidelines
├── src/
│   ├── run_eval.py      # Runs models against the benchmark
│   └── score.py         # Computes metrics from raw outputs
├── results/
│   ├── raw/             # Full model outputs (never overwrite)
│   └── analysis/        # Scored results, figures, tables
├── paper/               # Manuscript drafts
└── log.md               # Dated research log
```

## Models evaluated

*(To be finalized September 2026 — 3–4 open-weight instruction-tuned models, e.g., Llama, Qwen, Mistral families.)*

## Ethics statement

This project studies model *behavior in response to* extraction- and distillation-related prompts; it does not perform model extraction or unauthorized distillation. All experiments use open-weight models under their published licenses. The dataset contains prompts designed to probe safety boundaries and is released for research purposes with expected-response labels attached.

## Status

- [ ] Literature review & scoping (Aug–Sep)
- [ ] Benchmark design & rubric (Oct)
- [ ] Dataset construction & pilot (Nov)
- [ ] Full experiments (Dec)
- [ ] Analysis & drafting (Jan)
- [ ] Revision cycles (Feb)
- [ ] Submission (Mar)
