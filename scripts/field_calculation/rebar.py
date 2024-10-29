####
### TO BE PROCESSED
####
import pandas as pd
import numpy as np
import six.moves.cPickle as pkl
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

# No rebar
df0 = pd.read_csv('/home/shared_data/Bmaps/rebar/DSMap_V15.txt', header=None, names=['X','Y','Z','Bx','By','Bz'], delim_whitespace=True, skiprows=4)
df0 = df0.sort_values(['X','Y','Z'])

# All rebar
df1 = pd.read_csv('../data/Bmaps/DSMap_V15_with_shielding.txt', header=None, names=['X','Y','Z','Bx','By','Bz'], delim_whitespace=True, skiprows=4)
df1 = df1.sort_values(['X','Y','Z'])

# Non-endcap rebar
df2 = pd.read_csv('../data/Bmaps/DSMap_V15_with_shielding_no_endcap.txt', header=None, names=['X','Y','Z','Bx','By','Bz'], delim_whitespace=True, skiprows=4)
df2 = df2.sort_values(['X','Y','Z'])

# Want Rebar, RebarUp, and RebarDown maps
df_rebar = df1.copy()
for var in ['Bx','By','Bz']:
    df_rebar.loc[:,var] -= df0[var]

df_rebarup = df1.copy()
for var in ['Bx','By','Bz']:
    df_rebarup.loc[:,var] *= 1.2
    df_rebarup.loc[:,var] -= 0.2*df2[var]
    df_rebarup.loc[:,var] -= df0[var]

df_rebardo = df1.copy()
for var in ['Bx','By','Bz']:
    df_rebardo.loc[:,var] *= 0.8
    df_rebardo.loc[:,var] += 0.2*df2[var]
    df_rebardo.loc[:,var] -= df0[var]

names = ['Rebar','RebarUp','RebarDown']
for idf, df in enumerate([df_rebar, df_rebarup, df_rebardo]):
    df.eval('X = X/1000', inplace=True)
    df.eval('Y = Y/1000', inplace=True)
    df.eval('Z = Z/1000', inplace=True)
    df.eval('Bx = Bx*10000', inplace=True)
    df.eval('By = By*10000', inplace=True)
    df.eval('Bz = Bz*10000', inplace=True)
    
    df.eval('X = X+3.896', inplace=True)

    df = df.round({'X':3,'Y':3,'Z':3})

    lines = {'Center'        : '(X==0.0) & (Y==0.0)',
             'R=0.8, Phi=0'  : '(X==0.8) & (Y==0.0)',
             'R=0.8, Phi=90' : '(X==0.0) & (Y==0.8)',
             'R=0.8, Phi=180': '(X==-0.8) & (Y==0.0)',
             'R=0.8, Phi=270': '(Y==-0.8) & (X==0.0)'}

    fig, ax = plt.subplots(1,3,figsize=(10,6),sharey=True)
    for i,field in enumerate(['Bx','By','Bz']):
        for label, query in lines.items():
            df_line = df.query(query)
            ax[i].scatter(df_line['Z'], df_line[field], label=label, s=2)
            ax[i].set_xlabel('Z [m]')
            ax[i].set_title(f'{field}')
    handles,labels = ax[2].get_legend_handles_labels()
    fig.tight_layout()
    fig.subplots_adjust(left=0.20,right=0.97)
    fig.legend(handles,labels,loc='center left')
    plt.savefig(f'{names[idf]}.png')

    df = df.set_index(['X','Y','Z'])
    x = list(df.index.levels[0])
    y = list(df.index.levels[1])
    z = list(df.index.levels[2])

    for grid in ['DSCylFMSAll','DSCylFine','DSCartVal']:
        if grid == 'DSCartVal' and names[idf] != 'Rebar': continue
        nominal_map = pd.read_pickle(f'../data/Bmaps/Mu2e_V13_{grid}_Helicalc_All_Coils_All_Busbars.Mu2E.p')
        nominal_map = nominal_map.query('(Z>4.200) & (Z<13.900)')
        
        points_to_eval = np.array(nominal_map[['X','Y','Z']])

        # Use RegularGridInterpolator to get rebar Bx/By/Bz at nominal map points
        for field in ['Bx','By','Bz']:
            data = df[field].values.reshape(len(x),len(y),len(z))
            interp = RegularGridInterpolator((x,y,z),data)
            nominal_map.loc[:,field] += interp(points_to_eval)
                
        # Propagate shifts to Br / Bphi
        nominal_map.eval('Bphi = -Bx*sin(Phi)+By*cos(Phi)', inplace=True)
        nominal_map.eval('Br = Bx*cos(Phi)+By*sin(Phi)', inplace=True)
        
        print(nominal_map)
        pkl.dump(nominal_map, open(f'../data/Bmaps/Mu2e_V13_{grid}_Helicalc_All_Coils_All_Busbars_{names[idf]}.Mu2E.p',"wb"), pkl.HIGHEST_PROTOCOL)

