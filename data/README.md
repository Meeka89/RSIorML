# Dataset

Two files hold the benchmark. Both are JSON Lines (one JSON object per line) so that
items can be appended, diffed, and reviewed one at a time in version control.

- `prompts/prompts.jsonl` — single-turn items (categories 1–3)
- `conversations/conversations.jsonl` — multi-turn context-shift items (category 4)

`schema.md` is the authoritative field reference. `python -m src.validate` checks
every item against it and fails loudly on anything malformed.

## ID convention

`<category-prefix>-<topic>-<nnn>`, e.g. `leg-distill-001`, `uns-safetyremoval-004`,
`amb-extract-012`, `shift-imitation-003`.

Prefixes: `leg` (legitimate), `uns` (unsafe), `amb` (ambiguous), `shift` (multi-turn).

IDs are permanent. If an item is retired, mark it `"status": "retired"` rather than
deleting the line or reusing the ID — published results reference IDs.

## Paraphrase groups

Consistency-across-paraphrases is one of the six metrics, so several items share a
`paraphrase_group`. Every member of a group must carry the same `category` and
`expected_response`; only the surface wording changes. `validate` enforces this.
