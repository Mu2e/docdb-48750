from copy import deepcopy # for testing
import os
import numpy as np
import pandas as pd
from mu2e import mu2e_ext_path
from mu2e.cfg_defs import cfg_data, cfg_geom, cfg_plot, cfg_params, cfg_pickle
from mean_fields import get_mean_fields_dict
from model_globals import noise, noise_str, phony_curl, phony_curl_str, z0, LSQ_config_dict_minimal, N_opt_tests, opt_dict, p_eff_dict, N_toys_nominal

#### field map locations
# test / validation points (only one map)
mapfile_test = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar.Mu2E.p'
# fitting points
mapfile_125 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}.Mu2E.p'
mapfile_3 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_external_fit.Mu2E.p'
mapfile_4 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}{phony_curl_str}.Mu2E.p'
mapfile_6 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_No_Coils_All_Busbars{noise_str}.Mu2E.p'
mapfile_7 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_No_Busbars{noise_str}.Mu2E.p'
mapfile_8 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_HPCMagUnc.Mu2E.p'
mapfile_9 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_SparseZPhi.Mu2E.p'
mapfile_10 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_HPCMagUnc_SparseZPhi.Mu2E.p'
# calculate mean Bx, By, Bz (for params setup)
mean_fields_dict = get_mean_fields_dict({'nominal': mapfile_125, 'phony_curl': mapfile_4, 'busbars': mapfile_6, 'DSCoils': mapfile_7, 'HPCMagUnc': mapfile_8})
# model 1 toys:
mapfile_1_toys = {}
for toy_num in range(N_toys_nominal-1):
    model_num = f'1_toy_{toy_num}'
    mapfile_1_toys[model_num] = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_toy_{toy_num}.Mu2E.p'

mfd = get_mean_fields_dict({model_num: mapfile for model_num, mapfile in mapfile_1_toys.items()})
mean_fields_dict.update(mfd)
#### Shared tuples ####
# data
cfg_data_test = cfg_data('helicalc', 'DS', mapfile_test,
                         #('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
                         ('Z >= 4.25', 'Z <= 13.85', 'R <= 0.800'))
# geom
# full phi steps
phi_steps = (0., 0.39269908, 0.78539816, 1.17809725, 1.57079633, 1.96349541,
            2.35619449, 2.74889357)
# 1/2 phi steps
phi_steps_half = (0., 0.78539816, 1.57079633,2.35619449)
cfg_geom_cyl = cfg_geom('cyl', z_steps=None, r_steps=None, phi_steps=phi_steps,
                        x_steps=None, y_steps=None, systunc=None,
                        interpolate=False, do2pi=False, do_selection=False)
cfg_geom_cyl_half = cfg_geom('cyl', z_steps=None, r_steps=None, phi_steps=phi_steps_half,
                        x_steps=None, y_steps=None, systunc=None,
                        interpolate=False, do2pi=False, do_selection=False)
cfg_geom_cart = cfg_geom('cart', z_steps=None, r_steps=None, phi_steps=None,
                        x_steps=None, y_steps=None, systunc=None,
                        interpolate=False, do2pi=False, do_selection=False)
# plot
# note: sub_dir does not do anything at the moment.
cfg_plot_mpl = cfg_plot('mpl_nonuni', zlims=[-2, 2], save_loc='LSQ_fit/docdb-48750', sub_dir=None, df_fine=None)
cfg_plot_none = cfg_plot('none', zlims=None, save_loc=None, sub_dir=None, df_fine=None)
# minimal params for testing
cfg_params_test = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         length1=0, ms_c1=0, ns_c1=0, length2=0, ms_c2=0, ns_c2=0,
                         ks_dict={'k1': [mean_fields_dict['nominal']['Bx'], True],
                                  'k2': [mean_fields_dict['nominal']['By'], True],
                                  'k3': [mean_fields_dict['nominal']['Bz'], True],
                                  'k4': [0., True], 'k5': [0., True],
                                  'k6': [0., True], 'k7': [0., True],},
                         bs_tuples=None, bs_bounds=None,
                         loss='linear', method='leastsq',
                         ms_asym_max=-1,
                         #version=1006,
                         version=1008,
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)

#### Model specific configurations
#### Fit 1. nominal ####
# data
cfg_data1 = cfg_data('helicalc', 'DS', mapfile_125,
                     #('Z > 4.200', 'Z < 13.900'))
                     ('Z >= 4.25', 'Z <= 13.85')) # fix to use BP at upstream end
# PINN subtracted
n = LSQ_config_dict_minimal['1']['fitnames']['Initial']
mapfile_ps1 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps1 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps1 = cfg_data('helicalc', 'DS', mapfile_ps1,
                        #('Z > 4.200', 'Z < 13.900'))
                        ('Z >= 4.25', 'Z <= 13.85'))
cfg_data_test_ps1 = cfg_data('helicalc', 'DS', mapfile_test_ps1,
                             #('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
                             ('Z >= 4.25', 'Z <= 13.85', 'R <= 0.800'))
# params
'''
cfg_params1 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         length1=12.5, ms_c1=70, ns_c1=7, length2=0, ms_c2=0, ns_c2=0,
                         ks_dict={'k1': [mean_fields_dict['nominal']['Bx'], False],
                                  'k2': [mean_fields_dict['nominal']['By'], False],
                                  'k3': [mean_fields_dict['nominal']['Bz'], False],
                                  'k4': [0., True], 'k5': [0., False],
                                  'k6': [0., False], 'k7': [0., True],},
                         bs_tuples=None, bs_bounds=None,
                         loss='linear', method='leastsq',
                         ms_asym_max=10,
                         version=1006,
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)
'''
## FIXME! This is just for testing various parameter configurations for PINN paper
cfg_params1 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         # length1=12.5, ms_c1=70, ns_c1=7, length2=0, ms_c2=0, ns_c2=0, # v1008, chi2=8.9
                         #length1=12.5, ms_c1=70, ns_c1=7, length2=0, ms_c2=0, ns_c2=0, # v1008, chi2=2.1
                         #length1=12.5, ms_c1=50, ns_c1=10, length2=0, ms_c2=0, ns_c2=0, # v1008, chi2=
                         #length1=12.5, ms_c1=50, ns_c1=5, length2=0, ms_c2=0, ns_c2=0,
                         #length1=12.5, ms_c1=70, ns_c1=8, length2=0, ms_c2=0, ns_c2=0,
                         ###length1=13.850 - 4.215 + 3.4, ms_c1=40, ns_c1=4, length2=0, ms_c2=0, ns_c2=0,
                         # first test
                         #length1=12.5, ms_c1=45, ns_c1=7, length2=0, ms_c2=0, ns_c2=0,
                         #length1=12.5, ms_c1=70, ns_c1=3, length2=0, ms_c2=0, ns_c2=0,
                         length1=12.5, ms_c1=55, ns_c1=7, length2=0, ms_c2=0, ns_c2=0, # GOOD! Nominal fit, nominal set of data
                         #length1=12.5, ms_c1=55, ns_c1=3, length2=0, ms_c2=0, ns_c2=0, # with limited Z and Phi (x1/2 in both)
                         # length1=12.5, ms_c1=55, ns_c1=1, length2=0, ms_c2=0, ns_c2=0, # quick test
                         # length1=12.5, ms_c1=70, ns_c1=1, length2=0, ms_c2=0, ns_c2=0,
                         ks_dict={'k1': [mean_fields_dict['nominal']['Bx'], True],
                                  'k2': [mean_fields_dict['nominal']['By'], True],
                                  'k3': [mean_fields_dict['nominal']['Bz'], False],
                                  'k4': [0., True], 'k5': [0., True],
                                  'k6': [0., True], 'k7': [0., True],},
                         # no ks, all zero
                         # ks_dict={'k1': [0., True],
                         #          'k2': [0., True],
                         #          'k3': [0., True],
                         #          'k4': [0., True], 'k5': [0., True],
                         #          'k6': [0., True], 'k7': [0., True],},
                         bs_tuples=None, bs_bounds=None,
                         loss='linear', method='leastsq', # lm
                         # loss='linear', method='least_squares', # trf
                         # loss='linear', method='newton', # newton-cg -- jac required
                         # loss='linear', method='cg', # cg -- extremely slow convergence
                         # ms_asym_max=10, # v1008, chi2=8.9
                         #ms_asym_max=15,
                         # ms_asym_max=20,
                         #ms_asym_max=30, # v1008, chi2=2.
                         # ms_asym_max=60,
                         ms_asym_max=-1, # NOMINAL
                         #version=1006,
                         #version=1007,
                         version=1008, # FOR PAPER
                         # version=1009, # single unconstrained normalization, phases
                         ###version=1010, # include k=0 (one additional term: n=1, non-zero Br) No! this model does not have any non-zero terms!
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)
                         # noise=noise, z0=4.215, AB_lim=None, k_lim=None)
