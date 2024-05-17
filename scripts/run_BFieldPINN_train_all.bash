#!/bin/bash
# driver for running all models

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

for i in $(seq 0 3);
do
    echo $i
    cmd="bash ${SCRIPT_DIR}/BFieldPINN/run_BFieldPINN_train_GPU${i}.bash &"
    echo $cmd
    eval "$cmd"
done
