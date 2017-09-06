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
  python gui.py
