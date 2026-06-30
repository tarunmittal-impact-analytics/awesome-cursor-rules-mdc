# Complete Usage Guide

This document is the full reference for **awesome-cursor-rules-mdc** — what it is, how it works, and every way to use it.

> **Fork:** [tarunmittal-impact-analytics/awesome-cursor-rules-mdc](https://github.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc)  
> **Upstream:** [sanjeed5/awesome-cursor-rules-mdc](https://github.com/sanjeed5/awesome-cursor-rules-mdc)  
> **Web catalog:** https://tarunmittal-impact-analytics.github.io/awesome-cursor-rules-mdc/

---

## Table of contents

1. [What is this repo?](#what-is-this-repo)
2. [What are Cursor rules?](#what-are-cursor-rules)
3. [What's inside this repo](#whats-inside-this-repo)
4. [Quick start — set up a new project](#quick-start--set-up-a-new-project)
5. [All ways to install rules](#all-ways-to-install-rules)
6. [Install methods compared](#install-methods-compared)
7. [CLI reference (`install_rules.py`)](#cli-reference-install_rulespy)
8. [Curl installer reference (`install.sh`)](#curl-installer-reference-installsh)
9. [Web catalog](#web-catalog)
10. [Preset stacks](#preset-stacks)
11. [Personal / custom rules](#personal--custom-rules)
12. [Example workflows by project type](#example-workflows-by-project-type)
13. [Generating library rules (maintainers)](#generating-library-rules-maintainers)
14. [Adding your own custom rules](#adding-your-own-custom-rules)
15. [Fork configuration](#fork-configuration)
16. [GitHub Pages setup](#github-pages-setup)
17. [After installing — using rules in Cursor](#after-installing--using-rules-in-cursor)
18. [Troubleshooting](#troubleshooting)

---

## What is this repo?

This repo is a **Cursor rules library and toolkit**. It provides:

1. **296 library rules** (`rules-mdc/`) — best-practice MDC files for frameworks, databases, data engineering, cloud, AI, and more.
2. **24 personal/custom rules** (`rules-custom/`) — hand-written workflow, architecture, security, RAG, and distributed systems rules.
3. **Install tooling** — CLI, curl script, and web catalog to copy rules into any project's `.cursor/rules/` folder.
4. **Rule generator** — scripts to create new library rules (requires API keys).

You do **not** need to clone this repo to use the rules. You can install directly from GitHub with curl or the web catalog.

---

## What are Cursor rules?

Cursor rules are persistent instructions that tell the AI how to behave in your project. They live in:

```
your-project/
  .cursor/
    rules/
      base.mdc
      react.mdc
      fastapi.mdc
```

Each `.mdc` file has YAML frontmatter + markdown content:

```markdown
---
description: React best practices
globs: **/*.{jsx,tsx}
alwaysApply: false
---

# React rules
- Prefer functional components
- ...
```

| Frontmatter field | Purpose |
|-------------------|---------|
| `description` | What the rule covers (used by Cursor to decide relevance) |
| `globs` | File patterns — rule applies when editing matching files |
| `alwaysApply: true` | Rule is always included in AI context |

**Alternative:** Cursor also supports `AGENTS.md` (plain markdown, no metadata). This repo uses `.mdc` files in `.cursor/rules/` because they support globs, multiple focused rules, and conditional application.

---

## What's inside this repo

```
.
├── rules-mdc/              # 296 library rules (react.mdc, clickhouse.mdc, …)
├── rules-custom/         # 24 personal/custom rules (RAG, security, architecture, …)
├── rules.json            # Catalog of all library rules + tags
├── custom-rules.json     # Catalog of personal rules
├── stacks.json           # Preset bundles (python-backend, personal, …)
├── repo.json             # Fork URL config (owner/repo, branch)
├── install.sh            # Curl installer (no Python needed)
├── docs/                 # Web catalog (GitHub Pages)
│   ├── index.html
│   └── catalog.json
└── src/
    ├── install_rules.py      # CLI installer
    ├── generate_catalog.py   # Build web catalog + sync URLs
    ├── generate_mdc_files.py # Generate library rules (needs API keys)
    └── repo_config.py        # Resolve fork URLs
```

### Two rule types

| Type | Directory | Count | Source | Install prefix |
|------|-----------|-------|--------|----------------|
| **Library** | `rules-mdc/` | 296 | Generated / template + LLM | `react`, `fastapi`, `clickhouse` |
| **Personal** | `rules-custom/` | 24 | Hand-written | `custom:base` or `--custom base` |

---

## Quick start — set up a new project

### Option A: Personal rules only (fastest)

```bash
cd ~/my-new-project

curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh \
  | bash -s -- --custom-all --here
```

Installs: `base`, `simple`, `complex`, `frontend`, `backend` into `.cursor/rules/`.

### Option B: Personal + stack (recommended)

```bash
cd ~/my-new-project

# FastAPI backend
curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh \
  | bash -s -- --stack personal-python-backend --here

# React TypeScript frontend
curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh \
  | bash -s -- --stack personal-react-ts --here
```

### Option C: Library stack only

```bash
curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh \
  | bash -s -- --stack python-backend --here
```

### Commit rules to git

```bash
git add .cursor/rules
git commit -m "Add Cursor rules for project"
```

---

## All ways to install rules

| Method | Requires clone? | Requires Python? | Best for |
|--------|-----------------|------------------|----------|
| **Curl** (`install.sh`) | No | No | Quick one-liner from any terminal |
| **CLI** (`install_rules.py`) | Optional | Yes (uv) | Browse, search, dry-run, local dev |
| **Web catalog** | No | No | Visual browse + copy commands |
| **Manual copy** | Yes | No | Single rule, full control |

### 1. Curl installer

Works from any project directory. Fetches rules from GitHub.

```bash
# Library rules by name
curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh \
  | bash -s -- react fastapi pydantic --here

# Preset stack
curl -fsSL .../install.sh | bash -s -- --stack python-backend --here

# By tag (installs ALL matching library rules — can be many)
curl -fsSL .../install.sh | bash -s -- --tag python --tag backend --here

# Personal rules
curl -fsSL .../install.sh | bash -s -- --custom-all --here
curl -fsSL .../install.sh | bash -s -- --custom base frontend --here
curl -fsSL .../install.sh | bash -s -- --stack personal --here

# Preview without installing
curl -fsSL .../install.sh | bash -s -- --stack personal --here --dry-run
```

### 2. CLI installer

Requires [uv](https://github.com/astral-sh/uv). Can use local files or fetch from GitHub.

```bash
# Browse
uv run src/install_rules.py list
uv run src/install_rules.py list --tag python
uv run src/install_rules.py list-custom
uv run src/install_rules.py tags
uv run src/install_rules.py search fastapi
uv run src/install_rules.py stacks

# Install from inside your project
cd ~/my-new-project
uv run /path/to/awesome-cursor-rules-mdc/src/install_rules.py install react fastapi --here

# Install from GitHub (no local clone of rules needed)
uv run src/install_rules.py install --stack personal-python-backend --here --source github

# Mix personal + library rules
uv run src/install_rules.py install --custom base frontend react typescript --here

# Install to a specific path
uv run src/install_rules.py install --stack react-ts --target ~/my-app/.cursor/rules
```

Installed entry point (after `uv sync` in this repo):

```bash
uv run cursor-rules list
uv run cursor-rules install --stack personal --here
```

### 3. Web catalog

Open: **https://tarunmittal-impact-analytics.github.io/awesome-cursor-rules-mdc/**

- **Rules** tab — browse 296 library rules, filter by tag, multi-select, copy curl/uv commands
- **Personal** tab — browse 5 custom rules
- **Stacks** tab — browse preset bundles, copy install command

### 4. Manual copy

```bash
mkdir -p ~/my-new-project/.cursor/rules

# Single library rule from GitHub
curl -fsSL \
  https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/rules-mdc/react.mdc \
  -o ~/my-new-project/.cursor/rules/react.mdc

# Single personal rule
curl -fsSL \
  https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/rules-custom/base.mdc \
  -o ~/my-new-project/.cursor/rules/base.mdc
```

---

## Install methods compared

### By library name

```bash
install react fastapi pydantic
```

- **Control:** High — you pick exact rules
- **Count:** Few files
- **Use when:** You know exactly which libraries you use

### By tag

```bash
install --tag python --tag backend
```

- **Control:** Low — installs every rule matching any tag
- **Count:** Can be 50–80+ files
- **Use when:** You want broad coverage (usually prefer stacks instead)

### By preset stack

```bash
install --stack python-backend
```

- **Control:** Medium — curated ~5 rules
- **Count:** ~5 files
- **Use when:** Starting a new project with a known stack

### By personal rules

```bash
install --custom-all
install --custom base frontend
install --stack personal
```

- **Control:** High for workflow rules
- **Use when:** You want your personal AI behavior conventions in every project

---

## CLI reference (`install_rules.py`)

### Commands

| Command | Description |
|---------|-------------|
| `list` | List all library rules |
| `list --tag TAG` | Filter library rules by tag |
| `list-custom` | List personal rules |
| `list-custom --tag TAG` | Filter personal rules by tag |
| `tags` | Show all library tags with counts |
| `search QUERY` | Search library + personal rules |
| `stacks` | List all preset stacks |
| `install …` | Install rules into `.cursor/rules` |

### Install flags

| Flag | Description |
|------|-------------|
| `--here` | Install into `./.cursor/rules` (current directory) |
| `--target PATH` | Install into a specific directory |
| `--source local` | Copy from local `rules-mdc/` and `rules-custom/` (default) |
| `--source github` | Fetch from GitHub raw URLs |
| `--stack NAME` | Install a preset stack from `stacks.json` |
| `--tag TAG` | Install all library rules matching tag (repeatable, OR logic) |
| `--custom NAME …` | Install personal rules by name |
| `--custom-all` | Install all personal rules |
| `--custom-tag TAG` | Install personal rules matching tag |
| `--force` | Overwrite existing rule files |
| `--dry-run` | Preview without copying |

### Stack rule syntax

Stacks can mix library and personal rules:

```json
"personal-python-backend": {
  "rules": ["custom:base", "custom:backend", "fastapi", "sqlalchemy", "pytest"]
}
```

- `custom:base` → from `rules-custom/base.mdc`
- `fastapi` → from `rules-mdc/fastapi.mdc`

---

## Curl installer reference (`install.sh`)

### Options

| Flag | Description |
|------|-------------|
| `--here` | Install into `./.cursor/rules` (default) |
| `--target PATH` | Install into a specific directory |
| `--stack NAME` | Install preset stack |
| `--tag TAG` | Install library rules matching tag (repeatable) |
| `--custom NAME …` | Install personal rules (one or more names) |
| `--custom-all` | Install all personal rules |
| `--force` | Overwrite existing files |
| `--dry-run` | Preview without installing |

### Environment variables

```bash
CURSOR_RULES_REPO=owner/repo CURSOR_RULES_BRANCH=main \
  curl -fsSL .../install.sh | bash -s -- react --here
```

Defaults to values in `repo.json` / `install.sh`.

---

## Web catalog

**URL:** https://tarunmittal-impact-analytics.github.io/awesome-cursor-rules-mdc/

### Tabs

| Tab | Content |
|-----|---------|
| **Rules** | 296 library rules with tag filters and multi-select |
| **Personal** | 24 custom rules (RAG, security, architecture, patterns) |
| **Stacks** | 54 preset bundles with one-click copy |

### Regenerate catalog (after editing rules)

```bash
uv run src/generate_catalog.py
```

This updates `docs/catalog.json`, syncs URLs in `install.sh`, and refreshes GitHub Pages on next push.

---

## Preset stacks

### Library stacks

| Stack | Description | Rules included |
|-------|-------------|----------------|
| `python-backend` | FastAPI API | fastapi, sqlalchemy, pydantic, pytest, docker |
| `python-django` | Django web app | django, django-orm, django-rest-framework, pytest, docker |
| `python-flask` | Flask REST API | flask, sqlalchemy, pydantic, pytest, docker |
| `react-ts` | React + TypeScript SPA | react, typescript, vite, vitest, eslint |
| `next-js-fullstack` | Next.js full-stack | next-js, react, typescript, tailwind, prisma |
| `vue-frontend` | Vue 3 frontend | vue, typescript, vite, vitest, eslint |
| `angular-frontend` | Angular app | angular, typescript, eslint, cypress, jest |
| `data-ml` | Data science / ML | pandas, numpy, scikit-learn, pytorch, matplotlib |
| `ai-llm` | LLM applications | langchain, openai, pydantic, fastapi, pytest |
| `devops` | Infra / CI/CD | docker, kubernetes, terraform, ansible, github-actions |
| `aws-cloud` | AWS serverless | aws, aws-lambda, aws-rds, amazon-s3, terraform |
| `rust-web` | Rust web services | actix-web, rust, docker, postgresql, redis |
| `go-backend` | Go backend API | go, fiber, postgresql, redis, docker |
| `mobile-flutter` | Flutter mobile | flutter, firebase, expo, typescript |
| `e2e-testing` | Browser testing | playwright, cypress, vitest, eslint, typescript |

### Data engineering stacks (individual tools)

| Stack | Description |
|-------|-------------|
| `data-stack-clickhouse` | ClickHouse analytics |
| `data-stack-postgres` | PostgreSQL |
| `data-stack-mysql` | MySQL |
| `data-stack-bigquery` | Google BigQuery |
| `data-stack-snowflake` | Snowflake |
| `data-stack-duckdb` | DuckDB |
| `data-stack-spark` | Apache Spark |
| `data-stack-flink` | Apache Flink |
| `data-stack-kafka` | Apache Kafka |
| `data-stack-airflow` | Apache Airflow |
| `data-stack-dbt` | dbt |
| `data-stack-prefect` | Prefect |
| `data-stack-dagster` | Dagster |
| `data-stack-beam` | Apache Beam |
| `data-stack-cassandra` | Cassandra |
| `data-stack-trino` | Trino |

### Gen AI stacks

| Stack | Description |
|-------|-------------|
| `gen-ai-full` | Full gen AI stack with LangChain, LangGraph, RAG |
| `gen-ai-rag` | RAG pipeline development |
| `gen-ai-graph-rag` | Graph RAG with Neo4j |
| `gen-ai-multi-agent` | Multi-agent systems |

### Security & distributed systems

| Stack | Description |
|-------|-------------|
| `security-full` | Auth, authorization, rate limiting |
| `secrets-management` | AWS/GCP/Azure secret managers |
| `distributed-systems` | CAP, ACID, locks, caching, concurrency |
| `messaging-rabbitmq` | RabbitMQ |
| `messaging-aws-sqs` | AWS SQS |
| `messaging-gcp-pubsub` | Google Pub/Sub |

### Cloud data engineering

| Stack | Description |
|-------|-------------|
| `aws-data-engineering` | AWS Glue, EMR, Kinesis, SQS |
| `gcp-data-engineering` | BigQuery, Dataflow, Pub/Sub |
| `azure-data-engineering` | Data Factory, Service Bus |

Run `uv run src/install_rules.py stacks` to list all 54 stacks.

### Personal stacks

| Stack | Description | Rules included |
|-------|-------------|----------------|
| `personal` | All personal workflow rules | custom:base, custom:simple, custom:complex, custom:frontend, custom:backend |
| `personal-python-backend` | Personal + FastAPI | custom:base, custom:backend, custom:complex, fastapi, sqlalchemy, pydantic, pytest |
| `personal-react-ts` | Personal + React | custom:base, custom:frontend, custom:simple, react, typescript, vite, vitest |

### Install a stack

```bash
# Curl
curl -fsSL .../install.sh | bash -s -- --stack personal-python-backend --here

# CLI
uv run src/install_rules.py install --stack personal-python-backend --here --source github
```

---

## Personal / custom rules

Located in `rules-custom/`. These define **how the AI behaves**, not library-specific syntax.

| Rule | `alwaysApply` | Globs | Purpose |
|------|---------------|-------|---------|
| `base` | **Yes** | — | Core behavior: concise, incremental edits, analyze-first for complex tasks |
| `simple` | No | `**/*.md`, tests, docs | Minimal responses for docs and tests |
| `complex` | No | — | Step-by-step thinking for architecture and large refactors |
| `frontend` | No | components, pages, `*.tsx` | UI conventions (server components, 150-line limit) |
| `backend` | No | api, server, models, db | API/DB conventions (error handling, parameterized queries) |
| `software-architecture` | No | — | System design principles |
| `design-patterns` | No | code files | Classic design patterns |
| `ai-design-patterns` | No | py/ts | LLM application patterns |
| `multi-agent-systems` | No | py/ts | Multi-agent orchestration |
| `graph-rag` | No | py/ts | Graph RAG with knowledge graphs |
| `rag-development` | No | py/ts | Vector RAG pipelines |
| `vectorless-rag` | No | py/ts | Retrieval without embeddings |
| `token-optimization` | No | py/ts | LLM cost/token optimization |
| `authentication` | No | backend files | Auth and session management |
| `authorization` | No | backend files | Access control |
| `caching` | No | backend files | Cache strategies |
| `rate-limiting` | No | backend files | API rate limiting |
| `distributed-rate-limiting` | No | backend files | Distributed rate limits |
| `distributed-locks` | No | backend files | Distributed locks |
| `acid-properties` | No | py/sql | Transactional DB design |
| `cap-theorem` | No | — | Consistency vs availability |
| `env-secrets-management` | No | env/config files | .env and secrets management |
| `gen-ai-development` | No | py/ts | Gen AI app development |
| `concurrency-parallelism` | No | backend files | Concurrency patterns |

### Install personal rules

```bash
# All 24 custom rules
curl -fsSL .../install.sh | bash -s -- --custom-all --here

# Specific rules
curl -fsSL .../install.sh | bash -s -- --custom base frontend backend --here

# Via stack
curl -fsSL .../install.sh | bash -s -- --stack personal --here
```

### Recommended combo for new projects

Always install `base` (it's `alwaysApply: true`). Then add stack-specific rules:

```bash
# Full-stack Next.js project
curl -fsSL .../install.sh | bash -s -- --custom base frontend backend --here
curl -fsSL .../install.sh | bash -s -- --stack next-js-fullstack --here

# Or use the combined stack
curl -fsSL .../install.sh | bash -s -- --stack personal-python-backend --here
```

---

## Example workflows by project type

### New FastAPI backend

```bash
cd ~/my-api
curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh \
  | bash -s -- --stack personal-python-backend --here
git add .cursor/rules && git commit -m "Add Cursor rules"
```

### New React + Vite frontend

```bash
cd ~/my-frontend
curl -fsSL .../install.sh | bash -s -- --stack personal-react-ts --here
```

### New Next.js app

```bash
cd ~/my-next-app
curl -fsSL .../install.sh | bash -s -- --stack next-js-fullstack --here
curl -fsSL .../install.sh | bash -s -- --custom base --here
```

### LLM / AI project

```bash
cd ~/my-llm-app
curl -fsSL .../install.sh | bash -s -- --stack ai-llm --here
curl -fsSL .../install.sh | bash -s -- --custom base complex --here
```

### Existing project — add one rule

```bash
cd ~/existing-project
curl -fsSL .../install.sh | bash -s -- react --here
```

### Existing project — add personal base rule only

```bash
curl -fsSL .../install.sh | bash -s -- --custom base --here
```

---

## Generating library rules (maintainers)

This requires API keys and is only needed if you want to **create new library rules**, not to install existing ones.

### Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv)
- API keys in `.env` (see `.env.example`):
  - `EXA_API_KEY` — semantic web search
  - `GEMINI_API_KEY` (or OpenAI / Anthropic)

### Setup

```bash
git clone https://github.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc.git
cd awesome-cursor-rules-mdc
uv sync
cp .env.example .env
# Edit .env with your API keys
```

### Generate rules

```bash
# Process failed libraries (default)
uv run src/generate_mdc_files.py

# Regenerate all
uv run src/generate_mdc_files.py --regenerate-all

# Single library
uv run src/generate_mdc_files.py --library react

# By tag
uv run src/generate_mdc_files.py --tag python
```

### Add a new library to the catalog

1. Add entry to `rules.json`:
   ```json
   {
     "name": "your-library",
     "tags": ["python", "backend"]
   }
   ```
2. Run generator: `uv run src/generate_mdc_files.py`
3. Regenerate web catalog: `uv run src/generate_catalog.py`
4. Commit `rules-mdc/your-library.mdc` and updated JSON files

---

## Adding your own custom rules

### 1. Add the `.mdc` file

Create `rules-custom/my-rule.mdc`:

```markdown
---
description: My project conventions
globs: **/*.py
alwaysApply: false
---

- Use type hints everywhere
- Keep functions under 30 lines
```

### 2. Register in catalog

Add to `custom-rules.json`:

```json
{
  "name": "my-rule",
  "description": "My project conventions",
  "tags": ["personal", "custom", "python"]
}
```

### 3. (Optional) Add to a stack

Edit `stacks.json`:

```json
"my-stack": {
  "description": "My custom stack",
  "rules": ["custom:base", "custom:my-rule", "fastapi"]
}
```

### 4. Sync catalog

```bash
uv run src/generate_catalog.py
git add rules-custom/ custom-rules.json stacks.json docs/
git commit -m "Add my-rule custom rule"
git push
```

### 5. Install in projects

```bash
curl -fsSL .../install.sh | bash -s -- --custom my-rule --here
```

---

## Fork configuration

All URLs point to your fork via `repo.json`:

```json
{
  "repo": "tarunmittal-impact-analytics/awesome-cursor-rules-mdc",
  "branch": "main",
  "upstream": "sanjeed5/awesome-cursor-rules-mdc"
}
```

After changing `repo.json`, sync:

```bash
uv run src/generate_catalog.py
```

This updates:
- `docs/catalog.json` (web catalog URLs)
- `install.sh` (curl default repo)
- GitHub Pages install links

Python tools also auto-detect `git remote origin` when run locally.

### Override with environment variables

```bash
export CURSOR_RULES_REPO=your-user/awesome-cursor-rules-mdc
export CURSOR_RULES_BRANCH=main
```

---

## GitHub Pages setup

The web catalog deploys from the `docs/` folder.

### One-time setup

1. Push this repo to GitHub
2. Go to **Repository Settings → Pages**
3. Set **Source** to **GitHub Actions**
4. Push to `main` — the workflow in `.github/workflows/pages.yml` deploys automatically

### Manual catalog rebuild

```bash
uv run src/generate_catalog.py
git add docs/catalog.json
git commit -m "Update catalog"
git push
```

---

## After installing — using rules in Cursor

1. **Open your project** in Cursor
2. Rules appear in **Cursor Settings → Rules**
3. Rules with `globs` auto-apply when you edit matching files
4. Rules with `alwaysApply: true` (like `base.mdc`) are always active
5. You can `@mention` rules in chat to apply them manually

### Verify rules are loaded

- Open a file matching a rule's globs (e.g. a `.tsx` file for `react.mdc`)
- Start an Agent chat — the AI should follow the rule conventions
- Check Settings → Rules to see which rules are active

### Add project-specific rules

Create your own alongside installed ones:

```bash
cat > .cursor/rules/project.mdc << 'EOF'
---
description: This project's conventions
alwaysApply: true
---
- Use uv for Python dependencies
- Never commit .env files
- Run tests before opening a PR
EOF
```

---

## Troubleshooting

### Curl install fails with 404

Rules aren't on GitHub yet. Push your fork to `main` first:

```bash
git push origin main
```

Or use local install if you have the repo cloned:

```bash
uv run src/install_rules.py install --stack personal --here --source local
```

### Rule already exists (skipped)

Use `--force` to overwrite:

```bash
curl -fsSL .../install.sh | bash -s -- react --here --force
```

### `--stack` or `--tag` requires python3

The curl script uses Python for JSON parsing on stack/tag/custom-all operations. Install Python 3, or install rules by name instead.

### Web catalog shows old data

Regenerate and push:

```bash
uv run src/generate_catalog.py
git add docs/catalog.json && git commit -m "Update catalog" && git push
```

### Rules not applying in Cursor

- Confirm files are in `.cursor/rules/` (not `.cursorrules` or root)
- Check frontmatter syntax (valid YAML between `---` markers)
- Restart Cursor or reload the window
- Verify `globs` patterns match your file paths

### Wrong GitHub URLs after forking

Update `repo.json` and run `uv run src/generate_catalog.py`.

---

## Quick reference card

```bash
# ── Browse ──
uv run src/install_rules.py list
uv run src/install_rules.py list-custom
uv run src/install_rules.py search fastapi
uv run src/install_rules.py stacks

# ── New project (pick one) ──
curl -fsSL .../install.sh | bash -s -- --custom-all --here
curl -fsSL .../install.sh | bash -s -- --stack personal-python-backend --here
curl -fsSL .../install.sh | bash -s -- --stack react-ts --here

# ── Add to existing project ──
curl -fsSL .../install.sh | bash -s -- react --here
curl -fsSL .../install.sh | bash -s -- --custom base --here

# ── Preview ──
curl -fsSL .../install.sh | bash -s -- --stack personal --here --dry-run

# ── Maintainer ──
uv run src/generate_catalog.py
uv run src/generate_mdc_files.py --library react
```

Replace `.../install.sh` with:

```
https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh
```
