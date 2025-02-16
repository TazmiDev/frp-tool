# Requires Administrator Privileges
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Please run this script as administrator." -ForegroundColor Red
    exit
}

$scriptDir = $PSScriptRoot
if (-not $scriptDir) {
    $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
}

# Install Directory
$installDir = Join-Path $env:ProgramFiles "frp-tool"

# Create Directory Structure
New-Item -Path (Join-Path $installDir "frpinit") -ItemType Directory -Force | Out-Null

# Copy Files
try {
    Copy-Item -Path (Join-Path $scriptDir "frp-cli.py") -Destination $installDir -Force

    $sourceFrpInit = Join-Path $scriptDir "frpinit\*"
    $destFrpInit = Join-Path $installDir "frpinit"
    Copy-Item -Path $sourceFrpInit -Destination $destFrpInit -Recurse -Force

    $envPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
    if ($envPath -split ';' -notcontains $installDir) {
        [Environment]::SetEnvironmentVariable("Path", "$envPath;$installDir", "Machine")
    }

    $batchContent = @'
    @echo off
    python "%~dp0frp-cli.py" %*
    if %errorlevel% neq 0 (
    echo [ERROR]: %errorlevel%
    pause
    )
'@
    Set-Content -Path (Join-Path $installDir "frp.bat") -Value $batchContent -Encoding ASCII
    Write-Host "Installation completed! Please reopen the terminal to use the frp command!" -ForegroundColor Green
}
catch {
    Write-Host "Installation failed : $_" -ForegroundColor Red
    exit 1
}
