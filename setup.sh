#!/bin/bash

# Set up environment for GUI demo
export PROJECT_DIR=/project/projectdirs/lcls
export SOFTWARE_ROOT=${PROJECT_DIR}/bkpoon/software
export CONDA_ROOT=${SOFTWARE_ROOT}/conda_root
export PHENIX_ROOT=${SOFTWARE_ROOT}/phenix_root

# load conda environment
source ${CONDA_ROOT}/miniconda/bin/activate myEnv

# load Phenix environment or cctbx.xfel environment for GUI
#source ${PHENIX_ROOT}/phenix-installer-dev-2880-source/build/setpaths_all.sh
source ${CONDA_ROOT}/build/setpaths_all.sh

# Coot
export COOT_PREFIX=${SOFTWARE_ROOT}/coot-Linux-x86_64-openSUSE-12.3-gtk2-python
alias coot='${COOT_PREFIX}/bin/coot --no-guano'

# merge.sh environment
export MERGE_ROOT=${PROJECT_DIR}/bkpoon/gui_test/merge_root
export TARDATA=${PROJECT_DIR}/bkpoon/gui_test/test_data/r0108*.tar

# GUI demo
alias run_gui='python ${SOFTWARE_ROOT}/gui_demo/gui.py -d ${MERGE_ROOT}'
alias create_data='\
for i in `seq 1 3`; do \
  TAG=${USER}_${i} MULTINODE=True ${CONDA_ROOT}/modules/exafel_project/nks/merge_v02.sh 32;\
  TAG=${USER}_${i} MULTINODE=False ${CONDA_ROOT}/modules/exafel_project/nks/merge_v02.sh 32;\
done'
