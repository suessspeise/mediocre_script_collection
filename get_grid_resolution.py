# calculates grid "resolution" from ICON grid files
# resolution is a difficult term, as it is not well defined for triangular grids
# we can use either 
#  - triangle edge length or
#  - triangle surface area or
#  - the edge length of a equivalent square (with the same surface as the triangle)
#
# The real author of this code is Tobias Kölling. Thank you Tobi.

import xarray as xr
import numpy as np

def mean_triangle_edge(grid):
    # get the coordinates of all vertices, put into vectors, join to 'v'
    v = np.stack([grid.cartesian_x_vertices, grid.cartesian_y_vertices, grid.cartesian_z_vertices], axis=1)
    # get list of vertices for each edge
    voe = grid.edge_vertices.values - 1
    # get cartesian vectors for vertices (a and b) of each edge 
    a,b = v[voe]
    # calculate mean and multiply by sphere radius 
    # (in ICON grid files the sphere radius is == 1)
    #     it can be converted via the grid file attribute 'sphere_radius' (radius in m)
    #     for dyamond "semi_major_axis" == "sphere_radius"
    #     for eureca  "sphere_radius" is missing
    return np.linalg.norm(a - b, axis=-1).mean() * grid.attrs["semi_major_axis"]

def mean_triangle_area(grid, method='cell_area'):
    # two methods exist of calculating the mean triangle area
    if method not in ['cell_area', 'sphere_slice']:
        raise ValueError("mean_triangle_area: given method unknown.")
        return -1
    # either dividing the total sphere surface by the number of triangles
    # (which does only work for global grids)
    if method == 'sphere_slice':
        return 4 * np.pi * grid.attrs["semi_major_axis"] ** 2 / grid.dims["cell"]
    # or using the grid file value 'cell_area'
    # (which is not always given)
    elif method == 'cell_area':
        return grid.cell_area.values.mean()

def equivalent_square_edge(grid, method='cell_area'):
    return np.sqrt(mean_triangle_area(grid, method))


def print_resolution_summary(grid):
    print('mean triangle edge lenght: ', mean_triangle_edge(grid), 'm')
    print()
    print('edge length of equivalent square with equal surface: ', equivalent_square_edge(grid, method='sphere_slice'), 'm')
    print('calculated as: sphere surface / number of cells')
    print()
    print('edge length of equivalent square with equal surface: ', equivalent_square_edge(grid, method='cell_area'))
    print('calculated as: mean of cell size attribute')
    print()

if __name__ == "__main__":
    # get grid files of different simulations
    grid_r02b09 = xr.open_dataset("/pool/data/ICON/grids/public/mpim/0015/icon_grid_0015_R02B09_G.nc")
    eureca_dir = '/work/mh0010/m300408/DVC-test/EUREC4A-ICON/EUREC4A/experiments/EUREC4A/'
    grid_eur01 = xr.open_dataset(eureca_dir + 'grid_dynamics_1.nc')
    grid_eur02 = xr.open_dataset(eureca_dir + 'grid_dynamics_2.nc')
    
    print_resolution_summary(grid_eur01)
    print_resolution_summary(grid_r02b09)