# pickle
# first fit
cfg_pickle1 = cfg_pickle(use_pickle=False, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}', recreate=False)
# test
cfg_pickle_test1 = cfg_pickle(use_pickle=True, save_pickle=False,
                              load_name=f'docdb-48750/helicalc_Rebar{noise_str}',
                              save_name=f'docdb-48750/helicalc_Rebar{noise_str}', recreate=True)
# PINN subracted fit
cfg_pickle_ps1 = cfg_pickle(use_pickle=True, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}_PINN_subtracted', recreate=False)
# test, PINN subtracted
cfg_pickle_ps_test1 = cfg_pickle(use_pickle=True, save_pickle=False,
                                 load_name=f'docdb-48750/helicalc_Rebar{noise_str}_PINN_subtracted',
                                 save_name=f'docdb-48750/helicalc_Rebar{noise_str}_PINN_subtracted', recreate=True)

#### Fit 2. nominal, using traditional PINN ####
# data
cfg_data2 = cfg_data('helicalc', 'DS', mapfile_125,
                     ('Z > 4.200', 'Z < 13.900'))
# PINN subtracted
n = LSQ_config_dict_minimal['2']['fitnames']['Initial']
mapfile_ps2 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps2 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps2 = cfg_data('helicalc', 'DS', mapfile_ps2,
                        ('Z > 4.200', 'Z < 13.900'))
cfg_data_test_ps2 = cfg_data('helicalc', 'DS', mapfile_test_ps2,
                             ('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
# params
# cfg_params2 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
#                          length1=12.5, ms_c1=70, ns_c1=7, length2=0, ms_c2=0, ns_c2=0,
#                          ks_dict={'k1': [mean_fields_dict['nominal']['Bx'], False],
#                                   'k2': [mean_fields_dict['nominal']['By'], False],
#                                   'k3': [mean_fields_dict['nominal']['Bz'], False],
#                                   'k4': [0., True], 'k5': [0., False],
#                                   'k6': [0., False], 'k7': [0., True],},
#                          bs_tuples=None, bs_bounds=None,
#                          loss='linear', method='leastsq',
#                          ms_asym_max=10,
#                          version=1006,
#                          noise=noise, z0=z0, AB_lim=None, k_lim=None)
# FIXME! This is a test of traditional PINN with new formalism
cfg_params2 = deepcopy(cfg_params1)
# pickle
# first fit
#cfg_pickle2 = cfg_pickle(use_pickle=False, save_pickle=True,
#                         load_name=f'docdb-48750/helicalc_standard_PINN_Rebar{noise_str}',
cfg_pickle2 = cfg_pickle(use_pickle=True, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}',
                         save_name=f'docdb-48750/helicalc_standard_PINN_Rebar{noise_str}',
                         recreate=True)
# test
cfg_pickle_test2 = cfg_pickle(use_pickle=True, save_pickle=False,
                              load_name=f'docdb-48750/helicalc_standard_PINN_Rebar{noise_str}',
                              save_name=f'docdb-48750/helicalc_standard_PINN_Rebar{noise_str}', recreate=True)
# PINN subracted fit
cfg_pickle_ps2 = cfg_pickle(use_pickle=True, save_pickle=True,
                         # FIXME! There's a bug with loading params, recreate, then
                         # running when loading the params again
                         #load_name=f'docdb-48750/helicalc_standard_PINN_Rebar{noise_str}',
                         # using params1 as a starting point, because it is equivalent
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}',
                         save_name=f'docdb-48750/helicalc_standard_PINN_Rebar{noise_str}_PINN_subtracted', recreate=False)
# test, PINN subtracted
cfg_pickle_ps_test2 = cfg_pickle(use_pickle=True, save_pickle=False,
                                 load_name=f'docdb-48750/helicalc_standard_PINN_Rebar{noise_str}_PINN_subtracted',
                                 save_name=f'docdb-48750/helicalc_standard_PINN_Rebar{noise_str}_PINN_subtracted', recreate=True)

#### Fit 3. external points fit ####
# data
cfg_data3 = cfg_data('helicalc', 'DS', mapfile_3,
                     ('Z > 4.200', 'Z < 13.900'))
# PINN subtracted
n = LSQ_config_dict_minimal['3']['fitnames']['Initial']
mapfile_ps3 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_external_fit_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps3 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps3 = cfg_data('helicalc', 'DS', mapfile_ps3,
                        ('Z > 4.200', 'Z < 13.900'))
