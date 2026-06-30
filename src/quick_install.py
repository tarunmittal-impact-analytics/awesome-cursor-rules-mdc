#!/usr/bin/env python3
"""Install Cursor MDC rules from any project — no clone required.

Fetch this script and run from your project directory:

  curl -fsSL https://raw.githubusercontent.com/OWNER/REPO/main/src/quick_install.py \\
    | python3 - --here --alias "python backend"

  curl -fsSL .../src/quick_install.py | python3 - --here --stack backend-e2e-fastapi
  curl -fsSL .../src/quick_install.py | python3 - --here --tag python --custom base
  curl -fsSL .../src/quick_install.py | python3 - --here react fastapi
  curl -fsSL .../src/quick_install.py | python3 - --download react --output ./react.mdc
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

DEFAULT_REPO = os.environ.get("CURSOR_RULES_REPO", "tarunmittal-impact-analytics/awesome-cursor-rules-mdc")
DEFAULT_BRANCH = os.environ.get("CURSOR_RULES_BRANCH", "main")
USER_AGENT = "cursor-rules-quick-install"


def raw_base(repo: str, branch: str) -> str:
    return f"https://raw.githubusercontent.com/{repo}/{branch}"


def fetch_json(url: str) -> Any:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_bytes(url: str) -> Optional[bytes]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError:
        return None


class RuleRef:
    __slots__ = ("kind", "name")

    def __init__(self, kind: str, name: str) -> None:
        self.kind = kind
        self.name = name.lower()

    @property
    def label(self) -> str:
        return f"custom:{self.name}" if self.kind == "custom" else self.name


def parse_rule_ref(raw: str) -> RuleRef:
    value = raw.strip().lower()
    if value.startswith("custom:"):
        return RuleRef("custom", value.split(":", 1)[1])
    return RuleRef("library", value)


def load_remote_catalogs(repo: str, branch: str) -> Tuple[Dict[str, dict], Dict[str, dict], Dict[str, dict], Dict[str, dict]]:
    base = raw_base(repo, branch)
    rules_data = fetch_json(f"{base}/rules.json")
    stacks_data = fetch_json(f"{base}/stacks.json")
    aliases_data = fetch_json(f"{base}/install_aliases.json")
    custom_data = fetch_json(f"{base}/custom-rules.json")
    library = {entry["name"]: entry for entry in rules_data["libraries"]}
    custom = {entry["name"]: entry for entry in custom_data.get("rules", [])}
    stacks = stacks_data["stacks"]
    aliases = aliases_data.get("aliases", {})
    return library, custom, stacks, aliases


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


def resolve_alias(alias: str, aliases: Dict[str, dict], stacks: Dict[str, dict]) -> Tuple[List[RuleRef], Optional[str], Optional[List[str]], Optional[str]]:
    """Return (rules, stack_name, tags, custom_name) from alias lookup."""
    key = alias.strip().lower()
    if key not in aliases:
        normalized = key.replace("_", " ").replace("-", " ")
        if normalized in aliases:
            key = normalized
        elif key.replace(" ", "-") in stacks:
            return [], key.replace(" ", "-"), None, None
        elif key.replace(" ", "-") in {k.replace(" ", "-") for k in stacks}:
            for stack_name in stacks:
                if stack_name.replace("_", "-") == key.replace(" ", "-"):
                    return [], stack_name, None, None
        else:
            raise SystemExit(f"Unknown alias: {alias}\nRun with --list-aliases to see friendly names.")

    spec = aliases[key]
    if "stack" in spec:
        stack = spec["stack"]
        if stack not in stacks:
            raise SystemExit(f"Alias '{alias}' points to unknown stack: {stack}")
        rules = [parse_rule_ref(name) for name in stacks[stack]["rules"]]
        return rules, stack, None, None
    if "tag" in spec:
        return [], None, [spec["tag"]], None
    if "custom" in spec:
        return [RuleRef("custom", spec["custom"])], None, None, spec["custom"]
    raise SystemExit(f"Invalid alias spec for '{alias}'")


def rule_url(repo: str, branch: str, rule: RuleRef) -> str:
    subdir = "rules-custom" if rule.kind == "custom" else "rules-mdc"
    return f"{raw_base(repo, branch)}/{subdir}/{rule.name}.mdc"


def install_rule(
    rule: RuleRef,
    target_dir: Path,
    *,
    repo: str,
    branch: str,
    force: bool,
    dry_run: bool,
) -> Tuple[str, str]:
    destination = target_dir / f"{rule.name}.mdc"
    if destination.exists() and not force:
        return rule.label, "skipped"
    if dry_run:
        return rule.label, "would_install"
    content = fetch_bytes(rule_url(repo, branch, rule))
    if content is None:
        return rule.label, "missing"
    target_dir.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return rule.label, "installed"


def download_rule(rule: RuleRef, output: Path, *, repo: str, branch: str) -> int:
    content = fetch_bytes(rule_url(repo, branch, rule))
    if content is None:
        print(f"Missing: {rule.label}", file=sys.stderr)
        return 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(content)
    print(f"Downloaded: {output}")
    return 0


def dedupe(refs: Iterable[RuleRef]) -> List[RuleRef]:
    seen: Set[str] = set()
    unique: List[RuleRef] = []
    for ref in refs:
        key = f"{ref.kind}:{ref.name}"
        if key not in seen:
            seen.add(key)
            unique.append(ref)
    return unique


def validate_rules(refs: List[RuleRef], library: Dict[str, dict], custom: Dict[str, dict]) -> None:
    unknown = [
        ref.label
        for ref in refs
        if ref.name not in (custom if ref.kind == "custom" else library)
    ]
    if unknown:
        raise SystemExit(f"Unknown rules: {', '.join(unknown)}")


def cmd_list_aliases(aliases: Dict[str, dict]) -> None:
    print(f"Install aliases ({len(aliases)})\n")
    for name in sorted(aliases):
        spec = aliases[name]
        desc = spec.get("description", "")
        target = spec.get("stack") or spec.get("tag") or f"custom:{spec.get('custom')}"
        print(f"  {name:<28} -> {target}")
        if desc:
            print(f"    {desc}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install Cursor MDC rules into .cursor/rules from any project (no clone needed).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --here --alias "python backend"
  %(prog)s --here --stack backend-e2e-fastapi
  %(prog)s --here --tag python --custom base
  %(prog)s --here react fastapi --custom acid-properties
  %(prog)s --download react --output ./react.mdc
  %(prog)s --list-aliases
  %(prog)s --list-stacks

Pipe from any project:
  curl -fsSL https://raw.githubusercontent.com/OWNER/REPO/main/src/quick_install.py | python3 - --here --alias "mern"
        """,
    )
    parser.add_argument("rules", nargs="*", help="Library rule names (e.g. react fastapi)")
    parser.add_argument("--repo", default=DEFAULT_REPO, help=f"GitHub repo (default: {DEFAULT_REPO})")
    parser.add_argument("--branch", default=DEFAULT_BRANCH, help=f"Branch (default: {DEFAULT_BRANCH})")
    parser.add_argument("--stack", metavar="NAME", help="Preset stack name")
    parser.add_argument("--alias", metavar="TEXT", help='Friendly alias (e.g. "python backend", mern, gen ai)')
    parser.add_argument("--tag", action="append", dest="tags", metavar="TAG", help="Install all library rules with tag")
    parser.add_argument("--custom", nargs="*", dest="custom_rules", metavar="NAME", help="Custom/personal rule names")
    parser.add_argument("--custom-tag", action="append", dest="custom_tags", metavar="TAG")
    parser.add_argument("--here", action="store_true", help="Install into ./.cursor/rules (default)")
    parser.add_argument("--target", metavar="PATH", help="Install into a specific directory")
    parser.add_argument("--download", metavar="NAME", help="Download a single rule file (library or custom:name)")
    parser.add_argument("--output", "-o", metavar="PATH", help="Output path for --download")
    parser.add_argument("--list-aliases", action="store_true", help="List friendly install aliases")
    parser.add_argument("--list-stacks", action="store_true", help="List preset stacks")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    try:
        library, custom, stacks, aliases = load_remote_catalogs(args.repo, args.branch)
    except Exception as exc:
        print(f"Failed to fetch catalogs from GitHub: {exc}", file=sys.stderr)
        return 1

    if args.list_aliases:
        cmd_list_aliases(aliases)
        return 0

    if args.list_stacks:
        print(f"Available stacks ({len(stacks)})\n")
        for name, stack in sorted(stacks.items()):
            print(f"  {name}")
            print(f"    {stack['description']}\n")
        return 0

    if args.download:
        ref = parse_rule_ref(args.download)
        output = Path(args.output or f"{ref.name}.mdc").expanduser()
        catalog = custom if ref.kind == "custom" else library
        if ref.name not in catalog:
            print(f"Unknown rule: {ref.label}", file=sys.stderr)
            return 1
        return download_rule(ref, output, repo=args.repo, branch=args.branch)

    selected: List[RuleRef] = [parse_rule_ref(name) for name in args.rules]

    if args.alias:
        alias_rules, alias_stack, alias_tags, alias_custom = resolve_alias(args.alias, aliases, stacks)
        selected.extend(alias_rules)
        if alias_stack and not args.stack:
            args.stack = alias_stack
        if alias_tags:
            args.tags = (args.tags or []) + alias_tags
        if alias_custom:
            selected.append(RuleRef("custom", alias_custom))

    if args.custom_rules:
        selected.extend(parse_rule_ref(name) for name in args.custom_rules)

    if args.stack:
        if args.stack not in stacks:
            print(f"Unknown stack: {args.stack}", file=sys.stderr)
            print("Use --list-stacks to browse.", file=sys.stderr)
            return 1
        selected.extend(parse_rule_ref(name) for name in stacks[args.stack]["rules"])

    if args.tags:
        selected.extend(rules_for_tags(library, args.tags))

    if args.custom_tags:
        selected.extend(custom_rules_for_tags(custom, args.custom_tags))

    selected = dedupe(selected)
    if not selected:
        parser.print_help()
        print("\nNo rules selected. Use --stack, --alias, --tag, --custom, or rule names.", file=sys.stderr)
        return 1

    validate_rules(selected, library, custom)

    if args.here and args.target:
        print("Use either --here or --target, not both.", file=sys.stderr)
        return 1
    target_dir = Path(args.target).expanduser().resolve() if args.target else Path.cwd() / ".cursor" / "rules"

    print(f"Target: {target_dir}")
    print(f"Source: github ({args.repo}@{args.branch})")
    print(f"Rules:  {len(selected)}\n")

    results: Dict[str, List[str]] = {"installed": [], "skipped": [], "missing": [], "would_install": []}
    for rule in selected:
        name, status = install_rule(rule, target_dir, repo=args.repo, branch=args.branch, force=args.force, dry_run=args.dry_run)
        results[status].append(name)

    for status, items in results.items():
        if items:
            print(f"{status.replace('_', ' ').title()}: {', '.join(items)}")

    return 1 if results["missing"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
