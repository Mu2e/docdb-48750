# TO BE FILLED IN
# run dataframeprod on: nominal field with rebar, field with busbars only

import os

from mu2e import mu2e_ext_path
from mu2e.dataframeprod import DataFrameMaker

if __name__=='__main__':
    f_list = [
        'Mu2e_V13_DSCylFMSAll_Helicalc_No_Coils_All_Busbars', # Model 6
        'Mu2e_V13_DSCylFMSAll_Helicalc_All_Coils_No_Busbars', # Model 6
    ]
    model_list = [
        '6',
        '7',
    ]

    for f, model in zip(f_list, model_list):
        print(f'Processing model {model}: {f}')
        infile = os.path.join(mu2e_ext_path, 'Bmaps', 'docdb-48750', f)
        infile_val = os.path.join(mu2e_ext_path, 'Bmaps', 'docdb-48750', f.replace('DSCylFMSAll', 'DSCartVal'))
        # run on DSCylFMSAll
        data_maker = DataFrameMaker(
            infile, input_type='pkl', field_map_version='helicalc_coils')
        data_maker.do_basic_modifications(-3.904, descale=False)
        data_maker.make_dump('.Mu2E')
        print(data_maker.data_frame.head())
        print(data_maker.data_frame.tail())
        # run on DSCartVal
        data_maker_val = DataFrameMaker(
            infile_val, input_type='pkl', field_map_version='helicalc_coils')
        #print('__init__ done.')
        data_maker_val.do_basic_modifications(-3.904, descale=False, enforcePhiVals=False)
        #print('do_basic_modifications done.')
        data_maker_val.make_dump('.Mu2E')
        #print('make_dump done.')
        print(data_maker_val.data_frame.head())
        print(data_maker_val.data_frame.tail())
        print('\n\n')
