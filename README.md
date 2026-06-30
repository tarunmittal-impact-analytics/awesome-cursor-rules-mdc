# MDC Rules Generator

> **Disclaimer:** This project is not officially associated with or endorsed by Cursor. It is a community-driven initiative to enhance the Cursor experience.
>
> Forked from [sanjeed5/awesome-cursor-rules-mdc](https://github.com/sanjeed5/awesome-cursor-rules-mdc).

This project generates Cursor MDC (Markdown Cursor) rule files from a structured JSON file containing library information. It uses Exa for semantic search and LLM (Gemini) for content generation.

**📖 [Complete Usage Guide →](GUIDE.md)** — full reference for installing rules, preset stacks, personal rules, web catalog, curl/CLI, and new project setup.

[![Star History Chart](https://api.star-history.com/svg?repos=tarunmittal-impact-analytics/awesome-cursor-rules-mdc&type=Date)](https://www.star-history.com/#tarunmittal-impact-analytics/awesome-cursor-rules-mdc&Date)

## Features

- Generates comprehensive MDC rule files for libraries
- Uses Exa for semantic web search to gather best practices
- Leverages LLM to create detailed, structured content
- Supports parallel processing for efficiency
- Tracks progress to allow resuming interrupted runs
- Smart retry system that focuses on failed libraries by default

## Prerequisites

- Python 3.8+
- [uv](https://github.com/astral-sh/uv) for dependency management
- API keys for:
  - Exa (for semantic search)
  - LLM provider (Gemini, OpenAI, or Anthropic)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc.git
   cd awesome-cursor-rules-mdc
   ```

2. Install dependencies using uv:
   ```bash
   uv sync
   ```

3. Set up environment variables:
   Create a `.env` file in the project root with your API keys (see `.env.example`):
   ```
   EXA_API_KEY=your_exa_api_key
   GEMINI_API_KEY=your_google_gemini_api_key  # For Gemini
   # Or use one of these depending on your LLM choice:
   # OPENAI_API_KEY=your_openai_api_key
   # ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

## Usage

Run the generator script with:

```bash
uv run src/generate_mdc_files.py
```

By default, the script will only process libraries that failed in previous runs.

### Command-line Options

- `--test`: Run in test mode (process only one library)
- `--tag TAG`: Process only libraries with a specific tag
- `--library LIBRARY`: Process only a specific library
- `--output OUTPUT_DIR`: Specify output directory for MDC files
- `--verbose`: Enable verbose logging
- `--workers N`: Set number of parallel workers
- `--rate-limit N`: Set API rate limit calls per minute
- `--regenerate-all`: Process all libraries, including previously completed ones

### Examples

```bash
# Process failed libraries (default behavior)
uv run src/generate_mdc_files.py

# Regenerate all libraries
uv run src/generate_mdc_files.py --regenerate-all

# Process only Python libraries
uv run src/generate_mdc_files.py --tag python

# Process a specific library
uv run src/generate_mdc_files.py --library react
```

## Install Rules in Your Project

Browse and install rules into any project's `.cursor/rules` folder.

### Quick start

From this repo:

```bash
# Install specific libraries into your project
uv run src/install_rules.py install react fastapi --target ~/my-app/.cursor/rules

# Or from inside your project
cd ~/my-app
uv run /path/to/awesome-cursor-rules-mdc/src/install_rules.py install react --here
```

From any machine (no clone required):

```bash
# Fetch rules directly from GitHub
uv run src/install_rules.py install react fastapi --here --source github
```

### Browse the catalog

```bash
uv run src/install_rules.py list                    # all 241 rules
uv run src/install_rules.py list --tag python       # filter by tag
uv run src/install_rules.py tags                    # all tags with counts
uv run src/install_rules.py search fastapi          # search by name/tag
uv run src/install_rules.py stacks                  # preset bundles
```

### Install by use case

**By tag** (installs every rule matching any of the tags):

```bash
uv run src/install_rules.py install --tag python --tag backend --here
```

**By preset stack** (curated bundles in `stacks.json`):

```bash
uv run src/install_rules.py install --stack python-backend --here
uv run src/install_rules.py install --stack react-ts --here
uv run src/install_rules.py install --stack ai-llm --here
```

Available stacks: `python-backend`, `python-django`, `python-flask`, `react-ts`, `next-js-fullstack`, `vue-frontend`, `angular-frontend`, `data-ml`, `ai-llm`, `devops`, `aws-cloud`, `rust-web`, `go-backend`, `mobile-flutter`, `e2e-testing`, `personal`, `personal-python-backend`, `personal-react-ts`

### Personal / custom rules

Personal workflow rules live in `rules-custom/` (from `Desktop/Personal/cursor_rules`):

| Rule | Purpose |
|------|---------|
| `base` | Always-on core behavior (concise, incremental edits) |
| `simple` | Docs, tests, small files |
| `complex` | Architecture and large refactors |
| `frontend` | UI component conventions |
| `backend` | API/DB/server conventions |

```bash
# Install all personal rules
uv run src/install_rules.py install --custom-all --here

# Pick specific personal rules
uv run src/install_rules.py install --custom base frontend backend --here

# Personal rules + library stack
uv run src/install_rules.py install --stack personal-python-backend --here --source github

# List personal rules
uv run src/install_rules.py list-custom
```

Curl equivalent:

```bash
curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh | bash -s -- --custom-all --here
curl -fsSL .../install.sh | bash -s -- --custom base frontend --here
curl -fsSL .../install.sh | bash -s -- --stack personal --here
```

### Options

| Flag | Description |
|------|-------------|
| `--here` | Install into `./.cursor/rules` in the current directory |
| `--target PATH` | Install into a specific `.cursor/rules` directory |
| `--source local` | Copy from local `rules-mdc/` (default) |
| `--source github` | Fetch from GitHub raw URLs (no clone needed) |
| `--force` | Overwrite existing rule files |
| `--dry-run` | Preview without copying |
| `--custom NAME` | Install personal rules from `rules-custom/` |
| `--custom-all` | Install all personal rules |
| `--custom-tag TAG` | Install personal rules matching tag |

### Curl installer (no Python required)

```bash
# Install specific rules
curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh | bash -s -- react fastapi --here

# Install a preset stack
curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh | bash -s -- --stack python-backend --here

# Install by tag
curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh | bash -s -- --tag python --tag backend --here
```

Options: `--here`, `--target PATH`, `--stack NAME`, `--tag TAG`, `--custom`, `--custom-all`, `--force`, `--dry-run`

Override repo source with env vars: `CURSOR_RULES_REPO=owner/repo CURSOR_RULES_BRANCH=main`

### Web catalog

Browse all rules visually and copy install commands:

**https://tarunmittal-impact-analytics.github.io/awesome-cursor-rules-mdc/**

The catalog supports search, tag filters, multi-select, preset stacks, and one-click copy for curl/uv commands.

To regenerate `docs/catalog.json` after updating `rules.json` or `repo.json`:

```bash
uv run src/generate_catalog.py
```

GitHub Pages deploys automatically from `docs/` on push to `main` (enable Pages → Source: GitHub Actions in repo settings).

### Fork configuration

Repo URLs are centralized in `repo.json`. After forking, update it once:

```json
{
  "repo": "your-github-username/awesome-cursor-rules-mdc",
  "branch": "main",
  "upstream": "sanjeed5/awesome-cursor-rules-mdc"
}
```

Then sync generated URLs:

```bash
uv run src/generate_catalog.py
```

This updates `docs/catalog.json`, curl examples in `install.sh`, and GitHub Pages install links. Python tools also auto-detect `origin` from git when run locally.

## Adding New Rules

Adding support for new libraries is simple:

1. **Edit the rules.json file**:
   - Add a new entry to the `libraries` array:
   ```json
   {
     "name": "your-library-name",
     "tags": ["relevant-tag1", "relevant-tag2"]
   }
   ```

2. **Generate the MDC files**:
   - Run the generator script:
   ```bash
   uv run src/generate_mdc_files.py
   ```
   - The script automatically detects and processes new libraries

3. **Contribute back**:
   - Test your new rules with real projects
   - Consider raising a PR to contribute your additions back to the community

## Configuration

The script uses a `config.yaml` file for configuration. You can modify this file to adjust:

- API rate limits
- Output directories
- LLM model selection
- Processing parameters

## Project Structure

```
.
├── repo.json             # Fork repo coordinates (owner/repo, branch, upstream)
├── docs/                 # Static web catalog (GitHub Pages)
│   ├── index.html
│   └── catalog.json
├── install.sh            # Curl-based installer script
├── src/                  # Main source code directory
│   ├── generate_mdc_files.py  # Main generator script
│   ├── install_rules.py  # CLI to browse and install rules
│   ├── generate_catalog.py  # Build docs/catalog.json and sync fork URLs
│   ├── repo_config.py    # Resolve repo slug from repo.json / git / env
│   ├── config.yaml       # Configuration file
│   ├── mdc-instructions.txt   # Instructions for MDC generation
│   ├── logs/             # Log files directory
│   └── exa_results/      # Directory for Exa search results
├── rules-mdc/            # Output directory for generated MDC files
├── rules-custom/         # Personal/custom MDC rules
├── custom-rules.json     # Catalog for personal rules
├── rules.json            # Input file with library information
├── stacks.json           # Preset rule bundles for common stacks
├── GUIDE.md              # Complete usage guide (install, stacks, custom rules)
├── pyproject.toml        # Project dependencies and metadata
├── .env.example          # Example environment variables
└── LICENSE               # MIT License
```

## License

[MIT License](LICENSE)
