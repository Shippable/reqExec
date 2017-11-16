# reqExec

## Development

Run the following:

```
rm -rf /tmp/reqExec_dev_ve
virtualenv -p /usr/bin/python /tmp/reqExec_dev_ve
source /tmp/reqExec_dev_ve/bin/activate
pip install -r ./requirements/dev.txt
```

## Packaging binaries

Use `make package_<arch>_<os>` where `<arch>` is the architecture and `<os>` is the operating system you are building for.

The following are supported:

| Architecture  | OS     |
| ------------- |:------:|
| x86_64        | Ubuntu |
| aarch64       | Ubuntu |
