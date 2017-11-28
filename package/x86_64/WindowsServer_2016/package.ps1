$ErrorActionPreference = "Stop"

function buildReqExec
{
  pip install pyinstaller==3.3
  pip install -r requirements.txt
  python -m PyInstaller --clean --hidden-import=requests -F main.py
}

# TODO: move this to pipelines later
function packageBinaries
{
  $bin_directory = ".\dist\main"
  New-Item -ItemType Directory -Force -Path $bin_directory
  Move-Item -force .\dist\main.exe $bin_directory
  $tmpReqExecPath = "$Env:USERPROFILE/shippable/tmp/reqExec"
  New-Item -ItemType Directory -Force -Path $tmpReqExecPath
  Copy-Item -Force -Recurse dist $tmpReqExecPath/
  tar -zcvf reqExec.tar.gz -C $tmpReqExecPath .
}

echo "building reqExec binaries"
buildReqExec

echo "compressing binaries"
packageBinaries
