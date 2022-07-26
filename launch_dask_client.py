import pathlib
import getpass
# launches a dask Cluster
# this has MACHINE SPECIFIC (e.g. `queue` == partition name) and USER SPECIFIC (`account_name`) default parameter.

import tempfile
import dask_jobqueue as djq
import dask.distributed as ddist

def launch_dask_client(
    account_name = 'mh0926', # Account that is going to be 'charged' fore the computation
    queue = 'compute', # Name of the partition we want to use
    job_name = 'LC', # Job name that is submitted via sbatch
    memory = "60GiB", # Max memory per node that is going to be used - this depends on the partition
    cores = 72, # Max number of cores per task that are reserved - also partition dependend
    walltime = '3:00:00' # Walltime - also partition dependent
    ):
    scratch_dir = pathlib.Path('/scratch') / getpass.getuser()[0] / getpass.getuser() # Define the users scratch dir
    # Create a temp directory where the output of distributed cluster will be written to, after this notebook
    # is closed the temp directory will be closed
    dask_tmp_dir = tempfile.TemporaryDirectory(dir=scratch_dir, prefix=job_name)
    cluster = djq.SLURMCluster(memory=memory,
                           cores=cores,
                           project=account_name,
                           walltime=walltime,
                           queue=queue,
                           name=job_name,
                           scheduler_options={'dashboard_address': ':187'},
                           local_directory=dask_tmp_dir.name,
                           job_extra=[f'-J {job_name}', 
                                      f'-D {dask_tmp_dir.name}',
                                      f'--begin=now',
                                      f'--output={dask_tmp_dir.name}/LOG_cluster.%j.o',
                                      f'--output={dask_tmp_dir.name}/LOG_cluster.%j.o'
                                     ],
                           interface='ib0')
    cluster.scale(jobs=1) #order n nodes that will give us n*memory of distributed memory and n*cpus-per-task cores to work on
    return ddist.Client(cluster)

if __name__ == 'main':
    # dask_client = launch_dask_client()
    pass
