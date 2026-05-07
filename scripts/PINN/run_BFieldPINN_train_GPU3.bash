#!/bin/bash
# Run one model on GPU3

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $CONDA_PREFIX/etc/profile.d/conda.sh
conda activate mu2eBFit

# hard code for testing (should not switch to "y"
# once development is done -- will override fits!!)
test="n"
#test="y"

DEV=3

# hyperparam opt
#MODELS=("1_3" "1_7" "1_11" "1_15")
# reruns
#MODELS=("1_11" "1_15")
# remove memory overrun
# MODELS=("1_3" "1_4" "1_7")
## a optimization (16 - 21)
#MODELS=("1_19")
# MODELS=("1_23")
## lambda_ optimization / tests (25-30)
#MODELS=("1_28" "1_30")
#MODELS=("1_29")
#MODELS=("5")
# MODELS=("1_0")
# MODELS=("4_0")
# p_eff estimation
#MODELS=("1_p_eff_pert_15" "1_p_eff_pert_16" "1_p_eff_pert_17" "1_p_eff_pert_18" "1_p_eff_pert_19")
# rerun 1 with the proper pretraining
MODELS=("1")

#for i in 5 7;
#for i in 7;
for i in "${MODELS[@]}";
do
    echo $i
    LOGFILE=$SCRIPT_DIR/../../data/logs/docdb-48750/${i}_LSQ_fit_PINN_Training.log
    echo LOGFILE=${LOGFILE}
    cmd="python $SCRIPT_DIR/run_BFieldPINN_train.py -M $i -D $DEV -t ${test} &> $LOGFILE; python $SCRIPT_DIR/clean_PINN_log.py -L $LOGFILE >> $LOGFILE"
    echo $cmd
    eval "$cmd"
done
