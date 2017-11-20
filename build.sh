#!/bin/bash -e

export DRYDOCK_ORG="$1"
export ARCHITECTURE="$2"
export OS="$3"
export TAG="master"

check_input() {
  if [ -z "$DRYDOCK_ORG" ]; then
    echo "Missing input parameter DRYDOCK_ORG"
    exit 1
  fi

  if [ -z "$ARCHITECTURE" ]; then
    echo "Missing input parameter ARCHITECTURE"
    exit 1
  fi

  if [ -z "$OS" ]; then
    echo "Missing input parameter OS"
    exit 1
  fi
}

build_reqExec() {
  docker run -v $(pwd):/root/reqExec $DRYDOCK_ORG/microbase:$TAG bash -c "pushd /root/reqExec && /root/reqExec/package/$ARCHITECTURE/$OS/package.sh"
}

main() {
  check_input
  build_reqExec
}

main
