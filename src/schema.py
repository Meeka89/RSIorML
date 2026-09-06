"""Vocabularies and item loading. The single source of truth is data/schema.md;
this module encodes it so that malformed items fail fast rather than silently."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROMPTS_PATH = ROOT / "data" / "prompts" / "prompts.jsonl"
CONVERSATIONS_PATH = ROOT / "data" / "conversations" / "conversations.jsonl"

CATEGORIES = {"legitimate", "unsafe", "ambiguous", "multi_turn_shift"}
RESPONSES = {"normal", "clarify", "redirect", "refuse"}
TOPICS = {
    "distillation", "extraction", "compression", "fine_tuning",
    "safety_removal", "rsi", "alignment", "evaluation", "detection_evasion",
}
STATUSES = {"active", "retired"}


@dataclass
class Item:
    """One benchmark item. Single-turn items have a one-element `turns` list."""

    id: str
    category: str
    topic: str
    turns: list[str]
    expected_response: list[str]
    rationale: str
    source: str
    status: str = "active"
    paraphrase_group: str | None = None
    shift_turn: int = -1
    raw: dict = field(default_factory=dict, repr=False)

    @property
    def is_multi_turn(self) -> bool:
        return len(self.turns) > 1


def _read_jsonl(path: Path) -> list[dict]:
    items = []
    with path.open(encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            try:
                items.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path.name}:{lineno}: invalid JSON: {exc}") from exc
    return items


def load_items(include_retired: bool = False) -> list[Item]:
    """Load both files into one uniform list of Items."""
    items: list[Item] = []

    for row in _read_jsonl(PROMPTS_PATH):
        items.append(Item(
            id=row["id"],
            category=row["category"],
            topic=row["topic"],
            turns=[row["prompt"]],
            expected_response=[row["expected_response"]],
            rationale=row.get("rationale", ""),
            source=row.get("source", "author"),
            status=row.get("status", "active"),
            paraphrase_group=row.get("paraphrase_group"),
            raw=row,
        ))

    for row in _read_jsonl(CONVERSATIONS_PATH):
        items.append(Item(
            id=row["id"],
            category=row["category"],
            topic=row["topic"],
            turns=[t["content"] for t in row["turns"]],
            expected_response=list(row["expected_response"]),
            rationale=row.get("rationale", ""),
            source=row.get("source", "author"),
            status=row.get("status", "active"),
            paraphrase_group=row.get("paraphrase_group"),
            shift_turn=row.get("shift_turn", -1),
            raw=row,
        ))

    if not include_retired:
        items = [i for i in items if i.status == "active"]
    return items
