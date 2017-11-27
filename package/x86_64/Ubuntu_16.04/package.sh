#!/bin/bash -e

readonly VE_LOCATION=/tmp/reqExec_pkg_ve

init_ve() {
  rm -rf $VE_LOCATION
  virtualenv -p /usr/bin/python $VE_LOCATION
  # shellcheck disable=SC1090
  source $VE_LOCATION/bin/activate
  pip install pyinstaller==3.3
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
