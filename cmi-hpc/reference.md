# CMI HPC 參考（連線、硬體、選節點、提交）

資料擷取於 2026-11-22（`sinfo`／`scontrol show node`／`lscpu`／`nvidia-smi`）。節點數量與狀態會變，動手前用 `sinfo -o '%P %a %D %N %G %c %m'` 重查。

## 1. 連線

- Headnode：`r15543056@zinfandel.ncree.org`（主機名 `bug`）。金鑰登入，只做傳輸、提交、查詢；訓練、GPU 測試、大量處理一律送 Compute Node。
- **從 Windows 一律經 WSL**：Windows 的 `ssh` 會無輸出逾時（exit 255）。預設 distro 是 `docker-desktop`（沒有 bash），必須指定 `-d Ubuntu`。
- `~/.ssh/config` 對 `zinfandel.ncree.org` 有重複 Host 且使用者不同，命令列明寫 `r15543056@`。
- 遠端指令含引號或 `$` 時寫成 LF 腳本檔再送，不內嵌在 `bash -c "..."`：

```bash
wsl -d Ubuntu -e bash -c "ssh -o BatchMode=yes -o ConnectTimeout=10 r15543056@zinfandel.ncree.org 'bash -s' < /mnt/c/path/to/query.sh"
```

- 加 `BatchMode=yes`、`ConnectTimeout=10`，避免卡在密碼提示；單次查詢設總逾時，不做緊迴圈輪詢。
- 家目錄 `/share/home/r15543056`（NFS，所有節點可見）。`/share/home` 共 360 GB 與其他使用者共用，2026-11-22 剩 31 GB（92%）；大輸出先估算再送。
- `sacct`／`sacctmgr` 的資料庫連不上；查 job 用 `squeue -j <id>`（結束後回 `Invalid job id`），再讀 `logs/*.out`／`.err`。
- Headnode 可 ssh 到部分節點做唯讀檢查（`lscpu`、`nvidia-smi`），不在上面跑工作；部分節點會拒絕（permission denied／host key 未知）。

## 2. 節點與硬體

| 分區 | 節點 | 每節點資源 | 時間上限 | 帳號 |
|---|---|---|---|---|
| `l40s`（預設） | node-201 | 2× NVIDIA L40S 46 GB、16 vCPU（Xeon GraniteRapids）、62 GB RAM | 7 天 | 只收 `l40s`，腳本已寫 `--account=l40s` |
| `llm` | node-181 | 同 node-201 | 7 天 | 只收 `llm`；本帳號的 job 永遠 pending（`Job's account not permitted`），`sbatch --test-only` 不會發現 |
| `v100-32g` | node-202～204 可用（205～208 DOWN） | 1× V100 32 GB、4 vCPU、29 GB RAM | 7 天 | 全部 |
| `rtx3080` | node-171 | 3× RTX 3080 10 GB、6 vCPU（AMD EPYC-Milan）、46 GB RAM | 7 天 | 全部 |
| `ccchou` | node-191 | 同 node-171 | 7 天 | 標示全部，但疑似特定實驗室專用，先確認再用 |
| `rtx2080ti` | node-141、143、144、162 | 1× RTX 2080 Ti 11 GB、2 vCPU、15 GB RAM | 7 天 | 全部 |
| `cpu-2g` | node-11～13（44 核 / 500 GB）、node-14（96 核 / 500 GB，Xeon E7-8890 v4）、node-19（80 核 / 124 GB） | 純 CPU | 28 天 | 全部 |
| `cpu-3g` | node-17、18 | 36 核（Xeon Gold 6354）、250 GB RAM | 28 天 | 全部 |

要點：

- L40S 只有 **2 張**，且與其他使用者共用，常有一張被佔；自己同時最多用 2 張，並盡量讓兩張都有 job。
- 其他 GPU 節點的 CPU 與 RAM 很少（2～6 核、15～47 GB），`num_workers` 與資料載入要照節點調低。
- 排程器 `priority/basic`（先送先跑）搭配 backfill；沒有 fairshare。

## 3. 哪些任務用哪些節點

| 任務 | 分區 | 資源建議 |
|---|---|---|
| 大模型訓練／微調、長序列、MDgen 全長蛋白、LLM LoRA／DoRA 與評估 | `l40s` | 單 job 單 GPU；`-c 8 --mem 30G`，讓兩張卡各跑一個 |
| 中型訓練、要 32 GB 顯存但不需 L40S 速度 | `v100-32g` | 1 GPU、≤4 核、≤28 GB RAM；V100 無原生 bf16，先用 fp16／fp32 smoke 驗證 |
| 小模型、除錯、單元測試、GPU smoke | `rtx3080`（10 GB） | 10 GB 是硬上限，放不下就換節點，不縮小到失去代表性 |
| 極小 GPU 測試、環境驗證 | `rtx2080ti`（11 GB） | 只有 2 核 15 GB RAM |
| 前處理、特徵萃取、DARTS／LightGBM 等 CPU 基線、評估統計、下載資料 | `cpu-2g`／`cpu-3g` | 高記憶體或多核用 node-11～14；`cpu-3g` 常被大量 job 佔滿 |

