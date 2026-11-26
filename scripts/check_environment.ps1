. "$PSScriptRoot\common.ps1"
try {
    Invoke-Checked -Program 'py' -Arguments @('-3.11', '--version')
    Invoke-Checked -Program 'node' -Arguments @('--version')
    Invoke-Checked -Program 'npm.cmd' -Arguments @('--version')
    Invoke-Checked -Program 'git' -Arguments @('--version')
    Get-CimInstance Win32_OperatingSystem | Select-Object Caption, OSArchitecture, TotalVisibleMemorySize | Format-List
    Get-CimInstance Win32_Processor | Select-Object Name | Format-List
    Get-PSDrive -Name ([IO.Path]::GetPathRoot($ProjectRoot).Substring(0,1)) | Select-Object Used, Free | Format-List
    if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
        & nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
    }
    exit 0
} catch { Write-Error $_; exit 1 }
