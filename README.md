1) Install psana and cctbx
  # conda
  module load python
  conda create -n gui_demo
  source activate gui_demo

  # psana
  conda install -y --channel lcls-rhel7 psana-conda
  conda install -y -c conda-forge "mpich>=3" mpi4py h5py pytables libtiff=4.0.6
  conda install -y scons
  conda install -y wxpython libiconv Tornado

  # cctbx
  python bootstrap.py hot update --builder=xfel --cciuser=<username> --sfuser=<username>
  python bootstrap.py build --builder=xfel --with-python=`which python` --nproc=32
  cd build; make
