#!/bin/bash -e
                                                                                                                        
readonly VE_LOCATION=/tmp/reqExec_pkg_ve

# TODO: remove this once pyinstaller 3.4 is released and
# https://github.com/pyinstaller/pyinstaller/issues/2849 is resolved
install_pyinstaller() {
  pushd /home
    if [ ! -d pyinstaller ]; then
      git clone https://github.com/Bharath92/pyinstaller.git
    fi

    pushd pyinstaller
      git checkout 9d5a9b02c13c9e8ace6feb1f704189c51bdba1bd
      python setup.py install
    popd
  popd
}

install_prereqs() {
  sudo apt-get install -yy git zlib1g-dev
  rm -rf $VE_LOCATION || true
  export LC_ALL=C
  install_pyinstaller
  pip install virtualenv
}

init_ve() {
  virtualenv -p /usr/bin/python $VE_LOCATION
  source $VE_LOCATION/bin/activate
  pip install -r requirements.txt
}

package() {
  rm -rf dist || true
  pyinstaller --clean --hidden-import=requests main.py
}

main() {
  install_prereqs
  init_ve
  package
}

main
