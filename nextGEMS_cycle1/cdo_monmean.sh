#!/bin/bash
#SBATCH --partition=compute
#SBATCH --account=mh0926
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --time=02:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=hernan.campos@mpimet.mpg.de
#SBATCH --output=log/%x.%j.log
#SBATCH --error=log/%x.%j.log

# this is intended to get monthly means of 2D DYAMOND radiation data 
# for comparison with CERES EBAF satelite data

# selection
vars='rlut,rsdt,rsut'
monthlist=('01' '02' '03')

# dpp0052
dirname='/work/mh0287/k203123/GIT/icon-aes-dyw3/experiments/dpp0052/'
namemask='dpp0052_atm_2d_ml_2020'
outmask="dpp0052_radiation_2020"

# dpp0016
dirname='/work/mh0287/k203123/GIT/icon-aes-dyw_albW/experiments/dpp0016/'
namemask='dpp0016_atm_2d_ml_2020'
outmask="dpp0016_radiation_2020"

for month in ${monthlist[@]}; do
    outfile="${outmask}${month}.nc"
    echo "Month ${month}"
    echo ${outfile}

    cdo -P 8 -monmean -cat [ -apply,"-daymean -selname,${vars}" [ "${dirname}${namemask}${month}*" ] ] ${outfile}

    # dry testing
    #echo "${dirname}${namemask}${month}*" 
    #ls ${dirname}${namemask}${month}*
    echo ""
done
