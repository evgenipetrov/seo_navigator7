$lineLength = 240  # Set the maximum line length for code

# Store the current directory
$currentDirectory = Get-Location
$scriptDirectory = $PSScriptRoot

# Load environment variables from .env file
Write-Host "Loading environment variables from .env file..."
$envFilePath = ".\.env"
Get-Content $envFilePath | ForEach-Object {
    $line = $_.Trim()
    if ($line -ne "")
    {
        $key, $value = $line -split '=', 2
        Set-Item -Path env:$key -Value $value
    }
}

# Ensure the Conda executable path is correct
if (-Not(Test-Path -Path $env:CONDA_EXE))
{
    Write-Host "Conda executable not found at $env:CONDA_EXE"
    exit 1
}

# Check if the Conda environment exists
$envList = & "$env:CONDA_EXE" env list
$envExists = $envList -like "*$env:CONDA_PREFIX*"

if ($envExists)
{
    Write-Host "Ensuring Python linting and formatting tools are installed..."
    # Install Python packages from requirements.txt
    Write-Host "Installing Python dev packages from dev.txt..."
    & "$env:CONDA_EXE" run -n $env:CONDA_PREFIX pip install -r requirements.dev.txt
}

$env:PYTHONPATH += ";D:\Projects\seo_navigator\src"

Write-Host "Running tests..."
& $env:CONDA_EXE run -n $env:CONDA_PREFIX pytest .


