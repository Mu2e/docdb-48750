import os
import sys
import argparse
import time
import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt

from BFieldPINN.plotter import(
    # utils
    check_plot_dir,
    config_plots,
    ticks_in,
    ticks_sizes,
    get_label,
    # plot functions
    create_dict_from_history,
    make_plots_history_vs_epoch,
    make_input_data_profile,
    make_Bi_residual_1D_hist,
    make_deriv_1D_hist,
    make_fit_data_profile,
    make_mu2e_plot3d,
    make_weights_and_biases_plot,
)
config_plots()
# configs
fpath = os.path.dirname(os.path.realpath(__file__))
configs_dir = os.path.abspath(os.path.join(fpath, '..', '..', 'configs'))
sys.path.append(configs_dir)
from model_globals import noise
from LSQ_configs import LSQ_config_dict
from PINN_configs import NN_config_dict, files_dict

if __name__=='__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-M', '--Model',
                        help='Which model do you want to fit? [1 (default), 2, 3, 4, 5, 6, 7]')
    args = parser.parse_args()
    # fill defaults if necessary
    if args.Model is None:
        args.Model = '1'
    t0 = time.time()
    model_num = args.Model
    if '_' in model_num:
        has_full = False
    else:
        has_full = True
    model_fname = files_dict[model_num]['model_fname']
    # load dataframes
    print(f"Loading dataframes, plotdirs, history for model {model_num}: {model_fname}...")
    if has_full:
        full = files_dict[model_num]['full']
        df_meas = pd.read_pickle(full['meas'])
        df_test = pd.read_pickle(full['test'])
    # HERE!
    # add df_test custom for the derivative plots
    save = files_dict[model_num]['save']
    df_meas_s = pd.read_pickle(save['meas'])
    df_test_s = pd.read_pickle(save['test'])
    # make plot dirs if they don't exist
    plotdir, trackdir = check_plot_dir(model_fname)
    # history load
    history = pkl.load(open(model_fname+'/history.pkl', 'rb'))
    #### Epoch plots
    print('Making epoch plots...')
    parsed_history = create_dict_from_history(history)
    plot_dict = make_plots_history_vs_epoch(parsed_history, plotdir, model_num)
    print('Done.\n')
    #### derivatives histograms
    print('Making derivatives histograms...')
    for tup in zip([df_test_s], [' (Test Dataset)'], ['_df_test'], [200]):
    #for tup in zip([df_test_s, df_meas_s], [' (Test Dataset)', ' (Measured Dataset)'], ['_df_test', '_df_meas'], [200, 150]):
        df_, title_suff, fname_suff, nbins = tup
        _ = make_deriv_1D_hist(df_, bin_numerical=True, nbins=nbins, title_suff=title_suff,
                               include_numerical=True, include_exact=True,
                               fname_suff=fname_suff, plotdir=plotdir,
                               model_num=model_num)
        derivs_fig_dict = _
    print('Done.\n')
    #### fit profiles
    print('Making fit profiles...')
    # data
    print('df_meas')
    profile_fit_fig_dict = {}
    #q_strings = ['(X==-0.8) & (Y==0.0)', '(X==0.8) & (Y==0.0)', '(Y==0.0) & (Z==8.40)']
    # keep Z that's in all scenarios (sparser Z)
    q_strings = ['(X==-0.8) & (Y==0.0)', '(X==0.8) & (Y==0.0)', '(Y==0.0) & (Z==8.45)']
    # q_strings = ['(X==-0.8) & (Y==0.0)', '(X==0.8) & (Y==0.0)', '(Y==0.0) & (8.4149 <= Z <= 8.4151)']
    x_list = ['Z', 'Z', 'X']
    fname_suffs = ['_X_m0p8_Y_0p0', '_X_0p8_Y_0p0', '_Y_0p0_Z_8p4']
    for tup in zip(q_strings, x_list, fname_suffs):
        q_str, x, fname_suff = tup
        # DEBUG
        print(f'q_str={q_str}')
        _ = make_fit_data_profile(df_meas_s, df_test_s, x=x, q_str=q_str, title_suff='',
                                  fname_suff=fname_suff, noise=noise, plotdir=plotdir,
                                  model_num=model_num)
        profile_fit_fig_dict[x] = _
    # test
    print('df_test')
    profile_fit_fig_dict_test = {}
    #q_strings = ['(X==-0.8) & (Y==0.0)', '(Y==0.0) & (Z==8.40)']
    #x_list = ['Z', 'X']
    #fname_suffs = ['_X_m0p8_Y_0p0_df_test', '_Y_0p0_Z_8p4_df_test']
    for tup in zip(q_strings, x_list, fname_suffs):
        q_str, x, fname_suff = tup
        _ = make_fit_data_profile(df_test_s, df_test_s, x=x, q_str=q_str,
                                  title_suff=' (Test Dataset)',
                                  fname_suff=fname_suff+'_df_test', noise=None,
                                  plotdir=plotdir, model_num=model_num)
        profile_fit_fig_dict_test[x] = _
    ### ADD HISTOGRAM WITHOUT FINAL REFIT -- do better for scaling axes
    # things that rely on merged dataframes
    if has_full:
    ###if False: # testing
        #### input data & test profile
        print('Making input profile plots...')
        _ = make_input_data_profile(df_meas, df_test, q_str='(X == -0.8) & (Y == 0.0)',
                                    noise=noise, plotdir=plotdir, model_num=model_num)
        profile_input_fig_dict = _
        print('Done.\n')
        #### residuals histograms
        print('Making residuals histograms...')
        residuals_fig_dict = {}
        for tup in zip([df_test, df_meas], [' (Test Dataset)', ' (Measured Dataset)'],
                       ['_df_test', '_df_meas'], [300, 200]):
            df_, title_suff, fname_suff, nbins = tup
            if fname_suff == '_df_meas':
                add_noise_model = True
            else:
                add_noise_model = False
            _ = make_Bi_residual_1D_hist(df_, bin_orig=True, nbins=nbins, title_suff=title_suff,
                                         fname_suff=fname_suff, add_noise_model=add_noise_model,
                                         noise=noise, noise_on_final=True, plotdir=plotdir,
                                         model_num=model_num)
            residuals_fig_dict[fname_suff[1:]] = _
        print('Done.\n')
        #### derivatives histograms
        # print('Making derivatives histograms...')
        # for tup in zip([df_test], [' (Test Dataset)'], ['_df_test'], [200]):
        #     df_, title_suff, fname_suff, nbins = tup
        #     _ = make_deriv_1D_hist(df_, bin_numerical=True, nbins=nbins, title_suff=title_suff,
        #                            include_numerical=True, include_exact=True,
        #                            fname_suff=fname_suff, plotdir=plotdir,
        #                            model_num=model_num)
        #     derivs_fig_dict = _
        # print('Done.\n')
        # #### fit profiles
        # print('Making fit profiles...')
        # # data
        # print('df_meas')
        # profile_fit_fig_dict = {}
        # #q_strings = ['(X==-0.8) & (Y==0.0)', '(X==0.8) & (Y==0.0)', '(Y==0.0) & (Z==8.40)']
        # # keep Z that's in all scenarios (sparser Z)
        # q_strings = ['(X==-0.8) & (Y==0.0)', '(X==0.8) & (Y==0.0)', '(Y==0.0) & (Z==8.45)']
        # # q_strings = ['(X==-0.8) & (Y==0.0)', '(X==0.8) & (Y==0.0)', '(Y==0.0) & (8.4149 <= Z <= 8.4151)']
        # x_list = ['Z', 'Z', 'X']
        # fname_suffs = ['_X_m0p8_Y_0p0', '_X_0p8_Y_0p0', '_Y_0p0_Z_8p4']
        # for tup in zip(q_strings, x_list, fname_suffs):
        #     q_str, x, fname_suff = tup
        #     # DEBUG
        #     print(f'q_str={q_str}')
        #     _ = make_fit_data_profile(df_meas, df_test, x=x, q_str=q_str, title_suff='',
        #                               fname_suff=fname_suff, noise=noise, plotdir=plotdir,
        #                               model_num=model_num)
        #     profile_fit_fig_dict[x] = _
        # # test
        # print('df_test')
        # profile_fit_fig_dict_test = {}
        # #q_strings = ['(X==-0.8) & (Y==0.0)', '(Y==0.0) & (Z==8.40)']
        # #x_list = ['Z', 'X']
        # #fname_suffs = ['_X_m0p8_Y_0p0_df_test', '_Y_0p0_Z_8p4_df_test']
        # for tup in zip(q_strings, x_list, fname_suffs):
        #     q_str, x, fname_suff = tup
        #     _ = make_fit_data_profile(df_test, df_test, x=x, q_str=q_str,
        #                               title_suff=' (Test Dataset)',
        #                               fname_suff=fname_suff+'_df_test', noise=None,
        #                               plotdir=plotdir, model_num=model_num)
        #     profile_fit_fig_dict_test[x] = _
        #### mu2eplots
        print('Making mu2eplots...')
        mu2eplots_all_dict = {}
        # [LSQ, PINN, LSQ refit, Full model]
        coord_to_datas = [lambda i: f'B{i}', lambda i: f'dB{i}',
                          lambda i: f'B{i}_min_dB{i}_NN', lambda i: f'B{i}']
        coord_to_fits = [lambda i: f'B{i}_fit', lambda i: f'dB{i}_NN',
                         lambda i: f'B{i}_fit_2', lambda i: f'B{i}_fit_full']
        fname_suffs = ['_LSQfit', '_PINNfit', '_LSQ2fit', '_FullModel']
        title_suffs = ['LSQ Model', 'PINN Model', 'LSQ Refit', 'Full Model']
        for tup in zip(coord_to_datas, coord_to_fits, fname_suffs, title_suffs):
            c_to_d, c_to_f, fs, ts1 = tup
            _ = make_mu2e_plot3d(df_meas, steps=[0.0, np.pi/2.], steps_nice=[r'0', r'\pi/2'],
                                             conditions=('Z > 4.200', 'Z < 13.900'),
                                             coord_to_data=c_to_d, coord_to_fit=c_to_f,
                                             fname_suff=fs, title_nice=True,
                                             title_suff=f'\n{ts1} (#{model_num})',
                                             plotdir=plotdir, model_num=model_num)
            mu2eplot_fig_dict = _
            mu2eplots_all_dict[fs[1:]] = mu2eplot_fig_dict
        print('Done.\n')
    # make the weights and biases plot
    print('Making weights and biases plots...')
    wb_dict_init = pkl.load(open(model_fname+'/wb_dict_init.pkl', 'rb'))
    wb_dict_trained = pkl.load(open(model_fname+'/wb_dict_trained.pkl', 'rb'))
    N = np.sum([len(wb_dict_init['weights'][1].flatten()) for i in range(len(wb_dict_init['weights']))]) # total number of weights
    #N = wb_dict_init['weights'][0].shape[1] # nodes per hidden layer
    if N < 1000:
        Nbins_w = 50
        Nbins_b = 5
    else:
        Nbins_w = 500
        Nbins_b = 50
    _ = make_weights_and_biases_plot(wb_dict_init, wb_dict_trained,
                                     Nbins_w=Nbins_w, Nbins_b=Nbins_b,
                                     ylim_bias=True,
                                     title=None, make_title=False,
                                     plotdir=plotdir, model_num=model_num)
    wb_fig_dict = _
    print('Done.\n')
    print(f'Plots for {model_fname} done!')
    tf = time.time()
    dt = tf - t0
    dt_min = dt / 60.
    print(f'Elapsed time: {dt:0.1f} s = {dt_min:0.2f} min')
