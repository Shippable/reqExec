# ReqExec - Shippable build executor

[![Run Status](https://api.shippable.com/projects/59e069c1f7ca690700e9274f/badge?branch=master)](https://app.shippable.com/github/Shippable/reqExec)

`reqExec` is the component on the build node that executes the build steps.
Once [reqKick](https://github.com/shippable/reqKick) decides to run a build
step, it either

- calls `reqExec` directly to run build on the host, or
- spins up a `reqExec` mounted Docker container that runs the build in the container

Unlike [reqProc](https://github.com/shippable/reqProc) and [reqKick](https://github.com/shippable/reqKick),
`reqExec` is not an always-running agent, but a single platform-specific compiled binary that is responsible
for following tasks:

- run the `bash` scripts that contain the build step commands
- publish logs from running the script
- return the steps status back to [reqKick](https://github.com/shippable/reqKick)

It is one of the three components that are installed on the host when users [initialize](http://docs.shippable.com/platform/runtime/nodes/#byon-nodes) the host to act as a build node on Shippable. The other two components that are installed upon node initialization are [reqProc](https://github.com/shippable/reqProc)
and [reqKick](https://github.com/shippable/reqKick).

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

Any merged change in the project triggers Shippable assembly lines to compile
`reqExec` for all supported platforms and push the updated binaries  with `master` tag.

Use `./package/<ARCHITECTURE>/<OS>/package.<EXT>` to package binaries. The following are supported:

| ARCHITECTURE   | OS                  | EXT  |
| ------------   | --                  | ---  |
| x86_64         | Ubuntu_16.04        | sh   |
| x86_64         | macOS_10.12         | sh   |
| aarch64        | Ubuntu_16.04        | sh   |
| x86_64         | WindowsServer_2016  | ps1  |

## Releases

`reqExec` is updated with every Shippable release. The list of all Shippable releases can be found [here](https://github.com/Shippable/admiral/releases).
