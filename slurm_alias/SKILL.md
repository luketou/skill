---
name: slurm-alias
description: Slurm 叢集作業與節點資源狀態查詢快捷指令（q, qs, pbs）及節點資源監看工具。當需要查詢使用者排程、全叢集佇列或各節點 GPU/CPU/記憶體分配情況時使用。
---

# Slurm Aliases & Node Monitor

提供 Slurm HPC 叢集的日常別名快捷指令與 PBS 風格的節點詳細資源狀態監控工具。

## 提供的指令

1. **`q`** (`squeue -u $USER`)：查看當前使用者的排隊 (PENDING) 與執行中 (RUNNING) jobs。
2. **`qs`** (`squeue`)：查看整個叢集所有使用者的 jobs 狀態。
3. **`pbs`** (`check_slurm_node_usage.py`)：以 Torque/PBS 表格風格呈現各節點狀態、GPU/CPU 核心分配、記憶體剩餘量與當前運行中的 jobs。

## 使用方式

- 查詢自己的工作：`q`
- 查詢全域隊列：`qs`
- 查詢全節點 GPU / CPU / 記憶體使用率：`pbs`
- 依分區篩選節點：`pbs <partition_name>`（例如 `pbs gpu`、`pbs l40s`、`pbs cpu`）

詳細安裝與跨主機配置方式請參閱 [README.md](README.md)。
