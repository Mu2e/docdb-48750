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

# hyperparam opt
#MODELS=("1_1" "1_5" "1_9" "1_13")
# reruns
#MODELS=("1_9" "1_13")
# MODELS=("1_13")
# remove memory overrun
#MODELS=("1_1" "1_5" "1_9" "1_13")
# MODELS=("1_10")
## a optimization (16 - 23)
# MODELS=("1_17" "1_20")
#MODELS=("1_23")
# MODELS=("1_17")
# MODELS=("1")
## lambda_ optimization / tests (25-30)
#MODELS=("1_26")
# MODELS=("1_27")
# MODELS=("1_0")
MODELS=("1")

#for i in 2 3;
for i in "${MODELS[@]}";
do
    echo $i
    LOGFILE=$SCRIPT_DIR/../../data/logs/docdb-48750/${i}_LSQ_fit_PINN_Training.log
    echo LOGFILE=${LOGFILE}
    cmd="python $SCRIPT_DIR/run_BFieldPINN_train.py -M $i -D $DEV -t ${test} &> $LOGFILE; python $SCRIPT_DIR/clean_PINN_log.py -L $LOGFILE >> $LOGFILE"
    echo $cmd
    eval "$cmd"
done
