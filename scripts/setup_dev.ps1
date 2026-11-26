param([switch]$WithBrowser)
. "$PSScriptRoot\common.ps1"
try {
    Set-Location -LiteralPath $ProjectRoot
    if (-not (Test-Path -LiteralPath $Python)) {
        Invoke-Checked -Program 'py' -Arguments @('-3.11', '-m', 'venv', '.venv')
    }
    Invoke-Checked -Program $Python -Arguments @('-m', 'pip', 'install', '-r', 'requirements.lock')
    Set-Location -LiteralPath $Frontend
    Invoke-Checked -Program 'npm.cmd' -Arguments @('ci')
    if ($WithBrowser) { Invoke-Checked -Program 'npx.cmd' -Arguments @('playwright', 'install', 'chromium') }
    Write-Output 'Setup complete. Run scripts/start_dev.ps1.'
    exit 0
} catch { Write-Error $_; exit 1 }
