# Skills

Snapshot of the agent skills installed in `~/.agents/skills`, kept here to record versions and local edits.

| Folder | Upstream | License |
|---|---|---|
| `mattpocock/` | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT (`mattpocock/LICENSE`) |
| `nature/` | [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) | Apache-2.0 (`nature/LICENSE`) |

Upstream hashes come from `~/.agents/.skill-lock.json` (`skillFolderHash`). Running `npx skills update` overwrites the local changes listed below; restore them from this repo.

## Local changes (2026-10-24)

- `mattpocock/implement`: adds Survey / Subtract / Audit-the-diff steps and lean rules (smallest diff, reuse before adding), based on pstack's laziness-protocol and subtract-before-you-add.
- `mattpocock/implement-spec`: implementer subagents follow steps 1-4 of `implement` instead of calling `tdd` directly, and the final report includes out-of-scope cleanup.
- `nature/nature-*`: descriptions rewritten with `writing-for-agents` (one trigger per branch, explicit hand-offs between overlapping skills); `nature-paper-trans`, `nature-literature-pipeline` and `nature-shared` set to `disable-model-invocation: true`; some bodies trimmed. Usage guide: `nature/USAGE.zh-TW.md`.

## mattpocock

| Skill | Upstream folder hash | Installed/updated | Local changes |
|---|---|---|---|
| `ask-matt` | `d6a0d9bf3cdc` | 2026-10-20 | unchanged |
| `chief-of-staff` | `dbdf91354f95` | 2026-10-20 | unchanged |
| `claude-handoff` | `57d198aca08e` | 2026-10-20 | unchanged |
| `codebase-design` | `07ba1cd60efc` | 2026-10-20 | unchanged |
| `code-review` | `fee7bb5fdddc` | 2026-10-20 | unchanged |
| `diagnosing-bugs` | `5fdd6cc53385` | 2026-10-20 | unchanged |
| `domain-modeling` | `ea30ee454ba2` | 2026-10-20 | unchanged |
| `git-guardrails-claude-code` | `ceed97af0963` | 2026-10-20 | unchanged |
| `grilling` | `28aceb4c9567` | 2026-10-20 | unchanged |
| `grill-me` | `3df14e2d3a89` | 2026-10-20 | unchanged |
| `grill-with-docs` | `eedaf2562c83` | 2026-10-20 | unchanged |
| `handoff` | `ce24892bd2d4` | 2026-10-20 | unchanged |
| `implement` | `4804b466ab26` | 2026-10-20 | modified 2026-10-24 |
| `implement-spec` | `0cfefc751d0c` | 2026-10-20 | modified 2026-10-24 |
| `improve-codebase-architecture` | `39bd9cc130f7` | 2026-10-20 | unchanged |
| `loop-me` | `a0dfdc356268` | 2026-10-20 | unchanged |
| `migrate-to-shoehorn` | `0aea91a3599a` | 2026-10-20 | unchanged |
| `pr` | `00b896d811ad` | 2026-10-20 | unchanged |
| `prototype` | `e41d92e171f0` | 2026-10-20 | unchanged |
| `research` | `0a6796c5667e` | 2026-10-20 | unchanged |
| `retro` | `335c1862a43d` | 2026-10-20 | unchanged |
| `scaffold-exercises` | `44a0ee332b9d` | 2026-10-20 | unchanged |
| `setup-matt-pocock-skills` | `aafaabf96fa3` | 2026-10-20 | unchanged |
| `setup-pre-commit` | `5b63f9f665ba` | 2026-10-20 | unchanged |
| `setup-ts-deep-modules` | `b32508a8a7d6` | 2026-10-20 | unchanged |
| `tdd` | `667dbdd00c09` | 2026-10-20 | unchanged |
| `teach` | `3fd617b610e5` | 2026-10-20 | unchanged |
| `to-questionnaire` | `46dfbeeba12a` | 2026-10-20 | unchanged |
| `to-spec` | `136b9651747c` | 2026-10-20 | unchanged |
| `to-tickets` | `2dee20ad722a` | 2026-10-20 | unchanged |
| `triage` | `4cb951d62ecc` | 2026-10-20 | unchanged |
| `wait-what` | `c8b050e6b8c7` | 2026-10-20 | unchanged |
| `wayfinder` | `32b0ce970b13` | 2026-10-20 | unchanged |
| `wizard` | `e396d3ba97c7` | 2026-10-20 | unchanged |
| `writing-beats` | `3a28fb076fda` | 2026-10-20 | unchanged |
| `writing-for-agents` | `ad2925850efb` | 2026-10-20 | unchanged |
| `writing-fragments` | `98e500e0097e` | 2026-10-20 | unchanged |
| `writing-shape` | `ac92229646fc` | 2026-10-20 | unchanged |

## nature

| Skill | Upstream folder hash | Installed/updated | Local changes |
|---|---|---|---|
| `nature-academic-search` | `6f8c8b44d791` | 2026-10-07 | modified 2026-10-24 |
| `nature-citation` | `371df73411e1` | 2026-10-07 | modified 2026-10-24 |
| `nature-data` | `68ec0a065ec8` | 2026-10-07 | modified 2026-10-24 |
| `nature-downloader` | `0d6c5cdbf5a4` | 2026-10-07 | modified 2026-10-24 |
| `nature-experiment-log` | `0f33f75d2898` | 2026-10-07 | modified 2026-10-24 |
| `nature-figure` | `38168eac341f` | 2026-10-07 | modified 2026-10-24 |
| `nature-image2ppt` | `d41c300345b6` | 2026-10-07 | modified 2026-10-24 |
| `nature-literature-pipeline` | `8daac5e475a4` | 2026-10-07 | modified 2026-10-24 |
| `nature-paper2ppt` | `b41df90544a8` | 2026-10-07 | modified 2026-10-24 |
| `nature-paper-card` | `f990462f5a4b` | 2026-10-07 | modified 2026-10-24 |
| `nature-paper-to-patent` | `e5252108262b` | 2026-10-07 | modified 2026-10-24 |
| `nature-paper-trans` | `7e9d52cd3fc1` | 2026-10-07 | modified 2026-10-24 |
| `nature-polishing` | `8fa324de5b88` | 2026-10-07 | modified 2026-10-24 |
| `nature-reader` | `547cd103d79b` | 2026-10-07 | modified 2026-10-24 |
| `nature-ref-verifier` | `eb66dd3ffe61` | 2026-10-07 | modified 2026-10-24 |
| `nature-response` | `5f80cf7a54bb` | 2026-10-07 | modified 2026-10-24 |
| `nature-reviewer` | `7b9057c8ba0a` | 2026-10-07 | modified 2026-10-24 |
| `nature-shared` | `bdfa1d654f13` | 2026-10-07 | modified 2026-10-24 |
| `nature-statistics` | `a06c4450e7ee` | 2026-10-07 | modified 2026-10-24 |
| `nature-writing` | `ac10ae2ef28d` | 2026-10-07 | modified 2026-10-24 |
| `researchwrite` | `81a5b859d215` | 2026-10-07 | unchanged |