from typing import Dict

def make_repro_pack_artifacts(user_goal: str, plan_md: str, inspection_md: str, pipeline_md: str) -> Dict[str, str]:
    run_local = """#!/usr/bin/env bash
set -euo pipefail

# Example placeholders:
# VCF="your.vcf.gz"
# META="metadata.tsv"
# mkdir -p results

echo "Edit this script with your real file paths."
"""

    run_hpc = """#!/bin/bash
#PBS -l select=1:ncpus=8:mpiprocs=8
#PBS -N genomics_copilot_run
#PBS -l walltime=12:00:00
#PBS -q smp
#PBS -o genomics_copilot.out
#PBS -e genomics_copilot.err

set -euo pipefail
cd $PBS_O_WORKDIR

echo "Load modules here (bcftools/plink/admixture) as needed."
"""

    readme = f"""# Genomics Agentic Research Copilot — Reproducibility Pack

## Goal
{user_goal}

## Plan
{plan_md}

## Data inspection
{inspection_md}

## Pipeline scripts / commands
{pipeline_md}

## How to run
1) Edit `run_local.sh` with your file paths  
2) Run: `bash run_local.sh`  
3) For HPC: edit modules/paths in `run_hpc.pbs` and submit with `qsub run_hpc.pbs`

## Notes
- This pack is generated automatically by the agentic app.
- Always verify paths and parameters for your dataset and organism.
"""

    return {
        "run_local.sh": run_local,
        "run_hpc.pbs": run_hpc,
        "README_repro.md": readme
    }
