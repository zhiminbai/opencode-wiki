# opencode-wiki — Agent Guide

**What this is:** A daily-research wiki for OpenCode. Covers finance (金融),
product knowledge (产品), daily life (生活), learning (学习), and
reading (阅读). Follows the
[Karpathy LLM-Wiki](https://github.com/2233admin/obsidian-llm-wiki) three-layer
pattern: `sources/` → `concepts/` + `entities/` → `synthesis/`.

No build step, no dev server, no linter. Only plain Markdown.

## Directory structure

```
inbox/        # Raw incoming material (clippings, screenshots, drafts)
sources/      # Source summaries — one file per ingested source
  ├── 金融/   #   Finance sources
  ├── 产品/   #   Product sources
  ├── 生活/   #   Daily life sources
  ├── 学习/   #   Learning sources
  └── 阅读/   #   Reading sources
concepts/     # Frameworks, methods, terms, theories
  ├── 金融/
  ├── 产品/
  ├── 生活/
  ├── 学习/
  └── 阅读/
entities/     # People, companies, tools, organizations
  ├── 金融/
  ├── 产品/
  ├── 生活/
  ├── 学习/
  └── 阅读/
synthesis/    # Cross-topic analysis, query answers, monthly reviews
  ├── 金融/
  ├── 产品/
  ├── 生活/
  ├── 学习/
  └── 阅读/
index.md      # Wiki catalog — read this first before any operation
log.md        # Append-only operation log
AGENTS.md     # This file — update when workflow patterns emerge
```

## Page conventions

- **Frontmatter:** every page has `type:` (`source`, `concept`, `entity`, `synthesis`)
  and `date_updated:`.
- **Tags:** domain prefix: `金融/`, `产品/`, `生活/`, `学习/`, `阅读/`.
- **Wikilinks:** use `[[wikilinks]]` for cross-references.
- **Source pages** summarize a single input. Keep them factual.
  Interpretation goes in concept/entity pages.
- **Concept pages** can include `confidence:` (high/medium/low) to track
  how well-supported a claim is.
- **Synthesis pages** cite their sources and note contradictions explicitly.

## Operations

1. **Ingest** a source → create entry in `sources/` → update/create
   related `concepts/` and `entities/` → update `index.md` → append `log.md`.
2. **Query** the wiki → search `index.md` + grep across all dirs → cite sources.
3. **Never modify `inbox/` entries** after ingest. Treat them as read-only
   source evidence.

What matters: `index.md` and `log.md` must be kept current. Every write
operation finishes with both updated.

## Watch for

If any of these appear, the setup has changed — update this file:
- `package.json`, `pnpm-lock.yaml`, or package-manager files → package scripts
- `.github/` workflows → CI steps
- `Makefile` / `justfile` → task runner commands
- Other instruction files (`CLAUDE.md`, `.cursor/rules/`, `opencode.json`)
