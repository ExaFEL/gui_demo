# Install psana and cctbx
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
  python bootstrap.py build --builder=xfel --with-python=`which python` --nproc=32 <br />
  cd build; make

# Running
  module load python <br />
  source activate gui_demo <br />
  source \<cctbx installation>/build/setpaths_all.sh
  python gui.py