cfg_data_test_ps3 = cfg_data('helicalc', 'DS', mapfile_test_ps3,
                             ('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
# params
# cfg_params3 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
#                          length1=12.5, ms_c1=70, ns_c1=7, length2=0, ms_c2=0, ns_c2=0,
#                          ks_dict={'k1': [mean_fields_dict['nominal']['Bx'], False],
#                                   'k2': [mean_fields_dict['nominal']['By'], False],
#                                   'k3': [mean_fields_dict['nominal']['Bz'], False],
#                                   'k4': [0., True], 'k5': [0., False],
#                                   'k6': [0., False], 'k7': [0., True],},
#                          bs_tuples=None, bs_bounds=None,
#                          loss='linear', method='leastsq',
#                          ms_asym_max=10,
#                          version=1006,
#                          noise=noise, z0=z0, AB_lim=None, k_lim=None)
## FIXME! This is just for testing various parameter configurations for PINN paper
cfg_params3 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         # length1=12.5, ms_c1=70, ns_c1=7, length2=0, ms_c2=0, ns_c2=0, # v1008, chi2=8.9
                         #length1=12.5, ms_c1=70, ns_c1=7, length2=0, ms_c2=0, ns_c2=0, # v1008, chi2=2.1
                         #length1=12.5, ms_c1=50, ns_c1=10, length2=0, ms_c2=0, ns_c2=0, # v1008, chi2=
                         #length1=12.5, ms_c1=50, ns_c1=5, length2=0, ms_c2=0, ns_c2=0,
                         #length1=12.5, ms_c1=70, ns_c1=8, length2=0, ms_c2=0, ns_c2=0,
                         length1=13.850 - 4.215 + 3.3, ms_c1=30, ns_c1=2, length2=0, ms_c2=0, ns_c2=0,
                         # length1=12.5, ms_c1=70, ns_c1=1, length2=0, ms_c2=0, ns_c2=0,
                         # ks_dict={'k1': [mean_fields_dict['nominal']['Bx'], True],
                         #          'k2': [mean_fields_dict['nominal']['By'], True],
                         #          'k3': [mean_fields_dict['nominal']['Bz'], False],
                         #          'k4': [0., True], 'k5': [0., True],
                         #          'k6': [0., True], 'k7': [0., True],},
                         # no ks, all zero
                         ks_dict={'k1': [0., False],
                                  'k2': [0., False],
                                  'k3': [0., False],
                                  'k4': [0., False], 'k5': [0., False],
                                  'k6': [0., False], 'k7': [0., False],},
                         bs_tuples=None, bs_bounds=None,
                         # loss='linear', method='leastsq', # lm
                         loss='linear', method='least_squares', # trf
                         # loss='linear', method='newton', # newton-cg -- jac required
                         # loss='linear', method='cg', # cg -- extremely slow convergence
                         # ms_asym_max=10, # v1008, chi2=8.9
                         #ms_asym_max=15,
                         # ms_asym_max=20,
                         #ms_asym_max=30, # v1008, chi2=2.
                         # ms_asym_max=60,
                         ms_asym_max=-1,
                         #version=1006,
                         #version=1007,
                         version=1008,
                         # version=1009, # single unconstrained normalization, phases
                         # noise=noise, z0=z0, AB_lim=None, k_lim=None)
                         noise=noise, z0=4.215, AB_lim=None, k_lim=None)
# pickle
# first fit
cfg_pickle3 = cfg_pickle(use_pickle=False, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}_external_fit',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}_external_fit', recreate=False)
# test
cfg_pickle_test3 = cfg_pickle(use_pickle=True, save_pickle=False,
                              load_name=f'docdb-48750/helicalc_Rebar{noise_str}_external_fit',
                              save_name=f'docdb-48750/helicalc_Rebar{noise_str}_external_fit', recreate=True)
# PINN subracted fit
cfg_pickle_ps3 = cfg_pickle(use_pickle=True, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}_external_fit',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}_external_fit_PINN_subtracted', recreate=False)
# test, PINN subtracted
cfg_pickle_ps_test3 = cfg_pickle(use_pickle=True, save_pickle=False,
                                 load_name=f'docdb-48750/helicalc_Rebar{noise_str}_external_fit_PINN_subtracted',
                                 save_name=f'docdb-48750/helicalc_Rebar{noise_str}_external_fit_PINN_subtracted', recreate=True)

#### Fit 4. phony curled field injected ####
# data
cfg_data4 = cfg_data('helicalc', 'DS', mapfile_4,
                     ('Z > 4.200', 'Z < 13.900'))
# PINN subtracted
n = LSQ_config_dict_minimal['4']['fitnames']['Initial']
mapfile_ps4 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}{phony_curl_str}_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps4 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps4 = cfg_data('helicalc', 'DS', mapfile_ps4,
                        ('Z > 4.200', 'Z < 13.900'))
cfg_data_test_ps4 = cfg_data('helicalc', 'DS', mapfile_test_ps4,
                             ('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
# params
# with ASYM
# cfg_params4 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
#                          length1=12.5, ms_c1=70, ns_c1=7, length2=0, ms_c2=0, ns_c2=0,
#                          ks_dict={'k1': [mean_fields_dict['phony_curl']['Bx'], False],
#                                   'k2': [mean_fields_dict['phony_curl']['By'], False],
#                                   'k3': [mean_fields_dict['phony_curl']['Bz'], False],
#                                   'k4': [0., True], 'k5': [0., False],
#                                   'k6': [0., False], 'k7': [0., True],},
#                          bs_tuples=None, bs_bounds=None,
#                          loss='linear', method='leastsq',
#                          ms_asym_max=10,
#                          version=1006,
#                          noise=noise, z0=z0, AB_lim=None, k_lim=None)
## FIXME! This is just for testing various parameter configurations for PINN paper
cfg_params4 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         length1=12.5, ms_c1=55, ns_c1=7, length2=0, ms_c2=0, ns_c2=0, # with asymm
                         # length1=12.5, ms_c1=55, ns_c1=1, length2=0, ms_c2=0, ns_c2=0, # without asymm
                         ks_dict={'k1': [mean_fields_dict['nominal']['Bx'], True],
                                  'k2': [mean_fields_dict['nominal']['By'], True],
                                  'k3': [mean_fields_dict['nominal']['Bz'], False],
                                  'k4': [0., True], 'k5': [0., True],
                                  'k6': [0., True], 'k7': [0., True],},
                         # all ks or
                         # no ks, all zero
                         # ks_dict={'k1': [0., True],
                         #          'k2': [0., True],
                         #          'k3': [0., False],
                         #          'k4': [0., True], 'k5': [0., True],
                         #          'k6': [0., True], 'k7': [0., True],},
                         bs_tuples=None, bs_bounds=None,
                         loss='linear', method='leastsq', # lm
                         # loss='linear', method='least_squares', # trf
                         ms_asym_max=-1,
                         version=1008,
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)
# SYM only
# cfg_params4 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
#                          length1=12.5, ms_c1=70, ns_c1=1, length2=0, ms_c2=0, ns_c2=0,
#                          ks_dict={'k1': [mean_fields_dict['phony_curl']['Bx'], False],
#                                   'k2': [mean_fields_dict['phony_curl']['By'], False],
#                                   'k3': [mean_fields_dict['phony_curl']['Bz'], False],
#                                   'k4': [0., True], 'k5': [0., True],
#                                   'k6': [0., True], 'k7': [0., True],},
#                          bs_tuples=None, bs_bounds=None,
#                          loss='linear', method='leastsq',
#                          ms_asym_max=-1,
#                          version=1006,
#                          noise=noise, z0=z0, AB_lim=None, k_lim=None)
# pickle
# first fit
cfg_pickle4 = cfg_pickle(use_pickle=False, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}{phony_curl_str}',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}{phony_curl_str}', recreate=False)
# test
cfg_pickle_test4 = cfg_pickle(use_pickle=True, save_pickle=False,
                              load_name=f'docdb-48750/helicalc_Rebar{noise_str}{phony_curl_str}',
                              save_name=f'docdb-48750/helicalc_Rebar{noise_str}{phony_curl_str}', recreate=True)
