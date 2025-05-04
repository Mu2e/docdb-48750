#!/bin/bash
# Run one model on GPU2

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $CONDA_PREFIX/etc/profile.d/conda.sh
conda activate mu2eBFit

# hard code for testing (should not switch to "y"
# once development is done -- will override fits!!)
test="n"
#test="y"

DEV=2

# hyperparam opt
# MODELS=("1_2" "1_6" "1_10" "1_14")
# reruns
# MODELS=("1_14")
# MODELS=("1_12")
# remove memory overrun
# MODELS=("1_2" "1_6" "1_10")
## a optimization (16 - 21)
#MODELS=("1_18" "1_21")
#MODELS=("1_18")
# MODELS=("1_24") # tanh
## lambda_ optimization / tests (25-30)
#MODELS=("1_27" "1_29")
#MODELS=("1_28")
MODELS=("4")

#for i in 4 6;
#for i in 6;
for i in "${MODELS[@]}";
do
    echo $i
    LOGFILE=$SCRIPT_DIR/../../data/logs/docdb-48750/${i}_LSQ_fit_PINN_Training.log
    echo LOGFILE=${LOGFILE}
    cmd="python $SCRIPT_DIR/run_BFieldPINN_train.py -M $i -D $DEV -t ${test} &> $LOGFILE; python $SCRIPT_DIR/clean_PINN_log.py -L $LOGFILE >> $LOGFILE"
    echo $cmd
    eval "$cmd"
done
