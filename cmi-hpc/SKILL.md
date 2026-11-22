---
name: cmi-hpc
description: CMI Slurm HPC 的 job 工作流程：選分區與節點、部署程式快照、smoke test、大量提交、查佇列與失敗原因、取回結果並留下驗證紀錄。連線方式、硬體清單與提交指令見 reference.md。
---

# CMI HPC 工作流程

連線（經 WSL）、節點硬體、任務選節點與 `sbatch`／`hpc_run.py` 指令都在 [reference.md](reference.md)，動手前先對照。`$HPC_RUN` 指本 skill 的 `scripts/hpc_run.py`，預設 `~/.agents/skills/cmi-hpc/scripts/hpc_run.py`，在專案 repo 根目錄執行（設定見 reference.md §4.1）。專案內若有 `hpc/project.yaml` 與 `job/README.md`，其資源設定為候選值。MDgen 的 GPU 工作優先用 [m5-hpc](../m5-hpc/SKILL.md)（RTX 4090，無 Slurm）；需要 L40S、V100、CPU 節點或大量分片才用本 skill。

## 步驟

1. **接手**：`python $HPC_RUN history`（或查 `<run>/job_history`）找出先前的 run ID 與 Job ID，確認 worktree、分支、dirty diff。
   完成：知道哪些 job 在跑、已結束、各對應哪個快照。

2. **選分區**：依 reference.md §3 的顯存、CPU／RAM 需求選分區，並查佇列與 `df -h /share/home/r15543056`。
   完成：分區、GPU 數、`-c`／`--mem`、時間上限已決定。

3. **本機檢查**：跑專案的本地檢查（如 WSL `bash scripts/check.sh`）；新測試先 commit。
   完成：exit 0。

4. **Smoke**：
   - 只想確認流程能送（沒有要驗證模型）：把 `scripts/smoke_cpu.sh` 複製到專案 `job/`，`python $HPC_RUN submit --tag smoke job/smoke_cpu.sh`，CPU 分區，通常數秒內啟動。
   - 要驗證正式工作：用正式 launcher 與入口、最小輸入、**同一分區**送一個 job；smoke 不加 `--nice`。
   完成：job 離開佇列；（GPU job）`.out` 開頭有拿到 GPU；CPU smoke 的 log 末行是 `SMOKE_OK`；產物狀態成功；量到單 case 時間、顯存峰值與輸出大小。只拿到 Job ID 不算完成。

5. **估算**：單 case 時間與輸出大小 × 矩陣規模，對照剩餘空間、時間上限、可用 GPU 數。
   完成：放得下、不逼近時間上限；放不下先與使用者確認。

6. **正式提交**：沿用 smoke 的快照（`--run <run_id>`）；程式有變就新快照並重做 smoke。只有一次送大量 job 才加 `--nice=10000`，單一或少量 job 用 nice 0。逐筆記錄分片 → Job ID；任何一筆失敗或結果不明就停，先查 `history` 與 `squeue`，從中斷處續送。
   完成：預期數量都有 Job ID，pending 原因是 `Priority` 或 `Resources`。

7. **監看**：`python $HPC_RUN status <run_id>` 查狀態；排隊（`Priority`／`Resources`）是正常的，不要迴圈等待，隔一段時間查一次，GPU 分區可能要等數十分鐘以上。遠端查詢寫成腳本檔經 WSL 執行；結束的 job 先讀 `.out`／`.err`（逾時為 `DUE TO TIME LIMIT`）；最長設定第一批跑完就核對時間。
   完成：知道完成數、失敗數與原因；有逾時風險趁排隊取消重送。

8. **取回與紀錄**：只 `fetch` 小型 JSON 與 log，大型張量留在 server。README 引用的每個 server 數字（空間、大小、雜湊、佇列狀態）連同指令與原始輸出存成同目錄 log。
   完成：每個數字都找得到出處，專案檢查通過。

## 失敗與授權

OOM、沒拿到 GPU、逾時、程式錯誤與 `submission_unknown` 分開記錄並保留 log；沒拿到 GPU 不是 OOM。同一快照重送時，在 run 的 `job_history` 補記先前失敗或取消的 job 與原因。

恢復訓練建立新 run，指定確切來源 checkpoint 並記錄父 run；完成標準是成功繼續一步。

資源設定是候選值，不是授權；清理或覆寫既有 run、checkpoint、結果，以及超出使用者已授權範圍的資源，都先取得明確同意。
