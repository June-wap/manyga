$ErrorActionPreference = 'Stop'
$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot '.venv\Scripts\python.exe'
$Frontend = Join-Path $ProjectRoot 'frontend'
function Assert-Python {
    if (-not (Test-Path -LiteralPath $Python)) { throw 'Run scripts/setup_dev.ps1 first (.venv missing).' }
}
function Invoke-Checked {
    param([string]$Program, [string[]]$Arguments)
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed with exit code ${LASTEXITCODE}: $Program" }
}
