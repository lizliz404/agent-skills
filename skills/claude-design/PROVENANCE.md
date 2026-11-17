# PROVENANCE (do not delete)

- Source: `/home/liz/Downloads/skills-no-public-url.zip`
  sha256 `c6105d04e1693f6426eddc8d8f759e7c1e3783300273cb2a4a47149e70307e4d`
  (52,977 bytes, received 2026-09-30; local pack, no public URL).
- Per README.txt inside the zip: `claude-design/` = single-file HTML explainer
  method (a.k.a. Codex-design); `presentation-logic/` + `html-slides/` from an
  academic-research-assistant bundle.
- Flattened on install: the zip nests the latter two under
  `academic-research-assistant/`; nesting breaks one-level skill discovery,
  so they live here as siblings with this note instead.
- License: NONE declared in the zip (no LICENSE file, no license field in
  frontmatter). Treat as unlicensed local material: internal use only,
  do not republish or push to any public repo.
- Security audit 2026-09-30: no `..`/absolute paths, no symlinks, no
  executables, no scripts/postinstall (19 files: 18×.md + README.txt).
  Gaps vs SKILL.md cross-refs: `references/design-styles.md` IS present
  (13,920 bytes); `assets/` starter templates referenced by SKILL.md §"Technical
  scaffolding"/"Quick reference index" are MISSING from the zip — deck/prototype
  builds must use design-templates `decks/upstream/` starters instead.
- Exposure: NOT bridged to `~/.agents/skills`, no Pi/OpenCode config change.
  New resident skill names = 0. Reached only via the design-templates router.
