#!/bin/bash
# Run all first iteration fits of LSQ

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

source $CONDA_PREFIX/etc/profile.d/conda.sh
conda activate mu2eBFit

# hard code for testing (should not switch to "y"
# once development is done -- will override fits!!)
test="n"
#test="y"

# loop through the 7 models
for i in $(seq 1 7);
do
    echo $i
    LOGFILE=$SCRIPT_DIR/../data/logs/docdb-48750/${i}_LSQ_fit_Initial.log
    echo LOGFILE=${LOGFILE}
    python $SCRIPT_DIR/LSQ/run_LSQ_fit.py -M $i -P n -t ${test} &> $LOGFILE
done
