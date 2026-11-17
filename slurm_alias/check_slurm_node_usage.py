#!/usr/bin/env python3
import subprocess
import re
import sys

# Mapping of known GPU models to their memory size in GB
GPU_MEM_MAP = {
    'rtx3080': '10gb',
    'rtx3090': '24gb',
    'rtx2080ti': '11gb',
    'rtx4080': '16gb',
    'rtx4090': '24gb',
    'rtx6000': '48gb',
    'l40s': '48gb',
    'l40': '48gb',
    'l4': '24gb',
    't4': '16gb',
    'v100_32g': '32gb',
    'v100': '16gb',
    'a100': '40gb',
    'a100_80gb': '80gb',
    'a800': '80gb',
    'a6000': '48gb',
    'a5000': '24gb',
    'a40': '48gb',
    'a30': '24gb',
    'a10': '24gb',
    'h100': '80gb',
    'h800': '80gb',
    'h200': '141gb',
    'b200': '192gb',
}

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout
    except FileNotFoundError:
        sys.stderr.write(f"Error: Command '{cmd[0]}' not found. Please ensure Slurm client tools are installed and in PATH.\n")
        return ""
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Error running command {' '.join(cmd)}: {e.stderr}\n")
        return ""

def parse_idx_string(idx_str):
    """Parses a string like '0-2,4' into a list of integer indices [0, 1, 2, 4]."""
    indices = []
    if not idx_str:
        return indices
    for part in idx_str.split(','):
        if '-' in part:
            try:
                start, end = part.split('-')
                indices.extend(range(int(start), int(end) + 1))
            except ValueError:
                pass
        else:
            try:
                indices.append(int(part))
            except ValueError:
                pass
    return indices

def parse_gres(gres_str):
    """Parses Gres string to return (gpu_type, total_gpus)."""
    if not gres_str or gres_str == '(null)':
        return None, 0
    # Pattern: gpu:type:count
    match = re.search(r'gpu:([^:]+):(\d+)', gres_str)
    if match:
        return match.group(1), int(match.group(2))
    # Pattern: gpu:count
    match = re.search(r'gpu:(\d+)', gres_str)
    if match:
        return 'gpu', int(match.group(1))
    return None, 0

def get_gpu_mem(gpu_type):
    """Resolves GPU memory size."""
    if not gpu_type:
        return "0gb"
    match = re.search(r'(\d+)g', gpu_type)
    if match:
        return f"{match.group(1)}gb"
    return GPU_MEM_MAP.get(gpu_type.lower(), "16gb")

def safe_int(val, default=0):
    """Safely converts string to int, returning default on failure or non-numeric strings like 'N/A'."""
    if not val:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def extract_field(line, field_name):
    """Extracts the value of a specific field from scontrol oneliner output."""
    match = re.search(rf'\b{field_name}=(\S+)', line)
    return match.group(1) if match else None

def natural_sort_key(s):
    """Generates a natural sorting key for strings containing numbers."""
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', s)]

