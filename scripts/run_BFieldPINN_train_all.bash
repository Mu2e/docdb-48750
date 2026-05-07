#!/bin/bash
# driver for running all models

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

#for i in $(seq 0 3);
for i in $(seq 1 2); # fine tuning p_eff (4, 11)
do
    echo $i
    cmd="bash ${SCRIPT_DIR}/PINN/run_BFieldPINN_train_GPU${i}.bash &"
    echo $cmd
    eval "$cmd"
done
