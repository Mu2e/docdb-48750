import os
import sys
import argparse
import time
import numpy as np
import tensorflow as tf
import pickle as pkl

from BFieldPINN import BFieldPINN_dir, BFieldPINN_data
from BFieldPINN.ScalarPINN import ScalarPINN
from BFieldPINN.StandardPINN import StandardPINN
from BFieldPINN.NN_callbacks import get_callback_list, register_x_sin2x_func, PredictionTrack, TemperLambda
from BFieldPINN.tools import (
    init_GPU,
    set_GPU,
    get_GPU,
    make_LSQ_df_PINN_subtracted,
    evaluate_PINN_on_dfs,
    prep_PINN_inputs,
    load_and_process_FMS_fit_data,
    construct_normalizations_dict,
    #world_to_NN,
    #NN_to_world,
    #add_points_for_J,
    #calc_jacobian_numerical,
    #scale_J,
    #calc_div,
    #calc_curl,
    #div_and_curl_calculations
)
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
    parser.add_argument('-t', '--Testing',
                        help='Testing? If yes, uses an extremely minimal model function (k terms only). "y"/"n"(default).')
    args = parser.parse_args()
    # fill defaults if necessary
    if args.Model is None:
        args.Model = '1'
    if args.Device is None:
        args.Device = '0'
    if args.Testing is None:
        args.Testing = False
    else:
        args.Testing = args.Testing == 'y'
    # initializations
    # GPU
    dev = args.Device
    init_GPU()
    set_GPU(dev)
    print(f"The current GPU is: {get_GPU()}")
    # global seeds
    # set seeds -- numpy (data split), tensorflow (collocation selection)
    # numpy
    np_seed = 1313
    print(f'Using numpy random seed: {np_seed}\n')
    np.random.seed(np_seed)
    # tensorflow
    tf_seed = 1234
    print(f'Using tf random seed (global): {tf_seed}\n')
    tf.random.set_seed(tf_seed)
    # run specific model
    model_num = args.Model
    test = args.Testing
    if args.Testing:
        epochs = NN_config_dict[model_num]['epochs_test']
    else:
        epochs = NN_config_dict[model_num]['epochs']
    # pick the appropriate PINN class
    if NN_config_dict[model_num]['NN_type'] == 'Scalar':
        PINN = ScalarPINN
    else:
        PINN = StandardPINN
    # run preparations function
    init_config, df_dict = prep_PINN_inputs(files_dict[model_num], NN_config_dict[model_num])
    # intialize and compile PINN
    myPINN = PINN(**init_config)
    myPINN.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=NN_config_dict[model_num]['LR_init']))
    # set up callbacks
    callbacks = get_callback_list(myPINN, NN_config_dict[model_num])
    print(myPINN.summary())
    # train!
    t0 = time.time()
    history_callback = myPINN.fit((init_config['x_u'], init_config['y_u'], init_config['z_u']),
                                  epochs=epochs, batch_size=len(init_config['x_u']),
                                  callbacks=callbacks)
    N_epochs = len(history_callback.history['Loss'])
    if NN_config_dict[model_num]['track']:
        myPINN.pred_track[N_epochs-1] = myPINN.get_B(myPINN.tracking_data[:,0:1], myPINN.tracking_data[:,1:2], myPINN.tracking_data[:,2:3]).numpy()
    tf = time.time()
    dt = tf - t0
    dt_min = dt / 60.
    print(f'Training time: {dt:0.1f} s = {dt_min:0.2f}\n')
    # save the model
    print('Saving the trained model...')
    model_fname = files_dict[model_num]['model_fname']
    if not os.path.exists(model_fname):
        os.makedirs(model_fname)
    print(f'myPINN.save_model: {model_fname}')
    myPINN.save_model(model_fname)
    # save history
    sname = model_fname+'/history.pkl'
    print(f'history_callback.history: {sname}')
    pkl.dump(history_callback.history, open(sname, 'wb'))
    print('Done.\n')
    ## load model (REFERENCE)
    # myPINN_load = PINN.load_model(model_fname)
    # history_load = pkl.load(open(model_fname+'/history.pkl', 'rb'))
    ## dfs
    # df_dict, norm_dict = load_and_process_FMS_fit_data(files_dict[model_num]['in']['meas'], files_dict[model_num]['in']['test'], NN_config_dict[model_num])
    # myPINN_load.summary()
    # which instance to use for evaluations?
    myPINN_ = myPINN
    #myPINN_ = myPINN_load
    # history
    history = history_callback.history
    #history = history_load
    ### Evaluations
    # whether we calculate jacobian changes evaluation
    make_jac = NN_config_dict[model_num]['make_jacobian_df']
    if make_jac:
        keys_to_eval = ['df_meas', 'df_test', 'df_test_jac']
    else:
        keys_to_eval = ['df_meas', 'df_test']
    df_dict = evaluate_PINN_on_dfs(myPINN_, df_dict, keys_to_eval, make_jac, N_chunk=100000)
    # save dataframes
    print('Saving df_meas and df_test...')
    for k in ['meas', 'test']:
        f_ = files_dict[model_num]['save'][k]
        print(f'df_{k}: {f_}')
        df_dict[f'df_{k}'].to_pickle(f_)
    print('Done.')
    # save the files_dict -- not really necessary, this is importable in the script directory
    sdict_fname = model_fname+'/files_dict_model.p'
    print(f'Saving files_dict for this model to: {sdict_fname}')
    pkl.dump(files_dict[model_num], open(sdict_fname, 'wb'))
    print('Done.\n')
    ### Prepare for refit
    print('Preparing dataframes for LSQ refit...')
    df_meas_ps = make_LSQ_df_PINN_subtracted(df_dict['df_meas'], fname=files_dict[model_num]['out']['meas'], name='df_meas')
    df_test_ps = make_LSQ_df_PINN_subtracted(df_dict['df_test'], fname=files_dict[model_num]['out']['test'], name='df_test')
    print('Done.\n')
    print('PINN training script complete.')
