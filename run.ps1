# One-command start on Windows:  .\run.ps1   ->  http://localhost:8000
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
if (-not (Test-Path backend\.venv)) { python -m venv backend\.venv }
& backend\.venv\Scripts\python.exe -m pip install -q -r backend\requirements.txt
if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env; Write-Host "Created backend\.env - add your GEMINI_API_KEY there (optional)." }
Push-Location frontend; npm install --no-audit --no-fund; npm run build; Pop-Location
Set-Location backend
& .\.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
