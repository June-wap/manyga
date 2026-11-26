. "$PSScriptRoot\common.ps1"
try {
    Assert-Python
    Set-Location -LiteralPath $ProjectRoot
    $RuntimePort = & $Python -c 'from core.config import Settings; from urllib.parse import urlsplit; print(urlsplit(Settings().runtime_url).port)'
    if ($LASTEXITCODE -ne 0) { throw 'Invalid runtime configuration.' }
    Set-Location -LiteralPath $Frontend
    & node 'node_modules/vite/bin/vite.js' --host 127.0.0.1 --port $RuntimePort --strictPort
    exit $LASTEXITCODE
} catch { Write-Error $_; exit 1 }