# PINN subracted fit
cfg_pickle_ps4 = cfg_pickle(use_pickle=True, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}{phony_curl_str}',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}{phony_curl_str}_PINN_subtracted', recreate=False)
                         # save_name=f'docdb-48750/helicalc_Rebar{noise_str}{phony_curl_str}_PINN_subtracted', recreate=True) # CAUTION! Just a test.
# test, PINN subtracted
cfg_pickle_ps_test4 = cfg_pickle(use_pickle=True, save_pickle=False,
                                 load_name=f'docdb-48750/helicalc_Rebar{noise_str}{phony_curl_str}_PINN_subtracted',
                                 save_name=f'docdb-48750/helicalc_Rebar{noise_str}{phony_curl_str}_PINN_subtracted', recreate=True)

#### Fit 5. nominal, with a minimal set of LSQ parameters ####
# data
cfg_data5 = cfg_data('helicalc', 'DS', mapfile_125,
                     #('Z > 4.200', 'Z < 13.900'))
                     ('Z >= 4.25', 'Z <= 13.85'))
# PINN subtracted
n = LSQ_config_dict_minimal['5']['fitnames']['Initial']
mapfile_ps5 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps5 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps5 = cfg_data('helicalc', 'DS', mapfile_ps5,
                        #('Z > 4.200', 'Z < 13.900'))
                        ('Z >= 4.25', 'Z <= 13.85'))
cfg_data_test_ps5 = cfg_data('helicalc', 'DS', mapfile_test_ps5,
                             #('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
                             ('Z >= 4.25', 'Z <= 13.85', 'R <= 0.800'))
# params
# cfg_params5 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
#                          length1=12.5, ms_c1=70, ns_c1=1, length2=0, ms_c2=0, ns_c2=0,
#                          ks_dict={'k1': [mean_fields_dict['nominal']['Bx'], False],
#                                   'k2': [mean_fields_dict['nominal']['By'], False],
#                                   'k3': [mean_fields_dict['nominal']['Bz'], False],
#                                   'k4': [0., True], 'k5': [0., True],
#                                   'k6': [0., True], 'k7': [0., True],},
#                          bs_tuples=None, bs_bounds=None,
#                          loss='linear', method='leastsq',
#                          ms_asym_max=-1,
#                          version=1006,
#                          noise=noise, z0=z0, AB_lim=None, k_lim=None)
## FIXME! This is just for testing various parameter configurations for PINN paper
cfg_params5 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         #length1=12.5, # nominal
                         # testing length limits
                         #length1=9.6, # exact data length --> bad
                         length1=10.0, # adjust
                         ###ms_c1=60, ns_c1=1, length2=0, ms_c2=0, ns_c2=0, # orig minimal
                         ###ms_c1=55, ns_c1=1, length2=0, ms_c2=0, ns_c2=0,
                         ms_c1=55, ns_c1=7, length2=0, ms_c2=0, ns_c2=0, # test with nominal, large L
                         # length1=14.0, ms_c1=65, ns_c1=1, length2=0, ms_c2=0, ns_c2=0,
                         ks_dict={'k1': [mean_fields_dict['nominal']['Bx'], True],
                                  'k2': [mean_fields_dict['nominal']['By'], True],
                                  'k3': [mean_fields_dict['nominal']['Bz'], False],
                                  'k4': [0., True], 'k5': [0., True],
                                  'k6': [0., True], 'k7': [0., True],},
                         # all ks or
                         # no ks, all zero
                         # ks_dict={'k1': [0., True],
                         #          'k2': [0., True],
                         #          'k3': [0., False],
                         #          'k4': [0., True], 'k5': [0., True],
                         #          'k6': [0., True], 'k7': [0., True],},
                         bs_tuples=None, bs_bounds=None,
                         loss='linear', method='leastsq', # lm
                         # loss='linear', method='least_squares', # trf
                         ms_asym_max=-1,
                         version=1008,
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)
                         # noise=noise, z0=4.215, AB_lim=None, k_lim=None)
# pickle
# first fit
cfg_pickle5 = cfg_pickle(use_pickle=False, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}_CylSym_fit',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}_CylSym_fit',
                         recreate=False)
# test
cfg_pickle_test5 = cfg_pickle(use_pickle=True, save_pickle=False,
                              load_name=f'docdb-48750/helicalc_Rebar{noise_str}_CylSym_fit',
                              save_name=f'docdb-48750/helicalc_Rebar{noise_str}_CylSym_fit', recreate=True)
# PINN subracted fit
cfg_pickle_ps5 = cfg_pickle(use_pickle=True, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}_CylSym_fit',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}_CylSym_fit_PINN_subtracted', recreate=False)
# test, PINN subtracted
cfg_pickle_ps_test5 = cfg_pickle(use_pickle=True, save_pickle=False,
                                 load_name=f'docdb-48750/helicalc_Rebar{noise_str}_CylSym_fit_PINN_subtracted',
                                 save_name=f'docdb-48750/helicalc_Rebar{noise_str}_CylSym_fit_PINN_subtracted', recreate=True)

#### Fit 6. bus bars only (with connectors). includes noise ####
# data
cfg_data6 = cfg_data('helicalc', 'DS', mapfile_6,
                     ('Z > 4.200', 'Z < 13.900'))
