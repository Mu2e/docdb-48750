####
### TO BE PROCESSED
####
import os
from copy import deepcopy
from string import Template
import numpy as np
import pandas as pd
import lmfit as lm
import plotly.express as px
import matplotlib.pyplot as plt

#from plotting import config_plots
#config_plots()

from helicalc import helicalc_dir, helicalc_data
# DEBUG
#from helicalc import helicalc_dir
#helicalc_data = '/home/sdittmer/data/'
from helicalc.geometry import read_solenoid_geom_combined
from helicalc.solenoid_geom_funcs import load_all_geoms
# next two lines are for grid development only
from helicalc.tools import generate_cylindrical_grid_df, generate_cartesian_grid_df
from helicalc.constants import DS_FMS_cyl_grid, DS_FMS_cyl_grid_SP, DS_grid, DSCartVal_grid
# recalculating
from helicalc.solcalc import SolCalcIntegrator
# jacobian calculations
from helicalc.jacobian import div_and_curl_calculations

import sys

# this is where the combined map will go
#outdir = "/home/sdittmer/data/Bmaps/"
outdir = os.path.join(helicalc_data, "Bmaps", "docdb-48750", "")

paramname = 'Mu2e_V13' # Mau13
version = paramname.replace('Mu2e_V', '')

#####
# FMS grid
#####
#region = f'DSCylFMSAll_MetUnc{sys.argv[1]}'
region = f'DSCylFMSAll'
#region = f'DSCartVal'
query_str = '(Y<=0.005) & (Y>=-0.005) & (X<=-3.899) & (X>=-3.909) & (Z>=3.)' # for line near axis
query_str2 = f'(-0.001 <= Y <= 0.001) & (Z==8.8)'

# jacobian?
# yes
#suff = '_Jacobian'
# no
suff = ''

### FIXME! go to correct directory
solcalc_dir = '/home/sdittmer/data/Bmaps/SolCalc_partial/'
#solcalc_file_Template = Template(solcalc_dir+f'{paramname}.SolCalc.{region}_region.standard{suff}.'+'${coilstr}.pkl')
# FIXME! Haven't run SolCalc with Jacobian yet.
solcalc_file_Template = Template(solcalc_dir+f'{paramname}.SolCalc.{region}_region.standard.'+'${coilstr}.pkl')

# geometry file used
geom_df = read_solenoid_geom_combined(helicalc_dir+'dev/params/', paramname)

df_coils, df_interlayer, df_str, df_arc, df_arc_transfer, df_buscon, df_coilcon, df_radial_coils = load_all_geoms(version=version, return_dict=False)
# kludge for itertuples.
df_str.eval('cond_N = `cond N`', inplace=True)
df_arc.eval('cond_N = `cond N`', inplace=True)
df_arc_transfer.eval('cond_N = `cond N`', inplace=True)

