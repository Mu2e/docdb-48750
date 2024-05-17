import os
import sys
import numpy as np
import pandas as pd
from tqdm import tqdm
from interpolation_with_jacobian import get_df_interp_func_with_Jacobian
from BFieldPINN.tools import calc_div, calc_curl
# configs
fpath = os.path.dirname(os.path.realpath(__file__))
configs_dir = os.path.abspath(os.path.join(fpath, '..', '..', 'configs'))
sys.path.append(configs_dir)
from model_globals import noise
from LSQ_configs import LSQ_config_dict
from PINN_configs import files_dict

if __name__=='__main__':
    # get plot and dir
    #plotdir = os.path.join(os.path.abspath(os.path.join(fpath, '..', '..', 'plots', 'other')), '')
    ddir = os.path.join(os.path.abspath(os.path.join(fpath, '..', '..', 'data', 'Bmaps', 'docdb-48750')), '')
    # random seed
    np_seed = 1234
    print(f'Using numpy random seed: {np_seed}\n')
    np.random.seed(np_seed)
    # import field map
    fmap = LSQ_config_dict['1']['cfg_data_test'].path
    print(f'Interpolating the field from: {fmap}')
    df = pd.read_pickle(fmap)
    # set up interpolation function
    interp_deriv_func = get_df_interp_func_with_Jacobian(df, bounds=None, Blabels=['Bx','By','Bz'])
    # generate random df points
    N = len(df)
    print(f'Generating {N} random points in the mapping volume for interpolating.')
    Rmax = 0.8 # m
    rs = Rmax * np.sqrt(np.random.default_rng().random((N, 1)))
    ths = np.random.default_rng().random((N, 1)) * 2 * np.pi
    x_f = rs * np.cos(ths)
    y_f = rs * np.sin(ths)
    z_f = np.random.default_rng().uniform(low=df.Z.min(), high=df.Z.max(), size=((N, 1)))
    df_interp = pd.DataFrame({'X': x_f[:, 0], 'Y': y_f[:, 0], 'Z': z_f[:, 0]})
    # calculate!
    print('Interpolating...')
    B_list = []
    J_list = []
    for row in tqdm(df_interp.itertuples(), total=N):
        B, J = interp_deriv_func([row.X, row.Y, row.Z])
        B_list.append(B)
        J_list.append(J)
    B_list = np.array(B_list)
    J_list = np.array(J_list)
    divB = calc_div(J_list)
    curlB_vec = calc_curl(J_list)
    curlB = np.linalg.norm(curlB_vec, axis=1)
    # add to dataframe
    df_interp.loc[:, 'Bx_interp'] = B_list[:, 0]
    df_interp.loc[:, 'By_interp'] = B_list[:, 1]
    df_interp.loc[:, 'Bz_interp'] = B_list[:, 2]
    df_interp.loc[:, 'divB'] = divB
    df_interp.loc[:, 'curlB'] = curlB
    df_interp.loc[:, 'curlB_x'] = curlB_vec[:, 0]
    df_interp.loc[:, 'curlB_y'] = curlB_vec[:, 1]
    df_interp.loc[:, 'curlB_z'] = curlB_vec[:, 2]
    # save dataframe
    print('Saving results...')
    df_interp.to_pickle(ddir+'interpolation_derivatives_df.p')
    print('Done.')
