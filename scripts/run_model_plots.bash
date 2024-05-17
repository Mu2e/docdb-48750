#!/bin/bash
# Run all first iteration fits of LSQ

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $CONDA_PREFIX/etc/profile.d/conda.sh
conda activate mu2eBFit

# loop through the 5 models at one time
for i in $(seq 1 5);
do
    echo $i
    LOGFILE=$SCRIPT_DIR/../data/logs/docdb-48750/${i}_Model_Plots.log
    echo LOGFILE=${LOGFILE}
    python $SCRIPT_DIR/plotting/run_model_plots_single_model.py -M $i &> $LOGFILE &
done