def construct_map(outname, coil_type='ideal', include_coils=np.arange(1, 67), include_bus=None, region='DSCylFMS', df_SolCalc=None, df_coil_geom=None,
                  df_str_geom=None, df_arc_geom=None, df_arc_transfer_geom=None, df_radial_coil_geom=None, df_buscon=None,
                  include_interlayer=True, df_SolCalc_distorted=None, include_radial_coils=None, radial_coils_reverse=False,
                  include_buscon=None, include_coilcon=None, paramname=paramname, suff=suff):
    # load all SolCalc coils if not passed in
    if df_SolCalc is None:
        df_SolCalc = pd.read_pickle(solcalc_file_Template.substitute(coilstr="coils_1-66"))
    # make empty list for coils if "None" passed in
    if include_coils is None:
        include_coils = np.array([])
    # set up final dataframe
    df = df_SolCalc.copy()
    print(df)
    df_H = []
    # coils and busbars, treated differently if we only use SolCalc
    if 'HP' in df.columns:
        cols_save = ['X', 'Y', 'Z', 'HP']
    else:
        cols_save = ['X', 'Y', 'Z']
    # save initial info
    df_H.append(df[cols_save])
    # add different types of conductors
    if coil_type=='ideal':
        print('ideal coil loop')
        cols_save = []
        if df_SolCalc_distorted is None:
            # SolCalc stuff
            #cols_save = ['X', 'Y', 'Z', 'HP']
            for c in include_coils:
                for b in ['Bx', 'By', 'Bz']:
                    cols_save.append(f'{b}_solcalc_{c}')
            df = df[cols_save]
        else:
            for c in include_coils:
                for b in ['Bx', 'By', 'Bz']:
                    cols_save.append(f'{b}_solcalc_{c}')
            df = df[cols_save]
            # replace any columns with the distorted SolCalc
            for c in include_coils:
                for b in ['Bx', 'By', 'Bz']:
                    col = f'{b}_solcalc_{c}'
                    if col in df_SolCalc_distorted.columns:
                        df.loc[:, col] = df_SolCalc_distorted[col].values
        df_H.append(df)
    elif coil_type=='helical':
        # helicalc stuff
        # must pass in geometry info. this is a bit clunky...
        # FIXME!
        if df_coil_geom is None:
            raise RuntimeError('Coil geometry ("df_coil_geom") dataframe was not passed in, but is necessary to determine number of layers of each coil.')
        cols_save = []
        # handle any PS+TS coils first
        #cols_save = ['X', 'Y', 'Z', 'HP']
        coils_ideal = include_coils[include_coils <= 55]
        coils_helical = include_coils[include_coils > 55]
        for c in coils_ideal:
            for b in ['Bx', 'By', 'Bz']:
                cols_save.append(f'{b}_solcalc_{c}')
        df = df[cols_save]
        # helical coils next
        df_H.append(df)
        il_warns = 0
