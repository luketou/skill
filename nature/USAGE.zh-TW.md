# Nature Skills 使用指南

來源：`npx skills` 從 `Yuan1z0825/nature-skills` 安裝，兩份複本在 `C:\Users\toulu\.agents\skills` 與 `C:\Users\toulu\.claude\skills`（不是 junction，修改時兩份都要改）。2026-10-24 已依 `writing-for-agents` 改寫 description 與部分內文；執行 `npx skills update` 會覆蓋這些修改。

## 一、工作流程地圖

```text
找文獻 ──────────► 讀文獻 ──────────► 寫作 ─────────► 圖表／統計／資料 ──► 投稿 ──────────► 返修
academic-search    reader             writing         figure                writing          response
citation (CNS)     paper-card         polishing       statistics            (投稿材料)        polishing
downloader         /paper-trans       (researchwrite  data                  reviewer          statistics
/literature-       paper2ppt (組會)    開題/計畫書)    experiment-log        (投稿前自審)      ref-verifier
 pipeline (定期)                                       (實驗紀錄)            ref-verifier
                                                                            (參考文獻定稿)
旁支：paper-to-patent（論文 → 專利）、image2ppt（圖片 → 可編輯 PPT）
```

標 `/` 的兩個 skill 已改為「手動呼叫」（`disable-model-invocation: true`），模型不會自動觸發，要自己輸入 `/nature-paper-trans`、`/nature-literature-pipeline`。`nature-shared` 也已改為手動，它只是其他 nature skill 依路徑讀取的共用參考檔，不需要也不該直接呼叫。

## 二、各 skill 一覽

### 找文獻

| Skill | 用途 | 典型說法 | 邊界：這些情況改用 |
|---|---|---|---|
| `nature-academic-search` | 跨資料庫找文獻（不限期刊）、MeSH/PubMed 檢索策略、檢查文件中的引文是否存在、`.ris/.bib/.nbib` 轉換、嚴格他引與引用者畫像 | 「幫我找 2020 年後關於 X 的文獻」「把這個 .nbib 轉成 .bib」「算這篇的嚴格他引」 | 只要 Nature/CNS 系列 → `nature-citation`；逐欄位校正參考文獻 → `nature-ref-verifier`；每天自動推送 → `/nature-literature-pipeline`；要下載全文 → `nature-downloader` |
| `nature-citation` | 為稿件中的論點逐段配上 Nature/CNS 系列支撐文獻，輸出 RIS/EndNote/Zotero | 「幫這段補 Nature 系列的引用」「找 CNS 文獻支撐這個說法」 | 不限期刊 → `nature-academic-search` |
| `nature-ref-verifier` | 參考文獻逐欄位多源校驗（作者、標題、年、卷期、頁碼、DOI），輸出分級報告與 BibTeX/Zotero 修正 | 「核對這篇論文的參考文獻」「ref check 這個 .bib」 | 只想確認引文存在或要找新文獻 → `nature-academic-search` |
| `nature-downloader` | 合法管道下載全文：OA、出版社 API、知網與機構瀏覽器授權，含 SI | 「下載這幾篇 DOI 的 PDF」「從知網下載這篇」 | 還沒決定讀哪幾篇 → `nature-academic-search` |
| `/nature-literature-pipeline` | 設定每日定時文獻推送：檢索 → 六維評分 → 精讀 → 推送飛書/Telegram → 歸檔 | `/nature-literature-pipeline` 研究方向 X，每天 08:30 推送 | 一次性檢索 → `nature-academic-search` |

### 讀文獻

| Skill | 用途 | 典型說法 | 邊界：這些情況改用 |
|---|---|---|---|
| `nature-reader` | 已發表論文的中英對照 Markdown 閱讀版（含圖表、公式、source map），或針對論文的帶出處問答、片段翻譯 | 「把這篇做成中英對照」「這篇的 Fig. 3 在說什麼」 | 要結構化分析卡 → `nature-paper-card`；要保留原版面的中文 PDF → `/nature-paper-trans`；翻譯自己的中文稿成英文 → `nature-polishing` |
| `nature-paper-card` | 單篇論文 16 節固定格式精讀卡：方法、主張—證據鏈、局限、研究點子 | 「幫這篇做精讀卡」「拆解這篇的方法和證據鏈」 | 全文翻譯 → `nature-reader`；評自己的稿子 → `nature-reviewer`；做簡報 → `nature-paper2ppt` |
| `/nature-paper-trans` | 英文論文 PDF 逐頁生成保留版式的簡體中文圖片型 PDF | `/nature-paper-trans` 翻譯 paper.pdf 第 1–5 頁 | 需要可搜尋、可複製的譯文 → `nature-reader`。**需要內建 `image_gen` 生圖工具（Codex 類環境）；Claude Code 目前沒有，所以在這裡通常無法執行** |
| `nature-paper2ppt` | 從論文或閱讀筆記做中文學術 PPTX（含原圖與講稿），或修改既有簡報 | 「把這篇論文做成組會 PPT」「做一份答辯用的文獻匯報」 | 把截圖／圖片型投影片還原成可編輯 PPT → `nature-image2ppt` |
| `nature-image2ppt` | 把投影片圖片、截圖、掃描 PDF 或純圖片 PPTX 重建為物件層級可編輯 PowerPoint | 「這幾張截圖轉成可編輯 PPT」 | 從論文新做簡報 → `nature-paper2ppt` |

