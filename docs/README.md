# Documentation

| Document | Description |
|----------|-------------|
| [README.md](../README.md) | Project overview, quick install, features |
| [GUIDE.md](../GUIDE.md) | Complete usage reference (296 rules, 24 custom, 54 stacks) |

## Web catalog

**Live site:** https://tarunmittal-impact-analytics.github.io/awesome-cursor-rules-mdc/

Built from this folder:
- `index.html` — browse/search UI
- `catalog.json` — generated from `rules.json`, `custom-rules.json`, `stacks.json`

Regenerate after catalog changes:
```bash
uv run src/generate_catalog.py
```

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
| Preset stacks | 54 | `stacks.json` |
