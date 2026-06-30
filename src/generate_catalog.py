#!/usr/bin/env python3
"""Generate docs/catalog.json and sync fork-specific URLs across the repo."""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

try:
    from repo_config import REPO_ROOT, get_repo_config
except ModuleNotFoundError:
    from src.repo_config import REPO_ROOT, get_repo_config

RULES_JSON = REPO_ROOT / "rules.json"
CUSTOM_RULES_JSON = REPO_ROOT / "custom-rules.json"
STACKS_JSON = REPO_ROOT / "stacks.json"
ALIASES_JSON = REPO_ROOT / "install_aliases.json"
QUICK_INSTALL_SRC = REPO_ROOT / "src" / "quick_install.py"
QUICK_INSTALL_DOCS = REPO_ROOT / "docs" / "quick_install.py"
OUTPUT = REPO_ROOT / "docs" / "catalog.json"
INSTALL_SH = REPO_ROOT / "install.sh"


def sync_install_sh(config) -> None:
    content = INSTALL_SH.read_text(encoding="utf-8")
    content = re.sub(r'^REPO=".*"$', f'REPO="{config.repo}"', content, flags=re.MULTILINE)
    content = re.sub(r'^BRANCH=".*"$', f'BRANCH="{config.branch}"', content, flags=re.MULTILINE)

    raw_install = config.install_sh_url
    content = re.sub(
        r"https://raw\.githubusercontent\.com/[^/]+/[^/]+/[^/]+/install\.sh",
        raw_install,
        content,
    )
    INSTALL_SH.write_text(content, encoding="utf-8")


def main() -> None:
    config = get_repo_config()

    with RULES_JSON.open(encoding="utf-8") as handle:
        rules_data = json.load(handle)

    with STACKS_JSON.open(encoding="utf-8") as handle:
        stacks_data = json.load(handle)

    custom_rules = []
    if CUSTOM_RULES_JSON.is_file():
        with CUSTOM_RULES_JSON.open(encoding="utf-8") as handle:
            custom_data = json.load(handle)
        custom_rules = custom_data.get("rules", [])

    aliases = {}
    if ALIASES_JSON.is_file():
        with ALIASES_JSON.open(encoding="utf-8") as handle:
            aliases = json.load(handle).get("aliases", {})

    tag_counter: Counter[str] = Counter()
    rules = []
    for entry in rules_data["libraries"]:
        tags = entry.get("tags", [])
        tag_counter.update(tags)
        rules.append({"name": entry["name"], "tags": tags})

    catalog = {
        "repo": config.repo,
        "branch": config.branch,
        "upstream": config.upstream,
        "githubUrl": config.github_url,
        "pagesUrl": config.pages_url,
        "installShUrl": config.install_sh_url,
        "quickInstallUrl": f"{config.raw_base}/src/quick_install.py",
        "quickInstallPagesUrl": f"{config.pages_url}/quick_install.py",
        "rulesMdcBase": config.rules_mdc_base,
        "customRulesBase": config.custom_rules_base,
        "rules": sorted(rules, key=lambda item: item["name"]),
        "customRules": sorted(custom_rules, key=lambda item: item["name"]),
        "stacks": stacks_data["stacks"],
        "aliases": aliases,
        "tags": [
            {"name": tag, "count": count}
            for tag, count in tag_counter.most_common()
        ],
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as handle:
        json.dump(catalog, handle, indent=2)
        handle.write("\n")

    sync_install_sh(config)

    if QUICK_INSTALL_SRC.is_file():
        QUICK_INSTALL_DOCS.write_text(QUICK_INSTALL_SRC.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"Repo: {config.repo} ({config.branch})")
    print(f"Pages: {config.pages_url}")
    print(f"Wrote {OUTPUT} ({len(rules)} rules, {len(custom_rules)} custom, {len(catalog['stacks'])} stacks, {len(aliases)} aliases)")
    if QUICK_INSTALL_SRC.is_file():
        print(f"Copied {QUICK_INSTALL_DOCS}")
    print(f"Synced {INSTALL_SH}")


if __name__ == "__main__":
    main()
