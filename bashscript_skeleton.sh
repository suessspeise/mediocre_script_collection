# function intended to be added to .bashrc or .profile
skeleton(){
        if test -z "$1" ; then
                FILE_PATH="skeleton.sh"
        else
                FILE_PATH="$1.sh"
        fi
        echo '' > ${FILE_PATH}
        cat >> "${FILE_PATH}" << EOF
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


run() {
        echo "this is a generated bash script skeleton"
}

run \$@
        
EOF
}
skeleton $1
