# ULockAI Shield — start backend (Windows)
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Creating venv with Python 3.11..."
    py -3.11 -m venv .venv
}

Copy-Item "..\.env" -Destination ".env" -Force -ErrorAction SilentlyContinue

Write-Host "Installing dependencies..."
.\.venv\Scripts\pip install -q -r requirements-local.txt

Write-Host "Starting API on http://127.0.0.1:8000"
.\.venv\Scripts\uvicorn.exe app.main:app --host 0.0.0.0 --port 8000 --reload
