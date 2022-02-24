#!/bin/bash
#SBATCH --partition=compute
#SBATCH --account=mh0926
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --time=00:60:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=hernan.campos@mpimet.mpg.de
#SBATCH --output=log/%x.%j.log
#SBATCH --error=log/%x.%j.log

# this is intended to regrid 2D DYAMOND radiation data 
# for comparison with CERES EBAF satelite data
# EBAF is available in 1 x 1 latlon grids
# we use conservative remapping, to conserve the fluxes

monthlist=('01' '02' '03')

# dpp0052
dirname='/work/mh0287/k203123/GIT/icon-aes-dyw3/experiments/dpp0052/'
#inmask='dpp0052_atm_2d_ml_2020'
outmask="dpp0052_radiation_2020"
inmask=$outmask

# dpp0016
#dirname='/work/mh0287/k203123/GIT/icon-aes-dyw_albW/experiments/dpp0016/'
#namemask='dpp0052_atm_2d_ml_2020'
#outmask="dpp0016_radiation_2020"
inmask=$outmask

dyamond_grid='/work/dicad/cmip6-dev/data4freva/model/global/dyamond/NextGEMS/MPIM-DWD-DKRZ/ICON-SAP-5km/Cycle1/atm/fx/gn/grid.nc'


for month in ${monthlist[@]}; do
    infile="${inmask}${month}.nc"
    outfile="${outmask}${month}_1x1.nc"
    echo "Month $month"
    echo ${outfile}
    cdo -P 8 remapcon,global_1.0 -setgrid,$dyamond_grid ${infile} ${outfile}
    echo ""
done

