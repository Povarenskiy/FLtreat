#!/bin/sh 
#SBATCH -U "dep 816, user kuhtevich, theme 00000.000, prog FIRECON, task 00346, cust SAEP, tel 28774, class 99" 
#SBATCH -N 2 -n 24 --ntasks-per-node=12 --nice=0  -p BATCH -t 300:00:00 -o go_00346.o%j -e go_00346.e%j	
export MPIRUN_USE_TREES=1	
export MPIRUN_USE_GATHER_TREE=1 
export MPIRUN_USE_BCAST_TREE=1 
export VIADEV_USE_SHMEM_COLL=0 
/opt/slurm/bin/srun --mpi=mvapich ./EGAK_3 00346