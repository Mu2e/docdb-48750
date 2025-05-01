#!/bin/bash
# Run one model on GPU0

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $CONDA_PREFIX/etc/profile.d/conda.sh
conda activate mu2eBFit

# hard code for testing (should not switch to "y"
# once development is done -- will override fits!!)
test="n"
#test="y"

DEV=0

# hyperparam opt
# MODELS=("1_0" "1_4" "1_8" "1_12")
# reruns
# MODELS=("1_12")
# MODELS=("1_9")
# remove memory overrun
#MODELS=("1_0" "1_8" "1_12")
# MODELS=("1_0")
## a optimization (16 - 22)
#MODELS=("1_16")
#MODELS=("1_22")
## lambda_ optimization / tests (25-30)
#MODELS=("1_25")
# MODELS=("1_30")
# MODELS=("9")
# MODELS=("1")
MODELS=("1_0")

#for i in 1;
for i in "${MODELS[@]}";
do
    echo $i
    LOGFILE=$SCRIPT_DIR/../../data/logs/docdb-48750/${i}_LSQ_fit_PINN_Training.log
    echo LOGFILE=${LOGFILE}
    cmd="python $SCRIPT_DIR/run_BFieldPINN_train.py -M $i -D $DEV -t ${test} &> $LOGFILE; python $SCRIPT_DIR/clean_PINN_log.py -L $LOGFILE >> $LOGFILE"
    echo $cmd
    eval "$cmd"
done
