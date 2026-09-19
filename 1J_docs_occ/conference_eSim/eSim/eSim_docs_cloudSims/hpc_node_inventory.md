# HPC Node Inventory — Speed Cluster

Run these commands **on the cluster** (interactive shell or inside a job) to fill in the blank table below.

## Inspection Commands

```bash
# 1. List all nodes in partition ps with core/memory/feature info
sinfo -p ps -o "%n %c %m %f %G"

# 2. Full partition descriptor for ps (CPU serial)
scontrol show partition ps

# 3. Full partition descriptor for pl (long-running jobs)
scontrol show partition pl

# 4. Full partition descriptor for pt (throughput / high-parallelism)
scontrol show partition pt

# 5. Detailed view of a specific node (replace <nodename> from sinfo output)
scontrol show node <nodename>

# 6. Current queue depth per partition
squeue -p ps,pl,pt -o "%.10i %.9P %.8j %.8u %.2t %.10M %.6D %R" | head -30
```

## Results Table

Paste `scontrol show partition` output into the Notes column, or fill manually.

| Partition | Max CPUs/task | Max mem | Max walltime | GPUs? | Notes |
|-----------|---------------|---------|--------------|-------|-------|
| ps        |               |         |              | No    |       |
| pl        |               |         |              | No    |       |
| pt        |               |         |              | No    |       |

## Target Configuration (fill after inspection)

| Setting | Planned value | Rationale |
|---------|--------------|-----------|
| `--cpus-per-task` | 32 (or actual node core count if lower) | Fill each node |
| `--mem` | 64G | ~2 GB per concurrent E+ worker |
| `--workers` | same as cpus-per-task | Intra-node E+ parallelism |
| Partition | ps (fall back to pl/pt if ps caps cpus-per-task < 32) | |

## Decision Log

| Date | Finding | Decision |
|------|---------|----------|
|      |         |          |
