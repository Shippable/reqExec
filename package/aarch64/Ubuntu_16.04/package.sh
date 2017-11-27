#!/bin/bash -e

readonly VE_LOCATION=/tmp/reqExec_pkg_ve
readonly PYINSTALLER_DIR=~/pyinstaller

# TODO: remove this once pyinstaller 3.4 is released and
# https://github.com/pyinstaller/pyinstaller/issues/2849 is resolved
install_pyinstaller() {
  rm -rf $PYINSTALLER_DIR || true
  mkdir -p $PYINSTALLER_DIR
  pushd $PYINSTALLER_DIR
    git clone https://github.com/Bharath92/pyinstaller.git
    pushd pyinstaller
      git checkout 9d5a9b02c13c9e8ace6feb1f704189c51bdba1bd
      python setup.py install
    popd
  popd
}

init_ve() {
  rm -rf $VE_LOCATION || true
  virtualenv -p /usr/bin/python $VE_LOCATION
  source $VE_LOCATION/bin/activate
  install_pyinstaller
  pip install -r requirements.txt
}

package() {
  rm -rf dist || true
  export LC_ALL=C
  pyinstaller --clean --hidden-import=requests main.py
}

main() {
  init_ve
  package
}

main
