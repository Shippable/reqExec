# reqExec
[![Run Status](https://api.shippable.com/projects/59e069c1f7ca690700e9274f/badge?branch=master)](https://app.shippable.com/github/Shippable/reqExec)

## Development

### Pre-requisties

1. Python 2.7.x
2. pip
3. virtualenv

### Virtualenv

```bash
rm -rf /tmp/reqExec_dev_ve
virtualenv -p /usr/bin/python /tmp/reqExec_dev_ve
source /tmp/reqExec_dev_ve/bin/activate
pip install -r ./requirements/dev.txt
```

### Packaging binaries

Use `./build.sh <ARCHITECTURE> <OS> [DRYDOCK_ORG]` to package binaries. `DRYDOCK_ORG` is optional. If it's specified, the packaging happens inside `DRYDOCK_ORG/microbase:master` container.

| ARCHITECTURE   | OS            | DRYDOCK_ORG    |
| ------------   | --            | -----------    |
| x86_64         | Ubuntu_16.04  | drydock        |
| x86_64         | macOS_10.12   |                |
| aarch64        | Ubuntu_16.04  | drydockaarch64 |
