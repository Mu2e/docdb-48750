import os
import sys
import argparse
from mu2e.hallprober import field_map_analysis
# configs
fpath = os.path.dirname(os.path.realpath(__file__))
configs_dir = os.path.abspath(os.path.join(fpath, '..', '..', 'configs'))
sys.path.append(configs_dir)
from LSQ_configs import cfg_plot_mpl, cfg_plot_none, cfg_params_test, LSQ_config_dict

if __name__=='__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-M', '--Model',
                        help='Which model do you want to fit? [1 (default), 2, 3, 4, 5, 6, 7]')
    parser.add_argument('-P', '--PINN_Subtracted',
                        help='Use the PINN subtracted field? "y" / "n" (default)')
    parser.add_argument('-t', '--Testing',
                        help='Testing? If yes, uses an extremely minimal model function (k terms only). "y"/"n"(default).')
    args = parser.parse_args()
    # fill defaults if necessary
    if args.Model is None:
        args.Model = '1'
    if args.PINN_Subtracted is None:
        args.PINN_Subtracted = False
    else:
        args.PINN_Subtracted = args.PINN_Subtracted == 'y'
    if args.Testing is None:
        args.Testing = False
    else:
        args.Testing = args.Testing == 'y'
    # run specific model
    config = LSQ_config_dict[args.Model]
    if args.Testing:
        cfg_params_ = cfg_params_test
    else:
        cfg_params_ = config['cfg_params']
    if args.PINN_Subtracted:
        name = config['fitnames']['PINN_Subtracted']
        cfg_data_ = config['cfg_data_ps']
        cfg_pickle_ = config['cfg_pickle_ps']
        cfg_data_test_ = config['cfg_data_test_ps']
        cfg_pickle_test_ = config['cfg_pickle_test_ps']
    else:
        name = config['fitnames']['Initial']
        cfg_data_ = config['cfg_data']
        cfg_pickle_ = config['cfg_pickle']
        cfg_data_test_ = config['cfg_data_test']
        cfg_pickle_test_ = config['cfg_pickle_test']
    # print configs:
    print(f'run_LSQ_fit.py configs: Model={args.Model}, PINN Subtracted? {args.PINN_Subtracted}, '
          +f'Testing? {args.Testing}')
    # fit
    print('Fitting...\n')
    hmd, ff = field_map_analysis(name, cfg_data_,
                                 config['cfg_geom_fit'], cfg_params_,
                                 cfg_pickle_, cfg_plot_mpl,
                                 use_name_in_df=True)
    # recreate for df_test
    print('\nEvaluating (df_test)...\n')
    hmd_rec, ff_rec = field_map_analysis(name, cfg_data_test_,
                                 config['cfg_geom_test'], cfg_params_,
                                 cfg_pickle_test_, cfg_plot_none,
                                 use_name_in_df=True)
