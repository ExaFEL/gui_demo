# Install psana and cctbx

  ## Construct conda environment on pslogin (conda version 4.6.14)
  conda create -y -n gui_demo <br />
  conda activate gui_demo <br />
  conda install -y --channel lcls-rhel7 psana-conda <br />
  conda install -y future libtiff tqdm=4.23.4 wxpython=3 <br />
  conda install -y -c conda-forge orderedset procrunner

  ## Get CCTBX sources on pslogin 
  python bootstrap.py hot update --builder=xfel --cciuser=\<username\>

  ## Build CCTBX on psana
  python bootstrap.py build --builder=xfel --use-conda=${CONDA_PREFIX} --nproc=32

  ## Starting GUI
  source \<CCTBX installation\>/build/setpaths.sh <br />
  libtbx.python gui_demo/gui.py

# Old instructions for Cori
  ## conda
  module load python <br />
  conda create -n gui_demo <br />
  source activate gui_demo

  ## psana
  conda install -y --channel lcls-rhel7 psana-conda <br />
  conda install -y -c conda-forge "mpich>=3" mpi4py h5py pytables libtiff=4.0.6 <br />
  conda install -y scons <br />
  conda install -y wxpython libiconv Tornado <br />

  ## cctbx
  python bootstrap.py hot update --builder=xfel --cciuser=\<username\> --sfuser=\<username\> <br />
  python bootstrap.py build --builder=xfel --with-python=\`which python\` --nproc=32 <br />
  cd build; make

  ## Coot
  wget 'https://www2.mrc-lmb.cam.ac.uk/personal/pemsley/coot/binaries/release/coot-0.8.7-binary-Linux-x86_64-openSUSE-12.3-python-gtk2.tar.gz' <br />
  tar -xf coot-0.8.7-binary-Linux-x86_64-openSUSE-12.3-python-gtk2.tar.gz <br />
  wget 'https://ftp-osl.osuosl.org/pub/libpng/src/libpng15/libpng-1.5.29.tar.xz' <br />
  module load zlib <br />
  tar -xf libpng-1.5.29.tar.xz <br />
  cd libpng-1.5.29 <br />
  ./configure --prefix=\<Coot directory\> <br />
  make; make install <br />

# Running
  module load python <br />
  source activate gui_demo <br />
  source \<cctbx installation>/build/setpaths_all.sh <br />
  export COOT_PREFIX=\<Coot directory\> <br />
  export GUI_DEMO_PREFIX=\<gui_demo directory\> <br />
  python gui.py
  
# Quick Start Guide
  Guide to displaying beta-blip example. This requires downloading an example json, mtz, and pdb file. <br />
  Download gui_demo_example folder from https://stanford.box.com/s/khiepwwd7740u2u5s278rgj7infmwnq8 <br />
  Unzip gui_demo_example.zip <br />
  This folder contains the directory structure: <br />
      . <br />
      +-- _beta-blip_refine <br />
      |   +-- beta-blip_refine.json <br />
      |   +-- beta-blip_refine_001.mtz <br />
      |   +-- beta-blip_refine_001.pdb <br />
  Notice that the files must be named after the folder, i.e. filename starts with beta-blip_refine <br />
  Numbering convention for the pdb and mtz files start from 001 to 999. The electron density with the largest number will be displayed. <br />
  Json file contains the crystallography statistics.  <br />
  
  conda activate gui_demo <br />
  source \<cctbx installation>/build/setpaths_all.sh <br />
  export COOT_PREFIX=\<Coot directory\> <br />
  export GUI_DEMO_PREFIX=\<gui_demo directory\> <br />
  python gui.py -d \<gui_demo_example directory> <br />
