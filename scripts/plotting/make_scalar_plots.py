import os
import sys
import argparse
import time
from copy import deepcopy
import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt

from helicalc.solenoid_geom_funcs import load_all_geoms

from BFieldPINN.plotter import(
    # utils
    check_plot_dir,
    config_plots,
    ticks_in,
    ticks_sizes,
    get_label,
)
config_plots()
from scalar_plot_funcs import plot_phi, plot_busbars_coils_RZ_projection
# configs
fpath = os.path.dirname(os.path.realpath(__file__))
configs_dir = os.path.abspath(os.path.join(fpath, '..', '..', 'configs'))
sys.path.append(configs_dir)
from model_globals import x0
from LSQ_configs import LSQ_config_dict
from PINN_configs import files_dict

## CONDUCTOR OVERLAY GLOBALS
plot_dict_all = {
    'straights': {'type': 'straight', 'z': 201, 'index_range': [None, None]},
    'arcs': {'type': 'arc', 'z': 203, 'index_range': [None, None]},
    'arcs_transfer': {'type': 'arc', 'z': 205, 'index_range': [None, None]},
    'busbarconnect': {'type': 'arc', 'z': 201, 'index_range': [None, None]},
    'coilconnect': {'type': 'arc', 'z': 201, 'index_range': [None, None]},
    'coils': {'type': 'coil', 'z': 199, 'index_range': [55, 66]}
}
model_dict = {
    '1': ['coils', 'straights', 'arcs', 'arcs_transfer'],
    '2': ['coils', 'straights', 'arcs', 'arcs_transfer'],
    '3': ['coils', 'straights', 'arcs', 'arcs_transfer'],
    '4': ['coils', 'straights', 'arcs', 'arcs_transfer'],
    '5': ['coils', 'straights', 'arcs', 'arcs_transfer'],
    '6': ['straights', 'arcs', 'arcs_transfer', 'busbarconnect'],
    '7': ['coils', 'coilconnect'],
}

## title dict
title_dict = {
    'phi_cart': r'$\varphi$ from Trivial Cartesian Terms',
    'phi_cyl': r'$\varphi$ from Cylindrical Bessel Function Expansion',
    'phi_cyl_sym': r'$\varphi$ from Cylindrical Bessel Function Expansion ($n < 1$)',
    'phi_cyl_asym': r'$\varphi$ from Cylindrical Bessel Function Expansion ($n \geq 1$)',
    'phi_PINN': r'$\varphi$ from PINN',
    'phi_tot': r'$\varphi$, Full Model',
}

if __name__=='__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-M', '--Model',
                        help='Which model do you want to fit? ["all" (default), 1, 2, 3, 4, 5, 6, 7]')
    args = parser.parse_args()
    # fill defaults if necessary
    if args.Model is None:
        args.Model = 'all'
    if args.Model == 'all':
        models = [str(i) for i in range(1, 8)]
    else:
        models = [args.Model]
    # load geometries for conductor overlay
    df_dict = load_all_geoms(version=13, return_dict=True)
    # loop through models
    for model_num in models:
        title_pre = f'Model #{model_num}: '
        print(title_pre)
        config = LSQ_config_dict[model_num]
        model_fname = files_dict[model_num]['model_fname']
        plotdir = os.path.join(model_fname, 'plots', 'phi_plots')
        os.makedirs(plotdir, exist_ok=True)
        # load df_phi and mesh_dict
        df_phi = pd.read_pickle(model_fname+'/df_scalar_Full_Results.p')
        #print(df_phi.columns)
        mesh_dict = pkl.load(open(model_fname+'/mesh_dict_scalar.p', 'rb'))
        #print(mesh_dict)
        # loop through any phi columns
        phi_cols = [c for c in df_phi.columns if ("phi_" in c) and ("rphi" not in c)]
        # loop through columns
        for phi_col in phi_cols:
            print(phi_col)
            plotfile = os.path.join(plotdir, model_num+'_'+phi_col)
            # make the base plot
            fig, ax = plot_phi(df_phi, mesh_dict, phi_col, title=title_pre+title_dict[phi_col],
                               plotfile=plotfile,
                               equal_colorbars=False, add_pos_x=True)
            # add conductor overlays
            plot_dict = {}
            for bus in model_dict[model_num]:
                plot_dict[bus] = deepcopy(plot_dict_all[bus])
            ax = plot_busbars_coils_RZ_projection(df_phi, df_dict, plot_dict, ax,
                                                  x0=x0, add_current=True)
            plotfile = os.path.join(plotdir, model_num+'_'+phi_col+'_conductor_overlay')
            ax.legend(loc='upper right').set_zorder(100)
            #ax.legend(loc='upper right', bbox_to_anchor=(1.0, 1.05)).set_zorder(100)
            fig.savefig(plotfile+'.pdf', dpi=100)
            fig.savefig(plotfile+'.png', dpi=100)
        print()
