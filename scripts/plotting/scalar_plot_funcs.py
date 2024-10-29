import os
import sys
import argparse
import time
import numpy as np
import pandas as pd
import pickle as pkl
import matplotlib.pyplot as plt

from helicalc.solenoid_geom_funcs import cylinder, get_3d_straight, get_3d_arc
from BFieldPINN.plotter import(
    # utils
    check_plot_dir,
    config_plots,
    ticks_in,
    ticks_sizes,
    get_label,
)

### set up base of plot (phi)
def plot_phi(df, mesh_dict, phi_col, title, plotfile=None, equal_colorbars=False, add_pos_x=True):
    fig, ax = plt.subplots(figsize=(14, 6), constrained_layout='constrained')
    #cax2 = fig.add_axes([0.28, 0.81, 0.5, 0.05])
    cax2 = fig.add_axes([0.28, 0.78, 0.5, 0.05])
    if equal_colorbars:
        vmin = df[phi_col].min()
        vmax = df[phi_col].max()
        cax1 = None
        cax3 = None
    else:
        vmin = None
        vmax = None
        #cax1 = fig.add_axes([0.15, 0.195, 0.02, 0.5])
        #cax3 = fig.add_axes([0.89, 0.195, 0.02, 0.5])
        cax1 = fig.add_axes([0.15, 0.175, 0.02, 0.5])
        cax3 = fig.add_axes([0.89, 0.175, 0.02, 0.5])
    n_points = 0
    for i, tup in enumerate(zip(['Z0', 'BODY', 'Z1'], [['X', 'Y'], ['Z', 'RPhi'], ['X', 'Y']], [[' [m]', ' [m]'], [' [m]', ' [rad]'], [' [m]', ' [m]']],
                            ['viridis', 'viridis', 'viridis'], [cax1, cax2, cax3], ['vertical', 'horizontal', 'vertical'], ['left', 'top', 'right'],)):
        loc, coords, units, cscale, cax, orient, tick_pos = tup
        #print(f'Plotting area {loc}')
        qstr = f'area == "{loc}"'
        #print(df.columns)
        df_ = df.query(qstr)
        #print(df_)
        #print(df_.columns)
        sfs = [df_['z_sf'].iloc[0], df_['rphi_sf'].iloc[0]]
        #sfs = [1, -1]
        qm = ax.pcolormesh(sfs[0]*mesh_dict[loc]['X'] + df_['X_offset'].iloc[0], sfs[1]*mesh_dict[loc]['Y'] + df_['Y_offset'].iloc[0],
                           df_[phi_col].values.reshape(mesh_dict[loc]['X'].shape), vmin=vmin, vmax=vmax, rasterized=True)
        reorient=True
        if equal_colorbars:
            if loc == 'BODY':
                cb = fig.colorbar(qm, cax=cax, orientation=orient)
            else:
                reorient=False
        else:
            cb = fig.colorbar(qm, cax=cax, orientation=orient)
        if reorient:
            if orient == 'vertical':
                cax.yaxis.set_ticks_position(tick_pos)
            else:
                cax.xaxis.set_ticks_position(tick_pos)
        # add a point in the +x direction?
        if add_pos_x and (coords[0] == 'X'):
            df0 = df_[~np.isnan(df_[phi_col])]
            #point = df0.iloc[df0['X'].argmax()]
            points = df0[np.isclose(df0['X'], df0['X'].max())]
            if n_points < 1:
                label = r'$+x$'
            else:
                label = None
            ax.scatter([sfs[0]*(points.X.iloc[0]+0.05) + df_['X_offset'].iloc[0]], [points.Y.mean()], s=25, marker='+', c='blue', label=label)
            n_points += 1
    # if add_busbars:
    #     df0 = df.query('area == "BODY"').iloc[0]
    #     x_off = df0.X_offset
    #     y_off = df0.Y_offset
    #     ax = plot_busbars(df_dict, ax, x_off, y_off, z_sf=body_sfs[0], rphi_sf=body_sfs[1], R0=df0.R, add_current=True)
    #if add_pos_x or add_busbars:
    if add_pos_x:
        ax.legend(loc='upper right').set_zorder(100)
        #ax.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9)).set_zorder(100)
    # add empty points for clearer boundaries
    ax.scatter([8.0, 8.9 - 7.0, 8.9 + 7.0, 8.0], [3.75, 0.0, 0.0, -2.6], alpha=0.0)
    # format
    ax.axis('equal')
    ax = ticks_in(ax)
    ax.set_title(title)
    ax.set_xlabel(r'$z$ (or $\pm x$) [m]')
    ax.set_ylabel(r'$-r \phi + \pi$ (or $y$) [m]')
    if not plotfile is None:
        fig.savefig(plotfile+'.pdf', dpi=100)
        fig.savefig(plotfile+'.png', dpi=100)
    #fig.savefig(plotfile+'.png', dpi=100)
    return fig, ax


