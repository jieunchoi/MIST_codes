#!/bin/bash

#SBATCH -n 4
#SBATCH -N 1
#SBATCH -t <<RUNTIME>>
#SBATCH --mem 4000
#SBATCH -p conroy
#SBATCH -o <<RUNNAME>>.o
#SBATCH -e <<RUNNAME>>.e

export OMP_NUM_THREADS=4
cd <<DIRNAME>>
./clean
./mk
echo "SLURM JOB ID: $SLURM_JOB_ID"
./rn