#!/usr/bin/env bash
# ==============================================================================
# Slurm Aliases for HPC Clusters
# Convenient shortcuts for querying job queues and cluster node status.
# ==============================================================================

# q: View queued and running jobs for the current user
alias q="squeue -u \$USER"

# qs: View all queued and running jobs across the cluster
alias qs="squeue"

# Determine directory containing this script (supports both Bash and Zsh)
if [ -n "${BASH_SOURCE[0]}" ]; then
    _SLURM_ALIAS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
elif [ -n "${(%):-%x}" ]; then
    _SLURM_ALIAS_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd)"
else
    _SLURM_ALIAS_DIR="$(pwd)"
fi

# pbs: View PBS/Torque-style node status and GPU/CPU/Memory usage table
alias pbs="python3 \"${_SLURM_ALIAS_DIR}/check_slurm_node_usage.py\""
