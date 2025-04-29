import os
from copy import deepcopy
from LSQ_configs import LSQ_config_dict as LSQ_c
# should be the same as mu2e_ext_path, but this is more consistent
#from mu2e import mu2e_ext_path
from BFieldPINN import BFieldPINN_data
# local imports
from useful_funcs import is_number
from model_globals import N_opt_tests, opt_dict

### NN configurations
base_NN_dict = {
    ## generic information
    #'model_fname': LSQ_min['1']['fitnames']['Initial'],
    #'NN_type': 'Scalar',
    #'NN_type': 'Standard',
    'epochs': 10000,
    #'epochs_test': 1000, # pre-train + train equal
    'epochs_test': 100, # very basic test (not through pretrain)
    ## training info
    'perc_train': 0.8,
    ## NETWORK STRUCTURE
    'N_hidden': 8, 'N_nodes': 64, 'activ': 'x_sin2x', 'snake_a': 5.0,
    # 'N_hidden': 8, 'N_nodes': 64, 'activ': 'x_sin2x', 'snake_a': 2.0,
    # 'N_hidden': 8, 'N_nodes': 64, 'activ': 'x_sin2x', 'snake_a': 10.0,
    # 'lambda_': 0.1, 'N_f': 50000, 'reg': 0.0, 'initializer_type': 'uniform',
    'lambda_': 0.001, 'N_f': 50000, 'reg': 0.0, 'initializer_type': 'uniform',
    #'initializer_lim': 0.1,
    'initializer_lim': 0.05,
    # 'initializer_lim': 0.01,
    #'initializer_lim': (3. / 64.)**(1./2.),
    # seeds
    #'initializer_seed': 1111,
    #'colloc_seed': 4321,
    'initializer_seed': None,
    'colloc_seed': None,
    ## CALLBACK CONFIGS
    # LR
    'LR_init': 0.002,
    # 'LR_init': 0.001,
    # 'LR_monitor': 'Loss', 'LR_factor': 0.5, 'LR_patience': 300, 'LR_min': 1e-8,
    # 'LR_monitor': 'Loss_val', 'LR_factor': 0.5, 'LR_patience': 1000, 'LR_min': 1e-8,
    #'LR_monitor': 'Loss_val', 'LR_factor': 0.5, 'LR_patience': 600, 'LR_min': 1e-8,
    #'LR_monitor': 'Loss_val', 'LR_factor': 0.5, 'LR_patience': 600, 'LR_min': 5e-5,
    'LR_monitor': 'Loss', 'LR_factor': 0.5, 'LR_patience': 300, 'LR_min': 5e-5,
    # early stop
    # 'Stop_monitor': 'Loss', 'Stop_patience': 3000, 'Stop_min_delta': 1e-6,
    ##'Stop_monitor': 'Loss_val', 'Stop_patience': 3000, 'Stop_min_delta': 1e-6,
    'Stop_monitor': 'Loss_val', 'Stop_patience': 5000, 'Stop_min_delta': 1e-6,
    # temper / pretrain lambda
    # 'lambda_pretrain': 500, 'lambda_N_wait': 200000, 'lambda_mult_factor': 1.0, 'lambda_add_factor': 0.0,
    # 'lambda_start_temper': 200000, 'lambda_max': 1000,
    # temper
    # 'lambda_pretrain': 0, 'lambda_N_wait': 250, 'lambda_mult_factor': 2.0, 'lambda_add_factor': 0.0,
    # 'lambda_start_temper': 1000, 'lambda_max': 0.2,
    'lambda_pretrain': 0, 'lambda_N_wait': 250, 'lambda_mult_factor': 1.25, 'lambda_add_factor': 0.001,
    # 'lambda_start_temper': 1000, 'lambda_max': 0.2,
    'lambda_start_temper': 1000, 'lambda_max': 0.1,
    # false pretrain
    # 'lambda_pretrain': 0, 'lambda_N_wait': 1, 'lambda_mult_factor': 1.0, 'lambda_add_factor': 0.099,
    # 'lambda_start_temper': 1250, 'lambda_max': 0.1,
    # save tracking information
    'track': True, 'track_stride': 10, 'track_queries': ['(X==-0.8) & (Y==0.0)', '(Y==0.0) & (Z==8.40)'],
    # jacobian dataframe setup
    'make_jacobian_df': True, 'jac_dxyz': 0.001,
}

