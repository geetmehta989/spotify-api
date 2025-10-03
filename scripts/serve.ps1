param(
  [string]$Host = "127.0.0.1",
  [int]$Port = 8000
)
$ErrorActionPreference = 'Stop'
if (Test-Path .venv) { . .\.venv\Scripts\Activate.ps1 }
$env:PYTHONPATH = (Get-Location).Path
uvicorn src.api_app:app --host $Host --port $Port
