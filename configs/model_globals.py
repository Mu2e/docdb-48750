# parameters for modifying original map data
# thermal noise
noise = 0.3 # Gauss
noise_str = '_noise'+str(noise).replace('.', 'p')
# toys (including nominal)
N_toys_nominal = 10
# phony curled field
phony_curl = 20.0 # Gauss / m
phony_curl_str = f'_curlZ'+str(phony_curl).replace('-', 'm').replace('.', 'p')
# x0 offset (center of DS)
x0 = -3.904
# z0 offest (center of DS)
z0 = 9.033
#z0 = 9.7 # Susan's number (middle after cutting out points) -- this is probably better.
# number of hyperparam optmization runs
#N_opt_tests = 20
#N_opt_tests = 21 # after determining best
#N_layer_tests = [4, 8, 10, 11, 12]
#N_nodes_tests = [64, 128, 192, 256]
N_layer_tests = [2, 4, 8, 10]
N_nodes_tests = [16, 32, 64, 96]
N_layer_nodes = len(N_layer_tests) * len(N_nodes_tests)
# N_opt_tests = N_layer_nodes
# tanh added
#N_opt_tests = N_layer_nodes+1 # after determining best -- FIXME! More for "a" optim?
# p_eff estimation
#tau_p_eff = 0.1 # how much to perturb the residuals
tau_p_eff = 0.5 * noise
seed_p_eff_gen = 54321 # if I run again, I want the same seed (repeatability)
N_toys_p_eff = 20 # 30 min each, 4 GPUs -> 2.5 hours
# create dict for p_eff estimation (same network structure)
p_eff_dict = {}
for i in range(N_toys_p_eff):
    model_num = f'1_p_eff_pert_{i}'
    p_eff_dict[model_num] = 0
# create dict for optimization of network structure
opt_dict = {}
i = 0
for L in N_layer_tests:
    for N in N_nodes_tests:
        model_num = f'1_{i}'
        opt_dict[model_num] = {'N_hidden': L, 'N_nodes': N, 'activ': 'x_sin2x', 'snake_a': 5.0, 'LR_init': 0.002, 'N_f': 50000, 'initializer_lim': 0.05}
        #opt_dict[model_num] = {'N_hidden': L, 'N_nodes': N, 'activ': 'x_sin2x', 'snake_a': 2.0, 'LR_init': 0.002, 'N_f': 50000, 'initializer_lim': 0.05}
        ##opt_dict[model_num] = {'N_hidden': L, 'N_nodes': N, 'activ': 'x_sin2x', 'snake_a': 2.0, 'LR_init': 0.002, 'N_f': 50000}
        ##opt_dict[model_num]['initializer_lim'] = (3. / N)**(1./2.)
        #opt_dict[model_num]['initializer_lim'] = 0.05
        # opt_dict[model_num]['initializer_lim'] = 0.15 # 16 nodes
        opt_dict[model_num]['initializer_lim'] = 0.11 # 16 nodes, using heuristic, x0.7
        #opt_dict[model_num]['initializer_lim'] = 0.126 # 16 nodes, using heuristic, x0.8
        # opt_dict[model_num]['initializer_lim'] = 0.157 # 16 nodes, using heuristic, x1.0
        opt_dict[model_num]['lambda_pretrain'] = 500
        # opt_dict[model_num]['LR_init'] = 0.004 # 1_0 tests
        opt_dict[model_num]['LR_init'] = 0.01 # 1_0 tests
        # further tuning after initial tests
        #if i in [9, 12, 13]: # no movement from initial loss
        #if i in [9]: # no movement from initial loss
        #    opt_dict[model_num]['LR_init'] = 0.001
        # if i in [12, 13]: # no movement from initial loss
        '''
        if i in [9, 12, 13]: # no movement from initial loss
            # opt_dict[model_num]['LR_init'] = 0.001
            # opt_dict[model_num]['LR_init'] = 0.004
            opt_dict[model_num]['initializer_lim'] = 0.1
        '''
        if i in [11, 14, 15]: # memory alloc issues
            opt_dict[model_num]['N_f'] = 25000
            #opt_dict[model_num]['LR_init'] = 0.001
        ### tempering, after further tests below
        opt_dict[model_num]['lambda_pretrain'] = 0
        opt_dict[model_num]['lambda_'] = 0.001
        # opt_dict[model_num]['lambda_'] = 0.0001
        ##opt_dict[model_num]['lambda_N_wait'] = 250
        opt_dict[model_num]['lambda_N_wait'] = 3
        ##opt_dict[model_num]['lambda_start_temper'] = 1000
        opt_dict[model_num]['lambda_start_temper'] = 1250
        # opt_dict[model_num]['lambda_start_temper'] = 1500
        ##opt_dict[model_num]['lambda_mult_factor'] = 1.25
        opt_dict[model_num]['lambda_mult_factor'] = 1.0
        ##opt_dict[model_num]['lambda_add_factor'] = 0.001
        opt_dict[model_num]['lambda_add_factor'] = 0.0001
        opt_dict[model_num]['lambda_max'] = 0.1
        opt_dict[model_num]['LR_patience'] = 300 # default = 300
        opt_dict[model_num]['Stop_patience'] = 5000 # default = 3000
        opt_dict[model_num]['LR_min'] = 5e-5 # default = 1e-8
        opt_dict[model_num]['Stop_monitor'] = 'Loss_val'
        opt_dict[model_num]['LR_monitor'] = 'Loss'
        i += 1