NN_config_dict = {
    '1': dict(
        deepcopy(base_NN_dict),
        **{'model_fname': LSQ_c['1']['fitnames']['Initial'], 'NN_type': 'Scalar'},
    ),
    '2': dict(
        deepcopy(base_NN_dict),
        **{'model_fname': LSQ_c['2']['fitnames']['Initial'], 'NN_type': 'Standard'},
    ),
    '3': dict(
        deepcopy(base_NN_dict),
        **{'model_fname': LSQ_c['3']['fitnames']['Initial'], 'NN_type': 'Scalar'},
    ),
    '4': dict(
        deepcopy(base_NN_dict),
        **{'model_fname': LSQ_c['4']['fitnames']['Initial'], 'NN_type': 'Scalar'},
    ),
    '5': dict(
        deepcopy(base_NN_dict),
        **{'model_fname': LSQ_c['5']['fitnames']['Initial'], 'NN_type': 'Scalar'},
    ),
    '6': dict(
        deepcopy(base_NN_dict),
        **{'model_fname': LSQ_c['6']['fitnames']['Initial'], 'NN_type': 'Scalar'},
        #**{'model_fname': LSQ_c['6']['fitnames']['Initial'], 'NN_type': 'Standard'},
    ),
    '7': dict(
        deepcopy(base_NN_dict),
        **{'model_fname': LSQ_c['7']['fitnames']['Initial'], 'NN_type': 'Scalar'},
        #**{'model_fname': LSQ_c['7']['fitnames']['Initial'], 'NN_type': 'Standard'},
    ),
    '8': dict(
        deepcopy(base_NN_dict),
        **{'model_fname': LSQ_c['8']['fitnames']['Initial'], 'NN_type': 'Scalar'},
    ),
    '9': dict(
        deepcopy(base_NN_dict),
        **{'model_fname': LSQ_c['9']['fitnames']['Initial'], 'NN_type': 'Scalar'},
    ),
    '10': dict(
        deepcopy(base_NN_dict),
        **{'model_fname': LSQ_c['10']['fitnames']['Initial'], 'NN_type': 'Scalar'},
    ),
}

# add to model 1 for hyperparam opt
# FIXME! Be more careful about params -- don't want to overwrite these accidentally
for i in range(N_opt_tests):
    model_num = f'1_{i}'
    opt_ = opt_dict[model_num]
    NN_config_dict[model_num] = dict(
        deepcopy(base_NN_dict),
        **{'model_fname': LSQ_c[model_num]['fitnames']['Initial'], 'NN_type': 'Scalar'},
    )
    # update for particular opt choice
    NN_config_dict[model_num]['N_f'] = opt_['N_f']
    NN_config_dict[model_num]['LR_init'] = opt_['LR_init']
    NN_config_dict[model_num]['initializer_lim'] = opt_['initializer_lim']
    NN_config_dict[model_num]['lambda_pretrain'] = opt_['lambda_pretrain']
    NN_config_dict[model_num]['N_hidden'] = opt_['N_hidden']
    NN_config_dict[model_num]['N_nodes'] = opt_['N_nodes']
    NN_config_dict[model_num]['activ'] = opt_['activ']
    # below only relevant when using snake activation
    NN_config_dict[model_num]['snake_a'] = opt_['snake_a']
    # lambda_
    #if 'lambda_' in opt_.keys():
    #    NN_config_dict[model_num]['lambda_'] = opt_['lambda_']
    # many optional params
    for k in ['lambda_', 'lambda_N_wait', 'lambda_start_temper', 'lambda_mult_factor', 'lambda_add_factor',
    'lambda_max', 'LR_patience', 'Stop_monitor', 'LR_monitor', 'Stop_patience']:
        if k in opt_.keys():
            NN_config_dict[model_num][k] = opt_[k]



## FIXME! Testing updating PINN structure for LSQ updates
'''
NN_config_dict['1']['epochs'] = 10000
NN_config_dict['1']['lambda_'] = 0.1
NN_config_dict['1']['snake_a'] = 1.0
# NN_config_dict['1']['activ'] = 'gelu'
NN_config_dict['1']['LR_init'] = 0.002
NN_config_dict['1']['N_hidden'] = 4 # def: 8
NN_config_dict['1']['N_nodes'] = 32 # def: 64
NN_config_dict['1']['initializer_lim'] = 0.1 # def: 0.05
NN_config_dict['1']['N_f'] = 30000 # def: 50000
'''
# NN_config_dict['1']['LR_init'] = 0.00025
# NN_config_dict['1']['LR_min'] = 1e-9 # def: 1e-8
# NN_config_dict['1']['epochs'] = 1000 # test
#NN_config_dict['1']['epochs'] = 3000
# NN_config_dict['1']['lambda_pretrain'] = 20 # def: 500
# NN_config_dict['1']['epochs'] = 100
# NN_config_dict['1']['lambda_pretrain'] = 500 # def: 500
# NN_config_dict['1']['initializer_type'] = None # def: 'uniform'
#NN_config_dict['1']['snake_a'] = 10.0
# NN_config_dict['1']['N_hidden'] = 4 # def: 8
# NN_config_dict['1']['N_nodes'] = 64 # def: 64
# NN_config_dict['1']['initializer_lim'] = 0.05 # def: 0.05
# NN_config_dict['1']['activ'] = 'tanh'
# NN_config_dict['1']['activ'] = 'gelu'
# NN_config_dict['1']['lambda_'] = 0.05

