#!/usr/bin/env python3
"""Merge new rule entries into rules.json without duplicating existing names."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RULES_JSON = REPO_ROOT / "rules.json"
BATCH_JSON = Path(__file__).resolve().parent / "new_rules_batch.json"


def main() -> None:
    with RULES_JSON.open(encoding="utf-8") as handle:
        catalog = json.load(handle)

    with BATCH_JSON.open(encoding="utf-8") as handle:
        batch = json.load(handle)

    existing = {entry["name"] for entry in catalog["libraries"]}
    added = []
    for entry in batch["libraries"]:
        if entry["name"] in existing:
            continue
        catalog["libraries"].append(entry)
        added.append(entry["name"])

    catalog["libraries"].sort(key=lambda item: item["name"])

    with RULES_JSON.open("w", encoding="utf-8") as handle:
        json.dump(catalog, handle, indent=2)
        handle.write("\n")

    print(f"Added {len(added)} new libraries to rules.json")
    if added:
        print(", ".join(added))


if __name__ == "__main__":
    main()
