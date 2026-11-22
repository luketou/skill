#!/bin/bash
#SBATCH --job-name=smoke-cpu
#SBATCH --partition=cpu-2g
#SBATCH --account=users
#SBATCH --cpus-per-task=1
#SBATCH --mem=1G
#SBATCH --time=00:05:00
# 流程 smoke：不需 GPU、不載入專案環境。驗證快照、提交、log 與 fetch。
# 複製到專案 job/ 後用 hpc_run.py submit --tag smoke job/smoke_cpu.sh 提交。
set -eo pipefail
echo "host: $(hostname)  job: $SLURM_JOB_ID  partition: $SLURM_JOB_PARTITION"
echo "snapshot: $PWD"
ls -d src results logs 2>/dev/null || true
echo "run dir: ${MDGEN_RUN_DIR:-unset}"
mkdir -p "${MDGEN_RUN_DIR:-.}/results"
echo ok > "${MDGEN_RUN_DIR:-.}/results/smoke.txt"
echo SMOKE_OK
