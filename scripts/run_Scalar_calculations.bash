#!/bin/bash
# Run all first iteration fits of LSQ

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $CONDA_PREFIX/etc/profile.d/conda.sh
conda activate mu2eBFit

# if you want to change the GPU, change it here
# PINN evaluation is not the bottleneck in this calculation, so there isn't
# much benefit to running on multiple GPUs at once.
dev=1

# loop through the 7 models
for i in $(seq 1 7);
do
    echo $i
    LOGFILE=$SCRIPT_DIR/../data/logs/docdb-48750/${i}_Scalar_calc.log
    echo LOGFILE=${LOGFILE}
    cmd="python $SCRIPT_DIR/misc/calculate_scalar_potential.py -M $i -D ${dev} &> $LOGFILE; python ${SCRIPT_DIR}/BFieldPINN/clean_PINN_log.py -L $LOGFILE >> $LOGFILE"
    echo $cmd
    eval "$cmd"
done
