# Research log

Dated, append-only. One entry per working session: what was done, what was decided and
why, what is next. Decisions recorded here are what the methods section gets written
from — do not rely on memory or on git history alone.

Format: `## YYYY-MM-DD` then `**Done** / **Decided** / **Next**`.

---

## 2026-09-06

**Done**
- Set up repository structure per the plan in `README.md`.
- Moved the original proposal to `docs/proposal/` (`.md` and `.pdf`).
- Wrote `data/schema.md`, the labeling rubric, and the scoring rubric.
- Seeded 15 single-turn prompts and 4 multi-turn conversations as design examples.
- Built the pipeline: `src/run_eval.py` -> `results/raw/` -> `src/score.py` ->
  `results/analysis/`. Verified end to end with the offline `echo` provider.
- Wrote `docs/handbook.md` -- the full project guide covering research design,
  annotation methodology, the ML background, metrics, timeline, and failure modes.

**Decided**
- *Models are served over an OpenAI-compatible HTTP API* (vLLM / Ollama / llama.cpp)
  rather than loaded in-process. One code path for every model, and the harness runs
  on a laptop while the model runs elsewhere.
- *No system prompt by default.* The research question is about the model's own
  contextual judgment. Runs with a system prompt are a separate experimental
  condition and must be recorded in the run manifest.
- *Conversations store user turns only.* The model's real replies become the history
  at eval time; pre-written assistant turns would leak expected behavior and test the
  model against a script it never produced.
- *Every context-shift conversation needs a benign control* sharing its early turns
  (see `shift-control-001`). Without controls, a model that pattern-matches on
  distillation vocabulary is indistinguishable from one that tracks context — which
  is the entire research question.
- *Rates over empty denominators report `null`, not 0.0.* An undefined rate and a
  rate of zero mean different things in a results table.
- *The heuristic classifier is a pilot tool only.* Reported numbers require a judge
  validated against human labels at kappa >= 0.8.
- *`docs/handbook.md` is orientation, not specification.* It will drift as the project
  develops. `rubric/`, `data/schema.md` and this log stay authoritative; when the
  handbook contradicts them, the handbook is what's wrong.

**Next**
- Read `rottger2024xstest` and verify the positioning claim in
  `papers/bibliography.md` against 2025-2026 work. The contribution statement depends
  on that gap being real.
- Decide the target dataset size per category, and how many paraphrases per item.
- Choose the 3-4 open-weight models (README says finalize this month).
- Pick a license for code and for data — they may differ, and the data license needs
  thought given the prompt content. See the open question below.

**Open questions**
- License: code and dataset. Unresolved.
- Second annotator for the kappa requirement in the rubric — who?
- Does the `unsafe` split get released publicly, or held back and described? Weigh
  reproducibility against providing a ready-made misuse prompt set.
