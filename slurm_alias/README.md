# Slurm Aliases (`q`, `qs`, `pbs`)

本工具包收集了在 Slurm HPC 叢集環境中最實用的三個別名快捷指令（`q`, `qs`, `pbs`），以及模擬 PBS/Torque 節點資源監控面板的 Python 腳本（`check_slurm_node_usage.py`）。

適合從 PBS/Torque 轉移至 Slurm 習慣這些指令的使用者，或是希望獲得更直觀的節點 GPU/CPU/記憶體分配總覽的研究者。

---

## 快速預覽：這三個指令是什麼？

| 指令 | 對應指令 / 腳本 | 功能說明 |
|---|---|---|
| `q` | `squeue -u $USER` | 快速查詢**自己帳號**當前所有排隊中 (PENDING) 與執行中 (RUNNING) 的 jobs |
| `qs` | `squeue` | 查詢**整個叢集**所有使用者目前所有排程與執行狀態 |
| `pbs` | `check_slurm_node_usage.py` | 顯示如同 PBS/Torque 風格的**全節點 GPU / CPU / 記憶體即時資源狀態總覽**與執行中的 Job 列表 |

---

## `pbs` 指令特色

Slurm 原生的 `sinfo` 與 `squeue` 缺乏單一清晰視圖來快速看出**哪顆 GPU 是空的、哪台節點還有 CPU/顯存**。

`pbs` 腳本透過 `scontrol show node` 與 `scontrol show job` 彙整資料，呈現：
1. **GPU 虛擬子節點劃分**：GPU 節點會自動依 GPU 編號拆分為 subnode，如 `node-181[0](l40s)`、`node-171[2](rtx3080)`。
2. **直觀狀態標註**：
   - `free`：有空閒資源可供調度。
   - `job-exclusive`：GPU 已被 job 佔用。
   - `job-busy`：CPU 或節點資源已被滿載。
   - `offline`：節點處於 DOWN / DRAIN / FAIL 狀態。
3. **容量統計 (Free/Total)**：
   - `mem f/t`：顯存或記憶體（可用 / 總量）
   - `ncpus f/t`：CPU 核心數（可用 / 總量）
   - `ngpus f/t`：GPU 數量（可用 / 總量，例如 `1/1` 代表空閒，`0/1` 代表已被佔用）
4. **當前執行資訊**：節點右側直接列出正在執行的 `JobID:JobName(User)`。
5. **詳細 Job 表格**：下方附上所有執行中 job 的節點、Job ID、使用者、狀態、CPUs、GRES 要求與 Job 名稱。
6. **支援 Partition 篩選**：直接代入參數即可篩選特定分區，例如 `pbs gpu` 或 `pbs l40s`。

---

## 如何搬移到另一台電腦／叢集使用？

請在另一台電腦上選擇以下任一種方式安裝：

### 方法一：Git Clone 完整倉庫（最推薦，方便日後同步更新）

在目標電腦終端機執行：

```bash
# 1. Clone 本倉庫至家目錄
git clone https://github.com/luketou/skill.git ~/skill
# （若有 SSH Key，亦可使用：git clone git@github.com:luketou/skill.git ~/skill）

# 2. 執行一鍵設定腳本（會自動將引用路徑加入 ~/.bashrc）
cd ~/skill/slurm_alias
bash install.sh

# 3. 立即生效
source ~/.bashrc
```

> **提示**：如果想手動設定，只需在 `~/.bashrc` 最後加入這行即可：
> ```bash
> [ -f "$HOME/skill/slurm_alias/slurm_aliases.sh" ] && source "$HOME/skill/slurm_alias/slurm_aliases.sh"
> ```

---

### 方法二：僅複製 `slurm_alias` 資料夾（輕量獨立模式）

若另一台電腦不想下載整個 `skill` 倉庫，只複製 `slurm_alias` 資料夾即可：

1. **從原電腦複製到目標電腦**：
   ```bash
   scp -r slurm_alias user@target-cluster:~/.slurm_alias
   ```

2. **在目標電腦啟用別名**：
   在目標電腦的 `~/.bashrc` 加入：
   ```bash
   [ -f "$HOME/.slurm_alias/slurm_aliases.sh" ] && source "$HOME/.slurm_alias/slurm_aliases.sh"
   ```
   接著執行 `source ~/.bashrc` 即可！

---

### 方法三：手動貼入 `~/.bashrc`（純手動最速設定）

如果你已將 `check_slurm_node_usage.py` 放至目標電腦的某個路徑（例如 `~/bin/check_slurm_node_usage.py`）：

在目標電腦的 `~/.bashrc` 加入：
```bash
# Slurm Aliases
alias q="squeue -u $USER"
alias qs="squeue"
alias pbs="python3 ~/bin/check_slurm_node_usage.py"
```
然後執行 `source ~/.bashrc`。

