# m5 主機與路徑參考（2026-11-06 實測）

## 主機

| 主機 | 連線 | GPU | 用途 |
| :--- | :--- | :--- | :--- |
| `m5813`（跳板） | 本機 `ssh m5813`（jeff@140.112.13.54:6666） | RTX 2060 SUPER 8 GB | 前處理、小測試 |
| `m5-cluster1` | 在 m5813 內 `ssh m5-cluster1` | RTX 4090 24 GB | 訓練、生成 |
| `m5-cluster2` | 在 m5813 內 `ssh m5-cluster2` | RTX 4090 24 GB | 訓練、生成 |

## 路徑

- 主存放：m5813 的 `/mnt/hdd2/tou`（code、checkpoint；節點沒有 `/mnt/hdd2`）。
- 節點執行副本：`/mnt/hdd/jeff/tou/<專案>`；暫存 `/mnt/hdd/jeff/tou/tmp`。
- cache：`HF_HOME=/mnt/hdd/jeff/.cache/huggingface`、`TORCH_HOME=/mnt/hdd/jeff/.cache/torch`。
- 空間（實測時）：cluster1 `/mnt/hdd` 剩 362G、cluster2 剩 431G；m5813 `/mnt/hdd` 剩 136G（85%）、`/mnt/hdd2` 剩 2.0T。大型 checkpoint／軌跡定期移到 NAS。以 `df -h` 重新確認，數字會變。

## Conda

env 在節點 `/home/jeff/.conda/envs/`（`mdgen`、`mdgen2026`、`mdgen2026-r2-a6-cu126` 等），base 在 `/opt/miniconda3`。`mdgen` 為 torch 2.0.1+cu118，兩台皆 `torch.cuda.is_available() == True`。

## 傳檔（在 m5813 上執行，已設免密碼）

```bash
# 送 code
rsync -avP /mnt/hdd2/tou/<專案>/ m5-cluster1:/mnt/hdd/jeff/tou/<專案>/
# 取回 checkpoint
rsync -avP m5-cluster1:/mnt/hdd/jeff/tou/<專案>/checkpoints/ /mnt/hdd2/tou/<專案>/checkpoints/
```

## 已踩過的坑

- Windows → m5813 → 節點：`ssh` 不加 `-n`、或以 stdin 灌腳本（`Get-Content | ssh ... bash -s`）會卡住無輸出。做法：`scp` 腳本到 m5813，再 `ssh -n m5813 "bash /tmp/<腳本>"`；腳本內跳節點的 `ssh` 加 `</dev/null`。
- 遠端指令含引號或括號時 PowerShell 會先解析報錯；一律寫成 LF 腳本檔再傳。
