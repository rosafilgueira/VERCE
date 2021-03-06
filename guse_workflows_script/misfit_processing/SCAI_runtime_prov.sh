#!/bin/bash -l

export USER=$(whoami)

echo "--------- profile LOAD" 1>&2
echo "--------- profile LOAD"
source /etc/profile
echo "--------- modules.sh LOAD" 1>&2
echo "--------- modules.sh LOAD" 
source /etc/profile.d/modules.sh


module load tools/python/2.7.9

unzip vercepes >/dev/null
PROV="provfold"$(cat control)
mkdir -p $HOME/$PROV
PROV_TARGET_BASE_URL=gsiftp://dir-irods.epcc.ed.ac.uk//UEDINZone/home/public/
SOURCE_BASE_URL=gsiftp://lxlogin1.lrz.de
DATA_TARGET_BASE=gsiftp://dir-irods.epcc.ed.ac.uk/~/verce/
RUN_PATH=$(pwd)

python verce-hpc-pe/src/dirmonitor-dataprov.py $HOME/$PROV $SOURCE_BASE_URL $PROV_TARGET_BASE_URL $DATA_TARGET_BASE