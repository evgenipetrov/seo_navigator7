# Reset Script for Django Project Environment in PowerShell

Write-Host "Starting environment reset process..."

# Construct full paths to the cleanup and setup scripts using $PSScriptRoot
$destroyScriptPath = Join-Path -Path $PSScriptRoot -ChildPath "destroy-env.ps1"
$setupScriptPath = Join-Path -Path $PSScriptRoot -ChildPath "windows_setup-env.ps1"


Write-Host "Running Cleanup Script..."
if (Test-Path -Path $destroyScriptPath)
{
    & $destroyScriptPath
    Write-Host "Cleanup completed."
}
else
{
    Write-Host "Cleanup script not found at $cleanupScriptPath"
}

Write-Host "Running Setup Script..."
if (Test-Path -Path $setupScriptPath)
{
    & $setupScriptPath
    Write-Host "Setup completed."
}
else
{
    Write-Host "Setup script not found at $setupScriptPath"
}

Write-Host "Environment reset process is complete."
