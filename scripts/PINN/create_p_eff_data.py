# note: must have run LSQ fit on model 1 (nominal, scalar PINN) in order to have the input data!
import os
import sys
import numpy as np
import pandas as pd
# configs
fpath = os.path.dirname(os.path.realpath(__file__))
configs_dir = os.path.abspath(os.path.join(fpath, '..', '..', 'configs'))
sys.path.append(configs_dir)
# from LSQ_configs import cfg_plot_mpl, cfg_plot_none, cfg_params_test, LSQ_config_dict
from PINN_configs import files_dict
from model_globals import noise, tau_p_eff, seed_p_eff_gen, N_toys_p_eff

if __name__=='__main__':
    model = '1' # nominal, ScalarPINN
    LSQfile = files_dict[model]['in']['meas']
    # load original df
    df = pd.read_pickle(LSQfile)
    B_fit_orig = df[['Bx_fit', 'By_fit', 'Bz_fit']].values
    # set seed and generate deltas for the N toys
    np.random.seed(seed_p_eff_gen)
    delta = np.random.normal(0.0, tau_p_eff, size=(N_toys_p_eff, len(df), 3))
    print(f'delta[0] = {delta[0]}')
    print(f'delta[1] = {delta[1]}')
    # iterate over toys
    for i in range(N_toys_p_eff):
        delta_ = delta[i]
        B_fit_pert = B_fit_orig - delta_
        # add to dataframe and save
        for ind, comp in zip([0, 1, 2], ['x', 'y', 'z']):
            df.loc[:, f'B{comp}_fit_orig'] = B_fit_orig[:, ind]
            df.loc[:, f'B{comp}_fit'] = B_fit_pert[:, ind]
            df.loc[:, f'delta_{comp}_pert'] = delta_[:, ind]
        outfile = LSQfile.replace('.Mu2E.Fit.p', f'.Mu2E.Fit.p_eff_pert_{i}.p')
        df.to_pickle(outfile)
