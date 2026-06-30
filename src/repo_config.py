"""Resolve GitHub repo coordinates for this fork."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import NamedTuple

REPO_ROOT = Path(__file__).resolve().parent.parent
REPO_JSON = REPO_ROOT / "repo.json"


class RepoConfig(NamedTuple):
    repo: str
    branch: str
    upstream: str

    @property
    def owner(self) -> str:
        return self.repo.split("/", 1)[0]

    @property
    def name(self) -> str:
        return self.repo.split("/", 1)[1]

    @property
    def raw_base(self) -> str:
        return f"https://raw.githubusercontent.com/{self.repo}/{self.branch}"

    @property
    def rules_mdc_base(self) -> str:
        return f"{self.raw_base}/rules-mdc"

    @property
    def custom_rules_base(self) -> str:
        return f"{self.raw_base}/rules-custom"

    @property
    def install_sh_url(self) -> str:
        return f"{self.raw_base}/install.sh"

    @property
    def github_url(self) -> str:
        return f"https://github.com/{self.repo}"

    @property
    def pages_url(self) -> str:
        return f"https://{self.owner}.github.io/{self.name}/"


def _load_repo_json() -> dict:
    if not REPO_JSON.is_file():
        return {}
    with REPO_JSON.open(encoding="utf-8") as handle:
        return json.load(handle)


def _detect_from_git() -> tuple[str | None, str | None]:
    try:
        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=True,
            cwd=REPO_ROOT,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None, None

    match = re.search(r"github\.com[:/](?P<owner>[^/]+)/(?P<repo>[^/.]+)", remote)
    if not match:
        return None, None

    slug = f"{match.group('owner')}/{match.group('repo')}"

    try:
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
            cwd=REPO_ROOT,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        branch = None

    return slug, branch or None


def get_repo_config() -> RepoConfig:
    file_config = _load_repo_json()
    detected_repo, detected_branch = _detect_from_git()

    repo = (
        os.environ.get("CURSOR_RULES_REPO")
        or detected_repo
        or file_config.get("repo")
        or "tarunmittal-impact-analytics/awesome-cursor-rules-mdc"
    )
    branch = (
        os.environ.get("CURSOR_RULES_BRANCH")
        or detected_branch
        or file_config.get("branch")
        or "main"
    )
    upstream = file_config.get("upstream", "sanjeed5/awesome-cursor-rules-mdc")

    return RepoConfig(repo=repo, branch=branch, upstream=upstream)
