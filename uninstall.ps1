if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "require administrator privileges" -ForegroundColor Red
    exit
}
$installDir = Join-Path $env:ProgramFiles "frp-tool"

# remove files
if (Test-Path $installDir) {
    Remove-Item -Path $installDir -Recurse -Force
}

# clear environment variable
$envPath = [Environment]::GetEnvironmentVariable("Path", "Machine") -split ';' | 
Where-Object { $_ -ne $installDir }
[Environment]::SetEnvironmentVariable("Path", ($envPath -join ';'), "Machine")

Write-Host "Uninstall completed!" -ForegroundColor Green