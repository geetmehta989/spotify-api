param(
  [string]$Artist,
  [string]$Dataset,
  [string]$Output
)
$ErrorActionPreference = 'Stop'
if (Test-Path .venv) { . .\.venv\Scripts\Activate.ps1 }
$env:PYTHONPATH = (Get-Location).Path
$cmd = "-m src.main"
if ($Artist) { $cmd = "$cmd --artist `"$Artist`"" }
if ($Dataset) { $cmd = "$cmd --dataset `"$Dataset`"" }
if ($Output)  { $cmd = "$cmd --output `"$Output`"" }
python $cmd
