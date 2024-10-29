import os
import pickle as pkl
import numpy as np
import pandas as pd
configs_dir = os.path.dirname(os.path.realpath(__file__))

def calculate_means(fname):
    df = pd.read_pickle(fname)
    subdict = {}
    for i in ['x', 'y', 'z']:
        subdict[f'B{i}'] = df[f'B{i}'].mean()
    return subdict

def get_mean_fields_dict(init_dict, force_recalculate=False):
    mean_fields_dict = {}
    for key, fname in init_dict.items():
        # check if txt file of values exists
        outfile = f'{key}_mean_fields.p'
        save_name = os.path.join(configs_dir, outfile)
        if outfile in os.listdir(configs_dir):
            if force_recalculate:
                subdict = calculate_means(fname)
                pkl.dump(subdict, open(save_name, 'wb'))
            else:
                subdict = pkl.load(open(save_name, 'rb'))
        else:
            subdict = calculate_means(fname)
            pkl.dump(subdict, open(save_name, 'wb'))
        mean_fields_dict[key] = subdict

    return mean_fields_dict
