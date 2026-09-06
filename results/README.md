# Results

## `raw/`

One JSONL file per run: `<model>__<YYYYMMDD-HHMMSS>.jsonl`. Line 1 is a manifest
(model, decoding parameters, system-prompt condition, timestamp, platform); every
other line is one turn's prompt and response.

**These files are append-only experimental records. Never edit or overwrite one.**
If a run was wrong, keep it, and note in `log.md` why it was superseded. They are
committed to git on purpose — see `.gitignore`.

## `analysis/`

Derived from `raw/` by `src/score.py`, and regenerable at any time:

- `<stem>.scored.jsonl` — per-turn records with `actual_response` and `correct`
- `<stem>.metrics.json` — the six metrics plus per-category and confusion tables

Figures and tables for the paper also live here.
