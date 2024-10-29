# FIXME!
# Ideally the cartesian term calculation and cylindrical expansion terms calculation
# track the fitting code (FMS_BFieldModel/BField_LSQ)
import numpy as np
import pandas as pd
import scipy.special as special
import tensorflow as tf
from tqdm import tqdm
import multiprocessing
from joblib import Parallel, delayed

from BFieldPINN.tools import world_to_NN

# calc_phi_cartesian, helper_phi_cyl_m, calc_phi_cyl

def center_phi(phi_vals):
    pmi = np.min(phi_vals)
    pma = np.max(phi_vals)
    pra = pma - pmi
    pmean = (pmi + pma) / 2.
    return phi_vals - pmean, pmean

def prep_phi_df(df_base, norm_dict, z0, R0=0.8, dz=0.010, dphi=0.010, dxy=0.010):
    # ranges from input df, and setup grid
    z0 = df_base.Z.min()
    z1 = df_base.Z.max()
    ### BODY (rectangle)
    zs = np.arange(z0, z1 + dz, dz)
    # phi
    phis = np.arange(0, 2*np.pi + dphi, dphi)
    Z, PHI = np.meshgrid(zs, phis)
    R = R0 * np.ones_like(Z)
    X = R * np.cos(PHI)
    Y = R * np.sin(PHI)
    df1 = pd.DataFrame({'area': 'BODY', 'make_plot': True, 'X': np.ravel(X), 'Y': np.ravel(Y), 'Z': np.ravel(Z),
                        'R': np.ravel(R), 'Phi': np.ravel(PHI), 'X_offset': 0.0, 'Y_offset': R0 * np.pi, 'z_sf': 1., 'rphi_sf': -1.})
    ### Z0 endcap: (z0, circle)
    xs = np.arange(-R0, R0+dxy, dxy)
    ys = np.arange(-R0, R0+dxy, dxy)
    XX, YY = np.meshgrid(xs, ys)
    R2 = (XX**2 + YY**2)**(1/2)
    PHI2 = np.arctan2(YY, XX)
    ZZ2 = z0 * np.ones_like(XX)
    df2 = pd.DataFrame({'area': 'Z0', 'make_plot': True, 'X': np.ravel(XX), 'Y': np.ravel(YY), 'Z': np.ravel(ZZ2),
                        'R': np.ravel(R2), 'Phi': np.ravel(PHI2), 'X_offset': z0 - R0 - 0.05, 'Y_offset': 0.0, 'z_sf': -1., 'rphi_sf': 1.})
    # remove large R points for plotting
    df2.loc[df2.R > 0.8, 'make_plot'] = False
    ### Z1 endcap: (z1, circle)
    ZZ3 = z1 * np.ones_like(XX)
    df3 = pd.DataFrame({'area': 'Z1', 'make_plot': True, 'X': np.ravel(XX), 'Y': np.ravel(YY), 'Z': np.ravel(ZZ3),
                        'R': np.ravel(R2), 'Phi': np.ravel(PHI2), 'X_offset': z1 + R0 + 0.05, 'Y_offset': 0.0, 'z_sf': 1., 'rphi_sf': 1.})
    # remove large R points for plotting
    df3.loc[df3.R > 0.8, 'make_plot'] = False
    # combine dataframes
    df_phi = pd.concat([df1, df2, df3], axis=0, ignore_index=True)
    # normalizations (PINN)
    for coord in ['X', 'Y', 'Z']:
        df_phi.loc[:, f'{coord}_norm'] = world_to_NN(df_phi.loc[:, coord], coord, norm_dict)
    # calculate R * Phi
    df_phi.loc[:, 'RPhi'] = df_phi.loc[:, 'R'] * df_phi.loc[:, 'Phi']
    # calculate centered Z (for expansion fit)
    df_phi.loc[:, 'Z_cent'] = df_phi.loc[:, 'Z'] - z0
    # store meshses (plotting)
    mesh_dict = {
        'Z0': {'X': XX, 'Y': YY},
        'BODY': {'X': Z, 'Y': R*PHI},
        'Z1': {'X': XX, 'Y': YY},
    }

    return df_phi, mesh_dict

