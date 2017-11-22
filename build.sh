#!/bin/bash -e

export ARCHITECTURE="$1"
export OS="$2"
export DRYDOCK_ORG="$3"
export TAG="master"

check_input() {
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
  if [ -z "$DRYDOCK_ORG" ]; then
    echo "Building on host..."
    ./package/$ARCHITECTURE/$OS/package.sh
  else
    echo "Building inside $DRYDOCK_ORG/microbase:$TAG"
    docker run -v $(pwd):/root/reqExec $DRYDOCK_ORG/microbase:$TAG bash -c "pushd /root/reqExec && /root/reqExec/package/$ARCHITECTURE/$OS/package.sh"
  fi
}

main() {
  check_input
  build_reqExec
}

main