### functions related to overlays of busbars and coils
def get_cylinder_inner_surface_xyz_corners(df, x0, coil_num, R0=None):
    c = df.query(f'Coil_Num == {coil_num}').iloc[0]
    if not R0 is None:
        r = R0
    else:
        r = c.Ri
    x, y, z = cylinder(r, c.L, xc=c.x, yc=c.y, zc=c.z,
                       pitch=c.rot0, yaw=c.rot1, roll=c.rot2,
                       nt=2, nv=2, flip_angles=False, theta_from_origin=True)
    return x-x0, y, z

def plot_coil(ax, df, coil_num, x0, R0, zsf, rsf, x_off, y_off, zorder, add_current=True, add_label=False):
    if R0 is None:
        y_func = lambda r, phi: rsf*r*phi + y_off
        label_suff = ''
    else:
        y_func = lambda r, phi: rsf*R0*phi + y_off
        #label_suff = '\n(projected)'
        label_suff = ''
    if add_label:
        label = 'Coils'+label_suff
    else:
        label = None
    x, y, z = get_cylinder_inner_surface_xyz_corners(df, x0, coil_num=coil_num, R0=R0)
    phi = np.arctan2(y, x)
    phi[phi < 0] = phi[phi < 0] + 2*np.pi
    r = (x**2 + y**2)**(1/2)
    #rphi = r * phi
    rphi = y_func(r, phi)
    # plot coil projection
    ax.fill_between(zsf*z[:, 0]+x_off, y1=y_func(r[:,0], phi[:,0]), y2=y_func(r[:,1], phi[:,1]),
                    #color='green',
                    #facecolor=None,
                    color='none',
                    #alpha=0.2,
                    alpha=0.2,
                    #edgecolor='green',
                    edgecolor='black',
                    linewidth=1, zorder=zorder, label=label)
    if add_current:
        zs = np.linspace(z.min(), z.max(), 3)[1:]
        # zs = np.arange(z.min(), z.max() + 0.4, 0.4)[1:]
        # if len(zs) < 2:
        #     zs = np.linspace(z.min(), z.max(), 3)[1:]
        #rphis = np.linspace(rphi.min(), rphi.max(), 5)[:-1]
        rphis = np.linspace(rphi.min(), rphi.max(), 5)[1:]
        dr = rphis[1] - rphis[0]
        #rphis = rphis + dr/5.
        rphis = rphis - dr/5.
        dz = zs[1] - zs[0]
        zs = zs - dz/2.
        for z_ in zs:
            for rp_ in rphis:
                ax.arrow(zsf*z_+x_off, rp_, 0., -0.75,
                         #color='green',
                         color='black',
                         alpha=0.1, linewidth=0.05, width=0.03, zorder=zorder+1)
    return ax

def plot_straight(ax, df, iloc, x0, R0, zsf, rsf, x_off, y_off, zorder, add_current=True, add_label=False):
    nz = 10
    minZ = 10
    if R0 is None:
        y_func = lambda r, phi: rsf*r*phi + y_off
        label_suff = ''
    else:
        y_func = lambda r, phi: rsf*R0*phi + y_off
        #label_suff = '\n(projected)'
        label_suff = ''
    df0 = df.iloc[iloc]
    L = df0.length
    nz_L = max(int(nz*L), minZ)
    x, y, z = get_3d_straight(df, bar_num=df0['cond N'], nz=nz_L, center=True)
    x = x-x0
    r = (x**2 + y**2)**(1/2)
    phi = np.arctan2(y, x)
    phi[phi<0] = phi[phi<0] + 2*np.pi
    x_ends = [zsf*z[0]+x_off, zsf*z[-1]+x_off]
    y_ends = [y_func(r[0], phi[0]), y_func(r[-1], phi[-1])]
    if add_label:
        label = f'Busbars{label_suff}'
    else:
        label = None
    # plot bar
    ax.plot(x_ends, y_ends, '-',
            #color='black',
            color='red',
            linewidth=2,
            #alpha=0.4,
            alpha=0.3,
            label=label, zorder=zorder)
    if add_current:
        i0 = nz_L//2
        # hand adjustments for clarity
        if df0['cond N'] == 12:
            i0 = int(7*nz_L/16)
        i1 = i0+1
        z0 = zsf*z[i0]+x_off
        z1 = zsf*z[i1]+x_off
        y0 = y_func(r[i0], phi[i0])
        y1 = y_func(r[i1], phi[i1])
        dz = z1 - z0
        dy = y1 - y0
        ax.arrow(z0, y0, dz, dy,
                 #color='gray',
                 color='red',
                 #alpha=0.8,
                 alpha=0.4,
                 linewidth=1., width=0.03, zorder=zorder+1)
    return ax

