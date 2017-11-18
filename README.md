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

Use `./package/<architecture>/<os>/package.sh` to package binaries. The following platforms are currently supported:

| architecture  | os           |
| ------------- |:------------:|
| x86_64        | Ubuntu_16.04 |
| aarch64       | Ubuntu_16.04 |
