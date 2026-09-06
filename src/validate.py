"""Check every dataset item against data/schema.md.

    python -m src.validate

Exits non-zero on any error, so it can gate a commit or CI run.
"""

from __future__ import annotations

import sys
from collections import defaultdict

from .schema import CATEGORIES, RESPONSES, STATUSES, TOPICS, Item, load_items


def check(items: list[Item]) -> list[str]:
    errors: list[str] = []
    seen: dict[str, int] = defaultdict(int)

    for it in items:
        seen[it.id] += 1
        where = f"[{it.id}]"

        if it.category not in CATEGORIES:
            errors.append(f"{where} unknown category {it.category!r}")
        if it.topic not in TOPICS:
            errors.append(f"{where} unknown topic {it.topic!r}")
        if it.status not in STATUSES:
            errors.append(f"{where} unknown status {it.status!r}")

        for label in it.expected_response:
            if label not in RESPONSES:
                errors.append(f"{where} unknown expected_response {label!r}")

        if len(it.turns) != len(it.expected_response):
            errors.append(
                f"{where} {len(it.turns)} turns but "
                f"{len(it.expected_response)} expected_response labels"
            )
        if not it.rationale.strip():
            errors.append(f"{where} empty rationale (the rubric requires one)")
        if any(not t.strip() for t in it.turns):
            errors.append(f"{where} empty turn text")

        multi = it.is_multi_turn
        if multi and it.category != "multi_turn_shift":
            errors.append(f"{where} multi-turn item must have category multi_turn_shift")
        if it.category == "multi_turn_shift":
            if not multi:
                errors.append(f"{where} multi_turn_shift item has only one turn")
            if it.shift_turn != -1 and not 1 <= it.shift_turn <= len(it.turns):
                errors.append(f"{where} shift_turn {it.shift_turn} out of range")

    for item_id, count in seen.items():
        if count > 1:
            errors.append(f"[{item_id}] duplicate id ({count} occurrences)")

    # Paraphrase groups must agree on both labels, or the consistency metric is
    # measuring label noise instead of model consistency.
    groups: dict[str, list[Item]] = defaultdict(list)
    for it in items:
        if it.paraphrase_group:
            groups[it.paraphrase_group].append(it)
    for name, members in groups.items():
        if len(members) < 2:
            errors.append(f"[{name}] paraphrase group has only one member")
        cats = {m.category for m in members}
        exps = {tuple(m.expected_response) for m in members}
        if len(cats) > 1:
            errors.append(f"[{name}] members disagree on category: {sorted(cats)}")
        if len(exps) > 1:
            errors.append(f"[{name}] members disagree on expected_response: {sorted(exps)}")

    return errors


def main() -> int:
    items = load_items(include_retired=True)
    errors = check(items)
    if errors:
        print(f"{len(errors)} problem(s) found:", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1

    active = [i for i in items if i.status == "active"]
    by_cat: dict[str, int] = defaultdict(int)
    for it in active:
        by_cat[it.category] += 1
    print(f"OK - {len(active)} active items ({len(items) - len(active)} retired)")
    for cat in sorted(by_cat):
        print(f"  {cat:<18} {by_cat[cat]:>4}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