def main():
    partition_filter = sys.argv[1] if len(sys.argv) > 1 else None

    # Get job info
    # Run scontrol show job -d -o
    jobs_output = run_cmd(['scontrol', 'show', 'job', '-d', '-o'])
    
    # Dictionaries to map jobs to nodes/GPUs
    # (node_name, gpu_idx) -> list of job dicts
    node_gpu_jobs = {}
    # node_name -> list of job dicts (CPU-only jobs on that node)
    node_cpu_jobs = {}
    # List to store raw details for the job detail table
    job_detail_rows = []
    # Set to keep track of nodes printed (for filtering the job list by partition)
    printed_nodes = set()

    # Regex to find Nodes=... GRES=... in job output
    # e.g., Nodes=node-32 CPU_IDs=0-3,16-19 Mem=0 GRES=gpu:v100_32g:1(IDX:0)
    alloc_pattern = re.compile(r'Nodes=([a-zA-Z0-9_-]+)\s+CPU_IDs=[^\s]+\s+Mem=[^\s]+\s+GRES=([^\s]*)')

    for line in jobs_output.strip().split('\n'):
        if not line:
            continue
        job_state = extract_field(line, 'JobState')
        if job_state not in ('RUNNING', 'SUSPENDED'):
            continue
        
        job_id = extract_field(line, 'JobId')
        user_info = extract_field(line, 'UserId')
        user = user_info.split('(')[0] if user_info else 'unknown'
        num_cpus_str = extract_field(line, 'NumCPUs')
        num_cpus = safe_int(num_cpus_str, 1)
        job_name = extract_field(line, 'JobName') or 'unknown'

        job_info = {
            'JobId': job_id,
            'User': user,
            'NumCPUs': num_cpus,
            'State': job_state,
            'JobName': job_name
        }

        # Find all node allocations for this job
        allocations = alloc_pattern.findall(line)
        for node, gres_info in allocations:
            # Extract TresPerNode for the job details table
            tres_per_node = extract_field(line, 'TresPerNode')
            gres_val = tres_per_node if (tres_per_node and tres_per_node != '(null)') else "N/A"
            
            # Save raw job details
            job_detail_rows.append({
                'Node': node,
                'JobId': job_id,
                'User': user,
                'State': job_state,
                'NumCPUs': num_cpus,
                'Gres': gres_val,
                'JobName': job_name
            })

            idx_match = re.search(r'IDX:([0-9,-]+)', gres_info)
            if idx_match:
                gpu_indices = parse_idx_string(idx_match.group(1))
                # Distribute CPUS across the allocated GPUs on this node
                cpus_per_gpu = max(1, num_cpus // len(gpu_indices)) if gpu_indices else num_cpus
                for idx in gpu_indices:
                    key = (node, idx)
                    if key not in node_gpu_jobs:
                        node_gpu_jobs[key] = []
                    # Create a copy with adjusted CPU count for this GPU
                    g_job = job_info.copy()
                    g_job['NumCPUs'] = cpus_per_gpu
                    node_gpu_jobs[key].append(g_job)
            else:
                # CPU job or GPU job with no IDX assigned yet
                if node not in node_cpu_jobs:
                    node_cpu_jobs[node] = []
                node_cpu_jobs[node].append(job_info)

    # Get node info
    nodes_output = run_cmd(['scontrol', 'show', 'node', '-d', '-o'])
    if not nodes_output and not jobs_output:
        return
    
    # Print headers
    format_str = "{:<25} {:<15} {:>6} {:>5} {:>6} {:>12} {:>7} {:>7} {:>7} {}"
    print(format_str.format("", "", "", "", "", "mem", "ncpus", "nmics", "ngpus", ""))
    print(format_str.format("vnode", "state", "njobs", "run", "susp", "f/t", "f/t", "f/t", "f/t", "jobs"))
    print(format_str.format("-" * 25, "-" * 15, "-" * 6, "-" * 5, "-" * 6, "-" * 12, "-" * 7, "-" * 7, "-" * 7, "-" * 7))

    for line in nodes_output.strip().split('\n'):
        if not line:
            continue
        
        node_name = extract_field(line, 'NodeName')
        if not node_name:
            continue
        
        partitions = extract_field(line, 'Partitions') or ''
        if partition_filter and partition_filter not in partitions:
            continue
        printed_nodes.add(node_name)

        cpu_tot_str = extract_field(line, 'CPUTot')
        cpu_alloc_str = extract_field(line, 'CPUAlloc')
        cpu_tot = safe_int(cpu_tot_str, 0)
        cpu_alloc = safe_int(cpu_alloc_str, 0)
        cpu_free = max(0, cpu_tot - cpu_alloc)

        real_mem_str = extract_field(line, 'RealMemory')
        free_mem_str = extract_field(line, 'FreeMem')
        real_mem_gb = safe_int(real_mem_str, 0) // 1024
        free_mem_gb = safe_int(free_mem_str, 0) // 1024

        state = extract_field(line, 'State') or 'unknown'
        gres = extract_field(line, 'Gres') or ''

        gpu_type, num_gpus = parse_gres(gres)

        # Check if node is offline
        is_offline = any(s in state.upper() for s in ('DOWN', 'DRAIN', 'FAIL', 'POWER_DOWN'))
        if is_offline:
            cpu_free = 0
            free_mem_gb = 0

        if num_gpus == 0:
            # CPU Node
            # Determine state
            if is_offline:
                node_state = 'offline'
            elif cpu_free <= 0:
                node_state = 'job-busy'
            else:
                node_state = 'free'

            # Gather jobs running on this CPU node
            jobs_list = node_cpu_jobs.get(node_name, [])
            seen = set()
            deduped_job_strings = []
            for j in jobs_list:
                if j['JobId'] not in seen:
                    seen.add(j['JobId'])
                    deduped_job_strings.append(f"{j['JobId']}:{j['JobName']}({j['User']})")

            njobs = len(seen)
            run_jobs = sum(1 for j in jobs_list if j['State'] == 'RUNNING')
            susp_jobs = sum(1 for j in jobs_list if j['State'] == 'SUSPENDED')

            mem_str = f"{free_mem_gb}gb/{real_mem_gb}gb"
            cpu_str = f"{cpu_free}/{cpu_tot}"
            jobs_str = ",".join(deduped_job_strings) if deduped_job_strings else "--"
            partition_type = partitions.split(',')[0].replace('*', '') if partitions else 'cpu'
            node_display_name = f"{node_name}({partition_type})"

            print(format_str.format(
                node_display_name,
                node_state,
                njobs,
                run_jobs,
                susp_jobs,
                mem_str,
                cpu_str,
                "0/0",
                "0/0",
                jobs_str
            ))
        else:
            # GPU Node
            # Distribute CPU-only jobs on this node to GPU subnodes
            gpu_allocations = [[] for _ in range(num_gpus)]
            for idx in range(num_gpus):
                gpu_allocations[idx].extend(node_gpu_jobs.get((node_name, idx), []))

            # Assign CPU-only jobs to subnodes with the most free CPUs
            cpu_only_jobs = node_cpu_jobs.get(node_name, [])
            for job in cpu_only_jobs:
                # Find GPU index with the most free CPUs
                best_idx = 0
                max_free_cpus = -999999
                for idx in range(num_gpus):
                    allocated_cpus = sum(j['NumCPUs'] for j in gpu_allocations[idx])
                    free_cpus = (cpu_tot // num_gpus) - allocated_cpus
                    if free_cpus > max_free_cpus:
                        max_free_cpus = free_cpus
                        best_idx = idx
                gpu_allocations[best_idx].append(job)

            # Print subnodes
            gpu_mem = get_gpu_mem(gpu_type)
            gpu_display = gpu_type.replace('_', '-') if gpu_type else 'gpu'
            for idx in range(num_gpus):
                subnode_name = f"{node_name}[{idx}]({gpu_display})"
                sub_jobs = gpu_allocations[idx]
                seen = set()
                deduped_job_strings = []
                for j in sub_jobs:
                    if j['JobId'] not in seen:
                        seen.add(j['JobId'])
                        deduped_job_strings.append(f"{j['JobId']}:{j['JobName']}({j['User']})")

                njobs = len(seen)
                run_jobs = sum(1 for j in sub_jobs if j['State'] == 'RUNNING')
                susp_jobs = sum(1 for j in sub_jobs if j['State'] == 'SUSPENDED')

                if is_offline:
                    subnode_state = 'offline'
                elif njobs > 0:
                    subnode_state = 'job-exclusive'
                else:
                    subnode_state = 'free'

                # Calculate CPU counts for this GPU subnode
                total_cpus_sub = cpu_tot // num_gpus
                allocated_cpus_sub = sum(j['NumCPUs'] for j in sub_jobs)
                limit_cpus_sub = max(total_cpus_sub, allocated_cpus_sub)
                free_cpus_sub = 0 if is_offline else max(0, limit_cpus_sub - allocated_cpus_sub)

                mem_str = f"{gpu_mem}/{gpu_mem}"
                cpu_str = f"{free_cpus_sub}/{limit_cpus_sub}"
                
                # Check if this GPU index is actually allocated to a job
                has_gpu_job = any((node_name, idx) in node_gpu_jobs for _ in sub_jobs)
                gpu_str = "0/1" if (has_gpu_job or is_offline) else "1/1"
                
                jobs_str = ",".join(deduped_job_strings) if deduped_job_strings else "--"

                print(format_str.format(
                    subnode_name,
                    subnode_state,
                    njobs,
                    run_jobs,
                    susp_jobs,
                    mem_str,
                    cpu_str,
                    "0/0",
                    gpu_str,
                    jobs_str
                ))

    # Print active jobs table
    print()
    job_format_str = "{:<12} {:<10} {:<12} {:<10} {:<5} {:<15} {}"
    print(job_format_str.format("node", "jobid", "user", "state", "cpus", "gres", "name"))
    
    # Filter rows if partition_filter is set
    filtered_rows = job_detail_rows
    if partition_filter:
        filtered_rows = [r for r in job_detail_rows if r['Node'] in printed_nodes]
        
    if not filtered_rows:
        print("-- no running jobs mapped to nodes --")
    else:
        filtered_rows.sort(key=lambda r: (natural_sort_key(r['Node']), natural_sort_key(r['JobId'])))
        for row in filtered_rows:
            print(job_format_str.format(
                row['Node'],
                row['JobId'],
                row['User'],
                row['State'],
                str(row['NumCPUs']),
                row['Gres'],
                row['JobName']
            ))

if __name__ == '__main__':
    main()
