# Skills

Snapshot of the agent skills installed in `~/.agents/skills`, kept here to record versions and local edits.

| Folder | Upstream | License |
|---|---|---|
| `mattpocock/` | [mattpocock/skills](https://github.com/mattpocock/skills) | MIT (`mattpocock/LICENSE`) |
| `nature/` | [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) | Apache-2.0 (`nature/LICENSE`) |
| `cmi-hpc/` | local, from [luketou/mdgen_neighbor](https://github.com/luketou/mdgen_neighbor) `.claude/skills/hpc-workflow` | none |
| `m5-hpc/` | local, m5 RTX 4090 cluster workflow | none |
| `slurm_alias/` | local, Slurm HPC alias shortcuts (`q`, `qs`, `pbs`) and node monitor | none |

Upstream hashes come from `~/.agents/.skill-lock.json` (`skillFolderHash`). Running `npx skills update` overwrites the local changes listed below; restore them from this repo.

## Local changes (2026-10-24)

- `mattpocock/implement`: adds Survey / Subtract / Audit-the-diff steps and lean rules (smallest diff, reuse before adding), based on pstack's laziness-protocol and subtract-before-you-add.
- `mattpocock/implement-spec`: implementer subagents follow steps 1-4 of `implement` instead of calling `tdd` directly, and the final report includes out-of-scope cleanup.
- `nature/nature-*`: descriptions rewritten with `writing-for-agents` (one trigger per branch, explicit hand-offs between overlapping skills); `nature-paper-trans`, `nature-literature-pipeline` and `nature-shared` set to `disable-model-invocation: true`; some bodies trimmed. Usage guide: `nature/USAGE.zh-TW.md`.

## Skill 功能與使用時機

「呼叫方式」欄：**自動**表示模型會依描述自行觸發，也可以手動輸入 `/名稱`；**手動**表示設了 `disable-model-invocation: true`，只能自己輸入 `/名稱` 呼叫。

### mattpocock：規劃與釐清

| Skill | 呼叫方式 | 功能 | 使用時機 |
|---|---|---|---|
| `ask-matt` | 手動 | 這套 skill 的導覽：根據你的情況推薦該用哪個 skill 或流程 | 忘了有哪些 skill、不確定從哪個開始時 |
| `grilling` | 自動 | 以決策樹方式一輪輪追問，直到雙方對計畫有共同理解 | 想把計畫、決策或想法的漏洞問出來時；說「grill」時觸發 |
| `grill-me` | 手動 | 呼叫 `grilling` 的捷徑 | 想直接開始被追問、壓力測試計畫時 |
| `grill-with-docs` | 手動 | `grilling` 加 `domain-modeling`：邊追問邊寫 ADR 與術語表 | 釐清設計的同時要留下決策紀錄與專案術語時 |
| `loop-me` | 手動 | 以追問的方式產出這個工作區的 workflow 規格 | 想把一個重複性工作流程定義清楚、寫成規格時 |
| `wayfinder` | 手動 | 把超過單一 session 能處理的大工作拆成 issue tracker 上的決策 ticket，逐一解決 | 目標很大、路徑還不清楚，需要先找方向時 |
| `to-questionnaire` | 手動 | 把你自己答不出來的決策整理成問卷，交給別人填 | 決策需要同事、指導教授或客戶提供資訊時 |
| `prototype` | 自動 | 寫一次性的原型程式來回答一個設計問題 | 想確認狀態模型、邏輯或 UI 長相是否合理，再決定正式做法時 |
| `research` | 自動 | 派背景 agent 查一手資料，結果寫成 repo 裡的 Markdown | 需要查文件、API 事實或做大量閱讀，又不想中斷手上工作時 |
| `teach` | 手動 | 跨多個 session 有狀態地教你一個主題 | 想有系統地學一個新概念或技術時 |

### mattpocock：規格與實作

| Skill | 呼叫方式 | 功能 | 使用時機 |
|---|---|---|---|
| `setup-matt-pocock-skills` | 手動 | 為 repo 設定 issue tracker、triage 標籤與領域文件位置 | 在一個 repo 第一次使用這套工程 skill 之前，執行一次 |
| `to-spec` | 手動 | 不再追問，直接把目前對話整理成 spec 並發佈到 issue tracker | 討論已經充分、要把結論定成規格時 |
| `to-tickets` | 手動 | 把計畫或 spec 拆成 tracer-bullet ticket，並標出彼此的阻擋關係 | spec 定好、要拆成可分頭實作的工作項目時 |
| `implement` | 手動 | 依 spec 或 ticket 實作：先盤點可重用的程式碼、先刪後加、檢查 diff 中每個新增，再 code review 與 commit（本 repo 有修改） | 實作單一件工作，想要最小 diff、不重複造輪子時 |
| `implement-spec` | 手動 | 依 ticket 依賴圖平行派出多個實作 subagent（各自照 `implement` 的步驟），合併到整合分支 | 一份 spec 有多張 ticket，要平行實作時 |
| `tdd` | 自動 | 紅→綠測試驅動開發的參考：好測試的標準、測試放哪、常見反模式 | 測試先行開發功能或修 bug、寫整合測試時 |
| `diagnosing-bugs` | 自動 | 針對難纏 bug 與效能退化的診斷流程 | 程式壞掉、拋錯、測試失敗或變慢，原因不明時 |
| `code-review` | 自動 | 從「是否符合 repo 規範」和「是否符合 spec」兩個面向，平行審查某個基準點之後的變更 | 審查分支、PR 或進行中的改動時 |
| `pr` | 自動 | PR 描述的範本 | 撰寫 PR body 時 |
| `triage` | 手動 | 用狀態機推進 issue 與外部 PR：分類、驗證、必要時追問，寫成 agent 可直接接手的簡報 | 整理 issue tracker 上待處理的 issue 與 PR 時 |

### mattpocock：架構與程式品質

| Skill | 呼叫方式 | 功能 | 使用時機 |
|---|---|---|---|
| `codebase-design` | 自動 | 設計 deep module（小介面、大量行為、清楚的 seam）的共用詞彙 | 設計或改善模組介面、決定 seam 放哪、讓程式更好測試時 |
| `improve-codebase-architecture` | 手動 | 掃描 codebase 找出可加深的模組，產出 HTML 報告，再針對選中的項目追問 | 想系統性地找出架構上的痛點與重構機會時 |
| `domain-modeling` | 自動 | 建立並精煉專案的領域模型：挑戰術語、想邊界案例、寫 GLOSSARY 與 ADR | 討論專案術語、編輯 GLOSSARY.md 或 ADR 時 |
| `setup-ts-deep-modules` | 手動 | 在 TypeScript repo 設定 dependency-cruiser，讓每個 package 只能透過入口檔存取 | 想在 TS monorepo 強制模組邊界時 |
| `migrate-to-shoehorn` | 自動 | 把測試中的 `as` 型別斷言改成 @total-typescript/shoehorn | TS 測試要用部分資料、想移除 `as` 時 |
| `setup-pre-commit` | 自動 | 設定 Husky pre-commit：lint-staged（Prettier）、型別檢查、測試 | 想在 commit 時自動格式化與檢查時 |
| `git-guardrails-claude-code` | 自動 | 設定 Claude Code hook，在執行前擋下 push、reset --hard、clean 等危險 git 指令 | 想防止 agent 做出破壞性的 git 操作時 |

### mattpocock：Session 與協作

| Skill | 呼叫方式 | 功能 | 使用時機 |
|---|---|---|---|
| `chief-of-staff` | 手動 | 在單一長時間 session 中協調 subagent 與排程，持續追一個長期目標 | 目標需要長時間、多個 agent 輪流推進時 |
| `handoff` | 手動 | 把目前對話壓縮成交接文件，存到暫存目錄 | context 快滿或要換 agent 接手時 |
| `claude-handoff` | 手動 | 寫交接摘要並立刻啟動背景 agent 接手 | 想讓新的 agent 馬上在背景接續目前工作時 |
| `retro` | 手動 | 對一次 coding session 做回顧，建議如何改善 agent 的環境（文件、skill、設定） | session 結束後想讓下次跑得更順時 |
| `wait-what` | 手動 | 要求 agent 用簡化技術英文、補上脈絡重新說明上一則訊息 | 看不懂 agent 剛剛在說什麼時 |
| `wizard` | 自動 | 產生互動式 bash 精靈，帶人一步步完成只有人能做的操作 | 設定雲端資源、憑證、CI secret、第三方後台或一次性遷移時 |
| `scaffold-exercises` | 自動 | 建立課程練習的目錄結構（題目、解答、說明）並通過 lint | 建立 AI Hero 課程練習或新章節時 |

### mattpocock：寫作

| Skill | 呼叫方式 | 功能 | 使用時機 |
|---|---|---|---|
| `writing-for-agents` | 自動 | 撰寫給 agent 讀的文件的原則：context pointer、資訊層級、完成條件、刪減 | 建立或修改 skill、AGENTS.md、CLAUDE.md 時 |
| `writing-fragments` | 手動 | 寫作的發散階段：先挖出零散素材，不講結構 | 文章剛起步、還在蒐集想法時 |
| `writing-beats` | 手動 | 把素材組成一連串 beat（敘事節點），每個術語先定義再使用 | 素材夠了，要排出文章的推進順序時 |
| `writing-shape` | 手動 | 把素材逐段塑形成一篇文章 | 結構已定，要寫成完整段落時 |

### nature：文獻檢索與取得

| Skill | 呼叫方式 | 功能 | 使用時機 |
|---|---|---|---|
| `nature-academic-search` | 自動 | 跨資料庫檢索文獻（不限期刊）、MeSH/PubMed 檢索策略、檢查引文是否存在、`.ris/.bib/.nbib` 轉換、嚴格他引與引用者分析 | 一次性找文獻、轉換書目格式、算他引時 |
| `nature-citation` | 自動 | 為稿件中的論點逐段配上 Nature/CNS 系列支撐文獻，匯出 RIS/EndNote/Zotero | 只要 Nature/CNS 系列的引用時；不限期刊改用 `nature-academic-search` |
| `nature-ref-verifier` | 自動 | 參考文獻逐欄位多源校驗（作者、標題、年份、卷期、頁碼、DOI），輸出分級報告與修正版 BibTeX | 投稿或開題前核對整份參考文獻時 |
| `nature-downloader` | 自動 | 透過 OA、出版社 API、知網與機構授權合法下載全文與 SI | 已知要讀哪幾篇，需要 PDF 或補充材料時 |
| `nature-literature-pipeline` | 手動 | 設定每日定時文獻推送：檢索、六維評分、精讀、推送到飛書/Telegram、歸檔 | 想持續追蹤某個研究方向的新文獻時 |

### nature：閱讀與報告

| Skill | 呼叫方式 | 功能 | 使用時機 |
|---|---|---|---|
| `nature-reader` | 自動 | 已發表論文的中英對照閱讀版（含圖表、公式、出處對照），或針對論文的帶出處問答 | 想讀懂一篇英文論文、問某張圖在說什麼時 |
| `nature-paper-card` | 自動 | 單篇論文的 16 節精讀卡：方法、主張與證據鏈、局限、研究點子 | 要深入拆解一篇論文的方法與證據時 |
| `nature-paper-trans` | 手動 | 英文論文 PDF 逐頁譯成保留版式的簡體中文圖片型 PDF（需要 `image_gen` 生圖工具，Claude Code 通常無法執行） | 需要版面與原文一致的中文 PDF 時 |
| `nature-paper2ppt` | 自動 | 從論文或閱讀筆記做中文學術 PPTX（含原圖與講稿） | 組會報告、文獻匯報、會議或答辯簡報時 |
| `nature-image2ppt` | 自動 | 把投影片圖片、截圖、掃描 PDF 重建成可編輯的 PowerPoint | 手上只有圖片型投影片，需要改內容時 |

### nature：寫作與投稿

| Skill | 呼叫方式 | 功能 | 使用時機 |
|---|---|---|---|
| `nature-writing` | 自動 | 依作者提供的證據起草章節、重構論證、調整正文與 SI 的分配、準備首次投稿材料 | 寫新章節、重組 Results、準備 cover letter 時 |
| `nature-polishing` | 自動 | 潤色既有文字（事實與主張不變）、自己中文稿的中譯英、跨段一致性、LaTeX 排版 | 內容已定，只要改語言或版面時 |
| `researchwrite` | 自動 | 撰寫、修改或審查研究計畫、開題報告、科研項目申請書 | 寫開題報告或計畫書時；一般論文章節改用 `nature-writing` |
| `nature-figure` | 自動 | 用 Python 或 R 畫、改、審、匯出投稿用多面板科研圖；明確要求時可用 AI 生成圖形摘要 | 製作或檢查論文圖表時 |
| `nature-statistics` | 自動 | 審查統計報告：實驗單位、n、檢定、不確定性、圖注統計；起草統計方法小節 | 檢查統計寫法、寫 Statistical analysis 時 |
| `nature-data` | 自動 | 撰寫或審查 Data/Code Availability 聲明、選資料倉儲、FAIR metadata | 投稿前寫資料可用性聲明時 |
| `nature-experiment-log` | 自動 | 把照片、語音、文字整理成帶 YAML frontmatter 與實驗 ID 的標準 Markdown 實驗日誌 | 記錄或整理每天的實驗紀錄時 |
| `nature-reviewer` | 自動 | 模擬審稿：三份互相獨立的審稿報告加上綜合意見 | 投稿前想先從審稿人角度挑毛病時 |

### nature：返修與其他

| Skill | 呼叫方式 | 功能 | 使用時機 |
|---|---|---|---|
| `nature-response` | 自動 | 收到期刊決定後：逐點回覆審稿意見、返修信、修訂標記稿 | 收到真實審稿意見、準備返修時 |
| `nature-paper-to-patent` | 自動 | 從論文或發明人資料起草中國發明專利：權利要求書、說明書、技術交底書 | 想把研究成果申請專利時 |
| `nature-shared` | 手動 | 其他 nature skill 依路徑讀取的共用參考檔 | 不需要直接呼叫 |

更完整的邊界說明（遇到哪些情況改用哪個 skill）見 [`nature/USAGE.zh-TW.md`](nature/USAGE.zh-TW.md)。

### HPC 與叢集工具

| Skill / Tool | 呼叫方式 | 功能 | 使用時機 |
|---|---|---|---|
| `cmi-hpc` | 自動 / 手動 | CMI Slurm HPC job 的提交、smoke test、佇列與失敗分析 | 在 Slurm 叢集上跑分片工作與大規模運算時 |
| `m5-hpc` | 自動 / 手動 | m5 主機群（RTX 4090，無 Slurm，用 tmux）的部署與訓練流程 | 在 m5 cluster 跑 GPU 訓練或生成時 |
| `slurm-alias` | Shell / 手動 | Slurm 常用別名（`q`, `qs`, `pbs`）與節點/GPU 資源即時監看腳本 | 在 Slurm 叢集查詢排程、尋找空閒 GPU/CPU 節點或監控資源時（詳見 [`slurm_alias/README.md`](slurm_alias/README.md)） |

## 版本紀錄

### mattpocock

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

### nature

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