# after determining best L and N
# optimize snake "a"
for a in [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]:
    model_num = f'1_{i}'
    # usin best number of layers and nodes: 8 and 64
    opt_dict[model_num] = opt_dict[model_num] = {'N_hidden': 8, 'N_nodes': 64, 'activ': 'x_sin2x', 'snake_a': a, 'LR_init': 0.002, 'N_f': 50000}
    opt_dict[model_num]['initializer_lim'] = (3. / N)**(1./2.)
    opt_dict[model_num]['lambda_pretrain'] = 500
    # customizations
    #if i in [16, 17, 18, 23]: # play around with LR (no movement of these)
    # if i in [23]: # play around with LR (no movement of these)
    #     #opt_dict[model_num]['LR_init'] = 0.004 # some movement on 23 pretrain -- nothing else
    #     opt_dict[model_num]['LR_init'] = 0.001
    #     opt_dict[model_num]['lambda_pretrain'] = 200
    # if i in [16, 17, 18]: # play around with LR (no movement of these)
    #     opt_dict[model_num]['LR_init'] = 0.01
    i += 1
# swap to tanh activation using best network structure. Note "a" is meaningless now
model_num = f'1_{i}'
opt_dict[model_num] = {'N_hidden': 8, 'N_nodes': 64, 'activ': 'tanh', 'snake_a': 2.0, 'LR_init': 0.002, 'N_f': 50000,
               #'initializer_lim': (3. / 64.)**(1./2.), 'lambda_pretrain': 500}
               'initializer_lim': 0.5, 'lambda_pretrain': 500}