選擇順序：顯存需求 → CPU／RAM 瓶頸 → 佇列（`squeue -h -o '%P %T' | sort | uniq -c`）。smoke 通過的分區就是正式提交的分區；換分區要重做 smoke。

## 4. 提交 job

### 4.1 標準路徑：`scripts/hpc_run.py`（有此腳本的專案）

由 repo 根目錄執行；工具建立唯讀快照、核對 SHA-256、把 `src/results`、`src/logs` 連到 run 目錄、提交並記到 `<run>/job_history` 與本機 `hpc_job_history`。

```bash
python scripts/hpc_run.py submit --tag smoke job/<launcher>.sh <args>        # 新快照 + smoke
python scripts/hpc_run.py submit --run <run_id> job/<launcher>.sh <args>     # 沿用同一快照正式送
python scripts/hpc_run.py status <run_id>
python scripts/hpc_run.py tail <run_id> logs/<job>.out
python scripts/hpc_run.py fetch <run_id> <本機目錄> results/x.json logs/<job>.out   # 單次上限 20 MiB
python scripts/hpc_run.py history
```

- 覆寫分區：`--sbatch=--partition=v100-32g --sbatch=--account=users`（命令列優先於腳本內的 `#SBATCH`）。
- 傳環境變數：`--env KEY=VALUE`；指定節點：`--sbatch=--nodelist=node-201`。
- 24 小時內相同 launcher 與參數會 exit 3 停止；先 `status`／`history` 確認，真的要重送才加 `--force`（只換分區也算相同，要加）。
- 快照只帶 tracked 檔，加 `job/`、`scripts/`、`mdgen/`、`hpc/` 底下的 untracked 檔；新測試先 commit。
- 在 WSL 建的 worktree，Windows git 讀不到；`hpc_run.py` 會自動處理，其他工具（`gh pr create` 等）要先設 `GIT_DIR`／`GIT_WORK_TREE`。

### 4.2 沒有提交工具的專案：手動 `sbatch`

快照放共享儲存（`/share/home/r15543056/<專案>/hpc_runs/<run_id>`），程式、輸出、log 分開；腳本內用絕對 Python 路徑並 `module load`（預設 `python/3.11.12-gpu cuda/12.8`）。

```bash
sbatch -p l40s -A l40s --gres=gpu:1 -c 8 --mem=30G -t 12:00:00 \
       -J <名稱> -o logs/%j.out -e logs/%j.err job/<launcher>.sh
# 其他分區：-p v100-32g -A users --gres=gpu:1 -c 4 --mem=28G
# CPU：     -p cpu-2g   -A users -c 32 --mem=120G -t 1-00:00:00
```

回覆沒有有效 Job ID 時視為 `submission_unknown`，先查 `squeue -u $USER` 再決定是否重送。

### 4.3 優先序與排隊

- 一次送大量 job：加 `--nice=10000`（`hpc_run.py` 用 `--sbatch=--nice=10000`），讓其他工作先跑；需要優先的少量 job 用 nice 0。只能調高 nice；`scontrol update Priority=` 不持久。
- 要讓已送出的 job 排在另一批之後：`scontrol update JobId=<id> Dependency=afterany:<id1>:<id2>…`。事後調高 nice 無效。
- 取消：`scancel <id>`；有逾時風險的趁還在排隊取消重送。

### 4.4 `job/env.sh` 與 GPU 健康

- 載入 modules 與 venv 後會跑 GPU preflight（2×2 CUDA matmul），失敗就停。`.out` 開頭 `nvidia-smi` 印出 `No devices were found` 是沒拿到 GPU，不是 OOM，不可當量測結果。
- `node-201` 單 GPU job 若分到第二張卡，Slurm 會把 `CUDA_VISIBLE_DEVICES` 設成 1，但 job 內只看得到 device 0（`CUDA_ERROR_NO_DEVICE`）；`env.sh` 在 `GPU_DEVICE_ORDINAL` 有值時改用它，自寫腳本要照做。
- 清掉繼承的 `SSH_CLIENT`，否則 `module load` 會載入 `~/.bashrc` 而在 compute node 失敗。
- DeepSpeed 匯入會找 CUDA 工具鏈，需 `CUDA_HOME` 指向 CUDA 12.8 module 路徑。

## 5. 常用查詢

```bash
squeue -u $USER                         # 自己的 job（alias: q）
squeue -j <id> -o '%i %P %T %R'         # 狀態與 pending 原因
sinfo -o '%P %a %D %N %G %c %m'         # 分區與節點資源
scontrol show node <node> | grep -E 'CPUAlloc|AllocMem|Gres|State'
df -h /share/home/r15543056
```

`pbs` 指令（見 `../slurm_alias`）可一次看到每張 GPU 是否空閒。pending 原因 `Priority`／`Resources` 正常；`Job's account not permitted` 代表分區帳號不符，取消後改送其他分區或 `-p l40s -A l40s`。