#         for i, c in enumerate(coils_helical):
        print('helical coil loop')
        for c in coils_helical:
            row = df_coil_geom.query(f'Coil_Num == {c}').iloc[0]
            nL = int(row.N_layers)
            # grab each layer
            for L in range(1, nL+1):
                cols_save = [f"B{i}_helicalc_c{c}_l{L}" for i in ['x', 'y', 'z']]
                df_ = pd.read_pickle(helicalc_data+f'Bmaps/helicalc_partial/{paramname}.{region}_region.standard-helicalc{suff}.coil_{c}_layer_{L}.pkl')
                df_H.append(df_[cols_save])
            # if multiple layers, grab interlayer connections
            if include_interlayer:
                if (nL > 1):
                    cols_save = [f"B{i}_bus_arc_cn_{c}_il" for i in ['x', 'y', 'z']]
                    df_ = pd.read_pickle(helicalc_data+f'Bmaps/helicalc_partial/{paramname}.{region}_region.standard-helicalc{suff}.coil_{c}_interlayer.pkl')
                    df_H.append(df_[cols_save])
            else:
                if il_warns==0:
                    print("Be aware: helical coils in use, but interlayer connections not included.")
                    il_warns += 1

    # add busbars
    # FIXME! Allow breakdown of different types of straight and arc sections. e.g. tangential vs. longitudinal straight bus bars.
    # e.g. arc vs arc transfer, e.g. arc concentric with coils vs. not
    if not include_bus is None:
        print('bus bar loop')
        if include_bus == 'all':
            df_list = [df_str_geom, df_arc_geom, df_arc_transfer_geom]
            label_list = ['str', 'arc', 'arc']
            full_label_list = ['straight', 'arc', 'arc']
        elif include_bus == 'straight':
            df_list = [df_str_geom]
            label_list = ['str']
            full_label_list = ['straight']
        elif include_bus == 'arc':
            df_list = [df_arc_geom, df_arc_transfer_geom]
            label_list = ['arc', 'arc']
            full_label_list = ['arc', 'arc']
        # select specific conductors from each type of bus bar
        elif type(include_bus) is dict:
            df_list = [df_str_geom[np.isin(df_str_geom.cond_N, include_bus['straight'])],
                       df_arc_geom[np.isin(df_arc_geom.cond_N, include_bus['arc'])],
                       df_arc_transfer_geom[np.isin(df_arc_transfer_geom.cond_N, include_bus['arc_transfer'])]
                      ]
            label_list = ['str', 'arc', 'arc']
            full_label_list = ['straight', 'arc', 'arc']
        else:
            raise NotImplementedError(f'The value "{include_bus}" for argument "include_bus" is invalid! Please use one of the following options: ["all", "straight", "arc"]')
        # loop through busbars
        for df_bus, lab, full_lab in zip(df_list, label_list, full_label_list):
            for row in df_bus.itertuples():
                cn = row.cond_N
                cols = [f"B{i}_bus_{lab}_cn_{cn}" for i in ['x', 'y', 'z']]
                df_ = pd.read_pickle(helicalc_data+f'Bmaps/helicalc_partial/{paramname}.{region}_region.standard-busbar{suff}.cond_N_{cn}_{full_lab}.pkl')
                df_H.append(df_[cols])
    # add radial currentsnp.arange(56, 67)
    if not include_radial_coils is None:
        print('radial coil currents loop')
        if radial_coils_reverse:
            #rev_str = "_reverse"
            rev_str = "_reversed"
        else:
            rev_str = ""
        for c in include_radial_coils:
            #df_ = pd.read_pickle(helicalc_data+f'Bmaps/auxiliary_partial/{paramname}.{region}_region.standard-radial_coil.Coil_Num_{c}_radial{rev_str}.pkl')
            df_ = pd.read_pickle(helicalc_data+f'Bmaps/auxiliary_partial/{paramname}.{region}_region.standard-radial_coil{suff}.Coil_Num_{c:0.1f}_radial{rev_str}.pkl')
            cols_save = []
            cols_rename = {}
            for i in ['x', 'y', 'z']:
                for end in ['in', 'out']:
                    cols_rename[f'B{i}_radial_coil_{c:0.1f}{end}'] = f'B{i}_radial_coil_{c}{end}'
                    cols_save.append(f'B{i}_radial_coil_{c}{end}')
            # rename columns, then save
            df_.rename(columns=cols_rename, inplace=True)
            df_H.append(df_[cols_save])
    # busbar connect
    if not include_buscon is None:
        print('busbar connects loop')
        for c in include_buscon:
            df_ = pd.read_pickle(helicalc_data+f'Bmaps/auxiliary_partial/{paramname}.{region}_region.standard-helicalc{suff}.coil_{c}_buscon.pkl')
            cols_save = []
            cols_rename = {}
            for i in ['x', 'y', 'z']:
                cols_rename[f'B{i}_bus_arc_cn_{c:0.1f}_buscon'] = f'B{i}_bus_arc_cn_{c}_buscon'
                cols_save.append(f'B{i}_bus_arc_cn_{c}_buscon')
            # rename columns, then save
            df_.rename(columns=cols_rename, inplace=True)
            df_H.append(df_[cols_save])
    # coil connect
    if not include_coilcon is None:
        print('coil connects loop')
        for c in include_coilcon:
            df_ = pd.read_pickle(helicalc_data+f'Bmaps/auxiliary_partial/{paramname}.{region}_region.standard-helicalc{suff}.coil_{c}_coilcon.pkl')
            cols_save = []
            cols_rename = {}
            for i in ['x', 'y', 'z']:
                # FIXME! This is a bug in calculation code.
                # cols_rename[f'B{i}_bus_arc_cn_{c:0.1f}_buscon'] = f'B{i}_bus_arc_cn_{c}_coilcon'
                # cols_save.append(f'B{i}_bus_arc_cn_{c}_coilcon')
                # coilcon
                cols_rename[f'B{i}_bus_arc_cn_{c:0.1f}_coilcon'] = f'B{i}_bus_arc_cn_{c}_coilcon'
                cols_save.append(f'B{i}_bus_arc_cn_{c}_coilcon')
            # rename columns, then save
            df_.rename(columns=cols_rename, inplace=True)
            df_H.append(df_[cols_save])
    # combine dataframes
    df_H = pd.concat(df_H, axis=1)
    df = df_H
    # combine the different fields
    for i in ['x', 'y', 'z']:
        cols = []
        for col in df.columns:
            if f'B{i}_' in col:
                cols.append(col)
        if len(cols) > 0:
            eval_str = f'B{i} = '+'+'.join(cols)
            df.eval(eval_str, inplace=True, engine='python')
    if len(cols) > 0:
        # apply scaling
        # T -> gauss
        for i in ['x', 'y', 'z']:
            df.eval(f'B{i} = B{i} * 1e4', inplace=True)
        # drop individual results columns
        if 'HP' in df.columns:
            df = df[['X', 'Y', 'Z', 'HP', 'Bx', 'By', 'Bz']]
        else:
            df = df[['X', 'Y', 'Z', 'Bx', 'By', 'Bz']]
    else:
        if 'HP' in df.columns:
            df = df[['X', 'Y', 'Z', 'HP']]
        else:
            df = df[['X', 'Y', 'Z']]
    # save to output_dir
    df.to_pickle(outdir+outname)
    print(f'saved: {outdir+outname}')
    # calculate Jacobian and add to new df?
    if suff == '_Jacobian':
        # note already converted to Gauss above.
        df_nom, J = div_and_curl_calculations(df, T_to_Gauss=False, m_to_mm=False)
        df_nom.to_pickle(outdir+outname.replace(".pkl", "_Jacobian_df.pkl"))
        sname = outdir+outname.replace(".pkl", "_Jacobian_df.pkl")
        print(f'saved: {sname}')
        return df, df_nom, J
    else:
        return df, None, None

