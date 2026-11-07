---
name: m5-hpc
description: 在 m5 主機群（m5813 跳板、m5-cluster1/2 RTX 4090，無 Slurm、用 tmux）上部署程式、smoke test、跑 GPU 訓練或生成、恢復 checkpoint、取回結果與清理。需要 L40S 48 GB 或大量分片時改用 cmi-hpc（Slurm）。
---

# m5 GPU 工作流程

主機、路徑、conda、rsync 指令與踩過的坑見 [reference.md](reference.md)；動手前先對照。m5 沒有 Slurm／PBS，一切靠 SSH + tmux。

## 共用規則（任何步驟都適用）

- 帳號與實驗室共用：啟動前 `nvidia-smi` 確認無人佔用；預計佔用 4090 超過 24 小時先在群組報備；DataLoader `num_workers` ≤ 16。
- 只操作本任務建立的目錄與檔案；清理、覆寫既有 run／checkpoint／結果須使用者明確同意。
- SSH／傳輸用有限逾時；SSH 斷線不等於任務失敗，先查 tmux 與 log。
- 從 Windows 操作時遵守 reference.md 的 ssh `-n` 與 LF 腳本規則。

## 步驟

1. **接手與確認目標**：讀目標 repo 的 `AGENTS.md`、確認 worktree、分支與 dirty diff；`ssh -n m5813` 查 `tmux ls`（cluster 節點同）找出先前 run。
   完成：知道哪些 run 還在跑、各自對應哪份程式。

2. **選機器**：預設 `m5-cluster1`／`m5-cluster2` 的 4090；前處理與小測試用 m5813。`nvidia-smi` 與 `df -h /mnt/hdd` 都夠才開跑。
   完成：機器、GPU 編號（`CUDA_VISIBLE_DEVICES=0`）、空間已確認。

3. **本機檢查與快照**：先跑本次修改適用的本地檢查。程式從 tracked 檔（加必要且明列的 untracked 檔）排除產物與大檔後，`rsync` 到 m5813 `/mnt/hdd2/tou/<專案>`，再 rsync 到節點 `/mnt/hdd/jeff/tou/<專案>`；不使用 `--delete`。用唯一 run ID，記錄 commit、dirty 狀態與 SHA-256 manifest，傳完核對遠端雜湊。logs、cache、results、checkpoint 用獨立路徑，不寫進快照目錄。
   完成：節點副本與本機一致，所需資料在節點可讀。

4. **Smoke**：用正式入口與環境、最小資料／step／時間，在節點的具名 tmux（`tmux new -s jeff_<任務>`）跑，輸出導到 log。依變更驗證資料讀取、模型載入、forward/backward/optimizer 與最小輸出；涉及 checkpoint 時驗證寫入、重載與繼續一步。
   完成：process 正常結束、確實用到 GPU、產物通過驗證；記下單步時間與顯存峰值。小資料通過不證明正式規模的記憶體與效能。

5. **正式啟動**：沿用通過 smoke 的同一份快照；程式有變更就重新快照並重做 smoke。tmux 名稱、run ID、啟動時間、參數、資料／模型／env 識別與來源 checkpoint 先存檔再啟動。
   完成：`tmux ls` 與 `nvidia-smi` 看得到任務，log 持續前進。

6. **監看**：只讀指定 log 的有限尾端（`tail -n`），按需查詢不要緊迴圈輪詢。區分 OOM、GPU 被佔用、程式錯誤、被他人終止；保留 log 與錯誤摘要。
   完成：知道狀態與原因；有風險（顯存或空間逼近上限）時趁早處理。

7. **Checkpoint 與恢復**：區分推論權重與完整恢復狀態（模型、optimizer、scheduler、step、隨機狀態）。只恢復已完整寫出的 checkpoint；恢復建立新 run，指定確切來源 checkpoint 並記錄父 run，確認 max steps 是總步數還是額外步數。
   完成：成功繼續一步且進度正確，不是只載入模型。

8. **取回與清理**：`rsync -avP` 把產物與 checkpoint 取回 m5813 `/mnt/hdd2/tou`，確認檔案數與大小／雜湊後，才在使用者授權下清掉節點副本與暫存（`/mnt/hdd/jeff/tou/tmp`）。大型檔留遠端，只取需要的；長期保留的移 NAS（共享儲存不代表有備份）。
   完成：結果已在 `/mnt/hdd2/tou`，節點只剩本任務允許保留的內容。

## 回報

回報 run ID、機器、tmux 名稱、快照與結果路徑、實際狀態、已通過與未執行的驗證。只有程序終止狀態與產物檢查都符合，才宣告通過。