i += 1
# lambda
#for lambda_ in [0.0, 0.1, 0.2, 0.5, 1.0, 2.0]: # CORRECT
for lambda_ in [0.0, 0.1, 0.001, 0.001, 0.001, 0.0001]: # TESTING
# for lambda_ in [0.0, 0.1, 0.1, 0.001, 0.001, 0.0001]: # TESTING
    model_num = f'1_{i}'
    # opt_dict[model_num] = opt_dict[model_num] = {'N_hidden': 8, 'N_nodes': 64, 'activ': 'x_sin2x', 'snake_a': 2.0, 'LR_init': 0.002, 'N_f': 50000}
    opt_dict[model_num] = opt_dict[model_num] = {'N_hidden': 8, 'N_nodes': 64, 'activ': 'x_sin2x', 'snake_a': 5.0, 'LR_init': 0.002, 'N_f': 50000}
    # opt_dict[model_num]['initializer_lim'] = (3. / N)**(1./2.)
    ##opt_dict[model_num]['initializer_lim'] = 0.05 # a=5
    #opt_dict[model_num]['initializer_lim'] = 0.0785 # a=5 using heuristic
    opt_dict[model_num]['initializer_lim'] = 0.055 # a=5 using heuristic * 0.7
    #opt_dict[model_num]['initializer_lim'] = 0.137 # a=2 using heuristic * 0.7
    # opt_dict[model_num]['initializer_lim'] = 0.069 # a=2, D=2 using heuristic * 0.7
    # opt_dict[model_num]['initializer_lim'] = 0.15 # a=2
    opt_dict[model_num]['lambda_pretrain'] = 500
    # opt_dict[model_num]['lambda_pretrain'] = 1250
    opt_dict[model_num]['lambda_'] = lambda_
    # customizations
    if i in [27, 28, 29, 30]: # no movement
        opt_dict[model_num]['lambda_pretrain'] = 0
        #opt_dict[model_num]['lambda_pretrain'] = 500
        #opt_dict[model_num]['LR_init'] = 0.01
        opt_dict[model_num]['LR_init'] = 0.002
        # opt_dict[model_num]['LR_init'] = 0.001
        # opt_dict[model_num]['LR_init'] = 0.01 # 1_0 tests -- try on 1_28 (nominal network) --> BAD
        # opt_dict[model_num]['lambda_N_wait'] = 100000
        #opt_dict[model_num]['lambda_N_wait'] = 1000
        # opt_dict[model_num]['lambda_N_wait'] = 100
        ###opt_dict[model_num]['lambda_N_wait'] = 250
        opt_dict[model_num]['lambda_N_wait'] = 3
        # opt_dict[model_num]['lambda_N_wait'] = 300
        # opt_dict[model_num]['lambda_N_wait'] = 500
        # opt_dict[model_num]['lambda_N_wait'] = 1 # rapid temper -- similar to pretraining
        #opt_dict[model_num]['lambda_start_temper'] = 0
        # opt_dict[model_num]['lambda_start_temper'] = 750
        # opt_dict[model_num]['lambda_start_temper'] = 100000
        #opt_dict[model_num]['lambda_start_temper'] = 1000
        # opt_dict[model_num]['lambda_start_temper'] = 0
        #opt_dict[model_num]['lambda_start_temper'] = 1000
        opt_dict[model_num]['lambda_start_temper'] = 1250
        opt_dict[model_num]['lambda_mult_factor'] = 1.0
        #opt_dict[model_num]['lambda_mult_factor'] = 2.0
        ###opt_dict[model_num]['lambda_mult_factor'] = 1.25
        # opt_dict[model_num]['lambda_add_factor'] = 0.0
        #opt_dict[model_num]['lambda_add_factor'] = 0.05
        # opt_dict[model_num]['lambda_add_factor'] = 0.01
        #opt_dict[model_num]['lambda_add_factor'] = 0.002
        # opt_dict[model_num]['lambda_add_factor'] = 0.005
        #opt_dict[model_num]['lambda_add_factor'] = 0.001
        opt_dict[model_num]['lambda_add_factor'] = 0.0001
        # opt_dict[model_num]['lambda_add_factor'] = 0.1
        # opt_dict[model_num]['lambda_max'] = 0.2
        opt_dict[model_num]['lambda_max'] = 0.1
        #opt_dict[model_num]['LR_patience'] = 20000 # default = 300
        # opt_dict[model_num]['LR_patience'] = 150 # default = 300
        opt_dict[model_num]['LR_patience'] = 300 # default = 300
        # opt_dict[model_num]['LR_patience'] = 400 # default = 300
        # opt_dict[model_num]['LR_patience'] = 600 # default = 300
        ###opt_dict[model_num]['LR_patience'] = 1000 # default = 300
        opt_dict[model_num]['Stop_patience'] = 5000 # default = 3000
        opt_dict[model_num]['LR_min'] = 5e-5 # default = 1e-8
        # monitor something other than "Loss", e.g. "Loss_val" or "Loss_B"
        # opt_dict[model_num]['LR_monitor'] = 'Loss_val'
        opt_dict[model_num]['Stop_monitor'] = 'Loss_val'
        opt_dict[model_num]['LR_monitor'] = 'Loss'
        # opt_dict[model_num]['Stop_monitor'] = 'Loss'
    i += 1