---

## 使用範例

### 1. 查詢自己的排程
```bash
q
```
*相當於 `squeue -u $USER`，快速掌握自己送出的 job 是否已經開始跑，或還在排隊。*

### 2. 查詢整個叢集的排程
```bash
qs
```
*相當於 `squeue`，查看整個叢集目前的 job 負載與排隊狀況。*

### 3. 查看叢集節點資源總覽
```bash
pbs
```

輸出範例：
```text
                                                                       mem   ncpus   nmics   ngpus 
vnode                     state            njobs   run   susp          f/t     f/t     f/t     f/t jobs
------------------------- --------------- ------ ----- ------ ------------ ------- ------- ------- -------
node-11(cpu-2g)           free                 2     2      0  431gb/500gb   12/44     0/0     0/0 54429:c300(userA),54430:c350(userA)
node-17(cpu-3g)           free                 4     4      0  163gb/250gb   32/36     0/0     0/0 54376:PCMOBO(userB)
node-181[0](l40s)         free                 0     0      0    48gb/48gb     8/8     0/0     1/1 --
node-181[1](l40s)         free                 0     0      0    48gb/48gb     8/8     0/0     1/1 --
node-191[0](rtx3080)      job-exclusive        1     1      0    10gb/10gb     0/2     0/0     0/1 54458:model_test(userC)
node-191[1](rtx3080)      job-exclusive        1     1      0    10gb/10gb     0/2     0/0     0/1 54459:train(userC)
node-191[2](rtx3080)      free                 0     0      0    10gb/10gb     2/2     0/0     1/1 --
node-201[0](l40s)         free                 0     0      0    48gb/48gb     8/8     0/0     1/1 --
node-201[1](l40s)         job-exclusive        1     1      0    48gb/48gb     1/8     0/0     0/1 54441:eval_dinov2(userD)
node-205[0](v100-32g)     offline              0     0      0    32gb/32gb     0/4     0/0     0/1 --

node         jobid      user         state      cpus  gres            name
node-11      54429      userA        RUNNING    16    N/A             c300
node-191     54458      userC        RUNNING    2     gres:gpu:rtx3080:1 model_test
node-201     54441      userD        RUNNING    7     gres:gpu:l40s:1 eval_dinov2
```

### 4. 依 Partition（分區）篩選節點
若叢集分區較多，可以加上分區名稱過濾：
```bash
# 只看 GPU 相關分區
pbs gpu

# 只看 l40s 分區
pbs l40s

# 只看 cpu 分區
pbs cpu
```

### 5. 即時動態監看（配合 watch 指令）
想要像 `htop` 一樣每 10 秒刷新一次節點資源狀態：
```bash
watch -n 10 -c "pbs l40s"
```

---

## 檔案結構說明

```text
slurm_alias/
├── check_slurm_node_usage.py   # 主要核心 Python 腳本（解析 scontrol 輸出並美化排版）
├── check_slurm_node_usage.sh   # Bash 封裝包裝器（自動導向至 check_slurm_node_usage.py）
├── slurm_aliases.sh            # 別名定義腳本（定義 q, qs, pbs，自動解析所在目錄）
├── install.sh                  # 一鍵安裝腳本（將 source 語法寫入 ~/.bashrc）
├── SKILL.md                    # Agent Skill 說明文件
└── README.md                   # 使用說明與部署手冊（本文件）
```

---

## 系統需求與環境

1. **Python 3**：
   - 本腳本僅使用 Python 3 標準函式庫（`subprocess`, `re`, `sys`），**不需要**安裝任何額外第三方套件（如 pandas、numpy、tabulate 等都不需要）。
2. **Slurm 客戶端工具**：
   - 系統需要有 `squeue` 與 `scontrol` 命令（一般 HPC 登入節點皆已內建）。
3. **Shell**：
   - `slurm_aliases.sh` 支援 Bash 與 Zsh。

---

## 常見問題 (FAQ)

### Q: 另一台電腦的 GPU 型號不同（例如是 A100、H100、RTX 4090），顯存大小顯示正確嗎？
A: 腳本內建了常見 GPU 型號映射表（包含 H100、H200、A100、A800、L40S、RTX 4090、RTX 3090、V100、T4 等）。若遇到自訂或新型號顯卡，可直接在 `check_slurm_node_usage.py` 開頭的 `GPU_MEM_MAP` 字典中新增型號與顯存大小。

### Q: 執行 `pbs` 時出現 `Permission denied`？
A: 請確保 Python 腳本具備執行權限：
```bash
chmod +x check_slurm_node_usage.py check_slurm_node_usage.sh install.sh
```

### Q: 如果登入節點預設沒有載入 Python 模組？
A: 在某些 HPC 叢集上，需先載入模組（例如 `module load python` 或系統提供的 Python 模組）。只要終端機中 `python3` 可用即可執行。
