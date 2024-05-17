import os
import sys
import time
import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt

from BFieldPINN.plotter import(
    # utils
    #check_plot_dir,
    config_plots,
    ticks_in,
    ticks_sizes,
    get_label,
    # plot functions
    #create_dict_from_history,
    #make_plots_history_vs_epoch,
    #make_input_data_profile,
    #make_Bi_residual_1D_hist,
    make_deriv_1D_hist,
    #make_fit_data_profile,
    #make_mu2e_plot3d,
)
config_plots()
# configs
fpath = os.path.dirname(os.path.realpath(__file__))
configs_dir = os.path.abspath(os.path.join(fpath, '..', '..', 'configs'))
sys.path.append(configs_dir)
#from model_globals import noise
#from LSQ_configs import LSQ_config_dict
#from PINN_configs import NN_config_dict, files_dict


if __name__=='__main__':
    # plot and data dirs
    plotdir = os.path.join(os.path.abspath(os.path.join(fpath, '..', '..', 'plots', 'other')), '')
    ddir = os.path.join(os.path.abspath(os.path.join(fpath, '..', '..', 'data', 'Bmaps', 'docdb-48750')), '')
    # load df
    df_interp = pd.read_pickle(ddir+'interpolation_derivatives_df.p')
    # plot!
    #### derivatives histograms
    print('Making derivatives histograms...')
    #for tup in zip([df], [' (Test Dataset)'], ['_df_test'], [200]):
    #    df_, title_suff, fname_suff, nbins = tup
    fig_dict = make_deriv_1D_hist(df_interp, bin_numerical=True, nbins=200, title_suff='',
                           include_numerical=True, include_exact=False,
                           fname_suff='', plotdir=None,
                           model_num='')
    # update title and save
    cols = ['divB', 'curlB', 'curlB_x', 'curlB_y', 'curlB_z']
    col_names = [r'$\nabla \cdot \vec{B}$', r'$\nabla \times \vec{B}$', r'$(\nabla \times \vec{B})_x$',
             r'$(\nabla \times \vec{B})_y$', r'$(\nabla \times \vec{B})_z$']
    for col, col_name in zip(cols, col_names):
        fname = os.path.join(plotdir, f'interpolation_{col}_numerical')
        fig_dict[col]['ax'].set_title(col_name+' from Interpolation: Random Sample')
        fig_dict[col]['fig'].savefig(fname+'.pdf', bbox_inches='tight', pad_inches=0.25)
    print('Done.\n')


