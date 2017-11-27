#!/bin/bash -e

readonly VE_LOCATION=/tmp/reqExec_pkg_ve
readonly PYINSTALLER_DIR=/tmp/pyinstaller
readonly PYINSTALLER_AARCH_FIX_REPO="https://github.com/Bharath92/pyinstaller.git"
readonly PYINSTALLER_AARCH_FIX_COMMIT="9d5a9b02c13c9e8ace6feb1f704189c51bdba1bd"

# TODO:
# Remove this once pyinstaller 3.4 is released and
# https://github.com/pyinstaller/pyinstaller/issues/2849 is resolved
install_pyinstaller() {
  rm -rf $PYINSTALLER_DIR
  git clone $PYINSTALLER_AARCH_FIX_REPO $PYINSTALLER_DIR
  pushd $PYINSTALLER_DIR
    git checkout $PYINSTALLER_AARCH_FIX_COMMIT
    python setup.py install
  popd
}

init_ve() {
  rm -rf $VE_LOCATION
  virtualenv -p /usr/bin/python $VE_LOCATION
  # shellcheck disable=SC1090
  source $VE_LOCATION/bin/activate
  install_pyinstaller
  pip install -r requirements.txt
}

package() {
  rm -rf dist
  pyinstaller --clean --hidden-import=requests main.py
}

main() {
  init_ve
  package
}

main
