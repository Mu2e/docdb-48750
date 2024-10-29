import numpy as np

# 3D grid interpolation (standard routine)
#def get_df_interp_func(filename=None, df=None, gauss=True, mm=False, scipy_interp=False, bounds=None, Blabels=['Bx','By','Bz']):
def get_df_interp_func_with_Jacobian(df, bounds=None, Blabels=['Bx','By','Bz']):
    '''
    This factory function will return an interpolating function for any field map. An input x,y,z will output the corresponding Bx,By,Bz or Br,Bphi,Bz. Will decide later if linear interpolation is good enough.

    Assumed file for input has length: meters, Bfield: Gauss
    '''
    df = df.copy()
    # labels
    Bx_l, By_l, Bz_l = Blabels

    xs = df.X.unique()
    ys = df.Y.unique()
    zs = df.Z.unique()

    if bounds is not None:
        xmin = xs[xs < bounds.xmin][-1]
        xmax = xs[xs > bounds.xmax][0]
        ymin = ys[ys < bounds.ymin][-1]
        ymax = ys[ys > bounds.ymax][0]
        zmin = zs[zs < bounds.zmin][-1]
        zmax = zs[zs > bounds.zmax][0]
        query_string = f"X>={xmin} & X<={xmax} & Y>={ymin} & Y<={ymax} & Z>={zmin} & Z<={zmax}"
        df = df.query(query_string)

        xs = df.X.unique()
        ys = df.Y.unique()
        zs = df.Z.unique()

    dx = xs[1]-xs[0]
    dy = ys[1]-ys[0]
    dz = zs[1]-zs[0]

    lx = len(xs)
    ly = len(ys)
    lz = len(zs)

    df_np = df[["X","Y","Z",Bx_l,By_l,Bz_l]].values

    x, y, z, bx, by, bz = df_np.T

    def get_cube(x, y, z):
        a_x, a_y, a_z = len(xs[xs <= x]) - 1, len(ys[ys <= y]) - 1, len(zs[zs <= z]) - 1
        corner_a = (ly * lz) * a_x + (lz) * a_y + a_z
        corner_b = corner_a + lz
        corner_c = corner_a + ly * lz
        corner_d = corner_a + ly * lz + lz
        index_list = [corner_a,corner_a+1,corner_b,corner_b+1,
        corner_c,corner_c+1,corner_d,corner_d+1]
        return df_np[index_list]

    def interp_single(xd,yd,zd,dx,dy,dz,ff):
        # values used often
        o_m_xd = 1-xd
        o_m_yd = 1-yd
        o_m_zd = 1-zd
        # value interpolation
        c00 = ff[0,0,0]*o_m_xd + ff[1,0,0] * xd
        c01 = ff[0,0,1]*o_m_xd + ff[1,0,1] * xd
        c10 = ff[0,1,0]*o_m_xd + ff[1,1,0] * xd
        c11 = ff[0,1,1]*o_m_xd + ff[1,1,1] * xd

        c0 = c00 * o_m_yd + c10 * yd
        c1 = c01 * o_m_yd + c11 * yd
        c = c0 * o_m_zd + c1 * zd

        # derivatives at interpolation point
        # solutions needed
        # c00 / ... derivatives
        dc00_dx = (ff[1,0,0] - ff[0,0,0]) / dx
        dc10_dx = (ff[1,1,0] - ff[0,1,0]) / dx
        dc01_dx = (ff[1,0,1] - ff[0,0,1]) / dx
        dc11_dx = (ff[1,1,1] - ff[0,1,1]) / dx
        # c0 / c1 derivatives
        dc0_dx = dc00_dx * o_m_yd + dc10_dx * yd
        dc1_dx = dc01_dx * o_m_yd + dc11_dx * yd
        dc0_dy = (c10 - c00) / dy
        dc1_dy = (c11 - c01) / dy
        # complete solutions
        dc_dx = dc0_dx * o_m_zd + dc1_dx * zd
        dc_dy = dc0_dy * o_m_zd + dc1_dy * zd
        dc_dz = (c1 - c0) / dz
        dc_dxyz = np.array([dc_dx, dc_dy, dc_dz])

        return c, dc_dxyz

    def interp(p_vec):
        cube = get_cube(*p_vec)

        xx = [cube[0,0], cube[4,0]]
        yy = [cube[0,1], cube[2,1]]
        zz = [cube[0,2], cube[1,2]]

        dx = xx[1] - xx[0]
        dy = yy[1] - yy[0]
        dz = zz[1] - zz[0]

        bxs_grid = cube[:,3].reshape((2,2,2))
        bys_grid = cube[:,4].reshape((2,2,2))
        bzs_grid = cube[:,5].reshape((2,2,2))

        xd = (p_vec[0]-xx[0])/(dx)
        yd = (p_vec[1]-yy[0])/(dy)
        zd = (p_vec[2]-zz[0])/(dz)

        bx, dbx = interp_single(xd,yd,zd, dx, dy, dz, bxs_grid)
        by, dby = interp_single(xd,yd,zd, dx, dy, dz, bys_grid)
        bz, dbz = interp_single(xd,yd,zd, dx, dy, dz, bzs_grid)

        B = np.array([bx, by, bz])
        J = np.array([dbx, dby, dbz])

        return B, J

    return interp