# Standard PINN for Model 4 (phony curl)
model_num = f'4_0'
opt_dict[model_num] = opt_dict[model_num] = {'N_hidden': 8, 'N_nodes': 64, 'activ': 'x_sin2x', 'snake_a': 5.0, 'LR_init': 0.002, 'N_f': 50000}
opt_dict[model_num]['initializer_lim'] = 0.055 # a=5 using heuristic * 0.7
#opt_dict[model_num]['lambda_'] = 0.0
#opt_dict[model_num]['lambda_max'] = 0.0
opt_dict[model_num]['lambda_'] = 0.00001
opt_dict[model_num]['lambda_max'] = 0.00001
opt_dict[model_num]['lambda_start_temper'] = 20000
#opt_dict[model_num]['lambda_pretrain'] = 20000 # --> this will by default leave lambda_=0 and run quicker (no colloc)
opt_dict[model_num]['lambda_pretrain'] = 0 # --> leaves colloc in, which will be better for diagnosis
opt_dict[model_num]['NN_type'] = 'Standard'

# Standard PINN for Model 8 (HPCMagUnc)
model_num = f'8_0'
opt_dict[model_num] = opt_dict[model_num] = {'N_hidden': 8, 'N_nodes': 64, 'activ': 'x_sin2x', 'snake_a': 5.0, 'LR_init': 0.002, 'N_f': 50000}
opt_dict[model_num]['initializer_lim'] = 0.055 # a=5 using heuristic * 0.7
#opt_dict[model_num]['lambda_'] = 0.0
#opt_dict[model_num]['lambda_max'] = 0.0
opt_dict[model_num]['lambda_'] = 0.00001
opt_dict[model_num]['lambda_max'] = 0.00001
opt_dict[model_num]['lambda_start_temper'] = 20000
#opt_dict[model_num]['lambda_pretrain'] = 20000 # --> this will by default leave lambda_=0 and run quicker (no colloc)
opt_dict[model_num]['lambda_pretrain'] = 0 # --> leaves colloc in, which will be better for diagnosis
opt_dict[model_num]['NN_type'] = 'Standard'

# Standard PINN no physics constraints for Model 2 (StandardPINN, nominal)
model_num = f'2_0'
opt_dict[model_num] = opt_dict[model_num] = {'N_hidden': 8, 'N_nodes': 64, 'activ': 'x_sin2x', 'snake_a': 5.0, 'LR_init': 0.002, 'N_f': 50000}
opt_dict[model_num]['initializer_lim'] = 0.055 # a=5 using heuristic * 0.7
#opt_dict[model_num]['lambda_'] = 0.0
#opt_dict[model_num]['lambda_max'] = 0.0
opt_dict[model_num]['lambda_'] = 0.00001
opt_dict[model_num]['lambda_max'] = 0.00001
opt_dict[model_num]['lambda_start_temper'] = 20000
#opt_dict[model_num]['lambda_pretrain'] = 20000 # --> this will by default leave lambda_=0 and run quicker (no colloc)
opt_dict[model_num]['lambda_pretrain'] = 0 # --> leaves colloc in, which will be better for diagnosis
opt_dict[model_num]['NN_type'] = 'Standard'

# calculate number hyperparam tests
N_opt_tests = len(opt_dict)

