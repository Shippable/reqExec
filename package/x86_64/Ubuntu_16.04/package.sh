#!/bin/bash -e

readonly VE_LOCATION=/tmp/reqExec_pkg_ve

init_ve() {
  virtualenv -p /usr/bin/python $VE_LOCATION
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
