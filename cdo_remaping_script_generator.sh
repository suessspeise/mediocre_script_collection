#!/usr/bin/env bash
script_dir="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Data info
exp_name='dpp0052_atm_2d_ml_2020'
input_path='/work/mh0287/k203123/GIT/icon-aes-dyw3/experiments/dpp0052/'
resolution_path='/work/bb1153/m300901/NextGEMS_Cycle01/resolution.txt'
weight_path='/work/bb1153/m300901/NextGEMS_Cycle01/weightfile2.nc'

# Node/Sbatch info
cpu_time='01:30:00'
partition_name='compute2,compute'
num_nodes=1
account_number='bb1153'
months="01 02"
day_starts="0 1 2 3"
job_name="dpp0052"

output_path=${script_dir}'/output/'
path_files=${script_dir}'/'
log_path=${script_dir}'/objects_output'

for month in ${months}; do
  for day_start in ${day_starts}; do
    FILE_PATH='./'$exp_name${month}${day_start}x'.run'
cat >> "${FILE_PATH}" << EOF
#!/usr/bin/env bash

#=============================================================================
# mistral cpu batch job parameters
# --------------------------------
#SBATCH --account=${account_number}
#SBATCH --job-name=${job_name}-${month}${day_start}x
#SBATCH --partition=${partition_name}
#SBATCH --chdir=${path_files}
#SBATCH --nodes=${num_nodes}
#SBATCH --threads-per-core=2
# the following is needed to work around a bug that otherwise leads to
# a too low number of ranks when using compute,compute2 as queue
#SBATCH --output=${log_path}/$exp_name${month}${day_start}x.o
#SBATCH --error=${log_path}/$exp_name${month}${day_start}x.o
#SBATCH --exclusive
#SBATCH --time=${cpu_time}
#=============================================================================

if [ ! -d "${input_path}" ]; then
  echo "Error: ${input_path} not found"
  exit 1
fi
if [[ ! -d "${output_path}" ]]; then
  mkdir -p "${output_path}"
fi
if [[ ! -d "${log_path}" ]]; then
  mkdir -p "${log_path}"
fi

echo "##START RUN ${exp_name}${month}${day_start}"
echo "Select data and remap"
cdo -P 16 -remap,"${resolution_path}","${weight_path}" -select,name=pr,clt ${input_path}${exp_name}${month}${day_start}*.nc ${output_path}${exp_name}${month}${day_start}x.nc
echo "Sum daily"
cdo -P 16 -daysum ${output_path}${exp_name}${month}${day_start}x.nc ${output_path}${exp_name}${month}${day_start}x_sum.nc 
echo "##END RUN ${exp_name}${month}${day_start}"
EOF

done
done

