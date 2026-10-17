# Vendored reference snapshots

Read-only snapshots of the projects talkcut learned from, kept so agents can read their source offline.
Each was a shallow clone of the default branch on 2026-10-17 (UTC+8), with `.git` removed (plain files, not submodules).
talkcut's own scripts do not import any of this code.

**License notice:** every folder here keeps its **own upstream license**. The repository's MIT license does **not** apply to these files. AGPL-3.0 (ai-jian-koubo, hotclip) and CC BY-NC 4.0 (dbskill, non-commercial only) carry obligations of their own, so check them before reusing any of this code.

| Folder | Upstream | Commit | Commit date | License | Size | Stripped |
|---|---|---|---|---|---|---|
| `dbskill/` | https://github.com/dontbesilent2025/dbskill | `926bcb9ae40f348f080f387b259fee4ec0b75f55` | 2026-10-17 | CC BY-NC 4.0 | 6.1 MB | `books/*.pdf` (9 MB), `books/*开源推文集.md` (1.3 MB), `知识库/原子库/atoms.jsonl` (2.7 MB), `demo.gif` |
| `chengfeng-videocut-skills/` | https://github.com/Agentchengfeng/chengfeng-videocut-skills | `a33b43e08c34fa8beeb5e78498e852f4e80975a5` | 2026-09-20 | Apache-2.0 (LICENSE + NOTICE.md kept) | 3.6 MB | nothing |
| `ai-jian-koubo/` | https://github.com/lcbuaaliu/ai-jian-koubo | `e223b91ed82446182e52dc2806ee69d8bcab0485` | 2026-06-24 | AGPL-3.0 | 2.2 MB | `assets/review-ui.png` (1.4 MB) |
| `ai-xunjian/` | https://github.com/fxl1209739475-fxl/ai-xunjian | `dbfba5f5f78490c627dc8e79fc47d518efd19199` | 2026-08-07 | MIT | 1.2 MB | nothing |
| `FunClip/` | https://github.com/modelscope/FunClip | `36acf72e2add3c4af33fd35d373574a5dee96482` | 2026-10-08 | MIT | 1.2 MB | `font/STHeitiMedium.ttc` (56 MB), 4 doc images over 1 MB |
| `hotclip/` | https://github.com/xixihhhh/hotclip | `4f4347d12c8a989d16be46aaeed7455d1f35f992` | 2026-10-08 | AGPL-3.0 | 7.1 MB | `resources/fonts/SourceHanSansSC-Bold.otf` (17 MB), `docs/media/clip-*.mp4` |
| `cli/` (Gitruck) | https://github.com/Gitruck/cli | `b13422c057ede71928777839be635a1e1377cc8b` | 2026-10-17 | MIT | 7.5 MB | nothing (`.gitmodules` kept as a plain file; submodules not fetched) |
| `hyperframes/` | https://github.com/heygen-com/hyperframes | `b18b3e958aa199529fa5fa06728e81b97d520021` | 2026-10-17 | Apache-2.0 | 9.8 MB | **Partial snapshot** (full repo is 348 MB): kept only `README.md`, `LICENSE`, `CREDITS.md`, `skills/embedded-captions`, `skills/talking-head-recut`, `skills/hyperframes-core`, `registry/components/caption-*`, `packages/core/src` + `package.json`. Dropped: docs, examples, other skills and packages, registry blocks, and all media |

Stripping rules for every repo: removed `.git`, `node_modules`, `__pycache__`, video/audio/archive/model-weight/font files, GIFs, and any file over 1 MB. `.env*` files were removed except `*.example` templates, which contain placeholders only.

To refresh: re-clone with `--depth 1`, apply the same rules, and update this table.
