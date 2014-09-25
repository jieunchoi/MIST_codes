#!/bin/bash

#SBATCH -n 8
#SBATCH -N 1
#SBATCH -t <<RUNTIME>>
#SBATCH --mem 8000
#SBATCH -p conroy
#SBATCH -o <<RUNNAME>>.o
#SBATCH -e <<RUNNAME>>.e

cd <<DIRNAME>>
./clean
./mk
./rn