def plot_arc(ax, df, iloc, x0, R0, zsf, rsf, x_off, y_off, zorder, add_current=True, add_label=False):
    nphi = 30
    if R0 is None:
        y_func = lambda r, phi: rsf*r*phi + y_off
        label_suff = ''
    else:
        y_func = lambda r, phi: rsf*R0*phi + y_off
        #label_suff = '\n(projected)'
        label_suff = ''
    df0 = df.iloc[iloc]
    x, y, z = get_3d_arc(df, bar_num=df0['cond N'], nphi=nphi)
    # center is the mean of the 4 edges
    # pattern is: x[0], x[1], x[2], x[3] == four corners of the cross-section
    x = np.mean(x.reshape((nphi, -1)), axis=1)
    y = np.mean(y.reshape((nphi, -1)), axis=1)
    z = np.mean(z.reshape((nphi, -1)), axis=1)
    x = x - x0
    r = (x**2 + y**2)**(1/2)
    phi = np.arctan2(y, x)
    phi[phi<0] = phi[phi<0] + 2*np.pi
    # split bar if looping around cut point
    ys = y_func(r, phi)
    dy0 = np.sign(np.diff(ys)[0])
    dys = np.sign(np.diff(ys))
    if not all(dys == dy0): # splitting behavior
    #if False: # old behavior
        i_split = np.where(dys != dy0)[0][0] + 1
        z_list = [z[:i_split], z[i_split:]]
        y_list = [ys[:i_split], ys[i_split:]]
    else:
        z_list = [z]
        y_list = [ys]

    for i, tup in enumerate(zip(z_list, y_list)):
        z_, y_ = tup
        if add_label and (i == 0):
            label = f'Busbars{label_suff}'
        else:
            label = None
        # plot bar
        ax.plot(zsf*z_+x_off, y_, '-',
                #color='black',
                color='red',
                linewidth=2,
                #alpha=0.4,
                alpha=0.3,
                label=label, zorder=zorder)
        if add_current:
            nphi_ = len(z_)
            i0 = nphi_//2
            # hand tune here
            #if df0['cond N'] == 12:
            #    i0 = int(7*nz_L/16)
            i1 = i0+1
            z0 = zsf*z_[i0]+x_off
            z1 = zsf*z_[i1]+x_off
            y0 = y_[i0]
            y1 = y_[i1]
            dz = z1 - z0
            dy = y1 - y0
            ax.arrow(z0, y0, dz, dy,
                     #color='gray',
                     color='red',
                     #alpha=0.8,
                     alpha=0.4,
                     linewidth=1., width=0.03, zorder=zorder+1)
    return ax

def plot_busbars_coils_RZ_projection(df_phi, df_dict, plot_dict, ax, x0, add_current=True):
    # arc
    nphi = 30
    # grab values from df_phi
    df_p = df_phi.query('area == "BODY"')
    x_off = df_p.X_offset.iloc[0]
    y_off = df_p.Y_offset.iloc[0]
    z_sf = df_p.z_sf.iloc[0]
    rphi_sf = df_p.rphi_sf.iloc[0]
    R0 = df_p.R.iloc[0]
    # loop through all types of bus we want to plot
    bus_label = False
    for k, config in plot_dict.items():
        df_ = df_dict[k].iloc[config['index_range'][0]:config['index_range'][1]]
        #print(df_)
        if config['type'] == 'arc':
            for i in range(len(df_)):
                #print(i)
                #print(ax)
                if (i == 0) and (not bus_label):
                    add_label = True
                    bus_label = True
                else:
                    add_label = False
                ax = plot_arc(ax, df_, iloc=i, x0=x0, R0=R0, zsf=z_sf, rsf=rphi_sf,
                              x_off=x_off, y_off=y_off, zorder=config['z'],
                              add_current=add_current, add_label=add_label)
        elif config['type'] == 'straight':
            for i in range(len(df_)):
                #print(i)
                #print(ax)
                if (i == 0) and (not bus_label):
                    add_label = True
                    bus_label = True
                else:
                    add_label = False
                ax = plot_straight(ax, df_, iloc=i, x0=x0, R0=R0, zsf=z_sf, rsf=rphi_sf,
                                   x_off=x_off, y_off=y_off, zorder=config['z'],
                                   add_current=add_current, add_label=add_label)
        elif config['type'] == 'coil':
            for i, c in enumerate(df_.Coil_Num.values):
                #print(c)
                if i == 0:
                    add_label=True
                else:
                    add_label=False
                ax = plot_coil(ax, df_, coil_num=c, x0=x0, R0=R0, zsf=z_sf, rsf=rphi_sf,
                               x_off=x_off, y_off=y_off, zorder=config['z'],
                               add_current=add_current, add_label=add_label)
        else:
            bt = config['bustype']
            raise ValueError(f'"type"=="{bt}" is not supported. Please try again using "type" from ["arc", "straight", "coil"].')
    return ax
