#!/usr/bin/env python3
"""Install Cursor MDC rules into a project's .cursor/rules directory."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, NamedTuple, Optional, Set, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG = REPO_ROOT / "rules.json"
DEFAULT_CUSTOM_CATALOG = REPO_ROOT / "custom-rules.json"
DEFAULT_STACKS = REPO_ROOT / "stacks.json"
DEFAULT_RULES_DIR = REPO_ROOT / "rules-mdc"
DEFAULT_CUSTOM_RULES_DIR = REPO_ROOT / "rules-custom"


class RuleRef(NamedTuple):
    kind: str
    name: str

    @property
    def label(self) -> str:
        return f"custom:{self.name}" if self.kind == "custom" else self.name


def _get_repo_config():
    try:
        from repo_config import get_repo_config
    except ModuleNotFoundError:
        from src.repo_config import get_repo_config
    return get_repo_config()


def github_library_base() -> str:
    return _get_repo_config().rules_mdc_base


def github_custom_base() -> str:
    return _get_repo_config().custom_rules_base


def load_catalog(catalog_path: Path) -> Dict[str, dict]:
    with catalog_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return {entry["name"]: entry for entry in data["libraries"]}


def load_custom_catalog(catalog_path: Path) -> Dict[str, dict]:
    with catalog_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return {entry["name"]: entry for entry in data["rules"]}


def load_stacks(stacks_path: Path) -> Dict[str, dict]:
    with stacks_path.open(encoding="utf-8") as handle:
        data = json.load(handle)
    return data["stacks"]


def parse_rule_ref(raw: str, *, default_kind: str = "library") -> RuleRef:
    value = raw.strip().lower()
    if value.startswith("custom:"):
        return RuleRef("custom", value.split(":", 1)[1])
    return RuleRef(default_kind, value)


def resolve_target_dir(here: bool, target: Optional[str]) -> Path:
    if here and target:
        raise SystemExit("Use either --here or --target, not both.")
    if here:
        return Path.cwd() / ".cursor" / "rules"
    if target:
        return Path(target).expanduser().resolve()
    return Path.cwd() / ".cursor" / "rules"


def rules_for_tags(catalog: Dict[str, dict], tags: Iterable[str]) -> List[RuleRef]:
    wanted = {tag.strip().lower() for tag in tags if tag.strip()}
    matched: Set[RuleRef] = set()
    for name, entry in catalog.items():
        entry_tags = {tag.lower() for tag in entry.get("tags", [])}
        if wanted & entry_tags:
            matched.add(RuleRef("library", name))
    return sorted(matched, key=lambda ref: ref.label)


def custom_rules_for_tags(catalog: Dict[str, dict], tags: Iterable[str]) -> List[RuleRef]:
    wanted = {tag.strip().lower() for tag in tags if tag.strip()}
    matched: Set[RuleRef] = set()
    for name, entry in catalog.items():
        entry_tags = {tag.lower() for tag in entry.get("tags", [])}
        if wanted & entry_tags:
            matched.add(RuleRef("custom", name))
    return sorted(matched, key=lambda ref: ref.label)


def search_rules(catalog: Dict[str, dict], query: str) -> List[str]:
    needle = query.strip().lower()
    if not needle:
        return []
    matches: Set[str] = set()
    for name, entry in catalog.items():
        haystack = " ".join([name, *entry.get("tags", [])]).lower()
        if needle in haystack:
            matches.add(name)
        elif all(part in haystack for part in needle.split()):
            matches.add(name)
    return sorted(matches)


def fetch_remote_rule(rule: RuleRef) -> Optional[bytes]:
    base = github_custom_base() if rule.kind == "custom" else github_library_base()
    url = f"{base}/{rule.name}.mdc"
    request = urllib.request.Request(url, headers={"User-Agent": "cursor-rules-installer"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError:
        return None


def install_rule(
    rule: RuleRef,
    target_dir: Path,
    *,
    source: str,
    local_rules_dir: Path,
    local_custom_dir: Path,
    force: bool,
    dry_run: bool,
) -> Tuple[str, str]:
    destination = target_dir / f"{rule.name}.mdc"

    if destination.exists() and not force:
        return rule.label, "skipped"

    if dry_run:
        return rule.label, "would_install"

    target_dir.mkdir(parents=True, exist_ok=True)
    local_dir = local_custom_dir if rule.kind == "custom" else local_rules_dir

    if source == "local":
        source_file = local_dir / f"{rule.name}.mdc"
        if not source_file.is_file():
            return rule.label, "missing"
        shutil.copy2(source_file, destination)
        return rule.label, "installed"

    content = fetch_remote_rule(rule)
    if content is None:
        return rule.label, "missing"
    destination.write_bytes(content)
    return rule.label, "installed"


def install_rules(
    rule_refs: Iterable[RuleRef],
    target_dir: Path,
    *,
    library_catalog: Dict[str, dict],
    custom_catalog: Dict[str, dict],
    source: str,
    local_rules_dir: Path,
    local_custom_dir: Path,
    force: bool,
    dry_run: bool,
) -> int:
    unique: List[RuleRef] = []
    seen: Set[str] = set()
    for ref in rule_refs:
        key = f"{ref.kind}:{ref.name}"
        if key not in seen:
            seen.add(key)
            unique.append(ref)

    unknown = [
        ref.label
        for ref in unique
        if ref.name not in (custom_catalog if ref.kind == "custom" else library_catalog)
    ]
    if unknown:
        print(f"Unknown rules: {', '.join(unknown)}", file=sys.stderr)
        print("Run `list`, `list-custom`, or `search` to browse available rules.", file=sys.stderr)
        return 1

    if not unique:
        print("No rules selected.", file=sys.stderr)
        return 1

    print(f"Target: {target_dir}")
    print(f"Source: {source}")
    print()

    results: Dict[str, List[str]] = {
        "installed": [],
        "skipped": [],
        "missing": [],
        "would_install": [],
    }

    for rule in unique:
        rule_name, status = install_rule(
            rule,
            target_dir,
            source=source,
            local_rules_dir=local_rules_dir,
            local_custom_dir=local_custom_dir,
            force=force,
            dry_run=dry_run,
        )
        results[status].append(rule_name)

    for status, items in results.items():
        if items:
            label = status.replace("_", " ")
            print(f"{label.title()}: {', '.join(items)}")

    if results["missing"]:
        return 1
    return 0


def cmd_list(catalog: Dict[str, dict], tags: Optional[List[str]], *, kind: str = "library", title_prefix: str = "") -> None:
    if tags:
        if kind == "custom":
            names = [ref.name for ref in custom_rules_for_tags(catalog, tags)]
        else:
            names = [ref.name for ref in rules_for_tags(catalog, tags)]
        title = f"{title_prefix}Rules matching tags: {', '.join(tags)}"
    else:
        names = sorted(catalog)
        title = f"{title_prefix}All available rules"

    print(f"{title} ({len(names)})\n")
    for name in names:
        entry = catalog[name]
        tag_text = ", ".join(entry.get("tags", []))
        prefix = "custom:" if kind == "custom" else ""
        print(f"  {prefix}{name:<28} [{tag_text}]")


def cmd_list_custom(catalog: Dict[str, dict], tags: Optional[List[str]]) -> None:
    cmd_list(catalog, tags, kind="custom", title_prefix="Custom ")


def cmd_tags(catalog: Dict[str, dict]) -> None:
    counter: Counter[str] = Counter()
    for entry in catalog.values():
        counter.update(entry.get("tags", []))

    print(f"Available tags ({len(counter)})\n")
    for tag, count in counter.most_common():
        print(f"  {tag:<24} ({count})")


def cmd_search(catalog: Dict[str, dict], query: str, *, custom_catalog: Optional[Dict[str, dict]] = None) -> None:
    matches = search_rules(catalog, query)
    if custom_catalog:
        matches.extend(search_rules(custom_catalog, query))

    if not matches:
        print(f"No rules matched '{query}'.")
        return

    unique_matches = sorted(set(matches))
    print(f"Matches for '{query}' ({len(unique_matches)})\n")
    for name in unique_matches:
        if custom_catalog and name in custom_catalog:
            entry = custom_catalog[name]
            display = f"custom:{name}"
        else:
            entry = catalog[name]
            display = name
        tag_text = ", ".join(entry.get("tags", []))
        print(f"  {display:<28} [{tag_text}]")


def cmd_stacks(stacks: Dict[str, dict]) -> None:
    print(f"Available stacks ({len(stacks)})\n")
    for stack_name, stack in sorted(stacks.items()):
        rules = ", ".join(stack["rules"])
        print(f"  {stack_name}")
        print(f"    {stack['description']}")
        print(f"    rules: {rules}\n")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Browse and install Cursor MDC rules into .cursor/rules",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s list
  %(prog)s list-custom
  %(prog)s search fastapi
  %(prog)s stacks
  %(prog)s install react fastapi --here
  %(prog)s install --custom base frontend --here
  %(prog)s install --custom-all --here
  %(prog)s install --stack personal-python-backend --here
  %(prog)s install --stack python-backend --here --source github
        """,
    )

    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--custom-catalog", type=Path, default=DEFAULT_CUSTOM_CATALOG)
    parser.add_argument("--stacks-file", type=Path, default=DEFAULT_STACKS)
    parser.add_argument("--rules-dir", type=Path, default=DEFAULT_RULES_DIR)
    parser.add_argument("--custom-rules-dir", type=Path, default=DEFAULT_CUSTOM_RULES_DIR)

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="List library rules")
    list_parser.add_argument("--tag", action="append", dest="tags", metavar="TAG")

    list_custom_parser = subparsers.add_parser("list-custom", help="List personal/custom rules")
    list_custom_parser.add_argument("--tag", action="append", dest="tags", metavar="TAG")

    subparsers.add_parser("tags", help="List all library tags with counts")
    search_parser = subparsers.add_parser("search", help="Search library and custom rules")
    search_parser.add_argument("query", help="Search query")
    subparsers.add_parser("stacks", help="List preset rule stacks")

    install_parser = subparsers.add_parser("install", help="Install rules into .cursor/rules")
    install_parser.add_argument("rules", nargs="*", help="Library rule names (e.g. react fastapi)")
    install_parser.add_argument("--custom", nargs="*", dest="custom_rules", metavar="NAME", help="Custom rule names (e.g. base frontend)")
    install_parser.add_argument("--custom-all", action="store_true", help="Install all custom rules")
    install_parser.add_argument("--tag", action="append", dest="tags", metavar="TAG")
    install_parser.add_argument("--custom-tag", action="append", dest="custom_tags", metavar="TAG")
    install_parser.add_argument("--stack", metavar="NAME")
    install_parser.add_argument("--here", action="store_true")
    install_parser.add_argument("--target")
    install_parser.add_argument("--source", choices=["local", "github"], default="local")
    install_parser.add_argument("--force", action="store_true")
    install_parser.add_argument("--dry-run", action="store_true")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not args.catalog.is_file():
        print(f"Catalog not found: {args.catalog}", file=sys.stderr)
        return 1

    catalog = load_catalog(args.catalog)
    custom_catalog = load_custom_catalog(args.custom_catalog) if args.custom_catalog.is_file() else {}

    if args.command == "list":
        cmd_list(catalog, args.tags)
        return 0

    if args.command == "list-custom":
        if not custom_catalog:
            print(f"Custom catalog not found: {args.custom_catalog}", file=sys.stderr)
            return 1
        cmd_list_custom(custom_catalog, args.tags)
        return 0

    if args.command == "tags":
        cmd_tags(catalog)
        return 0

    if args.command == "search":
        cmd_search(catalog, args.query, custom_catalog=custom_catalog or None)
        return 0

    if args.command == "stacks":
        if not args.stacks_file.is_file():
            print(f"Stacks file not found: {args.stacks_file}", file=sys.stderr)
            return 1
        cmd_stacks(load_stacks(args.stacks_file))
        return 0

    if args.command == "install":
        selected: List[RuleRef] = [parse_rule_ref(name) for name in args.rules]

        if args.custom_rules:
            selected.extend(parse_rule_ref(name, default_kind="custom") for name in args.custom_rules)

        if args.custom_all:
            selected.extend(RuleRef("custom", name) for name in sorted(custom_catalog))

        if args.stack:
            if not args.stacks_file.is_file():
                print(f"Stacks file not found: {args.stacks_file}", file=sys.stderr)
                return 1
            stacks = load_stacks(args.stacks_file)
            if args.stack not in stacks:
                print(f"Unknown stack: {args.stack}", file=sys.stderr)
                print(f"Available: {', '.join(sorted(stacks))}", file=sys.stderr)
                return 1
            selected.extend(parse_rule_ref(name) for name in stacks[args.stack]["rules"])

        if args.tags:
            selected.extend(rules_for_tags(catalog, args.tags))

        if args.custom_tags:
            selected.extend(custom_rules_for_tags(custom_catalog, args.custom_tags))

        if args.source == "local":
            if not args.rules_dir.is_dir():
                print(f"Local rules directory not found: {args.rules_dir}", file=sys.stderr)
                print("Use --source github to fetch rules without a local clone.", file=sys.stderr)
                return 1
            if any(ref.kind == "custom" for ref in selected) and not args.custom_rules_dir.is_dir():
                print(f"Custom rules directory not found: {args.custom_rules_dir}", file=sys.stderr)
                return 1

        target_dir = resolve_target_dir(args.here, args.target)
        return install_rules(
            selected,
            target_dir,
            library_catalog=catalog,
            custom_catalog=custom_catalog,
            source=args.source,
            local_rules_dir=args.rules_dir,
            local_custom_dir=args.custom_rules_dir,
            force=args.force,
            dry_run=args.dry_run,
        )

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