##df_SolCalc = pd.read_pickle(solcalc_file_Template.substitute(coilstr="coils_1-66"))
# FIXME! kludge needed to get the correct grid points
#df_SolCalc = pd.read_pickle(helicalc_data+f'Bmaps/helicalc_partial/Mu2e_V13.{region}_region.standard-busbar{suff}.cond_N_10_arc.pkl')
# add HP -- "add_points_for_Jacobian" needed updating. Really field should be rerun, or load and update each file by hand (not imposssible)
if suff == '_Jacobian':
    df_SolCalc = pd.read_pickle(helicalc_data+f'Bmaps/docdb-48750/TEMP_{region}_SolCalc.pkl')
else:
    df_SolCalc = pd.read_pickle(solcalc_file_Template.substitute(coilstr="coils_1-66"))

region_orig = region
#region_orig, unc = region.split('_')
# from Susan
###df = construct_map(f'{paramname}_{region_orig}_Helicalc_All_Coils_All_Busbars_{unc}.pkl', coil_type='helical', include_coils=np.arange(1, 67), include_bus='all', region=region, df_SolCalc=df_SolCalc, df_coil_geom=geom_df, df_str_geom = df_str, df_arc_geom = df_arc, df_arc_transfer_geom = df_arc_transfer, include_interlayer=True)
#df = construct_map(f'{paramname}_{region}_Helicalc_All_Coils_All_Busbars.pkl', coil_type='helical', include_coils=np.arange(1, 67), include_bus='all', region=region, df_SolCalc=df_SolCalc, df_coil_geom=geom_df, df_str_geom = df_str, df_arc_geom = df_arc, df_arc_transfer_geom = df_arc_transfer, include_interlayer=True)

### BUSBARS (+Radial current)
#df = construct_map(f'{paramname}_{region_orig}_Helicalc_No_Coils_All_Busbars.pkl', coil_type='helical', include_coils=None, include_bus='all', region=region,
#                   df_SolCalc=df_SolCalc, df_coil_geom=geom_df, df_str_geom = df_str, df_arc_geom = df_arc, df_arc_transfer_geom = df_arc_transfer,
#                   df_radial_coil_geom=df_radial_coils, include_interlayer=True, include_radial_coils=np.arange(56, 67), radial_coils_reverse=True,
#                   paramname=paramname)

### BUSBARS (no radial current or with radial current)
# df, df_nom, J = construct_map(f'{paramname}_{region_orig}_Helicalc_No_Coils_All_Busbars.pkl', coil_type='helical', include_coils=None, include_bus='all', region=region,
#                   df_SolCalc=df_SolCalc, df_coil_geom=geom_df, df_str_geom = df_str, df_arc_geom = df_arc, df_arc_transfer_geom = df_arc_transfer,
#                   # no radial
#                   #df_radial_coil_geom=df_radial_coils, include_interlayer=True, include_radial_coils=None, radial_coils_reverse=True,
#                   # with radial, reverse
#                   df_radial_coil_geom=df_radial_coils, include_interlayer=True, include_radial_coils=np.arange(56, 67), radial_coils_reverse=True,
#                   # BAD. with radial, not reverse
#                   #df_radial_coil_geom=df_radial_coils, include_interlayer=True, include_radial_coils=np.arange(56, 67), radial_coils_reverse=False,
#                   paramname=paramname)

