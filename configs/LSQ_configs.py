import os
import numpy as np
import pandas as pd
from mu2e import mu2e_ext_path
from mu2e.cfg_defs import cfg_data, cfg_geom, cfg_plot, cfg_params, cfg_pickle
from mean_fields import get_mean_fields_dict
from globals import noise, noise_str, phony_curl, phony_curl_str, z0, LSQ_config_dict_minimal

#### field map locations
# test / validation points (only one map)
mapfile_test = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar.Mu2E.p'
# fitting points
mapfile_125 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}.Mu2E.p'
mapfile_3 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_external_fit.Mu2E.p'
mapfile_4 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}{phony_curl_str}.Mu2E.p'
# calculate mean Bx, By, Bz (for params setup)
mean_fields_dict = get_mean_fields_dict({'nominal': mapfile_125, 'phony_curl': mapfile_4})
#### Shared tuples ####
# data
cfg_data_test = cfg_data('helicalc', 'DS', mapfile_test,
                         ('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
# geom
phi_steps = (0., 0.39269908, 0.78539816, 1.17809725, 1.57079633, 1.96349541,
             2.35619449, 2.74889357)
cfg_geom_cyl = cfg_geom('cyl', z_steps=None, r_steps=None, phi_steps=phi_steps,
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
                         version=1006,
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)

#### Model specific configurations
#### Fit 1. nominal ####
# data
cfg_data1 = cfg_data('helicalc', 'DS', mapfile_125,
                     ('Z > 4.200', 'Z < 13.900'))
# PINN subtracted
n = LSQ_config_dict_minimal['1']['fitnames']['Initial']
mapfile_ps1 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps1 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps1 = cfg_data('helicalc', 'DS', mapfile_ps1,
                        ('Z > 4.200', 'Z < 13.900'))
cfg_data_test_ps1 = cfg_data('helicalc', 'DS', mapfile_test_ps1,
                             ('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
# params
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
cfg_params2 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
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
                         load_name=f'docdb-48750/helicalc_standard_PINN_Rebar{noise_str}',
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
mapfile_ps3 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps3 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps3 = cfg_data('helicalc', 'DS', mapfile_ps3,
                        ('Z > 4.200', 'Z < 13.900'))
cfg_data_test_ps3 = cfg_data('helicalc', 'DS', mapfile_test_ps3,
                             ('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
# params
cfg_params3 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
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
mapfile_ps4 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps4 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps4 = cfg_data('helicalc', 'DS', mapfile_ps4,
                        ('Z > 4.200', 'Z < 13.900'))
cfg_data_test_ps4 = cfg_data('helicalc', 'DS', mapfile_test_ps4,
                             ('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
# params
cfg_params4 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         length1=12.5, ms_c1=70, ns_c1=7, length2=0, ms_c2=0, ns_c2=0,
                         ks_dict={'k1': [mean_fields_dict['phony_curl']['Bx'], False],
                                  'k2': [mean_fields_dict['phony_curl']['By'], False],
                                  'k3': [mean_fields_dict['phony_curl']['Bz'], False],
                                  'k4': [0., True], 'k5': [0., False],
                                  'k6': [0., False], 'k7': [0., True],},
                         bs_tuples=None, bs_bounds=None,
                         loss='linear', method='leastsq',
                         ms_asym_max=10,
                         version=1006,
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)
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
# test, PINN subtracted
cfg_pickle_ps_test4 = cfg_pickle(use_pickle=True, save_pickle=False,
                                 load_name=f'docdb-48750/helicalc_Rebar{noise_str}{phony_curl_str}_PINN_subtracted',
                                 save_name=f'docdb-48750/helicalc_Rebar{noise_str}{phony_curl_str}_PINN_subtracted', recreate=True)

#### Fit 5. nominal, with a minimal set of LSQ parameters ####
# data
cfg_data5 = cfg_data('helicalc', 'DS', mapfile_125,
                     ('Z > 4.200', 'Z < 13.900'))
# PINN subtracted
n = LSQ_config_dict_minimal['5']['fitnames']['Initial']
mapfile_ps5 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_All_Busbars_Rebar{noise_str}_{n}_PINN_Subtracted.Mu2E.p'
mapfile_test_ps5 = mu2e_ext_path+f'Bmaps/docdb-48750/Mu2e_V13_DSCartVal_Helicalc_All_Coils_All_Busbars_Rebar_{n}_PINN_Subtracted.Mu2E.p'
cfg_data_ps5 = cfg_data('helicalc', 'DS', mapfile_ps5,
                        ('Z > 4.200', 'Z < 13.900'))
cfg_data_test_ps5 = cfg_data('helicalc', 'DS', mapfile_test_ps5,
                             ('Z > 4.200', 'Z < 13.900', 'R <= 0.800'))
# params
cfg_params5 = cfg_params(pitch1=0, ms_h1=0, ns_h1=0, pitch2=0, ms_h2=0, ns_h2=0,
                         length1=12.5, ms_c1=70, ns_c1=1, length2=0, ms_c2=0, ns_c2=0,
                         ks_dict={'k1': [mean_fields_dict['nominal']['Bx'], False],
                                  'k2': [mean_fields_dict['nominal']['By'], False],
                                  'k3': [mean_fields_dict['nominal']['Bz'], False],
                                  'k4': [0., True], 'k5': [0., True],
                                  'k6': [0., True], 'k7': [0., True],},
                         bs_tuples=None, bs_bounds=None,
                         loss='linear', method='leastsq',
                         ms_asym_max=-1,
                         version=1006,
                         noise=noise, z0=z0, AB_lim=None, k_lim=None)
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
}
