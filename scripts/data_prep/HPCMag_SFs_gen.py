import os
import numpy as np
import pickle as pkl

if __name__=='__main__':
    data_prep_dir = os.path.dirname(os.path.realpath(__file__))
    configs_dir = os.path.join(os.path.abspath(os.path.join(data_prep_dir, '..', '..', 'configs')), '')
    # DEBUG
    #print(f'configs_dir = {configs_dir}')
    seed_HPC = 2025
    print(f'Using random seed for HPC BMag systematic: {seed_HPC}\n')
    np.random.seed(seed_HPC)
    # hall probes
    labels_BP = ['BP1', 'BP2', 'BP3', 'BP4', 'BP5']
    labels_SP = ['SP1', 'SP2', 'SP3']
    labels_HPs = labels_BP + labels_SP
    RMS = 1e-4 # size of SFs
    SFs = 1. + np.random.normal(loc=0, scale=RMS, size=len(labels_HPs))
    one_min_SFs = SFs - 1.
    SFs_dict = {}
    one_min_SFs_dict = {}
    for i in range(len(labels_HPs)):
        SFs_dict[labels_HPs[i]] = SFs[i]
        one_min_SFs_dict[labels_HPs[i]] = one_min_SFs[i]
    print(f'SFs for HPCMagUnc example:\n{SFs_dict}\n')
    print(f'SFs - 1 for HPCMagUnc example:\n{one_min_SFs_dict}\n')
    print(f'mean(SFs-1) = {np.mean(one_min_SFs)}\n')
    outfile = os.path.join(configs_dir, 'HPCMagUnc_SFs.p')
    print(f'Saving to: {outfile}')
    pkl.dump(SFs_dict, open(outfile, 'wb'))
    print('Done.\n')
