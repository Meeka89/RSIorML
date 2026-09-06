"""Run models against the benchmark and write raw outputs.

    python -m src.run_eval --model echo                       # offline smoke test
    python -m src.run_eval --model Qwen/Qwen2.5-7B-Instruct   # against a served model

Writes results/raw/<model>__<timestamp>.jsonl, one record per turn. Raw files are
append-only artifacts: never edit or overwrite them. Scoring reads from here.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import platform
import sys
from pathlib import Path

from .providers import ProviderError, get_provider
from .schema import ROOT, load_items

RAW_DIR = ROOT / "results" / "raw"

# No system prompt by default: the research question is about the model's own
# contextual judgment, not about how well a prompt we wrote steers it. Runs with a
# system prompt are a separate condition and must be recorded in the manifest.
DEFAULT_SYSTEM = None


def slugify(name: str) -> str:
    return "".join(c if c.isalnum() or c in "-._" else "-" for c in name)


def run(model: str, out_path: Path, system: str | None, limit: int | None,
        category: str | None, seed_note: str) -> int:
    items = load_items()
    if category:
        items = [i for i in items if i.category == category]
    if limit:
        items = items[:limit]

    provider = get_provider(model)
    started = dt.datetime.now(dt.timezone.utc).isoformat()
    manifest = {
        "record_type": "manifest",
        "model": model,
        "started_utc": started,
        "system_prompt": system,
        "temperature": provider.temperature,
        "max_tokens": provider.max_tokens,
        "n_items": len(items),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "note": seed_note,
    }

    out_path.parent.mkdir(parents=True, exist_ok=True)
    errors = 0
    with out_path.open("w", encoding="utf-8") as out:
        out.write(json.dumps(manifest) + "\n")

        for n, item in enumerate(items, 1):
            history: list[dict] = []
            print(f"[{n}/{len(items)}] {item.id}", flush=True)

            for turn_idx, user_turn in enumerate(item.turns, 1):
                history.append({"role": "user", "content": user_turn})
                record = {
                    "record_type": "response",
                    "item_id": item.id,
                    "category": item.category,
                    "topic": item.topic,
                    "turn": turn_idx,
                    "n_turns": len(item.turns),
                    "shift_turn": item.shift_turn,
                    "paraphrase_group": item.paraphrase_group,
                    "expected_response": item.expected_response[turn_idx - 1],
                    "prompt": user_turn,
                    "model": model,
                }
                try:
                    reply = provider.complete(history, system=system)
                    record["response"] = reply
                    record["error"] = None
                except ProviderError as exc:
                    # Record and continue: one dead turn shouldn't lose the whole run.
                    reply = ""
                    record["response"] = ""
                    record["error"] = str(exc)
                    errors += 1
                    print(f"    turn {turn_idx} failed: {exc}", file=sys.stderr)

                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                # The model's own reply becomes context for the next turn -- this is
                # what makes multi-turn context-shift measurable.
                history.append({"role": "assistant", "content": reply})

    print(f"\nwrote {out_path}")
    if errors:
        print(f"{errors} turn(s) errored; they are marked in the file and excluded from metrics")
    return 1 if errors else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", required=True, help="model id, or 'echo' for an offline run")
    ap.add_argument("--out", type=Path, default=None)
    ap.add_argument("--system", default=DEFAULT_SYSTEM, help="optional system prompt (separate condition)")
    ap.add_argument("--limit", type=int, default=None, help="run only the first N items")
    ap.add_argument("--category", default=None, help="restrict to one category")
    ap.add_argument("--note", default="", help="free-text note stored in the manifest")
    args = ap.parse_args()

    out = args.out
    if out is None:
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        out = RAW_DIR / f"{slugify(args.model)}__{stamp}.jsonl"
    return run(args.model, out, args.system, args.limit, args.category, args.note)


if __name__ == "__main__":
    raise SystemExit(main())
