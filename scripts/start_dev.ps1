# Foreground desktop owns backend + direct Vite child; closing it stops both.
& "$PSScriptRoot\start_desktop.ps1"
exit $LASTEXITCODE
