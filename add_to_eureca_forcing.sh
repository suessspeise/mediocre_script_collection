#!/bin/bash
#SBATCH --partition=compute
#SBATCH --account=mh0926
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=24
#SBATCH --time=02:00:00
#SBATCH --mail-type=ALL
#SBATCH --mail-user=hernan.campos@mpimet.mpg.de
#SBATCH --output=%x.%j.log
#SBATCH --error=%x.%j.log

# REQUIRES A LOCAL COPY OF FILES here:
workingdir='/work/mh0926/m300872/eureca4K/'
# this can be done like this....:
# eurecapath='/work/mh0010/m300408/DVC-test/EUREC4A-ICON/EUREC4A'
# cp -r $eurecapath/initc/ ./
# cp -r $eurecapath/latbc ./
# cp -r $eurecapath/sst_sic/ ./


# debugging
#shopt -s expand_aliases
#alias ll='ls -lh --color=auto'

# how much is added?
constant=4
cdo_options="-P 8"

# filename without extension as prefix for temporary files
prefix=$(basename $infile .nc)
# to differentiate temporary files
temp_ident="_temporary_"

# 'cdo addc' adds a constant to the entire file. 
# we have to split and merge the dataset, to add to a single field.
# for testing purposes there is a non modifying verison
addc_singlevar(){
	dry_addc_singlevar $1 $2
	# time wet_addc_singlevar $1 $2
}
wet_addc_singlevar(){
	infile=$1
	var=$2
	if ( test -f $infile ) ; then
		printf '\e[32m%s\e[0m' "OK"
		echo ": adding $constant to $infile, variable $var"
	else
		printf '\e[31m%s\e[0m' "FILE NOT FOUND"
		echo ": adding $constant to $infile, variable $var"
	fi
	tfile="${prefix}${temp_ident}${var}.nc"
	cdo ${cdo_options} splitname $infile ${prefix}${temp_ident}
	cdo ${cdo_options} addc,$constant $tfile ${temp_ident}${constant}.nc
	mv "${temp_ident}${constant}.nc" $tfile
	cdo ${cdo_options} -O merge $(ls ${prefix}${temp_ident}*.nc) ${prefix}.nc
	rm ${prefix}${temp_ident}*.nc
}
dry_addc_singlevar(){
	infile=$1
	var=$2
	if ( test -f $infile ) ; then
		printf '\e[32m%s\e[0m' "OK"
		echo ": adding $constant to $infile, variable $var"
	else
		printf '\e[31m%s\e[0m' "FILE NOT FOUND"
		echo ": adding $constant to $infile, variable $var"
	fi
}


# as the variable name is different in different netcdf files, we use 3 separate loops
var='SST'
for filename in ${workingdir}sst_sic/data/*.nc ; do
	addc_singlevar $filename $var
done

var='t'
for filename in ${workingdir}initc/*/*.nc ; do
	addc_singlevar $filename $var
done

var='temp'
for filename in ${workingdir}latbc/*/*.nc ; do
	addc_singlevar $filename $var
done
