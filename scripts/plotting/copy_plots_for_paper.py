import os
import time
import sys
import shutil
# configs
fpath = os.path.dirname(os.path.realpath(__file__))
configs_dir = os.path.abspath(os.path.join(fpath, '..', '..', 'configs'))
sys.path.append(configs_dir)
from LSQ_configs import LSQ_config_dict
from PINN_configs import files_dict
plots_dir = os.path.abspath(os.path.join(fpath, '..', '..', 'plots'))
sys.path.append(plots_dir)
from plots_for_paper import model_plots_for_paper

if __name__=='__main__':
    t0 = time.time()
    for model_num, plot_list in model_plots_for_paper.items():
        # temp!
        #####
        #if (not '4' in model_num) and (not '8' in model_num):
        #if (not model_num == '4') and (not model_num == '8') and (not model_num == '9'):
        if (not model_num == '1'):
            continue
        #####
        print(f'Copying plots for model {model_num}...')
        model_fname = files_dict[model_num]['model_fname']
        old_plot_dir = os.path.join(model_fname, 'plots')
        new_plot_dir = os.path.join(plots_dir, LSQ_config_dict[model_num]['subdir'])
        #print(old_plot_dir, new_plot_dir) # DEBUG
        for pfile in plot_list:
            src_file = os.path.join(old_plot_dir, pfile)
            dst_file = os.path.join(new_plot_dir, pfile)
            shutil.copy(src_file, dst_file)
        print('Done.\n')
    print('Done copying plots.')
    tf = time.time()
    dt = tf - t0
    dt_min = dt / 60.
    print(f'Elapsed time: {dt:0.1f} s = {dt_min:0.2f} min')