# so we can create directory tree before dataframes are ready, need a minimal
# copy of the LSQ dir
LSQ_config_dict_minimal = {
    '1': {'subdir': '1_Nominal',
          'fitnames': {'Initial': 'fma_1_Nominal_fitmap', 'PINN_Subtracted': 'fma_1_Nominal_PINN_subtracted_fitmap'},
    },
    '2': {'subdir': '2_Traditional_PINN',
          'fitnames': {'Initial': 'fma_2_Traditional_PINN_fitmap', 'PINN_Subtracted': 'fma_2_Traditional_PINN_PINN_subtracted_fitmap'},
    },
    '3': {'subdir': '3_External_Fit',
          'fitnames': {'Initial': 'fma_3_External_Fit_fitmap', 'PINN_Subtracted': 'fma_3_External_Fit_PINN_subtracted_fitmap'},
    },
    '4': {'subdir': '4_Phony_Curl',
          'fitnames': {'Initial': 'fma_4_Phony_Curl_fitmap', 'PINN_Subtracted': 'fma_4_Phony_Curl_PINN_subtracted_fitmap'},
    },
    '5': {'subdir': '5_Nominal_CylSym',
          'fitnames': {'Initial': 'fma_5_Nominal_CylSym_fitmap', 'PINN_Subtracted': 'fma_5_Nominal_CylSym_PINN_subtracted_fitmap'},
    },
    '6': {'subdir': '6_Busbars_Only',
          'fitnames': {'Initial': 'fma_6_Busbars_Only_fitmap', 'PINN_Subtracted': 'fma_6_Busbars_Only_PINN_subtracted_fitmap'},
    },
    '7': {'subdir': '7_DSCoils_Only',
          'fitnames': {'Initial': 'fma_7_DSCoils_Only_fitmap', 'PINN_Subtracted': 'fma_7_DSCoils_Only_PINN_subtracted_fitmap'},
    },
    '8': {'subdir': '8_HPCMagUnc',
          'fitnames': {'Initial': 'fma_8_HPCMagUnc_fitmap', 'PINN_Subtracted': 'fma_8_HPCMagUnc_PINN_subtracted_fitmap'},
    },
    '9': {'subdir': '9_SparseZPhi',
          'fitnames': {'Initial': 'fma_9_SparseZPhi_fitmap', 'PINN_Subtracted': 'fma_9_SparseZPhi_PINN_subtracted_fitmap'},
    },
    '10': {'subdir': '10_HPCMagUnc_SparseZPhi',
          'fitnames': {'Initial': 'fma_10_HPCMagUnc_SparseZPhi_fitmap', 'PINN_Subtracted': 'fma_10_HPCMagUnc_SparseZPhi_PINN_subtracted_fitmap'},
    },
}

# model 1 toys:
for toy_num in range(N_toys_nominal):
    model_num = f'1_toy_{toy_num}'
    LSQ_config_dict_minimal[model_num] = {
        'subdir': f'1_Nominal_toy_{toy_num}', 'fitnames': {'Initial': f'fma_1_Nominal_toy_{toy_num}_fitmap',
        'PINN_Subtracted': f'fma_1_Nominal_toy_{toy_num}_PINN_subtracted_fitmap'}
    }

# add to model 1 for p_eff estimation
# FIXME! Be more careful about fitnames -- don't want to overwrite these accidentally
#for i in range(N_opt_tests):
#    model_num = f'1_{i}'
for model_num in p_eff_dict.keys():
    i = model_num.split('_')[0]
    fnames = LSQ_config_dict_minimal[i]['fitnames']
    sdir = LSQ_config_dict_minimal[i]['subdir']
    LSQ_config_dict_minimal[model_num] = {
        'subdir': sdir.replace(i, model_num),
        'fitnames': {'Initial': fnames['Initial'], f'PINN_Subtracted': fnames['PINN_Subtracted'].replace(i, model_num)}
    }

# add to model 1 for hyperparam opt
# FIXME! Be more careful about fitnames -- don't want to overwrite these accidentally
#for i in range(N_opt_tests):
#    model_num = f'1_{i}'
for model_num in opt_dict.keys():
    i = model_num.split('_')[0]
    fnames = LSQ_config_dict_minimal[i]['fitnames']
    sdir = LSQ_config_dict_minimal[i]['subdir']
    LSQ_config_dict_minimal[model_num] = {
        'subdir': sdir.replace(i, model_num),
        'fitnames': {'Initial': fnames['Initial'], f'PINN_Subtracted': fnames['PINN_Subtracted'].replace(i, model_num)}
    }
