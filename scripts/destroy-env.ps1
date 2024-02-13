# Prepare Environment Script for Django Project in PowerShell

# Load environment variables from .env file
Write-Host "Loading environment variables from .env file..."
$envFilePath = ".\.env"
Get-Content $envFilePath | ForEach-Object {
    $line = $_.Trim()
    if ($line -ne "")
    {
        $key, $value = $line -split '=', 2
        Set-Item -Path env:$key -Value $value
        Write-Output "${key}: ${value}"
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



# Database Cleanup
# For SQLite, simply remove the database file
# For other databases, use appropriate commands to drop the database
Write-Host "Cleaning up the database..."
$dbFilePath = "$env:DJANGO_PROJECT_DIR\db.sqlite3"
if (Test-Path -Path $dbFilePath) {
    Remove-Item -Path $dbFilePath -Force
    Write-Host "Database file removed."
} else {
    Write-Host "Database file does not exist. Skipping removal."
    # For other databases, you might run a command to drop the database
    # & "$env:CONDA_EXE" run -n $env:CONDA_PREFIX python "$env:DJANGO_PROJECT_DIR\manage.py" flush --no-input
    # Or use direct database commands to drop the database
}

# Remove Django Migration Files
Write-Host "Removing Django migration files..."
$migrationPaths = Get-ChildItem -Path "$env:DJANGO_PROJECT_DIR" -Include "migrations" -Recurse -Directory
foreach ($path in $migrationPaths) {
    Get-ChildItem -Path $path.FullName -File | Where-Object { $_.Name -ne "__init__.py" } | Remove-Item -Force
    Write-Host "Removed migrations from $($path.FullName)"
}

if ($envExists) {
    Write-Host "Removing Conda environment: $env:CONDA_PREFIX"
    & "${env:CONDA_EXE}" env remove --name ${env:CONDA_PREFIX} -y
} else {
    Write-Host "Conda environment $env:CONDA_PREFIX does not exist. Skipping removal."
}

# Optionally, remove Docker images if necessary
if ($env:DOCKER_BUILD_ENABLED -eq "true") {
    Write-Host "Removing Docker image: ${env:DOCKER_IMAGE_NAME}:${env:SEO_SPIDER_VERSION}"
    docker rmi "${env:DOCKER_IMAGE_NAME}:${env:SEO_SPIDER_VERSION}"
}
