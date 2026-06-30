#!/usr/bin/env python3
"""Generate template MDC files for libraries missing from rules-mdc/."""

from __future__ import annotations

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RULES_JSON = REPO_ROOT / "rules.json"
OUTPUT_DIR = REPO_ROOT / "rules-mdc"
PROGRESS = REPO_ROOT / "src" / "mdc_generation_progress.json"

GLOBS_BY_TAG = {
    "python": "**/*.py",
    "javascript": "**/*.{js,jsx,ts,tsx}",
    "typescript": "**/*.{ts,tsx}",
    "sql": "**/*.{sql,py}",
    "frontend": "**/*.{tsx,jsx,vue,svelte,css}",
    "mobile": "**/*.{swift,kt,kts,dart}",
    "ios": "**/*.{swift,m,h}",
    "android": "**/*.{kt,kts,java}",
    "go": "**/*.go",
    "rust": "**/*.rs",
    "java": "**/*.{java,kt}",
    "devops": "**/*.{yaml,yml,Dockerfile,tf,hcl}",
    "data-engineering": "**/*.{py,sql,yml,yaml}",
    "ai": "**/*.{py,ts,tsx}",
    "gen-ai": "**/*.{py,ts,tsx}",
    "cloud": "**/*.{py,ts,yml,yaml,tf,hcl}",
    "aws": "**/*.{py,ts,yml,yaml,tf,hcl}",
    "gcp": "**/*.{py,ts,yml,yaml,tf,hcl}",
    "azure": "**/*.{py,ts,yml,yaml,tf,hcl}",
    "security": "**/*.{py,ts,go,rs,yml,yaml,env*}",
    "backend": "**/*.{py,ts,go,rs,java}",
}


def pick_globs(tags: list[str]) -> str:
    for tag in tags:
        if tag in GLOBS_BY_TAG:
            return GLOBS_BY_TAG[tag]
    return "**/*"


def title(name: str) -> str:
    return " ".join(part.capitalize() for part in name.replace("-", " ").split())


def build_content(name: str, tags: list[str], description: str) -> str:
    tag_text = ", ".join(tags)
    sections = [
        ("Code organization", [
            f"Follow idiomatic {title(name)} project structure and naming conventions.",
            "Keep configuration separate from business logic.",
            "Prefer small, focused modules over large monolithic files.",
        ]),
        ("Performance", [
            "Profile before optimizing; measure impact of changes.",
            "Use connection pooling and caching where appropriate.",
            "Avoid N+1 queries and unbounded in-memory operations.",
        ]),
        ("Security", [
            "Never hardcode secrets; use environment variables or secret managers.",
            "Validate and sanitize all external input.",
            "Apply least-privilege access for services and credentials.",
        ]),
        ("Testing", [
            "Write tests for critical paths and edge cases.",
            "Use integration tests for external service boundaries.",
            "Mock external dependencies in unit tests.",
        ]),
        ("Operations", [
            "Add structured logging with correlation IDs.",
            "Define health checks and graceful shutdown handlers.",
            "Document deployment requirements and environment variables.",
        ]),
    ]

    if "data-engineering" in tags or "sql" in tags:
        sections.insert(1, ("Data quality", [
            "Validate schema and data types at pipeline boundaries.",
            "Make pipelines idempotent where possible.",
            "Track data lineage and document transformation logic.",
        ]))
    if "ai" in tags or "gen-ai" in tags or "rag" in tags:
        sections.insert(1, ("AI-specific", [
            "Version prompts, models, and retrieval indexes together.",
            "Log token usage, latency, and model version per request.",
            "Treat LLM output as untrusted until validated.",
        ]))

    body = [f"# {title(name)} Best Practices", "", f"Tags: {tag_text}", ""]
    for heading, bullets in sections:
        body.append(f"## {heading}")
        body.append("")
        for bullet in bullets:
            body.append(f"- {bullet}")
        body.append("")
    return "\n".join(body).rstrip() + "\n"


def main() -> None:
    with RULES_JSON.open(encoding="utf-8") as handle:
        libraries = json.load(handle)["libraries"]

    progress = {}
    if PROGRESS.is_file():
        with PROGRESS.open(encoding="utf-8") as handle:
            progress = json.load(handle)

    created = []
    for entry in libraries:
        name = entry["name"]
        path = OUTPUT_DIR / f"{name}.mdc"
        if path.is_file():
            continue

        tags = entry.get("tags", [])
        description = f"Best practices and coding standards for {title(name)}."
        globs = pick_globs(tags)
        content = (
            f"---\n"
            f"description: {description}\n"
            f"globs: {globs}\n"
            f"---\n\n"
            f"{build_content(name, tags, description)}"
        )
        path.write_text(content, encoding="utf-8")
        progress[name] = "completed"
        created.append(name)

    with PROGRESS.open("w", encoding="utf-8") as handle:
        json.dump(progress, handle, indent=2)
        handle.write("\n")

    print(f"Created {len(created)} template MDC files")
    if created:
        print(", ".join(created[:20]), "..." if len(created) > 20 else "")


if __name__ == "__main__":
    main()
