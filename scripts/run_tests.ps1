param([switch]$Browser, [switch]$Embedded)
. "$PSScriptRoot\common.ps1"
try {
    Assert-Python
    Set-Location -LiteralPath $ProjectRoot
    Invoke-Checked -Program $Python -Arguments @('-m', 'ruff', 'check', 'core', 'apps', 'tests', 'scripts')
    Invoke-Checked -Program $Python -Arguments @('-m', 'pytest', '-q')
    if ($Embedded) {
        Invoke-Checked -Program $Python -Arguments @('scripts/verify_integration.py')
        Invoke-Checked -Program $Python -Arguments @('scripts/verify_dev_scripts.py')
    }
    Set-Location -LiteralPath $Frontend
    Invoke-Checked -Program 'npm.cmd' -Arguments @('run', 'build')
    Invoke-Checked -Program 'npm.cmd' -Arguments @('test')
    if ($Browser) { Invoke-Checked -Program 'npm.cmd' -Arguments @('run', 'test:e2e') }
    exit 0
} catch { Write-Error $_; exit 1 }