### Extra customizations. See commented example
# NN_config_dict['5']['epochs'] = 20000
# standard PINN
NN_config_dict['2']['LR_init'] = 0.001
NN_config_dict['2']['LR_patience'] = 200
# phony curl
# ORIG
'''
NN_config_dict['4']['lambda_pretrain'] = 200
NN_config_dict['4']['lambda_'] = 0.5
NN_config_dict['4']['LR_init'] = 0.001
NN_config_dict['4']['LR_patience'] = 200
'''
# TESTING
NN_config_dict['4']['NN_type'] = 'Standard'
NN_config_dict['4']['lambda_'] = 0.0
NN_config_dict['4']['lambda_pretrain'] = 0
NN_config_dict['4']['N_f'] = 1000 # small sample to look at div and curl throughout training
NN_config_dict['4']['N_hidden'] = 4 # def: 8
# debuging 6 (busbars only)
#NN_config_dict['6']['lambda_'] = 0.0
#NN_config_dict['6']['N_f'] = 2
#NN_config_dict['6']['lambda_'] = 0.01
#NN_config_dict['6']['N_f'] = 20000
#NN_config_dict['6']['epochs'] = 20000
#NN_config_dict['6']['lambda_pretrain'] = 1000
#NN_config_dict['6']['N_hidden'] = 10
#NN_config_dict['6']['N_nodes'] = 128
#NN_config_dict['6']['LR_init'] = 0.001
#NN_config_dict['6']['lambda_'] = 0.05
# debugging 7 (DS coils only with connectors)
#NN_config_dict['7']['lambda_'] = 0.0
#NN_config_dict['7']['N_f'] = 2

### filenames
files_dict = {}
for model_num in NN_config_dict.keys():
    config = LSQ_c[model_num]
    # model name
    model_fname = BFieldPINN_data + 'BFieldPINN/docdb-48750/'\
     + config['subdir'] + '_' + NN_config_dict[model_num]['NN_type'] +'PINN'
    # get dataframe names
    # meas
    outfile_meas = config['cfg_data_ps'].path
    save_meas = os.path.join(model_fname, 'df_meas_NN_Results.p')
    save_meas_full = os.path.join(model_fname, 'df_meas_Full_Results.p')
    infile_meas = outfile_meas.replace('_PINN_Subtracted', '').replace('.Mu2E.p', '.Mu2E.Fit.p')
    if not is_number(model_num):
        infile_meas = infile_meas.replace(model_num, model_num.split('_')[0])
    # check if eval exists
    Bdir = infile_meas[:infile_meas.rfind('/')+1]
    eval_file = infile_meas.replace('.Mu2E', '_eval.Mu2E')
    eval_file = eval_file[eval_file.rfind('/')+1:]
    if eval_file in os.listdir(Bdir):
        infile_meas = os.path.join(Bdir, eval_file)
        # debug printout
        #print('Found eval file. Not all points in df_meas used in fit.')
    # test
    outfile_test = config['cfg_data_test_ps'].path
    save_test = os.path.join(model_fname, 'df_test_NN_Results.p')
    save_test_full = os.path.join(model_fname, 'df_test_Full_Results.p')
    infile_test = outfile_test.replace('_PINN_Subtracted', '').replace('.Mu2E.p', '.Mu2E.Fit.p')
    if not is_number(model_num):
        infile_test = infile_test.replace(model_num, model_num.split('_')[0])
    # file dictionary
    files_dict[model_num] = {
        'model_fname': model_fname,
        'in': {'meas': infile_meas, 'test': infile_test},
        'save': {'meas': save_meas, 'test': save_test},
        'out': {'meas': outfile_meas, 'test': outfile_test},
        'full': {'meas': save_meas_full, 'test': save_test_full},
    }