def eval_phi_ScalarPINN(PINN_inst, df_phi):
    x_phi = tf.cast(df_phi.X_norm.values.reshape(len(df_phi), 1), dtype=tf.float32)
    y_phi = tf.cast(df_phi.Y_norm.values.reshape(len(df_phi), 1), dtype=tf.float32)
    z_phi = tf.cast(df_phi.Z_norm.values.reshape(len(df_phi), 1), dtype=tf.float32)
    inputs_phi = tf.concat([x_phi, y_phi, z_phi], axis = 1)
    pred_phi = PINN_inst.call(inputs_phi).numpy()
    df_phi.loc[:, 'phi_PINN'] = pred_phi
    df_phi.loc[~df_phi.make_plot, 'phi_PINN'] = np.nan
    # center the phi values
    df_phi.loc[:, 'phi_PINN'], phi_PINN0 = center_phi(df_phi.loc[:, 'phi_PINN'])
    return df_phi, phi_PINN0

def eval_phi_cartesian(df, **params):
    x, y, z = df[['X', 'Y', 'Z_cent']].values.T
    phi = -(params['k1']*x + params['k2']*y + params['k3']*z +
            params['k4']*x*y + params['k5']*x*z + params['k6']*y*z +
            params['k7']*x*y*z)
    df.loc[:, 'phi_cart'] = phi
    df.loc[~df.make_plot, 'phi_cart'] = np.nan
    df.loc[:, 'phi_cart'], phi_cart0 = center_phi(df.loc[:, 'phi_cart'])
    return df, phi_cart0

def helper_phi_cyl_m(df, m, params, n_min=None, n_max=None):
    phi_cyl_ = np.zeros_like(df.X)
    L = params['length1']
    k_pre = 2*np.pi / L
    km = k_pre * (m+1)
    cosZ = np.cos(km * df.Z_cent)
    sinZ = np.sin(km * df.Z_cent)
    if n_max is None:
        n_max = int(params['ns_c1'])
    if n_min is None:
        n_min = 0
    for n in range(n_min, n_max):
        try:
            Amn = params[f'Ac1_{m}_{n}']
            Bmn = params[f'Bc1_{m}_{n}']
            Dn = params[f'Dc1_{n}']
            phi_ =  special.iv(n, km * df.R) * np.sin(n * df.Phi + Dn) * (Amn*cosZ + Bmn*sinZ)
            phi_cyl_ += phi_
        except:
            pass
    return phi_cyl_

def eval_phi_cyl_single_run(df, params, n_min=None, n_max=None, num_cpu=None):
    if num_cpu is None:
        num_cpu = multiprocessing.cpu_count()
    results_list = Parallel(n_jobs=num_cpu)(delayed(helper_phi_cyl_m)(df, m, params, n_min, n_max)
                                            for m in tqdm(range(int(params['ms_c1'])), desc='m', total=int(params['ms_c1'])))
    return np.sum(results_list, axis=0)

def eval_phi_cyl_all(df, params, n_min_list=[None, None, 1], n_max_list=[None, 1, None], name_list=['phi_cyl', 'phi_cyl_sym', 'phi_cyl_asym'], num_cpu=None):
    phi0_cyl_dict = {}
    for nmi, nma, name in zip(n_min_list, n_max_list, name_list):
        print(f'{name}: n_min={nmi}, n_max={nma}')
        phi = eval_phi_cyl_single_run(df, params, n_min=nmi, n_max=nma, num_cpu=num_cpu)
        df.loc[:, name] = phi
        df.loc[~df.make_plot, name] = np.nan
        df.loc[:, name], phi0 = center_phi(df.loc[:, name])
        phi0_cyl_dict[name] = phi0
    return df, phi0_cyl_dict

def eval_total_phi(df, phi_cols=['phi_cart', 'phi_cyl', 'phi_PINN']):
    phi_tot = np.zeros(len(df))
    for col in phi_cols:
        phi_tot += df.loc[:, col]
    df.loc[:, 'phi_tot'] = phi_tot
    df.loc[:, 'phi_tot'], phi0_tot = center_phi(df.loc[:, 'phi_tot'])
    return df, phi0_tot
