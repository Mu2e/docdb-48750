import os
import sys
import pandas as pd
#import pickle as pkl
# configs
fpath = os.path.dirname(os.path.realpath(__file__))
configs_dir = os.path.abspath(os.path.join(fpath, '..', 'configs'))
sys.path.append(configs_dir)
from LSQ_configs import LSQ_config_dict
#from PINN_configs import NN_config_dict, files_dict
from PINN_configs import files_dict

def merge_results(model_num, files_dict):
    model_fname = files_dict[model_num]['model_fname']
    ###outfile_meas = config['cfg_data_ps'].path
    print(f'Merging results for model {model_num} ({model_fname})...')
    # first load saved PINN
    save = files_dict[model_num]['save']
    df_meas = pd.read_pickle(save['meas'])
    df_test = pd.read_pickle(save['test'])
    # load refit -- start from out names (just before refit)
    out = files_dict[model_num]['out']
    has_eval = '_eval.Mu2E' in files_dict[model_num]['in']['meas']
    if has_eval:
        msuff = '_eval'
    else:
        msuff = ''
    name = LSQ_config_dict[model_num]['fitnames']['PINN_Subtracted']
    # if not 'toy' in model_fname:
    mfile = out['meas'].replace('.Mu2E.p', f'_{name}{msuff}.Mu2E.Fit.p')
    tfile = out['test'].replace('.Mu2E.p', f'_{name}.Mu2E.Fit.p')
    # else:
    #     mfile = out['meas'].replace('.Mu2E.p', f'_{name}{msuff}.Mu2E.Fit.p')
    #     tfile = out['test'].replace('.Mu2E.p', f'_{name}.Mu2E.Fit.p').replace('')
    print(f'df_meas: LSQ refit from {mfile} added to PINN results {save["meas"]}.')
    print(f'df_test: LSQ refit from {tfile} added to PINN results {save["test"]}.')
    df_meas_final = pd.read_pickle(mfile)
    df_test_final = pd.read_pickle(tfile)
    # LSQ saves in different order, so resort
    df_meas_final.sort_values(by=['X', 'Y', 'Z'], inplace=True)
    df_test_final.sort_values(by=['X', 'Y', 'Z'], inplace=True)
    # add LSQ refit to to dataframe
    for df_, df_f_ in zip([df_meas, df_test], [df_meas_final, df_test_final]):
        for i in ['x', 'y', 'z', 'r', 'phi']:
            # refit
            df_.loc[:, f'B{i}_fit_2'] = df_f_.loc[:, f'B{i}_fit']
            # PINN subtracted values, which we will want for plotting
            df_.loc[:, f'B{i}_min_dB{i}_NN'] = df_.loc[:, f'B{i}'] - df_.loc[:, f'dB{i}_NN']
            # and full model
            df_.loc[:, f'B{i}_fit_full'] = df_.loc[:, f'B{i}_fit_2'] + df_.loc[:, f'dB{i}_NN']
    # save
    full = files_dict[model_num]['full']
    df_meas.to_pickle(full['meas'])
    df_test.to_pickle(full['test'])
    print('Done.\n')
    return df_meas, df_test


if __name__=='__main__':
    # models = ['1'] + [f'1_toy_{i}' for i in range(9)]
    # models = ['1_toy_0']
    models = ['1']
    #for model_num in files_dict.keys():
    # for model_num in ['1']:
    # for model_num in ['4']:
    # for model_num in ['4_0']:
    # for model_num in ['5']:
    #for model_num in ['8']:
    # for model_num in ['10']:
    for model_num in models:
        df_meas, df_test = merge_results(model_num, files_dict)
