. "$PSScriptRoot\common.ps1"
try {
    Assert-Python
    Set-Location -LiteralPath $ProjectRoot
    & $Python -m apps.backend
    exit $LASTEXITCODE
} catch { Write-Error $_; exit 1 }
