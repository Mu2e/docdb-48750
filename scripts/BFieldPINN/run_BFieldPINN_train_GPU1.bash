#!/bin/bash
# Run one model on GPU1

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $CONDA_PREFIX/etc/profile.d/conda.sh
conda activate mu2eBFit

# hard code for testing (should not switch to "y"
# once development is done -- will override fits!!)
test="n"
#test="y"

DEV=1

for i in 2 3;
do
    echo $i
    LOGFILE=$SCRIPT_DIR/../../data/logs/docdb-48750/${i}_LSQ_fit_PINN_Training.log
    echo LOGFILE=${LOGFILE}
    cmd="python $SCRIPT_DIR/run_BFieldPINN_train.py -M $i -D $DEV -t ${test} &> $LOGFILE; python $SCRIPT_DIR/clean_PINN_log.py -L $LOGFILE >> $LOGFILE"
    echo $cmd
    eval "$cmd"
done
