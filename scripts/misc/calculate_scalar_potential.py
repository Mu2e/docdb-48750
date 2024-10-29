# this code calculates the scalar potential from the different components of the model
# Note that we can only calculate the PINN scalar potential when using the ScalarPINN.
# In model tests using StandardPINN, the PINN df columns will be left off.
import os
import sys
import argparse
import pickle as pkl
import numpy as np
import pandas as pd
import multiprocessing
from joblib import Parallel, delayed
from BFieldPINN import BFieldPINN_data
from BFieldPINN.ScalarPINN import ScalarPINN
from BFieldPINN.StandardPINN import StandardPINN
from BFieldPINN.tools import (
    init_GPU,
    set_GPU,
    get_GPU,
)
from scalar_potential_funcs import center_phi, prep_phi_df, eval_phi_ScalarPINN, eval_phi_cartesian, helper_phi_cyl_m, eval_phi_cyl_all, eval_total_phi
# configs
fpath = os.path.dirname(os.path.realpath(__file__))
configs_dir = os.path.abspath(os.path.join(fpath, '..', '..', 'configs'))
sys.path.append(configs_dir)
from LSQ_configs import LSQ_config_dict
from PINN_configs import NN_config_dict, files_dict

if __name__=='__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-M', '--Model',
                        help='Which model do you want to fit? [1 (default), 2, 3, 4, 5, 6, 7]')
    parser.add_argument('-D', '--Device',
                        help='Which GPU to use? [0 (default), 1, 2, 3].')
    args = parser.parse_args()
    # fill defaults if necessary
    if args.Model is None:
        args.Model = '1'
    # if args.Model == 'all':
    #     models = [str(i) for i in range(1, 8)]
    # else:
    #     models = [args.Model]
    models = [args.Model]
    if args.Device is None:
        args.Device = '0'
    # initializations
    # GPU
    dev = args.Device
    init_GPU()
    set_GPU(dev)
    print(f"The current GPU is: {get_GPU()}")
    # run specific models
    for model in models:
        config = LSQ_config_dict[model]
        model_fname = files_dict[model]['model_fname']
        NN_type = NN_config_dict[model]['NN_type']
        print(f'Model {model}: {NN_type}PINN, {model_fname}')
        # grab df_test and norm_dict
        if NN_type == 'Scalar':
           myPINN = ScalarPINN.load_model(model_fname)
        else:
           myPINN = StandardPINN.load_model(model_fname)
        norm_dict = myPINN.norm_dict
        df_test = pd.read_pickle(model_fname+'/df_test_Full_Results.p')
        # load LSQ params (PINN subtracted). grab z0
        pfile = config['cfg_pickle_ps'].save_name +'_results.p'
        param_file = os.path.join(BFieldPINN_data, 'fit_params', pfile)
        params = pkl.load(open(param_file, 'rb'))
        z0 = params['z0']
        # set up df
        df_phi, mesh_dict = prep_phi_df(df_test, norm_dict, z0, R0=0.8, dz=0.010, dphi=0.010, dxy=0.010)
        # PINN terms, if relevant
        if NN_type == 'Scalar':
            print('Adding PINN scalar...')
            df_phi, phi0_PINN = eval_phi_ScalarPINN(myPINN, df_phi)
            print('Done.')
        else:
            print(f'NN_type={NN_type} does not allow for calculation of scalar. Skipping.')
            phi0_PINN = None
        # Cartesian terms
        df_phi, phi0_cart = eval_phi_cartesian(df_phi, **params)
        # LSQ model terms
        df_phi, phi0_dict = eval_phi_cyl_all(df_phi, params,
                                             n_min_list=[None, None, 1],
                                             n_max_list=[None, 1, None],
                                             name_list=['phi_cyl', 'phi_cyl_sym', 'phi_cyl_asym'],
                                             num_cpu=64)
        # calculate total
        if NN_type == 'Scalar':
            phi_cols = ['phi_cart', 'phi_cyl', 'phi_PINN']
        else:
            phi_cols = ['phi_cart', 'phi_cyl']
        df_phi, phi0_tot = eval_total_phi(df_phi, phi_cols=phi_cols)
        print(df_phi)
        # complete the phi0 dict
        phi0_dict['phi_cart'] = phi0_cart
        phi0_dict['phi_PINN'] = phi0_PINN
        phi0_dict['phi_tot'] = phi0_tot
        # save df, phi0 dict, and mesh_dict in PINN model directory.
        df_file = model_fname+'/df_scalar_Full_Results.p'
        phi0_file = model_fname+'/phi0_dict_scalar.p'
        mesh_file = model_fname+'/mesh_dict_scalar.p'
        df_phi.to_pickle(df_file)
        pkl.dump(phi0_dict, open(phi0_file, 'wb'))
        pkl.dump(mesh_dict, open(mesh_file, 'wb'))