mapfile_test6 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_No_Coils_All_Busbars.Mu2E.p'
cfg_data_test6 = cfg_data('helicalc', 'DS', mapfile_test6,
                         ('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
# PINN subtracted
n = LSQ_config_dict_minimal['6']['fitnames']['Initial']
mapfile_ps6 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_No_Coils_All_Busbars{noise_str}_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps6 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_No_Coils_All_Busbars_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps6 = cfg_data('helicalc', 'DS', mapfile_ps6,
                        ('Z > 4.200', 'Z < 13.900'))
cfg_data_test_ps6 = cfg_data('helicalc', 'DS', mapfile_test_ps6,
                             ('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
# params
cfg_params6 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         # cyl asym
                         length1=12.5, ms_c1=70, ns_c1=7, length2=0, ms_c2=0, ns_c2=0,
                         # cyl sym
                         #length1=12.5, ms_c1=40, ns_c1=1, length2=0, ms_c2=0, ns_c2=0,
                         # no cyl
                         #length1=0, ms_c1=0, ns_c1=0, length2=0, ms_c2=0, ns_c2=0,
                         ks_dict={'k1': [mean_fields_dict['busbars']['Bx'], False],
                                  'k2': [mean_fields_dict['busbars']['By'], False],
                                  'k3': [mean_fields_dict['busbars']['Bz'], False],
                                  # standard vary
                                  'k4': [0., True], 'k5': [0., False],
                                  'k6': [0., False], 'k7': [0., True],},
                                  # vary all
                                  #'k4': [0., True], 'k5': [0., True],
                                  #'k6': [0., True], 'k7': [0., True],},
                                  # nothing varying
                                  # 'k4': [0., False], 'k5': [0., False],
                                  # 'k6': [0., False], 'k7': [0., False],},
                         bs_tuples=None, bs_bounds=None,
                         loss='linear', method='leastsq',
                         ms_asym_max=10,
                         version=1006,
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)
# pickle
# first fit
cfg_pickle6 = cfg_pickle(use_pickle=False, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Busbars{noise_str}',
                         save_name=f'docdb-48750/helicalc_Busbars{noise_str}', recreate=False)
# test
cfg_pickle_test6 = cfg_pickle(use_pickle=True, save_pickle=False,
                              load_name=f'docdb-48750/helicalc_Busbars{noise_str}',
                              save_name=f'docdb-48750/helicalc_Busbars{noise_str}', recreate=True)
# PINN subracted fit
cfg_pickle_ps6 = cfg_pickle(use_pickle=True, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Busbars{noise_str}',
                         save_name=f'docdb-48750/helicalc_Busbars{noise_str}_PINN_subtracted', recreate=False)
# test, PINN subtracted
cfg_pickle_ps_test6 = cfg_pickle(use_pickle=True, save_pickle=False,
                                 load_name=f'docdb-48750/helicalc_Busbars{noise_str}_PINN_subtracted',
                                 save_name=f'docdb-48750/helicalc_Busbars{noise_str}_PINN_subtracted', recreate=True)

#### Fit 7. DS coils only (with connectors). includes noise ####
# data
cfg_data7 = cfg_data('helicalc', 'DS', mapfile_7,
                     ('Z > 4.200', 'Z < 13.900'))
mapfile_test7 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_No_Busbars.Mu2E.p'
cfg_data_test7 = cfg_data('helicalc', 'DS', mapfile_test7,
                         ('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
# PINN subtracted
n = LSQ_config_dict_minimal['7']['fitnames']['Initial']
mapfile_ps7 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_No_Busbars{noise_str}_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps7 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_No_Busbars_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps7 = cfg_data('helicalc', 'DS', mapfile_ps7,
                        ('Z > 4.200', 'Z < 13.900'))
cfg_data_test_ps7 = cfg_data('helicalc', 'DS', mapfile_test_ps7,
                             ('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
# params
cfg_params7 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         # cyl asym
                         length1=12.5, ms_c1=70, ns_c1=7, length2=0, ms_c2=0, ns_c2=0,
                         # cyl sym
                         #length1=12.5, ms_c1=40, ns_c1=1, length2=0, ms_c2=0, ns_c2=0,
                         # no cyl
                         #length1=0, ms_c1=0, ns_c1=0, length2=0, ms_c2=0, ns_c2=0,
                         ks_dict={'k1': [mean_fields_dict['DSCoils']['Bx'], False],
                                  'k2': [mean_fields_dict['DSCoils']['By'], False],
                                  'k3': [mean_fields_dict['DSCoils']['Bz'], False],
                                  # standard vary
                                  'k4': [0., True], 'k5': [0., False],
                                  'k6': [0., False], 'k7': [0., True],},
                                  # vary all
                                  #'k4': [0., True], 'k5': [0., True],
                                  #'k6': [0., True], 'k7': [0., True],},
                                  # nothing varying
                                  # 'k4': [0., False], 'k5': [0., False],
                                  # 'k6': [0., False], 'k7': [0., False],},
                         bs_tuples=None, bs_bounds=None,
                         loss='linear', method='leastsq',
                         ms_asym_max=10,
                         version=1006,
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)
# pickle
# first fit
cfg_pickle7 = cfg_pickle(use_pickle=False, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_DSCoils{noise_str}',
                         save_name=f'docdb-48750/helicalc_DSCoils{noise_str}', recreate=False)
# test
cfg_pickle_test7 = cfg_pickle(use_pickle=True, save_pickle=False,
                              load_name=f'docdb-48750/helicalc_DSCoils{noise_str}',
                              save_name=f'docdb-48750/helicalc_DSCoils{noise_str}', recreate=True)
# PINN subracted fit
cfg_pickle_ps7 = cfg_pickle(use_pickle=True, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_DSCoils{noise_str}',
                         save_name=f'docdb-48750/helicalc_DSCoils{noise_str}_PINN_subtracted', recreate=False)
# test, PINN subtracted
cfg_pickle_ps_test7 = cfg_pickle(use_pickle=True, save_pickle=False,
                                 load_name=f'docdb-48750/helicalc_DSCoils{noise_str}_PINN_subtracted',
                                 save_name=f'docdb-48750/helicalc_DSCoils{noise_str}_PINN_subtracted', recreate=True)

#### Fit 8. Hall probe calibration magnitude systematic. includes noise ####
# data
cfg_data8 = cfg_data('helicalc', 'DS', mapfile_8,
                     ('Z >= 4.25', 'Z <= 13.85'))
# PINN subtracted
n = LSQ_config_dict_minimal['8']['fitnames']['Initial']
mapfile_ps8 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_HPCMagUnc_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps8 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps8 = cfg_data('helicalc', 'DS', mapfile_ps8,
                        ('Z >= 4.25', 'Z <= 13.85'))
cfg_data_test_ps8 = cfg_data('helicalc', 'DS', mapfile_test_ps8,
                             ('Z >= 4.25', 'Z <= 13.85', 'R <= 0.800'))
# params
cfg_params8 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         length1=12.5, ms_c1=55, ns_c1=7, length2=0, ms_c2=0, ns_c2=0,
                         ks_dict={'k1': [mean_fields_dict['HPCMagUnc']['Bx'], True],
                                  'k2': [mean_fields_dict['HPCMagUnc']['By'], True],
                                  'k3': [mean_fields_dict['HPCMagUnc']['Bz'], False],
                                  'k4': [0., True], 'k5': [0., True],
                                  'k6': [0., True], 'k7': [0., True],},
                         bs_tuples=None, bs_bounds=None,
                         loss='linear', method='leastsq', # lm
                         # loss='linear', method='least_squares', # trf
                         ms_asym_max=-1,
                         version=1008,
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)
# pickle
# first fit
cfg_pickle8 = cfg_pickle(use_pickle=False, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc', recreate=False)
# test
cfg_pickle_test8 = cfg_pickle(use_pickle=True, save_pickle=False,
                              load_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc',
                              save_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc', recreate=True)
# PINN subracted fit
cfg_pickle_ps8 = cfg_pickle(use_pickle=True, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc_PINN_subtracted', recreate=False)
# test, PINN subtracted
cfg_pickle_ps_test8 = cfg_pickle(use_pickle=True, save_pickle=False,
                                 load_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc_PINN_subtracted',
                                 save_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc_PINN_subtracted', recreate=True)

#### Fit 9. Sparser Z and Phi ####
# data
cfg_data9 = cfg_data('helicalc', 'DS', mapfile_9,
                     ('Z >= 4.25', 'Z <= 13.85'))
# PINN subtracted
n = LSQ_config_dict_minimal['9']['fitnames']['Initial']
mapfile_ps9 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_SparseZPhi_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps9 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps9 = cfg_data('helicalc', 'DS', mapfile_ps9,
                        ('Z >= 4.25', 'Z <= 13.85'))
cfg_data_test_ps9 = cfg_data('helicalc', 'DS', mapfile_test_ps9,
                             ('Z >= 4.25', 'Z <= 13.85', 'R <= 0.800'))
# params
cfg_params9 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         #length1=12.5, ms_c1=55, ns_c1=7, length2=0, ms_c2=0, ns_c2=0,
                         length1=12.5, ms_c1=55, ns_c1=3, length2=0, ms_c2=0, ns_c2=0, # with limited Z and Phi (x1/2 in both)
                         ks_dict={'k1': [mean_fields_dict['nominal']['Bx'], True],
                                  'k2': [mean_fields_dict['nominal']['By'], True],
                                  'k3': [mean_fields_dict['nominal']['Bz'], False],
                                  'k4': [0., True], 'k5': [0., True],
                                  'k6': [0., True], 'k7': [0., True],},
                         bs_tuples=None, bs_bounds=None,
                         loss='linear', method='leastsq', # lm
                         # loss='linear', method='least_squares', # trf
                         ms_asym_max=-1,
                         version=1008,
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)
# pickle
# first fit
cfg_pickle9 = cfg_pickle(use_pickle=False, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}_SparseZPhi',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}_SparseZPhi', recreate=False)
# test
cfg_pickle_test9 = cfg_pickle(use_pickle=True, save_pickle=False,
                              load_name=f'docdb-48750/helicalc_Rebar{noise_str}_SparseZPhi',
                              save_name=f'docdb-48750/helicalc_Rebar{noise_str}_SparseZPhi', recreate=True)
# PINN subracted fit
cfg_pickle_ps9 = cfg_pickle(use_pickle=True, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}_SparseZPhi',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}_SparseZPhi_PINN_subtracted', recreate=False)
# test, PINN subtracted
cfg_pickle_ps_test9 = cfg_pickle(use_pickle=True, save_pickle=False,
                                 load_name=f'docdb-48750/helicalc_Rebar{noise_str}_SparseZPhi_PINN_subtracted',
                                 save_name=f'docdb-48750/helicalc_Rebar{noise_str}_SparseZPhi_PINN_subtracted', recreate=True)

#### Fit 10. Hall probe calibration magnitude systematic with Sparser Z and Phi ####
# data
cfg_data10 = cfg_data('helicalc', 'DS', mapfile_10,
                     ('Z >= 4.25', 'Z <= 13.85'))
# PINN subtracted
n = LSQ_config_dict_minimal['10']['fitnames']['Initial']
mapfile_ps10 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_HPCMagUnc_SparseZPhi_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps10 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps10 = cfg_data('helicalc', 'DS', mapfile_ps10,
                        ('Z >= 4.25', 'Z <= 13.85'))
cfg_data_test_ps10 = cfg_data('helicalc', 'DS', mapfile_test_ps10,
                             ('Z >= 4.25', 'Z <= 13.85', 'R <= 0.800'))
# params
cfg_params10 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         #length1=12.5, ms_c1=55, ns_c1=7, length2=0, ms_c2=0, ns_c2=0,
                         length1=12.5, ms_c1=55, ns_c1=3, length2=0, ms_c2=0, ns_c2=0, # with limited Z and Phi (x1/2 in both)
                         ks_dict={'k1': [mean_fields_dict['HPCMagUnc']['Bx'], True],
                                  'k2': [mean_fields_dict['HPCMagUnc']['By'], True],
                                  'k3': [mean_fields_dict['HPCMagUnc']['Bz'], False],
                                  'k4': [0., True], 'k5': [0., True],
                                  'k6': [0., True], 'k7': [0., True],},
                         bs_tuples=None, bs_bounds=None,
                         loss='linear', method='leastsq', # lm
                         # loss='linear', method='least_squares', # trf
                         ms_asym_max=-1,
                         version=1008,
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)
# pickle
# first fit
cfg_pickle10 = cfg_pickle(use_pickle=False, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc_SparseZPhi',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc_SparseZPhi', recreate=False)
# test
cfg_pickle_test10 = cfg_pickle(use_pickle=True, save_pickle=False,
                              load_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc_SparseZPhi',
                              save_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc_SparseZPhi', recreate=True)
# PINN subracted fit
cfg_pickle_ps10 = cfg_pickle(use_pickle=True, save_pickle=True,
                         load_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc_SparseZPhi',
                         save_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc_SparseZPhi_PINN_subtracted', recreate=False)
# test, PINN subtracted
cfg_pickle_ps_test10 = cfg_pickle(use_pickle=True, save_pickle=False,
                                 load_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc_SparseZPhi_PINN_subtracted',
                                 save_name=f'docdb-48750/helicalc_Rebar{noise_str}_HPCMagUnc_SparseZPhi_PINN_subtracted', recreate=True)

#### Fit 1 toys ####
cfg_tuple_toys_dict = {}
for toy_num in range(N_toys_nominal-1):
    model_num = f'1_toy_{toy_num}'
    # data
    cfg_data_ = cfg_data('helicalc', 'DS', mapfile_1_toys[model_num],
                         #('Z > 4.200', 'Z < 13.900'))
                         ('Z >= 4.25', 'Z <= 13.85')) # fix to use BP at upstream end
    # PINN subtracted
    n = LSQ_config_dict_minimal[model_num]['fitnames']['Initial']
    mapfile_ps_ = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_toy_{toy_num}_{n}_PINN_Subtracted.Mu2E.p'
    mapfile_test_ps_ = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
    cfg_data_ps_ = cfg_data('helicalc', 'DS', mapfile_ps_,
                            #('Z > 4.200', 'Z < 13.900'))
                            ('Z >= 4.25', 'Z <= 13.85'))
    cfg_data_test_ps_ = cfg_data('helicalc', 'DS', mapfile_test_ps_,
                                 #('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
                                 ('Z >= 4.25', 'Z <= 13.85', 'R <= 0.800'))
    # params
    cfg_params_ = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                             length1=12.5, ms_c1=55, ns_c1=7, length2=0, ms_c2=0, ns_c2=0, # GOOD! Nominal fit, nominal set of data
                             ks_dict={'k1': [mean_fields_dict[model_num]['Bx'], True],
                                      'k2': [mean_fields_dict[model_num]['By'], True],
                                      'k3': [mean_fields_dict[model_num]['Bz'], False],
                                      'k4': [0., True], 'k5': [0., True],
                                      'k6': [0., True], 'k7': [0., True],},
                             bs_tuples=None, bs_bounds=None,
                             loss='linear', method='leastsq', # lm
                             ms_asym_max=-1, # NOMINAL
                             version=1008, # FOR PAPER
                             noise=noise, z0=z0, AB_lim=None, k_lim=None)
    # pickle
    # first fit
    cfg_pickle_ = cfg_pickle(use_pickle=False, save_pickle=True,
                             load_name=f'docdb-48750/helicalc_Rebar{noise_str}_toy_{toy_num}',
                             save_name=f'docdb-48750/helicalc_Rebar{noise_str}_toy_{toy_num}', recreate=False)
    # test
    cfg_pickle_test_ = cfg_pickle(use_pickle=True, save_pickle=False,
                                  load_name=f'docdb-48750/helicalc_Rebar{noise_str}_toy_{toy_num}',
                                  save_name=f'docdb-48750/helicalc_Rebar{noise_str}_toy_{toy_num}', recreate=True)
    # PINN subracted fit
    cfg_pickle_ps_ = cfg_pickle(use_pickle=True, save_pickle=True,
                             load_name=f'docdb-48750/helicalc_Rebar{noise_str}_toy_{toy_num}',
                             save_name=f'docdb-48750/helicalc_Rebar{noise_str}_toy_{toy_num}_PINN_subtracted', recreate=False)
    # test, PINN subtracted
    cfg_pickle_ps_test_ = cfg_pickle(use_pickle=True, save_pickle=False,
                                     load_name=f'docdb-48750/helicalc_Rebar{noise_str}_toy_{toy_num}_PINN_subtracted',
                                     save_name=f'docdb-48750/helicalc_Rebar{noise_str}_toy_{toy_num}_PINN_subtracted', recreate=True)
    cfg_tuple_toys_dict[model_num] = {
        'cfg_data': cfg_data_,
        # 'mapfile_ps': mapfile_ps_,
        # 'mapfile_test_ps': mapfile_test_ps_,
        'cfg_data_ps': cfg_data_ps_,
        'cfg_data_test_ps': cfg_data_test_ps_,
        'cfg_params': cfg_params_,
        'cfg_pickle': cfg_pickle_,
        'cfg_pickle_test': cfg_pickle_test_,
        'cfg_pickle_ps': cfg_pickle_ps_,
        #'cfg_pickle_ps_test': cfg_pickle_ps_test_,
        'cfg_pickle_test_ps': cfg_pickle_ps_test_,
    }

#### Collect them all into a dictionary
Lmin = LSQ_config_dict_minimal
LSQ_config_dict = {
    '1': {'subdir': Lmin['1']['subdir'], 'fitnames': Lmin['1']['fitnames'],
          'cfg_data': cfg_data1, 'cfg_data_test': cfg_data_test,
          'cfg_data_ps': cfg_data_ps1, 'cfg_data_test_ps': cfg_data_test_ps1,
          'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,
          'cfg_params': cfg_params1, 'cfg_pickle': cfg_pickle1,
          'cfg_pickle_test': cfg_pickle_test1, 'cfg_pickle_ps': cfg_pickle_ps1,
          'cfg_pickle_test_ps': cfg_pickle_ps_test1},
    '2': {'subdir': Lmin['2']['subdir'], 'fitnames': Lmin['2']['fitnames'],
          'cfg_data': cfg_data2, 'cfg_data_test': cfg_data_test,
          'cfg_data_ps': cfg_data_ps2, 'cfg_data_test_ps': cfg_data_test_ps2,
          'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,
          'cfg_params': cfg_params2, 'cfg_pickle': cfg_pickle2,
          'cfg_pickle_test': cfg_pickle_test2, 'cfg_pickle_ps': cfg_pickle_ps2,
          'cfg_pickle_test_ps': cfg_pickle_ps_test2},
    '3': {'subdir': Lmin['3']['subdir'], 'fitnames': Lmin['3']['fitnames'],
          'cfg_data': cfg_data3, 'cfg_data_test': cfg_data_test,
          'cfg_data_ps': cfg_data_ps3, 'cfg_data_test_ps': cfg_data_test_ps3,
          'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,
          'cfg_params': cfg_params3, 'cfg_pickle': cfg_pickle3,
          'cfg_pickle_test': cfg_pickle_test3, 'cfg_pickle_ps': cfg_pickle_ps3,
          'cfg_pickle_test_ps': cfg_pickle_ps_test3},
    '4': {'subdir': Lmin['4']['subdir'], 'fitnames': Lmin['4']['fitnames'],
          'cfg_data': cfg_data4, 'cfg_data_test': cfg_data_test,
          'cfg_data_ps': cfg_data_ps4, 'cfg_data_test_ps': cfg_data_test_ps4,
          'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,
          'cfg_params': cfg_params4, 'cfg_pickle': cfg_pickle4,
          'cfg_pickle_test': cfg_pickle_test4, 'cfg_pickle_ps': cfg_pickle_ps4,
          'cfg_pickle_test_ps': cfg_pickle_ps_test4},
    '5': {'subdir': Lmin['5']['subdir'], 'fitnames': Lmin['5']['fitnames'],
          'cfg_data': cfg_data5, 'cfg_data_test': cfg_data_test,
          'cfg_data_ps': cfg_data_ps5, 'cfg_data_test_ps': cfg_data_test_ps5,
          'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,
          'cfg_params': cfg_params5, 'cfg_pickle': cfg_pickle5,
          'cfg_pickle_test': cfg_pickle_test5, 'cfg_pickle_ps': cfg_pickle_ps5,
          'cfg_pickle_test_ps': cfg_pickle_ps_test5},
    '6': {'subdir': Lmin['6']['subdir'], 'fitnames': Lmin['6']['fitnames'],
          'cfg_data': cfg_data6, 'cfg_data_test': cfg_data_test6,
          'cfg_data_ps': cfg_data_ps6, 'cfg_data_test_ps': cfg_data_test_ps6,
          'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,
          'cfg_params': cfg_params6, 'cfg_pickle': cfg_pickle6,
          'cfg_pickle_test': cfg_pickle_test6, 'cfg_pickle_ps': cfg_pickle_ps6,
          'cfg_pickle_test_ps': cfg_pickle_ps_test6},
    '7': {'subdir': Lmin['7']['subdir'], 'fitnames': Lmin['7']['fitnames'],
          'cfg_data': cfg_data7, 'cfg_data_test': cfg_data_test7,
          'cfg_data_ps': cfg_data_ps7, 'cfg_data_test_ps': cfg_data_test_ps7,
          'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,
          'cfg_params': cfg_params7, 'cfg_pickle': cfg_pickle7,
          'cfg_pickle_test': cfg_pickle_test7, 'cfg_pickle_ps': cfg_pickle_ps7,
          'cfg_pickle_test_ps': cfg_pickle_ps_test7},
    '8': {'subdir': Lmin['8']['subdir'], 'fitnames': Lmin['8']['fitnames'],
          'cfg_data': cfg_data8, 'cfg_data_test': cfg_data_test,
          'cfg_data_ps': cfg_data_ps8, 'cfg_data_test_ps': cfg_data_test_ps8,
          'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,
          'cfg_params': cfg_params8, 'cfg_pickle': cfg_pickle8,
          'cfg_pickle_test': cfg_pickle_test8, 'cfg_pickle_ps': cfg_pickle_ps8,
          'cfg_pickle_test_ps': cfg_pickle_ps_test8},
    '9': {'subdir': Lmin['9']['subdir'], 'fitnames': Lmin['9']['fitnames'],
          'cfg_data': cfg_data9, 'cfg_data_test': cfg_data_test,
          'cfg_data_ps': cfg_data_ps9, 'cfg_data_test_ps': cfg_data_test_ps9,
          'cfg_geom_fit': cfg_geom_cyl_half, 'cfg_geom_test': cfg_geom_cart,
          'cfg_params': cfg_params9, 'cfg_pickle': cfg_pickle9,
          'cfg_pickle_test': cfg_pickle_test9, 'cfg_pickle_ps': cfg_pickle_ps9,
          'cfg_pickle_test_ps': cfg_pickle_ps_test9},
    '10': {'subdir': Lmin['10']['subdir'], 'fitnames': Lmin['10']['fitnames'],
          'cfg_data': cfg_data10, 'cfg_data_test': cfg_data_test,
          'cfg_data_ps': cfg_data_ps10, 'cfg_data_test_ps': cfg_data_test_ps10,
          'cfg_geom_fit': cfg_geom_cyl_half, 'cfg_geom_test': cfg_geom_cart,
          'cfg_params': cfg_params10, 'cfg_pickle': cfg_pickle10,
          'cfg_pickle_test': cfg_pickle_test10, 'cfg_pickle_ps': cfg_pickle_ps10,
          'cfg_pickle_test_ps': cfg_pickle_ps_test10},
}

# model 1 toys
for model_num, cd in cfg_tuple_toys_dict.items():
    d_ = {'subdir': Lmin[model_num]['subdir'], 'fitnames': Lmin[model_num]['fitnames'],
          'cfg_data_test': cfg_data_test, 'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,}
    for k, v in cd.items():
        d_[k] = v
    LSQ_config_dict[model_num] = d_

# add to model 1 for p_eff estimate
# FIXME! Be more careful about params -- don't want to overwrite these accidentally
#for i in range(N_opt_tests):
#    model_num = f'1_{i}'
for model_num in p_eff_dict.keys():
    i = model_num.split('_')[0]
    if i == '1':
        cd_ = cfg_data1
        cdt_ = cfg_data_test
        cdp_ = cfg_data_ps1
        cdtp_ = cfg_data_test_ps1
        cp_ = cfg_params1
        cpi_ = cfg_pickle1
        cpit_ = cfg_pickle_test1
        cpip_ = cfg_pickle_ps1
        cpipt_ = cfg_pickle_ps_test1
    else:
        raise ValueError(f'The model_num "{model_num}" is not implemented yet. Please add it and try again.')
    # LSQ_config_dict[model_num] = {
    #     'subdir': Lmin[model_num]['subdir'], 'fitnames': Lmin[model_num]['fitnames'],
    #     'cfg_data': cfg_data1, 'cfg_data_test': cfg_data_test,
    #     'cfg_data_ps': cfg_data_ps1, 'cfg_data_test_ps': cfg_data_test_ps1,
    #     'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,
    #     'cfg_params': cfg_params1, 'cfg_pickle': cfg_pickle1,
    #     'cfg_pickle_test': cfg_pickle_test1, 'cfg_pickle_ps': cfg_pickle_ps1,
    #     'cfg_pickle_test_ps': cfg_pickle_ps_test1}
    LSQ_config_dict[model_num] = {
        'subdir': Lmin[model_num]['subdir'], 'fitnames': Lmin[model_num]['fitnames'],
        'cfg_data': cd_, 'cfg_data_test': cdt_,
        'cfg_data_ps': cdp_, 'cfg_data_test_ps': cdtp_,
        'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,
        'cfg_params': cp_, 'cfg_pickle': cpi_,
        'cfg_pickle_test': cpit_, 'cfg_pickle_ps': cpip_,
        'cfg_pickle_test_ps': cpipt_}

# add to model 1 for hyperparam opt
# FIXME! Be more careful about params -- don't want to overwrite these accidentally
#for i in range(N_opt_tests):
#    model_num = f'1_{i}'
for model_num in opt_dict.keys():
    i = model_num.split('_')[0]
    if i == '1':
        cd_ = cfg_data1
        cdt_ = cfg_data_test
        cdp_ = cfg_data_ps1
        cdtp_ = cfg_data_test_ps1
        cp_ = cfg_params1
        cpi_ = cfg_pickle1
        cpit_ = cfg_pickle_test1
        cpip_ = cfg_pickle_ps1
        cpipt_ = cfg_pickle_ps_test1
    elif i == '4':
        cd_ = cfg_data4
        cdt_ = cfg_data_test
        cdp_ = cfg_data_ps4
        cdtp_ = cfg_data_test_ps4
        cp_ = cfg_params4
        cpi_ = cfg_pickle4
        cpit_ = cfg_pickle_test4
        cpip_ = cfg_pickle_ps4
        cpipt_ = cfg_pickle_ps_test4
    elif i == '8':
        cd_ = cfg_data8
        cdt_ = cfg_data_test
        cdp_ = cfg_data_ps8
        cdtp_ = cfg_data_test_ps8
        cp_ = cfg_params8
        cpi_ = cfg_pickle8
        cpit_ = cfg_pickle_test8
        cpip_ = cfg_pickle_ps8
        cpipt_ = cfg_pickle_ps_test8
    elif i == '2':
        cd_ = cfg_data2
        cdt_ = cfg_data_test
        cdp_ = cfg_data_ps2
        cdtp_ = cfg_data_test_ps2
        cp_ = cfg_params2
        cpi_ = cfg_pickle2
        cpit_ = cfg_pickle_test2
        cpip_ = cfg_pickle_ps2
        cpipt_ = cfg_pickle_ps_test2
    else:
        raise ValueError(f'The model_num "{model_num}" is not implemented yet. Please add it and try again.')
    # LSQ_config_dict[model_num] = {
    #     'subdir': Lmin[model_num]['subdir'], 'fitnames': Lmin[model_num]['fitnames'],
    #     'cfg_data': cfg_data1, 'cfg_data_test': cfg_data_test,
    #     'cfg_data_ps': cfg_data_ps1, 'cfg_data_test_ps': cfg_data_test_ps1,
    #     'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,
    #     'cfg_params': cfg_params1, 'cfg_pickle': cfg_pickle1,
    #     'cfg_pickle_test': cfg_pickle_test1, 'cfg_pickle_ps': cfg_pickle_ps1,
    #     'cfg_pickle_test_ps': cfg_pickle_ps_test1}
    LSQ_config_dict[model_num] = {
        'subdir': Lmin[model_num]['subdir'], 'fitnames': Lmin[model_num]['fitnames'],
        'cfg_data': cd_, 'cfg_data_test': cdt_,
        'cfg_data_ps': cdp_, 'cfg_data_test_ps': cdtp_,
        'cfg_geom_fit': cfg_geom_cyl, 'cfg_geom_test': cfg_geom_cart,
        'cfg_params': cp_, 'cfg_pickle': cpi_,
        'cfg_pickle_test': cpit_, 'cfg_pickle_ps': cpip_,
        'cfg_pickle_test_ps': cpipt_}