# BUSBARS, BUSBAR CONNECTIONS
# df, df_nom, J = construct_map(f'{paramname}_{region_orig}_Helicalc_No_Coils_All_Busbars.pkl', coil_type='helical', include_coils=None, include_bus='all', region=region,
#                   df_SolCalc=df_SolCalc, df_coil_geom=geom_df, df_str_geom = df_str, df_arc_geom = df_arc, df_arc_transfer_geom = df_arc_transfer,
#                   # no radial
#                   df_radial_coil_geom=df_radial_coils, df_buscon=df_buscon, include_interlayer=True, include_radial_coils=None, radial_coils_reverse=True,
#                   # all busbar connectors
#                   include_buscon=np.arange(56, 67),
#                   # no buscon
#                   #include_buscon=None,
#                   paramname=paramname)

# DS coils, with or without busbars, with or without interlayer
# df, df_nom, J = construct_map(f'{paramname}_{region_orig}_Helicalc_No_Coils_All_Busbars.pkl', coil_type='helical',
#                               #include_coils=np.arange(56, 67),
#                               include_coils=None,
#                               include_bus='all',
#                               #include_bus=None,
#                               region=region,
#                               df_SolCalc=df_SolCalc, df_coil_geom=geom_df, df_str_geom = df_str, df_arc_geom = df_arc,
#                               df_arc_transfer_geom = df_arc_transfer,
#                               # no radial
#                               df_radial_coil_geom=df_radial_coils, df_buscon=df_buscon,
#                               #include_interlayer=True,
#                               include_interlayer=False,
#                               include_radial_coils=None,
#                               radial_coils_reverse=True,
#                               # all busbar connectors
#                               include_buscon=np.arange(56, 67),
#                               # no buscon
#                               #include_buscon=None,
#                               paramname=paramname)

# DS coils with busbar replacement
df, df_nom, J = construct_map(f'{paramname}_{region_orig}_Helicalc_All_Coils_No_Busbars.pkl', coil_type='helical',
                              include_coils=np.arange(56, 67),
                              #include_coils=None,
                              #include_bus='all',
                              include_bus=None,
                              region=region,
                              df_SolCalc=df_SolCalc, df_coil_geom=geom_df, df_str_geom = df_str, df_arc_geom = df_arc,
                              df_arc_transfer_geom = df_arc_transfer,
                              # no radial
                              df_radial_coil_geom=df_radial_coils, df_buscon=df_buscon,
                              include_interlayer=True,
                              #include_interlayer=False,
                              include_radial_coils=None,
                              radial_coils_reverse=True,
                              # all busbar connectors
                              #include_buscon=np.arange(56, 67),
                              # no buscon
                              include_buscon=None,
                              # coil connectors
                              include_coilcon=np.arange(56, 67),
                              # no coilcon
                              #include_coilcon=None,
                              paramname=paramname)

# debug
# df = construct_map(f'DEBUG_{paramname}_{region_orig}_Helicalc_No_Coils_All_Busbars.pkl', coil_type='helical', include_coils=None,
#                    include_bus='all',
#                    #include_bus='straight',
#                    region=region,
#                   df_SolCalc=df_SolCalc, df_coil_geom=geom_df, df_str_geom = df_str, df_arc_geom = df_arc, df_arc_transfer_geom = df_arc_transfer,
#                   df_radial_coil_geom=df_radial_coils, include_interlayer=True,
#                   #include_radial_coils=np.arange(56, 67),
#                   include_radial_coils=None,
#                   radial_coils_reverse=True,
#                   paramname=paramname)

df_line = df.query(query_str).copy()
print(df_line)
fig, ax = plt.subplots()

ax.scatter(df_line.Z, df_line.Bz, s=2)
ax.set_xlabel('Z [m]')
ax.set_ylabel('Bz [Gauss]');
plt.show()
