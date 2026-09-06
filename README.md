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
├── log.md                   # Dated research log -- decisions and rationale
├── requirements.txt
├── docs/proposal/           # Original project proposal (md + pdf)
├── papers/
│   ├── bibliography.md      # Annotated bibliography by background area
│   └── reading-notes.md     # Per-paper notes
├── data/
│   ├── schema.md            # Authoritative field reference for both datasets
│   ├── prompts/             # Single-turn labeled prompts (categories 1-3)
│   └── conversations/       # Multi-turn context-shift dialogues (category 4)
├── rubric/
│   ├── labeling-rubric.md   # How items get their category and expected response
│   └── scoring-rubric.md    # How model responses get classified
├── src/
│   ├── schema.py            # Vocabularies and item loading
│   ├── validate.py          # Dataset validation
│   ├── providers.py         # Model backends (OpenAI-compatible HTTP)
│   ├── classify.py          # Response classification + judge agreement
│   ├── run_eval.py          # Runs models against the benchmark
│   └── score.py             # Computes metrics from raw outputs
├── results/
│   ├── raw/                 # Full model outputs (append-only, never overwrite)
│   └── analysis/            # Scored results, metrics, figures
└── paper/
    └── outline.md           # Manuscript outline
```

## Quick start

The pipeline needs only the Python standard library. Verify the dataset and run the
offline smoke test:

```bash
python -m src.validate
```

```bash
python -m src.run_eval --model echo --limit 3
```

To evaluate a real model, serve it over an OpenAI-compatible endpoint (vLLM, Ollama,
or `llama.cpp`), point the harness at it, then score the run:

```bash
export BENCH_BASE_URL=http://localhost:8000/v1
```

```bash
python -m src.run_eval --model Qwen/Qwen2.5-7B-Instruct
```

```bash
python -m src.score results/raw/<the-file-just-written>.jsonl
```

`score.py` defaults to a keyword heuristic, which is for pilot runs only. Reported
numbers require a judge validated against human labels — see `rubric/scoring-rubric.md`.

## Working conventions

- **Add a dataset item** by appending one line to the relevant `.jsonl`, with a
  `rationale` written per `rubric/labeling-rubric.md`. Run `python -m src.validate`
  before committing.
- **Never edit `results/raw/`.** Superseded runs stay in place; note why in `log.md`.
- **Record design decisions in `log.md`, not just in commit messages.** The methods
  section gets written from that file.
- **Item IDs are permanent.** Retire with `"status": "retired"`; never reuse an ID.

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
