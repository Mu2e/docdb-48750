import os
import sys
fpath = os.path.dirname(os.path.realpath(__file__))
configs_dir = os.path.abspath(os.path.join(fpath, '..', '..', 'configs'))
sys.path.append(configs_dir)
from model_globals import LSQ_config_dict_minimal

if __name__=='__main__':
    start_dir = os.path.join(os.path.abspath(os.path.join(fpath, '..', '..')), '')
    # note if data does not exist, an actual directory will be created in the repo dir
    # (that's ok, it's not tracked).
    dirs_list = [
        'data/Bmaps/docdb-48750',
        'data/Bmaps/SolCalc_partial',
        'data/Bmaps/SolCalc_partial/tests',
        'data/Bmaps/SolCalc_partial/logs',
        'data/Bmaps/helicalc_partial',
        'data/Bmaps/helicalc_partial/tests',
        'data/Bmaps/helicalc_partial/logs',
        'data/Bmaps/auxiliary_partial',
        'data/Bmaps/auxiliary_partial/tests',
        'data/Bmaps/auxiliary_partial/logs',
        'data/Bmaps/aux',
        'data/fit_params/docdb-48750',
        'data/logs/docdb-48750',
        'data/BFieldPINN/docdb-48750',
        'data/plots/LSQ_fit/docdb-48750',
    ]
    # add the plot subdirs
    for k, subdict in LSQ_config_dict_minimal.items():
        plotdir = os.path.join('plots', subdict['subdir'])
        dirs_list.append(plotdir)

    print(f'All dirs to add, from {start_dir}: {dirs_list}')
    N = len(dirs_list)
    print_every = 1
    for i, d in enumerate(dirs_list):
        if (i % print_every == 0) or (i == N-1):
            print(f'Creating dir {i+1} / {N}')
        dirpath = os.path.join(start_dir, d)
        os.makedirs(dirpath, exist_ok=True)
    print('Done.')
