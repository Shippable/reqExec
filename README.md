# reqExec [![Run Status](https://api.shippable.com/projects/59e069c1f7ca690700e9274f/badge?branch=master)](https://app.shippable.com/github/Shippable/reqExec)

## Development

### Pre-requisties

1. Python 2.7.x
2. pip
3. virtualenv
4. tar (WindowsServer_2016)

### Virtualenv

```bash
rm -rf /tmp/reqExec_dev_ve
virtualenv -p /usr/bin/python /tmp/reqExec_dev_ve
source /tmp/reqExec_dev_ve/bin/activate
pip install -r ./requirements/dev.txt
```

### Packaging binaries

Use `./package/<ARCHITECTURE>/<OS>/package.<EXT>` to package binaries. The following are supported:

| ARCHITECTURE   | OS                  | EXT  |
| ------------   | --                  | ---  |
| x86_64         | Ubuntu_16.04        | sh   |
| x86_64         | macOS_10.12         | sh   |
| aarch64        | Ubuntu_16.04        | sh   |
| x86_64         | WindowsServer_2016  | ps1  |

