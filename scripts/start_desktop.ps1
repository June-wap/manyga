param([switch]$ConnectBackend, [switch]$ConnectRuntime)
. "$PSScriptRoot\common.ps1"
try {
    Assert-Python
    Set-Location -LiteralPath $ProjectRoot
    $DesktopArgs = @('-m', 'apps.desktop')
    if ($ConnectBackend) { $DesktopArgs += '--connect-backend' }
    if ($ConnectRuntime) { $DesktopArgs += '--connect-runtime' }
    & $Python @DesktopArgs
    exit $LASTEXITCODE
} catch { Write-Error $_; exit 1 }
