#!/bin/bash
#SBATCH --job-name=interpolate_pl  # Specify job name
#SBATCH --partition=compute,compute2    # Specify partition name
#SBATCH --ntasks=1             # Specify max. number of tasks to be invoked
#SBATCH --time=00:30:00        # Set a limit on the total run time
##SBATCH --mail-type=FAIL       # Notify user by email in case of job failure
#SBATCH --account=mh1049       # Charge resources on this project account
#SBATCH --output=my_job.o%j    # File name for standard output
#SBATCH --error=my_job.e%j     # File name for standard error output

set -xe

#This script interpolates 3D data to horizontally constant pressure levels. In this example, the pressure levels found over the ocean are used as the target to be interpolated on, specified in "nlev" below. 

plevs="1.906283,2.968396,4.481492,6.61451,9.526982,13.41836,18.52883,25.12494,33.53812,44.21873,57.69998,74.61192,95.70101,121.8712,154.2202,194.159,243.4279,303.9138,378.0523,468.5392,578.3923,710.9384,869.634,1058.485,1281.635,1543.777,1850.049,2205.059,2611.889,3072.785,3588.344,4157.792,4781.695,5461.337,6197.559,6991.115,7840.828,8740.436,9680.607,10655.46,11661.57,12689.84,13728.33,14768.18,15817.59,16888.67,17996.39,19158.18,20375.35,21649.44,22982.07,24375.29,25831.27,27352.11,28940.29,30598.22,32328.44,34133.54,36016.38,37981,40032.05,42174.65,44413.65,46753.34,49196.99,51746.3,54376.46,57039.22,59708.01,62375.36,65033.63,67674.36,70289.82,72871.8,75411.29,77899.77,80328.52,82687.39,84965.45,87151.59,89234.12,91201.06,93040.28,94738.95,96283.12,97657.91,98846.66,99828.92,100575.6,101028.5" #this is the list of pressure levels on which the data will be interpolated on
input_file_3d="/mnt/lustre02/work/mh1126/m300773/DYAMONDwinter/coupled/1x1deg/dpp0029/dpp0029_atm_3d_all_ml_20200131_1x1.nc"
ps_file="/mnt/lustre02/work/mh1126/m300773/DYAMONDwinter/coupled/1x1deg/dpp0029/dpp0029_atm_2d_ml_20200131_1x1.nc"
output_file="/mnt/lustre02/work/mh1126/m300773/DYAMONDwinter/coupled/1x1deg/dpp0029/dpp0029_atm_3d_all_pl_20200131_1x1.nc"

cdo -P 8 -O ap2pl,${plevs} -merge [ ${input_file_3d} -selname,ps ${ps_file} ] ${output_file}
