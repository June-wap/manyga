. "$PSScriptRoot\common.ps1"
try {
    $ControlDirectory = Join-Path $ProjectRoot 'runtime'
    if (Test-Path -LiteralPath $ControlDirectory) {
        Get-ChildItem -LiteralPath $ControlDirectory -Filter 'desktop-*.owner' | ForEach-Object {
            if ($_.Name -match '^desktop-([0-9]+)-[a-f0-9]{32}\.owner$') {
                $OwnedPid = [int]$Matches[1]
                if (Get-Process -Id $OwnedPid -ErrorAction SilentlyContinue) {
                    # Request UI close; never terminate a PID from a stale marker.
                    $StopFile = [IO.Path]::ChangeExtension($_.FullName, '.stop')
                    [IO.File]::WriteAllText($StopFile, 'STOP')
                    Write-Output "Requested graceful close for desktop $OwnedPid."
                }
            }
        }
    }
    exit 0
} catch { Write-Error $_; exit 1 }
