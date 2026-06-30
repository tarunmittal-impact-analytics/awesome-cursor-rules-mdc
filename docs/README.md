# Documentation

Unified docs live in three places — same content, different formats:

| Format | URL / path | Best for |
|--------|------------|----------|
| **Web docs (GitHub Pages)** | [guide.html](https://tarunmittal-impact-analytics.github.io/awesome-cursor-rules-mdc/guide.html) | Browsing concepts, use cases, rules vs stacks |
| **Web catalog** | [index.html](https://tarunmittal-impact-analytics.github.io/awesome-cursor-rules-mdc/) | Search rules/stacks, copy install commands |
| **Full reference** | [GUIDE.md](../GUIDE.md) | Complete CLI reference, maintainer workflows |
| **Overview** | [README.md](../README.md) | Quick start, features |

## GitHub Pages structure

```
docs/
├── index.html      # Browse/search catalog (rules, personal, stacks tabs)
├── guide.html      # Documentation — what is it, concepts, use cases
├── styles.css      # Shared styles for both pages
└── catalog.json    # Generated from rules.json + custom-rules.json + stacks.json
```

### Documentation sections (`guide.html`)

1. **What is this?** — repo purpose, counts, no-clone install
2. **Cursor rules** — what `.mdc` files are, frontmatter fields
3. **Key concepts** — library rules, personal rules, stacks
4. **Rules vs stacks** — detailed comparison with examples
5. **File structure** — why so many files, JSON indexes explained
6. **Use cases** — stacks by project type (backend, data eng, gen-ai, mobile)
7. **How to install** — curl, CLI, web catalog
8. **Mental model** — quick reference diagram
9. **For maintainers** — add new library rules

## Regenerate catalog

After changing `rules.json`, `custom-rules.json`, or `stacks.json`:

```bash
uv run src/generate_catalog.py
```

GitHub Pages redeploys automatically on push to `main` when `docs/**` or catalog sources change.

## Quick install

```bash
# Browse stacks
uv run src/install_rules.py stacks

# Install a stack into your project
curl -fsSL https://raw.githubusercontent.com/tarunmittal-impact-analytics/awesome-cursor-rules-mdc/main/install.sh \
  | bash -s -- --stack gen-ai-graph-rag --here
```

## Catalog stats

| Type | Count | Location |
|------|-------|----------|
| Library rules | 296 | `rules-mdc/` |
| Custom rules | 24 | `rules-custom/` |
| Preset stacks | 96 | `stacks.json` |