### 寫作與投稿

| Skill | 用途 | 典型說法 | 邊界：這些情況改用 |
|---|---|---|---|
| `nature-writing` | 依作者提供的證據起草章節、重構論證、調整正文與 SI 的分配、首次投稿材料（cover letter、title page、各類聲明） | 「幫我寫 Introduction」「Results 太散，重新組織」「準備首次投稿的 cover letter」 | 只改語言不動內容 → `nature-polishing`；收到審稿意見後的一切 → `nature-response`；開題報告／計畫書 → `researchwrite` |
| `nature-polishing` | 潤色既有文字（事實與主張不變）：句子精簡、自己中文稿的中譯英、跨段一致性檢查、LaTeX 浮動體與版面 | 「潤色這段 Abstract」「把這段中文翻成學術英文」「這頁圖排不好」 | 要新增或重組內容 → `nature-writing`；讀別人論文的中文翻譯 → `nature-reader` |
| `nature-reviewer` | 模擬審稿：三份互相獨立的審稿報告 + 綜合，評估重要性、有效性與 major/minor 問題 | 「投稿前幫我模擬審稿」「以審稿人角度挑這篇的毛病」 | 回覆真實審稿意見 → `nature-response`；只看統計 → `nature-statistics` |
| `nature-statistics` | 統計報告審查：實驗單位、n 與重複、檢定、不確定性、圖注統計；起草統計方法小節 | 「檢查這段的統計寫法」「寫 Statistical analysis 小節」 | 整體審稿 → `nature-reviewer`；畫圖 → `nature-figure` |
| `nature-figure` | 用 Python 或 R 畫、改、審、匯出投稿用多面板科研圖；明確要求時用 AI 生圖做圖形摘要／機制示意圖 | 「畫一張三面板的 Fig. 2」「檢查這張圖能不能投稿」 | 圖注裡的統計敘述 → `nature-statistics` |
| `nature-data` | 撰寫或審查 Data/Code Availability 聲明、資料倉儲與存取路徑、FAIR metadata、資料集引用 | 「寫 Data availability」「我的資料該放哪個 repository」 | 資料清理或分析 → 一般對話或 `nature-statistics` |
| `nature-experiment-log` | 把照片、語音、文字整理成帶 YAML frontmatter、實驗 ID 與附件歸檔的標準 Markdown 實驗日誌 | 「把今天的實驗照片和筆記整理成日誌」 | — |

### 返修

| Skill | 用途 | 典型說法 | 邊界：這些情況改用 |
|---|---|---|---|
| `nature-response` | 收到期刊決定後：逐點回覆審稿意見、返修 cover letter、修訂標記稿、LaTeX 回覆模板 | 「幫我回覆這份審稿意見」「寫返修信」 | 首次投稿材料 → `nature-writing`；模擬審稿 → `nature-reviewer`；修改稿中的統計問題可搭配 `nature-statistics` |

### 旁支

| Skill | 用途 | 典型說法 | 邊界：這些情況改用 |
|---|---|---|---|
| `nature-paper-to-patent` | 從論文或發明人材料寫中國發明專利：權利要求書／說明書 DOCX、技術交底書、論文—專利比對 | 「把這篇論文寫成技術交底書」 | 一般論文寫作 → `nature-writing` |
| `nature-shared` | 共用參考檔（期刊格式、正文紀律、Discussion 語言等），由其他 nature skill 依路徑讀取 | 不直接使用 | — |

## 三、最容易混淆的幾組

- **找文獻 vs 核對文獻**：要「找到」文獻用 `academic-search`（任何期刊）或 `citation`（只要 Nature/CNS）；要「修正」參考文獻清單的欄位錯誤用 `ref-verifier`。
- **寫 vs 潤 vs 回 vs 審**：內容要變 → `writing`；只改語言 → `polishing`；回覆真實審稿人 → `response`；模擬審稿人挑毛病 → `reviewer`。
- **翻譯**：讀別人的英文論文 → `reader`（Markdown 對照）或 `/paper-trans`（版式 PDF）；把自己的中文稿譯成英文 → `polishing`。
- **讀一篇論文**：要逐句看懂 → `reader`；要分析它的方法與證據 → `paper-card`；要拿去組會報告 → `paper2ppt`。
- **PPT**：從論文內容做 → `paper2ppt`；從現成圖片還原 → `image2ppt`。

## 四、未驗證事項

- 改寫後的 description 是否真的讓模型在實際提示下選對 skill，沒有用真實提示測試過。
- `nature-shared` 改為手動後，其他 skill 依相對路徑讀取它的檔案應不受影響（它們不是透過 Skill 工具呼叫它），但未實際跑一次 writing/polishing 確認。
- `/nature-paper-trans` 依賴的 `image_gen`、`view_image` 工具在 Claude Code 是否可用，未實測。
